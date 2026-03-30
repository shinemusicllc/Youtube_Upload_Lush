# Project Context: YouTube Upload Tool

## Overview
Du an dang duoc rebuild lai theo huong `FastAPI + Python backend` va UI HTML/CSS co san, thay vi tiep tuc frontend React/Vite cu.

## Current Reset State
- Root workspace da bi don sach phan lon frontend/backend prototype cu.
- Hien co:
  - `final_user_ui.html` la mockup user UI moi can noi vao backend.
  - `backend/` da co scaffold FastAPI toi thieu cho web route + template user page.
  - `frontend/` gan nhu khong con source app, chu yeu con `node_modules`.

## Target Architecture
- Backend: `FastAPI + Python`
- Worker: `Python worker + FFmpeg`
- Data target: `Postgres + Redis`
- Deploy target: `Docker Compose` tren `1 control VPS + nhieu worker VPS`
- OAuth: Google / YouTube OAuth cho connect channel.

## Product Flows
- Admin: quan ly manager, user, worker VPS/BOT, channel, render job.
- User: connect YouTube, tao render job, queue render, theo doi upload.

## UI Sources
- `final_user_ui.html` la visual source of truth cho ca user va admin UI moi.
- Luong nghiep vu admin/user da duoc chot lai ngay trong `backend/` va bo docs hien tai; khong con phu thuoc repo .NET cu trong workspace.

## Current Backend State
- `backend/app/templates/user_dashboard.html` la template user duy nhat dang duoc render boi FastAPI.
- `backend/app/static/js/user_dashboard.js` xu ly channel select, submit job, OAuth start, cancel/delete job tren HTML shell.
- Admin da duoc doi tu trang bootstrap tam sang shell Elevated SaaS Jinja voi cac route:
  - `/admin/user/index`
  - `/admin/ManagerBOT/index`
  - `/admin/channel/index`
  - `/admin/render/index`
- `/admin` redirect ve `/admin/user/index`.
- `/`, `/app`, `/admin`, `/api/health` da tra duoc response local.
- OAuth Google da co flow that: start URL, validate `state`, callback, `code -> token`, lay `userinfo + channels.list(mine=true)` va cap nhat kenh vao SQLite bootstrap.
- Local upload da duoc nang cap len huong `resumable chunk upload`: backend co upload session API, frontend upload chunk truoc roi moi tao job, va fallback direct upload da doi sang stream-to-disk.
- Da co worker control scaffold toi thieu: `POST /api/workers/register`, `POST /api/workers/heartbeat`, `POST /api/workers/claim`, `POST /api/workers/jobs/{job_id}/progress|complete|fail`, `workers/agent/main.py`, va bo infra `Dockerfile / docker-compose / Caddyfile / systemd`.
- Host thu nghiem dang chay tai `http://82.197.71.6:8000`; 2 worker da heartbeat thanh cong ve control plane. `simulate job processing` hien dang tat mac dinh tren worker env.
- Host shared da duoc gan route domain phia server cho `ytb.jazzrelaxation.com` thong qua Caddy chung cua may, reverse proxy ve app `172.17.0.1:8000`, va `.env` cua app da doi `APP_BASE_URL / APP_DOMAIN / GOOGLE_REDIRECT_URI` sang domain moi.
- Host web app tren shared VPS hien da duoc quan ly bang `systemd` service `youtube-upload-web.service`, bind `0.0.0.0:8000` de Caddy container reverse proxy vao on dinh.
- Da bo sung public pages phuc vu Google OAuth brand verification:
  - `/home` la homepage public
  - `/privacy-policy` la trang privacy public
  - `/terms-of-service` la trang terms public
- `ytb.jazzrelaxation.com` da tro DNS ve `82.197.71.6` va Caddy da xin cert Let's Encrypt thanh cong; app dang len that qua HTTPS.
- Backend da co worker-authenticated asset route `GET /api/workers/jobs/{job_id}/assets/{slot}` de worker tai local upload qua control plane.
- Worker Python da duoc tach module thanh `config / control_plane / downloader / ffmpeg_pipeline / job_runner`; co the download local asset, download Google Drive/HTTP, va chay FFmpeg fast-path `copy/remux`.
- Code moi da duoc deploy len host va 2 worker VPS, nhung worker execution hien dang duoc khoa bang `WORKER_EXECUTE_JOBS=false` de tranh an nham queue demo truoc khi bat render that.
- `worker-01` da duoc bat `WORKER_EXECUTE_JOBS=true` sau khi don queue demo cho rieng worker nay; service dang `active`, heartbeat on dinh, va hien khong co active job nao cho `worker-01`.
- `worker-02` van giu `WORKER_EXECUTE_JOBS=false` lam worker fallback cho den khi test xong luong render that tren `worker-01`.
- Da sua bug Google Drive downloader tren worker: cac asset co link `/file/d/.../view` gio duoc tai vao thu muc rieng theo `slot`, tranh bi ghi de nhau khi `video_loop` va `audio_loop` cung co ten file tam mac dinh la `view`.
- `worker-01` da xu ly thanh cong mot job Drive that `job-40a682dd` voi 1 link video + 1 link audio Google Drive, output 60 giay tai `/opt/youtube-upload-lush/worker-data/outputs/job-40a682dd-Worker01-Drive-Real-Links-Retry-20260326.mp4`.
- Control plane da co route worker-authenticated de worker lay YouTube OAuth upload target theo job/channel; worker da co module upload YouTube bang `refresh token -> resumable upload API`.
- Rollout YouTube upload da duoc mo khoa rieng cho `worker-01`; `worker-02` van giu `WORKER_UPLOAD_TO_YOUTUBE=false` de standby. Host/control plane da co `GOOGLE_CLIENT_ID/SECRET` hop le va channel test da co refresh token that.
- Sau khi deploy code upload YouTube, da verify lai luong render khong regression bang job `job-e667631b`; sau do da rollout upload that tren `worker-01` va upload thanh cong job `job-777d9f0a` len YouTube.
- User dashboard da duoc tach view-state cho job: `completed` khong con hien chung la `Hoan tat`, ma phan biet ro `Render hoan tat` va `Da upload YouTube` dua tren `output_url` + moc thoi gian upload; timeline hien rieng `Render` va `Upload`.
- User dashboard da co live endpoint `GET /api/user/dashboard/live`; frontend poll 5 giay/lần de cap nhat KPI, tab count va render queue realtime ma khong can refresh trang.
- Admin da co:
  - login/logout qua session cookie
  - role gate `admin`, `manager`
  - manager filter luu session
  - API/admin contract theo module
  - persistence local bang `backend/app/data/app_state.db`
- Data target van la `Postgres + Redis`, nhung hien tai local bootstrap dang dung SQLite snapshot de giu state qua restart.

