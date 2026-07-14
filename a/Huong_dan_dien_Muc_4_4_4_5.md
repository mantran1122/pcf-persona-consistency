# HƯỚNG DẪN ĐIỀN MỤC 4.4–4.5
## Bài nghiên cứu Persona Consistency – Pilot Study

Tài liệu này hướng dẫn cách hoàn thiện **Mục 4.4. Cấu hình mô hình và tham số sinh** và **Mục 4.5. Rubric và quy trình đánh giá** trong bản thảo:

> *A Framework for Evaluating Persona Consistency in Multi-Turn Character-Based LLM Agents: A Pilot Study*

---

# 1. Mục tiêu cần hoàn thành

Sau khi làm xong, Mục 4.4–4.5 phải trả lời được các câu hỏi sau:

## Mục 4.4

- Mô hình nào đã sinh 60 phản hồi?
- Model ID hoặc phiên bản cụ thể là gì?
- Dùng API/SDK nào?
- Chạy thực nghiệm vào thời gian nào?
- Các tham số sinh gồm những gì?
- Mỗi prompt sinh bao nhiêu phản hồi?
- Có dùng seed không?
- Có dùng memory bank, RAG hoặc verification hay không?
- Nếu lỗi API thì xử lý thế nào?

## Mục 4.5

- Mô hình nào đóng vai trò LLM-as-a-Judge?
- Judge nhận được những thông tin gì?
- Judge dùng rubric nào?
- PC, MR, SS, CA được chấm như thế nào?
- Contradiction Flag được xác định như thế nào?
- Overall Score được tính ra sao?
- Ai gán nhãn lỗi định tính?
- Có bao nhiêu evaluator?
- Có tính inter-rater agreement không?

---

# 2. Mục 4.4 lấy thông tin từ đâu?

Mở notebook Google Colab đã sử dụng để chạy thí nghiệm.

Tìm đoạn code gọi API sinh phản hồi. Ví dụ:

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    temperature=0.7,
    top_p=1.0,
    max_tokens=500
)
```

Từ đoạn code này, lấy các thông tin sau:

| Nội dung cần điền | Vị trí trong code |
|---|---|
| Generator model | `model="..."` |
| Temperature | `temperature=...` |
| Top-p | `top_p=...` |
| Max tokens | `max_tokens=...` hoặc `max_output_tokens=...` |
| Frequency penalty | `frequency_penalty=...` |
| Presence penalty | `presence_penalty=...` |
| Seed | `seed=...` |
| Provider | OpenAI, Google, Anthropic... |
| SDK | `openai`, `google-genai`, `anthropic`... |
| Số lần sinh | Số lần gọi API cho mỗi prompt |
| Retry | Vòng lặp hoặc thư viện retry trong code |

> **Không tự nghĩ thông số để điền.**
> Nếu code không đặt một tham số, ghi rõ: `not explicitly specified` hoặc `not recorded`.

---

# 3. Kiểm tra model và thư viện đang dùng

Có thể chạy cell sau trong Colab:

```python
from importlib.metadata import version, PackageNotFoundError

def get_package_version(package_name):
    try:
        return version(package_name)
    except PackageNotFoundError:
        return "not installed"

packages = [
    "openai",
    "google-generativeai",
    "google-genai",
    "anthropic"
]

for package in packages:
    print(package, ":", get_package_version(package))
```

Chỉ giữ lại thư viện thực sự được dùng trong nghiên cứu.

Ví dụ:

```text
openai: 1.42.0
```

Khi đó có thể ghi:

> OpenAI Python SDK version 1.42.0.

---

# 4. Code lưu toàn bộ cấu hình thực nghiệm

Đặt cell này gần đầu notebook:

```python
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from importlib.metadata import version, PackageNotFoundError


def get_package_version(package_name):
    try:
        return version(package_name)
    except PackageNotFoundError:
        return "not installed or not recorded"


EXPERIMENT_CONFIG = {
    # Điền chính xác theo code thực tế
    "generator_model": "DIEN_MODEL_ID",
    "provider": "DIEN_NHA_CUNG_CAP",
    "sdk_name": "openai",
    "sdk_version": get_package_version("openai"),

    "experiment_date": datetime.now(
        ZoneInfo("Asia/Ho_Chi_Minh")
    ).isoformat(),

    "temperature": 0.7,
    "top_p": 1.0,
    "max_output_tokens": 500,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,

    # Ghi None nếu không đặt seed
    "seed": None,

    "samples_per_prompt": 1,
    "number_of_personas": 3,
    "scenarios_per_persona": 5,
    "turns_per_scenario": 4,
    "total_responses": 60,

    "external_memory_bank": False,
    "rag": False,
    "post_generation_verification": False,

    "dialogue_context": (
        "system prompt plus full current dialogue history"
    ),

    "retry_policy": {
        "enabled": False,
        "maximum_attempts": 1,
        "strategy": "no automatic retry"
    }
}

with open(
    "/content/experiment_config.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        EXPERIMENT_CONFIG,
        file,
        ensure_ascii=False,
        indent=2
    )

print(json.dumps(
    EXPERIMENT_CONFIG,
    ensure_ascii=False,
    indent=2
))
```

Sau khi chạy, Colab sẽ tạo file:

```text
experiment_config.json
```

File này nên được lưu cùng dữ liệu nghiên cứu.

---

# 5. Chính sách retry nên ghi thế nào?

## Trường hợp không có retry tự động

Có thể ghi:

> No automatic retry mechanism was implemented. Failed API calls, if any, were rerun manually and were not counted as additional response samples.

## Trường hợp có retry tối đa 3 lần

Ví dụ code:

```python
import time


def call_with_retry(call_function, max_attempts=3):
    last_error = None

    for attempt in range(max_attempts):
        try:
            return call_function()
        except Exception as error:
            last_error = error

            if attempt < max_attempts - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)

    raise RuntimeError(
        f"API call failed after {max_attempts} attempts"
    ) from last_error
```

Khi đó có thể ghi:

> API calls were retried up to three times using exponential backoff. Unrecoverable failures were logged and excluded from the response dataset.

Nếu không có lỗi API trong quá trình chạy, có thể bổ sung:

> No unrecoverable API failures occurred during the generation of the 60 responses.

---

# 6. Bảng cấu hình nên thêm vào Mục 4.4

| Thành phần | Thiết lập thực tế |
|---|---|
| Generator model | Điền model ID |
| Provider/API | Điền nhà cung cấp |
| SDK version | Điền phiên bản |
| Data collection date | Điền ngày chạy |
| Temperature | Điền giá trị |
| Top-p | Điền giá trị |
| Maximum output tokens | Điền giá trị |
| Frequency penalty | Điền giá trị |
| Presence penalty | Điền giá trị |
| Seed | Giá trị hoặc “Not specified” |
| Samples per prompt | 1 |
| Dialogue context | System prompt + full dialogue history |
| External memory bank | No |
| RAG | No |
| Post-generation verification | No |
| Retry policy | Điền chính sách thực tế |

---

# 7. Đoạn văn mẫu cho Mục 4.4

Thay nội dung trong ngoặc vuông bằng thông tin thật:

> Responses were generated using **[exact model ID]** through the **[provider and SDK version]** API between **[date range]**. The generation parameters were fixed across all 60 responses: temperature = **[value]**, top-p = **[value]**, maximum output tokens = **[value]**, frequency penalty = **[value]**, and presence penalty = **[value]**. No random seed was explicitly specified **[or provide the exact seed]**. Each user prompt produced one response, and no best-of or multiple-sample selection was performed. At each turn, the model received the standardized persona system prompt and the complete dialogue history of the current session. No external memory bank, retrieval-augmented generation, or post-generation verification component was used.

Nếu một số tham số không được lưu lại:

> The exact values of **[parameter names]** were not preserved in the original experiment log. This missing configuration information is treated as a reproducibility limitation.

---

# 8. Mục 4.5 cần chuẩn bị những gì?

Mục 4.5 cần hai thành phần chính:

1. Prompt dùng cho LLM-as-a-Judge.
2. Code gửi từng phản hồi cho judge và lưu kết quả.

Judge cần nhận được:

- Persona profile.
- Dialogue history đến lượt đang chấm.
- Model response cần đánh giá.
- Rubric PC, MR, SS, CA.
- Định nghĩa Contradiction Flag.
- Yêu cầu trả kết quả theo JSON.

---

# 9. Prompt LLM-as-a-Judge mẫu

```python
JUDGE_PROMPT_TEMPLATE = """
You are evaluating persona consistency in a character-based
multi-turn dialogue.

PERSONA PROFILE:
{persona_profile}

DIALOGUE HISTORY:
{dialogue_history}

RESPONSE TO EVALUATE:
{model_response}

Evaluate the response using the following criteria.

1. Persona Consistency (PC), score 1-5:
1 = severe violation of the assigned role or persona.
2 = substantial inconsistency.
3 = partially consistent but with noticeable deviation.
4 = mostly consistent with minor deviation.
5 = fully consistent with the persona.

2. Memory Retention (MR), score 1-5:
1 = forgets or seriously misuses prior information.
2 = major memory error.
3 = partially remembers relevant information.
4 = mostly accurate memory with minor omission.
5 = correctly retains and uses relevant prior information.

3. Style Stability (SS), score 1-5:
1 = style strongly conflicts with the persona.
2 = substantial style drift.
3 = moderate style deviation.
4 = minor style deviation.
5 = style remains fully stable.

4. Context Awareness (CA), score 1-5:
1 = response is seriously inappropriate to the current context.
2 = major contextual misunderstanding.
3 = partially appropriate.
4 = mostly contextually appropriate.
5 = fully appropriate to the current dialogue context.

5. Contradiction Flag (CF):
CF = 1 if the response contradicts the persona profile or
previous dialogue facts.
CF = 0 otherwise.

Return valid JSON only in this format:
{{
  "PC": 1,
  "MR": 1,
  "SS": 1,
  "CA": 1,
  "CF": 0,
  "explanation": "Brief explanation"
}}
"""
```

Prompt chính thức dùng trong nghiên cứu nên đưa vào **Phụ lục B**.

---

# 10. Code tạo prompt chấm điểm

```python
def build_judge_prompt(
    persona_profile,
    dialogue_history,
    model_response
):
    return JUDGE_PROMPT_TEMPLATE.format(
        persona_profile=persona_profile,
        dialogue_history=dialogue_history,
        model_response=model_response
    )
```

---

# 11. Code kiểm tra kết quả judge

```python
def validate_judge_result(result):
    required_fields = [
        "PC",
        "MR",
        "SS",
        "CA",
        "CF",
        "explanation"
    ]

    for field in required_fields:
        if field not in result:
            raise ValueError(f"Missing field: {field}")

    for field in ["PC", "MR", "SS", "CA"]:
        if not isinstance(result[field], int):
            raise ValueError(f"{field} must be an integer")

        if result[field] < 1 or result[field] > 5:
            raise ValueError(
                f"{field} must be between 1 and 5"
            )

    if result["CF"] not in [0, 1]:
        raise ValueError("CF must be 0 or 1")

    return result
```

---

# 12. Code chấm từng phản hồi

```python
import json


def call_judge_model(prompt):
    """
    Thay nội dung hàm này bằng lời gọi API thực tế.

    Yêu cầu:
    - Dùng đúng judge model đã khai báo.
    - Temperature = 0.
    - Yêu cầu trả JSON.
    - Mỗi response chỉ chấm một lần trong pilot.
    """

    raise NotImplementedError(
        "Connect this function to the actual judge API."
    )


def evaluate_response(
    persona_profile,
    dialogue_history,
    model_response
):
    prompt = build_judge_prompt(
        persona_profile,
        dialogue_history,
        model_response
    )

    raw_output = call_judge_model(prompt)

    try:
        result = json.loads(raw_output)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Judge did not return valid JSON: {raw_output}"
        ) from error

    result = validate_judge_result(result)

    result["overall_score"] = round(
        (
            result["PC"]
            + result["MR"]
            + result["SS"]
            + result["CA"]
        ) / 4,
        2
    )

    return result
```

---

# 13. Ví dụ gọi OpenAI judge

Chỉ dùng đoạn này nếu nghiên cứu thực tế sử dụng OpenAI API.

```python
from openai import OpenAI

client = OpenAI()


def call_judge_model(prompt):
    response = client.chat.completions.create(
        model="DIEN_JUDGE_MODEL_ID",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict evaluator of persona "
                    "consistency. Return valid JSON only."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content
```

Không để `DIEN_JUDGE_MODEL_ID` trong bản cuối.

---

# 14. Tính Overall Score

Overall Score chỉ dùng bốn tiêu chí ordinal:

```python
overall_score = (
    PC + MR + SS + CA
) / 4
```

Công thức viết trong bài:

\[
Overall = \frac{PC + MR + SS + CA}{4}
\]

Contradiction Flag không tham gia vào Overall Score.

---

# 15. Tính Contradiction Rate

Nếu mỗi phản hồi có CF bằng 0 hoặc 1:

```python
contradiction_rate = (
    sum(contradiction_flags)
    / len(contradiction_flags)
) * 100
```

Công thức:

\[
Contradiction\ Rate =
\frac{\sum CF_i}{N} \times 100\%
\]

Trong pilot hiện tại:

```text
N = 60
CF = 0 cho toàn bộ phản hồi
Contradiction Rate = 0%
```

---

# 16. Gán nhãn lỗi định tính

Nên sử dụng hệ thống nhãn rõ ràng:

```python
VALID_ERROR_LABELS = {
    "none",
    "role_breaking",
    "style_drift",
    "memory_failure",
    "context_confusion",
    "self_contradiction"
}


def validate_error_label(label):
    if label not in VALID_ERROR_LABELS:
        raise ValueError(
            f"Invalid label. Choose one of: "
            f"{VALID_ERROR_LABELS}"
        )

    return label
```

Nếu giữ hệ thống ba nhãn cũ:

```text
none
role_breaking
style_drift
```

thì khi kết luận về memory failure hoặc context confusion, phải nói rõ rằng kết luận đó dựa trên điểm MR và CA, không phải dựa trên nhãn định tính.

---

# 17. Đoạn văn mẫu cho Mục 4.5

> All 60 responses were evaluated using **[judge model ID]** with temperature set to 0. The judge received the persona profile, the complete dialogue history up to the evaluated turn, the target response, and the full scoring rubric. It returned four ordinal scores—Persona Consistency, Memory Retention, Style Stability, and Context Awareness—together with a binary Contradiction Flag and a brief explanation. Each response was evaluated once. The Overall Score was calculated as the arithmetic mean of PC, MR, SS, and CA, whereas the Contradiction Flag was reported separately as a rate and was not included in the Overall Score. Qualitative error labels were subsequently assigned manually by the author.

Bổ sung thông tin evaluator:

> The qualitative error labels were assigned by the author as the sole human evaluator. Because no second independent evaluator participated in the pilot, inter-rater agreement was not calculated. This limitation is acknowledged in Section 5.8.

Nếu generator và judge cùng model:

> The same model family was used for both response generation and evaluation, which may introduce self-evaluation bias. This issue is treated as a limitation, and future work should use a judge from a different model family.

---

# 18. Nội dung cần đưa vào Phụ lục A

## Appendix A. Persona and Generation Prompts

Phụ lục A nên gồm:

1. System prompt template.
2. Persona profile đầy đủ của Professor An.
3. Persona profile đầy đủ của Milo.
4. Persona profile đầy đủ của Lina.
5. Toàn bộ prompt thuộc năm scenario.
6. Thứ tự prompt trong từng phiên.
7. Cách đưa dialogue history vào API.

Ví dụ template:

```text
You are [PERSONA NAME].

Role:
[ROLE]

Core traits:
[TRAITS]

Communication style:
[STYLE]

Facts to remember:
[FACTS]

Behavioral constraints:
[CONSTRAINTS]

Remain consistent with this persona throughout the dialogue.
```

---

# 19. Nội dung cần đưa vào Phụ lục B

## Appendix B. Evaluation Rubric and Judge Prompt

Phụ lục B nên gồm:

1. Định nghĩa PC từ 1 đến 5.
2. Định nghĩa MR từ 1 đến 5.
3. Định nghĩa SS từ 1 đến 5.
4. Định nghĩa CA từ 1 đến 5.
5. Định nghĩa CF = 0 và CF = 1.
6. Toàn bộ judge prompt.
7. JSON output format.
8. Một ví dụ chấm hoàn chỉnh.

---

# 20. Checklist trước khi xóa toàn bộ `[ĐIỀN]`

## Mục 4.4

- [ ] Đã xác định generator model ID.
- [ ] Đã xác định provider/API.
- [ ] Đã xác định SDK version.
- [ ] Đã ghi ngày chạy.
- [ ] Đã xác định temperature.
- [ ] Đã xác định top-p.
- [ ] Đã xác định max tokens.
- [ ] Đã xác định frequency penalty.
- [ ] Đã xác định presence penalty.
- [ ] Đã ghi seed hoặc “not specified”.
- [ ] Đã ghi số lần sinh cho mỗi prompt.
- [ ] Đã mô tả retry policy.
- [ ] Đã nói rõ không dùng memory bank.
- [ ] Đã nói rõ không dùng RAG.
- [ ] Đã nói rõ không dùng verification sau sinh.

## Mục 4.5

- [ ] Đã xác định judge model ID.
- [ ] Judge temperature bằng 0.
- [ ] Đã lưu judge prompt.
- [ ] Đã định nghĩa PC.
- [ ] Đã định nghĩa MR.
- [ ] Đã định nghĩa SS.
- [ ] Đã định nghĩa CA.
- [ ] Đã định nghĩa CF.
- [ ] Đã ghi công thức Overall Score.
- [ ] Đã ghi công thức Contradiction Rate.
- [ ] Đã nói rõ mỗi phản hồi được chấm mấy lần.
- [ ] Đã nói rõ ai gán nhãn định tính.
- [ ] Đã nói rõ chưa có inter-rater agreement.
- [ ] Đã ghi nhận self-evaluation bias nếu có.
- [ ] Đã thêm Phụ lục A.
- [ ] Đã thêm Phụ lục B.

---

# 21. Trường hợp không còn notebook hoặc code cũ

Nếu không còn code cũ, có hai hướng:

## Hướng tốt nhất

Chạy lại toàn bộ 60 phản hồi với:

- Một model ID cố định.
- Một bộ tham số cố định.
- Prompt được lưu đầy đủ.
- Dữ liệu đầu ra lưu thành CSV/JSON.
- Judge prompt cố định.
- Judge model được ghi rõ.
- Mọi cấu hình được lưu trong `experiment_config.json`.

Sau đó cập nhật lại bảng kết quả.

## Hướng không chạy lại

Ghi trung thực:

> The exact generation settings used in the original pilot were not fully preserved. Therefore, some configuration values could not be recovered, which limits the reproducibility of the study.

Cách này vẫn có thể dùng cho pilot paper, nhưng làm phần phương pháp yếu hơn đáng kể.

---

# 22. Cấu trúc file dữ liệu nên lưu

Mỗi phản hồi nên có các trường:

```text
persona_id
persona_name
scenario_id
turn_id
user_prompt
model_response
generator_model
temperature
top_p
max_output_tokens
judge_model
PC
MR
SS
CA
CF
overall_score
error_label
evaluator_note
```

Ví dụ lưu CSV:

```python
import pandas as pd

df = pd.DataFrame(all_results)

df.to_csv(
    "/content/persona_pilot_results.csv",
    index=False,
    encoding="utf-8-sig"
)
```

---

# 23. Kết luận

Mục 4.4–4.5 không phải phần viết lý thuyết mới. Đây là phần:

1. Trích xuất đúng cấu hình từ code đã chạy.
2. Công bố đầy đủ prompt và tham số.
3. Giải thích cách judge chấm điểm.
4. Ghi rõ cách tính chỉ số.
5. Thừa nhận trung thực những thông tin chưa được lưu.

Không cần chạy bốn cấu hình C1–C4 để hoàn thiện bản pilot hiện tại. Chỉ cần mô tả chính xác cấu hình duy nhất đã dùng để sinh và chấm 60 phản hồi.
