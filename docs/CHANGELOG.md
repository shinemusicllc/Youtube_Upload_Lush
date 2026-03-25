# Changelog

### 2026-03-25 15:10 - Backend Shell Contract Scaffold
- Added: Scaffold `backend/app/schemas.py`, `backend/app/store.py`, `backend/app/routers/api_user.py`, `backend/app/routers/api_admin.py` va `backend/AGENTS.md`.
- Changed: Chot seed contract in-memory JSON-friendly cho `user`, `worker`, `channel`, `channel grant`, `render job`, `oauth summary`.
- Fixed: Co san API shell response cho user/admin de backend boot nhanh ma chua can DB.
- Affected files: `backend/AGENTS.md`, `backend/app/__init__.py`, `backend/app/routers/__init__.py`, `backend/app/routers/api_admin.py`, `backend/app/routers/api_user.py`, `backend/app/schemas.py`, `backend/app/store.py`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap, chi them scaffold contract va seed store; risk chinh la contract se can tiep tuc dong bo khi persistence layer duoc gan vao.

### 2026-03-25 00:00 - Project Reset Bootstrap
- Added: Tao lai `docs/*` va root `AGENTS.md` cho workspace moi.
- Changed: Chot lai huong build moi theo HTML/template + FastAPI thay cho prototype React/Vite cu.
- Fixed: Khoi phuc project memory toi thieu de co the tiep tuc task theo rule du an.
- Affected files: `AGENTS.md`, `docs/*`
- Impact/Risk: Thap, chi anh huong rule/context de phuc vu rebuild sach.

### 2026-03-25 15:12 - User dashboard Jinja scaffold
- Added: Tao `backend/app/routers/web.py` va `backend/app/templates/user_dashboard.html` cho user page render bang FastAPI/Jinja.
- Changed: Chuyen KPI, channel select, connected channel list, render tabs, va render table sang seed context tu backend.
- Fixed: Loai hardcode du lieu lap lai trong UI user, giu `main.py` va cac router API khac nguyen trang.
- Affected files: `backend/app/routers/web.py`, `backend/app/templates/user_dashboard.html`, `docs/PROJECT_CONTEXT.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Trung binh, route web va template moi can duoc include vao app chinh de hien thi production.

### 2026-03-25 15:45 - HTML Template Backend Wiring
- Added: Tao `backend/app/static/js/user_dashboard.js` de noi channel select, tao job, tim kiem nhanh, cancel/delete job va start Google OAuth tu HTML shell.
- Changed: Chuyen `/` va `/app` sang render `backend/app/templates/user_dashboard.html`; xoa template user du thua va sua `backend/app/__init__.py`, `backend/AGENTS.md` cho phase moi.
- Fixed: Sua `api_user.py` de parse `schedule_time` tu format `dd/mm/yyyy HH:mm`, tu suy ra `source_mode`, va sua store de tr? user dashboard view model + job actions.
- Affected files: `backend/AGENTS.md`, `backend/app/__init__.py`, `backend/app/routers/api_user.py`, `backend/app/routers/web.py`, `backend/app/static/js/user_dashboard.js`, `backend/app/store.py`, `backend/app/templates/user_dashboard.html`, `docs/PROJECT_CONTEXT.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Trung binh; local HTML shell da noi end-to-end voi FastAPI, nhung OAuth Google moi o muc start URL/env contract va persistence van la in-memory.

### 2026-03-25 15:58 - Admin Elevated Shell Wiring
- Added: Tao Jinja admin shell va 4 page `user_index`, `worker_index`, `channel_index`, `render_index` de bam layout Elevated SaaS tu repo .NET cu.
- Changed: Chuyen `/admin` thanh redirect ve `/admin/user/index`; mount them static path `/admin-themes`, `/css`, `/js`; bo dashboard bootstrap tam.
- Fixed: Noi du lieu seed FastAPI vao bang admin `User / BOT / Channel / Render` va verify local browser cho ca 4 route.
- Affected files: `backend/app/main.py`, `backend/app/routers/web.py`, `backend/app/store.py`, `backend/app/templates/admin/_layout.html`, `backend/app/templates/admin/_summary_strip.html`, `backend/app/templates/admin/user_index.html`, `backend/app/templates/admin/worker_index.html`, `backend/app/templates/admin/channel_index.html`, `backend/app/templates/admin/render_index.html`, `docs/PROJECT_CONTEXT.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Trung binh; admin da len dung shell moi, nhung action modal/create-edit-delete hien van la stub UI va chua noi persistence/CRUD that.

### 2026-03-25 16:05 - Admin Parity Audit
- Added: Doi chieu route va thao tac admin FastAPI hien tai voi admin .NET cu theo 4 module `User / BOT / Channel / Render`.
- Changed: Khong co thay doi code runtime; cap nhat bo nho du an de chot trang thai parity hien tai.
- Fixed: Lam ro pham vi da co va con thieu, tranh hieu nham rang admin moi da noi day du workflow cu.
- Affected files: `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap; giup lap ke hoach noi backend dung thu tu uu tien thay vi tiep tuc sua UI tren nen logic chua day du.

### 2026-03-25 16:10 - Admin Parity Checklist
- Added: Tao `docs/ADMIN_PARITY_CHECKLIST.md` voi checklist parity chi tiet cho admin theo tung module va tung route/thao tac cua app cu.
- Changed: Chot ro cac muc `DONE/PARTIAL/TODO` va thu tu trien khai khuyen nghi de noi backend admin.
- Fixed: Bien danh gia parity tu mo ta hoi thoai thanh tai lieu thao tac duoc.
- Affected files: `docs/ADMIN_PARITY_CHECKLIST.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap; giup doi chieu tien do admin nhanh va tranh bo sot flow khi rebuild.

### 2026-03-25 16:18 - Final User UI Design Spec
- Added: Tao `docs/FINAL_USER_UI_ANALYSIS.md` de phan tich chi tiet `final_user_ui.html` thanh he token/layout/component/interactions co the dung lam spec.
- Changed: Viet lai `docs/UI_SYSTEM.md` theo huong `final_user_ui.html` la visual source of truth cho toan bo du an; cap nhat `docs/PROJECT_CONTEXT.md` va `docs/DECISIONS.md`.
- Fixed: Loai bo su lech huong trong tai lieu UI, tranh tiep tuc sua admin theo visual language cua app cu.
- Affected files: `docs/UI_SYSTEM.md`, `docs/FINAL_USER_UI_ANALYSIS.md`, `docs/PROJECT_CONTEXT.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap; khoa huong visual dung truoc khi tiep tuc refactor admin va noi logic parity.

### 2026-03-25 16:24 - UI Source Of Truth Clarification
- Added: Ghi chu ro reference SaaS moi chi la nguon polish phu cho shell details.
- Changed: Dieu chinh `docs/UI_SYSTEM.md` va `docs/FINAL_USER_UI_ANALYSIS.md` de giu `final_user_ui.html` lam source of truth chinh.
- Fixed: Loai bo nguy co doi nham visual source of truth khi tham chieu them mot shell SaaS mau.
- Affected files: `docs/UI_SYSTEM.md`, `docs/FINAL_USER_UI_ANALYSIS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap; giu huong thiet ke nhat quan truoc khi sua admin UI.

### 2026-03-25 16:37 - Admin Render UI Sync
- Added: Rewrite `backend/app/templates/admin/render_index.html` theo shell Tailwind/Lucide moi, giu nguyen field render co san.
- Changed: Bo toan bo Bootstrap/Stisla markup cu trong trang render list.
- Fixed: Dong bo trang render cua admin voi `final_user_ui.html` va `admin/_layout.html` moi.
- Affected files: `backend/app/templates/admin/render_index.html`
- Impact/Risk: Thap; chi tac dong layout render admin, khong doi contract backend.

### 2026-03-25 16:46 - Remove Deerflow Credit
- Added: Xoa footer credit `Created By Deerflow` khoi admin va user shell.
- Changed: Giao dien gom hon, khong con link credit o goc duoi.
- Fixed: Loai bo text credit con sot o 2 shell chinh.
- Affected files: `backend/app/templates/admin/_layout.html`, `backend/app/templates/user_dashboard.html`
- Impact/Risk: Thap; chi la polish UI, khong anh huong logic.
### 2026-03-25 17:05 - Admin UI Unified With Final User Visual
- Added: Chup headless screenshot cho 4 route admin de verify visual sau refactor, luu vao `artifacts/admin-*.png`.
- Changed: Refactor `admin/_layout.html`, `admin/_summary_strip.html`, `admin/user_index.html`, `admin/worker_index.html`, `admin/channel_index.html`, `admin/render_index.html` theo visual language cua `final_user_ui.html`.
- Fixed: Loai bo hoan toan shell/table Bootstrap-Stisla cu trong admin templates va doi badge/status ve class moi khong phu thuoc style cu.
- Affected files: `backend/app/store.py`, `backend/app/templates/admin/_layout.html`, `backend/app/templates/admin/_summary_strip.html`, `backend/app/templates/admin/user_index.html`, `backend/app/templates/admin/worker_index.html`, `backend/app/templates/admin/channel_index.html`, `backend/app/templates/admin/render_index.html`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`, `artifacts/admin-user-ui.png`, `artifacts/admin-worker-ui.png`, `artifacts/admin-channel-ui.png`, `artifacts/admin-render-ui.png`, `artifacts/admin-worker-ui-1920.png`, `artifacts/admin-render-ui-1920.png`
- Impact/Risk: Trung binh; admin da ve dung he visual chuan, nhung CRUD/action parity voi app cu van chua noi backend that.
### 2026-03-25 17:56 - User Management Parity Module 1
- Added: Noi backend FastAPI cho toan bo module `User Management` gom `index/create/delete/resetpassword/updatetelegram/manager/admins/managerbot` va them cac page/template admin user con thieu.
- Changed: Rewrite `backend/app/routers/web.py` theo contract field nhat quan, bo route stub/lech ten cu, va cap nhat `backend/app/store.py` de phuc vu dung context cho template admin user.
- Fixed: Sua loi 500 o cac route `create/manager/admins/managerbot`, sua sai lech template name/context key, va noi that action `create/edit/reset/toggle role/BOT mapping`.
- Affected files: `backend/app/routers/web.py`, `backend/app/store.py`, `backend/app/templates/admin/user_index.html`, `backend/app/templates/admin/user_create.html`, `backend/app/templates/admin/user_edit.html`, `backend/app/templates/admin/user_reset_password.html`, `backend/app/templates/admin/user_role_list.html`, `backend/app/templates/admin/user_manager_bot.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Trung binh; module user admin da chay du luong tren local, nhung persistence van la in-memory va action `Kenh` moi chi filter danh sach kenh seed o muc co ban.
### 2026-03-25 18:35 - BOT Management Parity Module 2
- Added: Noi backend FastAPI cho module `BOT Management` gom danh sach BOT, dialog `Sua/Xoa/Luong`, page `BOT cua user`, page `User cua BOT`, va route loc channel theo BOT.
- Changed: Mo rong `backend/app/store.py` de co context/manipulation cho BOT va rewrite `backend/app/templates/admin/worker_index.html` thanh man admin BOT dung visual system hien tai.
- Fixed: Bo trang thai `PARTIAL/TODO` cu cua module 2, cap nhat `docs/ADMIN_PARITY_CHECKLIST.md` sach encoding va chot module 1-2 ve trang thai dung thuc te.
- Affected files: `backend/app/routers/web.py`, `backend/app/store.py`, `backend/app/schemas.py`, `backend/app/templates/admin/worker_index.html`, `backend/app/templates/admin/bot_of_user.html`, `backend/app/templates/admin/user_of_bot.html`, `backend/app/templates/admin/channel_index.html`, `docs/ADMIN_PARITY_CHECKLIST.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Trung binh; module BOT da chay du luong tren local, nhung van phu thuoc seed in-memory va chua co auth/session manager that.
### 2026-03-25 19:10 - Channel Management Parity Module 3
- Added: Noi backend FastAPI cho module `Channel Management` gom `channel/index`, `channel/user`, `channel/bot`, `channel/users`, `updateuserchannel`, `adduser`, `updateprofile`, `export`, `delete`, `deleteajax`.
- Changed: Mo rong `backend/app/store.py` voi `channel_user_links`, helper build/filter context cho channel, va them `render/channel` de phuc vu action `DS Render` tu module channel.
- Fixed: Loai bo toan bo action stub tren man channel, sua lien ket `User -> Kenh` ve route dung, va cap nhat checklist parity de phan anh chinh xac module 3 da hoan tat.
- Affected files: `backend/app/routers/web.py`, `backend/app/store.py`, `backend/app/templates/admin/channel_index.html`, `backend/app/templates/admin/channel_user.html`, `backend/app/templates/admin/channel_users.html`, `backend/app/templates/admin/render_index.html`, `backend/app/templates/admin/user_index.html`, `docs/ADMIN_PARITY_CHECKLIST.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Trung binh; module channel da chay du luong tren local va cross-link sang render hoat dong, nhung persistence van la in-memory va man render detail/delete all chua lam.
### 2026-03-25 19:35 - Render Management Parity Module 4
- Added: Noi backend FastAPI cho module `Render Management` gom `render/index`, `render/channel`, `render/renderinfo`, `render/delete`, va bo sung `render/deletejob` de hoan tat action tren bang.
- Changed: Cap nhat `backend/app/store.py` voi `render_delete_meta` that, helper tim job/user cua job, va context detail render bam dung flow readonly cua app cu.
- Fixed: Nut `Chi tiet`, `Xoa tung job`, `Xoa tat ca du lieu` tren man render khong con la stub; badge `xoa lan cuoi` khong con la du lieu gia lap.
- Affected files: `backend/app/routers/web.py`, `backend/app/store.py`, `backend/app/templates/admin/render_index.html`, `backend/app/templates/admin/render_detail.html`, `docs/ADMIN_PARITY_CHECKLIST.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Trung binh; module render da dat parity chinh cho admin local, nhung auth/role/session manager filter that va persistence van chua duoc noi.

### 2026-03-25 20:25 - Shared Admin Infrastructure Module 5
- Added: Them `backend/app/auth.py`, `backend/app/templates/admin/login.html`, route login/logout/session update, va contract `api_admin` theo module.
- Changed: `backend/app/main.py` dung `SessionMiddleware`; `backend/app/routers/web.py` gate admin theo role/session va manager scope; `backend/app/store.py` persist state xuong `backend/app/data/app_state.db`; `backend/app/templates/admin/_layout.html` doi sang logout form that; `backend/app/templates/admin/user_create.html` khoa manager binding khi manager tao user.
- Fixed: Admin shell khong con mo tu do khi chua dang nhap, manager filter duoc nho qua session, va state admin/user/job khong con mat sau restart.
- Affected files: `backend/requirements.txt`, `backend/app/auth.py`, `backend/app/main.py`, `backend/app/routers/web.py`, `backend/app/routers/api_admin.py`, `backend/app/store.py`, `backend/app/templates/admin/_layout.html`, `backend/app/templates/admin/login.html`, `backend/app/templates/admin/user_create.html`, `docs/PROJECT_CONTEXT.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`, `docs/ADMIN_PARITY_CHECKLIST.md`
- Impact/Risk: Trung binh; module 5 da hoan tat cho local bootstrap, nhung persistence hien van la cau noi SQLite tam thoi truoc khi chuyen sang Postgres + Redis.
### 2026-03-25 21:05 - Git Bootstrap And Initial Push
- Added: Khoi tao Git repo tai workspace `D:\\Youtube_BOT_UPLOAD`, cau hinh remote `origin` tro den `https://github.com/shinemusicllc/Youtube_Upload_Lush.git`, va tao initial commit cho snapshot hien tai.
- Changed: Cap nhat `.gitignore` de loai tru SQLite state, upload local, cache va artifact phat sinh trong qua trinh chay local.
- Fixed: Bo file `backend/data/app_state.db` va `backend/data/uploads/` ra khoi index truoc khi push de tranh day state test len remote.
- Affected files: `.gitignore`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap; repo da duoc day len GitHub thanh cong, nhung commit dau tien hien van bao gom thu muc tham chieu `YoutubeBOTUpload-master` vi backend hien tai con dua vao asset va source tham chieu tu repo cu.

### 2026-03-25 19:47 - Repo sync to root and local app startup
- Added: copied repo content into workspace root and created `backend\venv` with installed dependencies.
- Changed: local app now runs from root workspace via `uvicorn` on `127.0.0.1:8000`.
- Fixed: validated startup using `/api/health`.
- Affected files: `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: app is runnable locally; root still contains two extra directories because delete commands are blocked by policy.
### 2026-03-25 22:05 - Real Google OAuth Connect Flow
- Added: implemented real Google OAuth callback flow with `state` validation, token exchange, `userinfo`, `channels.list(mine=true)`, and local `.env.example` contract.
- Changed: user dashboard now accepts notice banners from OAuth callback; bootstrap channel list is filtered by current user; app auto-loads root `.env` before building the store.
- Fixed: `Kết nối Google` no longer stops at auth URL scaffold and now creates/updates a real connected channel record with `refresh token` metadata in SQLite bootstrap.
- Affected files: `backend/app/auth.py`, `backend/app/routers/api_user.py`, `backend/app/routers/web.py`, `backend/app/schemas.py`, `backend/app/store.py`, `backend/app/templates/user_dashboard.html`, `backend/requirements.txt`, `.env.example`, `docs/PROJECT_CONTEXT.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: trung binh; OAuth connect da chay that tren local bootstrap, nhung `refresh token` van dang luu trong SQLite local va can duoc dua sang secret storage/encryption truoc khi production.
### 2026-03-25 22:25 - Admin KPI Strip Alignment
- Added: bo sung icon va nhan phu cho KPI strip admin de dong bo voi pattern KPI cua user workspace.
- Changed: `summary_strip` admin gio tra ve icon, accent text va value color class; partial `admin/_summary_strip.html` render du label, icon, so lon va nhan phu duoi so tren tat ca tab admin.
- Fixed: KPI admin khong con bi thieu icon/chu phu, va KPI `Đang Upload` khi bang `0` hien so mau den de de nhin hon.
- Affected files: `backend/app/store.py`, `backend/app/templates/admin/_summary_strip.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: thap; chi thay doi presentation layer dung chung cho cac tab admin, khong doi route hay contract nghiep vu.
### 2026-03-25 22:45 - Admin Manager Picker And Avatar Palette
- Added: tao manager picker dung chung voi search input, checkbox multi-select va hidden query sync cho cac tab admin co filter manager.
- Changed: doi user avatar chu sang palette mau on dinh theo ten; thay `select multiple` manager cu bang component picker bam visual app hien tai.
- Fixed: bo loc manager khong con la o `select` tho va co the search/chon nhieu manager de loc nhu workflow cu; avatar user khong con xam dong loat.
- Affected files: `backend/app/store.py`, `backend/app/templates/admin/_layout.html`, `backend/app/templates/admin/_manager_picker.html`, `backend/app/templates/admin/user_index.html`, `backend/app/templates/admin/worker_index.html`, `backend/app/templates/admin/channel_index.html`, `backend/app/templates/admin/render_index.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: trung binh-thap; thay doi UI layer va JS dung chung cho 4 tab admin, da duoc smoke test route sau login va compile local.
### 2026-03-25 22:55 - Admin KPI Accent Badges
- Added: them badge nho cho nhan phu KPI admin nhu `Online`, `Active`, `Accounts`, `Render`, `Upload`, `Queue`.
- Changed: `summary_strip` admin gio cap them `accent_badge_class`; partial KPI render nhan phu dang chip nhe thay vi text thuong.
- Fixed: nhan phu KPI admin de scan hon va dong bo hon voi y tuong badge mau mau user yeu cau.
- Affected files: `backend/app/store.py`, `backend/app/templates/admin/_summary_strip.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: thap; chi thay doi presentation layer o partial KPI admin dung chung.
### 2026-03-25 23:05 - Manager Picker Tag Flow
- Added: manager picker gio hien selected manager thanh tag trong trigger, moi tag co nut `x` de bo nhanh va co tag/option `Xóa tất cả` khi chon nhieu.
- Changed: bo logic summary text `n manager da chon`, chuyen sang flow tag-style de sat hon voi app cu va giam thao tac bo chon.
- Fixed: manager da chon khong con bi an sau summary text, va viec bo chon khong can mo panel roi bo tick thu cong tung manager nua.
- Affected files: `backend/app/templates/admin/_manager_picker.html`, `backend/app/templates/admin/_layout.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: trung binh-thap; thay doi UI/JS dung chung cho 4 tab admin, da duoc smoke test route sau login va compile local.
### 2026-03-25 16:45 - Audit old render flow
- Added: Tai lieu noi bo ve luong render that cua app .NET cu tu luc tao job den luc bot cap nhat progress/complete.
- Changed: Lam ro app cu dang di theo huong `concat/remux/copy` voi FFmpeg thay vi full re-encode cho case loop video + nhac.
- Fixed: Loai bo nham lan truoc do giua "render 4K nang" va "ghep loop 4K" bang cach doi chieu truc tiep code worker cu.
- Affected files: `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Giup kien truc moi giu duoc fast path nhe tai nguyen, nhung chua thay doi code production.
### 2026-03-25 23:58 - Resumable Upload And Worker Scaffold
- Added: Upload session API cho local upload resumable, worker register/heartbeat API, worker agent Python, infra deploy skeleton va env production example.
- Changed: User form local upload tu cho file binary di thang vao `POST /user/jobs` sang huong upload chunk truoc, tao job sau bang asset refs.
- Fixed: Fallback local upload khong con `await file.read()` toan bo file vao memory va khong con de overwrite theo `slot-filename`.
- Affected files: `backend/app/schemas.py`, `backend/app/store.py`, `backend/app/routers/api_user.py`, `backend/app/routers/api_worker.py`, `backend/app/main.py`, `backend/app/routers/__init__.py`, `backend/app/static/js/user_dashboard.js`, `backend/app/templates/user_dashboard.html`, `.env.production.example`, `.dockerignore`, `infra/**`, `workers/**`, `scripts/**`, `AGENTS.md`, `docs/PROJECT_CONTEXT.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Da co ban thu nghiem host + worker chạy thật, nhung OAuth production va HTTPS/domain van chua cau hinh nen chua san sang production hoàn chỉnh.
### 2026-03-26 00:20 - Worker Claim Loop
- Added: Worker API cho `claim`, `progress`, `complete`, `fail`; worker agent loop co `simulate mode` opt-in.
- Changed: Job record duoc bo sung metadata claim/lease/runtime de control plane quan ly duoc worker state that.
- Fixed: Host thu nghiem duoc redeploy an toan va da don process du cua chinh app tren `:8010`, giu lai duy nhat runtime can thiet tren `:8000`.
- Affected files: `backend/app/schemas.py`, `backend/app/store.py`, `backend/app/routers/api_worker.py`, `workers/agent/main.py`, `scripts/bootstrap_worker.sh`, `docs/PROJECT_CONTEXT.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Da co queue contract worker-side de mo rong thanh render worker that, nhung hien tai worker chua download/render/upload media that; `simulate mode` van dang tat mac dinh tren server.
### 2026-03-26 00:33 - attach_shared_domain_route
- Added: Them route server-side cho `ytb.jazzrelaxation.com` vao Caddy shared tren host `82.197.71.6`.
- Changed: Cap nhat env runtime cua app host sang domain moi (`APP_BASE_URL`, `APP_DOMAIN`, `GOOGLE_REDIRECT_URI`) va restart uvicorn process.
- Fixed: Xac nhan reverse proxy noi bo tu Caddy container ve app Python qua `172.17.0.1:8000` hoat dong dung.
- Affected files: `/opt/spoticheck/app/deploy/Caddyfile`, `/opt/youtube-upload-lush/.env`, `docs/PROJECT_CONTEXT.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Domain da san sang o phia server nhung van chua public/HTTPS that cho den khi DNS `ytb.jazzrelaxation.com` tro ve `82.197.71.6`.
### 2026-03-26 01:40 - unlock_worker_media_pipeline_scaffold
- Added: Worker-authenticated local asset download route, worker modules `config/control_plane/downloader/ffmpeg_pipeline/job_runner`, va safety gate `WORKER_EXECUTE_JOBS`.
- Changed: Worker service chay qua `python -m workers.agent.main`, worker requirements co them `gdown`, va host/worker deploy da duoc cap nhat len code moi.
- Fixed: Domain `ytb.jazzrelaxation.com` da len cert Let's Encrypt that; worker deploy khong con bi nuot queue demo vi execution mac dinh dang khoa.
- Affected files: `backend/app/schemas.py`, `backend/app/store.py`, `backend/app/routers/api_worker.py`, `workers/agent/*`, `workers/__init__.py`, `infra/systemd/youtube-upload-worker.service`, `scripts/bootstrap_worker.sh`, `docs/PROJECT_CONTEXT.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Pipeline render that da co code va da len VPS, nhung chua duoc bat thuc thi thuc te cho queue; buoc tiep theo can bat `WORKER_EXECUTE_JOBS=true` co chu dich va noi phan YouTube OAuth upload.
### 2026-03-26 01:40 - enable_worker01_execution_gate
- Added: Rollout that cho `worker-01` bang `WORKER_EXECUTE_JOBS=true` sau khi don queue demo cua worker nay.
- Changed: Queue tren host da duoc don job demo `job-379e626e`; `worker-01` chuyen sang che do san sang xu ly that, `worker-02` van giu che do an toan.
- Fixed: Loai bo rui ro `worker-01` an nham job Drive placeholder ngay luc bat execution.
- Affected files: `docs/PROJECT_CONTEXT.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: He thong hien dang co 1 worker that (`worker-01`) va 1 worker standby (`worker-02`); buoc tiep theo nen tao 1 job test that de theo doi luong `download -> render`.

### 2026-03-26 02:00 - Fix Google Drive asset name collision on worker
- Added: Verify that pipeline with real Drive links now completes end-to-end on `worker-01` after downloader fix.
- Changed: Worker downloader now stores each asset in its own slot directory instead of reusing one flat temporary filename.
- Fixed: Google Drive links ending in `/view` no longer cause `audio_loop` to overwrite `video_loop`, eliminating false `Asset video_loop không có video stream` failures.
- Affected files: `workers/agent/downloader.py`, `docs/PROJECT_CONTEXT.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Trung binh-thap; fixes a real production blocker for Drive sources and has been validated with a successful 60-second output on `worker-01`.

### 2026-03-26 20:15 - Add gated YouTube OAuth upload stage
- Added: Worker-authenticated control plane route for YouTube upload target and new worker module `youtube_uploader.py` using refresh-token exchange plus resumable chunk upload.
- Changed: Worker config now supports `WORKER_UPLOAD_TO_YOUTUBE` and `YOUTUBE_UPLOAD_CHUNK_BYTES`; rollout was applied to host and both workers with upload gate explicitly kept off.
- Fixed: Post-deploy regression caused by missing redeploy of `downloader.py` was corrected, and render smoke `job-e667631b` completed successfully afterward.
- Affected files: `backend/app/routers/api_worker.py`, `backend/app/schemas.py`, `backend/app/store.py`, `workers/agent/config.py`, `workers/agent/control_plane.py`, `workers/agent/job_runner.py`, `workers/agent/youtube_uploader.py`, `workers/agent/downloader.py`, `scripts/bootstrap_worker.sh`, `docs/PROJECT_CONTEXT.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Trung binh; code path upload YouTube da san sang de bat sau khi co OAuth that, con render pipeline hien tai van giu an toan nho gate `WORKER_UPLOAD_TO_YOUTUBE=false`.

### 2026-03-26 20:25 - Create OAuth branding logo asset
- Added: New square brand assets for Google OAuth consent screen in both `SVG` and `PNG 120x120` formats.
- Changed: Reused the exact sidebar mark and adapted it to a neutral square canvas for better visibility on OAuth consent UI.
- Fixed: Branding setup now has a ready-to-upload logo file instead of relying on inline SVG embedded in templates.
- Affected files: `backend/app/static/brand/youtube-upload-lush-oauth-logo.svg`, `backend/app/static/brand/youtube-upload-lush-oauth-logo-preview.html`, `backend/app/static/brand/youtube-upload-lush-oauth-logo.png`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap; only adds branding assets and setup guidance, no runtime behavior change.

### 2026-03-26 20:40 - Add real delete action for user channels
- Added: User-facing delete API for connected channels and frontend action binding on the `My Channel` cards.
- Changed: OAuth scope request now includes `youtube.readonly` in addition to `youtube.upload` so channel lookup can succeed after reconnect.
- Fixed: The existing hidden `Xóa` affordance on channel cards now performs a real delete instead of being a dead UI element.
- Affected files: `backend/app/store.py`, `backend/app/routers/api_user.py`, `backend/app/templates/user_dashboard.html`, `backend/app/static/js/user_dashboard.js`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Trung binh-thap; deleting a connected channel will also remove jobs attached to that channel, and users must reconnect Google once to refresh scopes.

### 2026-03-26 21:05 - Harden host web runtime with systemd
- Added: `infra/systemd/youtube-upload-web.service` de quan ly web app bang `systemd` tren shared host.
- Changed: `scripts/bootstrap_host.sh` ho tro `DEPLOY_MODE=systemd` va cai host web service thay cho chi start process tam.
- Fixed: `ytb.jazzrelaxation.com` het loi `502` do origin `:8000` duoc supervisor giu song va tu restart.
- Affected files: `infra/systemd/youtube-upload-web.service`, `scripts/bootstrap_host.sh`, `infra/AGENTS.md`, `docs/PROJECT_CONTEXT.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap-trung binh; host app on dinh hon sau deploy/reboot, nhung cac lan deploy toi can dong bo service file nay cung code va `.venv` tren `/opt/youtube-upload-lush`.

### 2026-03-26 21:15 - Clean user channel row and transient OAuth notice
- Added: Client-side cleanup cho `notice` va `notice_level` trong URL sau khi user dashboard render xong.
- Changed: Channel card ben user duoc sap lai theo row action dung visual system, bo kieu nut xoa chen layout o mep phai.
- Fixed: Banner loi OAuth cu khong con bam theo URL qua moi lan refresh; channel row khong con nguy co tran viewport khi co action xoa.
- Affected files: `backend/app/templates/user_dashboard.html`, `backend/app/static/js/user_dashboard.js`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap; chi anh huong layout/hanh vi dashboard user, backend contract xoa channel giu nguyen.

### 2026-03-26 21:25 - Push current code and audit VPS sync
- Added: Commit `768cc1a` tren `main` da duoc push len GitHub.
- Changed: Co them bao cao doi chieu hash de danh gia muc do dong bo giua local, GitHub, host va 2 worker VPS.
- Fixed: Loai bo nghi van “da push chua” bang cach xac nhan `origin/main` trung local HEAD; dong thoi chi ro file nao tren VPS con lech de sync co chu dich.
- Affected files: `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap; khong doi runtime, chi cap nhat git state va ket qua audit dong bo deployment.
