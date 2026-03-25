# Worklog

### 2026-03-25
- [x] Khoi tao lai `docs/` va root `AGENTS.md` sau khi workspace bi don sach.
- [x] Xac nhan huong moi: bo React/Vite cu, rebuild UI theo `BaseSource.AppUI` va `final_user_ui.html`.
- [x] Scaffold `backend/app/routers/web.py` va `backend/app/templates/user_dashboard.html` de render user page bang FastAPI/Jinja.
- [x] Scaffold backend seed/data contract toi thieu cho `user`, `worker`, `channel`, `channel grant`, `render job`, `oauth summary` bang FastAPI/Pydantic in-memory store.
- [x] Tao `backend/AGENTS.md` de chot rule rieng cho khu vuc backend.
- [x] Xoa `frontend/` React/Vite cu va chot lai huong HTML/CSS template cho user shell.
- [x] Noi `user_dashboard.html` vao FastAPI, bo template user du thua va them `user_dashboard.js` cho submit/search/job action.
- [x] Sua `api_user.py` + `store.py` de parse `schedule_time`, suy ra `source_mode`, ho tro cancel/delete job va scaffold OAuth start URL.
- [x] Verify local: `python -m compileall backend/app`, `/api/health` = 200, `/app` = 200, `/admin` = 200, tao/huy/xoa job thanh cong tren browser.
- [x] Dung lai admin theo shell Elevated SaaS cua `BaseSource.AppUI`: mount `admin-themes/css/js`, tao Jinja layout chung, tach 4 route `/admin/user/index`, `/admin/ManagerBOT/index`, `/admin/channel/index`, `/admin/render/index`, va verify browser 4 page deu render.
- [x] Audit do phu admin parity giua FastAPI hien tai va app .NET cu: xac nhan admin moi chi moi cover shell + list page, chua co day du route/action/CRUD/filter/session/export/detail nhu app cu.
- [x] Tao `docs/ADMIN_PARITY_CHECKLIST.md` de chot checklist chi tiet theo module `User / BOT / Channel / Render / Shared infra` va xep thu tu uu tien noi backend admin.
- [x] Viet lai `docs/UI_SYSTEM.md` va tao `docs/FINAL_USER_UI_ANALYSIS.md`, chot `final_user_ui.html` la visual source of truth cho ca user va admin truoc khi refactor lai admin UI.
- [x] Bo sung ghi chu refinement: reference SaaS moi chi duoc dung de polish shell details (logo/avatar/logout/icon), khong thay vai tro source of truth cua `final_user_ui.html`.
- [x] Rewrite `backend/app/templates/admin/render_index.html` theo visual language cua `final_user_ui.html` va `admin/_layout.html` moi, bo Bootstrap/Stisla markup cu va giu nguyen field render co san.
- [x] Dong bo terminolgy UI tu `worker` sang `BOT` tren user/admin template va JS, dong thoi giu backend contract `worker` khong doi.
- [x] Xoa footer credit `Created By Deerflow` khoi ca admin shell va user shell de giao dien sach hon.
- [x] Refactor lai toan bo shell admin theo `final_user_ui.html`: sua `admin/_layout.html`, `_summary_strip.html`, va 4 man `user/worker/channel/render` sang cung he component nhe, bo markup Bootstrap cu.
- [x] Dong bo badge/status class trong `backend/app/store.py`, restart local backend, verify 4 route admin tra 200 va chup headless screenshot de kiem tra UI that.
### 2026-03-25
- [x] Implement xong module `1. User Management` theo `docs/ADMIN_PARITY_CHECKLIST.md`: route/page/action cho `index/create/delete/resetpassword/updatetelegram/manager/admins/managerbot` tren FastAPI.
- [x] Chuan hoa contract `store -> route -> template` cho cac man admin user, bo tinh trang lech template name, field name va action name.
- [x] Them `user_create`, `user_edit`, `user_reset_password`, `user_role_list`, `user_manager_bot` vao luong admin va noi backend that cho create/edit/reset/toggle role/BOT mapping.
- [x] Verify local end-to-end bang HTTP smoke test: tao user, cap nhat, reset password, gan BOT, sua/xoa mapping BOT, promote/demote manager, promote/demote admin, xoa user.
### 2026-03-25
- [x] Implement xong module `2. BOT Management` theo `docs/ADMIN_PARITY_CHECKLIST.md`: route/page/action cho `index/update/delete/updatethread/user/userofbot` tren FastAPI.
- [x] Cap nhat `backend/app/store.py` de support context cho danh sach BOT, BOT cua user, user cua BOT, va luong update/delete/thread tren BOT.
- [x] Rewrite `backend/app/templates/admin/worker_index.html` thanh man `Danh sach BOT` co manager filter, KPI strip, bang BOT va dialog `Sua/Xoa/Luong`.
- [x] Them `backend/app/templates/admin/bot_of_user.html` va `backend/app/templates/admin/user_of_bot.html`, dong thoi noi route `/admin/channel/bot` vao list channel theo BOT.
- [x] Viet lai `docs/ADMIN_PARITY_CHECKLIST.md` sach encoding va cap nhat trang thai module 1, module 2 de lam moc cho cac module tiep theo.
- [x] Verify local bang HTTP smoke test: `/admin/ManagerBOT/index`, `/admin/bot/user`, `/admin/bot/userofbot`, `/admin/channel/bot` deu tra `200`; restart backend de khoi phuc seed state sau test ghi.
### 2026-03-25
- [x] Implement xong module `3. Channel Management` theo `docs/ADMIN_PARITY_CHECKLIST.md`: route/page/action cho `index/user/bot/users/updateuserchannel/adduser/updateprofile/export/delete/deleteajax` tren FastAPI.
- [x] Bo sung mapping `channel_user_links` trong `backend/app/store.py`, chuan hoa helper `find/filter/build row` cho channel va giu du lieu nhat quan khi xoa user/BOT/channel.
- [x] Rewrite `backend/app/templates/admin/channel_index.html` va them `channel_user.html`, `channel_users.html` de noi du luong `DS User`, `DS Render`, cap quyen kenh theo user va user cua kenh.
- [x] Noi route `GET /admin/render/channel` de action `DS Render` tu module channel khong con la nut chet, va bo sung badge filter channel tren man render.
- [x] Verify bang `FastAPI TestClient`: `channel/index`, `channel/user`, `channel/bot`, `channel/users`, `render/channel`, `channel/export`, `updateuserchannel`, `addUser`, `updateprofile`, `delete`, `deleteajax` deu tra ket qua dung.
### 2026-03-25
- [x] Implement xong module `4. Render Management` theo `docs/ADMIN_PARITY_CHECKLIST.md`: route/page/action cho `index/channel/renderinfo/delete` va bo sung `deletejob` de nut xoa tren bang khong con la UI chet.
- [x] Cap nhat `backend/app/store.py` de co `render_delete_meta` that, helper tim job, helper suy user cua job theo `channel_user_links`, va context `render detail` readonly.
- [x] Rewrite `backend/app/templates/admin/render_index.html` theo visual system hien tai, noi form loc manager, action `Chi tiet`, `Xoa tung job`, `Xoa tat ca du lieu`.
- [x] Them `backend/app/templates/admin/render_detail.html` de bam dung flow `RenderInfo` cua app cu: Intro, VideoLoop, AudioLoop, Outro, kenh, thoi luong, lich, ten video.
- [x] Verify bang `FastAPI TestClient`: `render/index`, `render/channel`, `render/renderinfo`, `render/delete`, `render/deletejob` deu tra ket qua dung; compile backend pass.
### 2026-03-25
- [x] Implement xong module `5. Shared Admin Infrastructure`: login/logout admin qua session cookie, role gate `admin/manager`, manager filter session va route parity `POST /admin/UpdateSession`.
- [x] Mo rong `backend/app/routers/api_admin.py` thanh contract theo module cho session, users, roles, user-bot mapping, bots, channels va renders.
- [x] Them persistence local bang SQLite snapshot trong `backend/app/store.py`, luu duoc state admin/user/channel/job qua restart.
- [x] Them `backend/app/templates/admin/login.html`, doi nut logout trong shell thanh form that, va khoa manager binding tren form tao user khi dang nhap bang manager.
- [x] Verify bang `python -m compileall backend/app` va smoke test `TestClient`: redirect khi chua login, login admin, session manager filter, API/admin, va persistence qua `AppStore()` moi deu pass.
### 2026-03-25
- [x] Khoi tao Git cho workspace `D:\\Youtube_BOT_UPLOAD`, them remote `origin` tro den `https://github.com/shinemusicllc/Youtube_Upload_Lush.git`.
- [x] Sua `.gitignore` de bo qua dung `backend/data/app_state.db`, `backend/data/uploads/` va cac artifact local truoc khi commit.
- [x] Tao initial commit `Initial FastAPI control plane rebuild` voi toan bo workspace hien tai, bao gom backend FastAPI, docs parity, `final_user_ui.html` va repo tham chieu `.NET` dang duoc dung de phuc vu asset/UI reference.
- [x] Push thanh cong branch `main` len GitHub remote va set upstream `origin/main`.
### 2026-03-25
- [x] Clone repo `https://github.com/shinemusicllc/Youtube_Upload_Lush.git` vao workspace tam va copy noi dung repo ra root `D:\Youtube_BOT_UPLOAD`.
- [x] Tao `backend\venv`, cai `backend/requirements.txt`, start local app bang `uvicorn` tren `127.0.0.1:8000`.
- [x] Verify startup qua `GET /api/health` tra `{"status":"ok"}`.
- [!] Policy hien tai chan lenh xoa, nen hai thu muc du `Youtube_Upload_Lush` va `YoutubeBOTUpload-master` van con ton tai o root; noi dung repo chinh da nam dung o root.
### 2026-03-25
- [x] Implement flow Google OAuth that cho user dashboard: sinh `state` trong session, callback `/auth/google/callback`, doi `code -> token`, goi `userinfo` va `channels.list(mine=true)`, roi tao/cap nhat channel that trong `backend/app/store.py`.
- [x] Mo rong `ChannelRecord` de luu `oauth_refresh_token`, subject, scope, token type; gioi han bootstrap channel theo user dang dung va them banner notice tren user dashboard.
- [x] Bo sung `.env.example`, tu nap `.env` o root workspace, cai them dependency `httpx` cho smoke test va verify flow bang `FastAPI TestClient` voi mock Google responses (`oauth_smoke_ok`).
- [x] Restart local `uvicorn` va verify lai `GET /api/health` = `{"status":"ok"}` sau khi ap dung code moi.
### 2026-03-25
- [x] Chinh lai KPI strip admin theo `UI_SYSTEM`: bo sung icon, nhan phu duoi so, va giu pattern divider-strip dong nhat cho tat ca tab `User / BOT / Channel / Render`.
- [x] Cap nhat `backend/app/store.py` de `summary_strip` tra ve du icon/mau/accent/value class; rieng KPI upload = `0` hien so mau den de de doc hon.
- [x] Sua partial dung chung `backend/app/templates/admin/_summary_strip.html`, compile backend va restart local `uvicorn`, verify `GET /api/health` = `{"status":"ok"}`.
### 2026-03-25
- [x] Doi avatar chu o admin user list sang palette mau on dinh theo ten, tao cam giac ngau nhien nhung khong bi thay doi qua moi lan reload.
- [x] Tao `backend/app/templates/admin/_manager_picker.html` va thay the `select multiple` tho bang manager picker co search + checkbox + multi-select cho cac tab `User / BOT / Channel / Render`.
- [x] Cap nhat CSS/JS chung trong `backend/app/templates/admin/_layout.html`, compile backend, smoke test `admin_ui_smoke_ok`, restart local `uvicorn` va verify lai `GET /api/health` = `{"status":"ok"}`.
### 2026-03-25
- [x] Thu nghiem them badge nhe cho nhan phu trong KPI strip admin bang partial dung chung `backend/app/templates/admin/_summary_strip.html`.
- [x] Cap nhat `backend/app/store.py` de moi KPI co `accent_badge_class`, compile backend va restart local `uvicorn`, verify lai `GET /api/health` = `{"status":"ok"}`.
### 2026-03-25
- [x] Dieu chinh lai manager picker theo flow tag giong app cu hon: manager da chon hien thanh tag ngoai trigger, moi tag co nut `x` de bo nhanh, va co them `Xóa tất cả` khi dang chon nhieu manager.
- [x] Cap nhat `backend/app/templates/admin/_manager_picker.html` va JS/CSS dung chung trong `backend/app/templates/admin/_layout.html`, compile backend, smoke test `admin_manager_picker_smoke_ok`, restart local `uvicorn` va verify lai `GET /api/health` = `{"status":"ok"}`.
### 2026-03-25
- [x] Trace luong render cua app cu tu `RenderClientService -> BotHub -> UploadYoutubeBot MainWork -> RenderAdminService` de xac nhan pipeline that cua job render/upload.
- [x] Chot lai rang pipeline cu chu yeu la `download -> FFProbe validate -> ffmpeg concat/copy -> Chrome upload`, khong phai full re-encode, nen phu hop hon voi bai toan loop video 4K.
- [x] Ghi nhan cac diem can cai tien cho ban rebuild: preflight disk, tach phase job, bo Selenium upload, va giu fast-path `copy/remux` khi input hop le.
### 2026-03-25
- [x] Nang cap local upload tu `single multipart request` len huong `upload session + resumable chunk upload`, them backend API session, hidden asset refs, JS upload theo chunk va fallback stream-to-disk an toan hon.
- [x] Them scaffold worker-control plane toi thieu: `POST /api/workers/register`, `POST /api/workers/heartbeat`, `workers/agent/main.py`, va file infra/deploy (`Dockerfile`, `docker-compose`, `Caddyfile`, `systemd`, `bootstrap scripts`).
- [x] Tao `workers/AGENTS.md` va `infra/AGENTS.md`, cap nhat root `AGENTS.md` va `docs/PROJECT_CONTEXT.md` de phan tach ro khu vuc `backend / workers / infra`.
- [x] Verify local bang `compileall`, `node --check`, smoke test `upload session -> chunk upload -> create job -> worker register/heartbeat`.
- [x] Deploy thu nghiem control plane len `82.197.71.6:8000` va deploy worker agent len `109.123.233.131`, `62.72.46.42`; xac nhan 2 worker heartbeat thanh cong vao host state.
### 2026-03-25
- [x] Mo rong worker contract len `claim / progress / complete / fail`, them job lease metadata va queue refresh logic trong control plane.
- [x] Nang cap `workers/agent/main.py` thanh poll loop co `simulate mode` opt-in de worker co the dien tap full state machine ma khong bat mac dinh tren VPS.
- [x] Smoke test local cho `register -> claim -> progress -> complete`, sau do redeploy host/worker va xac nhan host van khoe, 2 worker van `active`.
- [x] Don stray process cua chinh app tren host (`:8010`) de tranh de lai runtime rac; giu lai duy nhat app nay tren `:8000`.
### 2026-03-26
- [x] Audit host shared `82.197.71.6` de tim reverse proxy chung dang chiem `80/443`, xac nhan Caddy shared nam trong stack `deploy` va app hien tai van chay rieng tren `:8000`.
- [x] Them site block `ytb.jazzrelaxation.com` vao `/opt/spoticheck/app/deploy/Caddyfile`, reverse proxy sang `172.17.0.1:8000`, validate va reload Caddy ma khong anh huong domain khac.
- [x] Cap nhat `/opt/youtube-upload-lush/.env` tren host sang `APP_BASE_URL=https://ytb.jazzrelaxation.com`, `APP_DOMAIN=ytb.jazzrelaxation.com`, `GOOGLE_REDIRECT_URI=https://ytb.jazzrelaxation.com/auth/google/callback`, roi restart app.
- [x] Verify server-side bang `curl --resolve`: route HTTP da redirect sang HTTPS dung domain moi; HTTPS cert chua cap duoc vi DNS public `ytb.jazzrelaxation.com` hien chua ton tai.
- [x] Xac nhan `ytb.jazzrelaxation.com` da tro DNS dung va Caddy da issue cert Let's Encrypt thanh cong; HTTPS handshake that da hoat dong.
- [x] Mo khoa backend contract cho worker media: luu them `asset_id` tren `JobAsset`, them route `GET /api/workers/jobs/{job_id}/assets/{slot}`, va smoke test `worker_asset_contract_ok` bang TestClient.
- [x] Tach worker Python thanh `config / control_plane / downloader / ffmpeg_pipeline / job_runner`, ho tro local asset download, Google Drive/HTTP download, va FFmpeg fast-path `copy/remux`.
- [x] Them safety gate `WORKER_EXECUTE_JOBS=false` mac dinh, cap nhat `systemd` service sang `python -m workers.agent.main`, va redeploy host + 2 worker VPS; verify host health = 200 va `worker-01`, `worker-02` heartbeat lai thanh `online`.
- [x] Audit queue song tren host, xoa job demo `job-379e626e` dang chan `worker-01`, va reindex lai queue `pending/queueing`.
- [x] Bat `WORKER_EXECUTE_JOBS=true` chi tren `worker-01`, restart service, va verify worker process `python -m workers.agent.main` van `active`.
- [x] Xac nhan tu host rang `worker-01` tiep tuc heartbeat `online`, khong an nham job nao, trong khi `worker-02` van giu execution gate tat.
- [x] Trace job Drive that `job-54798817` bi fail voi loi `Asset video_loop không có video stream`, xac dinh nguyen nhan la ca `video_loop` va `audio_loop` deu bi tai ve cung ten tam `view` doi voi Google Drive link dang `/file/d/.../view`.
- [x] Sua `workers/agent/downloader.py` de moi asset luon tai vao thu muc rieng theo `slot`, rollout ban va len `worker-01` va `worker-02`, restart service va verify compile tren worker.
- [x] Tao lai job Drive that `job-40a682dd` voi 2 link Google Drive user cung cap, theo doi live qua control plane, va xac nhan `worker-01` render fast-path thanh cong file output 60 giay.
- [x] Them route control plane de worker lay YouTube upload target theo job/channel, va them worker module `youtube_uploader.py` dung `refresh token -> resumable upload API`.
- [x] Compile va smoke test local cho contract YouTube upload target va uploader chunked; xac nhan `upload_video()` tra `watch_url` dung trong fake resumable flow.
- [x] Rollout code moi len host, `worker-01`, `worker-02`; restart dung process/service cua app nay ma khong dung vao reverse proxy hay app khac tren host shared.
- [x] Bat gap regression sau deploy do bo sot `workers/agent/downloader.py` tren worker, sua rollout, redeploy file nay len ca 2 worker va xac nhan worker service quay lai `active`.
- [x] Khoa ro rang `WORKER_UPLOAD_TO_YOUTUBE=false` + `YOUTUBE_UPLOAD_CHUNK_BYTES=8388608` trong `/etc/youtube-upload-worker.env` cua `worker-01` va `worker-02`.
- [x] Verify hau deploy bang job Drive that `job-e667631b`, xac nhan `worker-01` van render thanh cong va tra `worker://...` output khi upload gate dang tat.
- [x] Trich logo inline SVG tu sidebar user/admin thanh brand asset that, tao file `SVG` va `PNG 120x120` de dung cho Google OAuth consent screen.
- [x] Doi chieu yeu cau `Application home page / Privacy policy / Terms / Authorized domains` voi docs chinh thuc cua Google de chot cach dien cho domain `ytb.jazzrelaxation.com`.
- [x] Sua bộ scope OAuth trong backend de them `youtube.readonly`, compile local va rollout `backend/app/store.py` len host de flow connect Google xin du scope doc channel.
- [x] Noi hanh dong xoa that cho card `My Channel`: them API `DELETE /api/user/channels/{channel_id}`, rang buoc quyen theo user hien tai, va bat nut `Xóa` tren UI user dashboard.
- [x] Xu ly su co `502` tren `ytb.jazzrelaxation.com`: xac nhan Caddy/Cloudflare van on, origin `172.17.0.1:8000` bi `connection refused` do host app mat process `uvicorn`.
- [x] Tao `infra/systemd/youtube-upload-web.service`, cap nhat `scripts/bootstrap_host.sh` ho tro `DEPLOY_MODE=systemd`, rollout service file len host va `systemctl enable --now youtube-upload-web.service`.
- [x] Verify sau fix: `systemctl is-active youtube-upload-web.service` = `active`, `ss -ltnp` co listener `0.0.0.0:8000`, `curl http://127.0.0.1:8000/api/health` = `{\"status\":\"ok\"}`, `curl https://ytb.jazzrelaxation.com/api/health` = `{\"status\":\"ok\"}`.
- [x] Sua user channel card ve layout row on dinh: dua status vao trong block noi dung, doi nut xoa thanh icon action o cuoi hang, va verify local `DELETE /api/user/channels/{id}` tra `200`.
- [x] Them co che client-side de tu xoa `notice` va `notice_level` khoi URL sau khi user dashboard render xong, rollout `user_dashboard.js` len host va verify public health van `ok`.
- [x] Commit local workspace thanh `768cc1a Add YouTube upload pipeline and harden host runtime` va push len `origin/main`; xac nhan `git ls-remote origin refs/heads/main` trung commit moi.
- [x] Audit dong bo code giua local/GitHub/VPS bang hash file: host lech `backend/app/store.py` va `backend/app/routers/api_user.py`; `worker-01` khop toan bo file da doi chieu; `worker-02` lech `workers/agent/config.py`, `workers/agent/control_plane.py`, `workers/agent/job_runner.py`, `scripts/bootstrap_worker.sh`.
