# UI System

## Visual Source Of Truth
- File chuẩn visual cho toàn bộ dự án là [final_user_ui.html](D:/Youtube_BOT_UPLOAD/final_user_ui.html).
- Áp dụng cho cả:
  - user workspace
  - admin workspace
- Reference SaaS user cung cấp sau đó chỉ là `secondary refinement reference` cho:
  - logo / wordmark
  - avatar block
  - nút `Đăng xuất`
  - nhịp shell chrome
  - độ sắc của typography/icon
- Reference này không thay thế `final_user_ui.html` làm source of truth.
- `YoutubeBOTUpload-master/BaseSource.AppUI` chỉ còn là nguồn tham chiếu:
  - workflow
  - route nghiệp vụ
  - thứ tự thao tác
  - tên màn / hành động
- Không dùng repo .NET cũ làm nguồn visual chính nữa.

## Product Character
- Đây là `light operational workspace`.
- Không phải landing page.
- Không phải dashboard KPI-card template.
- Không phải dark SaaS admin.
- Trọng tâm là:
  - thao tác nhanh
  - nhiều dữ liệu
  - hierarchy rõ
  - cùng một mặt phẳng vận hành giữa form, trạng thái và queue/list

## Core Layout
- Shell chuẩn:
  - sidebar trái cố định
  - top header mờ nhẹ
  - content chính cuộn độc lập
- Content chuẩn:
  - 1 dải KPI ngang
  - 1 vùng thao tác chính
  - 1 bảng/list lớn phía dưới
- Với admin:
  - giữ shell này
  - tăng mật độ dữ liệu
  - thay module thao tác theo nghiệp vụ admin
  - không đổi design system

## BOT Management
- Flow `Cấp phát BOT` đã được gộp vào `Danh sách BOT`.
- Screen canon cho admin/manager là `backend/app/templates/admin/worker_index.html`.
- Mọi thao tác owner BOT, chọn user và xóa BOT phải đi trực tiếp trên flow này thay vì mở thêm screen điều phối tách riêng.

## Palette
- Background app: `#f3f5f9`
- Surface: `#ffffff`
- Border chính:
  - `rgb(226 232 240)`
  - `rgb(203 213 225)`
- Brand:
  - `#6b74f0`
  - `#5d67df`
  - `#4b56c9`
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
- Meta / id / timeline / queue / code-like text: `IBM Plex Mono`
- Nếu tinh chỉnh shell theo reference SaaS, chỉ được phép mượn tinh thần brand/editorial của shell đó; không được đổi toàn bộ hệ font nếu chưa cập nhật lại `final_user_ui.html` chính thức.

## Icon System
- Dùng `Lucide` làm icon system mặc định.
- Icon nhỏ, nét mảnh, không có nền trang trí riêng.
- Không quay lại `Font Awesome` như hệ icon chính cho UI mới.

## Spacing
- Thang spacing ưu tiên:
  - `4`
  - `8`
  - `12`
  - `16`
  - `24`
- Input/control cao khoảng `42px`.
- Panel padding chuẩn:
  - `p-6`
  - `px-5`
  - `px-6`

## Radius And Shadow
- Radius control nhỏ: `6-10px`
- Radius panel chính: khoảng `16px`
- Shadow rất nhẹ:
  - chỉ để tách lớp
  - không glow
  - không shadow đậm kiểu template

## Primary Components

### 1. App Shell
- Sidebar nền sáng, border mảnh.
- Header mờ nhẹ kiểu `frosted-header`.
- Không dùng dark sidebar nếu user UI là chuẩn visual.
- Logo, avatar sidebar và nút `Đăng xuất` phải được polish lại để đạt chất SaaS hơn, nhưng vẫn phải bám layout và component rhythm của `final_user_ui.html`.

### 2. KPI Strip
- Pattern chuẩn là `một dải KPI ngang`, chia cột bằng divider.
- Mỗi KPI gồm:
  - label nhỏ
  - số lớn
  - status text nhỏ
  - vạch màu ngắn phía dưới
- Không quay về KPI grid dạng nhiều card rời.

### 3. Elevated Panel
- Panel chuẩn là `elevated-card`.
- Nền trắng, border nhạt, shadow nhẹ, radius vừa.
- Không lồng quá nhiều panel trong panel.

### 4. Toolbar / Filter
- Search và filter nằm ở:
  - section header
  - hoặc panel header
- Không tạo thêm card lọc riêng nếu không cần.

### 5. Custom Select
- Pattern select chuẩn:
  - avatar/icon
  - label chính
  - meta phụ
  - selected state rõ
- Admin nên tái dùng pattern này cho:
  - chọn manager
  - chọn worker
  - chọn channel

### 6. Data Table / Queue Table
- Bảng là thành phần trung tâm.
- Header nhỏ, sắc, rõ sort state.
- Row cần có hierarchy thông tin, không chỉ là text phẳng.
- Cột đầu nên ưu tiên:
  - preview
  - title
  - meta
  - id

### 7. Status Chip
- Chip nhỏ, semantic, border nhạt.
- Không dùng badge quá to hoặc quá nhiều màu cùng lúc.

### 8. Row Actions
- Nút action compact, semantic theo màu.
- Đặt ở cuối row.
- Không dùng toolbar tách rời vô nghĩa.

## Admin Adaptation Rules
- Admin phải cùng visual language với `final_user_ui.html`.
- Khác biệt chỉ được nằm ở:
  - mật độ dữ liệu
  - route nghiệp vụ
  - loại bảng và form
- Không được khác ở:
  - shell
  - font
  - icon system
  - panel language
  - KPI pattern
  - table language

## Absolute Do-Nots
- Không quay lại shell Stisla/Bootstrap cũ như một app khác.
- Không dùng dark sidebar + light content cho admin.
- Không dùng KPI card grid rời.
- Không thêm modal-first CRUD dày đặc nếu chưa có lý do rõ.
- Không pha thêm một design system mới cho admin.
- Không quay lại `Font Awesome` làm icon system chính.
- Không dùng badge lớn, bo tròn quá mức, shadow nặng, gradient trang trí.
- Không để user là workspace mới còn admin là trang quản trị kiểu cũ.

## Working Rule
- Khi thêm bất kỳ màn admin nào:
  1. đối chiếu flow từ app cũ
  2. đối chiếu visual từ `final_user_ui.html`
  3. chỉ triển khai khi giữ được cả hai

## Current Status
- User UI đã có nguồn visual rõ là `final_user_ui.html`.
- Admin UI hiện đang lệch visual source of truth và cần được refactor lại theo file này trước khi tiếp tục nối parity logic sâu.
- Runtime hiện tại không còn màn `Cấp phát BOT` độc lập; các URL cũ chỉ nên giữ vai trò redirect về `Danh sách BOT`.
- Một số chi tiết shell của `final_user_ui.html` hiện vẫn có thể được polish thêm theo reference SaaS user đã đưa, nhưng mọi chỉnh sửa đều phải được xem là refinement của source of truth chứ không phải nguồn mới.
