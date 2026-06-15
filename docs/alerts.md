# Alert Rules và Runbook

## 1. High latency P95
- Mức độ: P2
- Điều kiện kích hoạt: `latency_p95_ms > 2500 for 1m`
- Ảnh hưởng: Độ trễ tail latency vượt SLO, người dùng có thể phải chờ phản hồi quá lâu
- Kiểm tra ban đầu:
  1. Mở các trace chậm nhất trong 1 giờ gần nhất
  2. So sánh thời gian của RAG span và LLM span
  3. Kiểm tra incident toggle `rag_slow` có đang bật hay không
- Hướng giảm thiểu:
  - Rút gọn query quá dài
  - Chuyển sang nguồn retrieval dự phòng
  - Giảm kích thước prompt hoặc số context được đưa vào model

## 2. High error rate
- Mức độ: P1
- Điều kiện kích hoạt: `error_rate_pct > 5 for 1m`
- Ảnh hưởng: Người dùng nhận response lỗi hoặc request không hoàn tất
- Kiểm tra ban đầu:
  1. Nhóm log theo `error_type` để xem lỗi nào xuất hiện nhiều nhất
  2. Kiểm tra các trace thất bại trong Langfuse
  3. Xác định lỗi đến từ LLM, tool, schema hay tầng ứng dụng
- Hướng giảm thiểu:
  - Rollback thay đổi gần nhất nếu lỗi xuất hiện sau deploy
  - Tạm tắt tool đang lỗi hoặc chuyển sang đường xử lý dự phòng
  - Retry bằng fallback model khi lỗi liên quan đến model chính

## 3. Cost budget spike
- Mức độ: P2
- Điều kiện kích hoạt: `hourly_cost_usd > 0.04 for 1m`
- Ảnh hưởng: Tốc độ tiêu thụ chi phí vượt ngân sách dự kiến
- Ghi chú metric: trong code hiện tại, `hourly_cost_usd` là alias của `total_cost_usd` trong snapshot metric
- Kiểm tra ban đầu:
  1. Tách trace theo `feature` và `model` để tìm nhóm request gây tăng chi phí
  2. So sánh `tokens_in` và `tokens_out` trước và sau khi alert firing
  3. Kiểm tra incident toggle `cost_spike` có đang bật hay không
- Hướng giảm thiểu:
  - Rút ngắn prompt và giới hạn độ dài output
  - Route request đơn giản sang model rẻ hơn
  - Áp dụng prompt cache hoặc response cache cho các request lặp lại
