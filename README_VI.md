# Day 13 - Observability Lab

Đây là bài lab thực hành về **Monitoring, Logging và Observability** cho một ứng dụng FastAPI dạng agent. Repo đã có sẵn khung code, nhưng còn một số phần `TODO` cần hoàn thiện để hệ thống có log chuẩn, trace đầy đủ, metric xem được, alert có ý nghĩa và báo cáo nộp bài rõ ràng.

## Mục tiêu bài làm

Sau khi hoàn thành, ứng dụng cần có:

- Structured JSON logging đúng schema
- Correlation ID xuyên suốt mỗi request
- PII scrubbing để không lộ dữ liệu nhạy cảm trong log
- Langfuse tracing với ít nhất 10 traces live
- Metrics cơ bản cho latency, traffic, error, token, cost và quality
- Dashboard đủ 6 panels
- Alert rules và runbook cho các sự cố chính
- Blueprint report mô tả bằng chứng triển khai và đóng góp cá nhân

## Yêu cầu cần hoàn thiện trong code

Các phần chính cần làm nằm trong:

- `app/middleware.py`: tạo và truyền `x-request-id`, bind `correlation_id` vào log context, thêm header thời gian xử lý
- `app/main.py`: enrich log bằng `user_id_hash`, `session_id`, `feature`, `model`, `env`
- `app/logging_config.py`: bật processor scrub PII trước khi ghi log
- `app/pii.py`: bổ sung pattern để che dữ liệu nhạy cảm như email, số điện thoại, địa chỉ, passport hoặc thông tin cá nhân khác
- `config/alert_rules.yaml`: kiểm tra và hoàn thiện ít nhất 3 alert rules có runbook link
- `docs/blueprint-template.md`: điền báo cáo nhóm, bằng chứng kỹ thuật, incident response và đóng góp cá nhân

## Cài đặt và chạy app

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Sau khi chạy, app mặc định ở:

```text
http://127.0.0.1:8000
```

Các endpoint quan trọng:

- `GET /health`: kiểm tra app, trạng thái tracing và incident
- `GET /metrics`: xem metric hiện tại
- `POST /chat`: gửi request đến agent
- `POST /incidents/{name}/enable`: bật một incident giả lập
- `POST /incidents/{name}/disable`: tắt incident giả lập

Ví dụ gọi `/chat`:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -H "x-request-id: req-demo1234" \
  -d '{
    "user_id": "u_team_01",
    "session_id": "s_demo_01",
    "feature": "qa",
    "message": "Xin chào, hãy trả lời câu hỏi mẫu"
  }'
```

## Cấu hình môi trường

File `.env.example` có các biến mẫu:

```env
APP_ENV=dev
APP_NAME=day13-observability-lab
LOG_LEVEL=INFO
LOG_PATH=data/logs.jsonl
AUDIT_LOG_PATH=data/audit.jsonl
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=https://cloud.langfuse.com
```

Nếu dùng Langfuse, cần điền:

- `LANGFUSE_PUBLIC_KEY`
- `LANGFUSE_SECRET_KEY`
- `LANGFUSE_HOST`

## Script hỗ trợ kiểm tra

Tạo request test:

```bash
python scripts/load_test.py --concurrency 5
```

Bật sự cố giả lập:

```bash
python scripts/inject_incident.py --scenario rag_slow
```

Kiểm tra log và tiến độ implementation:

```bash
python scripts/validate_logs.py
```

Mục tiêu tối thiểu là `VALIDATE_LOGS_SCORE >= 80/100`.

## Dashboard cần có

Dashboard chính cần đủ 6 panels:

1. Latency P50/P95/P99
2. Traffic, ví dụ request count hoặc QPS
3. Error rate có breakdown
4. Cost over time
5. Tokens in/out
6. Quality proxy, ví dụ heuristic score, thumbs hoặc regenerate rate

Yêu cầu chất lượng dashboard:

- Time range mặc định: 1 giờ
- Auto refresh: 15-30 giây
- Có threshold hoặc SLO line rõ ràng
- Đơn vị đo được ghi rõ
- Main dashboard chỉ nên có khoảng 6-8 panels

## Alert và runbook

Cần có ít nhất 3 alert rules:

- High latency P95
- High error rate
- Cost budget spike

Mỗi alert nên có:

- Tên alert
- Điều kiện trigger
- Mức độ nghiêm trọng
- Runbook link trỏ đến `docs/alerts.md`
- Cách kiểm tra nguyên nhân và hướng giảm thiểu

## Báo cáo cần nộp

Điền file:

```text
docs/blueprint-template.md
```

Các phần quan trọng:

- Tên nhóm, repo URL, danh sách thành viên
- Điểm `VALIDATE_LOGS_FINAL_SCORE`
- Tổng số traces trên Langfuse
- Kết quả kiểm tra PII leak
- Screenshot correlation ID, PII redaction, trace waterfall
- Screenshot dashboard đủ 6 panels
- Bảng SLO
- Alert rules và runbook
- Incident response: scenario, triệu chứng, root cause, bằng chứng, cách fix
- Đóng góp cá nhân của từng thành viên kèm commit hoặc PR

## Cách chấm điểm

Tổng điểm theo mô hình **60/40**:

- **60 điểm nhóm**:
  - 30 điểm technical implementation: logging, tracing, dashboard, SLO, alerts, PII
  - 10 điểm incident response và debugging
  - 20 điểm live demo và trình bày
- **40 điểm cá nhân**:
  - 20 điểm báo cáo cá nhân
  - 20 điểm bằng chứng commit hoặc PR

Điều kiện đạt:

- `VALIDATE_LOGS_SCORE >= 80/100`
- Có ít nhất 10 traces live trên Langfuse
- Dashboard đủ 6 panels
- Blueprint report có đầy đủ tên thành viên và bằng chứng

## Gợi ý chia việc trong nhóm

- Member A: Logging và PII
- Member B: Tracing và log enrichment
- Member C: SLO và alerts
- Member D: Load test và incident injection
- Member E: Dashboard, evidence và report

## Cấu trúc repo

```text
app/
  main.py                FastAPI app và endpoint chính
  agent.py               luồng xử lý agent
  logging_config.py      cấu hình structlog và ghi JSONL
  middleware.py          correlation ID middleware
  pii.py                 helper scrub/hash dữ liệu nhạy cảm
  tracing.py             helper Langfuse tracing
  schemas.py             request/response/log schema
  metrics.py             metric in-memory
  incidents.py           bật/tắt incident giả lập
  mock_llm.py            LLM giả lập deterministic
  mock_rag.py            retrieval giả lập deterministic
config/
  slo.yaml               SLO mẫu
  alert_rules.yaml       alert rules mẫu
  logging_schema.json    schema log kỳ vọng
scripts/
  load_test.py           tạo request test
  inject_incident.py     bật incident giả lập
  validate_logs.py       kiểm tra log
data/
  sample_queries.jsonl   query mẫu
  expected_answers.jsonl đáp án mẫu
  incidents.json         mô tả incident
docs/
  blueprint-template.md  báo cáo nộp bài
  alerts.md              runbook alert
  dashboard-spec.md      yêu cầu dashboard
  grading-evidence.md    checklist bằng chứng chấm điểm
```
