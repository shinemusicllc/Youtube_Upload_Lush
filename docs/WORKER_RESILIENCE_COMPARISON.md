# Worker Resilience Comparison

## Mục tiêu

Tài liệu này gom lại phần so sánh thực dụng giữa:

- app cũ `.NET/WPF + SignalR` ở `UploadYoutubeBot`
- app mới `FastAPI control-plane + Python worker`

Trọng tâm là 4 câu hỏi vận hành:

- mất mạng/nghẽn mạng thì bot có tự nối lại không
- worker bị restart/crash thì có tự lên lại không
- đang render/upload dở mà restart thì có chạy tiếp không
- Telegram hiện có đang làm gì thật sự không

## Kết luận ngắn

- App cũ mạnh hơn ở `reconnect mềm` khi mạng chập chờn vì dùng `SignalR` với `WithAutomaticReconnect`.
- App mới mạnh hơn ở `tự bật lại sau crash/reboot VPS` vì chạy bằng `systemd Restart=always`.
- Cả hai hiện `không có resume thật` cho render đang chạy dở.
- App mới đặc biệt yếu ở pha `uploading`: nếu worker mất tracking hoặc restart giữa chừng thì job bị đẩy sang `error`, không tự upload tiếp.
- Telegram bot cũ hiện không cho thấy có cơ chế cảnh báo tự động đang hoạt động trong codebase đã audit.

## Bảng So Sánh

| Tình huống | App cũ | App mới | Ý nghĩa vận hành |
|---|---|---|---|
| Mất mạng ngắn, nghẽn mạng, internet chập chờn | Có `SignalR` auto reconnect, retry 3 giây/lần, vẫn giữ process sống nếu app chưa chết | Không có connection persistent; worker gọi HTTP polling, có thể văng process nếu request lỗi không được nuốt ở outer loop | App cũ mượt hơn khi mạng chỉ chập chờn ngắn |
| Worker/bot process crash | Nếu chỉ mở tay như desktop app thì thường không tự lên lại trừ khi có autorun/service ngoài | Có `systemd Restart=always`, tự bật lại sau 5 giây | App mới tốt hơn rõ cho production VPS |
| Reboot VPS / reboot máy | Phụ thuộc autorun ngoài app | Service có thể tự lên cùng hệ thống nếu đã `enable` | App mới phù hợp vận hành VPS hơn |
| Đang download mà bot restart | Không thấy cơ chế resume | Job được đưa lại `pending`, tải lại từ đầu | Mất thời gian nhưng còn tự hồi |
| Đang render mà bot restart | Không thấy resume | Job được đưa lại `pending`, render lại từ đầu | Không mất queue, nhưng mất tiến độ |
| Đang upload YouTube mà bot restart | Không thấy resume upload | Job bị chuyển `error`, không tự nối tiếp upload | Đây là rủi ro lớn nhất hiện tại |
| Theo dõi bot online/offline | Có `Connected/Disconnected` qua SignalR + `PingAsync` | Có `register_worker` + `heartbeat_worker` + `last_seen` | Cả hai đều biết bot còn sống hay không |
| Telegram cảnh báo | Không thấy luồng gửi Telegram tự động chạy thật trong repo đã audit | Chưa có Telegram alert | Hiện gần như chưa có monitoring Telegram thật |

## Telegram Audit

### Những gì đã xác nhận

- Bot Telegram hiện tại là `@ShineMediaBot`.
- Bot không có `webhook`.
- Bot không có `commands` được set.
- Bot không có `description`.
- Trong repo cũ có field lưu `LinkTelegram` và `TelegramAPI` cho user.
- Trong repo cũ có endpoint cập nhật thông tin Telegram cho user/admin.
- Có một đoạn gọi `SendTextMessageAsync(...)` nhưng đang bị comment, không phải luồng chạy thật.

### Suy ra thực tế

- Telegram trong app cũ có vẻ là `thông tin cấu hình/user metadata`, không phải một hệ thống alert production đang hoạt động rõ ràng trong code đã audit.
- Nếu trước đây có cảnh báo Telegram thật, nhiều khả năng logic đó nằm ở:
  - một repo khác
  - script deploy ngoài source hiện tại
  - môi trường cũ không còn nằm trong thư mục đã kiểm tra

## Hành Vi Hiện Tại Của App Mới

### Khi worker còn chạy nhưng mạng control-plane chập chờn

- Worker mới không có lớp reconnect riêng như SignalR.
- Nếu request HTTP tới control-plane lỗi và exception thoát khỏi vòng xử lý chính, process có thể chết.
- Khi process chết, `systemd` sẽ kéo nó lên lại.

### Khi worker bị restart/crash

- Nếu worker đang chạy qua `systemd`, thường không cần SSH vào bật tay.
- Nếu worker đang chạy thủ công trong phiên `ssh`, mất process là phải vào bật lại.

### Khi job đang chạy dở

| Pha | Hành vi hiện tại |
|---|---|
| `downloading` | reset về `pending`, chạy lại từ đầu |
| `rendering` | reset về `pending`, chạy lại từ đầu |
| `uploading` | chuyển `error`, không tự resume |

## Bảng Hardening Thực Dụng

### Mức Dễ

| Việc nên làm | Giải quyết gì | Chi phí | Ưu tiên |
|---|---|---|---|
| Bọc `heartbeat / claim / progress / complete` bằng retry ngắn với backoff | Giảm crash do lỗi mạng ngắn | Thấp | Rất cao |
| Bắt exception ở outer loop để worker không chết chỉ vì 1 request lỗi | Tránh restart không cần thiết | Thấp | Rất cao |
| Ghi log rõ `network error`, `control-plane unreachable`, `restart cause` | Dễ chẩn đoán bot lag hay chết | Thấp | Cao |
| Thêm health summary trên dashboard: `last heartbeat`, `last claim`, `last progress`, `last error` | Admin nhìn phát biết bot đang nghẽn hay chết | Thấp | Cao |
| Telegram/notification tối thiểu khi worker offline quá N giây | Có cảnh báo sớm thay vì nhìn dashboard thủ công | Thấp | Cao |

### Mức Vừa

| Việc nên làm | Giải quyết gì | Chi phí | Ưu tiên |
|---|---|---|---|
| Lưu `active_job_ids` thật trong heartbeat thay vì chỉ gửi rỗng | Control-plane phân biệt được job nào còn sống thật | Vừa | Rất cao |
| Lưu state tạm cho job render vào `job_dir/state.json` | Biết worker chết ở pha nào, có thể quyết định resume hay replay | Vừa | Cao |
| Giữ lại artifact render tạm khi job đang chạy, không dọn sớm | Tạo nền cho resume render | Vừa | Cao |
| Có job reconciler nền ở control-plane để phát hiện worker offline và phân loại `requeue` vs `error` tốt hơn | Tránh xử lý lệch giữa các pha | Vừa | Cao |
| Tạo Telegram alert service thật ở control-plane | Cảnh báo nhất quán, không phụ thuộc worker desktop/app riêng | Vừa | Cao |

### Mức Mạnh

| Việc nên làm | Giải quyết gì | Chi phí | Ưu tiên |
|---|---|---|---|
| Resume render từ artifact/checkpoint thay vì render lại từ đầu | Tiết kiệm nhiều thời gian khi restart giữa chừng | Cao | Trung bình |
| Tách upload thành state machine có `upload session token / browser recovery plan` | Giảm lỗi nặng ở pha upload | Cao | Cao |
| Watchdog riêng cho browser upload session | Phân biệt lỗi mạng control-plane với lỗi Chrome/Studio | Cao | Trung bình |
| Notification pipeline đa kênh: Telegram + dashboard notice + email/webhook | Monitoring production bài bản | Cao | Trung bình |
| Supervisor metrics/observability hoàn chỉnh | Root-cause nhanh khi worker lag hoặc mất kết nối | Cao | Trung bình |

## Thứ Tự Nên Làm

### Gói tối thiểu nên làm ngay

1. Retry + backoff cho HTTP worker client.
2. Không để worker chết chỉ vì một request control-plane lỗi.
3. Dashboard hiển thị rõ `last_seen`, `last_progress`, `last_error`.
4. Telegram alert thật cho `worker offline`, `job upload error`, `worker restart loop`.

### Gói nên làm tiếp theo

1. Gửi `active_job_ids` thật trong heartbeat.
2. Reconcile job theo heartbeat chính xác hơn.
3. Giữ state/artifact để render có thể replay thông minh hoặc resume từng phần.

### Gói đáng đầu tư nếu chạy production lâu dài

1. State machine upload rõ ràng.
2. Resume upload hoặc recovery flow bán tự động.
3. Observability đủ để phân biệt:
   - lỗi mạng
   - lỗi control-plane
   - lỗi ffmpeg/render
   - lỗi browser/YouTube Studio

## Khuyến Nghị Thực Tế

Nếu mục tiêu là `an toàn production nhanh nhất`, mốc hợp lý là:

- chưa cần resume render ngay
- nhưng bắt buộc phải làm:
  - retry network
  - worker không chết vô cớ
  - alert offline thật
  - phân biệt `requeue` và `error` tốt hơn ở pha upload

Nếu mục tiêu là `tiết kiệm thời gian máy và thao tác tay`, ưu tiên tiếp theo là:

- giữ artifact render
- thêm state file cho job
- chuẩn bị đường cho resume bán phần

## Canonical References

- App mới:
  - `workers/agent/main.py`
  - `workers/agent/control_plane.py`
  - `workers/agent/job_runner.py`
  - `backend/app/store.py`
  - `infra/systemd/youtube-upload-worker.service`
  - `infra/systemd/youtube-upload-web.service`
- App cũ:
  - `UploadYoutubeBot/Services/SignalrClient.cs`
  - `UploadYoutubeBot/UI/MainWindow.xaml.cs`
  - `UploadYoutubeBot/Works/MainWork.cs`
  - `BaseSource.Services/Services/Signalr/BotHub.cs`
  - `BaseSource.Services/Services/BOT/ManagerBOTService.cs`
