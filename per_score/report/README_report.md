# Kết quả Human Evaluation — bộ file cho báo cáo

Sinh từ 2 file chấm (Giáo viên 1, Giáo viên 2) + `unblinding_key.csv`
(condition + điểm LLM judge). n = 513 mẫu, 6 persona × 5 scenario, 5 điều kiện
(B0, C1, C2, C3, C4). Tái tạo: chạy `per_score/make_report_files.py` rồi
`per_score/make_report_figures.py`.

## File dữ liệu

| File | Nội dung |
|---|---|
| `human_eval_merged.csv` | Bảng gộp từng mẫu: điểm PC/MR/SS/CA/CF + error_label của cả 2 giáo viên, overall từng người, human_overall (trung bình 2 người), condition/run/turn, điểm judge. **Đây là file dữ liệu gốc cho mọi phân tích.** |
| `interrater_agreement.csv` | Đồng thuận 2 giáo viên: % trùng khớp, % lệch ≤1, Spearman ρ, Cohen's κ (trọng số bậc hai cho thang 1–5). |
| `human_vs_judge.csv` | Validity của LLM judge: tương quan human↔judge (overall), κ trên cờ mâu thuẫn, % trùng nhãn lỗi. |
| `human_summary_by_condition.csv` | Trung bình từng tiêu chí, CF rate, error rate theo **điều kiện** — bảng chính của báo cáo. |
| `human_summary_by_persona.csv` / `..._by_scenario.csv` / `..._by_turn.csv` | Như trên, cắt theo persona / scenario / vị trí lượt. |
| `error_label_distribution.csv` | Đếm nhãn lỗi theo 3 nguồn (giáo viên 1 / giáo viên 2 / judge). |
| `error_label_confusion_r1_vs_r2.csv` | Ma trận nhầm lẫn nhãn lỗi giữa 2 giáo viên. |
| `statistical_tests_human.csv` | Kruskal–Wallis (human_overall ~ condition) + Mann–Whitney B0 vs C1..C4, hiệu chỉnh Holm. |

## Hình

| File | Nội dung |
|---|---|
| `figH1_overall_by_condition.png` | Điểm tổng hợp theo điều kiện, 3 nguồn đánh giá. |
| `figH2_interrater_kappa.png` | κ giữa 2 giáo viên theo từng tiêu chí. |
| `figH3_error_labels.png` | Phân bố nhãn lỗi theo nguồn. |
| `figH4_human_vs_judge.png` | Scatter human overall vs judge overall (ρ = 0.46). |
| `figH5_error_rate_by_condition.png` | % mẫu bị gán lỗi theo điều kiện. |

## Kết quả chính (tóm tắt để viết báo cáo)

1. **Thứ tự điều kiện nhất quán ở cả 3 nguồn đánh giá:** B0 < C1 < C2 < C3 ≈ C4
   (human_overall: 3.80 → 4.29 → 4.37 → 4.82 / 4.80). Kruskal–Wallis p ≪ 0.001;
   mọi so sánh B0 vs C* đều có ý nghĩa sau hiệu chỉnh Holm (xem `statistical_tests_human.csv`).
2. **Đồng thuận 2 giáo viên ở mức khá–tốt:** κw = 0.63 (PC), 0.74 (SS), 0.59 (CA);
   nhãn lỗi κ = 0.58 (trùng 79.1%). MR κ≈0 là artefact do điểm Giáo viên 1 gần như hằng số
   (502/513 điểm 5; trùng khớp thô 92.6%). CF κ = 0.27 — hai người hiểu ngưỡng cắm cờ khác nhau,
   nên báo cáo kèm % thô (79.5%).
3. **LLM judge khắt khe hơn người** (thấp hơn ~0.5–1.2 điểm tuỳ điều kiện; gán lỗi 84% ở B0
   so với 50–63% của người) nhưng **xếp hạng điều kiện giống hệt** — dùng judge làm thước đo
   tương đối giữa các điều kiện là hợp lệ, không dùng làm điểm tuyệt đối.
   Judge lạm dụng nhãn `constraint_violation` (106 mẫu) và `role_breaking` (53) so với người.
4. Lỗi phổ biến nhất theo cả 2 giáo viên: `style_drift` (83/73), rồi `domain_drift` (30/51).
