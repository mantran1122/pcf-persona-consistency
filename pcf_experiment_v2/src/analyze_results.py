"""Statistical analysis: descriptives, Wilson CIs, paired condition tests (Wilcoxon /
Friedman + Holm), effect sizes, inter-rater and human-LLM agreement, and figures.

Notes for the paper:
- Rubric scores are ordinal -> non-parametric tests only.
- Turns within a dialogue are not independent; the primary comparison unit is the
  dialogue (persona x run), using dialogue-level mean scores. Turn-level analyses are
  reported as exploratory.
"""

import itertools

import numpy as np
import pandas as pd
from scipy import stats

from . import utils
from .utils import FIGURES_DIR, SUMMARY_DIR

SCORE_KEYS = ["persona_consistency", "memory_retention", "style_stability", "context_awareness"]
ALL_METRICS = SCORE_KEYS + ["overall_score"]


# ---------------------------------------------------------------------------
# Descriptives
# ---------------------------------------------------------------------------

def wilson_ci(k, n, z=1.96):
    """Wilson 95% CI for a proportion."""
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def describe(df, by):
    rows = []
    for keys, g in df.groupby(by):
        keys = keys if isinstance(keys, tuple) else (keys,)
        row = dict(zip(by if isinstance(by, list) else [by], keys))
        for m in ALL_METRICS:
            row[f"{m}_mean"] = g[m].mean()
            row[f"{m}_sd"] = g[m].std()
            row[f"{m}_median"] = g[m].median()
            row[f"{m}_iqr"] = g[m].quantile(0.75) - g[m].quantile(0.25)
        k, n = int(g["contradiction_flag"].sum()), len(g)
        lo, hi = wilson_ci(k, n)
        row.update(n=n, contradiction_rate=k / n, cr_wilson_lo=lo, cr_wilson_hi=hi)
        rows.append(row)
    return pd.DataFrame(rows).round(4)


def export_summaries(df):
    utils.ensure_dirs()
    outputs = {
        "summary_by_condition.csv": describe(df, ["condition"]),
        "summary_by_persona.csv": describe(df, ["condition", "persona_id"]),
        "summary_by_scenario.csv": describe(df, ["condition", "scenario_id"]),
        "summary_by_turn_position.csv": describe(df, ["condition", "global_turn_id"]),
        "summary_by_run.csv": describe(df, ["condition", "run_id"]),
    }
    if "generator_id" in df.columns and df["generator_id"].nunique() > 1:
        outputs["summary_by_generator.csv"] = describe(df, ["generator_id", "condition"])
    for name, table in outputs.items():
        table.to_csv(SUMMARY_DIR / name, index=False, encoding="utf-8-sig")
    return outputs


# ---------------------------------------------------------------------------
# Condition comparisons (dialogue-level primary unit)
# ---------------------------------------------------------------------------

def dialogue_level(df):
    """Mean scores per dialogue (condition x persona x run [x generator])."""
    keys = ["condition", "persona_id", "run_id"]
    if "generator_id" in df.columns:
        keys.insert(1, "generator_id")
    agg = {m: "mean" for m in ALL_METRICS}
    agg["contradiction_flag"] = "mean"
    return df.groupby(keys).agg(agg).reset_index()


def rank_biserial(x, y):
    """Matched-pairs rank-biserial correlation for Wilcoxon signed-rank."""
    d = np.asarray(x) - np.asarray(y)
    d = d[d != 0]
    if len(d) == 0:
        return 0.0
    ranks = stats.rankdata(np.abs(d))
    r_plus = ranks[d > 0].sum()
    r_minus = ranks[d < 0].sum()
    return (r_plus - r_minus) / ranks.sum()


def holm_correction(pvals):
    order = np.argsort(pvals)
    m = len(pvals)
    adjusted = np.empty(m)
    running_max = 0.0
    for rank, idx in enumerate(order):
        running_max = max(running_max, (m - rank) * pvals[idx])
        adjusted[idx] = min(1.0, running_max)
    return adjusted


def compare_conditions(df, out_name="statistical_tests.csv"):
    """Paired tests on dialogue-level means. Wilcoxon for each condition pair,
    Friedman + Kendall's W when 3+ conditions. Pairing key is (persona_id, run_id[, generator_id])
    so with two generators present each is paired only against itself, never mixed."""
    dlg = dialogue_level(df)
    conditions = sorted(dlg["condition"].unique())
    pair_keys = ["persona_id", "run_id"]
    if "generator_id" in dlg.columns:
        pair_keys.append("generator_id")
    wide = {m: dlg.pivot_table(index=pair_keys, columns="condition", values=m)
            for m in ALL_METRICS + ["contradiction_flag"]}

    rows = []
    for m in ALL_METRICS + ["contradiction_flag"]:
        table = wide[m].dropna()
        # Friedman across all conditions
        if len(conditions) >= 3 and len(table) >= 3:
            fr_stat, fr_p = stats.friedmanchisquare(*[table[c] for c in conditions])
            n, k = len(table), len(conditions)
            kendall_w = fr_stat / (n * (k - 1))
            rows.append({"metric": m, "test": "friedman", "comparison": " vs ".join(conditions),
                         "statistic": fr_stat, "p_value": fr_p, "effect_size": kendall_w,
                         "effect_size_name": "kendall_w", "n_pairs": n})
        # Pairwise Wilcoxon
        pair_rows = []
        for a, b in itertools.combinations(conditions, 2):
            x, y = table[a], table[b]
            if (x - y).abs().sum() == 0:
                stat, p = np.nan, 1.0
            else:
                stat, p = stats.wilcoxon(x, y)
            pair_rows.append({"metric": m, "test": "wilcoxon", "comparison": f"{a} vs {b}",
                              "statistic": stat, "p_value": p,
                              "effect_size": rank_biserial(x, y),
                              "effect_size_name": "rank_biserial", "n_pairs": len(table),
                              "mean_a": x.mean(), "mean_b": y.mean()})
        pvals = [r["p_value"] for r in pair_rows]
        if pvals:
            adjusted = holm_correction(np.array(pvals))
            for r, p_adj in zip(pair_rows, adjusted):
                r["p_holm"] = p_adj
        rows.extend(pair_rows)

    result = pd.DataFrame(rows).round(5)
    result.to_csv(SUMMARY_DIR / out_name, index=False, encoding="utf-8-sig")
    return result


def compare_generators(df):
    """Does the condition ranking replicate across generators? Runs compare_conditions()
    separately within each generator_id and also a direct G1-vs-G2 paired test per condition
    (same persona/run/condition, different generator)."""
    if "generator_id" not in df.columns or df["generator_id"].nunique() < 2:
        return None
    per_gen = {}
    for gid, g in df.groupby("generator_id"):
        per_gen[gid] = compare_conditions(g, out_name=f"statistical_tests_{gid}.csv")

    dlg = dialogue_level(df)
    rows = []
    for m in ALL_METRICS + ["contradiction_flag"]:
        wide = dlg.pivot_table(index=["condition", "persona_id", "run_id"],
                               columns="generator_id", values=m)
        for condition, cg in wide.groupby(level="condition"):
            table = cg.dropna()
            gids = sorted(table.columns)
            if len(gids) != 2 or len(table) < 3:
                continue
            x, y = table[gids[0]], table[gids[1]]
            if (x - y).abs().sum() == 0:
                stat, p = np.nan, 1.0
            else:
                stat, p = stats.wilcoxon(x, y)
            rows.append({"metric": m, "condition": condition, "comparison": f"{gids[0]} vs {gids[1]}",
                        "statistic": stat, "p_value": p, "effect_size": rank_biserial(x, y),
                        "effect_size_name": "rank_biserial", "n_pairs": len(table),
                        "mean_g1": x.mean(), "mean_g2": y.mean()})
    result = pd.DataFrame(rows).round(5)
    if not result.empty:
        result["p_holm"] = holm_correction(result["p_value"].to_numpy())
    result.to_csv(SUMMARY_DIR / "statistical_tests_generator_comparison.csv", index=False,
                 encoding="utf-8-sig")
    return {"per_generator": per_gen, "generator_vs_generator": result}


# ---------------------------------------------------------------------------
# Agreement (human evaluation)
# ---------------------------------------------------------------------------

def cohens_kappa(a, b, weights=None, categories=None):
    """Cohen's kappa; weights: None | 'linear' | 'quadratic'."""
    a, b = pd.Series(a).reset_index(drop=True), pd.Series(b).reset_index(drop=True)
    mask = a.notna() & b.notna()
    a, b = a[mask], b[mask]
    if categories is None:
        categories = sorted(set(a) | set(b))
    k = len(categories)
    idx = {c: i for i, c in enumerate(categories)}
    obs = np.zeros((k, k))
    for x, y in zip(a, b):
        obs[idx[x], idx[y]] += 1
    obs /= obs.sum()
    exp = np.outer(obs.sum(axis=1), obs.sum(axis=0))
    if weights is None:
        w = 1 - np.eye(k)
    else:
        diff = np.abs(np.arange(k)[:, None] - np.arange(k)[None, :])
        w = diff if weights == "linear" else diff**2
    po, pe = (w * obs).sum(), (w * exp).sum()
    return 1 - po / pe if pe > 0 else np.nan


def compute_agreement(rater1_csv, rater2_csv, judged_df):
    """Inter-rater kappas + human-LLM agreement. Rater CSVs use the blinded sheet format."""
    r1 = pd.read_csv(rater1_csv)
    r2 = pd.read_csv(rater2_csv)
    key = pd.read_csv(utils.HUMAN_DIR / "unblinding_key.csv")
    merged = r1.merge(r2, on="sample_id", suffixes=("_r1", "_r2")).merge(key, on="sample_id")
    llm = merged.merge(judged_df[["record_id"] + SCORE_KEYS + ["contradiction_flag", "error_label"]],
                       on="record_id", suffixes=("", "_llm"))

    dims = {"PC": "persona_consistency", "MR": "memory_retention",
            "SS": "style_stability", "CA": "context_awareness"}
    rows = []
    for abbr, full in dims.items():
        rows.append({"dimension": abbr, "comparison": "rater1 vs rater2",
                     "kappa": cohens_kappa(merged[f"{abbr}_r1"], merged[f"{abbr}_r2"],
                                           weights="quadratic", categories=[1, 2, 3, 4, 5]),
                     "type": "weighted (quadratic)"})
        human_mean = (llm[f"{abbr}_r1"] + llm[f"{abbr}_r2"]) / 2
        rows.append({"dimension": abbr, "comparison": "human mean vs LLM judge",
                     "kappa": stats.spearmanr(human_mean, llm[full]).statistic,
                     "type": "spearman_rho"})
    rows.append({"dimension": "CF", "comparison": "rater1 vs rater2",
                 "kappa": cohens_kappa(merged["CF_r1"], merged["CF_r2"], categories=[0, 1]),
                 "type": "unweighted"})
    rows.append({"dimension": "error_label", "comparison": "rater1 vs rater2",
                 "kappa": cohens_kappa(merged["error_label_r1"], merged["error_label_r2"]),
                 "type": "unweighted"})
    out = pd.DataFrame(rows).round(4)
    out.to_csv(SUMMARY_DIR / "human_agreement.csv", index=False, encoding="utf-8-sig")
    return out


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------

CONDITION_COLORS = {"B0": "#9AA0A6", "C1": "#4C78A8", "C2": "#F58518", "C3": "#54A24B",
                    "C4": "#B279A2"}


def make_figures(df):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"figure.dpi": 150, "font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False})
    utils.ensure_dirs()
    conditions = sorted(df["condition"].unique())
    colors = [CONDITION_COLORS.get(c, "#666") for c in conditions]

    # Fig 1 — Overall score by condition (mean + 95% CI over dialogue means)
    dlg = dialogue_level(df)
    fig, ax = plt.subplots(figsize=(5, 3.2))
    means = [dlg.loc[dlg.condition == c, "overall_score"] for c in conditions]
    ax.bar(conditions, [m.mean() for m in means], color=colors,
           yerr=[1.96 * m.sem() for m in means], capsize=4)
    ax.set_ylabel("Overall score (1–5)")
    ax.set_ylim(1, 5)
    ax.set_title("Overall persona consistency by condition")
    fig.savefig(FIGURES_DIR / "fig1_overall_by_condition.png", bbox_inches="tight")
    plt.close(fig)

    # Fig 2 — Rubric dimensions by condition (grouped bars)
    fig, ax = plt.subplots(figsize=(7, 3.5))
    x = np.arange(len(SCORE_KEYS))
    width = 0.8 / len(conditions)
    for i, c in enumerate(conditions):
        vals = [df.loc[df.condition == c, k].mean() for k in SCORE_KEYS]
        ax.bar(x + i * width, vals, width, label=c, color=colors[i])
    ax.set_xticks(x + width * (len(conditions) - 1) / 2)
    ax.set_xticklabels(["PC", "MR", "SS", "CA"])
    ax.set_ylim(1, 5)
    ax.set_ylabel("Mean score (1–5)")
    ax.legend(frameon=False)
    ax.set_title("Rubric scores by condition")
    fig.savefig(FIGURES_DIR / "fig2_rubric_by_condition.png", bbox_inches="tight")
    plt.close(fig)

    # Fig 3 — Contradiction rate by condition with Wilson CI
    fig, ax = plt.subplots(figsize=(5, 3.2))
    rates, err_lo, err_hi = [], [], []
    for c in conditions:
        g = df[df.condition == c]
        k, n = int(g["contradiction_flag"].sum()), len(g)
        lo, hi = wilson_ci(k, n)
        rates.append(k / n)
        err_lo.append(k / n - lo)
        err_hi.append(hi - k / n)
    ax.bar(conditions, rates, color=colors, yerr=[err_lo, err_hi], capsize=4)
    ax.set_ylabel("Contradiction rate")
    ax.set_title("Contradiction rate by condition (Wilson 95% CI)")
    fig.savefig(FIGURES_DIR / "fig3_contradiction_rate.png", bbox_inches="tight")
    plt.close(fig)

    # Fig 4 — Overall score by scenario and condition
    fig, ax = plt.subplots(figsize=(7, 3.5))
    scenarios = sorted(df["scenario_id"].unique())
    x = np.arange(len(scenarios))
    for i, c in enumerate(conditions):
        vals = [df[(df.condition == c) & (df.scenario_id == s)]["overall_score"].mean()
                for s in scenarios]
        ax.bar(x + i * width, vals, width, label=c, color=colors[i])
    ax.set_xticks(x + width * (len(conditions) - 1) / 2)
    ax.set_xticklabels(scenarios)
    ax.set_ylim(1, 5)
    ax.set_ylabel("Overall score")
    ax.legend(frameon=False)
    ax.set_title("Score by scenario type")
    fig.savefig(FIGURES_DIR / "fig4_score_by_scenario.png", bbox_inches="tight")
    plt.close(fig)

    # Fig 5 — Score across global turn position (drift trend)
    fig, ax = plt.subplots(figsize=(7, 3.5))
    for i, c in enumerate(conditions):
        g = df[df.condition == c].groupby("global_turn_id")["overall_score"].mean()
        ax.plot(g.index, g.values, label=c, color=colors[i], linewidth=1.8)
    ax.set_xlabel("Global turn position")
    ax.set_ylabel("Mean overall score")
    ax.set_ylim(1, 5)
    ax.legend(frameon=False)
    ax.set_title("Persona consistency across dialogue turns (exploratory)")
    fig.savefig(FIGURES_DIR / "fig5_score_by_turn.png", bbox_inches="tight")
    plt.close(fig)

    # Fig 6 — LLM-inferred error label distribution (excluding 'none')
    fig, ax = plt.subplots(figsize=(6, 3.5))
    err = df[df.error_label != "none"]
    counts = err.groupby(["error_label", "condition"]).size().unstack(fill_value=0)
    counts = counts.loc[counts.sum(axis=1).sort_values().index]
    left = np.zeros(len(counts))
    for c in conditions:
        if c in counts:
            ax.barh(counts.index, counts[c], left=left, label=c,
                    color=CONDITION_COLORS.get(c, "#666"))
            left += counts[c].values
    ax.set_xlabel("Count")
    ax.legend(frameon=False)
    ax.set_title("LLM-inferred error labels by condition")
    fig.savefig(FIGURES_DIR / "fig6_error_labels.png", bbox_inches="tight")
    plt.close(fig)

    # Fig 7 — Heatmap persona x scenario (overall score, condition-averaged)
    pivot = df.pivot_table(index="persona_id", columns="scenario_id", values="overall_score")
    fig, ax = plt.subplots(figsize=(5.5, 3.8))
    im = ax.imshow(pivot.values, cmap="RdYlGn", vmin=1, vmax=5, aspect="auto")
    ax.set_xticks(range(len(pivot.columns)), pivot.columns)
    ax.set_yticks(range(len(pivot.index)), pivot.index)
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            ax.text(j, i, f"{pivot.values[i, j]:.2f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, label="Overall score")
    ax.set_title("Persona x scenario heatmap")
    fig.savefig(FIGURES_DIR / "fig7_heatmap_persona_scenario.png", bbox_inches="tight")
    plt.close(fig)

    return sorted(p.name for p in FIGURES_DIR.glob("*.png"))


def run_full_analysis(judged_df):
    """Main figures/summaries/tests stay scoped to G1 (the paper's primary, pre-registered
    generator) so their meaning is unchanged whether or not a G2 replication run exists yet.
    When a second generator is present, an additional generator-comparison analysis is run
    on the full (G1+G2) data and saved separately (statistical_tests_G1.csv / _G2.csv /
    _generator_comparison.csv, summary_by_generator.csv) rather than silently pooling both
    generators into the primary results."""
    primary = judged_df
    if "generator_id" in judged_df.columns:
        primary = judged_df[judged_df["generator_id"] == "G1"]

    export_summaries(judged_df)  # includes summary_by_generator.csv when >1 generator present
    tests = compare_conditions(primary)
    figs = make_figures(primary)
    gen_comparison = compare_generators(judged_df)
    return tests, figs, gen_comparison


if __name__ == "__main__":
    from .judge_responses import collect_judged_csv
    run_full_analysis(collect_judged_csv())
