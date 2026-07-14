# -*- coding: utf-8 -*-
"""Vẽ các hình cho báo cáo human evaluation -> per_score/report/*.png"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "report")
m = pd.read_csv(os.path.join(OUT, "human_eval_merged.csv"))
agree = pd.read_csv(os.path.join(OUT, "interrater_agreement.csv"))

# palette đã validate (light mode): r1=blue, r2=aqua, judge=yellow
C_R1, C_R2, C_JUDGE, C_VIOLET, C_RED = "#2a78d6", "#1baf7a", "#eda100", "#4a3aa7", "#e34948"
SURFACE, INK, INK2 = "#fcfcfb", "#0b0b0b", "#52514e"
plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "text.color": INK, "axes.edgecolor": INK2, "axes.labelcolor": INK,
    "xtick.color": INK2, "ytick.color": INK2, "font.size": 10.5,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#e8e7e3", "grid.linewidth": 0.6, "axes.axisbelow": True,
    "figure.dpi": 150,
})
CONDS = ["B0", "C1", "C2", "C3", "C4"]

def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, name), bbox_inches="tight")
    plt.close(fig)
    print("saved", name)

# ---- fig H1: overall theo condition, 3 nguồn đánh giá ----
g = m.groupby("condition")[["r1_overall", "r2_overall", "judge_overall"]].mean().reindex(CONDS)
fig, ax = plt.subplots(figsize=(7.2, 3.8))
x = np.arange(len(CONDS)); w = 0.26
for off, col, color, lab in [(-w, "r1_overall", C_R1, "Giáo viên 1"),
                             (0, "r2_overall", C_R2, "Giáo viên 2"),
                             (w, "judge_overall", C_JUDGE, "LLM judge")]:
    bars = ax.bar(x + off, g[col], width=w - 0.03, color=color, label=lab, zorder=3)
    for b, v in zip(bars, g[col]):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.06, f"{v:.2f}",
                ha="center", va="bottom", fontsize=8.5, color=INK2)
ax.set_xticks(x); ax.set_xticklabels(CONDS)
ax.set_ylim(0, 5.9); ax.set_ylabel("Điểm tổng hợp trung bình (1–5)")
ax.set_title("Điểm tổng hợp theo điều kiện — hai người chấm và LLM judge", loc="left", fontsize=11.5)
ax.grid(axis="x", visible=False)
ax.legend(frameon=False, loc="upper left", ncols=3, fontsize=9)
save(fig, "figH1_overall_by_condition.png")

# ---- fig H2: đồng thuận giữa 2 người chấm ----
sub = agree[agree.measure.isin(["PC", "MR", "SS", "CA", "CF", "error_label"])]
fig, ax = plt.subplots(figsize=(7.2, 3.4))
x = np.arange(len(sub))
bars = ax.bar(x, sub["weighted_kappa_quadratic"], width=0.5, color=C_R1, zorder=3)
for b, v in zip(bars, sub["weighted_kappa_quadratic"]):
    ax.text(b.get_x() + b.get_width() / 2, v + (0.02 if v >= 0 else -0.06),
            f"{v:.2f}", ha="center", va="bottom" if v >= 0 else "top", fontsize=9, color=INK2)
ax.axhline(0, color=INK2, lw=0.8)
ax.set_xticks(x)
ax.set_xticklabels(["PC", "MR*", "SS", "CA", "CF", "error\nlabel"])
ax.set_ylim(-0.15, 1.0); ax.set_ylabel("Cohen's κ")
ax.set_title("Đồng thuận giữa hai người chấm — Cohen's κ (PC/MR/SS/CA có trọng số bậc hai)", loc="left", fontsize=11)
ax.grid(axis="x", visible=False)
fig.text(0.01, -0.04, "*MR: κ≈0 do điểm Giáo viên 1 gần như hằng số (502/513 điểm 5), không phải bất đồng thực sự — exact agreement 92.6%.",
         ha="left", fontsize=8, color=INK2)
save(fig, "figH2_interrater_kappa.png")

# ---- fig H3: phân bố error label theo nguồn ----
dist = pd.read_csv(os.path.join(OUT, "error_label_distribution.csv"))
dist = dist[dist.error_label != "none"].sort_values("giao_vien_2", ascending=True)
fig, ax = plt.subplots(figsize=(7.2, 4.2))
y = np.arange(len(dist)); h = 0.26
for off, col, color, lab in [(h, "giao_vien_1", C_R1, "Giáo viên 1"),
                             (0, "giao_vien_2", C_R2, "Giáo viên 2"),
                             (-h, "judge_LLM", C_JUDGE, "LLM judge")]:
    ax.barh(y + off, dist[col], height=h - 0.03, color=color, label=lab, zorder=3)
    for yi, v in zip(y + off, dist[col]):
        if v > 0:
            ax.text(v + 1, yi, str(v), va="center", fontsize=8, color=INK2)
ax.set_yticks(y); ax.set_yticklabels(dist["error_label"])
ax.set_xlabel("Số mẫu bị gán nhãn (trên 513)")
ax.set_title("Phân bố nhãn lỗi (trừ 'none') theo nguồn đánh giá", loc="left", fontsize=11.5)
ax.grid(axis="y", visible=False)
ax.set_xlim(0, dist[["giao_vien_1","giao_vien_2","judge_LLM"]].values.max()*1.12)
ax.legend(frameon=False, loc="center right", bbox_to_anchor=(1.0, 0.55), fontsize=9)
save(fig, "figH3_error_labels.png")

# ---- fig H4: human vs judge scatter ----
fig, ax = plt.subplots(figsize=(5.4, 5))
rng = np.random.default_rng(17)
jx = m["human_overall"] + rng.uniform(-0.06, 0.06, len(m))
jy = m["judge_overall"] + rng.uniform(-0.06, 0.06, len(m))
ax.scatter(jx, jy, s=14, color=C_R1, alpha=0.35, edgecolors="none", zorder=3)
ax.plot([1, 5], [1, 5], color=INK2, lw=1, ls="--", zorder=2)
from scipy import stats as st
rho, _ = st.spearmanr(m["human_overall"], m["judge_overall"])
ax.text(0.03, 0.95, f"Spearman ρ = {rho:.2f} (n = {len(m)})", transform=ax.transAxes, fontsize=10)
ax.set_xlim(0.8, 5.2); ax.set_ylim(0.8, 5.2)
ax.set_xlabel("Human overall (trung bình 2 người chấm)")
ax.set_ylabel("LLM judge overall")
ax.set_title("Điểm người chấm vs điểm judge", loc="left", fontsize=11.5)
save(fig, "figH4_human_vs_judge.png")

# ---- fig H5: tỉ lệ lỗi & CF theo condition ----
g = m.groupby("condition").agg(
    r1_err=("r1_error_label", lambda s: (s != "none").mean()),
    r2_err=("r2_error_label", lambda s: (s != "none").mean()),
    judge_err=("judge_error_label", lambda s: (s != "none").mean())).reindex(CONDS)
fig, ax = plt.subplots(figsize=(7.2, 3.8))
x = np.arange(len(CONDS))
for col, color, lab, mk in [("r1_err", C_R1, "Giáo viên 1", "o"),
                            ("r2_err", C_R2, "Giáo viên 2", "s"),
                            ("judge_err", C_JUDGE, "LLM judge", "^")]:
    ax.plot(x, 100 * g[col], color=color, lw=2, marker=mk, ms=6, label=lab, zorder=3)
    ax.annotate(lab.split(" (")[0], (x[-1], 100 * g[col].iloc[-1]),
                xytext=(8, 0), textcoords="offset points", va="center", fontsize=8.5, color=color)
ax.set_xticks(x); ax.set_xticklabels(CONDS)
ax.set_ylabel("% mẫu có nhãn lỗi (≠ none)"); ax.set_ylim(0, None)
ax.set_xlim(-0.3, len(CONDS) - 0.3 + 1.0)
ax.set_title("Tỉ lệ mẫu bị gán lỗi theo điều kiện", loc="left", fontsize=11.5)
ax.grid(axis="x", visible=False)
ax.legend(frameon=False, fontsize=9)
save(fig, "figH5_error_rate_by_condition.png")
print("figures done")
