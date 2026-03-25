# Backend AGENTS

## Pham vi
- `backend/app/` la khu vuc FastAPI/Pydantic moi.
- `backend/app/templates/` va `backend/app/static/` la source of truth cho HTML/CSS/JS mode moi.

## Build / Test / Lint
- Kiem tra syntax: `python -m compileall backend/app`
- Khi da co test: `pytest`

## Coding conventions
- Route handler chi lam vai tro thin adapter, khong nhot business logic.
- Schema phai JSON-friendly, uu tien `BaseModel` ro rang, field name on dinh.
- Store tam thoi dung in-memory, khong phu thuoc DB hay template.
- Template HTML uu tien giu layout da chot, chi thay data cung bang Jinja va JS mong.

## Safety rules
- Khong doi contract field lon neu chua co decision moi.
- Khong day logic sang UI layer.
- Neu can thay doi seed data, giu payload ngan gon va doc duoc ngay.
- Khi doi route web/template, phai kiem tra lai `/`, `/app`, `/admin`, `/api/health`.
