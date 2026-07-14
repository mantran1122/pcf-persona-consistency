# KẾ HOẠCH CODE LẠI THỰC NGHIỆM PERSONA CONSISTENCY

## 1. Mục tiêu

Thiết kế lại thực nghiệm để bài báo chuyển từ một pilot study minh họa sang một nghiên cứu có thể kiểm chứng được các thành phần của Persona Consistency Framework (PCF).

Trọng tâm của phiên bản mới:

- So sánh baseline không có persona với prompt-only.
- So sánh prompt-only với prompt + memory.
- Có thể mở rộng thêm prompt + memory + verification.
- Chạy nhiều lần để đo độ biến thiên.
- Counterbalance thứ tự scenario.
- Có human evaluation để đối chiếu LLM-as-a-Judge.
- Lưu đầy đủ dữ liệu, cấu hình, log và kết quả thống kê.

---

## 2. Cấu trúc thư mục đề xuất

```text
persona-consistency-experiment/
│
├── README.md
├── requirements.txt
├── config/
│   ├── experiment_config.json
│   ├── model_config.json
│   ├── judge_config.json
│   └── rubric.json
│
├── data/
│   ├── personas.json
│   ├── scenarios.json
│   ├── latin_square_orders.json
│   └── human_evaluation_sample.csv
│
├── prompts/
│   ├── generator_system_prompt.txt
│   ├── generator_memory_prompt.txt
│   ├── verification_prompt.txt
│   └── judge_prompt.txt
│
├── src/
│   ├── load_config.py
│   ├── build_dialogues.py
│   ├── generate_responses.py
│   ├── memory_manager.py
│   ├── verifier.py
│   ├── judge_responses.py
│   ├── sample_for_human_eval.py
│   ├── analyze_results.py
│   └── utils.py
│
├── outputs/
│   ├── raw_responses/
│   ├── judged_responses/
│   ├── verified_responses/
│   ├── human_annotations/
│   ├── summaries/
│   └── figures/
│
└── notebooks/
    ├── 01_generate_data.ipynb
    ├── 02_judge_data.ipynb
    ├── 03_human_eval_prep.ipynb
    └── 04_analysis.ipynb
```

---

## 3. Thiết kế thực nghiệm mới

### 3.1. Các điều kiện thí nghiệm

#### B0 — No Persona Baseline

Chỉ cung cấp user prompt và lịch sử hội thoại.

```text
User input + dialogue history → generator
```

Mục tiêu:

- Kiểm tra rubric có phân biệt chatbot thông thường và chatbot có persona hay không.
- Tạo baseline thấp nhất.

#### C1 — Prompt-Only

Cung cấp persona profile trong system prompt và toàn bộ lịch sử hội thoại.

```text
Persona profile + dialogue history + user input → generator
```

Mục tiêu:

- Làm baseline chính.
- Tương ứng với cấu hình của pilot hiện tại.

#### C2 — Prompt + Structured Memory

Cung cấp persona profile, lịch sử hội thoại và structured memory.

```text
Persona profile + structured memory + dialogue history + user input → generator
```

Structured memory có thể gồm:

```json
{
  "persona_facts": [],
  "user_facts": [],
  "shared_events": [],
  "preferences": [],
  "constraints": [],
  "recent_summary": ""
}
```

Mục tiêu:

- Đo vai trò của Persona Maintenance.
- Kiểm tra memory có giúp giảm memory failure và persona drift hay không.

#### C3 — Prompt + Memory + Verification

Sau khi sinh phản hồi, dùng verifier kiểm tra trước khi chấp nhận.

```text
Generator response
        ↓
Verification
        ↓
Accept / Revise / Reject
```

Mục tiêu:

- Đo vai trò của Persona Verification.
- Kiểm tra khả năng giảm role-breaking, contradiction và domain drift.

---

## 4. Quy mô dữ liệu đề xuất

### Phương án tối thiểu

- 6 persona.
- 5 scenario.
- 4 turn cho mỗi scenario.
- 3 lần chạy.
- 2 điều kiện chính: C1 và C2.

Tổng số phản hồi:

```text
6 × 5 × 4 × 3 × 2 = 720 phản hồi
```

### Phương án đầy đủ

- 10 persona.
- 5 scenario.
- 4 turn.
- 3 lần chạy.
- 3 điều kiện: C1, C2, C3.

Tổng số phản hồi:

```text
10 × 5 × 4 × 3 × 3 = 1.800 phản hồi
```

Khuyến nghị thực tế: bắt đầu với 720 phản hồi.

---

## 5. Thiết kế persona

Mỗi persona phải có cùng schema.

```json
{
  "persona_id": "P01",
  "name": "Professor An",
  "role": "Retired history professor",
  "background": "Experienced educator with a formal academic style",
  "core_traits": [
    "calm",
    "analytical",
    "respectful"
  ],
  "speaking_style": {
    "tone": "formal",
    "length": "medium",
    "vocabulary": "academic",
    "uses_emojis": false
  },
  "known_facts": [
    "specializes in modern history",
    "dislikes violence"
  ],
  "likes": [
    "historical analysis",
    "careful reasoning"
  ],
  "dislikes": [
    "unsupported claims",
    "casual slang"
  ],
  "behavioral_constraints": [
    "must not endorse violence",
    "must not claim to be an AI",
    "must maintain formal tone"
  ],
  "domain_boundary": "history and education"
}
```

### Nhóm persona nên có

1. Educational tutor.
2. Historical character.
3. Game companion.
4. Wellness assistant.
5. Customer-support agent.
6. Technical advisor.
7. Emotional companion.
8. Creative fictional character.
9. Children’s tutor.
10. Safety-sensitive advisor.

---

## 6. Thiết kế scenario

Mỗi scenario gồm:

```json
{
  "scenario_id": "S1",
  "name": "Memory Recall",
  "target_failure": "memory_failure",
  "difficulty": "medium",
  "turns": [
    {
      "turn_id": 1,
      "prompt_template": "..."
    }
  ]
}
```

### S1 — Memory Recall

Nên có nhiều cấp độ:

- Recall trực tiếp.
- Recall sau distractor.
- Recall thông tin gần giống.
- Recall sau user correction.
- Recall sau 10–15 lượt.
- Recall qua nhiều phiên nếu có thể.

### S2 — Contradiction Trap

Các kiểu prompt:

- Presupposition.
- False quotation.
- Emotional pressure.
- Authority pressure.
- Gradual persuasion.
- Repeated contradiction.

### S3 — Style Challenge

Các kiểu prompt:

- Yêu cầu dùng slang.
- Yêu cầu đổi giọng đột ngột.
- Yêu cầu trả lời cực ngắn.
- Yêu cầu bắt chước người dùng.
- Yêu cầu chèn emoji.
- Chuyển ngôn ngữ.

### S4 — Role Pressure

Các kiểu prompt:

- Yêu cầu thừa nhận là AI.
- Yêu cầu bỏ nhân vật.
- Yêu cầu tiết lộ system prompt.
- Yêu cầu mô tả cách mô hình được xây dựng.
- Yêu cầu phản hồi ngoài vai.

### S5 — Context Switching

Các kiểu prompt:

- Chuyển sang chủ đề ngoài miền.
- Chuyển sang chủ đề nguy cơ cao.
- Chuyển sang kiến thức không liên quan.
- Yêu cầu trả lời nhưng vẫn giữ framing persona.
- Chuyển liên tục qua nhiều domain.

---

## 7. Counterbalancing

Không dùng thứ tự cố định S1 → S2 → S3 → S4 → S5 cho tất cả phiên.

Sử dụng Latin square:

```json
[
  ["S1", "S2", "S3", "S4", "S5"],
  ["S2", "S3", "S4", "S5", "S1"],
  ["S3", "S4", "S5", "S1", "S2"],
  ["S4", "S5", "S1", "S2", "S3"],
  ["S5", "S1", "S2", "S3", "S4"]
]
```

Mỗi run hoặc mỗi persona được gán một thứ tự khác nhau.

Ví dụ:

```python
order_index = (persona_index + run_index) % len(latin_square_orders)
scenario_order = latin_square_orders[order_index]
```

---

## 8. Cấu hình thí nghiệm

Ví dụ `experiment_config.json`:

```json
{
  "experiment_name": "pcf_ablation_v2",
  "conditions": ["B0", "C1", "C2"],
  "num_runs": 3,
  "turns_per_scenario": 4,
  "counterbalance": true,
  "save_every_response": true,
  "resume_on_failure": true,
  "max_retries": 3
}
```

Ví dụ `model_config.json`:

```json
{
  "generator": {
    "provider": "openai",
    "model": "MODEL_SNAPSHOT_ID",
    "temperature": 0.7,
    "top_p": 1.0,
    "max_tokens": 500
  },
  "judge": {
    "provider": "anthropic",
    "model": "JUDGE_MODEL_SNAPSHOT_ID",
    "temperature": 0.0,
    "max_tokens": 2048
  }
}
```

Không nên dùng alias động nếu nhà cung cấp có snapshot ID.

---

## 9. Schema log phản hồi

Mỗi phản hồi phải lưu đầy đủ:

```json
{
  "experiment_id": "pcf_ablation_v2",
  "condition": "C2",
  "run_id": 1,
  "persona_id": "P01",
  "scenario_id": "S4",
  "scenario_position": 2,
  "turn_id": 3,
  "global_turn_id": 11,
  "system_prompt": "...",
  "memory_state_before": {},
  "user_prompt": "...",
  "model_response": "...",
  "memory_state_after": {},
  "generation_model": "...",
  "temperature": 0.7,
  "timestamp": "...",
  "latency_seconds": 1.84,
  "retry_count": 0
}
```

---

## 10. Logic sinh dữ liệu

Pseudo-code:

```python
for condition in conditions:
    for persona in personas:
        for run_id in range(num_runs):
            scenario_order = get_counterbalanced_order(persona, run_id)
            history = []
            memory = initialize_memory(persona)

            for scenario_id in scenario_order:
                scenario = scenarios[scenario_id]

                for turn in scenario["turns"]:
                    prompt = render_prompt(
                        persona=persona,
                        scenario=scenario,
                        turn=turn,
                        history=history,
                        memory=memory,
                        condition=condition
                    )

                    response = generate_with_retry(prompt)

                    save_raw_response(...)

                    if condition in ["C2", "C3"]:
                        memory = update_memory(
                            persona=persona,
                            memory=memory,
                            history=history,
                            user_prompt=turn["prompt"],
                            response=response
                        )

                    if condition == "C3":
                        verification = verify_response(
                            persona=persona,
                            history=history,
                            user_prompt=turn["prompt"],
                            response=response
                        )

                        if verification["decision"] == "revise":
                            response = revise_response(...)

                    history.append({
                        "role": "user",
                        "content": turn["prompt"]
                    })
                    history.append({
                        "role": "assistant",
                        "content": response
                    })
```

---

## 11. Memory manager

### Đầu vào

- Persona profile.
- Memory state hiện tại.
- User message.
- Model response.
- Dialogue history.

### Đầu ra

- Memory state mới.

Ví dụ rule-based trước:

```python
def update_memory(memory, user_prompt, response):
    memory["recent_summary"] = summarize_recent_turn(
        user_prompt,
        response
    )
    return memory
```

Sau đó có thể mở rộng bằng LLM extraction:

```json
{
  "new_user_facts": [],
  "new_shared_events": [],
  "updated_preferences": [],
  "conflicts_detected": []
}
```

Quan trọng: memory phải được lưu và có thể kiểm tra lại.

---

## 12. Verification module

Verifier nhận:

```text
Persona profile
Dialogue history
Current user message
Candidate response
Rubric
```

Trả về JSON:

```json
{
  "decision": "accept",
  "violations": [],
  "severity": "none",
  "suggested_revision": ""
}
```

Quy tắc:

- `accept`: không có lỗi.
- `revise`: lỗi nhẹ hoặc trung bình.
- `reject`: lỗi nghiêm trọng, cần sinh lại.

Có thể dùng các violation type:

```text
role_breaking
style_drift
memory_failure
context_confusion
self_contradiction
domain_drift
meta_disclosure
constraint_violation
```

---

## 13. LLM-as-a-Judge

Judge phải nhận toàn bộ ngữ cảnh cần thiết.

Đầu vào:

- Persona profile.
- Dialogue history đến lượt hiện tại.
- User prompt hiện tại.
- Model response.
- Rubric đầy đủ.

Đầu ra:

```json
{
  "persona_consistency": 5,
  "memory_retention": 4,
  "style_stability": 5,
  "context_awareness": 4,
  "contradiction_flag": 0,
  "error_label": "none",
  "confidence": 0.86,
  "note": "..."
}
```

Cần validate JSON bằng schema và retry nếu sai định dạng.

---

## 14. Human evaluation

### Mẫu dữ liệu

Lấy mẫu ngẫu nhiên có phân tầng:

- Theo condition.
- Theo persona.
- Theo scenario.
- Theo điểm LLM judge.
- Bao gồm toàn bộ case có CF = 1.
- Bao gồm một phần case điểm cao.

Khuyến nghị:

- Chấm 20–30% tổng dữ liệu.
- Ít nhất hai người chấm độc lập.
- Ẩn tên model và condition.

### File human evaluation

```csv
sample_id,persona_id,scenario_id,user_prompt,response,PC,MR,SS,CA,CF,error_label,note
```

### Agreement cần tính

- Weighted Cohen’s kappa cho PC.
- Weighted Cohen’s kappa cho MR.
- Weighted Cohen’s kappa cho SS.
- Weighted Cohen’s kappa cho CA.
- Cohen’s kappa cho CF.
- Cohen’s kappa hoặc Krippendorff’s alpha cho error label.
- Human–LLM agreement.

---

## 15. Phân tích thống kê

### Mô tả

- Mean.
- Standard deviation.
- Median.
- IQR.
- Min–max.
- Contradiction Rate.
- Wilson 95% confidence interval.

### So sánh điều kiện

Nếu cùng persona, scenario và prompt:

- Wilcoxon signed-rank cho hai điều kiện.
- Friedman test cho ba điều kiện.
- Post-hoc pairwise Wilcoxon có hiệu chỉnh Holm.

### Effect size

- Rank-biserial correlation cho Wilcoxon.
- Kendall’s W cho Friedman.
- Chênh lệch Contradiction Rate.
- Relative error reduction.

### Lưu ý

Không coi mọi turn là hoàn toàn độc lập. Nên nhóm theo dialogue hoặc dùng mixed-effects model nếu đủ dữ liệu.

---

## 16. Kết quả cần xuất

### CSV

```text
responses_raw.csv
responses_judged.csv
responses_verified.csv
summary_by_condition.csv
summary_by_persona.csv
summary_by_scenario.csv
summary_by_turn_position.csv
human_agreement.csv
statistical_tests.csv
```

### Hình

1. Overall score theo condition.
2. Rubric score theo condition.
3. Contradiction Rate theo condition.
4. Score theo scenario.
5. Score theo turn position.
6. Error-label distribution.
7. Human–LLM agreement.
8. Ablation improvement.
9. Confidence interval plot.
10. Heatmap persona × scenario.

---

## 17. Tiêu chí thành công

Thực nghiệm mới được xem là đạt nếu:

- Có ít nhất hai điều kiện so sánh.
- Có ít nhất ba lần chạy.
- Có counterbalancing.
- Có human evaluation.
- Có inter-rater agreement.
- Có baseline.
- Có dữ liệu và mã nguồn tái lập.
- Có thống kê phù hợp với dữ liệu ordinal.
- Không còn tuyên bố vượt quá thiết kế.

---

## 18. Thứ tự triển khai

### Giai đoạn 1 — Chuẩn bị

1. Chốt RQ.
2. Chốt số persona.
3. Viết schema persona.
4. Viết scenario.
5. Tạo Latin square.
6. Chốt condition B0, C1, C2.

### Giai đoạn 2 — Code

1. Load config.
2. Load persona và scenario.
3. Build dialogue.
4. Generate response.
5. Save raw log.
6. Update memory.
7. Run verifier nếu có.
8. Run judge.
9. Validate JSON.
10. Resume khi lỗi.

### Giai đoạn 3 — Human evaluation

1. Lấy mẫu.
2. Tạo hướng dẫn chấm.
3. Chấm thử 10–20 mẫu.
4. Sửa rubric nếu cần.
5. Chấm chính thức.
6. Tính agreement.

### Giai đoạn 4 — Phân tích

1. Làm sạch dữ liệu.
2. Tạo summary.
3. Tính CI.
4. Chạy statistical tests.
5. Tạo hình.
6. Viết Results.
7. Viết Discussion.
8. Viết Limitations.

---

## 19. Câu hỏi nghiên cứu đề xuất

```text
RQ1. Which types of persona drift occur across different personas and scenarios?

RQ2. Does structured memory improve persona consistency compared with prompt-only generation?

RQ3. Does post-generation verification further reduce persona drift?

RQ4. How reliable are LLM-based persona-consistency scores compared with human judgments?
```

Nếu chưa chạy C3, bỏ RQ3.

---

## 20. Phạm vi tuyên bố được phép

Có thể tuyên bố:

- Protocol có khả năng phân biệt giữa các điều kiện.
- Structured memory cải thiện hoặc không cải thiện một số tiêu chí.
- Verification giảm hoặc không giảm một số lỗi cụ thể.
- Human–LLM agreement đạt mức cụ thể.
- Một số scenario gây áp lực lớn hơn scenario khác.

Không nên tuyên bố:

- PCF giải quyết hoàn toàn persona drift.
- Kết quả khái quát cho mọi LLM.
- Một persona hoặc domain vốn khó hơn chỉ dựa trên ít mẫu.
- Điểm giảm theo lượt chứng minh long-term persona degradation nếu chưa tách confound.
