# Admin Parity Checklist

## Mục tiêu
- Giữ tối đa luồng quản trị của app cũ trong `YoutubeBOTUpload-master/BaseSource.AppUI`.
- Tách rõ `đã có UI shell`, `đã có route`, `đã có logic CRUD`, `đã có parity đầy đủ`.
- Dùng file này làm checklist triển khai backend/admin theo thứ tự ưu tiên.

## Trạng thái tổng quan hiện tại
- Đã có:
  - shell admin FastAPI/Jinja
  - 4 màn chính: `User`, `BOT`, `Channel`, `Render`
  - static asset cũ: `admin-themes`, `css`, `js`
  - admin auth/session thật
  - persistence local bằng SQLite snapshot
- Chưa có:
  - auth người dùng cuối thật ngoài admin shell
  - Postgres + Redis production persistence

## Quy ước trạng thái
- `DONE`: Đã có giao diện và logic gần tương đương app cũ
- `PARTIAL`: Có shell hoặc route list nhưng chưa có thao tác đầy đủ
- `TODO`: Chưa làm

---

## 1. User Management

### 1.1 Danh sách người dùng
- App cũ:
  - `GET /admin/user/index`
  - manager filter
  - KPI strip
  - bảng user
  - action: `Kênh`, `BOT`, `Delete`, `ResetPassword`, `Edit`
- FastAPI hiện tại:
  - có route page `/admin/user/index`
  - có manager filter, KPI strip, bảng user
  - action `Kênh`, `BOT`, `Delete`, `ResetPassword`, `Edit` đã nối
- Trạng thái: `DONE`

### 1.2 Tạo user
- App cũ:
  - `GET /admin/user/create`
  - `POST /admin/user/create`
  - manager binding theo role
- FastAPI hiện tại:
  - có route `GET /admin/user/create`
  - có route `POST /admin/user/create`
  - form tạo user đã nối logic
- Trạng thái: `DONE`

### 1.3 Xóa user
- App cũ:
  - `POST /admin/user/delete`
- FastAPI hiện tại:
  - có route `POST /admin/user/delete`
  - có confirm flow từ danh sách user
- Trạng thái: `DONE`

### 1.4 Reset password
- App cũ:
  - `POST /admin/user/resetpassword`
- FastAPI hiện tại:
  - có route `POST /admin/user/resetpassword`
  - có page/form reset password
- Trạng thái: `DONE`

### 1.5 Edit user / gán manager
- App cũ:
  - `POST /admin/user/updatetelegram`
  - modal edit manager
- FastAPI hiện tại:
  - có route `POST /admin/user/updatetelegram`
  - có page edit user và gán manager
- Trạng thái: `DONE`

### 1.6 Danh sách manager
- App cũ:
  - `GET /admin/user/manager`
  - `POST /admin/user/updaterolemanager`
- FastAPI hiện tại:
  - có page riêng `GET /admin/user/manager`
  - có route `POST /admin/user/updaterolemanager`
- Trạng thái: `DONE`

### 1.7 Danh sách admin
- App cũ:
  - `GET /admin/user/admins`
  - `POST /admin/user/updateroleadmin`
- FastAPI hiện tại:
  - có page riêng `GET /admin/user/admins`
  - có route `POST /admin/user/updateroleadmin`
- Trạng thái: `DONE`

### 1.8 Gán BOT cho user
- App cũ:
  - `GET /admin/user/managerbot`
  - `POST /admin/user/addbot`
  - `POST /admin/user/deletebot`
  - `POST /admin/user/updatebotuser`
- FastAPI hiện tại:
  - có flow user-BOT mapping riêng
  - có các route `addbot`, `deletebot`, `updatebotuser`
  - page mapping BOT đã nối logic
- Trạng thái: `DONE`

---

## 2. BOT Management

### 2.1 Danh sách BOT
- App cũ:
  - `GET /admin/managerbot/index`
  - manager filter
  - KPI strip
  - action: `DS Kênh`, `DS User`, `Sửa`, `Xóa`, `Luồng`
- FastAPI hiện tại:
  - có route `/admin/ManagerBOT/index` và alias `/admin/managerbot/index`
  - có manager filter, KPI strip, bảng BOT
  - action `DS Kênh`, `DS User`, `Sửa`, `Xóa`, `Luồng` đã nối
- Trạng thái: `DONE`

### 2.2 Update BOT
- App cũ:
  - `POST /admin/bot/update`
- FastAPI hiện tại:
  - có route `POST /admin/bot/update`
  - có dialog cập nhật BOT
- Trạng thái: `DONE`

### 2.3 Delete BOT
- App cũ:
  - `POST /admin/managerbot/delete`
- FastAPI hiện tại:
  - có route `POST /admin/managerbot/delete`
  - có dialog xóa BOT
- Trạng thái: `DONE`

### 2.4 Update thread BOT
- App cũ:
  - `POST /admin/bot/updatethread`
- FastAPI hiện tại:
  - có route `POST /admin/bot/updatethread`
  - có alias `POST /admin/bot/updateThread`
  - có dialog cập nhật luồng BOT
- Trạng thái: `DONE`

### 2.5 Danh sách BOT của user
- App cũ:
  - `GET /admin/bot/user`
- FastAPI hiện tại:
  - có page riêng `GET /admin/bot/user`
  - liệt kê BOT gán cho user và liên kết ngược về flow mapping
- Trạng thái: `DONE`

### 2.6 Danh sách user của BOT
- App cũ:
  - `GET /admin/bot/userofbot`
- FastAPI hiện tại:
  - có page riêng `GET /admin/bot/userofbot`
  - liệt kê user đang gán với BOT theo mapping hiện tại
- Trạng thái: `DONE`

---

## 3. Channel Management

### 3.1 Danh sách channel
- App cũ:
  - `GET /admin/channel/index`
  - filter manager
  - KPI strip
  - action: `DS User`, `DS Render`, `Cập nhật`, `Xóa`, `Export`
- FastAPI hiện tại:
  - có route page `/admin/channel/index`
  - có manager filter, KPI strip, bảng channel
  - action `DS User`, `DS Render`, `Cập nhật`, `Xóa`, `Export` đã nối
- Trạng thái: `DONE`

### 3.2 Channel theo user
- App cũ:
  - `GET /admin/channel/user`
- FastAPI hiện tại:
  - có page riêng `GET /admin/channel/user`
  - cho phép bật hoặc thu hồi quyền kênh của user
- Trạng thái: `DONE`

### 3.3 Channel theo BOT
- App cũ:
  - `GET /admin/channel/bot`
- FastAPI hiện tại:
  - có route `GET /admin/channel/bot`
  - đã có filter/list và các action `DS User`, `DS Render`, `Cập nhật`, `Xóa`
- Trạng thái: `DONE`

### 3.4 User của channel
- App cũ:
  - `GET /admin/channel/users`
- FastAPI hiện tại:
  - có page riêng `GET /admin/channel/users`
  - có danh sách user của channel và liên kết chéo về user/BOT
- Trạng thái: `DONE`

### 3.5 Update user-channel
- App cũ:
  - `POST /admin/channel/updateuserchannel`
  - `POST /admin/channel/adduser`
- FastAPI hiện tại:
  - có route `POST /admin/channel/updateuserchannel`
  - có route `POST /admin/channel/adduser`
  - đã nối flow add/remove user-channel
- Trạng thái: `DONE`

### 3.6 Update profile channel
- App cũ:
  - `POST /admin/channel/updateprofile`
- FastAPI hiện tại:
  - có route `POST /admin/channel/updateprofile`
  - action cập nhật profile đã nối từ danh sách channel và các trang phụ
- Trạng thái: `DONE`

### 3.7 Export channel
- App cũ:
  - `GET /admin/channel/export`
- FastAPI hiện tại:
  - có route `GET /admin/channel/export`
  - trả file CSV báo cáo channel
- Trạng thái: `DONE`

### 3.8 Delete channel
- App cũ:
  - `GET /admin/channel/delete`
  - `GET /admin/channel/deleteajax`
- FastAPI hiện tại:
  - có route `GET /admin/channel/delete`
  - có route `GET/POST /admin/channel/deleteajax`
- Trạng thái: `DONE`

---

## 4. Render Management

### 4.1 Danh sách render
- App cũ:
  - `GET /admin/render/index`
  - manager filter
  - KPI strip
  - table render đầy đủ timeline
  - badge setting `xóa lần cuối`
- FastAPI hiện tại:
  - có route page `/admin/render/index`
  - có manager filter, KPI strip, bảng render đầy đủ timeline
  - badge `xóa lần cuối` đã nối dữ liệu thật
- Trạng thái: `DONE`

### 4.2 Render theo channel
- App cũ:
  - `GET /admin/render/channel`
- FastAPI hiện tại:
  - có route `GET /admin/render/channel`
  - dùng chung bảng render và action đầy đủ trong ngữ cảnh lọc theo kênh
- Trạng thái: `DONE`

### 4.3 Render detail
- App cũ:
  - `GET /admin/render/renderinfo`
- FastAPI hiện tại:
  - có route `GET /admin/render/renderinfo`
  - màn detail readonly bám đúng flow cấu hình render của app cũ
- Trạng thái: `DONE`

### 4.4 Delete all render
- App cũ:
  - `POST /admin/render/delete`
- FastAPI hiện tại:
  - có route `POST /admin/render/delete`
  - đã nối hành vi xóa toàn bộ render và cập nhật badge `xóa lần cuối`
- Trạng thái: `DONE`

---

## 5. Shared Admin Infrastructure

### 5.1 Auth / role enforcement
- App cũ:
  - controller có role gate `Admin`, `Manager`
- FastAPI hiện tại:
  - có login/logout admin thật qua session cookie
  - route web/API đã gate theo role `admin`, `manager`
  - page role `Manager`, `Admin` đã khóa `admin-only`
- Trạng thái: `DONE`

### 5.2 Manager filter session
- App cũ:
  - dùng `HttpContext.Session["Manangers"]`
  - layout có ajax `/admin/UpdateSession`
- FastAPI hiện tại:
  - manager filter đã lưu session thật
  - có route `POST /admin/UpdateSession`
  - các màn admin đọc lại filter từ session khi quay lại
- Trạng thái: `DONE`

### 5.3 API/admin contract
- App cũ:
  - nhiều controller/action theo từng module
- FastAPI hiện tại:
  - đã mở rộng contract theo module:
    - session / manager filter
    - users / roles / user-bot mapping
    - bots
    - channels
    - renders
- Trạng thái: `DONE`

### 5.4 Persistence
- App cũ:
  - DB/service thật
- FastAPI hiện tại:
  - state đã persist xuống `SQLite` local dưới dạng JSON snapshot
  - mutation admin/user/job không còn mất sau restart
- Trạng thái: `DONE`

---

## Mức độ parity hiện tại
- `UI shell parity`: khoảng 85%
- `list page parity`: khoảng 90%
- `admin action parity`: khoảng 85%
- `workflow parity tổng thể`: đã đạt mức dùng thay app cũ cho local bootstrap/admin prototype

## Thứ tự triển khai khuyến nghị tiếp theo
1. User auth thật ngoài admin shell
2. Google OAuth callback + token persistence
3. Worker/BOT registration + heartbeat thật
4. Chuyển persistence bridge từ SQLite snapshot sang Postgres + Redis

## Definition of Done cho admin parity
- Mỗi route quan trọng của app cũ có route tương ứng trong FastAPI
- Mỗi nút action chính không còn là `#` hay stub
- Modal/form submit vào backend thật
- Filter manager hoạt động đúng theo session/role
- Có đủ page liên kết chéo:
  - user -> BOT/channel
  - BOT -> user/channel
  - channel -> user/render
  - render -> detail
- Dữ liệu admin không còn phụ thuộc hoàn toàn vào seed in-memory
