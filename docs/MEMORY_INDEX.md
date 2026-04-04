# Memory Index

## Always Read For Project Task
- `AGENTS.md`
- `docs/PROJECT_BRIEF.md`
- `docs/MEMORY_INDEX.md`

## Read By Task Type

### Backend or API change
- `backend/AGENTS.md`
- `docs/modules/backend-app.md`
- `docs/DECISIONS_INDEX.md` neu dung contract, auth, store/schema, upload session, worker API

### User workspace or user flow UI
- `backend/AGENTS.md`
- `docs/UI_SYSTEM.md`
- `docs/modules/user-workspace.md`
- `docs/DECISIONS_INDEX.md` neu dung worker binding, upload flow, channel onboarding

### Admin workspace or admin flow UI
- `backend/AGENTS.md`
- `docs/UI_SYSTEM.md`
- `docs/modules/admin-workspace.md`
- `docs/DECISIONS_INDEX.md` neu dung assignment semantics, role gate, notice/search pattern

### Worker / browser / render / upload runtime
- `workers/AGENTS.md`
- `docs/modules/worker-control-plane.md`
- `docs/DECISIONS_INDEX.md`

### Deploy / infra / production sync
- `infra/AGENTS.md`
- `docs/modules/infra-runtime.md`
- `docs/DECISIONS_INDEX.md`

### Historical regression or "tai sao truoc day lam vay"
- Search trong `docs/DECISIONS.md` theo tu khoa module/feature
- Search trong `docs/WORKLOG.md` theo ngay, task title, file, issue
- Khong doc full hai file nay mac dinh

## Module Map
- `backend/app/main.py`, `backend/app/web.py`, `backend/app/api_*.py`, `backend/app/auth.py`, `backend/app/store.py`, `backend/app/schemas.py` -> `docs/modules/backend-app.md`
- `backend/app/templates/user_dashboard.html`, `backend/app/static/js/user_dashboard.js` -> `docs/modules/user-workspace.md`
- `backend/app/templates/admin/*`, `backend/app/static/js/admin_tables.js` -> `docs/modules/admin-workspace.md`
- `workers/agent/*` -> `docs/modules/worker-control-plane.md`
- `infra/docker/*`, `infra/caddy/*`, `infra/systemd/*`, `scripts/*` -> `docs/modules/infra-runtime.md`

## Retrieval First
- Graph repo name cho project nay la `youtube-bot-upload`.
- Neu repo task lon hoac khong ro entry point, uu tien:
  - `cgraph info --repo youtube-bot-upload`
  - `cgraph search <symbol> --repo youtube-bot-upload`
  - `cgraph neighbors ...`
  - `cgraph paths ...`
- Sau do moi mo code va docs lien quan.
- Chi re-index khi co thay doi cau truc lon, them module moi, hoac graph ro rang da stale.

## Legacy Compatibility
- `docs/PROJECT_CONTEXT.md` la extended context cua project.
- `docs/DECISIONS.md` la ledger day du.
- `docs/WORKLOG.md` la lich su task chi tiet.
- `docs/CHANGELOG.md` la tong hop thay doi.
- Bon file nay van duoc cap nhat, nhung khong con la bootstrap mac dinh.
