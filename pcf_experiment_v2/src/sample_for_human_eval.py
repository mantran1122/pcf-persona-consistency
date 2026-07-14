"""Stratified sampling for human evaluation.

Strata: condition x persona x scenario. Additionally ALL contradiction_flag=1 cases are
included, plus low-score and high-score cases within each stratum. Output is blinded
(no condition/model columns) and shuffled; the unblinding key is saved separately.
"""

import numpy as np
import pandas as pd

from . import load_config, utils
from .utils import HUMAN_DIR

RATING_COLUMNS = ["PC", "MR", "SS", "CA", "CF", "error_label", "note"]


def make_sample(judged_df, ctx=None, fraction=0.25, min_per_stratum=1,
                cf_full_conditions=("C1", "C2", "C3", "C4")):
    """Stratified sample for human evaluation.

    All contradiction_flag=1 cases from `cf_full_conditions` are force-included
    (they carry the ablation signal). Conditions outside that set (B0, where CF=1
    is near-universal and homogeneous) are only sampled via the regular strata,
    keeping the total near `fraction` of the data.
    """
    if ctx is None:
        ctx = load_config.load_all()
    rng = np.random.default_rng(ctx["experiment"].get("random_seed", 0))
    df = judged_df.copy()

    force = (df["contradiction_flag"] == 1) & df["condition"].isin(cf_full_conditions)
    selected = set(df.loc[force, "record_id"])

    strata_cols = ["condition", "persona_id", "scenario_id"]
    if "generator_id" in df.columns and df["generator_id"].nunique() > 1:
        strata_cols.insert(1, "generator_id")  # keep both generators proportionally represented
    for _, group in df.groupby(strata_cols):
        remaining = group[~group["record_id"].isin(selected)]
        n_target = max(min_per_stratum, int(round(len(group) * fraction)))
        n_take = max(0, n_target - (len(group) - len(remaining)))
        if n_take == 0 or remaining.empty:
            continue
        ranked = remaining.sort_values("overall_score")
        picks = []
        if len(ranked) >= 2 and n_take >= 2:
            picks = [ranked.index[0], ranked.index[-1]]  # lowest and highest score
        extra = n_take - len(picks)
        pool = ranked.index.difference(picks)
        if extra > 0 and len(pool) > 0:
            picks += list(rng.choice(pool, size=min(extra, len(pool)), replace=False))
        selected.update(ranked.loc[picks, "record_id"])

    sample = df[df["record_id"].isin(selected)].copy()
    sample = sample.sample(frac=1, random_state=int(rng.integers(0, 2**31))).reset_index(drop=True)
    sample["sample_id"] = [f"H{i + 1:04d}" for i in range(len(sample))]

    # Unblinding key (keep private until agreement is computed)
    key_cols = ["sample_id", "record_id", "condition", "run_id",
               "overall_score", "contradiction_flag", "error_label"]
    if "generator_id" in sample.columns:
        key_cols.insert(4, "generator_id")
    key = sample[key_cols]
    utils.ensure_dirs()
    key.to_csv(HUMAN_DIR / "unblinding_key.csv", index=False, encoding="utf-8-sig")

    # Blinded annotation sheet: no condition, no model, no judge scores
    blinded = sample[["sample_id", "persona_id", "scenario_id", "user_prompt", "model_response"]].copy()
    blinded = blinded.rename(columns={"model_response": "response"})
    for col in RATING_COLUMNS:
        blinded[col] = ""
    for rater in ("rater1", "rater2"):
        blinded.to_csv(HUMAN_DIR / f"human_evaluation_sheet_{rater}.csv",
                       index=False, encoding="utf-8-sig")

    utils.get_logger().info("Human-eval sample: %d items (%.1f%% of %d judged responses)",
                            len(sample), 100 * len(sample) / max(len(df), 1), len(df))
    return sample


if __name__ == "__main__":
    from .judge_responses import collect_judged_csv
    make_sample(collect_judged_csv())
