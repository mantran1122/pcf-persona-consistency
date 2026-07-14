# PHẢN BIỆN BẢN THẢO THEO TIÊU CHUẨN TẠP CHÍ Q4

**Tên bản thảo:** *Maintaining Persona Consistency in Long-Term Character-Based Conversational Agents Using Large Language Models*

---

## A. Editorial Summary

Bản thảo nghiên cứu vấn đề duy trì tính nhất quán nhân vật trong các conversational agent dựa trên LLM, tập trung vào hiện tượng chatbot quên thông tin, thay đổi phong cách, tự mâu thuẫn hoặc thoát vai khi hội thoại kéo dài. Tác giả tuyên bố ba đóng góp chính: xây dựng taxonomy gồm năm nhóm cơ chế, đề xuất Persona Consistency Framework và thiết kế một protocol đánh giá thử nghiệm với persona, scenario, rubric và phân tích lỗi.

Điểm mạnh lớn nhất của bài là phạm vi tài liệu tương đối rộng, có liên hệ được persona-based dialogue, long-term memory, grounding, role-playing và evaluation. Pilot study cũng phát hiện một điểm đáng quan tâm: chatbot có thể nhớ đúng thông tin nhưng vẫn bị role-breaking hoặc style drift.

Tuy nhiên, đóng góp chính chưa được chứng minh bằng thiết kế thực nghiệm đủ hợp lệ. Bốn điều kiện C1–C4 được mô tả như một ablation study nhưng thực tế không được chạy độc lập; không có kết quả theo condition. Mô hình sinh, phiên bản, prompt, tham số và LLM judge không được công bố. Chapter 5 và Chapter 6 còn mâu thuẫn về persona, số scenario và quy mô dữ liệu. Ngoài ra, “long-term” chỉ được kiểm tra trong một phiên 20 lượt, chưa phải tương tác dài hạn hoặc nhiều phiên.

Ở trạng thái hiện tại, bài chưa đạt chuẩn gửi tạp chí Q4. Bài cần được xem là một conceptual framework kèm pilot demonstration, không phải một nghiên cứu thực nghiệm đã xác nhận hiệu quả.

---

## B. Bảng điểm chi tiết

| Tiêu chí | Điểm /10 | Trọng số | Điểm quy đổi | Nhận xét ngắn |
|---|---:|---:|---:|---|
| Research problem và objectives | 6.5 | 8 | 5.20 | Vấn đề có ý nghĩa, RQ tương đối rõ nhưng phạm vi “long-term” không khớp thực nghiệm |
| Research gap | 5.5 | 10 | 5.50 | Có nêu gap nhưng chủ yếu dựa trên diễn giải, chưa chứng minh bằng tổng hợp so sánh có hệ thống |
| Novelty và contribution | 3.5 | 15 | 5.25 | Framework chủ yếu sắp xếp lại các kỹ thuật phổ biến; novelty chưa được phân biệt rõ với survey/taxonomy |
| Literature review | 7.0 | 8 | 5.60 | Nguồn khá rộng và mới, nhưng dài, thiên về mô tả và thiếu critical synthesis |
| Proposed framework hoặc method | 4.5 | 15 | 6.75 | Có cấu trúc dễ hiểu nhưng chưa phải kiến trúc triển khai; luồng xử lý còn mâu thuẫn |
| Methodology và reproducibility | 3.0 | 15 | 4.50 | Thiếu model, version, prompt, tham số, judge configuration, code và data lineage |
| Experimental design | 2.5 | 10 | 2.50 | Không chạy đủ bốn condition, không baseline thực sự, không repetition, không randomization |
| Evaluation metrics và protocol | 4.0 | 8 | 3.20 | Có rubric đa chiều nhưng định nghĩa còn chồng lấn; thiếu evaluator reliability |
| Data analysis | 2.5 | 5 | 1.25 | Chủ yếu dùng mean; thiếu SD, CI, effect size, significance test và kiểm soát repeated measures |
| Writing, structure và presentation | 4.5 | 4 | 1.80 | Có tổ chức chương mục nhưng quá dài, lặp ý, pha trộn ngôn ngữ và nhiều bảng khó đọc |
| Limitations, validity và ethics | 5.0 | 2 | 1.00 | Limitations khá trung thực nhưng thiếu threats-to-validity có cấu trúc và ethics |
| **Tổng cộng** |  | **100** | **42.55 ≈ 43/100** | **Chưa đạt tiêu chuẩn Q4** |

---

## C. Major Concerns

### 1. Abstract mô tả nghiên cứu chưa hoàn thành trong khi bài đã có Results

**Vị trí:** Abstract, trang 1; Chapter VI.

Abstract vẫn sử dụng các cách viết như “thiết kế một protocol”, “kết quả kỳ vọng” và không báo cáo bất kỳ kết quả định lượng nào. Trong khi đó, Chapter VI tuyên bố có 60 phản hồi, overall score 4.80–4.81 và 13 trường hợp persona drift.

**Vì sao nghiêm trọng:** Người đọc không thể xác định đây là research proposal, conceptual paper hay completed experiment.

**Ảnh hưởng:** Tạo ra sai lệch về trạng thái nghiên cứu và có thể dẫn đến desk rejection ngay từ vòng biên tập.

**Cách sửa:** Viết lại toàn bộ abstract theo cấu trúc background–gap–method–data–results–contribution–limitation. Không sử dụng “kết quả kỳ vọng”.

**Đoạn có thể dùng trực tiếp:**

> This study proposes a five-component analytical framework for examining persona consistency in character-based LLM agents and evaluates an initial protocol using three personas, five adversarial scenario categories, and 60 multi-turn responses. The pilot results show that memory retention and context awareness remained high, whereas role pressure and style manipulation produced the most frequent persona failures. However, because the study evaluates only one model configuration and does not execute the planned ablation conditions independently, the findings should be interpreted as preliminary evidence rather than validation of the complete framework.

**Mức độ ưu tiên:** Bắt buộc.

---

### 2. Tiêu đề và khái niệm “long-term” không được thực nghiệm hỗ trợ

**Vị trí:** Title, Introduction, RQ4, Experimental Setup và Conclusion.

Bài sử dụng cụm “Long-Term Character-Based Conversational Agents”, nhưng thực nghiệm chỉ gồm một phiên khoảng 20 lượt cho mỗi persona. Không có tương tác qua nhiều ngày, nhiều phiên, memory persistence, session restart hoặc kiểm tra quên dài hạn.

**Vì sao nghiêm trọng:** “Long-term” là một phần trung tâm của tiêu đề và research gap, không phải chi tiết phụ.

**Ảnh hưởng:** Construct validity thấp. Thực nghiệm hiện tại chỉ đo **multi-turn consistency under adversarial prompts**, không đo long-term conversational consistency.

**Cách sửa:** Chọn một trong hai hướng:

1. Thu hẹp tiêu đề và tuyên bố:

> **A Pilot Framework for Evaluating Persona Consistency in Multi-Turn Character-Based LLM Agents**

2. Hoặc thực hiện nghiên cứu nhiều phiên, kiểm tra thông tin sau khoảng trễ, cập nhật memory và xung đột giữa ký ức cũ–mới.

**Mức độ ưu tiên:** Bắt buộc.

---

### 3. Chapter 5 và Chapter 6 không thống nhất về dữ liệu và thiết kế

**Vị trí:** Sections 5.2–5.4 so với Sections 6.2–6.4.

Chapter 5 mô tả:

- Ba persona: giáo viên lịch sử, bạn đồng hành số và nhân vật hư cấu.
- Tên minh họa: Thầy Minh, Lani và Cô An.
- Bốn scenario.
- Mỗi scenario gồm 15–20 lượt.
- Bốn experimental conditions.

Chapter 6 lại sử dụng:

- Professor An, Milo và Lina.
- Năm scenario.
- Tổng cộng 60 phản hồi.
- Khoảng 20 lượt cho mỗi persona.
- Không có kết quả phân tách theo bốn condition.

**Vì sao nghiêm trọng:** Không thể xác định bộ dữ liệu nào thực sự được dùng và quy trình nào thực sự đã chạy.

**Ảnh hưởng:** Data provenance, reproducibility và internal validity đều không đạt yêu cầu.

**Cách sửa:** Tạo một bảng master duy nhất:

| Persona | Scenario | Condition | Repetition | Number of turns | Total responses |
|---|---|---|---:|---:|---:|

Sau đó cập nhật toàn bộ Chapter 5, Chapter 6, Abstract và Conclusion theo đúng bảng này. Mỗi mã P1–P3, S1–S5 và C1–C4 phải có định nghĩa cố định.

**Mức độ ưu tiên:** Bắt buộc.

---

### 4. Bốn experimental conditions chỉ được mô tả, không được thực nghiệm kiểm chứng

**Vị trí:** Sections 5.4, 6.3, 6.8 và 7.4.

Bài giới thiệu C1 Prompt-only, C2 Prompt + Memory, C3 Prompt + Grounding và C4 Full Framework. Tuy nhiên, phần hạn chế thừa nhận các cấu hình này “chưa được chạy như bốn thí nghiệm độc lập trên cùng 60 prompt”.

**Vì sao nghiêm trọng:** Đây là bằng chứng trực tiếp rằng contribution trung tâm của framework chưa được đánh giá.

**Ảnh hưởng:** Không thể kết luận memory, grounding hoặc verification cải thiện persona consistency. Các câu diễn giải về vai trò của từng module chỉ là giả thuyết.

**Cách sửa:** Chạy lại cùng một test set dưới cả bốn condition. Giữ cố định model, prompt sequence và generation parameters. Thực hiện ít nhất ba lần lặp với seed hoặc sampling run khác nhau.

Một thiết kế tối thiểu:

- 3 personas.
- 5 scenarios.
- 4 test turns/scenario.
- 4 conditions.
- 3 repetitions.

Tổng số tối thiểu: **720 responses**.

**Mức độ ưu tiên:** Bắt buộc.

---

### 5. Không xác định mô hình sinh phản hồi và điều kiện tái lập

**Vị trí:** Sections 5.4, 6.1 và 6.3.

Bài chỉ nói sử dụng “một LLM hội thoại” và chạy bằng Python trên Google Colab. Không có:

- Tên model.
- Model version hoặc snapshot.
- API/provider.
- Ngày truy cập.
- Temperature cụ thể.
- Top-p.
- Max tokens.
- Seed.
- Stop sequence.
- Số lần retry.
- Prompt templates.
- Cách duy trì dialogue state.

**Vì sao nghiêm trọng:** Hành vi role-playing và phản ứng trước yêu cầu thoát vai phụ thuộc mạnh vào model policy và system prompt.

**Ảnh hưởng:** Không thể tái lập kết quả 4.80–4.81 hay tỷ lệ role-breaking 18.33%.

**Cách sửa:** Thêm bảng reproducibility:

| Thành phần | Giá trị chính xác |
|---|---|
| Generator model | |
| Model snapshot/version | |
| Provider/API | |
| Access date | |
| Temperature | |
| Top-p | |
| Max output tokens | |
| Random seed/run ID | |
| System prompt | Appendix |
| Memory prompt | Appendix |
| Verification prompt | Appendix |

**Mức độ ưu tiên:** Bắt buộc.

---

### 6. Evaluation protocol không đủ độ tin cậy

**Vị trí:** Sections 5.5–5.6 và 6.8.

Bài tuyên bố manual evaluation là nguồn chấm chính và LLM judge chỉ hỗ trợ, nhưng không cho biết:

- Bao nhiêu người chấm.
- Ai là người chấm.
- Trình độ hoặc kinh nghiệm.
- Mỗi response được bao nhiêu người chấm.
- Có blind condition hay không.
- Judge model nào được dùng.
- Judge prompt và decoding settings.
- Ai giải quyết bất đồng.

Ngoài ra, kết quả lại nói chủ yếu dựa trên LLM-as-a-Judge.

**Vì sao nghiêm trọng:** Các điểm 4.55, 4.80 hay 5.00 có thể là sản phẩm của một evaluator duy nhất hoặc một LLM judge chưa hiệu chỉnh.

**Ảnh hưởng:** Measurement validity rất thấp, đặc biệt đối với style stability và persona consistency.

**Cách sửa:**

- Ít nhất hai người chấm độc lập; tốt hơn là ba.
- Ẩn tên condition.
- Chấm pilot và hiệu chỉnh rubric.
- Báo cáo Krippendorff’s alpha hoặc weighted kappa.
- Công bố đầy đủ LLM judge prompt.
- Đo tương quan giữa human scores và judge scores.

**Mức độ ưu tiên:** Bắt buộc.

---

### 7. Contradiction score, contradiction rate và overall score chưa nhất quán

**Vị trí:** Sections 5.5, 6.4–6.5.

Methodology quy định contradiction rate là biến nhị phân và không đưa vào overall score. Results lại trình bày thêm “contradiction score” 1–5 với giá trị 4.80, trong khi contradiction rate bằng 0%.

**Vì sao nghiêm trọng:** Hai biến có tên gần giống nhau nhưng không có operational definition rõ ràng.

**Ảnh hưởng:** Không biết tại sao contradiction score chỉ đạt 4.80 khi không có response nào được đánh dấu contradiction.

**Cách sửa:** Phải chọn một trong hai:

- **Binary contradiction flag:** 0/1; tính rate.
- **Contradiction severity:** 1–5; định nghĩa từng mức bằng anchor cụ thể.

Nếu giữ cả hai, cần giải thích rõ sự khác biệt và báo cáo confusion matrix giữa severity score và binary flag.

Rubric hiện tại cũng quá tổng quát: mô tả điểm 5 gộp đồng thời persona, memory, contradiction và style, khiến các metric không độc lập.

**Mức độ ưu tiên:** Bắt buộc.

---

### 8. Phân tích theo lượt bị confound với thứ tự scenario

**Vị trí:** Section 6.5 và RQ4.

Turns 11–15 có điểm thấp nhất, đồng thời đây là giai đoạn xuất hiện style challenge hoặc role pressure. Sau đó điểm phục hồi ở Turns 16–20.

**Vì sao nghiêm trọng:** Không thể biết điểm giảm do hội thoại dài hơn hay do scenario khó hơn.

**Ảnh hưởng:** RQ4 về xu hướng persona theo số lượt chưa được trả lời hợp lệ. Kết quả chỉ chứng minh loại prompt ảnh hưởng đến điểm số.

**Cách sửa:**

- Randomize hoặc counterbalance thứ tự scenario giữa các persona và repetitions.
- Đưa cùng một loại challenge vào early, middle và late turns.
- Phân tích riêng hiệu ứng của turn index và scenario type.
- Dùng mixed-effects model với persona và dialogue run là random effects.

**Mức độ ưu tiên:** Bắt buộc.

---

### 9. Framework chưa phải một phương pháp có thể triển khai

**Vị trí:** Chapter IV, đặc biệt sơ đồ trang 18.

Framework tổng hợp các thành phần phổ biến nhưng không định nghĩa:

- Data structure của persona và memory.
- Memory update rule.
- Retrieval function và ranking.
- Cách xử lý nguồn mâu thuẫn.
- Verification threshold.
- Khi nào accept, reject hoặc regenerate.
- Cách correction được thực hiện.
- Cách Persona Adaptation liên hệ với inference pipeline.

Sơ đồ còn đặt Verification trước Grounding, trong khi nội dung mô tả Grounding xảy ra trước generation và Verification xảy ra sau generation. Persona Adaptation được vẽ như bước cuối của pipeline dù phần văn bản xem đây là quá trình offline. Ngoài ra, bài không có Section 4.7 riêng cho Persona Adaptation dù đây là một trong năm thành phần trung tâm.

**Ảnh hưởng:** Framework giống taxonomy hoặc conceptual map hơn là proposed technical method.

**Cách sửa:** Vẽ lại luồng:

> Persona initialization → memory retrieval/grounding → response generation → persona verification → accept hoặc regenerate/correct → controlled memory update.

Đặt Persona Adaptation thành nhánh offline. Thêm pseudocode, input/output, threshold và exception handling.

**Mức độ ưu tiên:** Rất quan trọng.

---

### 10. Chưa có Discussion độc lập và kết luận vượt quá bằng chứng

**Vị trí:** Chapter VI và VII.

Bài chuyển trực tiếp từ Experiments and Results sang Conclusion. Không có Discussion riêng để:

- Đối chiếu kết quả với CharacterEval, InCharacter, PersonaGym hoặc long-term memory benchmarks.
- Giải thích tại sao memory score đạt tuyệt đối.
- Xem xét ceiling effect.
- Phân tích ảnh hưởng của model safety policy đến role-breaking.
- Phân biệt role-breaking có chủ ý vì transparency với persona failure.
- Trình bày internal, external, construct và conclusion validity.

**Ảnh hưởng:** Các kết luận hiện tại chủ yếu diễn giải nội bộ, chưa cho thấy ý nghĩa khoa học so với literature.

**Cách sửa:** Thêm Chapter VII Discussion và chuyển Conclusion thành Chapter VIII. Giảm mạnh việc lặp lại số liệu.

**Mức độ ưu tiên:** Rất quan trọng.

---

## D. Minor Concerns

1. Trang đầu vẫn để “Name” và “Email:” trống; đây là trạng thái chưa sẵn sàng nộp.
2. Tiêu đề ngắt dòng thiếu thẩm mỹ và bản thảo chưa theo template của một journal cụ thể.
3. “I. INTRO” nên đổi thành “1. Introduction” hoặc đúng chuẩn template.
4. Heading và nội dung pha trộn tiếng Anh–tiếng Việt thiếu nhất quán.
5. Persona ở Methodology và Results sử dụng các tên khác nhau.
6. Bảng 6.10 được dùng cho cả qualitative examples và error distribution.
7. Một số bảng ở trang 75–77 quá nhiều cột, tiêu đề bị tách thành các mảnh; cần dùng landscape hoặc tách bảng.
8. Caption như “Hình 6.1 Persona_metric_heatmap” trông giống tên biến hoặc tên file, không phải caption học thuật.
9. Có lỗi đánh máy và câu chưa hoàn chỉnh như “rong các hệ thống…”, “mâu thuẩn”, “trọng cuộc hội thoại”.
10. Nhiều đoạn lặp lại cùng lập luận.
11. Cụm “Trong framework được đề xuất…” và “Từ góc nhìn của nghiên cứu này…” được lặp với mật độ cao.
12. Chapter IV quá dài so với đóng góp kỹ thuật thực tế.
13. Các nguồn documentation như Character.AI, SillyTavern, LangChain và Hugging Face chỉ nên hỗ trợ mô tả.
14. Không có bảng related-work comparison trực tiếp.
15. References cần kiểm tra lại tính nhất quán APA 7, DOI/URL và cách ghi preprint.
16. Bản thảo 100 trang quá dài đối với một journal article thông thường.
17. Một số bảng và đoạn mô tả lặp lại cùng dữ liệu.
18. Không có appendix chứa prompt, dialogue log mẫu, annotation guideline và judge prompt.

---

## E. Missing Information

| Phần | Thông tin còn thiếu | Ảnh hưởng | Nội dung cần bổ sung |
|---|---|---|---|
| Abstract | Kết quả thực tế và giới hạn chính | Không phản ánh nghiên cứu đã thực hiện | N, model, metrics, kết quả chính, limitation |
| Generator | Tên và phiên bản LLM | Không tái lập được | Model ID, provider, snapshot, access date |
| Generation setup | Giá trị temperature, top-p, max tokens, seed | Không kiểm soát randomness | Bảng tham số đầy đủ |
| Prompting | System prompt và persona templates | Không thể kiểm chứng persona control | Công bố trong appendix/repository |
| Experimental conditions | Condition nào thực sự đã chạy | Không xác định treatment | N theo C1–C4 |
| Repetition | Số lần lặp mỗi prompt | Không ước lượng variance | Tối thiểu ba runs |
| Memory | Format, selection và update policy | C2 không tái lập được | Schema và thuật toán update |
| Grounding | Retrieval method và ranking | C3 chỉ là mô tả | Source, embedding, top-k, selection rule |
| Verification | Classifier/judge/threshold và correction action | C4 không phải method hoàn chỉnh | Prompt, model, threshold, regenerate policy |
| Human evaluation | Số evaluator và chuyên môn | Scores không đáng tin cậy | Rater profile và training |
| Reliability | Inter-rater agreement | Không biết mức đồng thuận | Alpha/kappa và CI |
| LLM judge | Model, prompt, runs và bias controls | Judge results không tái lập được | Full evaluation configuration |
| Data analysis | SD, CI, effect size, hypothesis test | Không đánh giá được độ chắc chắn | Descriptive và inferential statistics |
| Baselines | External hoặc strong baseline | Không biết framework tốt hơn gì | Prompt-only, memory baseline, existing method |
| Long-term setting | Multi-session, delays, memory persistence | Không đo đúng title | Thiết kế nhiều phiên |
| Data/code | Repository hoặc supplementary files | Không xác minh dữ liệu | Code, CSV, prompts, annotations |
| Ethics | Consent, data privacy, model terms | Thiếu submission requirement | Ethics statement |
| Threats to validity | Bốn loại validity | Kết luận thiếu giới hạn có hệ thống | Internal, construct, external, conclusion validity |

---

## F. Section-by-Section Evaluation

| Phần | Mức hiện tại | Điểm mạnh | Điểm yếu chính | Nội dung phải sửa | Quyết định |
|---|---|---|---|---|---|
| Title | Yếu | Nêu đúng chủ đề persona consistency | “Long-term” vượt quá thực nghiệm | Thu hẹp title hoặc chạy multi-session | Viết lại |
| Abstract | Rất yếu | Có bối cảnh và framework | Chỉ nói kết quả kỳ vọng, không có số liệu | Viết lại theo nghiên cứu đã hoàn thành | Viết lại hoàn toàn |
| Introduction | Trung bình | Problem và RQ khá rõ | Dài, lặp, đóng góp chưa phân biệt với taxonomy hiện có | Rút 30–40%, làm rõ claim | Sửa lớn |
| Research Gap | Trung bình thấp | Nhận diện được memory, evaluation và long dialogue | Gap chưa được chứng minh bằng comparison matrix | Thêm evidence và related-work table | Sửa lớn |
| Related Work | Khá | Nguồn rộng, nhiều paper phù hợp | Thiên về tóm tắt, thiếu phản biện và synthesis | Tổ chức theo research dimensions | Sửa vừa–lớn |
| Framework | Trung bình thấp | Cấu trúc năm nhóm dễ theo dõi | Không operational, flow sai, thiếu 4.7 Adaptation | Vẽ lại architecture và thêm algorithm | Viết lại phần lõi |
| 5.1 Research Design | Trung bình | Phân biệt conceptual, experimental, evaluation layers | Vẫn xen nhiều nội dung “có thể so sánh” | Chỉ mô tả quy trình đã thực hiện | Sửa lớn |
| 5.2 Persona/Scenario | Yếu | Có bảng persona và pressure types | Không khớp Chapter 6 | Đồng bộ persona, scenario, turns | Viết lại |
| 5.3 Pipeline | Trung bình thấp | Có logging và error labels | Không có thuật toán, code hoặc decision flow | Thêm pseudocode và schema | Sửa lớn |
| 5.4 Experimental Setup | Rất yếu | Dự kiến bốn condition hợp lý | Condition chưa được chạy, thiếu model/parameters | Thiết kế lại và chạy lại | Viết lại hoàn toàn |
| 5.5 Metrics | Trung bình | Bao phủ nhiều chiều persona | Rubric chồng lấn, contradiction không rõ | Operationalize từng metric | Sửa lớn |
| 5.6 Protocol | Yếu | Có pilot annotation idea | Không có rater details và reliability | Thiết kế human evaluation thật | Viết lại |
| 5.7 Data Analysis | Yếu | Có phân tích persona/scenario/turn/error | Thiếu uncertainty và inferential plan | Thêm statistical analysis thích hợp | Viết lại |
| Experiments/Results | Yếu | Có số liệu và qualitative examples | N nhỏ, không baseline, không ablation, ceiling effect | Rerun experiment và báo cáo đầy đủ | Làm lại |
| Discussion | Thiếu | Một phần diễn giải nằm trong Results | Không có đối chiếu literature hoặc validity | Viết chương mới | Bổ sung mới |
| Limitations | Trung bình khá | Thừa nhận nhiều giới hạn thật | Chưa cấu trúc theo validity; thiếu ethics | Thêm threats và ethics | Sửa lớn |
| Conclusion | Trung bình thấp | Tóm tắt được pilot findings | Lặp số liệu, một số claim vượt quá evidence | Giảm claim, nhấn mạnh preliminary nature | Viết lại |
| Writing/presentation | Yếu | Bảng, hình và heading tương đối nhiều | Dài, lặp, bảng vỡ, ngôn ngữ không thống nhất | Rút còn khoảng 30–40% độ dài hiện tại | Sửa lớn |

---

## G. Revision Priority

### Priority 1: Bắt buộc sửa trước khi gửi

1. Quyết định rõ bài là conceptual framework paper hay full experimental paper.
2. Đồng bộ toàn bộ persona, scenario, condition và sample size giữa Chapters 5–7.
3. Chạy thật bốn experimental conditions hoặc bỏ claim về ablation/framework effectiveness.
4. Công bố model, version, prompts và generation parameters.
5. Thiết kế lại human/LLM evaluation với nhiều evaluator và reliability.
6. Randomize hoặc counterbalance scenario order.
7. Viết lại Abstract, Title, Results claims và Conclusion.
8. Thêm Discussion và Threats to Validity.

### Priority 2: Cần sửa để tăng khả năng được chấp nhận

1. Xây dựng related-work comparison table để chứng minh novelty.
2. Chuyển framework thành pipeline có input, output, algorithm và feedback loop.
3. Thêm baseline ngoài prompt-only.
4. Báo cáo SD, CI, effect size và kiểm định phù hợp.
5. Công bố code, dataset, prompt và annotation guideline.
6. Kiểm tra judge bias và tương quan human–LLM scores.

### Priority 3: Cải thiện chất lượng trình bày

1. Rút mạnh các đoạn lặp trong Chapters 3–5.
2. Chuẩn hóa một ngôn ngữ cho toàn bài.
3. Sửa lại bảng nhiều cột ở trang 75–77.
4. Đánh số lại bảng, hình và chương.
5. Sửa lỗi ngữ pháp, thuật ngữ và citation style.
6. Chuyển phần chi tiết dài sang appendix hoặc supplementary materials.

---

## H. Final Decision

### Reject and Resubmit

Bản thảo có chủ đề phù hợp với NLP, conversational agents và human–AI interaction, đồng thời có một số quan sát pilot đáng quan tâm về role-breaking và style drift. Tuy nhiên, nghiên cứu hiện chưa chứng minh được contribution trung tâm. Experimental conditions được mô tả nhưng không được chạy đầy đủ; model và tham số không được công bố; Chapter 5 và Chapter 6 không nhất quán; evaluation thiếu nhiều evaluator và reliability; còn phân tích theo lượt bị confound với loại scenario. Do đó, các kết quả hiện tại không đủ để xác nhận hiệu quả của Persona Consistency Framework hoặc đưa ra kết luận về long-term consistency. Những vấn đề này không thể giải quyết bằng chỉnh sửa văn bản đơn thuần mà đòi hỏi thiết kế lại và chạy lại phần lớn thực nghiệm. Một bản thảo mới có dữ liệu, baseline, ablation và evaluation hợp lệ có thể được xem xét lại như một submission mới.

---

## I. Publication Readiness

- **Overall Score:** 43/100
- **Q4 Readiness:** 30%
- **Novelty Level:** Thấp
- **Methodological Strength:** Yếu
- **Reproducibility:** Thấp
- **Risk of Rejection:** Rất cao
- **Phần yếu nhất:** Experimental design và reproducibility
- **Phần tốt nhất:** Literature coverage và nhận diện nhiều dạng persona failure

### Ba việc cần làm ngay tiếp theo

1. Khóa lại một experimental design duy nhất, đồng bộ Chapters 5–7 và chạy đủ C1–C4.
2. Công bố đầy đủ model, prompts, parameters, evaluator protocol và raw data.
3. Thiết kế lại đánh giá với human raters, inter-rater agreement, randomization và statistical analysis.
