# User Workspace

## Responsibility
- Chua flow user dashboard: them kenh, browser session/noVNC, chon channel, tao render job, upload local asset, theo doi notice/toast.

## Entry Points
- Template: `backend/app/templates/user_dashboard.html`
- JS: `backend/app/static/js/user_dashboard.js`
- Data/context: `backend/app/web.py`, `backend/app/store.py`
- APIs: `backend/app/api_user.py`

## Key Files
- `backend/app/templates/user_dashboard.html`
- `backend/app/static/js/user_dashboard.js`
- `backend/app/api_user.py`
- `backend/app/store.py`

## Depends On
- `docs/UI_SYSTEM.md`
- Browser session APIs
- Upload session APIs
- Worker assignment data tu store

## Used By
- End-user flow tao kenh/job

## Invariants
- `+ Them Kenh` phai respect worker/VPS duoc chon/duoc gan.
- Upload local asset phai di qua upload session truoc khi job duoc tao.
- Notice/toast/search behavior phai dong bo voi pattern UI hien tai, khong quay lai `alert()` hoac notice co dinh.

## Known Pitfalls
- File picker local rat de bi browser cache/hidden-input behavior anh huong; can nho bump query string JS khi sua.
- Browser session va upload browser co the fail vi profile/session stale; can doi chieu worker runtime thay vi chi nhin UI.
- Khi doi layout form render, can giu nguyen nghiep vu slot upload/introduction neu schema/store van support.

## Related Decisions
- `DEC-002`
- `DEC-004`
- `DEC-005`
- `DEC-006`
