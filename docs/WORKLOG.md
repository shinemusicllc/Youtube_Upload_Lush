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
- [x] Dong bo nốt file lech len host (`store.py`, `api_user.py`) va `worker-02` (`config.py`, `control_plane.py`, `job_runner.py`, `bootstrap_worker.sh`), restart service tuong ung va verify health/service `active`.
- [x] Doi chieu lai hash sau sync: host va `worker-02` da khop local/GitHub o cac file truoc do bi lech; `worker-02` van giu `WORKER_EXECUTE_JOBS=false` va `WORKER_UPLOAD_TO_YOUTUBE=false`.
- [x] Pull repo local len commit `97df154`, doc lai project memory va rule bootstrap, quet config `backend/requirements.txt`, `workers/agent/requirements.txt`, `.env.example`, `infra/docker/host/docker-compose.yml`.
- [x] Tao local runtime moi bang `D:\Youtube_BOT_UPLOAD\.venv`, cai dependency cho backend va worker agent theo repo vua pull.
- [x] Tao `.env` dev toi thieu cho local (`SESSION_SECRET`, `WORKER_SHARED_SECRET`, `APP_BASE_URL`, `GOOGLE_*`) de backend boot on dinh tren `127.0.0.1:8000`.
- [x] Dung process `uvicorn` cu tren port `8000`, restart backend bang `.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000`, va verify `/api/health`, `/app`, `/admin/login` deu tra `200`.
- [x] Cap nhat `.gitignore` bo sung `.env` va `.venv/`; ghi nhan worker local chua duoc detach do policy moi truong chan launch background co env tuy bien.
- [x] Dieu chinh user UI theo pattern cu cho `My Channel`: giu badge `Đã kết nối` o ben phai va chi hien nut xoá icon-only khi hover/focus vao tung row channel.
- [x] Bo chu `Lush` khoi wordmark user sidebar bang cach doi `dashboard.page_title` va `dashboard.app_name` ve `Youtube Upload`.
- [x] Restart backend local sau khi sua template/store va verify lai `GET /app` tra `200`, HTML render dung wordmark moi va class hover channel action.
- [x] Doi wordmark sidebar user tu `Youtube Upload` thanh `Upload Youtube` theo ten san pham ma user chot cho local shell.
- [x] Restart backend local va verify lai `GET /app` render dung `<title>Upload Youtube</title>` va brand text `Upload Youtube`.
- [x] Trace loi OAuth local: callback dau tien da luu channel thanh cong nhung `store.complete_google_oauth()` thieu `return`, khien route callback crash `500`; reload URL callback cu moi dan toi notice `invalid_grant`.
- [x] Sua user dashboard de render `avatar_url` that cho channel OAuth neu co, fallback ve initials khi thieu anh.
- [x] Restart backend local va verify `/app` render dung avatar `yt3.ggpht.com` cua kenh moi trong khu `My Channel`.
- [x] Sua dropdown `Chọn kênh` de option list va trigger deu uu tien render `avatar_url` that, khong con chi hien initials cho kenh moi OAuth.
- [x] Restart backend local va verify `/app` co `data-avatar-url` trong dropdown seed va template option render `img.object-cover` cho kenh co avatar.
- [x] Them class `channel-avatar-media` de avatar anh that co border va do bong nhe o dropdown va khu `My Channel`, giu layout cu nhung bot flat.
- [x] Restart backend local va verify `/app` co class `channel-avatar-media` trong HTML render.
- [x] Noi preview cho job list: uu tien lay anh/video tu asset `video_loop`; local upload di qua route `/api/user/jobs/{job_id}/preview/{slot}`, Google Drive co `file id` thi suy ra thumbnail.
- [x] Them fallback preview cho du lieu seed/job cu bang `thumbnail_url` roi toi `channel_avatar_url`, de UI khong quay lai icon khi chua co preview that.
- [x] Restart backend local, compile lai `backend/app`, va verify hang job tren `/app` da render `job-preview-media` thay cho icon cu.
- [x] Tách meta `My Channel` thành `channel_id`, `bot_label`, `public_url`; nối tên kênh và `channel_id` thành link mở public channel YouTube, không thêm link YouTube Studio.
- [x] Restart backend local và verify HTML `/app` đã render `https://www.youtube.com/channel/<channel_id>` trong card `My Channel`.
- [x] Đổi ô preview media trong bảng render từ khung vuông sang tỉ lệ `4:3` cho cả preview thật và fallback icon/text để giảm khoảng trống ngang.
- [x] Restart backend local và verify `/app` vẫn trả `200` sau khi chỉnh layout thumbnail job.
- [x] Sửa notice trên user dashboard: message OAuth callback dùng tiếng Việt có dấu, thêm nút đóng `x`, và JS tự ẩn notice sau vài giây thay vì chỉ xóa query param.
- [x] Restart lại backend local bằng process detached, verify `/api/health` trả `200` và redirect `/auth/google/callback?error=test` đã encode đúng tiếng Việt có dấu.
- [x] Tăng stroke/shadow cho `channel-avatar-media` để avatar không bị chìm trên nền trắng ở `My Channel` và dropdown `Chọn kênh`.
- [x] Nối `channel_avatar_url` vào `render_jobs` và đổi cột kênh trong `list render` sang ưu tiên ảnh avatar thật, chỉ fallback về initials khi thiếu ảnh.
- [x] Restart backend local và verify HTML `/app` đã render avatar image trong cột kênh của bảng render.
- [x] Sync 5 file runtime mới (`api_user.py`, `web.py`, `user_dashboard.js`, `store.py`, `user_dashboard.html`) lên host `82.197.71.6:/opt/youtube-upload-lush`, backup bản cũ theo timestamp trước khi ghi đè.
- [x] Compile backend trên host, restart `youtube-upload-web.service`, verify `systemctl is-active` = `active`, `curl http://127.0.0.1:8000/api/health` = `{\"status\":\"ok\"}`, và `curl https://ytb.jazzrelaxation.com/api/health` = `{\"status\":\"ok\"}`.
- [x] Đối chiếu trực tiếp file trên host: template đã có `data-notice-close`, `data-notice-autohide`, avatar `<img>` trong cột kênh của bảng render, và JS đã có `initTransientNotice()`.
- [x] Đổi riêng hệ màu `My Channel` từ `emerald` sang `brand/blue` cho icon block, hover border và badge trạng thái để khớp visual language chung của app.
- [x] Sync lại `backend/app/templates/user_dashboard.html` lên host, restart `youtube-upload-web.service`, verify file trên host đã có `hover:border-brand-200` và `border-brand-200 bg-brand-50`.
- [x] Đồng bộ trigger của dropdown `Chọn kênh`: thêm dòng `channel meta` dưới tên kênh sau khi đã chọn, lấy từ `data-meta` của option để khớp với menu list.
- [x] Sync `user_dashboard.html` và `user_dashboard.js` lên host, restart `youtube-upload-web.service`, verify host đã có `channel-select-meta` trong template và `channelMeta` trong JS.
- [x] Đổi icon block và badge `Đã kết nối` của `My Channel` về lại họ `emerald`, nhưng giữ hover border của row theo `brand/blue`.
- [x] Bọc avatar channel bằng public link và bỏ `:focus-within` khỏi cơ chế ẩn/hiện status-delete để tránh trạng thái treo icon xoá sau khi click link public rồi quay lại tab.
- [x] Sync lại `backend/app/templates/user_dashboard.html` lên host, restart `youtube-upload-web.service`, verify host không còn `channel-row:focus-within`, có `channel.public_url` trên avatar, và public health vẫn `ok`.
- [x] Rollback thay đổi `channel-select-meta/channel-select-copy`: trả trigger của dropdown `Chọn kênh` về dạng cũ chỉ gồm avatar + tên kênh, giữ menu list nguyên như trước.
- [x] Sync lại `user_dashboard.html` và `user_dashboard.js` lên host, restart `youtube-upload-web.service`, verify host không còn `channel-select-copy`, `channel-select-meta`, hay `data-meta=`.
### 2026-03-26 10:14
- [x] Debug loi avatar trigger o dropdown Ch?n K�nh tren VPS: xac nhan option co data-avatar-url dung, nhung trigger van co the bi JS cap nhat nham node hoac dung file JS cache cu.
- [x] Tach selector trigger avatar thanh class rieng channel-select-trigger-avatar, cap nhat user_dashboard.js de chi update node trigger nay va trim vatarUrl truoc khi render <img>.
- [x] Tang version query cua /static/js/user_dashboard.js len 20260326-channel-avatar-fix de ep browser tren VPS nap file JS moi.
- [x] Deploy user_dashboard.html va user_dashboard.js len host 82.197.71.6, restart youtube-upload-web.service, verify origin/public health va xac nhan public HTML da tro toi JS version moi.
### 2026-03-26 10:34
- [x] Bo sung channel-select-meta vao trigger Ch?n K�nh de hien channel_id nho duoi ten kenh, nhung giu avatar + ten o cung structure on dinh de khong vo dropdown nua.
- [x] Refactor local-upload control tren user dashboard: doi icon label sang utton that co data-upload-trigger, tach file input hidden rieng, sua JS mo file picker on dinh thay vi phu thuoc click qua label.
- [x] Implement UI state cho upload local theo tung slot: idle -> uploading -> success, co vong tron progress, nut x de huy/remove, va auto upload ngay sau khi user chon file thay vi doi den luc submit form.
- [x] Sync user_dashboard.html va user_dashboard.js len host 82.197.71.6, restart youtube-upload-web.service, verify public HTML da dung JS version 20260326-upload-ui-flow va co markup moi.
### 2026-03-26 10:42
- [x] Doi text icon o tam vong progress local upload sang Lucide that (x, check) de dong bo voi he icon chung cua user dashboard.
- [x] Sync lai user_dashboard.html va user_dashboard.js len host, restart youtube-upload-web.service, va verify service/listener/health deu on dinh sau rollout.
### 2026-03-26 10:50
- [x] Doi mau state uploading cua nut progress local upload sang do cho ca ring va icon center de user nhin vao hieu ngay co the bam x de huy.
- [x] Sync lai template user dashboard len host, restart youtube-upload-web.service, verify origin va public health deu ok.
### 2026-03-26 11:15
- [x] Trace job `job-d3531066` tren VPS va xac nhan job creation/worker claim da hoat dong lai sau khi chuyen scheduling/claim logic sang mui gio `Asia/Saigon`.
- [x] Bo sung helper thoi gian chung trong `backend/app/store.py` (`_now`, `_normalize_datetime`, `APP_TIMEZONE`) de tat ca so sanh `scheduled_at`, `claimed_at`, `last_seen_at` va timestamp nghiep vu dung cung mot chuan gio Ha Noi.
- [x] Va bug tao job local: bo qua `UploadFile` rong va normalize empty string cho `*_asset_id`, `*_url` trong `backend/app/routers/api_user.py` va `backend/app/store.py`, tranh tao asset 0 byte cho `intro/outro` rong.
- [x] Deploy `store.py` va `api_user.py` len host, restart `youtube-upload-web.service`, verify worker da claim duoc job that; job cu `job-d3531066` fail do asset `video_loop` da duoc luu 0 byte truoc khi ban va moi duoc rollout.
### 2026-03-26 11:22
- [x] Kiem tra job thuc te tren host `job-777d9f0a` va xac nhan render da hoan tat, worker claim/progress/complete hoat dong dung.
- [x] Xac nhan phase upload YouTube chua chay: `upload_started_at = null`, `output_url = worker://.../job-777d9f0a-1.mp4`, va `status = completed` theo nghia hoan tat render local output chua phai upload YouTube.
- [x] Doi chieu voi rollout hien tai: worker dang tra output local path ve control plane, can mo khoa upload YouTube gate tren worker de buoc upload that duoc thuc thi.
### 2026-03-26 11:30
- [x] Kiem tra rollout upload YouTube that cho `worker-01`: xac nhan control plane co day du `GOOGLE_CLIENT_ID/SECRET` va channel `UC5f3fhbLie_m_WIQa1LNpSg` da co `refresh token` hop le tren host.
- [x] Doi chieu job `job-777d9f0a`: render hoan tat, output local da tao, nhung upload phase chua tung bat dau nen `upload_started_at` van `null`.
- [x] Xac nhan blocker hien tai nam o ha tang worker: khong the SSH truc tiep vao `109.123.233.131` bang credential host, va host control plane cung khong co key/password de SSH tiep sang worker de bat `WORKER_UPLOAD_TO_YOUTUBE=true`.
### 2026-03-26 11:38
- [x] Dang nhap duoc vao `worker-01` (`109.123.233.131`) va `worker-02` (`62.72.46.42`) bang credential user cung cap, audit env runtime thuc te cua 2 worker.
- [x] Bat `WORKER_UPLOAD_TO_YOUTUBE=true` tren `worker-01`, giu `worker-02` tiep tuc `WORKER_UPLOAD_TO_YOUTUBE=false` va `WORKER_EXECUTE_JOBS=false` de standby.
- [x] Doi `CONTROL_PLANE_URL` cua ca 2 worker sang `https://ytb.jazzrelaxation.com`, restart service va verify `youtube-upload-worker.service` deu `active`.
- [x] Upload thu cong file output cua job `job-777d9f0a` tu `worker-01` len YouTube bang code path worker (`youtube_uploader.py`), va control plane da cap nhat `upload_started_at`, `completed_at`, `output_url` theo watch URL that.
### 2026-03-26 12:02
- [x] Tach user dashboard status cua job thanh 2 phase ro rang: `Render hoan tat` va `Da upload YouTube`, thay vi hien chung `Hoan tat` cho moi job `completed`.
- [x] Bo sung derived status view trong `backend/app/store.py`: mau progress, badge status, timeline `Render/Upload`, va `youtube_watch_url` cho user UI.
- [x] Cap nhat `backend/app/templates/user_dashboard.html` de dung field moi, hien `Render:` / `Upload:`, an nut `Huy` khi job khong con cancel duoc, va them nut `Xem` khi job da co watch URL YouTube.
- [x] Deploy `store.py` va `user_dashboard.html` len host `82.197.71.6`, restart `youtube-upload-web.service`, verify origin/public HTML deu hien `Render`, `Upload` va link YouTube cho `job-777d9f0a`.
### 2026-03-26 13:30
- [x] Keo khoi thong tin job sang trai bang cach doi `td` thong tin job sang `pl-2 pr-6` va giam gap preview/text de mep cover khit hon voi divider sau cot STT.
- [x] Doi cot `Tien do` sang 2 thanh rieng `Render` (emerald) va `Upload` (rose), derive tu state thuc te cua job thay vi 1 thanh tong hop.
- [x] Bo sung `GET /api/user/dashboard/live` va polling 5 giay/l?n trong `user_dashboard.js` de cap nhat KPI, tab count, status, timeline va progress queue ma khong can refresh trang.
- [x] Deploy `api_user.py`, `store.py`, `user_dashboard.html`, `user_dashboard.js` len host `82.197.71.6`, restart `youtube-upload-web.service`, verify public `/app` va `/api/user/dashboard/live` deu tra du lieu moi.
### 2026-03-26 14:05
- [x] Sua user queue live polling de khong rerender tbody khi payload khong doi, loai bo hien tuong thumbnail preview nhay moi 5 giay.
- [x] Can lai cot Tien do bang layout noi bo trung tam hon va doi mau thanh Upload sang amber de giam choi, giu nguyen visual system hien tai.
- [x] Deploy user_dashboard.html va user_dashboard.js len host 82.197.71.6, restart youtube-upload-web.service, verify public health van ok.
### 2026-03-26 13:18
- [x] Audit lifecycle media tren control plane + worker, xac nhan job hen lich da co gate scheduled_at <= now nen khong render som, nhung local upload cache va worker output chua duoc don sach sau khi upload thanh cong.
- [x] Sua backend/app/store.py de completed job uu tien preview YouTube thumbnail, va cleanup local upload asset/session khi job da upload YouTube thanh cong hoac khi job bi xoa.
- [x] Sua workers/agent/job_runner.py de xoa file render trong worker-data/outputs ngay sau complete_job() thanh cong voi watch URL YouTube.
- [x] Deploy backend/app/store.py len host 82.197.71.6, deploy workers/agent/job_runner.py len worker-01 va worker-02, compile/restart service va verify health ok.
- [x] Don runtime stale tren VPS: worker-01 giam outputs tu 3.6G xuong 4K; control plane xoa 6 local asset file/session da khong con can va restart web service de memory reload state sach.
### 2026-03-26 13:44
- [x] Doc lai project memory, audit state host va xac nhan 2 kenh that Lê Hoàng, Loki Lofi deu dang map worker-01; worker-02 ban dau van WORKER_EXECUTE_JOBS=false, WORKER_UPLOAD_TO_YOUTUBE=false.
- [x] Tao 2 job hẹn lịch 26/03/2026 13:40 len 2 kenh that; ca hai job deu upload thanh cong nhung bi worker-01 claim truoc khi bai test worker-02 duoc khoa lai hoan toan (job-cee17d22, job-0cbf7a27).
- [x] Dung worker-01, map tam channel-7757adbd sang worker-02, bat gate execute/upload tren worker-02, tao job kiem soat job-a34dd1f9 lich 26/03/2026 13:43, va xac nhan claimed_by_worker_id=worker-02, upload thanh cong YouTube, output worker van rong sau job.
- [x] Khai phuc trang thai van hanh an toan sau test: start lai worker-01, tra channel-5e012410 va channel-7757adbd ve worker-01, tat lai gate execute/upload tren worker-02, va verify host + 2 worker deu active/online.### 2026-03-26 13:52
- [x] Audit bug vo viewport tren user dashboard bang code + Playwright, xac nhan nguyen nhan chinh la main flex item thieu min-w-0 nen bi no theo bang render, cong them bang dang khoa width boi min-w-[360px], whitespace-nowrap va action cung hang.
- [x] Sua ackend/app/templates/user_dashboard.html de them min-w-0/overflow-x-hidden cho content pane, bo rang buoc width cung o cot thong tin job va cho cum action wrap an toan.
- [x] Sua ackend/app/static/js/user_dashboard.js de live polling khi rerender tbody giu cung class/layout moi, tranh 5 giay sau lai quay ve DOM cu gay tran viewport.
- [x] Verify local va host bang Playwright: truoc fix odyScrollWidth tren trang live = 2113 voi viewport 1365; sau fix odyScrollWidth = 1365, bang chi con scroll noi bo trong wrapper thay vi keo vo ca trang.
- [x] Deploy user_dashboard.html va user_dashboard.js len host 82.197.71.6, restart youtube-upload-web.service, verify health ok.### 2026-03-26 14:03
- [x] Rà lại preview flow va chot huong bo YouTube thumbnail lam primary source; thay vao do worker se tao cached preview image va upload ve control plane de job giu anh ngay ca khi source/output da bi don.
- [x] Mo rong backend voi 	humbnail_path, preview_dir, route GET /api/user/jobs/{job_id}/preview-thumbnail, route worker POST /api/workers/jobs/{job_id}/thumbnail, va cleanup preview khi xoa job/channel/bot.
- [x] Mo rong worker fmpeg_pipeline.py, control_plane.py, job_runner.py de chup frame tu output video va day preview image ve control plane truoc khi cleanup.
- [x] Verify local bang smoke test ackend_preview_smoke_ok, compile backend/worker pass; rollout len host, worker-01, worker-02, restart service va verify health/service ctive.
- [x] Verify live payload: 3 job hien tai khong con bi ep dung i.ytimg.com, ma fallback ve ideo_loop_url; preview cache noi bo se ap dung cho cac job moi sau rollout.
### 2026-03-26 14:12
- [x] Tao job thuc te `job-e383de12` tren kenh `Loki Lofi` bang sample source de verify end-to-end preview cache moi sau rollout.
- [x] Theo doi live payload va xac nhan job upload YouTube thanh cong voi `preview_url=/api/user/jobs/job-e383de12/preview-thumbnail`, `preview_kind=image`, watch URL `https://www.youtube.com/watch?v=PTtcp73Od9A`.
- [x] Kiem tra runtime tren host va worker-01: `thumbnail_path=job-e383de12.jpg` da duoc luu trong `backend/data/previews`, file preview tai ve duoc, va `worker-data/outputs` khong con file output cua job sau khi upload xong.
- [x] Xoa job `job-e383de12` qua API user va verify lai DB/live endpoint/preview route: job bien mat khoi dashboard, file `backend/data/previews/job-e383de12.jpg` bi xoa, route preview tra `404`.
### 2026-03-26 14:26
- [x] SSH audit ca `worker-01` (`109.123.233.131`) va `worker-02` (`62.72.46.42`) de xac nhan he dieu hanh, CPU, RAM, disk va runtime worker hien tai.
- [x] Xac nhan ca hai worker deu la `Ubuntu 22.04.5 LTS`, 4 vCPU `AMD EPYC`, ~5.8 GiB RAM, disk ~400 GB; worker-01 dang dung ~30 GB root disk, worker-02 dang dung ~72 GB.
- [x] Kiem tra runtime browser/process: khong co `google-chrome`, `chromium`, `chromium-browser`, `Xvfb` hay process Chrome nao dang chay; worker service hien la Python systemd service thuần.
- [x] Ket luan ha tang worker hien tai da phu hop huong `render + upload API`, nen bai toan khong phai doi tu Windows sang Ubuntu nua ma la toi uu dung luong/cau hinh Linux cho cac worker moi ve sau.
### 2026-03-26 14:50
- [x] Noi `login_preview.html` vao route `/admin/login` bang template moi `backend/app/templates/admin/login.html`, giu dung contract session admin/manager hien tai va bo sung toggle password, notice state, giu lai username khi login sai.
- [x] Cap nhat `backend/app/routers/web.py` de sanitize `next` redirect, dong bo `page_title`, va truyen `form_data/notice_level` cho login template.
- [x] Smoke test local bang `TestClient`: `/admin/login` render duoc, login sai tra `400` va giu username, login dung tra `303` ve `/admin/user/index` va set session cookie.
- [x] Sync `web.py` va `admin/login.html` len host `82.197.71.6`, compile backend, restart `youtube-upload-web.service`, verify live `GET /admin/login = 200`, login sai giu username, login dung redirect vao `/admin/user/index`.
- [x] Audit auth/account/storage cua app moi va doi chieu app cu: admin auth da co nen, user auth that chua co; storage hien la SQLite JSON snapshot bootstrap, chua du cho multi-user production; co the tan dung workflow/role model cua app cu nhung khong copy cach luu password plaintext va auth stack `JWT -> cookie` chong lop.
### 2026-03-26 14:48
- [x] Rule bootstrap lai task login: doc project memory, `docs/UI_SYSTEM.md`, root/backend AGENTS va scan config chinh truoc khi sua UI/auth.
- [x] Audit auth hien tai trong FastAPI: login that chi moi co cho `admin/manager` qua session cookie; user workspace van chay theo shortcut `store._current_app_user()` thay vi user session that.
- [x] Doi chieu app cu o `YoutubeBOTUpload-master`: co the tai su dung phan tách role `Admin / Manager / User`, route/account workflow va quan he `manager -> user -> channel`, nhung khong copy auth/storage cu vi van giu plaintext password song song `PasswordHash`.
- [x] Noi `login_preview.html` vao route `/admin/login` bang file moi `backend/app/templates/admin/login.html`, giu contract form `username/password/next`, banner notice va them toggle hien/ẩn mat khau.
- [x] Verify bang `TestClient`: `GET /admin/login` tra `200`, login sai giu lai `username` + error, login dung tra `303` ve `/admin/user/index` va set cookie `admin_auth`.
- [x] Sync `backend/app/routers/web.py` va `backend/app/templates/admin/login.html` len host `82.197.71.6`, restart `youtube-upload-web.service`, verify public `/admin/login` tra `200` va Playwright login live thanh cong vao `/admin/user/index`.
### 2026-03-26 16:20
- [x] Rule bootstrap cho phase auth that: doc lai project memory, `docs/UI_SYSTEM.md`, root/backend AGENTS va scan config `backend/requirements.txt`, `workers/agent/requirements.txt`, `infra/docker/host/docker-compose.yml`.
- [x] Audit toan bo touchpoint auth/storage hien tai, xac nhan user workspace van phu thuoc `_current_app_user`, API `/api/user/*` chua co session gate, va password van dang luu/hiển thị plaintext trong `store.py` + `user_role_list.html`.
- [x] Dung auth layer moi trong `backend/app/auth.py`: bo sung `AppSessionUser`, helper `get/set/clear` user session va giu song song auth admin hien co trong cung session middleware.
- [x] Nang cap `backend/app/store.py` theo huong session-aware: user dashboard/job/channel/upload session gio nhan `user_id` that, OAuth callback bind vao user dang login, va preview/local asset route chi tra ve du lieu job thuoc user do.
- [x] Dua credential sang hash PBKDF2 trong `backend/app/store.py`, them migration tu `password` plaintext -> `password_hash`, va tao bang `auth_users/auth_credentials/auth_channel_grants` trong cung `backend/app/data/app_state.db` de giu source of truth cho auth/account.
- [x] Noi user login/logout that trong `backend/app/routers/web.py` voi route `/login`, `/logout`, redirect browser `/ -> /login`, `/app -> /login?next=/app` khi chua co session, va giu `/admin/login` tiep tuc dung cung UI shell.
- [x] Ràng buộc toan bo `backend/app/routers/api_user.py` vao current user session, dong thoi user dashboard topbar logout da thanh form POST that.
- [x] Bo hien thi password plaintext tren admin role list, doi field thanh `credential_status`, va doi cac input tao/reset password sang `type=password`.
- [x] Verify local bang `python -m compileall backend/app` va smoke test `TestClient`: `/app` redirect khi chua login, `/api/user/bootstrap` tra `401`, login user `demo-user/demo123` vao `/app` thanh cong, logout user redirect `/login`, login admin van vao `/admin/user/index`, va `store.user_meta['user-1']` chi con `password_hash`.
### 2026-03-26 16:35
- [x] Sync phase auth moi len host `82.197.71.6:/opt/youtube-upload-lush`, backup runtime cu vao `.backup/auth-phase-<timestamp>`, compile backend va restart `youtube-upload-web.service`.
- [x] Verify live/public route: `GET https://ytb.jazzrelaxation.com/login = 200`, `GET https://ytb.jazzrelaxation.com/app = 302 -> /login?next=/app`, `GET https://ytb.jazzrelaxation.com/admin/login = 200`, va HTML login da dung dung `form action` moi cho user/admin.
- [x] Inspect live persisted auth state tren host bang runtime `.venv`: user/account da duoc migrate sang `password_hash`, nhung password live khong trung seed local `admin123/demo123`, nen login that can dung credential cu cua he thong thay vi bo seed bootstrap.
### 2026-03-26 16:55
- [x] Doi huong auth UX tu `2 login page` sang `1 login page`: bo flow user-login va admin-login tach biet, chi giu duy nhat `/login` va dieu huong theo role sau khi xac thuc.
- [x] Cap nhat `backend/app/store.py` them `authenticate_login_user()` de xac thuc chung moi role tren cung credential source.
- [x] Sua `backend/app/routers/web.py` de `/login` tu dong set app-session hoac admin-session theo role, user dang login ma mo `/admin/*` se khong duoc dua vao login page rieng nua, va `/admin/login` tro thanh alias redirect ve `/login?next=/admin/user/index`.
- [x] Sua `backend/app/templates/admin/login.html` thanh shell login hop nhat, an switch-link khi khong can va giu mot form action duy nhat `/login`.
- [x] Verify local: `demo-user` login tu `/login` luon vao `/app`, `admin` login tu `/login` luon vao `/admin/user/index`, `admin` mo `/app` se bi redirect ve admin space, va HTML khong con link `/admin/login` nhu mot login page rieng.
- [x] Sync `web.py`, `store.py`, `admin/login.html` len host `82.197.71.6`, compile backend, restart `youtube-upload-web.service`, verify live `/login = 200`, `/admin/login = 302 -> /login?next=%2Fadmin%2Fuser%2Findex`, `/app = 302 -> /login?next=/app`, va HTML live khong con link sang login page thu hai.
### 2026-03-26 16:14
- [x] Siết lại bảng render user theo layout compact: bỏ fallback description thừa, ép title/meta/description về ellipsis 1 dòng, thu hẹp cột STT và giảm preview/action spacing để hàng nút tác vụ giữ một dòng ngang.
- [x] Đổi cột `BOT` sang `VPS` trên user dashboard, lấy tên hiển thị từ worker record thay vì cứng `job.worker_name`, đồng thời thêm `bot_meta` để vẫn nhìn ra alias nội bộ khi cần đối chiếu.
- [x] Sửa derive queue label trong `backend/app/store.py` thành `Queue #...` ngay cả khi `queue_order` runtime đã bị clear ở job completed, tránh hiện `Chưa xếp hàng` gây hiểu nhầm.
- [x] Đồng bộ lại renderer live trong `backend/app/static/js/user_dashboard.js`, tăng cache-bust version trong template và verify local bằng `TestClient` rằng `/app` không còn fallback text cũ, đã có `VPS`, `Queue #1` và JS version mới.
- [x] Rollout `store.py`, `user_dashboard.html`, `user_dashboard.js` lên host `82.197.71.6`, restart `youtube-upload-web.service`, verify `/api/health` public/origin đều `ok`.
- [x] Đổi `WORKER_NAME` live trên `worker-01` và `worker-02` sang chính IP VPS (`109.123.233.131`, `62.72.46.42`), restart `youtube-upload-worker.service`, và xác nhận host state đã nhận tên mới qua heartbeat.
### 2026-03-26 16:32
- [x] Chuẩn hóa danh tính worker theo IP VPS thật trong `backend/app/store.py`: thêm mapping `worker-01 -> 109.123.233.131`, `worker-02 -> 62.72.46.42`, auto-normalize `worker.name` khi load state, và giữ nguyên `worker.id` làm internal contract.
- [x] Rà soát và thay toàn bộ builder admin/user/export còn `replace("worker", "BOT")` sang helper display chung, bao gồm user channel cards, admin worker rows, channel rows, render rows, filter chip `filtered_bot`, dropdown gán worker và export `BotName`.
- [x] Dọn các dòng phụ còn lộ alias nội bộ trong UI admin: bỏ `bot_id` khỏi bảng `worker_index` và `bot_of_user`, đổi meta dòng phụ trong `user_manager_bot` sang `note` thay vì `worker_id`.
- [x] Verify local bằng `compileall` + runtime assertions rằng context `user/admin/export` không còn trả `worker-01/worker-02` ở phần hiển thị mà dùng IP VPS thật.
- [x] Rollout `store.py`, `admin/worker_index.html`, `admin/bot_of_user.html`, `admin/user_manager_bot.html` lên host `82.197.71.6`, restart `youtube-upload-web.service`, verify context runtime trên VPS đã trả `109.123.233.131`, `62.72.46.42` cho user/admin/export.
### 2026-03-26 17:01
- [x] Căn lại cột `Tiến độ` trong bảng render user: đổi progress stack sang `justify-end` và thêm `progress-cell` để block hai thanh bám đáy hàng, thẳng hơn với dòng `Upload` của cột timeline.
- [x] Đồng bộ renderer live trong `backend/app/static/js/user_dashboard.js` với markup template để sau mỗi lần polling bảng không bị quay lại layout cũ.
- [x] Tăng cache-bust version của `user_dashboard.js` lên `20260326-progress-bottom-align` để ép browser lấy JS mới ngay sau deploy.
- [x] Deploy `backend/app/templates/user_dashboard.html` và `backend/app/static/js/user_dashboard.js` lên host `82.197.71.6`, compile backend, restart `youtube-upload-web.service`, verify origin health `200` và public health `200`.
- [x] Ghi nhận lần restart có một nhịp `502` ngắn ngay sau reload service, sau đó origin/public đều hồi phục bình thường và runtime host đã chứa đúng class/version mới.
### 2026-03-26 17:11
- [x] Đảo hướng chỉnh cột `Tiến độ` theo phản hồi mới: đổi `progress-cell` sang `vertical-align: top`, kéo stack tiến độ lên trên và bỏ cách canh đáy để thanh amber bám gần dòng `Upload` của timeline hơn.
- [x] Đồng bộ lại cả Jinja template và renderer live `backend/app/static/js/user_dashboard.js` với class `justify-start gap-2 pt-1`, tránh tình trạng polling trả row layout cũ.
- [x] Tăng cache-bust version lên `20260326-progress-top-align` để browser không giữ asset của lần chỉnh trước.
- [x] Rollout lại `user_dashboard.html` và `user_dashboard.js` lên host `82.197.71.6`, restart `youtube-upload-web.service`, verify origin/public health đều `200` sau khi service lên ổn định.
### 2026-03-26 17:19
- [x] Tiếp tục siết cột `Tiến độ` theo phản hồi mới: kéo cả cụm `Render/Upload` sát top hơn bằng cách giảm top padding của cell từ `py-4` xuống `pt-2 pb-4`, đồng thời bỏ top inset còn lại của stack.
- [x] Giữ spacing nội bộ đã siết của hai progress row (`gap-1`, `mt-0.5`) và đồng bộ chính xác cùng markup đó vào renderer live `backend/app/static/js/user_dashboard.js`.
- [x] Tăng cache-bust version lên `20260326-progress-cell-top-tight` để client nhận ngay asset mới sau rollout.
- [x] Deploy lại `user_dashboard.html` và `user_dashboard.js` lên host `82.197.71.6`, restart `youtube-upload-web.service`, verify listener `:8000`, origin health `200` và public health `200`.
### 2026-03-26 17:32
- [x] Chỉnh đúng trọng tâm theo ảnh phản hồi: giữ progress cell top-tight nhưng hạ riêng block `Upload` xuống thêm một nấc nhỏ bằng `mt-1` để thanh amber nằm gần dòng `Upload:` trong timeline hơn.
- [x] Đồng bộ lại cùng một thay đổi cho live renderer `backend/app/static/js/user_dashboard.js` để polling không làm hàng `Upload` bật ngược về vị trí cũ.
- [x] Tăng cache-bust version lên `20260326-progress-upload-lower` để browser lấy asset mới ngay sau deploy.
- [x] Rollout lại `user_dashboard.html` và `user_dashboard.js` lên host `82.197.71.6`, restart `youtube-upload-web.service`, verify listener `:8000`, origin health `200` và public health `200`.
### 2026-03-26 18:02
- [x] Tiếp tục fine-tune cột `Tiến độ` theo phản hồi mới: hạ cả cụm `Render/Upload` xuống thêm một nấc nhỏ bằng cách đổi cell từ `pt-2 pb-4` sang `pt-3 pb-3`, nhưng vẫn giữ offset riêng của block `Upload`.
- [x] Đồng bộ lại cùng thay đổi đó vào live renderer `backend/app/static/js/user_dashboard.js` để polling không kéo cụm tiến độ về padding cũ.
- [x] Tăng cache-bust version lên `20260326-progress-stack-lower` để client tải asset mới ngay.
- [x] Rollout lại `user_dashboard.html` và `user_dashboard.js` lên host `82.197.71.6`, restart `youtube-upload-web.service`, verify listener `:8000`, origin health `200` và public health `200`.
### 2026-03-26 18:05
- [x] Điều chỉnh tiếp theo phản hồi mới: hạ riêng từng hàng trong cột `Tiến độ` bằng offset cụ thể thay vì chỉ dời cả cell; `Render` được kéo xuống thêm mạnh, `Upload` kéo xuống nhẹ hơn.
- [x] Dùng inline `margin-top: 6px` cho cả block `Render` và `Upload` trong template và live renderer để kiểm soát chính xác hơn mức hạ từng hàng.
- [x] Tăng cache-bust version lên `20260326-progress-render-upload-offset` để client nhận asset mới ngay sau deploy.
- [x] Rollout lại `user_dashboard.html` và `user_dashboard.js` lên host `82.197.71.6`, restart `youtube-upload-web.service`, verify listener `:8000`, origin health `200` và public health `200`.
### 2026-03-26 18:09
- [x] Tinh chỉnh tiếp theo yêu cầu định lượng: tăng offset riêng của block `Render` lên `12px` và block `Upload` lên `8px`, thay vì dùng cùng một khoảng cách.
- [x] Đồng bộ lại đúng hai offset này vào live renderer `backend/app/static/js/user_dashboard.js` để polling không làm lệch hàng `Render/Upload`.
- [x] Tăng cache-bust version lên `20260326-progress-split-offsets` để client nhận asset mới ngay sau deploy.
- [x] Rollout lại `user_dashboard.html` và `user_dashboard.js` lên host `82.197.71.6`, restart `youtube-upload-web.service`, verify listener `:8000`, origin health `200` và public health `200`.
### 2026-03-26 18:12
- [x] Điều chỉnh lại theo phản hồi mới: giữ `Render` ở offset hiện tại `12px`, nhưng kéo riêng `Upload` lên gần `Render` hơn bằng cách giảm offset từ `8px` xuống `4px`.
- [x] Đồng bộ lại cùng thay đổi này vào live renderer `backend/app/static/js/user_dashboard.js` để polling không trả lại khoảng cách cũ giữa hai hàng.
- [x] Tăng cache-bust version lên `20260326-progress-upload-up` để client nhận asset mới ngay sau deploy.
- [x] Rollout lại `user_dashboard.html` và `user_dashboard.js` lên host `82.197.71.6`, restart `youtube-upload-web.service`, verify listener `:8000`, origin health `200` và public health `200`.
### 2026-03-26 18:20
- [x] Áp trực tiếp thông số người dùng chốt cho cột `Tiến độ`: `Render margin-top = 6px`, `Upload margin-top = 1px`.
- [x] Đồng bộ đúng hai giá trị này vào live renderer `backend/app/static/js/user_dashboard.js` để polling không ghi đè spacing vừa chỉnh.
- [x] Tăng cache-bust version lên `20260326-progress-user-final-offsets` để client nhận asset mới ngay sau deploy.
- [x] Rollout lại `user_dashboard.html` và `user_dashboard.js` lên host `82.197.71.6`, restart `youtube-upload-web.service`, verify listener `:8000`, origin health `200` và public health `200`.
