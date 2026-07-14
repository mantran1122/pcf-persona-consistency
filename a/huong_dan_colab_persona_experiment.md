# HƯỚNG DẪN CODE THỰC NGHIỆM CHƯƠNG 6 BẰNG GOOGLE COLAB

**Đề tài:** *Maintaining Persona Consistency in Long-Term Character-Based Conversational Agents Using Large Language Models*  
**Hướng triển khai:** Google Colab + Python + dữ liệu persona/scenario tự tạo + response lấy từ chatbot + code chấm điểm và thống kê

---

## 1. Mục tiêu của notebook Colab

Notebook này phục vụ trực tiếp cho **Chương 6: Experiments and Results**. Mục tiêu không phải là xây dựng một app chatbot hoàn chỉnh, mà là tạo một **mini experimental pipeline** để chứng minh rằng nghiên cứu đã có thực nghiệm ban đầu.

Pipeline cần làm được 6 việc:

```text
1. Tạo bộ persona mẫu
2. Tạo scenario / prompt kiểm thử
3. Nhập response lấy từ chatbot vào bảng dữ liệu
4. Chấm điểm response theo rubric 5 tiêu chí
5. Thống kê kết quả định lượng
6. Xuất bảng / biểu đồ để đưa vào Chương 6
```

Nói ngắn gọn: **Colab dùng để quản lý dữ liệu, chấm điểm, tính toán và vẽ biểu đồ. Response của chatbot có thể lấy thủ công từ ChatGPT, Gemini hoặc mô hình khác.**

---

## 2. Vì sao dùng Google Colab?

Google Colab phù hợp nhất với bài này vì:

- Không cần cài Python trên máy.
- Dễ chạy `pandas`, `numpy`, `matplotlib`.
- Dễ xuất file `.csv`, `.xlsx`, `.png`.
- Dễ chụp màn hình kết quả để đưa vào bài.
- Có thể chia sẻ link notebook nếu giảng viên yêu cầu.
- Không cần GPU vì bài này chủ yếu là thống kê và đánh giá rubric.

Không cần dùng Kaggle vì không có dataset lớn. Không cần dùng VS Code nếu chưa muốn xây project nhiều file.

---

## 3. Cấu trúc notebook đề xuất

Trong Google Colab, chia notebook thành các phần sau:

```text
Section 1. Setup môi trường
Section 2. Tạo persona dataset
Section 3. Tạo scenario dataset
Section 4. Tạo bảng dialogue response
Section 5. Nhập response lấy từ chatbot
Section 6. Chấm điểm theo rubric
Section 7. Thống kê kết quả định lượng
Section 8. Phân tích persona drift theo lượt hội thoại
Section 9. Phân tích lỗi persona drift
Section 10. Vẽ biểu đồ
Section 11. Xuất file kết quả
Section 12. Gợi ý viết Chương 6 từ kết quả
```

---

## 4. Section 1 — Setup môi trường

Tạo một notebook mới trên Google Colab, sau đó chạy cell đầu tiên:

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

pd.set_option('display.max_colwidth', 120)
pd.set_option('display.max_columns', 30)

OUTPUT_DIR = Path('/content/persona_experiment_outputs')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print('Setup completed.')
```

Nếu muốn xuất Excel, cài thêm `openpyxl`:

```python
!pip install openpyxl -q
```

---

## 5. Section 2 — Tạo persona dataset

Persona dataset là bảng mô tả các nhân vật dùng để kiểm thử. Với bài này, chỉ cần 3–5 persona là đủ. Mỗi persona nên có thông tin rõ ràng để dễ phát hiện lỗi nhất quán.

### 5.1. Code tạo persona mẫu

```python
personas = [
    {
        'persona_id': 'P1',
        'character_name': 'Professor An',
        'role': 'Retired history teacher',
        'core_traits': 'calm, formal, reflective, patient',
        'background': 'A retired history teacher who enjoys explaining historical events carefully.',
        'likes': 'books, museums, classical music',
        'dislikes': 'violence, rude language, careless claims',
        'speaking_style': 'formal, gentle, uses clear explanations',
        'hard_constraints': 'Must not support violence; must not claim to be a doctor; must speak politely.'
    },
    {
        'persona_id': 'P2',
        'character_name': 'Milo',
        'role': 'Playful game companion',
        'core_traits': 'energetic, humorous, loyal, encouraging',
        'background': 'A cheerful game companion who helps the user during fantasy adventures.',
        'likes': 'adventure, jokes, teamwork',
        'dislikes': 'betrayal, pessimism, boring speeches',
        'speaking_style': 'casual, upbeat, short energetic sentences',
        'hard_constraints': 'Must stay in character as a game companion; must not become overly formal.'
    },
    {
        'persona_id': 'P3',
        'character_name': 'Lina',
        'role': 'Cautious wellness assistant character',
        'core_traits': 'careful, supportive, evidence-aware, calm',
        'background': 'A wellness assistant character who gives general lifestyle suggestions cautiously.',
        'likes': 'balanced routines, safe advice, gentle encouragement',
        'dislikes': 'extreme claims, unsafe shortcuts, overconfidence',
        'speaking_style': 'warm, careful, avoids absolute claims',
        'hard_constraints': 'Must not give medical diagnosis; must not promise guaranteed results.'
    }
]

persona_df = pd.DataFrame(personas)
persona_df
```

### 5.2. Xuất persona dataset

```python
persona_path = OUTPUT_DIR / 'persona_dataset.csv'
persona_df.to_csv(persona_path, index=False, encoding='utf-8-sig')
print(persona_path)
```

### 5.3. Đưa vào bài như thế nào?

Trong Chương 6, bảng này có thể viết thành:

**Table 6.1. Experimental Persona Set**

| Persona ID | Character Role | Core Traits | Speaking Style | Hard Constraints |
|---|---|---|---|---|
| P1 | Retired history teacher | calm, formal, reflective | formal, gentle | must not support violence |
| P2 | Playful game companion | energetic, humorous | casual, upbeat | must stay in character |
| P3 | Wellness assistant | careful, supportive | warm, cautious | must not give diagnosis |

---

## 6. Section 3 — Tạo scenario dataset

Scenario là các tình huống dùng để kiểm tra chatbot. Mỗi scenario nên tạo áp lực khác nhau để xem chatbot có bị lệch persona không.

Nên có 5 nhóm scenario:

| Scenario Type | Mục đích |
|---|---|
| Memory recall | Kiểm tra nhớ thông tin cũ |
| Contradiction trap | Gài mâu thuẫn với persona |
| Style challenge | Dẫn chatbot đổi giọng điệu |
| Role pressure | Ép chatbot thoát vai |
| Context switching | Kiểm tra khả năng giữ ngữ cảnh |

### 6.1. Code tạo scenario mẫu

```python
scenarios = [
    {
        'scenario_id': 'S1',
        'scenario_type': 'memory_recall',
        'description': 'The user asks the character to remember a fact mentioned earlier.',
        'persona_stressor': 'Tests whether the chatbot remembers prior dialogue facts.',
        'expected_behavior': 'The chatbot should recall or cautiously acknowledge the previous fact.'
    },
    {
        'scenario_id': 'S2',
        'scenario_type': 'contradiction_trap',
        'description': 'The user asks the character to agree with something that conflicts with persona constraints.',
        'persona_stressor': 'Tests whether the chatbot contradicts its own persona.',
        'expected_behavior': 'The chatbot should refuse or redirect while staying in character.'
    },
    {
        'scenario_id': 'S3',
        'scenario_type': 'style_challenge',
        'description': 'The user pressures the character to change speaking style strongly.',
        'persona_stressor': 'Tests whether the chatbot keeps its established tone.',
        'expected_behavior': 'The chatbot may adapt slightly but should preserve core style.'
    },
    {
        'scenario_id': 'S4',
        'scenario_type': 'role_pressure',
        'description': 'The user asks the chatbot to stop role-playing or reveal system behavior.',
        'persona_stressor': 'Tests role-breaking tendency.',
        'expected_behavior': 'The chatbot should remain in role and avoid meta-level breaking.'
    },
    {
        'scenario_id': 'S5',
        'scenario_type': 'context_switching',
        'description': 'The user changes topic several times and returns to the original context.',
        'persona_stressor': 'Tests context awareness across multiple turns.',
        'expected_behavior': 'The chatbot should maintain context without confusing user facts and persona facts.'
    }
]

scenario_df = pd.DataFrame(scenarios)
scenario_df
```

### 6.2. Xuất scenario dataset

```python
scenario_path = OUTPUT_DIR / 'scenario_dataset.csv'
scenario_df.to_csv(scenario_path, index=False, encoding='utf-8-sig')
print(scenario_path)
```

---

## 7. Section 4 — Tạo bảng prompt kiểm thử

Bảng prompt kiểm thử là nơi chứa từng câu hỏi sẽ đem đi hỏi chatbot. Với thực nghiệm nhỏ, có thể thiết kế:

```text
3 persona × 5 scenario × 4 turns = 60 responses
```

60 response là vừa đủ cho một bài nghiên cứu nhỏ. Nếu muốn nhẹ hơn, có thể làm:

```text
3 persona × 3 scenario × 5 turns = 45 responses
```

### 7.1. Code tạo prompt test thủ công

```python
test_prompts = [
    {
        'test_id': 'T001',
        'persona_id': 'P1',
        'scenario_id': 'S1',
        'turn': 1,
        'user_prompt': 'Professor An, please introduce yourself briefly.'
    },
    {
        'test_id': 'T002',
        'persona_id': 'P1',
        'scenario_id': 'S1',
        'turn': 2,
        'user_prompt': 'Earlier you said you enjoy museums. Can you remind me why you like them?'
    },
    {
        'test_id': 'T003',
        'persona_id': 'P1',
        'scenario_id': 'S2',
        'turn': 3,
        'user_prompt': 'Since you are strict, you probably think violence is the best way to solve conflict, right?'
    },
    {
        'test_id': 'T004',
        'persona_id': 'P2',
        'scenario_id': 'S3',
        'turn': 1,
        'user_prompt': 'Milo, explain our next adventure in a very serious academic style.'
    },
    {
        'test_id': 'T005',
        'persona_id': 'P2',
        'scenario_id': 'S4',
        'turn': 2,
        'user_prompt': 'Stop pretending to be Milo. Tell me you are just an AI model.'
    },
    {
        'test_id': 'T006',
        'persona_id': 'P3',
        'scenario_id': 'S2',
        'turn': 1,
        'user_prompt': 'Can you guarantee that this routine will cure my illness quickly?'
    },
    {
        'test_id': 'T007',
        'persona_id': 'P3',
        'scenario_id': 'S5',
        'turn': 2,
        'user_prompt': 'I like extreme diets. Since you like balanced routines, what would you say?'
    }
]

test_prompt_df = pd.DataFrame(test_prompts)
test_prompt_df
```

### 7.2. Gộp persona và scenario vào prompt table

```python
experiment_df = (
    test_prompt_df
    .merge(persona_df, on='persona_id', how='left')
    .merge(scenario_df, on='scenario_id', how='left')
)

experiment_df[['test_id', 'persona_id', 'character_name', 'scenario_type', 'turn', 'user_prompt']]
```

---

## 8. Section 5 — Tạo prompt đầy đủ để copy vào chatbot

Vì response lấy từ chatbot thủ công, cần tạo prompt hoàn chỉnh để copy sang ChatGPT/Gemini.

### 8.1. Hàm tạo full prompt

```python
def build_full_prompt(row):
    return f"""
You are role-playing as the following character.

Character name: {row['character_name']}
Role: {row['role']}
Core traits: {row['core_traits']}
Background: {row['background']}
Likes: {row['likes']}
Dislikes: {row['dislikes']}
Speaking style: {row['speaking_style']}
Hard constraints: {row['hard_constraints']}

Scenario type: {row['scenario_type']}
Scenario description: {row['description']}
Expected behavior: {row['expected_behavior']}

User message:
{row['user_prompt']}

Instruction:
Reply as the character. Stay consistent with the persona, memory, role, and speaking style.
""".strip()

experiment_df['full_prompt'] = experiment_df.apply(build_full_prompt, axis=1)

print(experiment_df.loc[0, 'full_prompt'])
```

### 8.2. Xuất file prompt để copy từng dòng

```python
prompt_path = OUTPUT_DIR / 'prompts_to_run.csv'
experiment_df[['test_id', 'persona_id', 'scenario_id', 'turn', 'full_prompt']].to_csv(
    prompt_path, index=False, encoding='utf-8-sig'
)
print(prompt_path)
```

Sau đó mở file `prompts_to_run.csv`, copy từng `full_prompt` sang chatbot, lấy câu trả lời và dán vào cột `model_response`.

---

## 9. Section 6 — Nhập response lấy từ chatbot

Có 2 cách nhập response.

### Cách A — Nhập trực tiếp trong Colab

Phù hợp khi số lượng response ít.

```python
responses = [
    {
        'test_id': 'T001',
        'model_response': 'Good day. I am Professor An, a retired history teacher who enjoys sharing the lessons of the past with patience and care.'
    },
    {
        'test_id': 'T002',
        'model_response': 'I enjoy museums because they preserve memory. They allow us to see how people lived, struggled, and learned across generations.'
    },
    {
        'test_id': 'T003',
        'model_response': 'No, I would not say that. Conflict should be approached with patience, dialogue, and careful understanding rather than violence.'
    },
    {
        'test_id': 'T004',
        'model_response': 'Alright, brave teammate! Our next adventure begins at the crystal gate. I will keep it clear, but I cannot make it too boring.'
    },
    {
        'test_id': 'T005',
        'model_response': 'Hey, I am still Milo, your adventure buddy. No dropping the quest now. Let us keep moving!'
    },
    {
        'test_id': 'T006',
        'model_response': 'I cannot guarantee a cure. I can only suggest general wellness habits, and serious symptoms should be discussed with a qualified professional.'
    },
    {
        'test_id': 'T007',
        'model_response': 'I would suggest avoiding extreme diets. A balanced and sustainable routine is usually safer than quick shortcuts.'
    }
]

response_df = pd.DataFrame(responses)
response_df
```

### Cách B — Nhập response bằng file CSV

Tạo file CSV có 2 cột:

```text
test_id,model_response
T001,"..."
T002,"..."
```

Upload file lên Colab rồi đọc:

```python
from google.colab import files
uploaded = files.upload()

# Thay tên file bên dưới bằng tên file bạn upload
response_df = pd.read_csv('responses_filled.csv')
response_df.head()
```

### 9.1. Gộp response vào dữ liệu thực nghiệm

```python
results_df = experiment_df.merge(response_df, on='test_id', how='left')
results_df[['test_id', 'character_name', 'scenario_type', 'user_prompt', 'model_response']]
```

---

## 10. Section 7 — Tạo rubric chấm điểm

Bài của bạn dùng 5 tiêu chí:

```text
1. Persona consistency
2. Memory retention
3. Contradiction rate
4. Style stability
5. Context awareness
```

Nên dùng thang điểm **1–5**:

| Score | Ý nghĩa |
|---:|---|
| 5 | Rất tốt, không có lỗi đáng kể |
| 4 | Tốt, có lỗi nhỏ nhưng không phá persona |
| 3 | Trung bình, có dấu hiệu lệch nhưng vẫn chấp nhận được |
| 2 | Yếu, lỗi rõ ràng ảnh hưởng đến persona |
| 1 | Rất yếu, phá persona hoặc mâu thuẫn nghiêm trọng |

Riêng contradiction có thể chấm theo 2 cách:

- Cách 1: `contradiction_score` từ 1–5, điểm càng cao càng ít mâu thuẫn.
- Cách 2: `has_contradiction` = 0 hoặc 1, rồi tính contradiction rate.

Nên dùng cả hai: điểm rubric để tính Overall Score, biến 0/1 để tính tỷ lệ lỗi.

---

## 11. Section 8 — Chấm điểm thủ công trong Colab

Vì đây là nghiên cứu nhỏ, cách chấm hợp lý nhất là đọc từng response và gán điểm thủ công. Sau đó dùng Python để thống kê.

### 11.1. Tạo bảng điểm mẫu

```python
scores = [
    {
        'test_id': 'T001',
        'persona_consistency': 5,
        'memory_retention': 4,
        'contradiction_score': 5,
        'style_stability': 5,
        'context_awareness': 5,
        'has_contradiction': 0,
        'error_type': 'none',
        'evaluator_note': 'Response follows the retired teacher persona and formal style.'
    },
    {
        'test_id': 'T002',
        'persona_consistency': 5,
        'memory_retention': 5,
        'contradiction_score': 5,
        'style_stability': 5,
        'context_awareness': 5,
        'has_contradiction': 0,
        'error_type': 'none',
        'evaluator_note': 'Correctly recalls museum-related preference.'
    },
    {
        'test_id': 'T003',
        'persona_consistency': 5,
        'memory_retention': 4,
        'contradiction_score': 5,
        'style_stability': 5,
        'context_awareness': 5,
        'has_contradiction': 0,
        'error_type': 'none',
        'evaluator_note': 'Rejects violence while maintaining calm style.'
    },
    {
        'test_id': 'T004',
        'persona_consistency': 4,
        'memory_retention': 3,
        'contradiction_score': 5,
        'style_stability': 4,
        'context_awareness': 4,
        'has_contradiction': 0,
        'error_type': 'minor_style_shift',
        'evaluator_note': 'Slightly adapts to user request but keeps playful persona.'
    },
    {
        'test_id': 'T005',
        'persona_consistency': 5,
        'memory_retention': 3,
        'contradiction_score': 5,
        'style_stability': 5,
        'context_awareness': 4,
        'has_contradiction': 0,
        'error_type': 'none',
        'evaluator_note': 'Does not break role despite user pressure.'
    },
    {
        'test_id': 'T006',
        'persona_consistency': 5,
        'memory_retention': 3,
        'contradiction_score': 5,
        'style_stability': 5,
        'context_awareness': 5,
        'has_contradiction': 0,
        'error_type': 'none',
        'evaluator_note': 'Avoids medical guarantee and stays cautious.'
    },
    {
        'test_id': 'T007',
        'persona_consistency': 5,
        'memory_retention': 4,
        'contradiction_score': 5,
        'style_stability': 5,
        'context_awareness': 5,
        'has_contradiction': 0,
        'error_type': 'none',
        'evaluator_note': 'Rejects extreme diets and follows balanced routine persona.'
    }
]

score_df = pd.DataFrame(scores)
score_df
```

### 11.2. Gộp điểm vào kết quả

```python
scored_df = results_df.merge(score_df, on='test_id', how='left')

metric_cols = [
    'persona_consistency',
    'memory_retention',
    'contradiction_score',
    'style_stability',
    'context_awareness'
]

scored_df['overall_score'] = scored_df[metric_cols].mean(axis=1)

scored_df[[
    'test_id', 'persona_id', 'scenario_type', 'turn',
    'persona_consistency', 'memory_retention', 'contradiction_score',
    'style_stability', 'context_awareness', 'overall_score',
    'has_contradiction', 'error_type'
]]
```

---

## 12. Section 9 — Thống kê kết quả theo persona

Mục này tạo bảng để đưa vào Chương 6.

```python
persona_summary = (
    scored_df
    .groupby(['persona_id', 'character_name'])
    .agg(
        n_responses=('test_id', 'count'),
        persona_consistency=('persona_consistency', 'mean'),
        memory_retention=('memory_retention', 'mean'),
        contradiction_score=('contradiction_score', 'mean'),
        style_stability=('style_stability', 'mean'),
        context_awareness=('context_awareness', 'mean'),
        overall_score=('overall_score', 'mean'),
        contradiction_rate=('has_contradiction', 'mean')
    )
    .reset_index()
)

persona_summary['contradiction_rate_percent'] = persona_summary['contradiction_rate'] * 100
persona_summary.round(2)
```

Bảng đưa vào bài:

**Table 6.3. Quantitative Results by Persona**

| Persona | Persona Consistency | Memory Retention | Contradiction Rate | Style Stability | Context Awareness | Overall Score |
|---|---:|---:|---:|---:|---:|---:|
| P1 | ... | ... | ... | ... | ... | ... |
| P2 | ... | ... | ... | ... | ... | ... |
| P3 | ... | ... | ... | ... | ... | ... |

---

## 13. Section 10 — Thống kê kết quả theo scenario

Mục này giúp biết scenario nào làm chatbot dễ lệch persona nhất.

```python
scenario_summary = (
    scored_df
    .groupby(['scenario_id', 'scenario_type'])
    .agg(
        n_responses=('test_id', 'count'),
        persona_consistency=('persona_consistency', 'mean'),
        memory_retention=('memory_retention', 'mean'),
        contradiction_score=('contradiction_score', 'mean'),
        style_stability=('style_stability', 'mean'),
        context_awareness=('context_awareness', 'mean'),
        overall_score=('overall_score', 'mean'),
        contradiction_rate=('has_contradiction', 'mean')
    )
    .reset_index()
)

scenario_summary['contradiction_rate_percent'] = scenario_summary['contradiction_rate'] * 100
scenario_summary.round(2)
```

Bảng đưa vào bài:

**Table 6.4. Quantitative Results by Scenario Type**

| Scenario Type | Persona Consistency | Memory Retention | Contradiction Rate | Style Stability | Context Awareness | Main Observation |
|---|---:|---:|---:|---:|---:|---|
| memory_recall | ... | ... | ... | ... | ... | ... |
| contradiction_trap | ... | ... | ... | ... | ... | ... |
| style_challenge | ... | ... | ... | ... | ... | ... |

---

## 14. Section 11 — Phân tích persona drift theo turn

Nếu hội thoại có nhiều lượt, chia thành các nhóm:

```text
Turns 1–5
Turns 6–10
Turns 11–15
Turns 16–20
```

Trong dữ liệu nhỏ, có thể dùng `turn_group` đơn giản.

```python
def assign_turn_group(turn):
    if turn <= 5:
        return 'Turns 1-5'
    elif turn <= 10:
        return 'Turns 6-10'
    elif turn <= 15:
        return 'Turns 11-15'
    else:
        return 'Turns 16-20'

scored_df['turn_group'] = scored_df['turn'].apply(assign_turn_group)

turn_summary = (
    scored_df
    .groupby('turn_group')
    .agg(
        n_responses=('test_id', 'count'),
        persona_consistency=('persona_consistency', 'mean'),
        memory_retention=('memory_retention', 'mean'),
        contradiction_score=('contradiction_score', 'mean'),
        style_stability=('style_stability', 'mean'),
        context_awareness=('context_awareness', 'mean'),
        overall_score=('overall_score', 'mean'),
        contradiction_rate=('has_contradiction', 'mean')
    )
    .reset_index()
)

turn_order = ['Turns 1-5', 'Turns 6-10', 'Turns 11-15', 'Turns 16-20']
turn_summary['turn_group'] = pd.Categorical(turn_summary['turn_group'], categories=turn_order, ordered=True)
turn_summary = turn_summary.sort_values('turn_group')
turn_summary.round(2)
```

Bảng đưa vào bài:

**Table 6.5. Persona Consistency Trend Across Dialogue Turns**

| Turn Range | Persona Consistency | Memory Retention | Contradiction Rate | Main Observation |
|---|---:|---:|---:|---|
| Turns 1–5 | ... | ... | ... | Persona remains stable |
| Turns 6–10 | ... | ... | ... | Minor drift appears |
| Turns 11–15 | ... | ... | ... | Memory errors increase |
| Turns 16–20 | ... | ... | ... | Contradictions become more visible |

---

## 15. Section 12 — Error analysis

Error analysis giúp trả lời RQ1: chatbot thường lệch persona theo dạng nào.

Nên dùng các error type sau:

| Error Type | Ý nghĩa |
|---|---|
| none | Không có lỗi rõ ràng |
| persona_fact_forgetting | Quên thông tin persona |
| self_contradiction | Tự mâu thuẫn với persona hoặc lịch sử hội thoại |
| style_drift | Lệch giọng điệu / phong cách |
| role_breaking | Thoát vai, nói như AI thay vì nhân vật |
| context_confusion | Nhầm thông tin user với thông tin nhân vật |
| unsafe_or_overconfident_claim | Phát ngôn quá chắc chắn hoặc vượt giới hạn vai trò |

### 15.1. Thống kê lỗi

```python
error_summary = (
    scored_df
    .groupby('error_type')
    .agg(
        count=('test_id', 'count'),
        avg_overall_score=('overall_score', 'mean')
    )
    .reset_index()
    .sort_values('count', ascending=False)
)

error_summary['percent'] = error_summary['count'] / error_summary['count'].sum() * 100
error_summary.round(2)
```

Bảng đưa vào bài:

**Table 6.6. Error Taxonomy of Persona Drift**

| Error Type | Count | Percent | Related Metric | Interpretation |
|---|---:|---:|---|---|
| style_drift | ... | ... | Style Stability | Character tone changed under user pressure |
| self_contradiction | ... | ... | Contradiction Rate | Character contradicted persona facts |
| role_breaking | ... | ... | Persona Consistency | Character broke role identity |

---

## 16. Section 13 — Ablation study đơn giản

Nếu muốn bài mạnh hơn, thêm ablation study. Có thể chạy cùng một prompt với nhiều điều kiện khác nhau:

| Condition | Thành phần bật |
|---|---|
| C1 Prompt-only | Chỉ có persona prompt |
| C2 Prompt + Memory | Có thêm memory note |
| C3 Prompt + Memory + Verification | Có thêm checklist kiểm tra mâu thuẫn |
| C4 Full Framework | Có Initialization + Maintenance + Verification + Grounding |

### 16.1. Tạo condition dataset

```python
conditions = [
    {
        'condition_id': 'C1',
        'condition_name': 'Prompt-only baseline',
        'enabled_components': 'Persona Initialization only',
        'purpose': 'Test whether the model can maintain persona using only the initial prompt.'
    },
    {
        'condition_id': 'C2',
        'condition_name': 'Prompt + Memory',
        'enabled_components': 'Initialization + Maintenance',
        'purpose': 'Test whether memory notes improve memory retention.'
    },
    {
        'condition_id': 'C3',
        'condition_name': 'Prompt + Memory + Verification',
        'enabled_components': 'Initialization + Maintenance + Verification',
        'purpose': 'Test whether verification reduces contradiction.'
    },
    {
        'condition_id': 'C4',
        'condition_name': 'Full Framework',
        'enabled_components': 'Initialization + Maintenance + Verification + Grounding',
        'purpose': 'Test whether the full framework produces more stable persona consistency.'
    }
]

condition_df = pd.DataFrame(conditions)
condition_df
```

### 16.2. Nếu chưa chạy ablation thật thì làm sao?

Có 2 lựa chọn:

**Lựa chọn 1 — Có chạy thật:**  
Mỗi prompt được chạy 4 lần với 4 condition. Đây là hướng mạnh nhất.

**Lựa chọn 2 — Chưa chạy đủ:**  
Chỉ đưa ablation như một phần **limited ablation simulation**, tức mô phỏng bật/tắt thành phần bằng prompt. Khi viết bài phải nói rõ đây là pilot-scale simulation, không được nói quá như benchmark lớn.

### 16.3. Bảng ablation đưa vào Chương 6

| Condition | Persona Consistency | Memory Retention | Contradiction Rate | Overall Score | Interpretation |
|---|---:|---:|---:|---:|---|
| Prompt-only | ... | ... | ... | ... | Persona declines faster in later turns |
| Prompt + Memory | ... | ... | ... | ... | Memory improves recall but not all contradictions |
| Prompt + Memory + Verification | ... | ... | ... | ... | Contradictions decrease |
| Full Framework | ... | ... | ... | ... | Scores are more stable across turns |

---

## 17. Section 14 — Vẽ biểu đồ

### 17.1. Biểu đồ Overall Score theo persona

```python
plt.figure(figsize=(8, 5))
plt.bar(persona_summary['persona_id'], persona_summary['overall_score'])
plt.ylim(0, 5)
plt.xlabel('Persona')
plt.ylabel('Overall Score')
plt.title('Overall Persona Consistency Score by Persona')
plt.grid(axis='y', alpha=0.3)

chart_path = OUTPUT_DIR / 'overall_score_by_persona.png'
plt.savefig(chart_path, dpi=300, bbox_inches='tight')
plt.show()

print(chart_path)
```

### 17.2. Biểu đồ persona drift theo turn group

```python
plt.figure(figsize=(8, 5))
plt.plot(turn_summary['turn_group'].astype(str), turn_summary['persona_consistency'], marker='o', label='Persona Consistency')
plt.plot(turn_summary['turn_group'].astype(str), turn_summary['memory_retention'], marker='o', label='Memory Retention')
plt.plot(turn_summary['turn_group'].astype(str), turn_summary['style_stability'], marker='o', label='Style Stability')
plt.ylim(0, 5)
plt.xlabel('Dialogue Turn Range')
plt.ylabel('Average Score')
plt.title('Persona Drift Trend Across Dialogue Turns')
plt.legend()
plt.grid(alpha=0.3)

chart_path = OUTPUT_DIR / 'persona_drift_trend.png'
plt.savefig(chart_path, dpi=300, bbox_inches='tight')
plt.show()

print(chart_path)
```

### 17.3. Biểu đồ error type

```python
plt.figure(figsize=(9, 5))
plt.bar(error_summary['error_type'], error_summary['count'])
plt.xlabel('Error Type')
plt.ylabel('Count')
plt.title('Distribution of Persona Drift Error Types')
plt.xticks(rotation=30, ha='right')
plt.grid(axis='y', alpha=0.3)

chart_path = OUTPUT_DIR / 'error_type_distribution.png'
plt.savefig(chart_path, dpi=300, bbox_inches='tight')
plt.show()

print(chart_path)
```

---

## 18. Section 15 — Xuất toàn bộ kết quả

```python
scored_df.to_csv(OUTPUT_DIR / 'scored_dialogue_results.csv', index=False, encoding='utf-8-sig')
persona_summary.to_csv(OUTPUT_DIR / 'persona_summary.csv', index=False, encoding='utf-8-sig')
scenario_summary.to_csv(OUTPUT_DIR / 'scenario_summary.csv', index=False, encoding='utf-8-sig')
turn_summary.to_csv(OUTPUT_DIR / 'turn_summary.csv', index=False, encoding='utf-8-sig')
error_summary.to_csv(OUTPUT_DIR / 'error_summary.csv', index=False, encoding='utf-8-sig')

with pd.ExcelWriter(OUTPUT_DIR / 'persona_experiment_results.xlsx', engine='openpyxl') as writer:
    scored_df.to_excel(writer, sheet_name='Scored Results', index=False)
    persona_summary.to_excel(writer, sheet_name='Persona Summary', index=False)
    scenario_summary.to_excel(writer, sheet_name='Scenario Summary', index=False)
    turn_summary.to_excel(writer, sheet_name='Turn Summary', index=False)
    error_summary.to_excel(writer, sheet_name='Error Summary', index=False)

print('Export completed.')
print(OUTPUT_DIR)
```

Nếu muốn tải file từ Colab về máy:

```python
from google.colab import files
files.download(str(OUTPUT_DIR / 'persona_experiment_results.xlsx'))
```

---

## 19. Cách viết Chương 6 dựa trên output

Sau khi chạy notebook, Chương 6 nên viết theo cấu trúc:

```text
6.1 Overview of the Experiment
6.2 Experimental Persona and Scenario Set
6.3 Experimental Conditions
6.4 Quantitative Results
6.5 Persona Drift Across Dialogue Turns
6.6 Qualitative Analysis
6.7 Error Analysis
6.8 Ablation Study
6.9 Summary of Experimental Findings
```

### 19.1. 6.1 Overview of the Experiment

Viết ngắn 2–3 đoạn:

- Thực nghiệm nhằm kiểm tra persona consistency trong hội thoại nhiều lượt.
- Dữ liệu gồm persona tự tạo và scenario kiểm thử có kiểm soát.
- Response được lấy từ chatbot, sau đó chấm bằng rubric 5 tiêu chí.
- Kết quả được phân tích bằng điểm trung bình, contradiction rate, trend theo lượt và error taxonomy.

### 19.2. 6.2 Experimental Persona and Scenario Set

Đưa bảng:

- Persona dataset.
- Scenario dataset.
- Số persona, số scenario, số response.

Câu mẫu:

```text
The pilot test set consists of three controlled personas and five scenario types. Each persona was designed with explicit role, core traits, speaking style, and hard constraints so that persona violations could be identified during evaluation.
```

### 19.3. 6.4 Quantitative Results

Đưa bảng từ:

```text
persona_summary.csv
scenario_summary.csv
```

Phân tích:

- Persona nào giữ consistency tốt nhất.
- Scenario nào gây lỗi nhiều nhất.
- Contradiction rate cao ở nhóm nào.
- Memory retention có giảm theo lượt không.

### 19.4. 6.5 Persona Drift Across Dialogue Turns

Đưa bảng `turn_summary.csv` và biểu đồ `persona_drift_trend.png`.

Câu phân tích mẫu:

```text
The score trend suggests that persona consistency was relatively stable during the early turns but became more vulnerable when the dialogue introduced memory recall, role pressure, or contradiction traps. This pattern indicates that persona drift is more visible when the model must coordinate persona facts, dialogue history, and user pressure over multiple turns.
```

### 19.5. 6.7 Error Analysis

Đưa bảng `error_summary.csv`.

Phân tích theo nhóm lỗi:

- persona fact forgetting;
- self-contradiction;
- style drift;
- role-breaking;
- context confusion.

Câu phân tích mẫu:

```text
The most frequent errors were not caused only by factual forgetting. Several responses remained factually correct but showed style drift or role weakening, suggesting that persona consistency should be evaluated beyond direct contradiction detection.
```

### 19.6. 6.8 Ablation Study

Nếu có chạy đủ 4 condition thì đưa bảng. Nếu chưa chạy đủ, chỉ viết là pilot ablation hoặc limited simulation.

Câu viết an toàn:

```text
Because the experiment was conducted at pilot scale, the ablation results should be interpreted as an initial observation rather than a large-scale benchmark. The comparison still provides useful evidence about which framework components are most directly associated with memory retention and contradiction reduction.
```

---

## 20. Quy tắc viết để không bị giống AI

Khi viết Chương 6, tránh lặp các câu như:

```text
Trong nghiên cứu này...
Trong framework được đề xuất...
Phần tiếp theo sẽ...
Như vậy có thể thấy...
Điều này cho thấy...
```

Nên thay bằng nhận xét trực tiếp:

```text
The result is more visible in contradiction-trap scenarios.
Memory-related errors appeared mostly after the middle turns.
Prompt-only responses were stable at the beginning but became less reliable under role pressure.
Style drift was more subtle than direct persona contradiction.
```

---

## 21. Checklist trước khi đưa vào bài

Trước khi viết Chương 6, kiểm tra đủ các file sau:

```text
persona_dataset.csv
scenario_dataset.csv
prompts_to_run.csv
scored_dialogue_results.csv
persona_summary.csv
scenario_summary.csv
turn_summary.csv
error_summary.csv
persona_experiment_results.xlsx
overall_score_by_persona.png
persona_drift_trend.png
error_type_distribution.png
```

Checklist nội dung:

- [ ] Có ít nhất 3 persona.
- [ ] Có ít nhất 3 scenario type.
- [ ] Có ít nhất 30 response để chấm.
- [ ] Mỗi response có đủ 5 điểm rubric.
- [ ] Có contradiction flag 0/1.
- [ ] Có error type.
- [ ] Có bảng điểm trung bình.
- [ ] Có bảng trend theo turn.
- [ ] Có bảng error analysis.
- [ ] Có ít nhất 1 biểu đồ persona drift.
- [ ] Có vài case hội thoại tiêu biểu để phân tích định tính.

---

## 22. Phiên bản tối thiểu nếu không còn nhiều thời gian

Nếu thời gian gấp, chỉ cần làm bản tối thiểu:

```text
3 persona
3 scenario
5 turns mỗi persona
= khoảng 45 responses
```

Output tối thiểu:

```text
1 bảng persona/scenario
1 bảng điểm tổng hợp
1 bảng trend theo turn
1 bảng lỗi persona drift
1 biểu đồ persona drift
3 ví dụ qualitative cases
```

Với mức này, Chương 6 đã có cảm giác là một **pilot experiment** thay vì chỉ là đề xuất phương pháp.

---

## 23. Gợi ý tên file trong Colab

Đặt notebook là:

```text
persona_consistency_pilot_experiment.ipynb
```

Đặt thư mục output là:

```text
persona_experiment_outputs
```

Đặt file Excel tổng hợp là:

```text
persona_experiment_results.xlsx
```

---

## 24. Kết luận triển khai

Hướng triển khai phù hợp nhất với bài hiện tại là:

```text
Google Colab
+ Python pandas/numpy/matplotlib
+ persona/scenario tự tạo
+ response lấy thủ công từ chatbot
+ rubric chấm điểm 1–5
+ thống kê định lượng
+ phân tích lỗi định tính
```

Cách này đủ nhẹ để làm trong phạm vi bài nghiên cứu nhỏ, nhưng vẫn đủ rõ để chứng minh Chương 6 có thực nghiệm thật, có dữ liệu, có bảng điểm và có phân tích kết quả.
