# Decisions Index

| ID | Decision | Status | Scope | Impact |
| --- | --- | --- | --- | --- |
| DEC-001 | Core architecture giu `FastAPI control plane + Python worker`; local bootstrap dung SQLite, data target ve sau la Postgres + Redis | Active | backend + workers | High |
| DEC-002 | `final_user_ui.html` la visual source of truth cho user/admin; `docs/UI_SYSTEM.md` mo ta design system hien tai | Active | UI system | High |
| DEC-003 | Worker la outbound agent theo contract `register + heartbeat + claim + progress + complete/fail` | Active | worker runtime | High |
| DEC-004 | Browser session onboarding va browser upload phai chay tren worker/VPS duoc gan, khong chay tren control plane | Active | worker/browser | High |
| DEC-005 | User co the duoc gan nhieu VPS; channel/browser session/render job phai bam theo worker so huu cua no | Active | user/admin assignment | High |
| DEC-006 | Local upload file lon phai qua `upload session + resumable chunk upload` truoc khi tao job | Active | upload flow | High |
| DEC-007 | Memory bootstrap moi dung `PROJECT_BRIEF + MEMORY_INDEX + DECISIONS_INDEX`; `PROJECT_CONTEXT + DECISIONS + WORKLOG` giu lai cho lich su/tuong thich nguoc | Active | docs/workflow | High |
| DEC-008 | Man `Cap phat BOT` la UI exception theo split-dispatch workspace, nhung van phai giu cung design system chung | Active | admin UI | Medium |
| DEC-009 | Browser upload phai giu progress/complete theo dialog telemetry, nhung visibility contract phai ho tro day du `draft/private/unlisted/public` giong app cu | Active | worker/browser upload | High |
| DEC-010 | `admin` va `manager` duoc vao chung workspace `Điều phối Render` qua `/app`; manager dung kho VPS cua minh, admin dung VPS tu tu cap phat cho chinh tai khoan admin | Active | admin/user workspace | High |
| DEC-011 | Một worker/VPS có thể được gán cho nhiều user; cleanup dữ liệu phải scoped theo `user_id + worker_id`, không xóa kiểu toàn worker khi chỉ gỡ một user hoặc đổi tên BOT | Active | admin assignment + channel data | High |
| DEC-012 | Worker cleanup theo 3 lớp: per-job cleanup, browser-session/profile cleanup, và janitor startup/periodic cho artifact stale | Active | worker runtime | High |

| DEC-013 | Scheduler moi worker giu `1 active job` va claim queue theo round-robin giua cac user tren cung worker; worker chi claim job tiep theo sau khi `run_job()` return, tuc sau cleanup local cua job truoc | Active | worker scheduling + disk safety | High |
| DEC-014 | Worker resilience dung retry/backoff cho HTTP, heartbeat background de tu reconnect sau mat mang/restart, Telegram chi alert khi worker offline qua 180s, va job `uploading` chi `requeue` khi mat ket noi luc upload moi bat dau | Active | worker runtime + control-plane ops | High |
| DEC-015 | Job dang `rendering/uploading` chi duoc chuyen trang thai sau `lease/grace window`; heartbeat hut ngan khong duoc lap tuc `pending/error` | Active | worker runtime + control-plane ops | High |
| DEC-016 | Them worker/BOT moi se di qua mot duong SSH bootstrap duy nhat tren control-plane; UI admin va CLI chi la hai mat goi chung mot helper, khong bootstrap qua Telegram | Active | admin ops + deploy | High |
| DEC-017 | `Xoa BOT` phai la decommission that tren VPS va `Them BOT` phai hien row provisioning live ngay trong Danh sach BOT | Active | admin ops + BOT UI | High |
| DEC-018 | Bootstrap/decommission worker phai chiu duoc Windows line endings va viec tai tao worker tren cung VPS: script upload sang Linux phai duoc normalize LF, venv phai tao o runtime dir, failed install row khong duoc giu slot `worker-XX`, va requirement worker phai du de boot tren may trang | Active | worker bootstrap + admin ops | High |
| DEC-019 | Worker browser/upload live se tam thoi bam sat flow on dinh gan `012e614`: worker service chay duoi `root`, browser canonical la `chromium-browser`/`chromium`, va chi giu lai cleanup stale `Xvfb` + decommission cleanup de tranh state cu sot lai | Superseded | worker runtime + browser profile | High |
| DEC-020 | `admin` va `manager` duoc xem nhu account workspace rieng tren cung VPS, nhung `ChannelRecord` van global theo `channel_id` nen `confirm_browser_session` phai chan viec link them mot kenh da thuoc account khac | Active | admin workspace + shared VPS isolation | High |
| DEC-021 | Neu worker phai dung snap-backed `chromium-browser`, runtime phai override `SNAP_USER_COMMON`, `SNAP_USER_DATA`, `SNAP_REAL_HOME` va `XDG_*` theo tung `browser_profile_path`; bootstrap BOT moi van uu tien browser non-snap, nhung login va upload phai dung cung mot env builder de profile isolation hoat dong ca voi snap | Active | worker runtime + browser profile isolation | High |
| DEC-022 | Production worker browser canonical chuyen sang native `google-chrome-stable`; login noVNC va upload phai dung chung `profile_path + _build_browser_env()` voi `HOME`, `DBUS`, `XDG_*`, `password-store=basic`, shutdown graceful, va khong pin `chromedriver` co dinh trong bootstrap | Active | worker runtime + browser profile | High |

## Notes
- `docs/DECISIONS.md` van giu full history va ly do chi tiet.
- `docs/modules/*.md` nen reference `DEC-xxx` thay vi copy lai noi dung decision.
- Neu co conflict giua docs cu va workflow moi, uu tien `PROJECT_BRIEF + MEMORY_INDEX + DECISIONS_INDEX`, sau do ghi ro vao `WORKLOG`.
