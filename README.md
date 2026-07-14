# Persona Consistency Framework (PCF) — code, data & human evaluation

Kho lưu trữ nghiên cứu về Persona Consistency Framework: giữ vai nhất quán
cho chatbot đóng vai nhân vật (persona) trong hội thoại dài, đánh giá qua
LLM-as-a-judge và human evaluation.

## Cấu trúc

| Thư mục/file | Nội dung |
|---|---|
| `pcf_experiment_v2/` | **Thực nghiệm chính** (bản thiết kế lại có baseline/ablation/counterbalancing). Code (`src/`), config, prompt, dữ liệu thô + đã judge (`outputs/`), thống kê + hình (`outputs/summaries`, `outputs/figures`). Xem `pcf_experiment_v2/README.md` để chạy lại. |
| `per_score/` | Bảng chấm human evaluation của 2 giáo viên (513 mẫu), script tổng hợp (`make_report_files.py`, `make_report_figures.py`) và bộ file kết quả cho báo cáo (`report/`, xem `report/README_report.md`). |
| `a/` | Bản thảo bài báo (các phiên bản `.docx`), phản biện nội bộ (`Phan_bien_Q4_Persona_Consistency.md`), quy tắc trích dẫn/viết. |
| `persona_experiment_outputs/`, `persona_experiment.ipynb` | Pilot thực nghiệm ban đầu (trước bản `pcf_experiment_v2`). |
| `PCF_Paper_Final_HumanEval_v08.docx` | Bản thảo bài báo hiện tại. |
| `Ke_hoach_code_lai_thuc_nghiem_PCF.md`, `Checklist_thuc_hien_nghien_cuu_PCF.md` | Kế hoạch thiết kế lại thực nghiệm và checklist theo dõi tiến độ. |

## Tái tạo kết quả

```bash
cd pcf_experiment_v2
pip install -r requirements.txt
# cần OPENAI_API_KEY (generator G1, memory_extractor, verifier) và
# ANTHROPIC_API_KEY (judge, generator G2) trong biến môi trường
python run_full.py           # sinh + judge + phân tích điều kiện B0/C1/C2/C3/C4 (generator G1)
python run_generator2.py     # (tùy chọn) lặp lại với generator thứ 2 để kiểm tra khái quát hóa
```

Không cần API key: `DRY_RUN=1 python run_full.py` chạy toàn bộ pipeline với output giả lập.

## Trạng thái / hạn chế đã biết

Xem `Phan_bien_Q4_Persona_Consistency.md` và `Checklist_thuc_hien_nghien_cuu_PCF.md`.
Đáng chú ý: bộ 513 mẫu human evaluation hiện có (`per_score/`) được sinh với
verifier = judge (cùng model) — vấn đề này đã được sửa trong `model_config.json`
cho **lần chạy tiếp theo**, nhưng dữ liệu đã chấm hiện tại vẫn phản ánh cấu hình cũ.

## License

TODO — chọn license trước khi công khai repo (vd. `MIT` cho code, `CC-BY-4.0` cho dữ liệu/bài viết).
