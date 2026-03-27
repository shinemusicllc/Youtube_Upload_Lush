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

### 2026-03-26 21:35 - Sync host and worker-02 to current main
- Added: Rollout co chu dich cac file con lech len host app va `worker-02`.
- Changed: Host restart lai `youtube-upload-web.service`; `worker-02` restart lai `youtube-upload-worker.service` nhung van giu safety gate tat.
- Fixed: Trang thai deployment tren VPS da dong bo voi local/GitHub o cac file da audit, khong con tinh trang host va worker-02 lech version.
- Affected files: `backend/app/store.py`, `backend/app/routers/api_user.py`, `workers/agent/config.py`, `workers/agent/control_plane.py`, `workers/agent/job_runner.py`, `scripts/bootstrap_worker.sh`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap-trung binh; restart service co nhiep ngat ngan, nhung health/public va worker state da duoc verify sau sync.

### 2026-03-26 21:50 - Add public verification pages
- Added: Public homepage, privacy policy page, and terms page for Google OAuth brand verification.
- Changed: Root route now renders a public application profile instead of redirecting anonymous visitors directly to `/login`.
- Fixed: `https://ytb.jazzrelaxation.com/` and legal URLs now return basic HTML pages that Google reviewers can access without authentication.
- Affected files: `backend/app/routers/web.py`, `backend/app/templates/public_home.html`, `backend/app/templates/public_legal.html`, `docs/PROJECT_CONTEXT.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap; thay doi hanh vi public root route de uu tien brand verification, nhung workflow login/app cua user van giu nguyen qua `/login` va `/app`.

### 2026-03-26 21:58 - Move public homepage to /home
- Added: Public verification homepage is now available at `/home`.
- Changed: Root route returns to the previous login-first behavior, while legal pages keep linking to the public `/home`.
- Fixed: Trang goc cua domain lai de dang cho van hanh dang nhap, trong khi Google verification van co trang public rieng de dung.
- Affected files: `backend/app/routers/web.py`, `docs/PROJECT_CONTEXT.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap; can cap nhat lai URL homepage trong Google Cloud tu `/` sang `/home`.
### 2026-03-26 22:10 - Local bootstrap after latest pull
- Added: Tao `.venv` local, cai dependency cho `backend` va `workers/agent`, va tao `.env` dev toi thieu de boot control plane local.
- Changed: Restart backend local bang `.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000` thay cho process Python cu.
- Fixed: Trang thai local sau pull khong con bi lech process/runtime cu; `GET /api/health`, `GET /app`, `GET /admin/login` deu tra `200`.
- Affected files: `.env`, `.gitignore`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap; thay doi chi phuc vu runtime local, khong tac dong deployment VPS. Worker local chua duoc detach do policy moi truong chan launch background co env tuy bien.
### 2026-03-26 22:25 - Polish channel card and sidebar wordmark
- Added: Them CSS hover/focus transition cho `My Channel` row de badge ket noi va nut xoa thay nhau o cung vi tri ben phai.
- Changed: Rut gon wordmark sidebar user tu `Youtube Upload Lush` ve `Youtube Upload`.
- Fixed: Nut xoa khong con lo san trong danh sach channel; giao dien quay lai pattern cu de gon hon va de scan hon.
- Affected files: `backend/app/templates/user_dashboard.html`, `backend/app/store.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap; chi anh huong user UI va text shell, khong doi contract backend.
### 2026-03-26 22:40 - Rename local user shell brand to Upload Youtube
- Added: Khong co thay doi chuc nang moi; cap nhat ten brand tren shell local de dong bo voi cach goi san pham hien tai.
- Changed: `dashboard.page_title` va `dashboard.app_name` trong seed/store doi tu `Youtube Upload` sang `Upload Youtube`.
- Fixed: Sidebar wordmark va `<title>` trang user khong con lech voi ten app ma user chot de dung trong local OAuth flow.
- Affected files: `backend/app/store.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap; chi doi text hien thi, khong anh huong contract backend.
### 2026-03-26 23:05 - Fix local OAuth callback and channel avatar rendering
- Added: Dua `avatar_url` vao user dashboard view-model de card `My Channel` co the render anh profile that cua kenh OAuth.
- Changed: Callback `/auth/google/callback` duoc harden de khong vo trang trang khi co loi ngoai `ValueError`.
- Fixed: Sua bug `complete_google_oauth()` thieu `return` gay `500` sau khi luu channel; loai bo nguyen nhan goc cua notice `invalid_grant` xuat hien sau khi user reload callback URL da dung mot lan.
- Affected files: `backend/app/store.py`, `backend/app/routers/web.py`, `backend/app/templates/user_dashboard.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap-trung binh; anh huong flow OAuth local va user dashboard, da verify local compile va HTML render avatar that.
### 2026-03-26 23:12 - Render avatar thật trong dropdown chọn kênh
- Added: Truyen `avatar_url` vao seed cua `dashboard.channels` de dropdown channel select co du lieu anh profile that.
- Changed: Trigger va option trong `channel-select` uu tien render `<img>` khi channel co `avatar_url`, fallback ve initials khi khong co anh.
- Fixed: Khu `Chọn kênh` khong con lech voi `My Channel`; kenh OAuth moi gio hien dung avatar profile.
- Affected files: `backend/app/templates/user_dashboard.html`, `backend/app/static/js/user_dashboard.js`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap; chi doi presentation cua dropdown chon kenh, khong anh huong contract job/OAuth.
### 2026-03-26 23:18 - Add subtle depth to channel avatars
- Added: Class `channel-avatar-media` de avatar image co border va shadow nhe.
- Changed: Avatar anh that trong `My Channel` va dropdown `Chọn kênh` dung cung treatment de dong nhat visual.
- Fixed: Avatar kenh khong con qua flat so voi card va input xung quanh.
- Affected files: `backend/app/templates/user_dashboard.html`, `backend/app/static/js/user_dashboard.js`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap; chi anh huong presentation cua avatar image.
### 2026-03-26 23:28 - Replace job icon with loop media preview
- Added: Preview resolution cho `video_loop`, ho tro local asset preview route va Google Drive thumbnail khi URL co `file id`.
- Changed: Bang render user uu tien render preview image/video trong cot asset thay vi icon placeholder.
- Fixed: Hang job khong con chi hien icon generic; job seed cu cung co fallback preview tu `thumbnail_url` hoac `channel_avatar_url`.
- Affected files: `backend/app/store.py`, `backend/app/routers/api_user.py`, `backend/app/templates/user_dashboard.html`, `backend/app/static/js/user_dashboard.js`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap-trung binh; co them route preview local va logic suy dien preview, da verify local compile va HTML render.
### 2026-03-26 23:36 - Link public channel trong My Channel
- Added: `public_url` cho tung kenh trong dashboard view-model de UI mo kenh public YouTube truc tiep.
- Changed: Card `My Channel` tach dong meta thanh `channel_id` linkable va `bot_label` plain text.
- Fixed: Khong can deep-link YouTube Studio nua; tranh mo sai account theo browser profile khac.
- Affected files: `backend/app/store.py`, `backend/app/templates/user_dashboard.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap; chi anh huong hanh vi click trong card kenh, khong doi flow OAuth/render.
### 2026-03-26 23:44 - Chuyen thumbnail job sang ti le 4:3
- Added: Khong co chuc nang moi; thong nhat khung preview job theo ti le ngang 4:3.
- Changed: O media cua bang render user doi tu khung vuong `w-20 h-20` sang `w-28 aspect-[4/3]` cho preview image/video va fallback state.
- Fixed: Giam khoang trong ben trai cua thumbnail, preview loop video dung ty le hop ly hon voi noi dung ngang.
- Affected files: `backend/app/templates/user_dashboard.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap; chi doi layout presentation cua danh sach render, khong anh huong data/job logic.
### 2026-03-27 00:02 - Harden user notice banner
- Added: Nut dong `x` va auto-hide timer cho notice tren user dashboard.
- Changed: Text OAuth notice chuyen sang tieng Viet co dau an toan theo escape/entity de tranh loi encoding file.
- Fixed: User khong can refresh de notice bien mat; callback OAuth khong con hien message khong dau.
- Affected files: `backend/app/routers/web.py`, `backend/app/templates/user_dashboard.html`, `backend/app/static/js/user_dashboard.js`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap; chi tac dong UI notice va redirect message sau OAuth, khong doi logic ket noi kenh.
### 2026-03-27 00:10 - Strengthen channel avatars and wire render-list avatars
- Added: `channel_avatar_url` vao view-model `render_jobs` de bang render co the dung avatar that cua kenh.
- Changed: `channel-avatar-media` co stroke/shadow ro hon de tach khoi nen trang; cot kenh trong `list render` uu tien `<img>` thay cho initials.
- Fixed: Avatar kenh khong con bi chim tren UI sang, va bang render user khong con lech voi `My Channel`/dropdown ve du lieu avatar.
- Affected files: `backend/app/store.py`, `backend/app/templates/user_dashboard.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap; chi doi presentation va data binding avatar trong user dashboard, khong anh huong flow job/OAuth.
### 2026-03-27 00:19 - Rollout user dashboard polish to host
- Added: Backup timestamp cho cac file runtime truoc khi sync len host shared.
- Changed: Host `ytb.jazzrelaxation.com` nhan ban moi cua `web.py`, `api_user.py`, `store.py`, `user_dashboard.html`, `user_dashboard.js`.
- Fixed: Ban public tren VPS da co notice dismiss/auto-hide va avatar that trong `list render`, khop voi local vua polish.
- Affected files: `backend/app/routers/api_user.py`, `backend/app/routers/web.py`, `backend/app/static/js/user_dashboard.js`, `backend/app/store.py`, `backend/app/templates/user_dashboard.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Trung binh-thap; da rollout len production-like host va restart service web, health check host/domain deu xanh.
### 2026-03-27 00:27 - Align My Channel with brand blue
- Added: Khong co logic moi; chi dong bo visual token cho khu `My Channel`.
- Changed: Icon block, hover border va badge `Đã kết nối` cua `My Channel` doi tu `emerald` sang `brand/blue`.
- Fixed: Khu `My Channel` khong con lech tone mau so voi phan con lai cua app sau khi deploy len host.
- Affected files: `backend/app/templates/user_dashboard.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap; chi doi mau UI va da rollout len host shared thanh cong.
### 2026-03-27 00:34 - Show channel id/meta in selected dropdown state
- Added: `channel-select-meta` trong trigger cua dropdown `Chọn kênh`, populated tu `data-meta` cua tung option.
- Changed: JS channel select render them dong meta/`channel_id` duoi ten kenh sau khi user chon, giu avatar va layout cu.
- Fixed: Trang thai da chon cua dropdown khong con mat `channel_id`, dong bo voi item hien trong menu list.
- Affected files: `backend/app/templates/user_dashboard.html`, `backend/app/static/js/user_dashboard.js`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap; chi doi presentation cua channel dropdown va da rollout len host shared.
### 2026-03-27 00:42 - Restore emerald status styling and fix sticky delete state
- Added: Avatar trong `My Channel` cung tro thanh public link, giong ten kenh va `channel_id`.
- Changed: Icon block va badge `Đã kết nối` cua `My Channel` doi ve `emerald`, trong khi row hover border van giu `brand/blue`.
- Fixed: Bo `:focus-within` khoi row action de click public link khong con de lai state hien icon xoá khi user quay lai tab.
- Affected files: `backend/app/templates/user_dashboard.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap; chi doi presentation/hanh vi hover-focus trong card kenh va da rollout len host shared.
### 2026-03-27 00:49 - Roll back selected-channel trigger meta
- Added: Khong co logic moi; day la rollback presentation cho dropdown `Chọn kênh`.
- Changed: Trigger duoc tra ve layout cu chi hien avatar + ten kenh, khong render `channel_id/meta` trong trang thai da chon.
- Fixed: Loai bo layout vo trigger va hien tuong dropdown “bay vao trong” sau lan sua gan nhat.
- Affected files: `backend/app/templates/user_dashboard.html`, `backend/app/static/js/user_dashboard.js`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Thap; rollback UI nho va da rollout len host shared.
### 2026-03-26 10:14 - fix_channel_select_trigger_avatar_on_vps
- Added: Class rieng channel-select-trigger-avatar cho avatar o trigger cua dropdown Ch?n K�nh.
- Changed: Tang query version cua user_dashboard.js de invalid cache browser tren VPS.
- Fixed: Trigger dropdown tren VPS gio uu tien render avatar that thay vi bi fallback sang initials do JS selector/cache.
- Affected files: backend/app/templates/user_dashboard.html, backend/app/static/js/user_dashboard.js.
- Impact/Risk: Tac dong hep trong user dashboard; yeu cau browser nap file JS moi, co the can hard refresh neu tab giu cache qua sat.
### 2026-03-26 10:34 - improve_channel_select_meta_and_local_upload_flow
- Added: D�ng meta channel_id nh? du?i t�n trong trigger Ch?n K�nh.
- Changed: C?m upload local d?i sang button th?t c� state UI ri�ng thay cho label icon tinh.
- Fixed: Click icon upload local gi? m? file picker ?n d?nh; upload local b?t d?u ngay sau khi ch?n file v� c� th? h?y/remove ngay tr�n n�t.
- Affected files: backend/app/templates/user_dashboard.html, backend/app/static/js/user_dashboard.js.
- Impact/Risk: C� thay d?i h�nh vi upload local tr�n user dashboard; n?u tab cu gi? cache JS th� c?n refresh d? nh?n flow m?i.
### 2026-03-26 10:42 - switch_upload_progress_center_to_lucide
- Added: Lucide icons cho tam vong progress local upload (x, check).
- Changed: Bo render text fallback trong JS cho center state cua upload action.
- Fixed: Cum upload local dong bo icon system voi phan con lai cua app.
- Affected files: backend/app/templates/user_dashboard.html, backend/app/static/js/user_dashboard.js.
- Impact/Risk: Tac dong hep trong user dashboard; can refresh tab de nap lai template moi.
### 2026-03-26 10:50 - make_uploading_progress_red
- Changed: State uploading cua upload action doi tu brand blue sang red/rose.
- Fixed: Tin hieu UI cho hanh dong huy upload ro rang hon khi dang co progress.
- Affected files: backend/app/templates/user_dashboard.html.
- Impact/Risk: Tac dong nho, chi anh huong mau cua local-upload progress state tren user dashboard.
### 2026-03-26 11:15 - Fix timezone schedule claim and empty local asset upload
- Added: `APP_TIMEZONE` support with `Asia/Saigon` default in `backend/app/store.py` for consistent app-local timestamps.
- Changed: Queue refresh, worker claim, progress, completion, OAuth timestamping, upload session timing, and admin/user timestamp writes now use shared app-local time helpers.
- Fixed: Local job creation no longer treats empty file inputs or blank `*_asset_id` values as real assets; this prevents zero-byte placeholder files for optional `intro/outro` slots.
- Affected files: `backend/app/store.py`, `backend/app/routers/api_user.py`.
- Impact/Risk: Existing broken jobs created before the fix remain broken and should be recreated; new jobs should schedule/claim correctly on VPS and avoid empty local assets.
### 2026-03-26 11:22 - Diagnose completed render without YouTube upload
- Added: Host-side diagnosis for real job `job-777d9f0a` using persisted runtime state.
- Changed: No code changes in this step.
- Fixed: Clarified that `completed` currently means render finished and local output exists, not that YouTube upload succeeded.
- Affected files: `docs/WORKLOG.md`, `docs/CHANGELOG.md`.
- Impact/Risk: User-facing status can be misunderstood until upload phase is enabled and surfaced separately.
### 2026-03-26 11:30 - Confirm upload blocker is worker access, not control plane
- Added: Verified host has Google OAuth client secrets and the connected channel keeps a valid refresh token in persisted state.
- Changed: No runtime code change in this step.
- Fixed: Narrowed the real blocker for YouTube upload rollout to worker infrastructure access.
- Affected files: `docs/WORKLOG.md`, `docs/CHANGELOG.md`.
- Impact/Risk: Control plane is ready, but upload cannot be enabled on `worker-01` until SSH access or equivalent configuration access to that worker is available.
### 2026-03-26 11:38 - Enable real YouTube upload on worker-01
- Added: Real YouTube upload rollout on `worker-01`, including successful upload of an existing rendered output using the worker's production upload path.
- Changed: `CONTROL_PLANE_URL` on both workers now uses `https://ytb.jazzrelaxation.com`; `worker-01` has `WORKER_UPLOAD_TO_YOUTUBE=true`, `worker-02` remains upload-disabled standby.
- Fixed: Closed the gap where jobs could reach `completed` after render but never enter the YouTube upload phase.
- Affected files: `docs/PROJECT_CONTEXT.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`, runtime env `/etc/youtube-upload-worker.env` on both workers.
- Impact/Risk: New jobs assigned to `worker-01` now upload to YouTube for real; monitor quota/API errors before enabling the same path on `worker-02`.
### 2026-03-26 12:02 - Distinguish render completion from YouTube upload in user queue
- Added: Derived user-facing job status view that distinguishes `Render hoan tat` from `Da upload YouTube`, plus direct `Xem` action when a YouTube watch URL exists.
- Changed: User queue timeline now shows separate `Render` and `Upload` timestamps; completed jobs no longer show `Huy`.
- Fixed: Eliminated the misleading `Hoan tat` state that previously hid whether a job had only rendered locally or had actually uploaded to YouTube.
- Affected files: `backend/app/store.py`, `backend/app/templates/user_dashboard.html`, `docs/PROJECT_CONTEXT.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`.
- Impact/Risk: Purely user-facing status/view-model change; backend worker/control-plane contract remains unchanged.
### 2026-03-26 13:30 - Add realtime render/upload progress to user queue
- Added: `GET /api/user/dashboard/live` for lightweight queue/KPI refresh and dual progress values `render_progress` / `upload_progress` in the user dashboard view-model.
- Changed: Job info column spacing is tighter; queue progress now renders two branded bars `Render` and `Upload` instead of a single generic bar.
- Fixed: User queue no longer requires a page refresh to observe status/timeline changes after worker progress updates.
- Affected files: `backend/app/routers/api_user.py`, `backend/app/store.py`, `backend/app/templates/user_dashboard.html`, `backend/app/static/js/user_dashboard.js`, `docs/PROJECT_CONTEXT.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`.
- Impact/Risk: Frontend now polls every 5 seconds; backend cost is low because the endpoint returns only the queue/KPI subset.
### 2026-03-26 14:05 - Stabilize live queue preview and rebalance progress column
- Added: Signature guard cho live polling de bo qua DOM patch khi payload queue khong doi.
- Changed: Can lai layout cot Tien do va doi progress Upload sang mau amber.
- Fixed: Thumbnail preview khong con chop moi 5 giay do rerender tbody tren user queue.
- Affected files: backend/app/static/js/user_dashboard.js, backend/app/templates/user_dashboard.html.
- Impact/Risk: Giam repaint o user dashboard; can hard refresh 1 lan neu browser dang cache JS cu.
### 2026-03-26 13:18 - Clean media cache after YouTube upload and purge stale VPS artifacts
- Added: Completed jobs now prefer YouTube thumbnail preview so local source cache can be deleted without breaking user queue preview.
- Changed: Control plane cleanup removes local upload sessions/assets when a job has uploaded to YouTube or when the job is deleted; worker upload flow now deletes the rendered output file right after successful YouTube upload.
- Fixed: VPS disk no longer keeps completed local source files and stale worker outputs indefinitely; manual cleanup removed 6 control-plane asset files and reduced worker-01 outputs from 3.6G to 4K.
- Affected files: backend/app/store.py, workers/agent/job_runner.py, runtime /opt/youtube-upload-lush/backend/data/app_state.db, runtime /opt/youtube-upload-lush/worker-data/outputs, docs/DECISIONS.md, docs/WORKLOG.md.
- Impact/Risk: Future scheduled jobs still keep source media in cache until due time; automatic end-to-end cleanup for new jobs is deployed, but I have not yet validated it with one brand-new upload job after rollout.
### 2026-03-26 13:44 - Verify scheduled upload on two real channels and controlled worker-02 rollout test
- Added: Ran 3 production-like upload checks against the real connected channels, including one controlled scheduled job forced onto worker-02.
- Changed: Temporarily toggled worker-02 execute/upload gates and channel-to-worker mapping for test, then restored both real channels back to worker-01 and returned worker-02 to standby.
- Fixed: Confirmed the controlled worker-02 path can claim exactly at scheduled time, upload to YouTube successfully, and leave worker-data/outputs empty after completion.
- Affected files: runtime /etc/youtube-upload-worker.env on worker-02, runtime youtube-upload-worker.service on worker-01 and worker-02, runtime /opt/youtube-upload-lush/backend/data/app_state.db, docs/WORKLOG.md.
- Impact/Risk: Two scheduled jobs requested for worker-02 were claimed first by worker-01 before the control-plane mapping was fully reloaded; a subsequent controlled job validated worker-02 end-to-end and the system has been restored to the previous safe topology.### 2026-03-26 13:52 - Fix render queue viewport overflow on user dashboard
- Added: Browser-level verification for page width/scroll behavior before and after the fix.
- Changed: Main content pane now clamps width with min-w-0 and overflow-x-hidden; render queue info/action cells now shrink and wrap instead of forcing the whole page wider than the viewport.
- Fixed: The render queue no longer stretches the entire dashboard beyond the right edge; any remaining overflow stays inside the table wrapper only.
- Affected files: ackend/app/templates/user_dashboard.html, ackend/app/static/js/user_dashboard.js, docs/WORKLOG.md.
- Impact/Risk: Table action buttons may wrap to a second line on tighter desktop widths, but this is preferable to breaking the full page viewport.### 2026-03-26 14:03 - Cache job preview image on control plane instead of depending on YouTube thumbnail
- Added: Worker-to-control-plane preview upload contract and persisted job preview storage served via /api/user/jobs/{job_id}/preview-thumbnail.
- Changed: Preview resolution now prefers cached local preview, then original source preview, and only falls back to YouTube thumbnail last.
- Fixed: Job preview no longer depends on external YouTube thumbnail availability and can survive source/output cleanup; deleting a job/channel/bot now also removes its cached preview.
- Affected files: ackend/app/schemas.py, ackend/app/store.py, ackend/app/routers/api_user.py, ackend/app/routers/api_worker.py, workers/agent/control_plane.py, workers/agent/ffmpeg_pipeline.py, workers/agent/job_runner.py, docs/DECISIONS.md, docs/WORKLOG.md.
- Impact/Risk: Existing jobs created before this rollout do not magically gain cached previews; they now fall back to their source URL when available, while newly processed jobs will upload and keep their own preview image automatically.
### 2026-03-26 14:12 - Verify cached preview lifecycle end-to-end on live VPS
- Added: Created and processed a fresh live job (`job-e383de12`) specifically to validate the new cached-preview contract after deployment.
- Changed: Verified runtime state across control plane and worker-01 rather than relying only on compile/smoke checks.
- Fixed: Confirmed the new lifecycle works as intended: preview image is cached on control plane, worker output is removed after upload success, and deleting the job also deletes the cached preview and invalidates its route.
- Affected files: runtime https://ytb.jazzrelaxation.com/api/user/dashboard/live, runtime /opt/youtube-upload-lush/backend/data/previews/job-e383de12.jpg, runtime /opt/youtube-upload-lush/backend/data/app_state.db, runtime /opt/youtube-upload-lush/worker-data/outputs, docs/WORKLOG.md.
- Impact/Risk: The live verification used a real YouTube upload (`https://www.youtube.com/watch?v=PTtcp73Od9A`); the dashboard entry was removed afterward, but the uploaded video itself still exists on YouTube unless deleted separately.
### 2026-03-26 14:26 - Audit worker VPS OS and hardware suitability for API-based upload pipeline
- Added: Collected live runtime inventory from both worker VPS, including OS, CPU, RAM, disk, browser presence, and worker service state.
- Changed: Confirmed the worker architecture no longer depends on GUI Chrome sessions; both nodes run a headless Python worker under systemd on Ubuntu.
- Fixed: Removed uncertainty about worker platform choice: the current two workers are already Ubuntu 22.04.5 LTS with 4 vCPU, ~5.8 GiB RAM, and ~400 GB disk each.
- Affected files: runtime 109.123.233.131, runtime 62.72.46.42, docs/WORKLOG.md.
- Impact/Risk: Future infrastructure optimization should focus on right-sizing Linux worker specs and storage policy rather than migrating away from Windows, because the active workers are already Linux and Chrome-free.
### 2026-03-26 14:50 - Wire custom admin login UI and audit account/storage gaps
- Added: Replaced the temporary admin login page with the UI from `login_preview.html`, including error banner, password visibility toggle, and preserved username after failed login.
- Changed: Hardened the admin login flow by sanitizing `next` redirect targets and passing explicit form/notice state into the template.
- Fixed: Live `/admin/login` now uses the designed UI and the full login flow works on both local and deployed environments.
- Affected files: backend/app/templates/admin/login.html, backend/app/routers/web.py, runtime https://ytb.jazzrelaxation.com/admin/login, docs/WORKLOG.md.
- Impact/Risk: Admin auth UX is now wired, but the broader account system still needs a real user-session layer, password hashing, and relational storage beyond the current SQLite JSON snapshot bootstrap.
### 2026-03-26 14:48 - Wire new admin login UI and audit auth/data management gaps
- Added: Restored and rewired the admin login template from `login_preview.html` into `backend/app/templates/admin/login.html`, including working form fields, error banner, hidden `next`, and password visibility toggle.
- Changed: Kept the existing `/admin/login` session-based auth contract intact while modernizing only the shell UI, so current admin routes do not need a migration to keep working.
- Fixed: The admin login route no longer points at a missing template; `TestClient` confirms GET render, failed-login state retention, and successful-login redirect/cookie flow all work again.
- Affected files: backend/app/templates/admin/login.html, docs/DECISIONS.md, docs/WORKLOG.md.
- Impact/Risk: This only modernizes admin login UI; user-side authentication is still not real yet because the user workspace still resolves a seed/current user directly in store logic.
### 2026-03-26 14:54 - Deploy and verify live admin login route with new UI shell
- Added: Live-host verification for the refreshed admin login route, including browser-level login on the production-like domain.
- Changed: Synced `backend/app/routers/web.py` and the new login template to the host, then restarted `youtube-upload-web.service`.
- Fixed: Public `/admin/login` now renders the new UI and completes the real admin session flow to `/admin/user/index` again.
- Affected files: backend/app/routers/web.py, backend/app/templates/admin/login.html, runtime /opt/youtube-upload-lush/backend/app/routers/web.py, runtime /opt/youtube-upload-lush/backend/app/templates/admin/login.html, docs/WORKLOG.md.
- Impact/Risk: Admin login is live and working, but this does not solve the separate gap that the user workspace still lacks real per-user authentication and still relies on seed/current-user shortcuts in store logic.
### 2026-03-26 16:20 - Introduce real user/admin auth on hashed credential storage
- Added: `AppSessionUser` session helpers, browser login/logout flow for `/login` and `/logout`, and per-user ownership checks for workspace routes, jobs, uploads, previews, and Google OAuth callback.
- Changed: Split auth/account persistence into relational SQLite tables `auth_users`, `auth_credentials`, `auth_channel_grants` while keeping jobs/workers/runtime queue state in the existing snapshot layer for now.
- Fixed: Removed plaintext password storage/display from admin role pages, migrated legacy credentials to PBKDF2 hashes, and stopped the user workspace from resolving a fake global current user.
- Affected files: backend/app/auth.py, backend/app/routers/api_user.py, backend/app/routers/web.py, backend/app/schemas.py, backend/app/store.py, backend/app/templates/admin/login.html, backend/app/templates/admin/user_create.html, backend/app/templates/admin/user_index.html, backend/app/templates/admin/user_reset_password.html, backend/app/templates/admin/user_role_list.html, backend/app/templates/user_dashboard.html, docs/DECISIONS.md, docs/WORKLOG.md.
- Impact/Risk: Local auth flow is now real and session-based, but this phase has not been deployed to the live VPS yet and still leaves session cookie naming/CSRF hardening plus full Postgres migration for a later phase.
### 2026-03-26 16:35 - Roll out user login gate to live control plane
- Added: Live deployment of the new auth phase to `82.197.71.6`, including runtime backup before overwrite.
- Changed: The public user workspace now gates `/app` behind `/login` and keeps separate login form targets for user and admin on the live domain.
- Fixed: The live site no longer opens the user workspace anonymously; `/app` now redirects to `/login?next=/app`.
- Affected files: runtime /opt/youtube-upload-lush/backend/app/auth.py, runtime /opt/youtube-upload-lush/backend/app/routers/api_user.py, runtime /opt/youtube-upload-lush/backend/app/routers/web.py, runtime /opt/youtube-upload-lush/backend/app/schemas.py, runtime /opt/youtube-upload-lush/backend/app/store.py, runtime /opt/youtube-upload-lush/backend/app/templates/admin/login.html, runtime /opt/youtube-upload-lush/backend/app/templates/admin/user_create.html, runtime /opt/youtube-upload-lush/backend/app/templates/admin/user_index.html, runtime /opt/youtube-upload-lush/backend/app/templates/admin/user_reset_password.html, runtime /opt/youtube-upload-lush/backend/app/templates/admin/user_role_list.html, runtime /opt/youtube-upload-lush/backend/app/templates/user_dashboard.html, docs/WORKLOG.md.
- Impact/Risk: Route gating on live is now correct, but login still depends on the existing real passwords stored on the VPS; the old seed credentials `admin123/demo123` are no longer valid on that database.
### 2026-03-26 16:55 - Unify login into a single role-aware entrypoint
- Added: A shared `authenticate_login_user()` path that accepts one login form and lets the backend decide whether to open user workspace or admin space.
- Changed: `/login` is now the only real login page; `/admin/login` has been demoted to a redirect alias that forwards into `/login?next=/admin/user/index`.
- Fixed: Removed the awkward two-login-page UX so user/admin/manager accounts no longer need separate entry pages; role-based redirect now happens immediately after successful authentication.
- Affected files: backend/app/store.py, backend/app/routers/web.py, backend/app/templates/admin/login.html, runtime /opt/youtube-upload-lush/backend/app/store.py, runtime /opt/youtube-upload-lush/backend/app/routers/web.py, runtime /opt/youtube-upload-lush/backend/app/templates/admin/login.html, docs/DECISIONS.md, docs/WORKLOG.md.
- Impact/Risk: The login UX is now simpler and closer to a single-account system, but admin web routes that are hit directly without a session still rely on existing route-level guards and may need a broader redirect middleware in a later pass.
### 2026-03-26 16:14 - Tighten user render table layout
- Added: Worker display resolution for user render rows so the table can show a VPS-facing label and still keep the internal worker alias as meta.
- Changed: User render rows now use a narrower STT column, smaller preview width, single-line ellipsis for long title/meta/description, and a no-wrap action bar to keep actions on one line.
- Fixed: Removed the redundant waiting sentence, replaced the `Chưa xếp hàng` fallback with `Queue #...`, and renamed the `BOT` column to `VPS`.
- Affected files: backend/app/store.py, backend/app/templates/user_dashboard.html, backend/app/static/js/user_dashboard.js, runtime /opt/youtube-upload-lush/backend/app/store.py, runtime /opt/youtube-upload-lush/backend/app/templates/user_dashboard.html, runtime /opt/youtube-upload-lush/backend/app/static/js/user_dashboard.js, docs/WORKLOG.md.
- Impact/Risk: Live worker display now depends on `worker.name`; production workers were switched from `worker-01/02` aliases to their public IPs so the new `VPS` column is immediately actionable without changing worker IDs.
### 2026-03-26 16:32 - Normalize worker identity to VPS IP across admin and user views
- Added: A shared worker display mapping in `store.py` that normalizes known worker IDs to their real VPS IPs while keeping `worker.id` unchanged for runtime contracts.
- Changed: Admin/user/channel/render/export contexts now resolve worker display labels from the normalized worker name instead of ad-hoc `replace("worker", "BOT")` transforms.
- Fixed: Removed the remaining visible `worker-01/worker-02` aliases from admin worker-related screens and from exported `BotName` values.
- Affected files: backend/app/store.py, backend/app/templates/admin/worker_index.html, backend/app/templates/admin/bot_of_user.html, backend/app/templates/admin/user_manager_bot.html, runtime /opt/youtube-upload-lush/backend/app/store.py, runtime /opt/youtube-upload-lush/backend/app/templates/admin/worker_index.html, runtime /opt/youtube-upload-lush/backend/app/templates/admin/bot_of_user.html, runtime /opt/youtube-upload-lush/backend/app/templates/admin/user_manager_bot.html, docs/DECISIONS.md, docs/WORKLOG.md.
- Impact/Risk: UI and exports are now IP-first for worker identity; internal filters, hidden fields, and job-claim logic still rely on stable `worker.id`, so no migration was needed for runtime queue behavior.
### 2026-03-26 17:01 - Bottom-align render progress bars with timeline rows
- Added: A dedicated `progress-cell` treatment for the user render table so the progress block can be aligned consistently within the row.
- Changed: The progress stack in both the Jinja template and live JS row renderer now uses `justify-end` with a slight bottom pad, and the dashboard script version was bumped to force a fresh asset load.
- Fixed: The two progress bars no longer sit visually too low or drift after live polling; they line up more cleanly against the `Upload` line in the timeline column.
- Affected files: backend/app/templates/user_dashboard.html, backend/app/static/js/user_dashboard.js, runtime /opt/youtube-upload-lush/backend/app/templates/user_dashboard.html, runtime /opt/youtube-upload-lush/backend/app/static/js/user_dashboard.js, docs/WORKLOG.md.
- Impact/Risk: This is a view-layer-only adjustment; there was a brief `502` window during web-service restart, but origin/public health returned to `200` immediately after rollout.
### 2026-03-26 17:11 - Top-align render progress stack to match upload timeline row
- Added: A top-aligned `progress-cell` behavior so the progress block can sit closer to the first timeline row and keep the amber upload bar nearer the `Upload` timestamp line.
- Changed: Switched the progress stack from `justify-end` to `justify-start` with a small top inset in both template and live JS renderer, and bumped the asset version to `20260326-progress-top-align`.
- Fixed: The previous bottom-biased alignment was rolled back; the progress block now sits higher and better matches the user's intended `Upload` row alignment.
- Affected files: backend/app/templates/user_dashboard.html, backend/app/static/js/user_dashboard.js, runtime /opt/youtube-upload-lush/backend/app/templates/user_dashboard.html, runtime /opt/youtube-upload-lush/backend/app/static/js/user_dashboard.js, docs/WORKLOG.md.
- Impact/Risk: This remains a view-only change; origin briefly needed a few seconds to accept local curl after restart, but final origin/public health both returned `200`.
### 2026-03-26 17:19 - Tighten progress cell toward the top edge
- Added: A tighter top-padding treatment for the progress table cell so the full `Render/Upload` stack sits visibly closer to the top of the row.
- Changed: The progress cell now uses `pt-2 pb-4` instead of symmetric `py-4`, while the internal stack top padding was reduced to zero and the JS renderer was kept in sync.
- Fixed: Both progress rows now sit higher together, instead of only nudging the amber upload row, which better matches the user's requested top-aligned table rhythm.
- Affected files: backend/app/templates/user_dashboard.html, backend/app/static/js/user_dashboard.js, runtime /opt/youtube-upload-lush/backend/app/templates/user_dashboard.html, runtime /opt/youtube-upload-lush/backend/app/static/js/user_dashboard.js, docs/WORKLOG.md.
- Impact/Risk: View-layer only; service restart completed cleanly and both origin/public health checks returned `200` after deploy.
### 2026-03-26 17:32 - Lower the upload progress row to match timeline upload line
- Added: A small dedicated top margin on the `Upload` progress block so the amber bar can line up closer to the third `Upload:` line in the timeline column.
- Changed: Kept the overall progress cell tight to the top, but offset only the upload block with `mt-1` in both the template and live JS row renderer; asset version moved to `20260326-progress-upload-lower`.
- Fixed: The amber upload bar no longer sits as high relative to the timeline upload row, reducing the visible mismatch highlighted in the user's screenshot.
- Affected files: backend/app/templates/user_dashboard.html, backend/app/static/js/user_dashboard.js, runtime /opt/youtube-upload-lush/backend/app/templates/user_dashboard.html, runtime /opt/youtube-upload-lush/backend/app/static/js/user_dashboard.js, docs/WORKLOG.md.
- Impact/Risk: View-layer only; deploy completed cleanly and both origin/public health checks returned `200`.
### 2026-03-26 18:02 - Lower the full progress stack by one more step
- Added: One more small downward shift for the whole progress stack so both `Render` and `Upload` rows move together while preserving the upload-row offset from the previous pass.
- Changed: The progress cell padding moved from `pt-2 pb-4` to `pt-3 pb-3` in both the template and live JS renderer; asset version moved to `20260326-progress-stack-lower`.
- Fixed: The progress stack now sits slightly lower overall, which should bring the amber bar closer to the target upload timeline row without breaking the spacing between the two progress blocks.
- Affected files: backend/app/templates/user_dashboard.html, backend/app/static/js/user_dashboard.js, runtime /opt/youtube-upload-lush/backend/app/templates/user_dashboard.html, runtime /opt/youtube-upload-lush/backend/app/static/js/user_dashboard.js, docs/WORKLOG.md.
- Impact/Risk: View-layer only; deploy completed cleanly and both origin/public health checks returned `200`.
### 2026-03-26 18:05 - Apply explicit per-row offsets inside the progress column
- Added: Explicit per-row vertical offsets for the `Render` and `Upload` blocks inside the progress cell to allow finer alignment against the timeline rows.
- Changed: Replaced implicit utility-only offsets with direct `margin-top: 6px` on both progress blocks in the template and live JS renderer; asset version moved to `20260326-progress-render-upload-offset`.
- Fixed: The progress rows can now be tuned more predictably than before, reducing trial-and-error from only shifting the outer cell padding.
- Affected files: backend/app/templates/user_dashboard.html, backend/app/static/js/user_dashboard.js, runtime /opt/youtube-upload-lush/backend/app/templates/user_dashboard.html, runtime /opt/youtube-upload-lush/backend/app/static/js/user_dashboard.js, docs/WORKLOG.md.
- Impact/Risk: View-layer only; deploy completed cleanly and both origin/public health checks returned `200`.
### 2026-03-26 18:09 - Split render/upload offsets to different final values
- Added: Separate final offsets for the two progress blocks so `Render` and `Upload` no longer move as a locked pair.
- Changed: `Render` now uses `margin-top: 12px` while `Upload` uses `margin-top: 8px` in both the template and live JS renderer; asset version moved to `20260326-progress-split-offsets`.
- Fixed: The progress column can now follow the requested asymmetry, letting `Render` drop further while nudging `Upload` only a little.
- Affected files: backend/app/templates/user_dashboard.html, backend/app/static/js/user_dashboard.js, runtime /opt/youtube-upload-lush/backend/app/templates/user_dashboard.html, runtime /opt/youtube-upload-lush/backend/app/static/js/user_dashboard.js, docs/WORKLOG.md.
- Impact/Risk: View-layer only; deploy completed cleanly and both origin/public health checks returned `200`.
### 2026-03-26 18:12 - Pull the upload row back up toward render
- Added: A tighter upload-row offset so the amber upload block can sit nearer the render block without changing render alignment.
- Changed: `Upload` offset was reduced from `margin-top: 8px` to `margin-top: 4px`, while `Render` stayed at `12px`; asset version moved to `20260326-progress-upload-up`.
- Fixed: The gap between `Render` and `Upload` is now narrower again, matching the user's intended direction instead of pushing upload further away.
- Affected files: backend/app/templates/user_dashboard.html, backend/app/static/js/user_dashboard.js, runtime /opt/youtube-upload-lush/backend/app/templates/user_dashboard.html, runtime /opt/youtube-upload-lush/backend/app/static/js/user_dashboard.js, docs/WORKLOG.md.
- Impact/Risk: View-layer only; deploy completed cleanly and both origin/public health checks returned `200`.
### 2026-03-26 18:20 - Set final manual progress offsets from user-provided values
- Added: A direct manual-offset configuration for the two progress rows using the exact values provided by the user.
- Changed: `Render` now uses `margin-top: 6px` and `Upload` uses `margin-top: 1px` in both the template and live JS renderer; asset version moved to `20260326-progress-user-final-offsets`.
- Fixed: The progress column no longer depends on inferred spacing guesses for this pass; it now reflects the explicit offset values the user requested.
- Affected files: backend/app/templates/user_dashboard.html, backend/app/static/js/user_dashboard.js, runtime /opt/youtube-upload-lush/backend/app/templates/user_dashboard.html, runtime /opt/youtube-upload-lush/backend/app/static/js/user_dashboard.js, docs/WORKLOG.md.
- Impact/Risk: View-layer only; deploy completed cleanly and both origin/public health checks returned `200`.
### 2026-03-26 18:26 - Sync local workspace with origin/main
- Added: A sync record noting that the local workspace was updated to the latest remote state before any further work.
- Changed: Local `main` fast-forwarded from `97df154` to `cb071ee` via `git pull --ff-only`; latest remote commit title is `Implement auth flow and refine dashboard runtime`.
- Fixed: The workspace is no longer behind `origin/main`, reducing the risk of working on stale code.
- Affected files: docs/WORKLOG.md, docs/CHANGELOG.md, local git metadata.
- Impact/Risk: Low risk; repository content now matches the latest remote commit, with only local project-log docs changed by this sync record.
### 2026-03-26 18:42 - Create a stronger OAuth brand logo for Google verification
- Added: A new square OAuth logo set built around a `JR` monogram tied to `JazzRelaxation`, including SVG, preview HTML, and a ready-to-upload PNG.
- Changed: The recommended Google branding asset is no longer the old icon-only mark; it now uses a more explicit brand identifier designed to read as `JazzRelaxation` at small size.
- Fixed: The previous logo was too generic for Google's branding review and did not clearly identify the app's brand and identity.
- Affected files: backend/app/static/brand/jazzrelaxation-upload-manager-oauth-logo.svg, backend/app/static/brand/jazzrelaxation-upload-manager-oauth-logo-preview.html, backend/app/static/brand/jazzrelaxation-upload-manager-oauth-logo.png, docs/WORKLOG.md, docs/CHANGELOG.md.
- Impact/Risk: Low risk; this only adds branding assets and project documentation, with no runtime behavior changes.
### 2026-03-26 21:22 - Standardize the shared favicon across public and app pages
- Added: A shared static favicon asset at `backend/app/static/brand/site-favicon.svg` based on the same orange icon already used in the login shell.
- Changed: `public_home`, `public_legal`, `admin/login`, `admin/_layout`, and `user_dashboard` now reference the shared favicon file instead of relying on missing or inline-only page-specific icon handling.
- Fixed: Public pages such as `/home` can now show the same browser-tab icon as the login page, eliminating the mismatch visible in the tab bar.
- Affected files: backend/app/static/brand/site-favicon.svg, backend/app/templates/public_home.html, backend/app/templates/public_legal.html, backend/app/templates/admin/login.html, backend/app/templates/admin/_layout.html, backend/app/templates/user_dashboard.html, docs/WORKLOG.md.
- Impact/Risk: Low runtime risk; local verification passed for `/home`, `/privacy-policy`, and `/login`, but live VPS deployment is still pending because SSH access from this machine was denied.
### 2026-03-26 21:24 - Deploy the shared favicon to the live VPS
- Added: A live runtime copy of the shared favicon and updated templates on the production host, with a backup snapshot stored before overwrite.
- Changed: The VPS at `82.197.71.6:/opt/youtube-upload-lush` now serves the same favicon wiring as local for public, login, admin, and user dashboard pages.
- Fixed: The public `/home` tab on `ytb.jazzrelaxation.com` now uses the same orange icon as the login tab instead of appearing without a favicon.
- Affected files: runtime /opt/youtube-upload-lush/backend/app/static/brand/site-favicon.svg, runtime /opt/youtube-upload-lush/backend/app/templates/public_home.html, runtime /opt/youtube-upload-lush/backend/app/templates/public_legal.html, runtime /opt/youtube-upload-lush/backend/app/templates/admin/login.html, runtime /opt/youtube-upload-lush/backend/app/templates/admin/_layout.html, runtime /opt/youtube-upload-lush/backend/app/templates/user_dashboard.html, runtime /opt/youtube-upload-lush/.backup/favicon-20260326-212434, docs/WORKLOG.md.
- Impact/Risk: Low risk; deploy only touched view/static files, `youtube-upload-web.service` returned `active`, and live favicon fetch returned `200 OK`.
### 2026-03-26 22:59 - Make the schedule picker jump to client time on click
- Added: A direct client-time shortcut for the `scheduleAt` picker so clicking or focusing the field immediately syncs it to the user's current system time.
- Changed: `backend/app/static/js/user_dashboard.js` now pushes `new Date()` into Flatpickr on `focus` and `click`, and pressing `Enter` while the picker is open confirms the selected value and closes the calendar; `backend/app/templates/user_dashboard.html` now serves JS version `20260326-schedule-now-enter`.
- Fixed: Users no longer need to manually scroll the calendar/time wheels just to set \"now\"; they can click the field and press `Enter` right away for a fast schedule input flow.
- Affected files: backend/app/static/js/user_dashboard.js, backend/app/templates/user_dashboard.html, runtime /opt/youtube-upload-lush/backend/app/static/js/user_dashboard.js, runtime /opt/youtube-upload-lush/backend/app/templates/user_dashboard.html, runtime /opt/youtube-upload-lush/.backup/schedule-now-enter-20260326-225856, docs/WORKLOG.md.
- Impact/Risk: Low risk; behavior change is isolated to the schedule input, local browser verification passed, and both origin/public health checks stayed `ok` after deploy.
### 2026-03-27 07:35 - Prepare the current workspace for GitHub sync
- Added: A project-log entry capturing that the latest local workspace bundle is being packaged for GitHub sync.
- Changed: The pending local bundle now includes the public OAuth pages, branding/favicon assets, and the schedule-picker shortcut work that had already been verified and deployed live.
- Fixed: The repository is no longer left in a \"live changed but not yet pushed\" state once this sync is completed.
- Affected files: docs/WORKLOG.md, docs/CHANGELOG.md, local git metadata.
- Impact/Risk: Low risk; no runtime behavior changes are introduced by this log entry itself, but it documents the code bundle about to be pushed.
### 2026-03-27 08:39 - Activate render pagination and quick-delete for the visible page
- Added: A real footer action cluster for the user render table with client-side pagination controls and a new `Xóa trang` button that targets only the jobs currently visible on the page.
- Changed: `backend/app/static/js/user_dashboard.js` now keeps render jobs in client state, applies search and sort before paginating, recalculates the summary text dynamically, and re-renders only the current page instead of dumping the full list every time.
- Fixed: The previous pagination UI was only static markup and did nothing; users can now move between pages, and bulk delete no longer requires clicking each row one by one.
- Affected files: backend/app/templates/user_dashboard.html, backend/app/static/js/user_dashboard.js, backend/app/routers/api_user.py, backend/app/store.py, docs/WORKLOG.md, docs/CHANGELOG.md.
- Impact/Risk: Medium-low risk; backend and JS syntax checks passed, but browser-level verification is still pending because no local background server was started in this session.
### 2026-03-27 08:47 - Localize and dismiss login error notices
- Added: A dismiss action for the shared login notice so users can close the error banner without reloading the page.
- Changed: The shared login template now renders the notice as a compact flex row with a right-side `x` button, and the authentication layer now returns the invalid-login message in Vietnamese with diacritics.
- Fixed: The old login alert could not be dismissed and the invalid-credentials message appeared without Vietnamese accents, reducing polish and readability.
- Affected files: backend/app/templates/admin/login.html, backend/app/store.py, docs/WORKLOG.md, docs/CHANGELOG.md.
- Impact/Risk: Low risk; the change is limited to login copy and UI behavior, and `python -m compileall backend/app` passed after the update.
### 2026-03-27 08:56 - Normalize remaining login auth messages to Vietnamese with diacritics
- Added: No new UI surface; this pass strictly finishes localization coverage for all login-related backend messages that can feed the shared notice banner.
- Changed: `backend/app/store.py` now returns Vietnamese-with-diacritics messages not only for invalid credentials, but also for required username/password and role-based access denial cases.
- Fixed: The runtime could still surface ASCII fallback strings in some authentication paths, which is why the screenshot still showed `Thong tin dang nhap khong hop le.` after the first UI pass.
- Affected files: backend/app/store.py, docs/WORKLOG.md, docs/CHANGELOG.md.
- Impact/Risk: Low risk; backend compile passed again and the change is limited to user-facing auth copy.
### 2026-03-27 09:07 - Restart local runtime and deploy the login/dashboard fixes to production
- Added: A runtime rollout snapshot on the production host covering the shared login notice fix plus the current user-dashboard pagination bundle.
- Changed: The local app process on `127.0.0.1:8000` was restarted onto the latest source, and the VPS runtime at `82.197.71.6:/opt/youtube-upload-lush` now serves the updated `store.py`, `login.html`, `user_dashboard.html`, `user_dashboard.js`, and `api_user.py`.
- Fixed: Both local and live runtimes were still capable of serving stale in-memory code before this restart/deploy pass; they are now aligned with the latest workspace state.
- Affected files: runtime local process `uvicorn backend.app.main:app`, runtime `/opt/youtube-upload-lush/backend/app/store.py`, runtime `/opt/youtube-upload-lush/backend/app/templates/admin/login.html`, runtime `/opt/youtube-upload-lush/backend/app/templates/user_dashboard.html`, runtime `/opt/youtube-upload-lush/backend/app/static/js/user_dashboard.js`, runtime `/opt/youtube-upload-lush/backend/app/routers/api_user.py`, docs/WORKLOG.md, docs/CHANGELOG.md.
- Impact/Risk: Medium-low risk; deploy touched both auth copy and dashboard behavior, but local health, host service status, and origin/public health checks all passed after rollout.
### 2026-03-27 09:34 - Deepen admin user editing and simplify the admin brand shell
- Added: Username editing controls to the admin user-edit modal and standalone edit page, including role-aware helper text and readonly behavior for cases where only admin may rename the account.
- Changed: `backend/app/store.py` now lets `update_admin_user()` process username changes with role-aware permission handling and cascades manager username renames to dependent users, workers, channels, and jobs; `backend/app/routers/web.py` now forwards `username` plus `actor_role` and refreshes the current admin session after self-edits; `backend/app/templates/admin/_layout.html` now shows `Youtube Upload` without the extra `Lush` word in the sidebar brand.
- Fixed: Admins can now rename any account, including admin accounts, while managers can rename only scoped user accounts; the previous UI had no username field at all and the sidebar wordmark wrapped with an unnecessary extra line.
- Affected files: backend/app/store.py, backend/app/routers/web.py, backend/app/templates/admin/_layout.html, backend/app/templates/admin/user_index.html, backend/app/templates/admin/user_edit.html, docs/WORKLOG.md, docs/CHANGELOG.md.
- Impact/Risk: Medium-low risk; backend compile and `TestClient` smoke tests passed locally, and the same bundle has now been rolled out to the live VPS with origin/public health checks back to `ok`.
### 2026-03-27 09:40 - Align admin dropdowns with workspace styling and reset manager filter default
- Added: A shared custom single-select enhancement in the admin shell so existing `select.toolbar-select` controls render as branded dropdown buttons with consistent menu states across admin pages and modals.
- Changed: `backend/app/templates/admin/_layout.html` now drives both the manager picker summary and the generic admin select treatment; `backend/app/auth.py`, `backend/app/store.py`, and `backend/app/routers/web.py` now preserve an empty `manager_ids` selection as the real `Tất cả manager` state instead of rehydrating the last sticky session filter.
- Fixed: Admin list tabs no longer reopen with a manager preselected by old session state, and admin dropdowns that previously fell back to native browser UI now visually match the workspace dropdown pattern.
- Affected files: backend/app/templates/admin/_layout.html, backend/app/templates/admin/user_index.html, backend/app/templates/admin/worker_index.html, backend/app/auth.py, backend/app/store.py, backend/app/routers/web.py, docs/DECISIONS.md, docs/WORKLOG.md, docs/CHANGELOG.md.
- Impact/Risk: Medium-low risk; local compile, health check, runtime restart, and browser smoke tests across the main admin tabs all passed, but the live VPS rollout is still pending.
### 2026-03-27 10:03 - Standardize admin table lists with workspace-style footer controls and harden CSV export
- Added: A shared admin table client script that injects per-table quick search, real pagination, a footer summary, and `Xóa trang` controls for every admin list marked with `data-admin-list-table`.
- Changed: `backend/app/templates/admin/_layout.html` now provides the shared table toolbar/footer styles and loads `backend/app/static/js/admin_tables.js`; list templates now opt into the shared behavior and mark deletable rows with `data-bulk-delete-form` or `data-bulk-delete-link`; `backend/app/templates/admin/render_index.html` now moves `Xóa tất cả dữ liệu` into the footer action cluster and removes the old “Xóa lần cuối bởi” block from the top of the panel.
- Fixed: Admin tables no longer miss search bars, mock pagination, and summary text; the channel export endpoint now responds with a stable CSV download header so the browser receives `bao-cao-channel-youtube.csv` instead of a random temporary name.
- Affected files: backend/app/static/js/admin_tables.js, backend/app/templates/admin/_layout.html, backend/app/templates/admin/user_index.html, backend/app/templates/admin/worker_index.html, backend/app/templates/admin/channel_index.html, backend/app/templates/admin/render_index.html, backend/app/templates/admin/user_role_list.html, backend/app/templates/admin/bot_of_user.html, backend/app/templates/admin/channel_user.html, backend/app/templates/admin/channel_users.html, backend/app/templates/admin/user_manager_bot.html, backend/app/templates/admin/user_of_bot.html, backend/app/routers/web.py, docs/DECISIONS.md, docs/WORKLOG.md, docs/CHANGELOG.md.
- Impact/Risk: Medium risk; the change touches all admin list tables and the export route, but local Python/JS syntax checks, runtime restart, browser smoke tests, and response-header verification all passed before live rollout.
### 2026-03-27 10:20 - Add shared admin table sorting, move table search into header, and harden upload-error affordance
- Added: Shared client-side sort controls for all admin tables with clickable header arrows and stateful ordering handled by `backend/app/static/js/admin_tables.js`.
- Changed: `backend/app/templates/admin/_layout.html` now renders the admin table search bar inline inside the list header block and styles sortable headers to match the workspace table language; `backend/app/templates/user_dashboard.html` and `backend/app/static/js/user_dashboard.js` now expose an `error` upload state so a bad local file turns the upload affordance into a clearable `x`.
- Fixed: Vietnamese text mojibake in admin/user-facing templates such as `Danh sách kênh`, `Tìm kiếm nhanh...`, and related labels; admin tables now actually reorder rows when sorted instead of only toggling the header state.
- Affected files: backend/app/static/js/admin_tables.js, backend/app/static/js/user_dashboard.js, backend/app/templates/admin/_layout.html, backend/app/templates/admin/bot_of_user.html, backend/app/templates/admin/channel_index.html, backend/app/templates/admin/channel_user.html, backend/app/templates/admin/channel_users.html, backend/app/templates/admin/login.html, backend/app/templates/admin/render_index.html, backend/app/templates/admin/user_edit.html, backend/app/templates/admin/user_index.html, backend/app/templates/admin/user_manager_bot.html, backend/app/templates/admin/user_of_bot.html, backend/app/templates/admin/user_role_list.html, backend/app/templates/admin/worker_index.html, backend/app/templates/user_dashboard.html, docs/DECISIONS.md, docs/WORKLOG.md, docs/CHANGELOG.md.
- Impact/Risk: Medium-low risk; the pass is mostly template/static only, and local syntax checks, browser smoke tests, plus live host restart/health verification all passed after rollout.
### 2026-03-27 10:39 - Refresh admin panel copy, move render-detail back action, and harden role-list feedback
- Added: Visible admin notice handling on the manager/admin role list pages so add/remove role actions now show clear success/error feedback in-place.
- Changed: Context copy in the admin `Danh sách kênh`, `Danh sách BOT`, and `Danh sách job render` panels now matches the current product workflow; the render-detail back button now sits at the top-right of the `Cấu hình chi tiết` pane instead of the upper banner.
- Fixed: Role add/remove flows now validate empty or unknown usernames cleanly and redirect back with readable Vietnamese notices instead of failing unclearly; the render-detail header copy no longer references the old app workflow.
- Affected files: backend/app/routers/web.py, backend/app/templates/admin/channel_index.html, backend/app/templates/admin/worker_index.html, backend/app/templates/admin/render_index.html, backend/app/templates/admin/render_detail.html, backend/app/templates/admin/user_role_list.html, docs/DECISIONS.md, docs/WORKLOG.md, docs/CHANGELOG.md.
- Impact/Risk: Low risk; changes are mostly template copy/layout plus route-level validation, and local compile, TestClient route checks, and browser smoke tests all passed.
### 2026-03-27 11:05 - Tighten admin create-user form and auto-filter manager picker
- Added: Auto-submit behavior for the shared admin manager picker, including visible selection badges with inline `x` removal.
- Changed: The admin create-user form now starts blank with autofill discouraged and the password field displayed as plain text while typing; manager-filter toolbars on `User`, `BOT`, `Kênh`, and `Render` now filter immediately without a separate top-level `Search` button.
- Fixed: Selecting the only available manager no longer collapses back into the `Tất cả manager` state; explicit `1/1` selection now persists in the URL and UI as a real filtered state.
- Affected files: backend/app/templates/admin/user_create.html, backend/app/templates/admin/_manager_picker.html, backend/app/templates/admin/_layout.html, backend/app/templates/admin/user_index.html, backend/app/templates/admin/worker_index.html, backend/app/templates/admin/channel_index.html, backend/app/templates/admin/render_index.html, docs/WORKLOG.md, docs/CHANGELOG.md.
- Impact/Risk: Medium risk; the shared picker behavior changed across all admin tabs that use manager filtering, but local compile, runtime restart, and browser smoke tests on create-user plus user-index passed before deploy.
### 2026-03-27 11:18 - Audit live worker telemetry for bandwidth and thread columns
- Added: No runtime change in this pass; it documents the live-behavior audit for worker telemetry shown in the admin BOT list.
- Changed: Confirmed that the current `Luồng` value shown in the admin table comes from worker heartbeat/config (`WORKER_THREADS`, `WORKER_CAPACITY`) rather than a deeper measured concurrency probe.
- Fixed: Clarified that `Băng thông` is not a live metric yet because the worker agent still posts `bandwidth_kbps=0` in every heartbeat, and the admin-side thread update action does not reconfigure the remote worker runtime.
- Affected files: docs/WORKLOG.md, docs/CHANGELOG.md.
- Impact/Risk: Low risk; this is an audit/result entry only, but it identifies two places that need a real implementation if the UI is expected to be operational telemetry.
### 2026-03-27 11:21 - Implement real worker bandwidth telemetry and old-style thread display
- Added: Đo băng thông thật từ `/proc/net/dev` trong heartbeat worker và đưa số liệu này lên admin BOT list.
- Changed: Cột `Luồng` ở admin BOT list nay hiển thị theo dạng `đang chạy / tối đa`; copy trong modal cập nhật luồng cũng được đổi sang nghĩa giới hạn tối đa.
- Fixed: Loại bỏ `bandwidth_kbps=0` hard-code khiến UI luôn hiện `0.00 KB/s` dù worker đang hoạt động.
- Affected files: `D:\Youtube_BOT_UPLOAD\workers\agent\control_plane.py`, `D:\Youtube_BOT_UPLOAD\backend\app\schemas.py`, `D:\Youtube_BOT_UPLOAD\backend\app\store.py`, `D:\Youtube_BOT_UPLOAD\backend\app\routers\web.py`, `D:\Youtube_BOT_UPLOAD\backend\app\templates\admin\worker_index.html`.
- Impact/Risk: Admin nhìn đúng hơn trạng thái vận hành hiện tại; tuy vậy `threads` vẫn chưa đồng nghĩa worker xử lý song song thật ở runtime.
### 2026-03-27 11:39 - Implement real worker concurrency by thread limit
- Added: Worker loop đa luồng thật trong `workers/agent/main.py`, mỗi job chạy nền với client riêng và tự báo `fail` nếu nổ lỗi.
- Changed: Control plane chỉ claim thêm khi worker còn slot trống, tự đồng bộ `busy/online` theo số job active, và `threads` trên control plane trở thành mức concurrency mong muốn thay vì bị heartbeat env cũ ghi đè.
- Fixed: Loại bỏ nguy cơ claim lại cùng một job active khi worker poll nhiều lần, đồng thời vá lease refresh để job dài không bị hết hạn giữa chừng.
- Affected files: `D:\Youtube_BOT_UPLOAD\backend\app\store.py`, `D:\Youtube_BOT_UPLOAD\workers\agent\control_plane.py`, `D:\Youtube_BOT_UPLOAD\workers\agent\main.py`.
- Impact/Risk: Hạ tầng đã sẵn sàng cho BOT chạy nhiều job song song theo `Luồng`; tuy vậy chưa có bài test production hai job render thật cùng lúc nên vẫn cần một vòng verify vận hành khi anh muốn mở luồng > 1 trên máy live.
### 2026-03-27 12:05 - Enable dual-worker live run and refine thread action icon
- Added: Asset test local thật trên host gồm video `asset-e2e-20260327.mp4` và audio `asset-e2e-20260327-tone.wav`, phục vụ bài test end-to-end không phụ thuộc nguồn ngoài.
- Changed: Nút `Luồng` ở admin BOT list đổi icon sang `waypoints`; `worker-02` được mở `execute + upload` và channel `Loki Lofi` được remap sang worker này để tham gia vận hành thật.
- Fixed: Tránh mất job test do web service giữ `store` trong memory bằng cách tạo job từ DB khi service dừng ngắn rồi khởi động lại với state mới.
- Affected files: `D:\Youtube_BOT_UPLOAD\backend\app\templates\admin\worker_index.html`, runtime host `82.197.71.6`, runtime worker `62.72.46.42`.
- Impact/Risk: Đã verify live hai worker cùng render/upload thật; tuy vậy vẫn chưa có bài test production một worker chạy `2/2` slot cùng lúc.
### 2026-03-27 12:30 - Validate 2-thread live worker capacity
- Added: Live concurrency test batch with 4 short jobs across worker-01 and worker-02.
- Changed: Operational worker config on VPS to WORKER_THREADS=2 and WORKER_CAPACITY=2.
- Fixed: Confirmed concurrency path claims 2 jobs per worker; isolated worker-02 failures to YouTube upload quota instead of runtime capacity.
- Affected files: docs/DECISIONS.md, docs/WORKLOG.md, docs/CHANGELOG.md
- Impact/Risk: Current worker SKU is validated for 2 concurrent slots; 3+ slots remain unverified and may overload CPU/RAM or hit upload instability.
### 2026-03-27 12:40 - Refine admin user list section copy
- Added: Mô tả ngữ cảnh rõ hơn cho section Danh sách người dùng.
- Changed: Thay copy kỹ thuật cũ bằng wording quản trị phù hợp với màn user list.
- Fixed: Chuẩn hóa lại heading và section note tiếng Việt có dấu ở block đầu bảng user.
- Affected files: backend/app/templates/admin/user_index.html, docs/WORKLOG.md, docs/CHANGELOG.md
- Impact/Risk: Chỉ đổi copy hiển thị, không ảnh hưởng logic hay contract backend.
### 2026-03-27 12:55 - Repair mojibake in admin user list template
- Added: Runtime recovery note for redeploying a clean user_index.html.
- Changed: Repaired Vietnamese copy in ackend/app/templates/admin/user_index.html while preserving recent UX changes.
- Fixed: Mojibake/garbled UTF-8 text on /admin/user/index caused by deploying a corrupted local template.
- Affected files: backend/app/templates/admin/user_index.html, docs/WORKLOG.md, docs/CHANGELOG.md
- Impact/Risk: Fix is isolated to one admin template; after redeploy the page should recover without affecting backend logic.
### 2026-03-27 13:20 - Refine workspace My Channel list visual rhythm
- Added: Stronger avatar shell treatment with accent stroke and clearer row hover presence for the `My Channel` list.
- Changed: Tightened channel row spacing, BOT chip color treatment, and row card emphasis to better match the workspace list/table language.
- Fixed: Reduced the flat look of channel avatars and improved scanability of channel identity vs status.
- Affected files: `D:\Youtube_BOT_UPLOAD\backend\app\templates\user_dashboard.html`, `D:\Youtube_BOT_UPLOAD\docs\WORKLOG.md`, `D:\Youtube_BOT_UPLOAD\docs\CHANGELOG.md`.
- Impact/Risk: Local-only visual refinement; no VPS deploy yet and no backend/runtime logic changed.
### 2026-03-27 13:35 - Polish My Channel badge hierarchy and encoding
- Added: Stable BOT badge tone assignment based on `bot_label` so different BOTs are visually distinguishable in the workspace channel list.
- Changed: Moved avatar emphasis fully to the avatar shell bottom accent instead of the row top stroke, and switched the connected-state icon to a guaranteed Lucide glyph.
- Fixed: Repaired mojibake strings inside the `My Channel` block for subtitle, add-channel CTA, connected badge, and delete action labels.
- Affected files: `D:\Youtube_BOT_UPLOAD\backend\app\store.py`, `D:\Youtube_BOT_UPLOAD\backend\app\templates\user_dashboard.html`, `D:\Youtube_BOT_UPLOAD\docs\WORKLOG.md`, `D:\Youtube_BOT_UPLOAD\docs\CHANGELOG.md`.
- Impact/Risk: Local-only UI refinement with no deploy; backend change is limited to presentation metadata for connected channel cards.
### 2026-03-27 13:50 - Restore My Channel BOT badge fallback and move avatar accent below content
- Added: Avatar inner wrapper so the colored accent can sit beneath the full avatar stack as a shadow-like ground line.
- Changed: Restored complete default BOT badge styling in the base chip class, while keeping per-BOT color overrides from backend.
- Fixed: Prevented BOT labels from collapsing into plain text when `bot_badge_class` is missing in a stale runtime, and moved the avatar accent out from inside the image layer.
- Affected files: `D:\Youtube_BOT_UPLOAD\backend\app\templates\user_dashboard.html`, `D:\Youtube_BOT_UPLOAD\docs\WORKLOG.md`, `D:\Youtube_BOT_UPLOAD\docs\CHANGELOG.md`.
- Impact/Risk: Local-only UI adjustment; a local backend restart may still be needed for the newer `bot_badge_class` payload to appear on an already-running process.
### 2026-03-27 14:00 - Convert avatar ground accent to badge-like stroke
- Added: Badge-style stroke capsule treatment for the avatar ground accent in the workspace My Channel list.
- Changed: Replaced the solid under-avatar line with a small outlined pill to better match the app's chip/badge language.
- Fixed: Reduced the visual mismatch between avatar decoration and the rest of the badge system.
- Affected files: `D:\Youtube_BOT_UPLOAD\backend\app\templates\user_dashboard.html`, `D:\Youtube_BOT_UPLOAD\docs\WORKLOG.md`, `D:\Youtube_BOT_UPLOAD\docs\CHANGELOG.md`.
- Impact/Risk: Local-only visual tweak with no backend or deploy impact.
### 2026-03-27 14:08 - Remove avatar ground accent from My Channel cards
- Changed: Removed the under-avatar accent treatment entirely so channel avatars render as clean framed blocks.
- Fixed: Eliminated the extra decorative element that was competing with the row's information hierarchy.
- Affected files: `D:\Youtube_BOT_UPLOAD\backend\app\templates\user_dashboard.html`, `D:\Youtube_BOT_UPLOAD\docs\WORKLOG.md`, `D:\Youtube_BOT_UPLOAD\docs\CHANGELOG.md`.
- Impact/Risk: Local-only visual simplification with no backend or deploy impact.
### 2026-03-27 14:20 - Create pre-frontend backup snapshot branch
- Added: Backup branch and GitHub snapshot point before the next frontend polish pass.
- Changed: No runtime code behavior changed; this is a source-control safety checkpoint.
- Fixed: Reduced rollback risk for upcoming workspace UI edits by preserving the current integrated state.
- Affected files: docs/WORKLOG.md, docs/CHANGELOG.md, git branch state.
- Impact/Risk: Safe backup only; no deploy or production impact.
### 2026-03-27 14:45 - Align render workspace lanes to updated final_user_ui shell
- Added: Updated lane shell treatments for Render Config, Quick Settings, and My Channel headers based on the latest `final_user_ui.html` reference.
- Changed: Refined input, upload-action, and footer action styling so Render Config and Quick Settings match the new source-of-truth layout while preserving live upload UX hooks.
- Fixed: Replaced noisy default helper text under upload fields with quiet status slots and repaired the channel select placeholder literal in the render form.
- Affected files: `D:\Youtube_BOT_UPLOAD\backend\app\templates\user_dashboard.html`, `D:\Youtube_BOT_UPLOAD\docs\WORKLOG.md`, `D:\Youtube_BOT_UPLOAD\docs\CHANGELOG.md`.
- Impact/Risk: Local-only UI alignment; no VPS deploy and no worker/backend contract changes.
### 2026-03-27 16:36 - Ổn định layout bảng render workspace
- Added: Thêm colgroup cho bảng render workspace để khóa nhịp cột.
- Changed: Chuyển bảng render sang width ổn định hơn bằng 	able-fixed + min-width rõ ràng.
- Fixed: Hạn chế hiện tượng list render bị vỡ layout sau khi chỉnh lại 3 lane phía trên.
- Affected files: backend/app/templates/user_dashboard.html
- Impact/Risk: Chỉ ảnh hưởng local UI workspace; chưa deploy live.
### 2026-03-27 16:45 - Siết lại width bảng render và bump cache local
- Added: Bump version asset workspace để tránh giữ cache cũ của trình duyệt.
- Changed: Chuyển bảng render về cấu trúc 	able-fixed ổn định hơn với colgroup và cột info co giãn.
- Fixed: Giảm hiện tượng render list bị tràn và giãn nhịp cột sai sau đợt polish UI.
- Affected files: backend/app/templates/user_dashboard.html
- Impact/Risk: Chỉ ảnh hưởng local UI workspace; chưa deploy live.
### 2026-03-27 17:15 - Đồng bộ workspace theo final_user_ui.html
- Added: Thêm elevated-card-panel và sync layout workspace theo file mẫu.
- Changed: Đồng bộ KPI strip, Render Config, Quick Settings, My Channel, và wording/action button với inal_user_ui.html.
- Fixed: Giữ logic backend hiện có nhưng đổi cấu trúc hiển thị về đúng nhịp của file nguồn, đồng thời đổi KPI live update sang text-line.
- Affected files: backend/app/templates/user_dashboard.html, backend/app/static/js/user_dashboard.js
- Impact/Risk: Chỉ ảnh hưởng local UI workspace; chưa deploy live.

### 2026-03-27 16:27 - Xac nhan runtime local sau su co /app
- Added: Ghi nhan ket qua kiem tra runtime local sau khi user bao app sap.
- Changed: Khong co thay doi code.
- Fixed: Xac nhan /app va /api/health dang tra 200/ok tren local.
- Affected files: docs/WORKLOG.md, docs/CHANGELOG.md
- Impact/Risk: Neu loi tai hien, can bat traceback foreground vi hien chua tai lap duoc.

### 2026-03-27 15:26 - Add KPI pills to final user UI reference
- Added: Semantic KPI pill treatment for the summary strip in `final_user_ui.html` to match the app summary style.
- Changed: Removed the floating `Created By Deerflow` credit and updated `docs/UI_SYSTEM.md` to allow the compact KPI pill variant.
- Fixed: Visual mismatch between the source-of-truth HTML and the app's KPI summary treatment.
- Affected files: `D:\Youtube_BOT_UPLOAD\final_user_ui.html`, `D:\Youtube_BOT_UPLOAD\docs\UI_SYSTEM.md`, `D:\Youtube_BOT_UPLOAD\docs\WORKLOG.md`, `D:\Youtube_BOT_UPLOAD\docs\CHANGELOG.md`.
- Impact/Risk: Local-only source-of-truth UI update; no backend contract or deploy behavior changed.
### 2026-03-27 15:38 - Deepen My Channel card treatment in final user UI
- Added: Header badge `Da them 3 kenh` and stronger channel-row card treatment for the `My Channel` panel in `final_user_ui.html`.
- Changed: Swapped the channel connection status icon to Lucide `check-circle-2` and restyled subtitle/meta text as a compact blue badge.
- Fixed: Made the channel list feel less flat by adding clearer border depth and aligning the panel closer to the provided reference image.
- Affected files: `D:\Youtube_BOT_UPLOAD\final_user_ui.html`, `D:\Youtube_BOT_UPLOAD\docs\UI_SYSTEM.md`, `D:\Youtube_BOT_UPLOAD\docs\WORKLOG.md`, `D:\Youtube_BOT_UPLOAD\docs\CHANGELOG.md`.
- Impact/Risk: Local-only source-of-truth UI refinement; no backend contract, API, or deploy behavior changed.
### 2026-03-27 15:44 - Revert My Channel depth pass and keep only connected badge
- Added: No new UI surface added; retained only the compact `Da ket noi` status badge for channel rows.
- Changed: Removed the `Da them 3 kenh` header badge and the extra depth styling that made the channel list feel heavier than the prior design.
- Fixed: Restored the earlier `My Channel` look while preserving the clearer connected-status chip.
- Affected files: `D:\Youtube_BOT_UPLOAD\final_user_ui.html`, `D:\Youtube_BOT_UPLOAD\docs\UI_SYSTEM.md`, `D:\Youtube_BOT_UPLOAD\docs\WORKLOG.md`, `D:\Youtube_BOT_UPLOAD\docs\CHANGELOG.md`.
- Impact/Risk: Local-only source-of-truth UI rollback; no backend, API, or deploy behavior changed.
### 2026-03-27 15:52 - Add light card borders to My Channel rows
- Added: Light card-border treatment for each channel row in `final_user_ui.html` so individual channels separate more clearly from the panel background.
- Changed: Removed `Bot-*` from the `My Channel` meta line so each row now shows only the channel link plus the connected badge.
- Fixed: Matched the reference image more closely without reintroducing the heavier depth pass that was reverted earlier.
- Affected files: `D:\Youtube_BOT_UPLOAD\final_user_ui.html`, `D:\Youtube_BOT_UPLOAD\docs\UI_SYSTEM.md`, `D:\Youtube_BOT_UPLOAD\docs\WORKLOG.md`, `D:\Youtube_BOT_UPLOAD\docs\CHANGELOG.md`.
- Impact/Risk: Local-only source-of-truth UI refinement; no backend, API, or deploy behavior changed.
### 2026-03-27 16:03 - Strengthen My Channel row borders and remove bot labels
- Added: Clearer bordered-card treatment for each `My Channel` row in `final_user_ui.html`, with only a very light shadow for separation.
- Changed: Removed `Bot-*` from channel meta text in both the `My Channel` panel and channel-select option metadata so the UI shows only the channel link.
- Fixed: Brought the channel rows closer to the provided reference image without changing the rest of the shell.
- Affected files: `D:\Youtube_BOT_UPLOAD\final_user_ui.html`, `D:\Youtube_BOT_UPLOAD\docs\WORKLOG.md`, `D:\Youtube_BOT_UPLOAD\docs\CHANGELOG.md`.
- Impact/Risk: Local-only source-of-truth UI refinement; no backend, API, or deploy behavior changed.
### 2026-03-27 16:17 - Finalize user workspace copy-sync branch
- Added: Synced final_user_ui.html to the newly provided final_user_ui - Copy.html reference and restored the Created By Deerflow footer on the user workspace.
- Changed: Updated the user workspace to use text-line KPI accents and the My Channel row pattern with inline channel_id | Bot-* meta plus badge-check status.
- Fixed: Rebuilt broken user_dashboard.html blocks while preserving the existing FastAPI, session, and API wiring.
- Affected files: D:\Youtube_BOT_UPLOAD\backend\app\templates\user_dashboard.html, D:\Youtube_BOT_UPLOAD\backend\app\static\js\user_dashboard.js, D:\Youtube_BOT_UPLOAD\final_user_ui.html, D:\Youtube_BOT_UPLOAD\docs\UI_SYSTEM.md, D:\Youtube_BOT_UPLOAD\docs\WORKLOG.md, D:\Youtube_BOT_UPLOAD\docs\CHANGELOG.md.
- Impact/Risk: Visual pass only for the user workspace; no deploy, data, or API contract change in this session.

### 2026-03-27 16:34 - Compact user workspace top section
- Added: worker/IP note nho gon cho My Channel row thay cho bot badge.
- Changed: giam page/panel/KPI/form spacing va rut gon chieu cao top workspace de render list lo ra som hon.
- Fixed: bo style channel-row-bot-chip va dong bo visual source of truth voi UI system moi.
- Affected files: backend/app/store.py, backend/app/templates/user_dashboard.html, final_user_ui.html, docs/UI_SYSTEM.md.
- Impact/Risk: thay doi spacing/presentation o user workspace; logic submit/render job khong doi.
### 2026-03-27 16:47 - Restore KPI and panel rhythm to match template
- Added: upload-slot-status pattern trong UI system cho status upload neo o hang label.
- Changed: tang lai page/panel/KPI spacing ve sat file mau, giu kich thuoc control va upload status runtime moi.
- Fixed: bo trang thai top section bi co nho va sat nhau hon so voi file mau.
- Affected files: backend/app/templates/user_dashboard.html, backend/app/static/js/user_dashboard.js, final_user_ui.html, docs/UI_SYSTEM.md.
- Impact/Risk: thay doi visual rhythm o workspace user; logic tao job/upload khong doi.
### 2026-03-27 16:58 - Tighten upload header alignment and channel hover action
- Added: gioi han file picker ideo/* cho Link video Intro va Link Outro.
- Changed: canh bottom upload status theo hang label va doi hover delete row kenh sang icon + text Xoa.
- Fixed: status Hoan tat khong con cao hon hang Link video loop va hover action sat file mau hon.
- Affected files: backend/app/templates/user_dashboard.html, final_user_ui.html.
- Impact/Risk: thay doi presentation o workspace user; logic upload/channel delete khong doi.### 2026-03-27 17:18 - Tighten render list width and hierarchy
- Added: `render-job-title` 2-line clamp cho thong tin job trong render list va note moi trong `docs/UI_SYSTEM.md` de khoa pattern nay.
- Changed: Rut gon preview, progress column, mot so cell padding va margin-top cua render list de bang bam lai tong chieu ngang/phuong doc cua layout mau.
- Fixed: Bo hien thi `Upload/Local Upload` trong thong tin job, giu lai chi title + `job_id` de title dai co the xuong 2 dong ma khong lam bang bi phong ngang.
- Affected files: `D:\Youtube_BOT_UPLOAD\backend\app\templates\user_dashboard.html`, `D:\Youtube_BOT_UPLOAD\backend\app\static\js\user_dashboard.js`, `D:\Youtube_BOT_UPLOAD\final_user_ui.html`, `D:\Youtube_BOT_UPLOAD\docs\UI_SYSTEM.md`, `D:\Youtube_BOT_UPLOAD\docs\WORKLOG.md`, `D:\Youtube_BOT_UPLOAD\docs\CHANGELOG.md`.
- Impact/Risk: Visual-only refinement cho user workspace render list; khong doi API, session, hay workflow render/upload.
### 2026-03-27 18:06 - Restore render duration meta in job info
- Added: Hien lai phan meta `source • render duration • job id` trong thong tin job cua render list.
- Changed: Dong bo template, JS render dong va file source-of-truth de meta line khop nhau.
- Fixed: Khoi phuc thong tin do dai render ma user can theo doi sau khi pass compact truoc do da an mat dong nay.
- Affected files: `D:\Youtube_BOT_UPLOAD\backend\app\templates\user_dashboard.html`, `D:\Youtube_BOT_UPLOAD\backend\app\static\js\user_dashboard.js`, `D:\Youtube_BOT_UPLOAD\final_user_ui.html`, `D:\Youtube_BOT_UPLOAD\docs\WORKLOG.md`, `D:\Youtube_BOT_UPLOAD\docs\CHANGELOG.md`.
- Impact/Risk: Chi doi presentation cua render list; khong doi API, queue hay workflow upload/render.
### 2026-03-27 18:35 - Audit render list template against live JS
- Added: Mot pass audit rieng cho khu vuc render list sau khi user sua tay template.
- Changed: Khong doi API hay markup runtime; chi xac nhan lai hook DOM, payload live va diem lech giua server HTML voi JS rerender.
- Fixed: Khoanh vung dung diem rui ro hien tai la header sort bi JS ghi de va row markup se khong giong template sau khi search/sort/pagination/live refresh.
- Affected files: D:\Youtube_BOT_UPLOAD\backend\app\templates\user_dashboard.html, D:\Youtube_BOT_UPLOAD\backend\app\static\js\user_dashboard.js, D:\Youtube_BOT_UPLOAD\docs\WORKLOG.md, D:\Youtube_BOT_UPLOAD\docs\CHANGELOG.md.
- Impact/Risk: Data live va API van on; rui ro nam o mat dong bo giao dien render list khi JS cap nhat bang.
### 2026-03-27 18:49 - Sync render list runtime with edited template
- Added: Runtime sort state bay gio bam truc tiep vao data-sort cua header render list thay vi tu tao markup moi.
- Changed: Dong bo enderJobRowMarkup() voi layout render list moi trong template, gom preview w-24 aspect-video, padding px-6, va dong meta ender duration + job id.
- Fixed: Search, sort, pagination va live refresh khong con nguy co render lai bang layout cu hoac ghi de header user vua sua tay.
- Affected files: D:\Youtube_BOT_UPLOAD\backend\app\static\js\user_dashboard.js, D:\Youtube_BOT_UPLOAD\docs\WORKLOG.md, D:\Youtube_BOT_UPLOAD\docs\CHANGELOG.md.
- Impact/Risk: Khong doi API hay du lieu live; chi khoa dong bo visual/runtime cho khu vuc render list.
### 2026-03-27 19:06 - Drive-only link status for remote asset fields
- Added: Status top-right cho cac field remote asset hien Đang kiểm tra..., Link hoạt động, hoac loi dinh dang ngay khi user dan link.
- Changed: Remote URL trong user workspace va API tao job gio chi chap nhan link Google Drive hop le; footer Created By Deerflow duoc go khoi app va source-of-truth.
- Fixed: Khong con truong hop dan link ngoai Drive van submit duoc, va khong con credit footer o goc phai duoi man hinh.
- Affected files: D:\Youtube_BOT_UPLOAD\backend\app\static\js\user_dashboard.js, D:\Youtube_BOT_UPLOAD\backend\app\routers\api_user.py, D:\Youtube_BOT_UPLOAD\backend\app\templates\user_dashboard.html, D:\Youtube_BOT_UPLOAD\final_user_ui.html, D:\Youtube_BOT_UPLOAD\docs\WORKLOG.md, D:\Youtube_BOT_UPLOAD\docs\CHANGELOG.md.
- Impact/Risk: Rule remote asset khat khe hon truoc; cac URL HTTP ngoai Google Drive se bi tu choi co chu dich.
### 2026-03-27 19:18 - Restore 4:3 preview and job kind label
- Added: Kind label uppercase nho o dau cell thong tin job de row render day va de scan hon.
- Changed: Preview render list quay lai ty le 4:3 trong ca template, JS runtime va file mau.
- Fixed: O preview khong con bi dai ngang 16:9, va thong tin job khong con trong qua khi title ngan.
- Affected files: D:\Youtube_BOT_UPLOAD\backend\app\templates\user_dashboard.html, D:\Youtube_BOT_UPLOAD\backend\app\static\js\user_dashboard.js, D:\Youtube_BOT_UPLOAD\final_user_ui.html, D:\Youtube_BOT_UPLOAD\docs\UI_SYSTEM.md, D:\Youtube_BOT_UPLOAD\docs\WORKLOG.md, D:\Youtube_BOT_UPLOAD\docs\CHANGELOG.md.
- Impact/Risk: Chi doi visual render list; logic live/update/sort khong doi.
### 2026-03-27 19:28 - Frontend stability audit for user workspace
- Added: Mot pass audit tong hop qua TestClient va Playwright cho frontend user workspace moi.
- Changed: Khong doi code; xac nhan lai cac flow login, live refresh, sort/search render list, drive-only validation va tao/xoa job smoke.
- Fixed: Khong co fix trong pass nay; phat hien residual issue preview asset tra body rong nen browser video preview dang sinh 416 Range Not Satisfiable.
- Affected files: D:\Youtube_BOT_UPLOAD\docs\WORKLOG.md, D:\Youtube_BOT_UPLOAD\docs\CHANGELOG.md.
- Impact/Risk: Frontend nhin chung da on cho cac flow chinh; rui ro con lai tap trung o render-list preview asset cho mot so job co file preview rong.
### 2026-03-27 18:57 - Harden render preview fallback
- Added: Guard helper kiem tra file preview/thumbnail co du lieu truoc khi phat local preview vao render list.
- Changed: User dashboard render jobs fallback sang Drive thumbnail/preview an toan khi local asset cua `video_loop` bi rong hoac da hu.
- Fixed: Loai bo truong hop preview route tra `200` body rong dan toi browser log `416 Range Not Satisfiable` trong render list.
- Affected files: backend/app/store.py
- Impact/Risk: Frontend render list on dinh hon voi du lieu cu bi loi asset; local runtime can restart de nap code moi.
### 2026-03-27 19:34 - Restore old sort header icons
- Added: Ghi chu nho trong UI system cho pattern sort header inline.
- Changed: Header sort cua render list quay lai cap icon `arrow-up/arrow-down` inline thay vi stack chevron doc.
- Fixed: Tra visual sort state ve dung kieu cu ma user da chot cho bang render.
- Affected files: backend/app/templates/user_dashboard.html, final_user_ui.html, docs/UI_SYSTEM.md
- Impact/Risk: Chi doi markup/CSS bieu tuong sort, khong tac dong logic sort runtime.
### 2026-03-27 20:38 - Commit branch and prepare VPS rollout
- Added: Commit moi tren branch rollout de co moc on dinh truoc khi deploy VPS.
- Changed: Day branch `codex/user-workspace-ui-copy-sync` len GitHub voi commit `0c88c39`.
- Fixed: Lam ro blocker deploy live hien tai la thieu credential SSH hop le tren may dang lam viec, khong phai loi code/runtime moi.
- Affected files: docs/WORKLOG.md, docs/CHANGELOG.md
- Impact/Risk: Branch da an toan de review/rollback; rollout VPS can credential host roi moi tiep tuc.
### 2026-03-27 20:46 - Roll out user workspace branch to VPS
- Added: Rollout live branch `codex/user-workspace-ui-copy-sync` len host `82.197.71.6` sau khi co lai root credential.
- Changed: Dong bo 5 file runtime user workspace len `/opt/youtube-upload-lush`, backup runtime cu truoc khi ghi de, va restart `youtube-upload-web.service`.
- Fixed: Mo khoa duoc blocker deploy truoc do (thieu SSH credential) va xac nhan service live chay lai on dinh voi code moi.
- Affected files: docs/WORKLOG.md, docs/CHANGELOG.md
- Impact/Risk: Live host dang chay code moi; neu can rollback nhanh co the copy lai tu `.backup/ui-sync-*` hoac dua host ve commit `main` tren runtime.
### 2026-03-27 20:51 - Add main rollback bundle on VPS
- Added: Bundle rollback `main` tai `/opt/youtube-upload-lush/.backup/main-rollback-20260327-2049` tren host live.
- Changed: Chot cach rollback an toan sau rollout bang file `main` da dat san tren VPS.
- Fixed: Lam ro rang backup `ui-sync-*` truoc rollout khong duoc tao dung; rollback nen dua tren `main-rollback-20260327-2049`.
- Affected files: docs/WORKLOG.md, docs/CHANGELOG.md
- Impact/Risk: Live host co san diem quay lui ro rang; can dung dung bundle `main-rollback-20260327-2049` neu muon ve `main`.
