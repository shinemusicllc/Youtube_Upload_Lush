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
- OAuth Google hien moi o muc start URL + env contract; callback/token exchange chua noi that.
- Admin da co:
  - login/logout qua session cookie
  - role gate `admin`, `manager`
  - manager filter luu session
  - API/admin contract theo module
  - persistence local bang `backend/app/data/app_state.db`
- Data target van la `Postgres + Redis`, nhung hien tai local bootstrap dang dung SQLite snapshot de giu state qua restart.
