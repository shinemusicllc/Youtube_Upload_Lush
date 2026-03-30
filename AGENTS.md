## Working agreements

- Khi giao tiếp, walkthrough, task/checklist va huong dan trien khai: viet tieng Viet.
- Giu nguyen tieng Anh cho ten ham/bien, log loi, lenh terminal, config key va API field.
- Luon phan loai nhiem vu thanh `Quick Task` hoac `Project Task`.

## Rule Bootstrap

### Build / Test / Lint
- Backend local: `python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000`
- Frontend hien tai uu tien `server-rendered HTML` qua FastAPI templates; khong mac dinh React/Vite neu chua co ly do ro rang.

### Coding conventions
- UI task bat buoc theo huong `uncodixfy`: phang, it radius, it nested cards, uu tien border/divider ro rang.
- Backend uu tien FastAPI router mong, schema ro rang, khong nhot business logic vao route handler.
- Muc tieu hien tai la rebuild sach tu giao dien co san (`final_user_ui.html`) thay vi tiep tuc React cu.

### Module Boundaries
- `backend/`: FastAPI, templates, static assets, API routers, seed/store prototype.
- `frontend/`: chi giu lai neu can tai su dung asset/build tooling; khong xem la source chinh cua UI moi.
- `workers/`: worker agent Python, logic heartbeat/claim/render trong tuong lai; khong nhot vao `backend/`.
- `infra/`: Docker, reverse proxy, systemd va deploy artifact; khong dat business logic vao day.

### Debug Workflow
- Neu loi template/static: kiem tra `backend/app/templates`, `backend/app/static`, route web.
- Neu loi API/domain: kiem tra `backend/app/routers`, `backend/app/schemas`, `backend/app/store`.
- Neu loi template/static: uu tien doi chieu `backend/app/templates`, `backend/app/static`, va `final_user_ui.html`.

### Safety Rules
- Khong sua repo `.NET` cu khi chua co migration plan ro rang.
- Khong doi domain model lon neu chua cap nhat `docs/DECISIONS.md`.
- Worker phai chu dong `pull/heartbeat` ve control plane; khong dua repo ve huong desktop bot hay push-job qua UI event.

## Project Task

- Truoc moi task: doc `docs/PROJECT_CONTEXT.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`.
- Sau moi task: append vao `docs/WORKLOG.md` va `docs/CHANGELOG.md`.
- Khi co quyet dinh moi: append vao `docs/DECISIONS.md`.

