# UI System

## Visual Source Of Truth
- File visual canon cho user/admin shell là `final_user_ui.html`.
- `backend/app/templates/admin/*` phải bám design language của file này, chỉ tinh chỉnh theo nhu cầu admin chứ không tách ra một design system riêng.
- `YoutubeBOTUpload-master/BaseSource.AppUI` chỉ còn là nguồn tham chiếu workflow, thứ tự thao tác, và tên màn hình cũ; không dùng làm nguồn visual chính.

## Product Character
- Đây là `light operational workspace`, không phải landing page và không phải dark SaaS admin template.
- Trọng tâm là thao tác nhanh, mật độ dữ liệu cao, hierarchy rõ, và một mặt phẳng vận hành liền mạch giữa form, trạng thái, và list/table.
- Ưu tiên giao diện “bình thường nhưng chắc tay”: cấu trúc rõ, panel gọn, badge nhỏ, ít hiệu ứng, không phô diễn.

## Shell Layout
- Sidebar trái cố định, nền sáng, border mảnh.
- Header trên cùng nhẹ, dùng pattern `frosted-header`.
- Main content cuộn độc lập.
- Rhythm chuẩn của trang admin:
  - summary strip
  - panel thao tác chính
  - bảng/list lớn phía dưới

## BOT Management
- Screen canon cho admin/manager là `backend/app/templates/admin/worker_index.html`.
- Flow `Cấp phát BOT` đã được gộp vào `Danh sách BOT`.
- Upload, live, và backup phải được quản trị trong cùng một mặt bảng, không mở lại screen điều phối BOT tách riêng.
- Workspace tabs cũ không còn là pattern của màn BOT gộp; route này đi thẳng vào shell + content của trang BOT.

## Palette
- Background app: `#f3f5f9`
- Surface: `#ffffff`
- Border chính: `rgb(226 232 240)`, `rgb(203 213 225)`
- Brand: `#6b74f0`, `#5d67df`, `#4b56c9`
- Semantic:
  - success/connected: emerald
  - waiting/queue: amber
  - upload/info: sky
  - destructive/error: rose
- Text:
  - heading: slate-900
  - body: slate-700/800
  - meta: slate-500/600

## Typography
- Display / section title: `Be Vietnam Pro`
- Body / control / table: `Inter`
- Meta / id / queue / code-like text: `IBM Plex Mono`
- Không đổi bộ font admin sang một hệ khác nếu chưa có decision mới.

## Spacing And Surface
- Thang spacing ưu tiên: `4`, `8`, `12`, `16`, `24`
- Input/control cao khoảng `42px`
- Panel padding chuẩn: `p-6`, `px-5`, `px-6`
- Radius:
  - control nhỏ: `6-10px`
  - panel chính: khoảng `16px`
- Shadow rất nhẹ, chỉ để tách lớp; không glow, không shadow nặng.

## Core Components

### 1. Summary Strip
- Một dải KPI ngang, không quay về grid card rời.
- Mỗi item gồm label nhỏ, value lớn, accent/status ngắn, và vạch màu ngắn phía dưới.

### 2. Elevated Panel
- Panel trắng, border nhạt, shadow nhẹ, radius vừa.
- Tránh lồng nhiều panel trong panel nếu không thật sự cần.

### 3. Toolbar And Filter
- Search/filter đặt ở section header hoặc panel header.
- Không tạo card lọc riêng chỉ để “cho có”.

### 4. Custom Select
- Select nên có label chính + meta phụ + selected state rõ.
- Admin ưu tiên tái dùng pattern này cho manager, worker, channel, và các picker gán scope.

### 5. Data Table
- Table là trung tâm của admin workspace.
- Header nhỏ, sắc, rõ trạng thái sort.
- Row phải có hierarchy thông tin, không chỉ là text phẳng.
- Các cột đầu nên ưu tiên preview/title/meta/id.

### 6. Status Chip And Actions
- Status chip nhỏ, semantic, border nhẹ.
- Row action compact, semantic theo màu, đặt ở cuối hàng.
- Không dùng badge to, pill quá tròn, hoặc action bar tách rời vô nghĩa.

## Admin Adaptation Rules
- Admin phải cùng visual language với user shell.
- Khác biệt được phép nằm ở:
  - mật độ dữ liệu
  - route nghiệp vụ
  - loại bảng và form
- Không khác ở:
  - shell
  - font
  - icon system
  - panel language
  - summary/KPI pattern
  - table language

## Absolute Do-Nots
- Không quay lại shell Stisla/Bootstrap cũ.
- Không dùng dark sidebar + light content cho admin.
- Không quay lại KPI card grid rời.
- Không thêm hero/dashboard filler trong workspace nội bộ.
- Không dùng `Font Awesome` làm icon system chính cho UI mới.
- Không tạo thêm design system riêng cho admin.
- Không tách BOT assignment thành một screen CRUD khác nếu chưa có decision mới.

## Working Rule
- Khi thêm hoặc sửa màn admin:
  1. Đối chiếu workflow từ app cũ nếu cần hiểu nghiệp vụ.
  2. Đối chiếu visual với `final_user_ui.html`.
  3. Chỉ triển khai khi vẫn giữ được cả workflow đúng lẫn design language đúng.

## Current Status
- User shell đã có visual source of truth rõ ràng.
- Admin BOT flow hiện lấy `worker_index.html` làm màn canon cho BOT gộp.
- Nếu có thay đổi thiết kế lớn hoặc tách khỏi các rule trên, phải cập nhật cả decision docs và file này.
