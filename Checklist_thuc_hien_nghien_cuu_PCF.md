# CHECKLIST THỰC HIỆN LẠI NGHIÊN CỨU PERSONA CONSISTENCY

> Dùng file này để đánh dấu tiến độ.  
> Quy ước:
>
> - `[ ]` Chưa làm
> - `[x]` Đã hoàn thành
> - `[~]` Đang thực hiện

---

# A. CHỐT HƯỚNG NGHIÊN CỨU

- [ ] Chọn hướng chính: evaluation methodology paper.
- [ ] Xác định PCF là analytical framework, không tuyên bố là mô hình mới.
- [ ] Chốt contribution chính.
- [ ] Chốt phạm vi bài báo.
- [ ] Bỏ các tuyên bố vượt quá dữ liệu.
- [ ] Xác định tạp chí mục tiêu.
- [ ] Kiểm tra giới hạn số từ và template tạp chí.

---

# B. SỬA CÂU HỎI NGHIÊN CỨU

- [ ] Giữ RQ1 về các dạng persona drift.
- [ ] Chuyển RQ2 cũ thành objective hoặc bỏ.
- [ ] Thêm RQ về hiệu quả của structured memory.
- [ ] Thêm RQ về verification nếu chạy C3.
- [ ] Thêm RQ về human–LLM agreement.
- [ ] Chỉ giữ RQ có thể trả lời bằng dữ liệu thực nghiệm.
- [ ] Cập nhật Abstract theo RQ mới.
- [ ] Cập nhật Introduction theo RQ mới.
- [ ] Cập nhật Conclusion theo RQ mới.

---

# C. THIẾT KẾ ĐIỀU KIỆN THÍ NGHIỆM

- [ ] Tạo B0 — No Persona Baseline.
- [ ] Tạo C1 — Prompt-Only.
- [ ] Tạo C2 — Prompt + Structured Memory.
- [ ] Quyết định có chạy C3 — Memory + Verification hay không.
- [ ] Giữ cùng persona giữa các condition.
- [ ] Giữ cùng scenario giữa các condition.
- [ ] Giữ cùng tham số sinh giữa các condition.
- [ ] Không dùng best-of selection.
- [ ] Ghi rõ input/output của từng condition.
- [ ] Vẽ sơ đồ data flow của PCF.

---

# D. PERSONA

- [ ] Chốt số persona tối thiểu.
- [ ] Tăng từ 3 lên ít nhất 6 persona.
- [ ] Mục tiêu tốt hơn: 10 persona.
- [ ] Tạo schema persona thống nhất.
- [ ] Mỗi persona có role.
- [ ] Mỗi persona có background.
- [ ] Mỗi persona có core traits.
- [ ] Mỗi persona có speaking style.
- [ ] Mỗi persona có known facts.
- [ ] Mỗi persona có likes.
- [ ] Mỗi persona có dislikes.
- [ ] Mỗi persona có behavioral constraints.
- [ ] Mỗi persona có domain boundary.
- [ ] Kiểm tra độ dài profile giữa các persona.
- [ ] Kiểm tra độ khó tương đối giữa các persona.
- [ ] Nhờ người khác review persona.
- [ ] Chỉnh persona bị mơ hồ hoặc quá dễ.

---

# E. SCENARIO

- [ ] Giữ 5 nhóm scenario chính.
- [ ] Viết lại Memory Recall khó hơn.
- [ ] Thêm distractor cho Memory Recall.
- [ ] Thêm delayed recall.
- [ ] Thêm conflicting memory prompt.
- [ ] Viết lại Contradiction Trap tinh vi hơn.
- [ ] Thêm presupposition.
- [ ] Thêm false quotation.
- [ ] Thêm emotional pressure.
- [ ] Viết lại Style Challenge.
- [ ] Thêm slang request.
- [ ] Thêm language switching.
- [ ] Thêm imitation request.
- [ ] Viết lại Role Pressure.
- [ ] Thêm meta disclosure prompt.
- [ ] Thêm system-prompt extraction prompt.
- [ ] Viết lại Context Switching.
- [ ] Thêm out-of-domain prompt.
- [ ] Thêm rapid topic switching.
- [ ] Mỗi scenario có target failure rõ.
- [ ] Mỗi prompt có difficulty label.
- [ ] Có hướng dẫn expected behavior.
- [ ] Có ít nhất một chuyên gia hoặc đồng nghiệp review scenario.
- [ ] Chạy thử scenario trên một số mẫu.
- [ ] Loại prompt quá dễ.
- [ ] Loại prompt mơ hồ.

---

# F. COUNTERBALANCING

- [ ] Tạo Latin square cho 5 scenario.
- [ ] Lưu Latin square vào file JSON.
- [ ] Gán thứ tự theo persona và run.
- [ ] Kiểm tra mọi scenario xuất hiện ở mọi vị trí.
- [ ] Không dùng cùng một thứ tự cho tất cả persona.
- [ ] Lưu scenario position trong log.
- [ ] Kiểm tra code counterbalance bằng unit test.
- [ ] Ghi rõ counterbalancing trong Methodology.

---

# G. CẤU HÌNH MÔ HÌNH

- [ ] Chốt generator chính.
- [ ] Chốt model snapshot ID.
- [ ] Chốt judge model.
- [ ] Chốt judge snapshot ID.
- [ ] Lưu SDK version.
- [ ] Lưu provider.
- [ ] Lưu temperature.
- [ ] Lưu top-p.
- [ ] Lưu max tokens.
- [ ] Lưu frequency penalty.
- [ ] Lưu presence penalty.
- [ ] Lưu timestamp.
- [ ] Xác định chiến lược seed.
- [ ] Nếu không đặt seed được, ghi rõ.
- [ ] Đặt judge temperature = 0 nếu phù hợp.
- [ ] Chạy ít nhất 3 lần cho mỗi prompt.
- [ ] Không trộn dữ liệu giữa các lần chạy.

---

# H. CODE HỆ THỐNG

- [ ] Tạo cấu trúc thư mục dự án.
- [ ] Viết `load_config.py`.
- [ ] Viết `build_dialogues.py`.
- [ ] Viết `generate_responses.py`.
- [ ] Viết `memory_manager.py`.
- [ ] Viết `verifier.py` nếu có C3.
- [ ] Viết `judge_responses.py`.
- [ ] Viết `sample_for_human_eval.py`.
- [ ] Viết `analyze_results.py`.
- [ ] Viết `utils.py`.
- [ ] Thêm retry.
- [ ] Thêm exponential backoff.
- [ ] Thêm resume khi notebook dừng.
- [ ] Validate JSON output.
- [ ] Lưu raw response ngay sau mỗi lượt.
- [ ] Lưu memory state trước và sau.
- [ ] Lưu token usage nếu API trả về.
- [ ] Lưu latency.
- [ ] Lưu retry count.
- [ ] Thêm logging ra file.
- [ ] Thêm unit test cơ bản.
- [ ] Chạy thử trên 1 persona.
- [ ] Chạy thử trên 1 condition.
- [ ] Kiểm tra log trước khi chạy toàn bộ.

---

# I. STRUCTURED MEMORY

- [ ] Chốt schema memory.
- [ ] Có persona facts.
- [ ] Có user facts.
- [ ] Có shared events.
- [ ] Có preferences.
- [ ] Có constraints.
- [ ] Có recent summary.
- [ ] Viết hàm initialize memory.
- [ ] Viết hàm update memory.
- [ ] Viết hàm retrieve memory.
- [ ] Kiểm tra memory không tự thêm thông tin sai.
- [ ] Lưu memory state từng turn.
- [ ] Ghi rõ memory update policy trong bài.
- [ ] Kiểm tra C2 chỉ khác C1 ở memory.
- [ ] Không thay đổi prompt ngoài phần cần thiết.

---

# J. VERIFICATION

- [ ] Chốt có chạy C3 hay không.
- [ ] Viết verification prompt.
- [ ] Định nghĩa accept.
- [ ] Định nghĩa revise.
- [ ] Định nghĩa reject.
- [ ] Định nghĩa violation types.
- [ ] Có role_breaking.
- [ ] Có style_drift.
- [ ] Có memory_failure.
- [ ] Có context_confusion.
- [ ] Có self_contradiction.
- [ ] Có domain_drift.
- [ ] Có meta_disclosure.
- [ ] Có constraint_violation.
- [ ] Lưu verdict của verifier.
- [ ] Lưu response trước sửa.
- [ ] Lưu response sau sửa.
- [ ] Không xóa response gốc.
- [ ] Ghi rõ số lần revise tối đa.

---

# K. LLM-AS-A-JUDGE

- [ ] Hoàn thiện rubric 1–5.
- [ ] Mô tả rõ mức 1.
- [ ] Mô tả rõ mức 2.
- [ ] Mô tả rõ mức 3.
- [ ] Mô tả rõ mức 4.
- [ ] Mô tả rõ mức 5.
- [ ] Định nghĩa CF.
- [ ] Định nghĩa error labels.
- [ ] Tách role_breaking và domain_drift.
- [ ] Thêm confidence field.
- [ ] Judge nhận persona profile.
- [ ] Judge nhận full history.
- [ ] Judge nhận current user message.
- [ ] Judge nhận target response.
- [ ] Judge trả JSON hợp lệ.
- [ ] Có retry nếu JSON lỗi.
- [ ] Lưu judge note.
- [ ] Không gọi error label là ground truth.
- [ ] Dùng cụm “LLM-inferred error label” trong bài.

---

# L. HUMAN EVALUATION

- [ ] Chọn ít nhất 2 người chấm.
- [ ] Viết hướng dẫn chấm.
- [ ] Tạo form hoặc CSV chấm.
- [ ] Ẩn condition.
- [ ] Ẩn model.
- [ ] Random hóa thứ tự mẫu.
- [ ] Lấy mẫu phân tầng theo condition.
- [ ] Lấy mẫu phân tầng theo persona.
- [ ] Lấy mẫu phân tầng theo scenario.
- [ ] Bao gồm toàn bộ CF = 1.
- [ ] Bao gồm case điểm thấp.
- [ ] Bao gồm case điểm cao.
- [ ] Chấm thử 10–20 mẫu.
- [ ] Thảo luận điểm bất đồng.
- [ ] Sửa wording rubric nếu cần.
- [ ] Chấm chính thức.
- [ ] Không để rater trao đổi trong vòng chính.
- [ ] Lưu annotation riêng từng rater.
- [ ] Tính weighted Cohen’s kappa cho PC.
- [ ] Tính weighted Cohen’s kappa cho MR.
- [ ] Tính weighted Cohen’s kappa cho SS.
- [ ] Tính weighted Cohen’s kappa cho CA.
- [ ] Tính Cohen’s kappa cho CF.
- [ ] Tính agreement cho error label.
- [ ] Tính human–LLM agreement.
- [ ] Báo cáo cách xử lý disagreement.

---

# M. PHÂN TÍCH THỐNG KÊ

- [ ] Làm sạch dữ liệu.
- [ ] Kiểm tra duplicate.
- [ ] Kiểm tra missing.
- [ ] Kiểm tra API error.
- [ ] Kiểm tra judge JSON error.
- [ ] Tính mean.
- [ ] Tính standard deviation.
- [ ] Tính median.
- [ ] Tính IQR.
- [ ] Tính Contradiction Rate.
- [ ] Tính Wilson 95% CI.
- [ ] Tính theo condition.
- [ ] Tính theo persona.
- [ ] Tính theo scenario.
- [ ] Tính theo turn position.
- [ ] Tính theo run.
- [ ] Chạy Wilcoxon cho hai condition.
- [ ] Chạy Friedman nếu có ba condition.
- [ ] Hiệu chỉnh multiple comparisons.
- [ ] Tính effect size.
- [ ] Không chỉ báo cáo p-value.
- [ ] Không coi mọi turn hoàn toàn độc lập.
- [ ] Cân nhắc phân tích ở dialogue level.
- [ ] Ghi rõ exploratory analysis.
- [ ] Không dùng từ “significant” nếu chưa test.

---

# N. HÌNH VÀ BẢNG

- [ ] Vẽ kiến trúc PCF.
- [ ] Vẽ data flow B0/C1/C2/C3.
- [ ] Tạo bảng so sánh PCF với RoleLLM.
- [ ] Thêm CharacterEval.
- [ ] Thêm InCharacter.
- [ ] Thêm SocialBench.
- [ ] Tạo bảng persona.
- [ ] Tạo bảng scenario.
- [ ] Tạo bảng experiment conditions.
- [ ] Tạo bảng model configuration.
- [ ] Tạo bảng human evaluator setup.
- [ ] Tạo bảng agreement.
- [ ] Tạo bảng statistical tests.
- [ ] Vẽ Overall theo condition.
- [ ] Vẽ rubric score theo condition.
- [ ] Vẽ Contradiction Rate theo condition.
- [ ] Vẽ error-label distribution.
- [ ] Vẽ score theo scenario.
- [ ] Vẽ score theo turn position.
- [ ] Vẽ human–LLM agreement.
- [ ] Vẽ heatmap persona × scenario.
- [ ] Kiểm tra hình đọc được khi in đen trắng.
- [ ] Kiểm tra font hình.
- [ ] Kiểm tra caption.
- [ ] Đánh số hình và bảng đúng.

---

# O. REPRODUCIBILITY

- [ ] Tạo GitHub hoặc OSF repository.
- [ ] Đăng notebook.
- [ ] Đăng source code.
- [ ] Đăng persona.
- [ ] Đăng scenario.
- [ ] Đăng prompts.
- [ ] Đăng rubric.
- [ ] Đăng raw logs.
- [ ] Đăng judged outputs.
- [ ] Đăng config JSON.
- [ ] Đăng requirements.txt.
- [ ] Viết README chạy lại.
- [ ] Ghi môi trường Python.
- [ ] Ghi SDK version.
- [ ] Ghi model snapshot.
- [ ] Ghi known limitations.
- [ ] Ẩn API key.
- [ ] Kiểm tra repository public.
- [ ] Thêm Data Availability Statement.
- [ ] Thêm Code Availability Statement.

---

# P. SỬA BÀI BÁO

## Introduction

- [ ] Viết lại problem statement.
- [ ] Viết gap dựa trên bảng đối chiếu.
- [ ] Hạ tuyên bố novelty.
- [ ] Cập nhật contributions.
- [ ] Cập nhật RQ.

## Related Work

- [ ] Viết theo hướng critical synthesis.
- [ ] Thêm RoleLLM.
- [ ] Thêm CharacterEval.
- [ ] Thêm InCharacter.
- [ ] Thêm SocialBench.
- [ ] Thêm LLM-as-a-Judge bias.
- [ ] Nêu limitations của từng nhánh.

## Framework

- [ ] Thêm formal definition.
- [ ] Thêm input/output từng component.
- [ ] Thêm data-flow diagram.
- [ ] Làm rõ Maintenance vs Grounding.
- [ ] Làm rõ Verification.
- [ ] Làm rõ Adaptation là offline component.
- [ ] Không tuyên bố framework đã được kiểm chứng nếu chưa chạy đủ.

## Methodology

- [ ] Viết lại experiment design.
- [ ] Thêm baseline.
- [ ] Thêm ablation.
- [ ] Thêm multiple runs.
- [ ] Thêm counterbalancing.
- [ ] Thêm human evaluation.
- [ ] Thêm sampling strategy.
- [ ] Thêm statistical plan.
- [ ] Thêm reproducibility artifact.

## Results

- [ ] Báo cáo theo condition.
- [ ] Báo cáo variance.
- [ ] Báo cáo CI.
- [ ] Báo cáo agreement.
- [ ] Báo cáo statistical tests.
- [ ] Không suy diễn quá mức.
- [ ] Tách primary và exploratory findings.

## Discussion

- [ ] Thảo luận memory effect.
- [ ] Thảo luận verification effect nếu có.
- [ ] Thảo luận ceiling effect.
- [ ] Thảo luận model-specific bias.
- [ ] Thảo luận human–LLM disagreement.
- [ ] Thảo luận practical implications.
- [ ] Thảo luận failure cases.

## Limitations

- [ ] Ghi rõ số model.
- [ ] Ghi rõ số persona.
- [ ] Ghi rõ số run.
- [ ] Ghi rõ giới hạn human sample.
- [ ] Ghi rõ model snapshot có thể thay đổi.
- [ ] Ghi rõ dữ liệu xây dựng thủ công.
- [ ] Ghi rõ ngôn ngữ thí nghiệm.
- [ ] Ghi rõ chưa đo multi-session nếu chưa làm.

## Conclusion

- [ ] Chỉ kết luận theo dữ liệu.
- [ ] Không khái quát cho mọi LLM.
- [ ] Không nói PCF giải quyết hoàn toàn persona drift.
- [ ] Nêu rõ contribution thực nghiệm.
- [ ] Nêu hướng tiếp theo ngắn gọn.

---

# Q. KIỂM TRA CUỐI TRƯỚC KHI NỘP

- [ ] Tất cả RQ đều có câu trả lời trong Results.
- [ ] Tất cả contribution đều có bằng chứng.
- [ ] Không có bảng đề xuất bị trình bày như kết quả đã chạy.
- [ ] Không có số liệu cũ còn sót.
- [ ] Không trộn pilot cũ với thực nghiệm mới.
- [ ] Tất cả hình khớp dữ liệu.
- [ ] Tất cả bảng khớp dữ liệu.
- [ ] Tất cả model ID chính xác.
- [ ] Tất cả timestamp chính xác.
- [ ] Tất cả reference có trong nội dung.
- [ ] Tất cả reference format đúng.
- [ ] Kiểm tra ngữ pháp tiếng Anh.
- [ ] Kiểm tra plagiarism.
- [ ] Kiểm tra AI-generated text policy của tạp chí.
- [ ] Kiểm tra ethics statement.
- [ ] Kiểm tra data availability.
- [ ] Kiểm tra code availability.
- [ ] Nhờ ít nhất một người đọc phản biện lần cuối.
- [ ] Chỉ nộp khi checklist bắt buộc đã hoàn thành.

---

# R. MỐC HOÀN THÀNH TỐI THIỂU ĐỂ NHẮM Q4

- [ ] Có baseline.
- [ ] Có ít nhất C1 và C2.
- [ ] Có ít nhất 6 persona.
- [ ] Có ít nhất 3 lần chạy.
- [ ] Có counterbalancing.
- [ ] Có human evaluation.
- [ ] Có inter-rater agreement.
- [ ] Có statistical testing phù hợp.
- [ ] Có public code và data.
- [ ] Có bảng đối chiếu framework hiện có.
- [ ] Có formalization PCF.
- [ ] Có bản tiếng Anh học thuật.
