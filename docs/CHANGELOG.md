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
