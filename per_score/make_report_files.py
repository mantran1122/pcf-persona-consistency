# -*- coding: utf-8 -*-
"""Xuất các file kết quả human evaluation cho báo cáo.

Đầu vào:
  - per_score/human_evaluation_sheet_rater1_scored.xlsx  (giáo viên 1)
  - per_score/human_evaluation_sheet_rater2 (1).xlsx     (giáo viên 2)
  - pcf_experiment_v2/outputs/human_annotations/unblinding_key.csv (condition + điểm judge)

Đầu ra: per_score/report/*.csv + *.png
"""
import os
import numpy as np
import pandas as pd
from scipy import stats

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "report")
os.makedirs(OUT, exist_ok=True)

CRIT = ["PC", "MR", "SS", "CA"]

r1 = pd.read_excel(os.path.join(BASE, "human_evaluation_sheet_rater1_scored.xlsx"), sheet_name="cham_diem")
r2 = pd.read_excel(os.path.join(BASE, "human_evaluation_sheet_rater2 (1).xlsx"), sheet_name="cham_diem")
key = pd.read_csv(os.path.join(BASE, "..", "pcf_experiment_v2", "outputs", "human_annotations", "unblinding_key.csv"))
assert (r1.sample_id == r2.sample_id).all() and len(r1) == len(key)

# ---------- 1) merged long file ----------
m = r1[["sample_id", "persona_id", "scenario_id"]].copy()
for c in CRIT + ["CF"]:
    m[f"r1_{c}"] = r1[c]
    m[f"r2_{c}"] = r2[c]
m["r1_error_label"] = r1["error_label"]
m["r2_error_label"] = r2["error_label"]
m["r1_overall"] = r1[CRIT].mean(axis=1)
m["r2_overall"] = r2[CRIT].mean(axis=1)
m["human_overall"] = (m["r1_overall"] + m["r2_overall"]) / 2
key = key.rename(columns={"overall_score": "judge_overall",
                          "contradiction_flag": "judge_CF",
                          "error_label": "judge_error_label"})
m = m.merge(key, on="sample_id")
m["turn"] = m["record_id"].str.extract(r"_t(\d)$").astype(int)
m.to_csv(os.path.join(OUT, "human_eval_merged.csv"), index=False, encoding="utf-8-sig")

# ---------- helpers ----------
def weighted_kappa(a, b, kmin=1, kmax=5):
    """Cohen's kappa, quadratic weights."""
    cats = list(range(kmin, kmax + 1))
    n = len(a)
    obs = pd.crosstab(pd.Categorical(a, cats), pd.Categorical(b, cats), dropna=False).values
    w = np.array([[(i - j) ** 2 for j in cats] for i in cats], float) / (kmax - kmin) ** 2
    pa, pb = obs.sum(1) / n, obs.sum(0) / n
    exp = np.outer(pa, pb) * n
    return 1 - (w * obs).sum() / (w * exp).sum()

def cohen_kappa(a, b):
    cats = sorted(set(a) | set(b))
    obs = pd.crosstab(pd.Categorical(a, cats), pd.Categorical(b, cats), dropna=False).values
    n = obs.sum()
    po = np.trace(obs) / n
    pe = (obs.sum(1) * obs.sum(0)).sum() / n ** 2
    return (po - pe) / (1 - pe) if pe < 1 else np.nan

# ---------- 2) inter-rater agreement ----------
rows = []
for c in CRIT:
    a, b = m[f"r1_{c}"], m[f"r2_{c}"]
    rho, p = stats.spearmanr(a, b)
    rows.append({"measure": c, "type": "ordinal 1-5",
                 "exact_agree_pct": round(100 * (a == b).mean(), 1),
                 "within1_agree_pct": round(100 * ((a - b).abs() <= 1).mean(), 1),
                 "spearman_rho": round(rho, 3), "spearman_p": f"{p:.2e}",
                 "weighted_kappa_quadratic": round(weighted_kappa(a, b), 3)})
a, b = m["r1_CF"], m["r2_CF"]
rows.append({"measure": "CF", "type": "binary 0/1",
             "exact_agree_pct": round(100 * (a == b).mean(), 1),
             "within1_agree_pct": np.nan, "spearman_rho": np.nan, "spearman_p": "",
             "weighted_kappa_quadratic": round(cohen_kappa(a, b), 3)})
a, b = m["r1_error_label"], m["r2_error_label"]
rows.append({"measure": "error_label", "type": "nominal 9 lop",
             "exact_agree_pct": round(100 * (a == b).mean(), 1),
             "within1_agree_pct": np.nan, "spearman_rho": np.nan, "spearman_p": "",
             "weighted_kappa_quadratic": round(cohen_kappa(a, b), 3)})
a, b = (m["r1_error_label"] != "none"), (m["r2_error_label"] != "none")
rows.append({"measure": "error_binary (loi/khong loi)", "type": "binary",
             "exact_agree_pct": round(100 * (a == b).mean(), 1),
             "within1_agree_pct": np.nan, "spearman_rho": np.nan, "spearman_p": "",
             "weighted_kappa_quadratic": round(cohen_kappa(a, b), 3)})
agree = pd.DataFrame(rows)
agree.to_csv(os.path.join(OUT, "interrater_agreement.csv"), index=False, encoding="utf-8-sig")

# ---------- 3) human vs judge ----------
rows = []
for name, col in [("giao vien 1", "r1_overall"), ("giao vien 2", "r2_overall"),
                  ("human mean", "human_overall")]:
    rho, p = stats.spearmanr(m[col], m["judge_overall"])
    pear, _ = stats.pearsonr(m[col], m["judge_overall"])
    rows.append({"comparison": f"{name} overall vs judge overall",
                 "spearman_rho": round(rho, 3), "pearson_r": round(pear, 3), "p": f"{p:.2e}"})
hj = pd.DataFrame(rows)
extra = []
for name, col in [("rater1", "r1_CF"), ("rater2", "r2_CF")]:
    extra.append({"comparison": f"{name} CF vs judge contradiction_flag",
                  "spearman_rho": np.nan,
                  "pearson_r": round(cohen_kappa(m[col], m["judge_CF"]), 3), "p": "kappa"})
for name, col in [("rater1", "r1_error_label"), ("rater2", "r2_error_label")]:
    extra.append({"comparison": f"{name} error_label vs judge error_label (exact %)",
                  "spearman_rho": np.nan,
                  "pearson_r": round(100 * (m[col] == m["judge_error_label"]).mean(), 1), "p": "%"})
hj = pd.concat([hj, pd.DataFrame(extra)], ignore_index=True)
hj.to_csv(os.path.join(OUT, "human_vs_judge.csv"), index=False, encoding="utf-8-sig")

# ---------- 4) summaries ----------
def summarize(by):
    g = m.groupby(by)
    out = g.agg(n=("sample_id", "count"))
    for pre in ["r1", "r2"]:
        for c in CRIT:
            out[f"{pre}_{c}_mean"] = g[f"{pre}_{c}"].mean().round(2)
        out[f"{pre}_overall_mean"] = g[f"{pre}_overall"].mean().round(2)
        out[f"{pre}_CF_rate"] = g[f"{pre}_CF"].mean().round(3)
        out[f"{pre}_error_rate"] = g[f"{pre}_error_label"].apply(lambda s: (s != "none").mean()).round(3)
    out["human_overall_mean"] = g["human_overall"].mean().round(2)
    out["human_overall_sd"] = g["human_overall"].std().round(2)
    out["judge_overall_mean"] = g["judge_overall"].mean().round(2)
    out["judge_CF_rate"] = g["judge_CF"].mean().round(3)
    return out.reset_index()

summarize("condition").to_csv(os.path.join(OUT, "human_summary_by_condition.csv"), index=False, encoding="utf-8-sig")
summarize("persona_id").to_csv(os.path.join(OUT, "human_summary_by_persona.csv"), index=False, encoding="utf-8-sig")
summarize("scenario_id").to_csv(os.path.join(OUT, "human_summary_by_scenario.csv"), index=False, encoding="utf-8-sig")
summarize("turn").to_csv(os.path.join(OUT, "human_summary_by_turn.csv"), index=False, encoding="utf-8-sig")

# ---------- 5) error labels ----------
labels = sorted(set(m["r1_error_label"]) | set(m["r2_error_label"]) | set(m["judge_error_label"]))
dist = pd.DataFrame({
    "error_label": labels,
    "giao_vien_1": [int((m["r1_error_label"] == l).sum()) for l in labels],
    "giao_vien_2": [int((m["r2_error_label"] == l).sum()) for l in labels],
    "judge_LLM": [int((m["judge_error_label"] == l).sum()) for l in labels],
})
dist.to_csv(os.path.join(OUT, "error_label_distribution.csv"), index=False, encoding="utf-8-sig")
conf = pd.crosstab(m["r1_error_label"], m["r2_error_label"])
conf.to_csv(os.path.join(OUT, "error_label_confusion_r1_vs_r2.csv"), encoding="utf-8-sig")

# ---------- 6) statistical tests (human_overall across conditions) ----------
conds = sorted(m["condition"].unique())
groups = [m.loc[m.condition == c, "human_overall"] for c in conds]
H, p_kw = stats.kruskal(*groups)
tests = [{"test": "Kruskal-Wallis human_overall ~ condition",
          "stat": round(H, 3), "p": f"{p_kw:.2e}", "note": "df=%d" % (len(conds) - 1)}]
pvals, pairs = [], []
for c in conds:
    if c == "B0":
        continue
    u, p = stats.mannwhitneyu(m.loc[m.condition == "B0", "human_overall"],
                              m.loc[m.condition == c, "human_overall"], alternative="two-sided")
    pairs.append((c, u)); pvals.append(p)
order = np.argsort(pvals)  # Holm correction
holm = [None] * len(pvals)
for rank, idx in enumerate(order):
    holm[idx] = min(1.0, pvals[idx] * (len(pvals) - rank))
for (c, u), p, ph in zip(pairs, pvals, holm):
    d1 = m.loc[m.condition == "B0", "human_overall"]; d2 = m.loc[m.condition == c, "human_overall"]
    tests.append({"test": f"Mann-Whitney B0 vs {c} (human_overall)", "stat": round(u, 1),
                  "p": f"{p:.2e}", "note": f"p_holm={ph:.2e}; mean B0={d1.mean():.2f} vs {c}={d2.mean():.2f}"})
pd.DataFrame(tests).to_csv(os.path.join(OUT, "statistical_tests_human.csv"), index=False, encoding="utf-8-sig")

print("CSV done. n =", len(m))
print(agree.to_string(index=False))
print(summarize("condition")[["condition", "n", "r1_overall_mean", "r2_overall_mean",
                              "human_overall_mean", "judge_overall_mean"]].to_string(index=False))
