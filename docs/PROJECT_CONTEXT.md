# Project Context: YouTube Upload Tool

## Overview
Du an dang duoc rebuild lai theo huong `FastAPI + Python backend` va UI HTML/CSS co san, thay vi tiep tuc frontend React/Vite cu.

## Current Reset State
- Root workspace da bi don sach phan lon frontend/backend prototype cu.
- Hien co:
  - `YoutubeBOTUpload-master/` lam nguon tham chieu UI/domain tu app .NET cu.
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
- `YoutubeBOTUpload-master/BaseSource.AppUI` chi con la nguon tham chieu workflow, route, va nghiep vu admin/user cua app cu; khong con la nguon visual chinh.

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
- DNS public cho `ytb.jazzrelaxation.com` hien chua ton tai, nen HTTP redirect da san sang tren host nhung HTTPS/Let's Encrypt se chi hoat dong sau khi domain tro ve `82.197.71.6`.
- Admin da co:
  - login/logout qua session cookie
  - role gate `admin`, `manager`
  - manager filter luu session
  - API/admin contract theo module
  - persistence local bang `backend/app/data/app_state.db`
- Data target van la `Postgres + Redis`, nhung hien tai local bootstrap dang dung SQLite snapshot de giu state qua restart.
