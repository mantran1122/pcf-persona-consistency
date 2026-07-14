# PCF Ablation Experiment v2

Thực nghiệm đánh giá Persona Consistency Framework (PCF), thiết kế lại theo
`Ke_hoach_code_lai_thuc_nghiem_PCF.md`: có baseline, ablation, multiple runs,
counterbalancing, human evaluation và thống kê phi tham số.

## Thiết kế

| Điều kiện | Input cho generator |
|---|---|
| B0 | history + user input (không persona) |
| C1 | persona system prompt + history + user input |
| C2 | C1 + structured memory block (khác C1 **duy nhất** ở memory) |
| C3 (tùy chọn) | C2 + verification accept/revise/reject |

Quy mô mặc định: 6 persona × 5 scenario × 4 turn × 3 run × 3 condition = **1.080 response**
(bỏ B0 còn 720). Thứ tự scenario counterbalance bằng **Williams design 10 hàng**
(cân bằng cả vị trí lẫn carryover bậc 1 — mỗi cặp thứ tự liền kề xuất hiện đúng 2 lần):
`order_index = (persona_index * num_runs + run_index) % 10`.

- Generator: `gpt-4o-mini-2024-07-18` (temperature 0.7)
- Judge: `claude-haiku-4-5` (temperature 0, khác họ model với generator; $1/$5 per MTok)
- Error label của judge là **LLM-inferred error label**, không phải ground truth.

## Cấu trúc

```
config/     experiment_config.json, model_config.json, rubric.json
data/       personas.json (6), scenarios.json (5×4 turn), domain_questions.json, latin_square_orders.json
prompts/    generator_system, generator_memory, memory_update, verification, judge
src/        load_config, build_dialogues, generate_responses, memory_manager,
            verifier, judge_responses, sample_for_human_eval, analyze_results, utils
tests/      test_counterbalance.py (Latin square + C1/C2 isolation + render tests)
notebooks/  run_experiment.ipynb (điều phối toàn pipeline)
outputs/    raw_responses/ judged_responses/ verified_responses/
            human_annotations/ summaries/ figures/ logs/
```

## Chạy

```bash
pip install -r requirements.txt

# 1) Kiểm tra pipeline không cần API key (dữ liệu giả):
DRY_RUN=1 python -m src.generate_responses
DRY_RUN=1 python -m src.judge_responses

# 2) Chạy thật:
export OPENAI_API_KEY=...
export ANTHROPIC_API_KEY=...
python -m src.generate_responses   # resume-safe: chạy lại sẽ bỏ qua record đã có
python -m src.judge_responses
python -m src.sample_for_human_eval
python -m src.analyze_results
```

Hoặc mở `notebooks/run_experiment.ipynb` (chạy được trên Colab: upload cả thư mục,
đặt key qua `google.colab.userdata`). Đặt `PILOT_MODE = True` để chạy thử
1 persona × 1 condition trước khi chạy toàn bộ (checklist mục H).

## Human evaluation

`sample_for_human_eval` xuất 2 sheet mù (không có condition/model/điểm judge) tại
`outputs/human_annotations/human_evaluation_sheet_rater{1,2}.csv`, kèm
`unblinding_key.csv` (giữ kín đến khi tính agreement). Mẫu phân tầng theo
condition × persona × scenario, gồm toàn bộ case CF=1 + case điểm thấp/cao nhất
mỗi stratum. Sau khi chấm xong chạy `analyze_results.compute_agreement(...)` để có
weighted Cohen's κ (PC/MR/SS/CA), κ cho CF và error label, và human–LLM agreement.

## Thống kê

Đơn vị phân tích chính là **dialogue** (persona × run, lấy mean) để tránh giả định
các turn độc lập; phân tích theo turn báo cáo là exploratory. Wilcoxon signed-rank
cho từng cặp condition + hiệu chỉnh Holm, Friedman + Kendall's W khi ≥3 condition,
effect size rank-biserial, Wilson 95% CI cho contradiction rate.

## Reproducibility

`outputs/summaries/environment_snapshot.json` lưu Python/SDK versions, model snapshot
ID, toàn bộ config và timestamp. Mỗi response lưu system prompt, memory state
trước/sau, latency, retry count, token usage. API key chỉ qua biến môi trường.
