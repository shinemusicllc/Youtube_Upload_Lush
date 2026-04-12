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
- Fixed: `Káº¿t ná»‘i Google` no longer stops at auth URL scaffold and now creates/updates a real connected channel record with `refresh token` metadata in SQLite bootstrap.
- Affected files: `backend/app/auth.py`, `backend/app/routers/api_user.py`, `backend/app/routers/web.py`, `backend/app/schemas.py`, `backend/app/store.py`, `backend/app/templates/user_dashboard.html`, `backend/requirements.txt`, `.env.example`, `docs/PROJECT_CONTEXT.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: trung binh; OAuth connect da chay that tren local bootstrap, nhung `refresh token` van dang luu trong SQLite local va can duoc dua sang secret storage/encryption truoc khi production.
### 2026-03-25 22:25 - Admin KPI Strip Alignment
- Added: bo sung icon va nhan phu cho KPI strip admin de dong bo voi pattern KPI cua user workspace.
- Changed: `summary_strip` admin gio tra ve icon, accent text va value color class; partial `admin/_summary_strip.html` render du label, icon, so lon va nhan phu duoi so tren tat ca tab admin.
- Fixed: KPI admin khong con bi thieu icon/chu phu, va KPI `Äang Upload` khi bang `0` hien so mau den de de nhin hon.
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
- Added: manager picker gio hien selected manager thanh tag trong trigger, moi tag co nut `x` de bo nhanh va co tag/option `XÃ³a táº¥t cáº£` khi chon nhieu.
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
- Impact/Risk: Da co ban thu nghiem host + worker cháº¡y tháº­t, nhung OAuth production va HTTPS/domain van chua cau hinh nen chua san sang production hoÃ n chá»‰nh.
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

### 2026-03-30 11:35 - sync_local_source_from_vps_runtime
- Added: backup dirty worktree local truoc khi recover code tu VPS tai D:\Youtube_BOT_UPLOAD__local_backup_20260330-112534.
- Changed: dong bo nguoc cac file source dang chay tren VPS ve repo main, gom backend/user-admin UI, worker pipeline, infra bootstrap, docs va inal_user_ui.html.
- Fixed: local/main quay ve dung trang thai source dang deploy tren host, khac phuc tinh trang repo va VPS bi lech nhau sau nhieu lan hotfix/deploy truc tiep.
- Affected files: AGENTS.md, backend/app/main.py, backend/app/schemas.py, backend/app/static/js/admin_tables.js, backend/app/static/js/user_dashboard.js, backend/app/store.py, backend/app/templates/admin/_layout.html, backend/app/templates/admin/login.html, backend/app/templates/admin/worker_index.html, backend/app/templates/user_dashboard.html, docs/ADMIN_PARITY_CHECKLIST.md, docs/CHANGELOG.md, docs/DECISIONS.md, docs/PROJECT_CONTEXT.md, docs/UI_SYSTEM.md, docs/WORKLOG.md, final_user_ui.html, infra/AGENTS.md, workers/agent/control_plane.py, workers/agent/ffmpeg_pipeline.py, workers/agent/job_runner.py, workers/agent/main.py
- Impact/Risk: repo main nay phan anh source dang chay tren VPS thay vi lich su local truoc do; khong mirror runtime artifact, secret hay repo .NET cu de tranh dua rac deploy vao git.
### 2026-03-30 14:35 - standardize_git_first_deploy_layout
- Added: scripts/git_runtime_layout.sh va docs/DEPLOYMENT.md de dong bo flow clone/pull + runtime symlink cho host/worker.
- Changed: scripts/bootstrap_host.sh va scripts/bootstrap_worker.sh khong con gia dinh source duoc copy san; docs/PROJECT_CONTEXT.md chot deploy model git-first; .gitignore bo qua cac symlink/runtime path moi.
- Fixed: control-plane va 2 worker duoc migrate khoi deploy copy thu cong sang checkout git sach tai /opt/youtube-upload-lush, runtime tach rieng tai /opt/youtube-upload-lush-runtime, giup local/GitHub/VPS khong con lech nhau.
- Affected files: .gitignore, docs/CHANGELOG.md, docs/DECISIONS.md, docs/DEPLOYMENT.md, docs/PROJECT_CONTEXT.md, docs/WORKLOG.md, scripts/bootstrap_host.sh, scripts/bootstrap_worker.sh, scripts/git_runtime_layout.sh
- Impact/Risk: deploy ve sau phai di qua origin/main; khong nen sua source truc tiep tren VPS nua. Runtime state duoc giu nguyen, nhung can tiep tuc theo doi disk usage cua /opt/youtube-upload-lush-runtime.
### 2026-03-30 16:35 - browser_session_channel_onboarding
- Added: Browser runtime local cho Ubuntu (`Chromium + Xvfb/Openbox + x11vnc + websockify/noVNC`), browser session schema/store/API, va modal user dashboard de mo/confirm dong remote session.
- Changed: Flow `+ Them Kenh` tren user workspace uu tien `browser session + noVNC`; OAuth van duoc giu lai lam fallback khi `BROWSER_SESSION_ENABLED=0`.
- Fixed: Host bootstrap/example env da co tham so bat browser runtime va route local tra thong diep cau hinh ro rang thay vi fail mo ho khi user bam them kenh luc chua bat env.
- Affected files: `backend/app/browser_runtime.py`, `backend/app/schemas.py`, `backend/app/store.py`, `backend/app/routers/api_user.py`, `backend/app/static/js/user_dashboard.js`, `backend/app/templates/user_dashboard.html`, `.env.example`, `.env.production.example`, `scripts/bootstrap_host.sh`, `docs/PROJECT_CONTEXT.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Da co scaffold end-to-end cho browser onboarding, nhung upload worker production van chua chuyen hoan toan sang `browser_profile`; host Ubuntu can cai du package GUI/noVNC va mo port web range truoc khi user su dung that.
### 2026-03-30 18:12 - browser_runtime_root_host_fix
- Added: Ghi chu van hanh host browser runtime vao `docs/PROJECT_CONTEXT.md`.
- Changed: Launcher Chromium tren Ubuntu them `--no-sandbox --disable-setuid-sandbox` de phu hop `youtube-upload-web.service` dang chay bang `root`.
- Fixed: Verify production host `82.197.71.6` tao duoc browser session that, `noVNC` mo duoc trang sign-in Google/YouTube, va `close_browser_session` dong duoc runtime session.
- Affected files: `backend/app/browser_runtime.py`, `docs/PROJECT_CONTEXT.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Tang runtime `+ Them Kenh` da san sang cho host hien tai; can test them duong click tu web app bang user workspace that khi co credential app hop le.
### 2026-03-30 19:05 - worker_owned_browser_sessions
- Added: Worker-side browser runtime/coordinator (`workers/agent/browser_runtime.py`, `workers/agent/browser_sessions.py`) va worker APIs `poll/sync browser session` tren control plane.
- Changed: Flow `+ Them Kenh` khong con mo Chromium tren control plane; session nay gio gáº¯n voi `worker/VPS` dau tien duoc cap cho user, worker tu poll va launch `Chromium + noVNC` tren may cua no.
- Fixed: User dashboard modal hien `VPS duoc cap` va khong mo noVNC som khi worker chua bao `awaiting_confirmation/confirmed`.
- Affected files: `backend/app/schemas.py`, `backend/app/store.py`, `backend/app/routers/api_worker.py`, `backend/app/static/js/user_dashboard.js`, `backend/app/templates/user_dashboard.html`, `workers/agent/config.py`, `workers/agent/control_plane.py`, `workers/agent/main.py`, `workers/agent/browser_runtime.py`, `workers/agent/browser_sessions.py`, `workers/AGENTS.md`, `scripts/bootstrap_worker.sh`, `docs/PROJECT_CONTEXT.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Kien truc nay hop voi mo hinh `render + upload tren cung 1 VPS`, nhung worker production can duoc redeploy va cap nhat env `BROWSER_SESSION_*` truoc khi flow `+ Them Kenh` su dung that tren production.
### 2026-03-30 21:13 - single_assigned_worker_per_user
- Added: Chuan hoa `user_worker_links` thanh mapping `1 user -> 1 worker`, worker candidate filter theo manager/worker da duoc cap, va blocked-message khi user chua duoc cap VPS.
- Changed: User bootstrap/dashboard/job list chi hien kenh va job cua assigned worker; reconnect OAuth/browser se rebind channel ve worker duoc cap, va admin copy tren man hinh mapping user-worker doi sang huong `VPS`.
- Fixed: Tao job tren kenh dang nam o VPS khac se bi chan som voi thong diep yeu cau reconnect kenh; manager doi VPS cho user se dong browser session cu de tranh login sai may.
- Affected files: `backend/app/store.py`, `backend/app/static/js/user_dashboard.js`, `backend/app/templates/admin/user_manager_bot.html`, `backend/app/templates/admin/bot_of_user.html`, `backend/app/templates/admin/user_of_bot.html`, `docs/PROJECT_CONTEXT.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Du lieu local/prototype cu co kenh nam o VPS khac assigned worker se bi an khoi workspace user cho toi khi reconnect tren VPS moi; can deploy code moi len production neu muon hanh vi nay ap dung tren host that.

### 2026-03-31 22:15 - Sync GitHub from VPS source
- Added: Dong bo local theo snapshot code deploy tren control VPS va ghi nhan VPS tam thoi la source of truth khi GitHub drift.
- Changed: Chuan bi dua GitHub ve dung state source tren `/opt/youtube-upload-lush`, ke ca file server untracked va cac file worker browser-flow bi thieu tren VPS.
- Fixed: Chua co thay doi logic moi; task nay chi dong bo ma nguon.
- Affected files: docs/DECISIONS.md, docs/WORKLOG.md, docs/CHANGELOG.md, backend/*, workers/*, scripts/*, infra/*
- Impact/Risk: GitHub se mat cac file/logic moi chi ton tai o local neu VPS khong co; doi lai GitHub se phan anh dung code dang duoc sua nong tren server.

### 2026-03-31 22:44 - split_bot_assignment_into_dedicated_admin_tab
- Added: Trang admin moi `Cáº¥p phÃ¡t BOT` tai `/admin/bot/assignment`, nav sidebar rieng, va template `backend/app/templates/admin/bot_assignment.html` dung lai luong chon manager/user + kho BOT trong theo visual system hien co.
- Changed: `Danh sÃ¡ch BOT` bo panel cap phat o dau trang va quay ve vai tro quan sat cum BOT VPS; cac link tu trang user lien quan BOT nay tro ve tab cap phat moi.
- Fixed: Giam tinh trang man `Danh sÃ¡ch BOT` vua list vua form thao tac day dac; luong cap/doi BOT nay co mot diem vao tap trung, de scan va de huong dan hon.
- Affected files: `backend/app/store.py`, `backend/app/routers/web.py`, `backend/app/templates/admin/worker_index.html`, `backend/app/templates/admin/bot_assignment.html`, `backend/app/templates/admin/user_index.html`, `backend/app/templates/admin/user_manager_bot.html`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Chua deploy production; local smoke da pass, nhung UI live tren VPS se chi doi sau khi commit/push va rollout len host.

### 2026-03-31 23:02 - align_bot_assignment_screen_with_attached_mockup
- Added: Page-specific split-dispatch layout rules cho `Cáº¥p phÃ¡t BOT`, giu sidebar cua app va dua manager scope filter len thanh tieu de mong phia tren.
- Changed: Bo dáº£i KPI khoi man `Cáº¥p phÃ¡t BOT`, chuyen content ve layout sat file `bot_assignment_ui.html`: trai la `Báº£ng Ä‘iá»u phá»‘i`, phai la `BOT cÃ²n trá»‘ng` voi toolbar va card grid phang hon.
- Fixed: Man cap phat truoc do van con mang nhieu dau vet cua shell admin tong quat, chua giong mockup user dua; ban moi tap trung hon va khop huong visual mong muon.
- Affected files: `backend/app/templates/admin/bot_assignment.html`, `docs/UI_SYSTEM.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Chi sua local UI cua route `/admin/bot/assignment`; backend contract cap phat giu nguyen, nhung can user xem local truoc khi commit/push.

### 2026-03-31 23:13 - make_bot_assignment_match_workspace_mockup_more_closely
- Added: Layout moi cho `Cáº¥p phÃ¡t BOT` theo workspace dieu phoi gan sat anh mau: top stat chips, panel `Danh sÃ¡ch BOT`, rail chuyen, target pane `GÃ¡n cho ngÆ°á»i nháº­n`, va danh sach BOT stage truoc khi luu.
- Changed: `backend/app/store.py` bo sung data contract cho worker rows day du, target options manager/user, default target, va count `available/assigned/offline` de template moi render dung shape.
- Fixed: Loi render local do `assignment_worker_rows` thieu `index/status_key`; sau khi bo sung context, route `/admin/bot/assignment` render `200` sau login va giu nguyen flow submit `/admin/bot/assign`.
- Affected files: `backend/app/templates/admin/bot_assignment.html`, `backend/app/store.py`, `docs/UI_SYSTEM.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: UI moi bam mockup hon nhung chua co visual screenshot tu browser automation trong thread nay; can user xem local de chot cam quan truoc khi commit/push.

### 2026-03-31 23:23 - tighten_bot_assignment_spacing_and_default_target
- Added: Manager mac dinh cho man `Cáº¥p phÃ¡t BOT` khi local state chi co 1 manager, giup khu `GÃ¡n cho ngÆ°á»i nháº­n` co target som ngay luc mo man.
- Changed: Giam `space-y` va padding dau trang trong `bot_assignment.html` de nhip cach voi header/shell sat hon cac tab admin khac.
- Fixed: Local server da duoc restart sach, `/api/health` tro lai `ok`, va route `/admin/bot/assignment` van render HTML co du worker/user/manager that trong local snapshot.
- Affected files: `backend/app/store.py`, `backend/app/templates/admin/bot_assignment.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Local snapshot hien van chi co `1 manager + 1 user`, nen dropdown khong dai nhu mockup; neu can DS phong phu hon de review UI, can seed them du lieu mau hoac import state that.

### 2026-03-31 23:41 - align_bot_assignment_top_spacing_with_other_admin_tabs
- Added: Offset am nhe cho section `Cáº¥p phÃ¡t BOT` de panel dau tien nhich gan top bar hon, khop nhá»‹p voi cac tab admin khac.
- Changed: Khong doi cau truc panel hay logic cap phat; chi chinh vertical spacing o dau man.
- Fixed: Khoang ho tren dau man `Cáº¥p phÃ¡t BOT` khong con lech nhin so voi `Danh sÃ¡ch BOT`.
- Affected files: `backend/app/templates/admin/bot_assignment.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Dieu chinh chi o muc layout spacing local, an toan va de rollback neu user muon sat hon/thoang hon them.

### 2026-03-31 23:43 - raise_bot_assignment_header_panel_further
- Added: Offset top manh hon cho section `Cáº¥p phÃ¡t BOT` de panel dau tien len them 1 náº¥c nua theo feedback visual.
- Changed: Gia tri offset section doi tu `-mt-2` sang `-mt-4`; khong dong vao structure hay JS.
- Fixed: Canh top panel cua tab `Cáº¥p phÃ¡t BOT` sat top bar hon va de dong bo hon voi cac tab admin khac.
- Affected files: `backend/app/templates/admin/bot_assignment.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Tinh chinh layout nho, an toan; neu user muon sat them nua thi co the tiep tuc vi task nay doc lap voi business logic.

### 2026-03-31 23:49 - remove_bot_assignment_hero_and_inline_stats_into_pool_header
- Added: 3 badge `Trá»‘ng / ÄÃ£ cáº¥p / Offline` duoc dua vao header panel `Danh sÃ¡ch BOT`, nam ben trai cum view toggle de sat mockup hon.
- Changed: Bo han hero card mo dau, nho hoa card BOT, va canh lai workspace split de 2 panel chiem toan bo khong gian theo huong anh mau.
- Fixed: Thanh mo dau khong con chiem cho vo nghia; kich co card BOT va nhá»‹p header nay gan hon file `bot_assignment_ui.html`.
- Affected files: `backend/app/templates/admin/bot_assignment.html`, `docs/UI_SYSTEM.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Khong doi business logic; man nay gio lech khoi mo ta `top hero` cu, nen UI system da duoc cap nhat lai cho dong bo.

### 2026-03-31 23:51 - tune_bot_assignment_panel_and_grid_sizes_for_50_bots
- Added: Breakpoint grid co dinh cho danh sach BOT de man rong co the len den 5 cot, phu hop hon voi bai toan 50 BOT va mockup user dua.
- Changed: Tinh chinh them gap workspace, split width trai/phai, va card BOT (`min-height`, `padding`) de mat do panel va item sat kich co trong file `bot_assignment_ui.html`.
- Fixed: Truoc do card BOT van con bi co gian tu do theo `auto-fill`, khien khi du lieu dong se khong giong mockup; ban moi on dinh hon tren man hinh rong.
- Affected files: `backend/app/templates/admin/bot_assignment.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Case 50 BOT tren desktop se gan mockup hon, nhung neu user muon pixel-fit tiep cho tung breakpoint cu the thi van co the tinh chinh them sau khi xem local.

### 2026-03-31 23:53 - restore_top_offset_for_bot_assignment_workspace
- Added: Offset top `-mt-4` duoc dat lai cho section `Cáº¥p phÃ¡t BOT` sau khi bo hero panel.
- Changed: Chi chinh vi tri khoi workspace theo truc doc de panel dau tien sat top bar hon.
- Fixed: Khoang cach top bar -> panel dau tien cua tab `Cáº¥p phÃ¡t BOT` quay ve gan nhá»‹p voi cac tab admin khac.
- Affected files: `backend/app/templates/admin/bot_assignment.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Dieu chinh layout nho, an toan; neu can sat hon nua thi co the tinh tiep ma khong anh huong business logic.

### 2026-04-01 00:16 - rebalance_bot_assignment_width_and_bottom_spacing
- Added: Them `padding-bottom` nhe cho section `Cáº¥p phÃ¡t BOT` de khoang tho phia duoi workspace can doi hon voi khoang cach phia tren.
- Changed: Dieu chinh gap workspace, split trai/phai, breakpoint 5 cot, va card BOT/stage list sizing de man desktop bam sat hon mockup va uu tien du 5 card ngang.
- Fixed: Giam tinh trang panel vuon sat day viewport qua muc va mat do card con hoi to so voi file mau.
- Affected files: `backend/app/templates/admin/bot_assignment.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Hieu ung chi nam o layout desktop/local; neu can pixel-fit them theo do phan giai man hinh that cua user, van co the tinh chinh tiep ma khong dong vao logic.

### 2026-04-01 00:21 - tighten_bot_assignment_bottom_edge_and_add_preview_fifth_card
- Added: Them 1 card BOT preview (`VPS-005`) chi tren man `Cáº¥p phÃ¡t BOT` khi local chua du 5 BOT that, de user nhin dung nhá»‹p 5 cot tren desktop.
- Changed: Bo `padding-bottom` vua them, tang lai `min-height` stage list, va tinh lai split desktop de mep day hai panel sat hon voi y do can doi ban dau.
- Fixed: Layout khong con bi hieu nguoc thanh tang khoang ho duoi panel; user xem duoc card thu 5 ma khong can sua du lieu that.
- Affected files: `backend/app/store.py`, `backend/app/templates/admin/bot_assignment.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Card thu 5 hien la preview-only tren local, checkbox bi khoa va khong tham gia luong assign that; truoc khi deploy co the giu hoac bo tuy muc dich demo UI.

### 2026-04-01 00:24 - sync_bot_assignment_preview_count_and_restart_local_server
- Added: Badge tong BOT cua man `Cáº¥p phÃ¡t BOT` tinh ca card preview de title va grid nhat quan khi demo 5 cot.
- Changed: Restart lai local `uvicorn` tren `127.0.0.1:8000` de browser nhan dung template/store moi nhat.
- Fixed: Trang local truoc do van co the hien nhu cu do hit vao process cu, khien user khong thay `VPS-005` du code da cap nhat.
- Affected files: `backend/app/store.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Khong doi business logic assign; chi dong bo local demo state va runtime de user duyá»‡t UI de hon.

### 2026-04-01 00:27 - remove_bot_assignment_cta_from_bot_list_header
- Added: Khong co thay doi chuc nang moi; panel `Danh sÃ¡ch BOT` duoc tra lai dung vai tro quan sat thuáº§n.
- Changed: Xoa CTA `Má»Ÿ tab Cáº¥p phÃ¡t BOT` va dua header panel ve layout chi con title + manager picker.
- Fixed: Panel dau trang cua `Danh sÃ¡ch BOT` khong con bi day rong va lech nhá»‹p so voi phien ban gon truoc do.
- Affected files: `backend/app/templates/admin/worker_index.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Chi la tinh chinh UI local, khong anh huong route hay luong cap phat BOT rieng.

### 2026-04-01 00:41 - make_assignment_target_picker_searchable_and_fix_selected_state
- Added: Picker `CHá»ŒN MANAGER / USER` tren man `Cáº¥p phÃ¡t BOT` ho tro search inline bang pattern `admin-select` co san cua app.
- Changed: Bo sung `data-search-text` cho option va doi marker hien thi target detail sang namespace rieng de JS update dung node.
- Fixed: Truong hop chon xong dropdown nhung panel ben duoi van hien `ChÆ°a chá»n ngÆ°á»i nháº­n`.
- Affected files: `backend/app/templates/admin/bot_assignment.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Chi tinh chinh UI/JS local cho man cap phat; khong doi contract submit `/admin/bot/assign`.

### 2026-04-01 00:46 - auto_stage_bots_on_select_in_assignment_workspace
- Added: Chon BOT la them thang vao danh sach gan; label/count va hint trong workspace duoc doi sang copy moi phan anh dung hanh vi nay.
- Changed: Loai bo cum mui ten o giua va doi desktop split thanh 2 panel truc tiep, giup panel trai rong hon va thao tac gon hon.
- Fixed: Khong con can tick BOT roi bam mui ten moi thay xuat hien ben phai.
- Affected files: `backend/app/templates/admin/bot_assignment.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Chi doi UI/JS tren man cap phat; submit contract van giu nguyen, nhung flow thao tac cua user da duoc don sang auto-add.

### 2026-04-01 00:55 - deploy_bot_assignment_refinement_to_vps_and_github
- Added: Ban refine moi cua `Cáº¥p phÃ¡t BOT` da duoc rollout len control VPS `82.197.71.6` va dong bo len GitHub `main`.
- Changed: Checkout tren VPS `/opt/youtube-upload-lush` duoc cap nhat ve commit `e5766d426f703382ef6e35a13e4a6aaf7f84822b`, giu nguyen runtime va restart lai `youtube-upload-web.service`.
- Fixed: Local, GitHub, va source dang chay tren VPS quay ve cung mot moc commit cho bo thay doi UI admin BOT assignment.
- Affected files: `backend/app/routers/web.py`, `backend/app/store.py`, `backend/app/templates/admin/_layout.html`, `backend/app/templates/admin/bot_assignment.html`, `backend/app/templates/admin/user_index.html`, `backend/app/templates/admin/user_manager_bot.html`, `backend/app/templates/admin/worker_index.html`, `docs/CHANGELOG.md`, `docs/DECISIONS.md`, `docs/UI_SYSTEM.md`, `docs/WORKLOG.md`
- Impact/Risk: App tren VPS dang healthy sau restart; rieng `scripts/bootstrap_host.sh` van phat sinh loi cu phap trong luot chay tu dong, nen lan nay da chot deploy bang sync + restart thu cong.
### 2026-04-01 09:35 - reconcile_bot_assignment_panel_before_save
- Added: Panel phai tren man Cap phat BOT tu nap BOT hien co cua manager/user da chon va tro thanh trang thai cuoi truoc khi bam luu.
- Changed: Danh sach BOT ben trai gio cho phep tick de them vao panel phai, x de bo khoi danh sach cho luu, va Reset de quay ve dung tap BOT ban dau cua target.
- Fixed: Submit /admin/bot/assign gio chap nhan ca truong hop bo cap het BOT; route web goi dung signature cua reconcile_assignment_target_bots.
- Affected files: backend/app/templates/admin/bot_assignment.html, backend/app/store.py, backend/app/routers/web.py, docs/WORKLOG.md, docs/CHANGELOG.md, docs/DECISIONS.md
- Impact/Risk: Flow cap phat BOT da doi sang reconcile full-state; can test lai 2 case admin cap kho manager va user doi/bo BOT tren UI that.
### 2026-04-01 10:05 - verify_local_bot_assignment_and_deploy_to_vps
- Added: Bai smoke test local cho flow cap phat BOT qua login admin that va submit route /admin/bot/assign.
- Changed: Local uvicorn duoc restart lai sau test de dong bo lai state in-memory voi app_state.db tren disk.
- Fixed: Ban thay doi desired-state cua man Cap phat BOT da duoc rollout len VPS 82.197.71.6 va web service da len lai on dinh.
- Affected files: backend/app/routers/web.py, backend/app/store.py, backend/app/templates/admin/bot_assignment.html, docs/WORKLOG.md, docs/CHANGELOG.md
- Impact/Risk: Production health da ok; can user test tay tren giao dien live de xac nhan UX add/remove/reset dung nhu mong doi.
### 2026-04-01 10:35 - align_bot_live_table_and_purge_channels_on_reassignment
- Added: Them helper _clear_worker_channels() de purge toan bo channel/job/browser profile cleanup tren BOT cu khi BOT bi go, doi owner, hoac bi xoa.
- Changed: Don gon action label tren bang user ve BOT, don empty-state panel phai cua man Cap phat BOT, va viet lai live JS cua Cụm BOT VPS de khop dung HTML hien tai.
- Fixed: Live row cua bang BOT khong con bi lech do JS mang logic thua cua man cap phat; doi/gỡ BOT cua user/manager gio xoa sach kenh cu tren chinh BOT do.
- Affected files: ackend/app/store.py, ackend/app/templates/admin/user_index.html, ackend/app/templates/admin/worker_index.html, ackend/app/templates/admin/bot_assignment.html, docs/WORKLOG.md, docs/CHANGELOG.md, docs/DECISIONS.md
- Impact/Risk: Viec doi owner BOT nay tro thanh destructive voi channel tren BOT cu; da smoke test local va can user test tay lai tren production cho 2 flow edit/gỡ BOT.

### 2026-04-01 11:05 - remove_preview_bot_and_fix_live_worker_ui
- Added: Loai bo hoan toan BOT preview khoi man Cap phat BOT va giu empty-state dung theo trang thai that cua danh sach BOT duoc gan.
- Changed: Rewrite lai giao dien va live script cua Danh sách BOT/Cụm BOT VPS bang chuoi UTF-8 sach, dong thoi cho phep fetch du lieu live ngay khi mo trang.
- Fixed: The BOT 168.119.229.109 / VPS-003 khong con xuat hien; panel phai khong con de lo icon/phu de placeholder khi da co BOT, va cot Băng thông co the cap nhat ngay tu API live.
- Affected files: backend/app/store.py, backend/app/templates/admin/bot_assignment.html, backend/app/templates/admin/worker_index.html, docs/WORKLOG.md, docs/CHANGELOG.md
- Impact/Risk: Can refresh trang sau deploy de nap HTML/JS moi; phan live Băng thông van phu thuoc worker heartbeat/API /api/admin/bots co du lieu.

### 2026-04-01 11:20 - restore_full_bot_assignment_list_and_real_bandwidth_live
- Added: Worker heartbeat gio tu tinh bandwidth_kbps that tu luu luong network tren worker thay vi gui 0 cung.
- Changed: Man Cap phat BOT mo mac dinh o list/full-width va giu kho BOT cao nhu bang cu de khong bi co ngang thanh mot hang card ngan.
- Fixed: Cot Băng thông co nguon du lieu live that de cap nhat; workspace Cap phat BOT khong con vao dang grid ngan khi chi co it BOT.
- Affected files: backend/app/templates/admin/bot_assignment.html, workers/agent/control_plane.py, docs/WORKLOG.md, docs/CHANGELOG.md
- Impact/Risk: Gia tri Băng thông se bat dau thay doi sau khi restart worker va qua it nhat 2 heartbeat; lan heartbeat dau tien van co the hien 0.00 KB/s.

### 2026-04-01 11:35 - deploy_full_width_assignment_list_and_restore_live_bandwidth
- Added: control_plane.py tren worker duoc mo rong them browser-session contract cu, active_job_ids compatibility va do bandwidth_kbps theo delta /proc/net/dev.
- Changed: Man Cap phat BOT chuyen sang list/full-width mac dinh va giu kho BOT cao/on dinh nhu bang cu.
- Fixed: Worker-01/worker-02 da heartbeat tro lai binh thuong, cot Băng thông tren production da len so live thay vi dung 0.00 KB/s.
- Affected files: backend/app/templates/admin/bot_assignment.html, workers/agent/control_plane.py, docs/WORKLOG.md, docs/CHANGELOG.md
- Impact/Risk: Băng thông hien la tong throughput mang tren worker (bo qua loopback), nen se dao dong theo heartbeat va tai that tren VPS.

### 2026-04-01 11:45 - switch_load_metric_to_cpu_delta_and_force_list_view_on_target_change
- Added: Worker heartbeat gio tinh load_percent bang CPU delta tu /proc/stat de phan anh tai thuc te tot hon.
- Changed: Man Cap phat BOT se reset ve list/full-width moi khi chon manager/user, giu khu Danh sach BOT trai ngang nhu bang goc.
- Fixed: Cot Tải khong con phu thuoc loadavg de roi dung 0% dai; target change tren Cap phat BOT khong con de view hep bat thuong.
- Affected files: backend/app/templates/admin/bot_assignment.html, workers/agent/control_plane.py, docs/WORKLOG.md, docs/CHANGELOG.md
- Impact/Risk: Lan heartbeat dau sau restart co the van 0% do chua co mau CPU truoc do; heartbeat tiep theo se co gia tri on dinh hon.

### 2026-04-01 12:05 - restore_grid_default_and_stable_assignment_panel_height
- Added: Thiết lập min-height ổn định cho 2 panel màn Cấp phát BOT để không bị co ngắn sau khi chọn target.
- Changed: Trả mặc định màn Cấp phát BOT về grid view và bỏ logic ép reset về list khi đổi manager/user.
- Fixed: Giữ đáy 2 panel bám sát bottom như trạng thái ban đầu, đồng thời xác nhận dữ liệu Tải/Băng thông trên production đã có số live.
- Affected files: backend/app/templates/admin/bot_assignment.html, docs/WORKLOG.md, docs/CHANGELOG.md
- Impact/Risk: Chỉ ảnh hưởng layout/JS của màn Cấp phát BOT; không đổi contract backend hay worker.

### 2026-04-01 12:05 - restore_grid_default_and_stable_assignment_panel_height
- Added: Thiet lap min-height on dinh cho 2 panel man Cap phat BOT de khong bi co ngan sau khi chon target.
- Changed: Tra mac dinh man Cap phat BOT ve grid view va bo logic ep reset ve list khi doi manager/user.
- Fixed: Giu day 2 panel bam sat bottom nhu trang thai ban dau, dong thoi xac nhan du lieu Tai/Bang thong tren production da co so live.
- Affected files: backend/app/templates/admin/bot_assignment.html, docs/WORKLOG.md, docs/CHANGELOG.md
- Impact/Risk: Chi anh huong layout/JS cua man Cap phat BOT; khong doi contract backend hay worker.
### 2026-04-01 12:20 - deploy_latest_local_admin_and_worker_changes_to_vps
- Added: Rollout batch file local moi nhat len control plane va ca 2 worker production.
- Changed: Dong bo web.py, store.py, user_index.html, worker_index.html, bot_assignment.html, va control_plane.py theo state local hien tai.
- Fixed: Production da chay lai sau restart service, compile pass, va health endpoint tra ok.
- Affected files: backend/app/routers/web.py, backend/app/store.py, backend/app/templates/admin/user_index.html, backend/app/templates/admin/worker_index.html, backend/app/templates/admin/bot_assignment.html, workers/agent/control_plane.py, docs/WORKLOG.md, docs/CHANGELOG.md.
- Impact/Risk: Batch deploy anh huong ca web va worker runtime; neu local co drift ngoai y muon thi production da duoc cap nhat theo dung state local.
### 2026-04-01 11:48 - verify_long_video_upload_completion_on_worker_01
- Added: Trace live job `job-998595bd` qua control plane va worker-01 de doi chieu pha upload/finalize cua video dai.
- Changed: Khong co thay doi code; task nay chi ghi nhan timeline production that.
- Fixed: Xac nhan case nay khong treo o YouTube Studio 100%; worker da complete thanh cong va chi cleanup output sau complete.
- Affected files: docs/WORKLOG.md, docs/CHANGELOG.md
- Impact/Risk: Khong anh huong runtime; thong tin nay xac nhan luong upload video dai hien tai dang dung cho job nay.
### 2026-04-01 12:55 - simplify_browser_upload_to_draft_footer_tracking
- Added: Them bo helper theo doi status/progress ngay tren dialog upload draft cua YouTube Studio va hanh vi dong dialog bang `X` sau khi YouTube da nhan file.
- Changed: Browser upload khong con di het wizard `Next/Next/Next/Done`; worker dung lai o buoc `Chi tiet`, theo doi footer duoi trai va dialog status de xac nhan upload.
- Fixed: Rut gon flow upload video dai, giam phu thuoc vao cac buoc cuoi cua wizard Studio va dua muc tieu ve dung nhu cau that la dua video vao `draft`.
- Affected files: workers/agent/browser_uploader.py, docs/DECISIONS.md, docs/WORKLOG.md, docs/CHANGELOG.md
- Impact/Risk: Flow moi phu thuoc vao wording/status trong dialog upload draft cua YouTube; can test bang job that tren production de chot cac token status cua YouTube Studio.
### 2026-04-01 14:30 - trace_worker_02_draft_flow_timeout_at_one_percent
- Added: Theo doi live 2 job worker-02 sau khi doi flow draft va doc state that tu `app_state.db` de phan biet stuck that voi fail nhanh.
- Changed: Khong doi code; task nay chi khoanh vung vi tri fail trong flow upload moi.
- Fixed: Xac nhan `1%` tren UI hien tai chi la moc mo browser/vao flow, khong phai YouTube upload that; hai job 10p/15p deu fail nhanh cung mot kieu `TimeoutException`.
- Affected files: docs/WORKLOG.md, docs/CHANGELOG.md
- Impact/Risk: Can bo sung debug/fallback cho giai doan mo upload dialog/file input; neu chua sua thi flow draft moi tren worker-02 van de fail som truoc khi vao editor/progress footer.
### 2026-04-01 15:20 - fail_fast_on_signed_out_browser_profiles
- Added: Detect som trang `Google Sign in` va `video-verification/selfie` ngay trong browser uploader.
- Changed: Browser upload se bao loi ro `Chrome profile cua kenh da mat dang nhap...` thay vi timeout chung chung o `1%`.
- Fixed: Loai bo case job browser upload dung gia o `1%` khi YouTube Studio thuc te da redirect ra khoi upload dialog vi profile mat login/challenge.
- Affected files: workers/agent/browser_uploader.py, docs/DECISIONS.md, docs/WORKLOG.md, docs/CHANGELOG.md
- Impact/Risk: User se phai reconnect kenh tren VPS khi profile da mat login; flow draft/footer chua the test success tren production cho toi khi co profile con dang nhap that.
### 2026-04-01 16:20 - compare_pre_draft_profile_launch_against_current
- Added: Doi chieu truc tiep launch saved profile cua commit GitHub cu (`f43c53e`) voi launch hien tai tren `worker-02`.
- Changed: Tam thoi restore launch cu de test (`--profile-directory=Default`, bo `HOME/XDG_RUNTIME_DIR`, bo stale-process cleanup), sau do tra `worker-02` ve lai ban launch hien tai.
- Fixed: Loai tru duoc gia thuyet rang flow draft moi tu ban than no da lam mo sai saved profile; ca launch cu va moi deu cung redirect sang `Google Sign in`.
- Affected files: workers/agent/browser_uploader.py, docs/WORKLOG.md, docs/CHANGELOG.md
- Impact/Risk: Blocker hien tai nam o session/profile da mat login tren VPS hoac mapping profile sai, khong phai o rieng thay doi launch code giua flow cu va flow moi.
### 2026-04-01 16:45 - verify_saved_profile_state_for_two_live_channels
- Added: Query runtime state tren control plane de map dung 2 kenh live sang 2 `browser_profile_key` hien tai.
- Changed: Mo truc tiep saved profile cua `Cozy Vibes` tren worker-01 va `Huy Phan` tren worker-02 chi de vao `studio.youtube.com`, khong dong vao flow upload.
- Fixed: Xac nhan day khong phai su co dong thoi tren tat ca kenh; `Cozy Vibes` van vao thang YouTube Studio, con `Huy Phan` moi bi redirect ve `Google Sign in`.
- Affected files: docs/WORKLOG.md, docs/CHANGELOG.md
- Impact/Risk: Hien tai chi can reconnect lai profile/kênh `Huy Phan` tren worker-02; khong nen quy loi chung cho browser uploader hay toan bo worker fleet.
### 2026-04-01 17:10 - cleanup_orphan_browser_profiles_and_compare_worker_profile_code
- Added: Query runtime `app_state(main)` de xac dinh duy nhat 2 `browser_profile_key` con duoc channel tham chieu tren production.
- Changed: Doi chieu checksum `browser_uploader.py`, `control_plane.py`, `main.py` va env worker giua `worker-01` va `worker-02` de tach biet source-code drift voi profile/session drift.
- Fixed: Don profile mo coi tren ca 2 worker, chi giu `user-1ac254308c` tren worker-01 va `user1-820833ec38` tren worker-02.
- Affected files: docs/WORKLOG.md, docs/CHANGELOG.md
- Impact/Risk: Giam nguy co nham profile cu khi debug; khac biet hien tai giua 2 worker nam o du lieu profile/session that, khong nam o source code profile-handling.
### 2026-04-01 17:31 - enable_worker_profile_cleanup_poll
- Added: Route `POST /api/workers/browser-profiles/cleanup-ack` vao worker API router dang mount that.
- Changed: `/api/workers/browser-sessions/poll` gio tra them `cleanup_profiles` de worker nhan lenh xoa browser profile sau khi xoa kenh.
- Fixed: Luong xoa kenh tren production da co the day xuong worker de xoa profile Chromium stale thay vi chi xoa mapping tren control plane.
- Affected files: backend/app/routers/api_worker.py, docs/WORKLOG.md, docs/CHANGELOG.md
- Impact/Risk: Contract poll giua control plane va worker da day du tro lai; profile stale se bi xoa that tren VPS, nen khong con ky vong tai su dung profile cu sau khi xoa kenh.
### 2026-04-01 22:05 - user render form layout 3/5 + 2/5
- Added: Cụm field mới trong `Render Config` gồm `Tên video`, `Link video loop`, `Link audio loop`, `Thời lượng render`, `Hẹn lịch đăng`, và cụm nút `Đặt lại / Render Job` đúng layout mockup.
- Changed: User dashboard chuyển form tạo job sang grid `lg:grid-cols-5`, với panel trái `col-span-3` và `My Channel` bên phải `col-span-2`; JS submit/reset chỉ còn xử lý `video_loop` và `audio_loop`.
- Fixed: Loại bỏ hoàn toàn các thành phần UI cũ không còn dùng (`Link Intro`, `Link Outro`, `Quick Settings`, `Mô tả`, counter `0/100`) để layout và hành vi form khớp ảnh mẫu.
- Affected files: `backend/app/templates/user_dashboard.html`, `backend/app/static/js/user_dashboard.js`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Backend contract giữ nguyên vì các field bỏ đi vốn optional; cần deploy template + JS cùng nhau để tránh mismatch hành vi form cũ.
### 2026-04-01 22:23 - fix mojibake login notice
- Added: Verify riêng cho login notice bằng `TestClient` và HTTP request tới process local đang chạy để phân biệt source code đúng với process cũ chưa reload.
- Changed: Các thông điệp auth trong `backend/app/store.py` được ghi lại bằng Unicode chuẩn thay vì chuỗi mojibake.
- Fixed: Notice đỏ ở màn login không còn hiện kiểu `ThÃ´ng tin Ä‘Äƒng nháº­p...`; sau restart local process, browser nhận đúng `Thông tin đăng nhập không hợp lệ.`.
- Affected files: `backend/app/store.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Nếu còn tab/browser đang hit process cũ thì phải refresh lại; không đổi contract backend, chỉ sửa text và reload process local.
### 2026-04-01 22:40 - polish user render config alignment and vps label
- Added: Thêm `worker_slot_label` riêng cho user dashboard để dòng meta kênh hiển thị theo dạng `channel_id | Bot-xx` với phần tên VPS màu slate.
- Changed: Căn lại footer action của `Render Config` để cụm `Đặt lại / Render Job` bám về bên phải, đồng thời tăng icon size bên trong ô vuông của `Render Config` và `My Channel`.
- Fixed: Ô `Hẹn lịch đăng` giờ căn giữa text ổn định và meta channel không còn hiện IP runtime thay cho alias VPS/BOT như ảnh mẫu.
- Affected files: `backend/app/templates/user_dashboard.html`, `backend/app/store.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Local demo account hiện có thể render `Bot-02` thay vì `Bot-01` tùy state gán VPS thực tế; đây là dữ liệu thật của local, không phải lệch template.
### 2026-04-01 22:48 - switch my channel vps label back to worker ip
- Added: Verify lại render HTML của user dashboard để chắc dòng meta kênh hiện trực tiếp IP VPS thật đang gắn với channel.
- Changed: Bỏ alias `Bot-01/Bot-02` trong context user dashboard và trả template về dùng `worker_label` làm nhãn VPS.
- Fixed: `My Channel` giờ hiện đúng dạng `UC... | 62.72.46.42` thay vì `UC... | Bot-02`.
- Affected files: `backend/app/templates/user_dashboard.html`, `backend/app/store.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: IP hiển thị phụ thuộc state worker hiện có trong local/prod; nếu worker name trong data đổi thì UI sẽ phản ánh đúng IP/name runtime đó.
### 2026-04-01 22:54 - style my channel worker ip as red badge
- Added: Nhãn IP VPS trong `My Channel` được bọc thành pill badge để tách rõ khỏi channel id.
- Changed: Badge VPS dùng palette `rose` với chữ đỏ, nền đỏ nhạt và viền nhẹ thay cho text slate thường.
- Fixed: Tên BOT/VPS không còn chìm trong dòng meta; phần IP nhìn nổi bật đúng ý user mà không đổi layout card.
- Affected files: `backend/app/templates/user_dashboard.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Nếu IP quá dài, badge vẫn giữ cùng dòng meta nhưng có thể chiếm thêm chiều ngang trên card hẹp.
### 2026-04-01 23:35 - deploy user dashboard badge update to production
- Added: Backup nhanh 2 file production trước khi rollout để có điểm quay lui tức thời trên host.
- Changed: Deploy bản mới của `backend/app/store.py` và `backend/app/templates/user_dashboard.html` lên control-plane `82.197.71.6`, sau đó compile và restart `youtube-upload-web.service`.
- Fixed: Production hiện đã dùng đúng UI `My Channel` mới với nhãn IP VPS dạng badge đỏ thay vì text thường/alias cũ.
- Affected files: `backend/app/store.py`, `backend/app/templates/user_dashboard.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Rollout này chỉ đụng 2 file web layer; nếu cần rollback có thể dùng ngay bản `.bak-20260401-2300` trên host.
### 2026-04-02 00:26 - add multi-vps picker for user channel connect
- Added: Popup `Chọn VPS để thêm kênh` dạng grid 2 cột cho user workspace, hiển thị IP VPS, mã `VPS-00x`, số kênh và trạng thái cơ bản để user click trực tiếp.
- Changed: Backend store/user dashboard/browser-session API giờ hỗ trợ `1 user -> nhiều VPS`; endpoint `POST /api/user/browser-sessions` nhận `worker_id` và browser session được mở trên đúng VPS được chọn.
- Fixed: Flow `+ Thêm Kênh` không còn bị khóa vào VPS đầu tiên của user; case chỉ có 1 VPS sẵn sàng vẫn đi thẳng như cũ, còn không có VPS browser-ready thì chặn rõ ràng bằng thông báo.
- Affected files: `backend/app/store.py`, `backend/app/schemas.py`, `backend/app/routers/api_user.py`, `backend/app/templates/user_dashboard.html`, `backend/app/static/js/user_dashboard.js`, `docs/PROJECT_CONTEXT.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Demo user local hiện chỉ thấy popup khi state thực tế được gán từ 2 VPS trở lên; admin assignment flow cũ vẫn còn vài giả định single-VPS ngoài phạm vi user-request lần này.
### 2026-04-02 00:45 - enable multi-vps assignment in admin workspace
- Added: Admin context giờ trả đầy đủ `assigned_workers`, `assigned_worker_count`, `assigned_worker_ids` và `current_worker_ids` để các màn `Cấp phát BOT`, `BOT của user`, `Danh sách VPS của user` hiển thị đúng nhiều VPS.
- Changed: `reconcile_assignment_target_bots`, `update_bot`, `add_user_bot`, `delete_user_bot` không còn ép user về worker đầu tiên; route admin lưu toàn bộ `worker_ids` được chọn và chỉ đóng browser session trên VPS bị gỡ.
- Fixed: Màn `Cấp phát BOT` không còn tự khóa user target về 1 card dù UI là multi-select, và các màn chi tiết admin không còn đọc sai theo worker đầu tiên.
- Affected files: `backend/app/store.py`, `backend/app/templates/admin/bot_assignment.html`, `backend/app/templates/admin/user_manager_bot.html`, `backend/app/templates/admin/bot_of_user.html`, `docs/PROJECT_CONTEXT.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Admin-side multi-VPS hiện đã đồng bộ với user workspace; vẫn cần rollout cùng toàn bộ file admin/store nếu deploy production để tránh mismatch giữa template và state logic.
### 2026-04-02 01:12 - restore optional intro input as footer toggle
- Added: Cụm toggle `Thêm Link Intro` ở footer trái của `Render Config`, mặc định ẩn và mở ra panel gọn chứa `Link intro` cùng nút upload video local khi user cần dùng intro.
- Changed: Form render user dashboard dùng khoảng trống bên trái phần action để chứa panel intro tùy chọn, giúp layout vẫn gọn và không đưa lại `Link Intro` thành field cố định.
- Fixed: JS form đã nối lại slot `intro` cho upload/reset/submit nhưng chỉ gửi `intro_url` hoặc `intro_asset_id` khi toggle được bật, tránh làm lệch flow render mặc định.
- Affected files: `backend/app/templates/user_dashboard.html`, `backend/app/static/js/user_dashboard.js`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Phần intro mới hiện phụ thuộc cache-busting qua query string JS; nếu trình duyệt giữ file JS cũ thì cần hard refresh để thấy toggle và hành vi submit đúng.
### 2026-04-02 01:46 - move intro action to render config header
- Added: Nút action `+ Thêm Intro` ở góc phải header `Render Config`, bấm lại đổi thành `− Bỏ Intro`, đồng bộ pattern với `+ Thêm Kênh`.
- Changed: `Link video Intro` được chuyển vào đúng vị trí giữa `Tên video` và `Link video loop`, mở/ẩn bằng animation nhẹ `max-height + opacity + translateY`; footer chỉ còn `Đặt lại / Render Job` căn phải như mockup.
- Fixed: Khi bấm `− Bỏ Intro`, frontend xóa sạch link, file local, upload session và hidden asset của slot `intro`, tránh giữ state cũ sau khi section bị ẩn.
- Affected files: `backend/app/templates/user_dashboard.html`, `backend/app/static/js/user_dashboard.js`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Trình duyệt cần lấy file JS mới `?v=20260402-intro-header-1`; nếu tab đang mở trước đó thì phải hard refresh để bỏ cache UI cũ.
### 2026-04-02 02:02 - normalize render form control heights and hidden intro spacing
- Added: Quy tắc spacing cho `introSlotPanel` ẩn bằng `!mt-0` để section intro không còn giữ khoảng cách thừa trong layout `space-y-5`.
- Changed: `panel-input` được nâng lên `42px` và các input trong upload rows (`intro`, `video loop`, `audio loop`) được đồng bộ về `h-[40px]` để toàn bộ control trong `Render Config` nhìn cùng một nhịp cao.
- Fixed: Khoảng cách giữa `Tên video` và `Link video loop` trở lại đều như các cặp field khác khi intro đang ẩn; text active vẫn là `− Bỏ Intro`.
- Affected files: `backend/app/templates/user_dashboard.html`, `backend/app/static/js/user_dashboard.js`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Nếu tab còn cache HTML/JS cũ, cần hard refresh để thấy spacing mới và hành vi ẩn intro không để lại gap.
### 2026-04-02 02:15 - fix local upload button file picker
- Added: Quy ước mới cho `data-upload-trigger`: cùng một listener xử lý cả mở file picker khi state `idle` và clear upload khi state không còn `idle`.
- Changed: `initFileInputs()` không còn bind click mở picker riêng; template bump query string JS sang `?v=20260402-upload-picker-fix-1` để buộc client lấy bundle mới.
- Fixed: Nút upload local trên workspace không còn phụ thuộc vào hai click listener chồng nhau, giảm lỗi bấm upload mà không mở file picker trên local browser.
- Affected files: `backend/app/static/js/user_dashboard.js`, `backend/app/templates/user_dashboard.html`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Nếu browser vẫn giữ HTML cũ thì cần hard refresh; sau khi lấy JS mới, upload picker sẽ mở lại bình thường trên local.
### 2026-04-02 02:25 - restore old upload ux feedback on local form
- Added: Ưu tiên `showPicker()` cho browser hỗ trợ khi bấm nút upload local, fallback về `input.click()` để khôi phục cảm giác chọn file trực tiếp như trước.
- Changed: Flow upload local vẫn giữ nguyên pipeline cũ `startSlotUpload -> uploadLocalFile -> setSlotStatus/setUploadVisual`, nên tiếp tục hiển thị `Đang chuẩn bị upload...`, phần trăm/progress ring, `Sẵn sàng`, và `Hoàn tất`.
- Fixed: Hành vi nút upload được kéo về đúng bản trước khi đổi UI: `idle` là mở file picker, còn khi đang upload/đã upload thì chính nút đó dùng để hủy/xóa upload state.
- Affected files: `backend/app/static/js/user_dashboard.js`, `backend/app/templates/user_dashboard.html`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Client cần lấy JS mới `?v=20260402-upload-behavior-restore-1`; nếu tab cũ chưa hard refresh thì vẫn có thể thấy hành vi không đồng nhất.
### 2026-04-02 02:33 - add browser-safe fallback for local file picker
- Added: Helper `openSlotFilePicker()` để mở file picker theo hai lớp fallback: thử `showPicker()`, nếu lỗi thì tạm bỏ class `hidden`, đẩy input ra ngoài viewport rồi `click()` thủ công.
- Changed: Click handler của `data-upload-trigger` giờ gọi helper này thay vì trực tiếp `showPicker()/click()`, còn template bump cache key JS sang `?v=20260402-picker-fallback-1`.
- Fixed: Case local browser vẫn không mở picker dù đã gộp listener nay có thêm fallback cho trình duyệt chặn thao tác trên `input type=file` đang `display:none`.
- Affected files: `backend/app/static/js/user_dashboard.js`, `backend/app/templates/user_dashboard.html`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Cần hard refresh để lấy JS mới; nếu browser extension/chính sách OS chặn file dialog thì vẫn phải kiểm tra thêm ngoài app.
### 2026-04-02 02:44 - deploy local control-plane and worker updates to vps
- Added: Rollout toàn bộ thay đổi runtime local hiện tại lên control-plane `82.197.71.6` và 2 worker `62.72.46.42`, `109.123.233.131`, kèm backup live trước khi ghi đè.
- Changed: Control-plane nhận bản mới của `backend/app/...`; hai worker nhận bộ agent mới gồm `control_plane.py`, `main.py`, `browser_runtime.py`, `browser_sessions.py`, `browser_uploader.py`.
- Fixed: Production hiện đã đồng bộ với local cho các thay đổi multi-VPS, UI/user dashboard, và worker browser-session/upload agent thay vì chỉ dừng ở môi trường local.
- Affected files: `backend/app/routers/api_user.py`, `backend/app/routers/api_worker.py`, `backend/app/routers/web.py`, `backend/app/schemas.py`, `backend/app/static/js/user_dashboard.js`, `backend/app/store.py`, `backend/app/templates/admin/bot_assignment.html`, `backend/app/templates/admin/bot_of_user.html`, `backend/app/templates/admin/user_index.html`, `backend/app/templates/admin/user_manager_bot.html`, `backend/app/templates/admin/worker_index.html`, `backend/app/templates/user_dashboard.html`, `workers/agent/control_plane.py`, `workers/agent/main.py`, `workers/agent/browser_runtime.py`, `workers/agent/browser_sessions.py`, `workers/agent/browser_uploader.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Backup live nằm ở `/opt/youtube-upload-lush/.deploy-backups/20260401-185959/control`, `/opt/youtube-upload-lush/.deploy-backups/20260401-190113/worker`, `/opt/youtube-upload-lush/.deploy-backups/20260401-190128/worker`; journal của worker vẫn hiển thị vài failure cũ trước thời điểm restart, nhưng sau rollout cả `youtube-upload-web.service` và `youtube-upload-worker.service` đều trở lại `active`.
### 2026-04-02 03:19 - remove duplicate detected-channel card from browser modal
- Added: Cache key JS mới `?v=20260402-modal-cleanup-1` để client lấy đúng bản modal đã dọn.
- Changed: Modal browser session bỏ hẳn card `Chưa nhận diện được kênh...` ở cuối; JS cũng không còn giữ node/update text cho block này.
- Fixed: Popup đăng nhập kênh không còn lặp thông tin xác nhận kênh ở phần dưới cùng, giúp modal ngắn và sạch hơn.
- Affected files: `backend/app/templates/user_dashboard.html`, `backend/app/static/js/user_dashboard.js`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Đã deploy lên `82.197.71.6`; nếu tab đang mở từ trước thì cần hard refresh để thấy modal gọn lại.

### 2026-04-02 08:39 - unify notices and add search affordances
- Added: Searchable role assignment select for manager/admin pages, search input inside channel picker, transient admin/user notice behavior with close button and 5s auto-hide, and toast stack for user workspace feedback.
- Changed: Admin role assignment now chooses real users from system data instead of blind free-text input; My Channel list now scrolls inside the panel when long.
- Fixed: Sticky notices that did not dismiss, browser/session/user dashboard alerts that still used window.alert, and channel picker usability when many channels exist.
- Affected files: backend/app/store.py, backend/app/templates/admin/user_role_list.html, backend/app/templates/admin/_admin_notice.html, backend/app/templates/admin/_layout.html, backend/app/static/js/admin_tables.js, backend/app/templates/user_dashboard.html, backend/app/static/js/user_dashboard.js.
- Impact/Risk: UI-only/admin-control changes; requires hard refresh to pick up new dashboard JS query string and re-test admin role assignment on local/prod after deploy.

### 2026-04-02 09:04 - deploy notice search scroll patch to production
- Added: Production backup snapshot for the deployed web/admin patch at /opt/youtube-upload-lush/.deploy-backups/20260402-090428-notice-role-search-post.
- Changed: Live control-plane on 82.197.71.6 now serves the new transient notice behavior, searchable role assignment, searchable channel picker, and My Channel internal scroll.
- Fixed: Production drift for this patch is closed; service restart and health/login verification completed after rollout.
- Affected files: backend/app/store.py, backend/app/static/js/admin_tables.js, backend/app/static/js/user_dashboard.js, backend/app/templates/admin/_admin_notice.html, backend/app/templates/admin/_layout.html, backend/app/templates/admin/user_role_list.html, backend/app/templates/user_dashboard.html.
- Impact/Risk: Web-only deploy on control-plane; worker VPS were intentionally left untouched because this patch does not change worker runtime.

### 2026-04-02 09:11 - polish admin credential copy and close icons
- Added: Production backup snapshot for the icon/font/copy polish at /opt/youtube-upload-lush/.deploy-backups/20260402-091151-icon-font-credential-copy-post.
- Changed: Admin notice/toast close controls now use Lucide x; credential copy now reads Đã băm mật khẩu instead of exposing PBKDF2 hash directly to operators.
- Fixed: Mojibake bullet in role-list Meta column (â€¢) and inconsistent close glyph rendering in admin/user transient messages.
- Affected files: backend/app/store.py, backend/app/templates/admin/_admin_notice.html, backend/app/templates/admin/_layout.html, backend/app/static/js/user_dashboard.js.
- Impact/Risk: Web-only patch on control-plane; requires refresh to see the updated icon/copy on live pages.

### 2026-04-02 09:26 - switch success notices to lucide check and simplify password copy
- Added: Production backup snapshot for this rollout at `/opt/youtube-upload-lush/.deploy-backups/20260402-093050-icon-check-password-copy`.
- Changed: Admin/user success notices now use Lucide `circle-check`; admin role list header now reads `Mật khẩu`; password-state copy now reads `Đã đặt mật khẩu`, `Cần đổi lại mật khẩu`, or `Chưa đặt mật khẩu`.
- Fixed: Success notice no longer depends on the previous verify-style glyph, and the role list no longer shows a technical hash-oriented label that is hard to read for operators.
- Affected files: `backend/app/store.py`, `backend/app/templates/admin/_admin_notice.html`, `backend/app/templates/admin/user_role_list.html`, `backend/app/templates/user_dashboard.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Low-risk web-only patch on control-plane; production restart and health/login checks passed after deploy.

### 2026-04-02 09:57 - align bot assignment stat badges with app badge system
- Added: Production backup snapshot for this rollout at `/opt/youtube-upload-lush/.deploy-backups/20260402-095713-bot-assignment-badges`.
- Changed: `Cấp phát BOT` stat badges (`Trống`, `Đã cấp`, `Offline`) now use the same outlined semantic-chip treatment as the rest of the app: thin border, lighter tinted background, tighter spacing, and calmer text sizing.
- Fixed: The screen no longer uses a separate heavy pill style for these counters, reducing visual drift from the app-wide badge language.
- Affected files: `backend/app/templates/admin/bot_assignment.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Low-risk template-only polish; deployed and verified on production `82.197.71.6`.

### 2026-04-02 10:00 - remove outer card shell from bot assignment view toggle
- Added: Production backup snapshot for this rollout at `/opt/youtube-upload-lush/.deploy-backups/20260402-100021-bot-assignment-toggle`.
- Changed: The `grid/list` switch in `Cấp phát BOT` no longer sits inside its own bordered card; the two Lucide icon buttons now live directly on the panel surface with subtle hover and brand-tinted active state.
- Fixed: The toggle cluster now matches the lighter badge/action language used elsewhere in the app instead of introducing another boxed control style.
- Affected files: `backend/app/templates/admin/bot_assignment.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Low-risk template-only polish; deployed and verified on production `82.197.71.6`.

### 2026-04-02 10:11 - switch bot assignment target header icon to standard lucide glyph
- Added: Production backup snapshot for this rollout at `/opt/youtube-upload-lush/.deploy-backups/20260402-101116-bot-assignment-header-icon`.
- Changed: The `Gán cho người nhận` header in `Cấp phát BOT` now uses Lucide `user-plus` instead of `user-round-plus` to match the rest of the app’s icon language.
- Fixed: The target-panel header no longer feels visually off compared with other Lucide controls in the admin shell.
- Affected files: `backend/app/templates/admin/bot_assignment.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Low-risk template-only polish; deployed and verified on production `82.197.71.6`.

### 2026-04-02 10:45 - stabilize browser draft upload completion tracking
- Added: Production backup snapshot for both workers at `/opt/youtube-upload-lush/.deploy-backups/20260402-1045-upload-draft-fix` and a recovered live watch URL for stuck job `job-35c08c71`.
- Changed: `workers/agent/job_runner.py` is now aligned with the production browser-upload path locally; `workers/agent/browser_uploader.py` now emits periodic keepalive updates, trims noisy dialog status text, and probes YouTube Studio content list in a background tab before declaring draft upload complete.
- Fixed: Browser-upload jobs no longer have to wait for the dialog footer to expose a perfect `100%` signal before the app can move past `91-94%`; the live stuck draft `job-35c08c71` was recovered to `completed` with `https://www.youtube.com/watch?v=v4GRMKIc5kE`.
- Affected files: `workers/agent/job_runner.py`, `workers/agent/browser_uploader.py`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Worker-only runtime patch deployed to `62.72.46.42` and `109.123.233.131`; control-plane web service was briefly restarted to reload the recovered job state.

### 2026-04-02 13:10 - close draft upload from footer completion state after 5-second settle
- Added: Production backup snapshot for both workers at `/opt/youtube-upload-lush/.deploy-backups/20260402-1310-footer-state-close-delay`.
- Changed: `workers/agent/browser_uploader.py` now recognizes the YouTube footer state equivalent to `Đã hoàn tất quá trình tải lên ... Quá trình xử lý sẽ sớm bắt đầu`, waits about 5 seconds, then lets the flow close the dialog into Drafts.
- Fixed: The worker no longer has to guess only from generic `100% uploaded` or background heuristics; it now follows the exact runtime state sequence the user captured from Studio, while still preventing content-list fast-path from closing too early.
- Affected files: `workers/agent/browser_uploader.py`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Worker-only patch deployed to `62.72.46.42` and `109.123.233.131`; control-plane code was unchanged.

### 2026-04-02 12:40 - migrate project memory to lean bootstrap workflow
- Added: `docs/PROJECT_BRIEF.md`, `docs/MEMORY_INDEX.md`, `docs/DECISIONS_INDEX.md`, va bo `docs/modules/*.md` de bootstrap theo module thay vi doc full history.
- Changed: Root `AGENTS.md` chuyen sang che do hybrid, bootstrap mac dinh bang `PROJECT_BRIEF + MEMORY_INDEX`, con `PROJECT_CONTEXT/DECISIONS/WORKLOG/CHANGELOG` duoc giu lai cho lich su va tuong thich nguoc.
- Fixed: Giam nguy co phinh context khi lam viec voi repo lon; task moi khong con bi buoc doc full `DECISIONS.md` va `WORKLOG.md` truoc moi buoc sua code.
- Affected files: `AGENTS.md`, `docs/PROJECT_BRIEF.md`, `docs/MEMORY_INDEX.md`, `docs/DECISIONS_INDEX.md`, `docs/modules/backend-app.md`, `docs/modules/user-workspace.md`, `docs/modules/admin-workspace.md`, `docs/modules/worker-control-plane.md`, `docs/modules/infra-runtime.md`, `docs/PROJECT_CONTEXT.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Workflow cu van chay duoc vi cac file legacy khong bi xoa, nhung can follow root `AGENTS.md` moi de huong dan task ve dung lop memory ngan.

### 2026-04-02 12:13 - wire cgraph retrieval into migrated workflow
- Added: FalkorDB graph `youtube-bot-upload` cho repo nay de phuc vu retrieval-first khi task lon hoac kho xac dinh entry point.
- Changed: `docs/MEMORY_INDEX.md` gio ghi ro ten graph va command mac dinh `cgraph info/search --repo youtube-bot-upload`.
- Fixed: Khong can doan graph name hay rerun full index sau moi task; agent co the query thang graph san co truoc khi mo nhieu file.
- Affected files: `docs/MEMORY_INDEX.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: Graph hien tai da dung duoc ngay, nhung can re-index lai khi cau truc repo doi lon hoac node/edge ro rang khong con phan anh code moi.

### 2026-04-02 12:33 - unify draft upload label with uploaded state
- Changed: Completed job luu o `YouTube Studio` dang `Bản nháp` gio cung hien nhan `Đã upload YouTube` thay vi copy rieng, de nguoi van hanh nhin nhanh khong bi tach nghia giua draft va uploaded.
- Fixed: Bo copy `Đã gửi YouTube`/`Đã lưu bản nháp` o user render list, vi no gay nham la app chua upload xong du video da duoc YouTube nhan va luu thanh draft.
- Affected files: `backend/app/store.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Deploy: Rolled out len `82.197.71.6`, backup live tai `/opt/youtube-upload-lush/.deploy-backups/20260402-123332-uploa2-cop26-uni526`, restart `youtube-upload-web.service`, verify `job-65174889` tra nhan `Đã upload YouTube` va `/api/health = {"status":"ok"}`.

### 2026-04-02 12:46 - remove browser upload marker and lock title rule
- Changed: Worker browser uploader khong con chen `[job-marker:...]` vao mo ta metadata; xac nhan draft/background probing gio dua tren title thuc te trong YouTube Studio sau khi dialog upload da chot.
- Changed: Form `Tên video` va API tao job gio chi nhan toi da `100` ky tu, va chi cho phep chu Latin ASCII, so, va khoang trang.
- Affected files: `workers/agent/browser_uploader.py`, `backend/app/routers/api_user.py`, `backend/app/templates/user_dashboard.html`, `backend/app/static/js/user_dashboard.js`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall backend/app workers/agent`, `node --check backend/app/static/js/user_dashboard.js`, va smoke helper `_validate_job_title(...)` cho ca case hop le/khong hop le.

### 2026-04-02 13:21 - add direct noVNC clipboard shortcuts
- Changed: Browser session worker khong con serve noVNC web root thang tu `/usr/share/novnc`; moi session dung mot web root rieng duoc sinh tu stock asset va chen them module `paste_shortcuts.js`.
- Changed: noVNC gio ho tro dan truc tiep bang `Ctrl+V` khi phien remote dang focus, dong thoi pass-through cac to hop sua noi dung thong dung (`Ctrl+A/C/X/Z/Y`) vao desktop tu xa thay vi ep nguoi dung mo panel clipboard ben trai.
- Affected files: `workers/agent/browser_runtime.py`, `workers/agent/novnc_overlay/paste_shortcuts.js`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall workers/agent` va smoke helper `_prepare_novnc_web_dir(...)` de xac nhan `vnc.html` duoc chen script `paste_shortcuts.js`.

### 2026-04-02 13:34 - remove title helper copy for tighter form spacing
- Changed: Bo dong helper text duoi field `Tên video` trong form `Render Config` de khoang cach giua `Tên video` va `Link video loop` quay lai deu nhu cac hang khac.
- Affected files: `backend/app/templates/user_dashboard.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall backend/app`

### 2026-04-02 14:06 - preserve cancelled jobs when worker reports late
- Changed: Worker loop bo qua `409 Conflict` muon tu cac route `/api/workers/jobs/*` khi job da bi user huy, de khong goi `fail_job(...)` va khong ghi de job sang trang thai `error`.
- Changed: Control plane giu nguyen status `cancelled` neu worker van goi `/fail` sau khi job da bi huy, thay vi doi thanh `error`.
- Affected files: `workers/agent/main.py`, `backend/app/store.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall backend/app workers/agent`

### 2026-04-02 14:12 - exclude cancelled jobs from error KPI
- Changed: User KPI `Xử lý lỗi` va admin summary `failed_jobs` chi con dem job `error`; job `cancelled` duoc xem la ket thuc hop le theo y nguoi dung, khong con bi cong vao KPI loi.
- Affected files: `backend/app/store.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall backend/app`

### 2026-04-02 14:49 - stabilize worker upload title, progress, and draft completion
- Changed: `workers/agent/job_runner.py` tao ban sao file upload theo title sach thay vi prefix `job-id`; `workers/agent/browser_uploader.py` set/verify title trong dialog, khong cho upload progress di lui, chi complete sau khi xac nhan row draft tren Studio, va salvage thanh cong neu DOM upload dialog bi `StaleElementReferenceException` o cuoi qua trinh.
- Affected files: `workers/agent/job_runner.py`, `workers/agent/browser_uploader.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall workers/agent`

### 2026-04-02 14:49 - rebalance render progress by phase
- Changed: `workers/agent/ffmpeg_pipeline.py` doi render progress sang cac pha `prepare assets`, `build sequence`, `concat output` de progress bar khong dung o moc thap trong luc ffmpeg van chuan hoa/tao file trung gian.
- Affected files: `workers/agent/ffmpeg_pipeline.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall workers/agent`

### 2026-04-02 15:20 - switch browser upload completion to footer-only
- Changed: `workers/agent/browser_uploader.py` bo logic match row trong YouTube Studio content list; worker gio chi theo doi footer dialog va coi upload thanh cong khi sau moc `100%` footer chuyen sang trang thai hau-upload nhu `processing will begin shortly`, `delayed for hours`, hoac `saved as draft/private`, giu 5 giay roi dong dialog.
- Affected files: `workers/agent/browser_uploader.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall workers/agent`

### 2026-04-02 15:20 - remove youtube watch URL dependency from app
- Changed: `workers/agent/job_runner.py` khong con gui `output_url` cho browser upload complete; `backend/app/templates/user_dashboard.html` bo nut `Xem`, vi app khong con phu thuoc vao `watch URL` de coi upload thanh cong.
- Affected files: `workers/agent/job_runner.py`, `backend/app/templates/user_dashboard.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall workers/agent backend/app`

### 2026-04-02 15:37 - complete upload on any footer-state change after 100%
- Changed: `workers/agent/browser_uploader.py` khong con yeu cau footer phai vao mot nhom trang thai cu the sau `100%`; worker gio luu footer text tai moc `100%`, va neu footer doi sang bat ky text khac nao trong 5 giay thi dong dialog va complete ngay.
- Affected files: `workers/agent/browser_uploader.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall workers/agent`

### 2026-04-02 16:08 - simplify browser upload to telemetry-only runtime
- Changed: `workers/agent/browser_uploader.py` bo toan bo logic cu phu thuoc `content-list row`, `watch URL`, `draft URL` va chi giu dialog/footer lam nguon telemetry `%/status`; completion gio success-biased theo worker/browser state thay vi doi YouTube row confirm.
- Affected files: `workers/agent/browser_uploader.py`, `workers/agent/downloader.py`, `backend/app/store.py`, `backend/app/schemas.py`, `backend/app/static/js/user_dashboard.js`, `docs/DECISIONS.md`, `docs/DECISIONS_INDEX.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall workers/agent`, `python -m compileall backend/app`, `node --check backend/app/static/js/user_dashboard.js`

### 2026-04-02 16:21 - keep cancel button disabled after job completion
- Changed: `backend/app/static/js/user_dashboard.js` bo nut `Sửa` khoi action cell va giu nut `Hủy` o trang thai disabled mau xam sau khi job da ket thuc; `backend/app/templates/user_dashboard.html` bump cache key de client lay JS moi ngay.
- Affected files: `backend/app/static/js/user_dashboard.js`, `backend/app/templates/user_dashboard.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `node --check backend/app/static/js/user_dashboard.js`, `python -m compileall backend/app`

### 2026-04-02 16:25 - deploy telemetry-only upload runtime to production
- Changed: rollout `backend/app/store.py`, `backend/app/schemas.py`, `backend/app/static/js/user_dashboard.js`, `backend/app/templates/user_dashboard.html` len control-plane `82.197.71.6`, va `workers/agent/browser_uploader.py`, `workers/agent/downloader.py`, `workers/agent/job_runner.py` len worker `62.72.46.42` va `109.123.233.131`.
- Affected files: production runtime under `/opt/youtube-upload-lush/*`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `systemctl is-active youtube-upload-web.service`, `systemctl is-active youtube-upload-worker.service`, `curl http://127.0.0.1:8000/api/health`, grep live template/js markers on production

### 2026-04-02 16:39 - switch audio_loop back to old fast-path
- Changed: `workers/agent/ffmpeg_pipeline.py` bo re-encode `audio_loop` sang mp3; worker gio copy audio goc vao render dir, cat bang `-c copy`, va giu nguyen suffix/codec de bam sat flow cua app cu va giam thoi gian render.
- Affected files: `workers/agent/ffmpeg_pipeline.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall workers/agent`

### 2026-04-02 17:02 - deploy audio_loop fast-path to workers
- Changed: rollout `workers/agent/ffmpeg_pipeline.py` len worker `62.72.46.42` va `109.123.233.131`.
- Affected files: production worker runtime under `/opt/youtube-upload-lush/workers/agent/ffmpeg_pipeline.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: remote `python3 -m compileall workers/agent`, `systemctl is-active youtube-upload-worker.service`

### 2026-04-02 17:28 - fix stuck browser upload footer parser
- Changed: `workers/agent/browser_uploader.py` khong con fallback `status_message` sang full dialog text, uu tien footer/parser moi thay vi body-text `%` cu, va coi cac trang thai hau-upload nhu `Đã lưu ở chế độ riêng tư / bản nháp` hoac processing sau upload la completion hop le.
- Affected files: `workers/agent/browser_uploader.py`, production workers `62.72.46.42`, `109.123.233.131`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall workers/agent`, remote `python3 -m compileall workers/agent`, `systemctl is-active youtube-upload-worker.service`

### 2026-04-02 17:27 - recover production job job-1f073e41 from false upload error
- Changed: sau khi xac nhan control-plane da nhan status thuc `Đã lưu ở chế độ riêng tư`, patch state SQLite va restart `youtube-upload-web.service` de reload state RAM, dua `job-1f073e41` ve `completed` voi thong diep `Đã upload YouTube`.
- Affected files: production app state `/opt/youtube-upload-lush-runtime/backend-data/app_state.db`, service `youtube-upload-web.service`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: query live app state tren `82.197.71.6` sau restart cho thay `status=completed`, `upload_progress=100`, `error_message=null`

### 2026-04-02 17:37 - simplify browser upload completion to 100%-only rule
- Changed: `workers/agent/browser_uploader.py` bo hoan toan logic doi footer doi trang thai sau 100%; worker gio chi can thay `100%`, cho ~5 giay de on dinh, dong dialog, va complete ngay. Van giu dialog/footer chi de lay `%` va message telemetry.
- Affected files: `workers/agent/browser_uploader.py`, production workers `62.72.46.42`, `109.123.233.131`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall workers/agent`, remote `python3 -m compileall workers/agent`, `systemctl is-active youtube-upload-worker.service`

### 2026-04-02 18:00 - prune legacy upload completion helpers
- Changed: `workers/agent/browser_uploader.py` duoc don lai ve mot state machine ro rang hon: xoa helper di san `_is_post_upload_state` va `_has_transfer_completed_signal`, bo parser body-text cho upload progress, va them `_read_upload_dialog_text` de telemetry chi bam vao dialog upload that.
- Affected files: `workers/agent/browser_uploader.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall workers/agent`

### 2026-04-02 18:30 - reduce worker progress timeout risk on long renders
- Changed: `workers/agent/main.py` tang timeout HTTP cua worker khi noi voi control-plane (`connect=20s, read/write=120s`) va `workers/agent/job_runner.py` them throttle cho progress update de tranh spam hang tram request `/progress` trong luc render/download file dai.
- Affected files: `workers/agent/main.py`, `workers/agent/job_runner.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall workers/agent`

### 2026-04-02 18:41 - allow Vietnamese titles in render form
- Changed: `backend/app/templates/user_dashboard.html` bo `pattern` HTML native, `backend/app/static/js/user_dashboard.js` cho phep Unicode letters/numbers thay vi Latin-only, va `backend/app/routers/api_user.py` doi backend validator sang `unicodedata.category` de nhan duoc ten video co dau tieng Viet.
- Affected files: `backend/app/templates/user_dashboard.html`, `backend/app/static/js/user_dashboard.js`, `backend/app/routers/api_user.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `node --check backend/app/static/js/user_dashboard.js`, `python -m compileall backend/app`

### 2026-04-02 18:53 - center STT column in render table
- Changed: `backend/app/templates/user_dashboard.html` can giua header va cell cua cot `STT`, dong thoi giam padding/widening khong can thiet; `backend/app/static/js/user_dashboard.js` cap nhat row markup dong de alignment nay giu nguyen sau moi lan render lai bang.
- Affected files: `backend/app/templates/user_dashboard.html`, `backend/app/static/js/user_dashboard.js`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `node --check backend/app/static/js/user_dashboard.js`, `python -m compileall backend/app`

### 2026-04-03 00:14 - align My Channel header and group channels by VPS
- Changed: `backend/app/templates/user_dashboard.html` dua nut `+ Thêm Kênh` len goc phai tren, them search bar ben duoi theo dung style field tren trang, filter card channel theo cac thuoc tinh dang hien tren card, va rut gon sidebar chi con `Điều phối Render`. `backend/app/store.py` sap xep `connected_channels` theo VPS de cac kenh cung worker nam lien nhau du them truoc hay sau.
- Affected files: `backend/app/templates/user_dashboard.html`, `backend/app/static/js/user_dashboard.js`, `backend/app/store.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `node --check backend/app/static/js/user_dashboard.js`, `python -m compileall backend/app`

### 2026-04-03 00:26 - add VPS status/count badge details in My Channel
- Changed: `backend/app/store.py` bo sung `worker_status_dot_class` va `worker_channel_count` cho tung `connected_channel`; `backend/app/templates/user_dashboard.html` render badge VPS moi voi dot xanh truoc IP va dot do + so kenh o cuoi; `backend/app/static/js/user_dashboard.js` bo xu ly empty card vi `My Channel` khong con hien hop `Khong tim thay kenh phu hop`.
- Affected files: `backend/app/store.py`, `backend/app/templates/user_dashboard.html`, `backend/app/static/js/user_dashboard.js`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `node --check backend/app/static/js/user_dashboard.js`, `python -m compileall backend/app`

### 2026-04-03 00:33 - restore red VPS label text and bullet separator
- Changed: `backend/app/templates/user_dashboard.html` doi text IP/VPS trong badge ve mau do va thay dot element truoc `x kênh` bang ky tu `•` de giong giao dien tham chieu; dong thoi bump cache key JS de browser lay ngay template moi.
- Affected files: `backend/app/templates/user_dashboard.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall backend/app`

### 2026-04-03 00:39 - make badge suffix fully red
- Changed: `backend/app/templates/user_dashboard.html` doi luon ky tu `•` va text `x kênh` trong badge VPS sang `text-rose-600` de toan bo suffix dong bo mau do.
- Affected files: `backend/app/templates/user_dashboard.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall backend/app`

### 2026-04-03 01:18 - open render workspace for admin and manager
- Changed: `backend/app/routers/web.py` bridge `admin session -> app session` khi vao `/app`; `backend/app/auth.py` va `backend/app/routers/api_user.py` mo workspace/API cho role `user/manager/admin`; `backend/app/store.py` thay workspace scope theo role, them nav item `Điều phối Render` vao sidebar admin, va doi copy workspace/logout path theo role.
- Affected files: `backend/app/auth.py`, `backend/app/routers/api_user.py`, `backend/app/routers/web.py`, `backend/app/store.py`, `docs/DECISIONS_INDEX.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall backend/app`, `node --check backend/app/static/js/user_dashboard.js`, `python` smoke test voi `TestClient` (`admin/manager -> /app`, `/api/user/bootstrap = 200`, bot assignment co target `user:admin-1`)

### 2026-04-03 01:31 - keep admin sidebar inside render workspace
- Changed: `backend/app/templates/user_dashboard.html` doi sidebar sang render theo `dashboard.nav_items`; `backend/app/store.py` bo sung `active_page + nav_items` cho workspace render, de `admin/manager` vao `/app` van thay full sidebar quan tri va `user` van giu sidebar mot muc.
- Affected files: `backend/app/templates/user_dashboard.html`, `backend/app/store.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall backend/app`, `python` smoke test HTML (`admin/manager /app` co links `/admin/user/index`, `/admin/ManagerBOT/index`, `/admin/bot/assignment`, `/admin/channel/index`, `/admin/render/index`, `/app`)

### 2026-04-03 14:00 - redirect HTML routes to login after render-workspace logout
- Changed: `backend/app/main.py` them `HTTPException` handler cho non-API HTML route de `/admin/*` va `/app` mat session se redirect ve `/login?next=...` thay vi tra `401 JSON`; `backend/app/routers/web.py` dong bo `/logout` xoa ca app/admin session bridge de admin dang o render workspace logout xong khong con tab nao bi den man hinh.
- Affected files: `backend/app/main.py`, `backend/app/routers/web.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall backend/app`, `python` smoke test voi `TestClient` (`admin -> /app -> POST /admin/logout -> /admin/render/index = 302 /login?next=%2Fadmin%2Frender%2Findex`, `/app = 302 /login?next=/app`)

### 2026-04-03 14:11 - merge password reset into edit-user flow
- Changed: `backend/app/templates/admin/user_index.html` bo action `Reset pass`, doi modal `Sửa user` thanh form sua `username + pass + manager`, va thay dong thong tin phu tren bang thanh `@username`; `backend/app/templates/admin/user_edit.html` dong bo cung field moi; `backend/app/store.py` doi admin user update sang `display_name = username` va chi reset password khi field `Pass` co gia tri; `backend/app/routers/web.py` cho `/admin/user/resetpassword` GET redirect ve `/admin/user/edit`.
- Affected files: `backend/app/templates/admin/user_index.html`, `backend/app/templates/admin/user_edit.html`, `backend/app/store.py`, `backend/app/routers/web.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall backend/app`, `python` smoke test voi `TestClient` (`/admin/user/index` khong con `Reset pass`, modal co `name=\"Password\"`, `/admin/user/resetpassword` => `302 /admin/user/edit?...`, submit `/admin/user/updatetelegram` van update duoc password)

### 2026-04-03 14:19 - show current password inside edit-user surfaces
- Changed: `backend/app/store.py` mo rong `auth_credentials` voi `password_plain`, luu/nạp lai pass plain de admin UI co the prefill field `Pass`; `backend/app/templates/admin/user_index.html` dua `data-password` vao nut `Sửa`; `backend/app/templates/admin/user_edit.html` hien sẵn pass hien tai trong field `Pass`.
- Affected files: `backend/app/store.py`, `backend/app/templates/admin/user_index.html`, `backend/app/templates/admin/user_edit.html`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall backend/app`, `python` smoke test voi `TestClient` (`data-password=\"manager123\"`, `value=\"manager123\"`, submit doi pass thanh `manager999` thi UI feed lai gia tri moi)

### 2026-04-03 14:57 - separate BOT edit modal from BOT assignment
- Changed: `backend/app/templates/admin/worker_index.html` doi modal `Cập nhật BOT` thanh 3 field `Tên BOT / Group / Manager`, bo `Chọn user`, va khoa manager select khi viewer la manager; `backend/app/store.py` doi `update_bot()` thanh flow chi sua `name/group/manager`, giu user assignment hien co va chan doi manager neu BOT dang gan cho user thuoc manager khac; `backend/app/routers/web.py` va `backend/app/routers/api_admin.py` dong bo payload/route theo contract moi.
- Affected files: `backend/app/templates/admin/worker_index.html`, `backend/app/store.py`, `backend/app/routers/web.py`, `backend/app/routers/api_admin.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall backend/app`, `python` smoke test voi `TestClient` (`admin /admin/ManagerBOT/index` co field `Group`, khong con `Chọn user`; `manager /admin/ManagerBOT/index` co hidden self binding + manager select disabled; POST `/admin/bot/update` tu manager van bi force vao manager cua chinh ho)

### 2026-04-03 15:16 - simplify manager-scoped user creation and remove BOT assignment nav
- Changed: `backend/app/templates/admin/user_create.html` rewrite lai UTF-8 de het mojibake; `backend/app/store.py` bo ep `user` phai co manager, cho `manager` tabs an `Manager/Admin`, va go nav `Cấp phát BOT` khoi `_admin_nav_items`; `backend/app/routers/web.py` truyen `viewer_role` vao cac context user de manager chi thay dung tabs va manager field lock scope cua chinh ho.
- Affected files: `backend/app/templates/admin/user_create.html`, `backend/app/store.py`, `backend/app/routers/web.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall backend/app`, `python` smoke test voi `TestClient` (admin tao user voi `manager_id=''` thanh cong, manager create page khong con tabs `Manager/Admin`, sidebar khong con `Cấp phát BOT`, manager tao user moi van bi force ve `manager-1`)

### 2026-04-03 16:05 - move all BOT control into BOT list and lock manager BOT scope
- Changed: `backend/app/templates/admin/_manager_picker.html` render manager-scope picker cua manager thanh badge tinh khong co nut `x`; `backend/app/templates/admin/user_index.html` va `backend/app/templates/admin/user_manager_bot.html` doi toan bo link `BOT` sang `/admin/ManagerBOT/index`; `backend/app/routers/web.py` redirect `/admin/bot/assignment` va `/admin/bot/assign` ve `Danh sách BOT`.
- Changed: `backend/app/templates/admin/worker_index.html` duoc rewrite UTF-8 sach; manager-side modal `Sửa BOT` doi sang `Tên BOT + manager khóa scope + Chọn user searchable`, admin-side giu `Tên BOT + Group + Chọn manager`; `backend/app/store.py` mo rong `update_bot()` de manager doi user assignment ngay tai `Danh sách BOT` va bo guard/message cu nhac `Cấp phát BOT`.
- Affected files: `backend/app/templates/admin/_manager_picker.html`, `backend/app/templates/admin/user_index.html`, `backend/app/templates/admin/user_manager_bot.html`, `backend/app/templates/admin/worker_index.html`, `backend/app/store.py`, `backend/app/routers/web.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall backend/app`, `python` smoke test voi `TestClient` (`manager /admin/ManagerBOT/index` co `data-manager-picker-locked=\"true\"`, modal co `edit-bot-user-id` va khong con `edit-bot-group`, `BOT` link trong user index khong con tro sang `/admin/bot/assignment`, `POST /admin/bot/update` scope manager thanh cong)

### 2026-04-03 16:33 - isolate admin/manager render workspace and lock manager filter on channel/render
- Changed: `backend/app/store.py` loai bo fallback cu trong `_workspace_channels_for_user()` de `/app` cua `admin/manager` chi hien worker/channel/job duoc link truc tiep cho chinh tai khoan ho, khong con bam vao tai nguyen cua user cung manager.
- Changed: `backend/app/store.py` va `backend/app/routers/web.py` truyen `viewer_role` day du vao `Danh sách Kênh` va `Danh sách Render`, bo sung `current_admin` dung cach cho cac route channel/render de manager picker render thanh badge khoa cung, khong con nut `x` gay reload lap.
- Affected files: `backend/app/store.py`, `backend/app/routers/web.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall backend/app`, `python` smoke test voi `TestClient` (`manager /admin/channel/index` va `/admin/render/index` deu co `data-manager-picker-locked=\"true\"`, khong con picker interactive; `manager/admin /app` khong con hien channel cua user thuong`)

### 2026-04-03 19:34 - harden manager scope across admin API/web and clean stale scope gaps
- Changed: `backend/app/routers/api_admin.py` duoc siết scope đồng bộ với `backend/app/routers/web.py`: manager direct URL/API vao `user/worker/channel/job` ngoai scope gio bi `403`, `update_bot()` API dung contract moi co `viewer_role/viewer_id`, va route API `POST /api/admin/bots/assign` chuyen thanh `410` vi flow `Cấp phát BOT` da bi bo.
- Changed: `backend/app/store.py` bo sung `viewer_id` vao `get_admin_user_bot_context()` de context user/bot cua manager dung chung summary scope moi; luot audit nay cung xac nhan `_workspace_channels_for_user()` va KPI shell khong con leak resource/kpi global cho manager. Dong thoi da xoa file router du `backend/app/web.py` de tranh chong cheo voi `backend/app/routers/web.py`.
- Affected files: `backend/app/store.py`, `backend/app/routers/web.py`, `backend/app/routers/api_admin.py`, `backend/app/web.py`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Verification: `python -m compileall backend/app`, `node --check backend/app/static/js/admin_tables.js`, smoke test voi `TestClient` (manager `403` khi truy cap `user/worker/channel/job` cua manager khac; admin `200`; `admin/manager /app` van `200` nhung chi hien resource gan truc tiep cho chinh tai khoan)

### 2026-04-03 20:05 - wire live RAM telemetry into BOT list and hard-lock manager modal fields
- Changed: `backend/app/store.py` persist them `ram_percent/ram_used_gb/ram_total_gb` from worker heartbeat and map BOT rows/live payload to `ram_percent` + `ram_text`.
- Changed: `backend/app/templates/admin/worker_index.html` render cot `RAM` bang du lieu RAM that, live JS row update cung dung `ram_percent/ram_text`, va manager-locked BOT modal doi sang `hidden input + readonly input` de tranh custom select bug.
- Changed: `backend/app/templates/admin/user_index.html` manager field trong modal `Sửa user` cung doi sang `hidden input + readonly input`, tranh viec JS/Select enhancer van cho tuong tac khi manager scope bi khoa.
- Verification: `python -m compileall backend/app`, `python -m compileall workers/agent`, `node --check backend/app/static/js/admin_tables.js`, smoke test `TestClient` + heartbeat gia lap xac nhan `/api/admin/bots` tra ve `ram_percent=67`, `ram_text=5.4GB / 8.0GB`.

### 2026-04-03 21:22 - allow shared VPS across users and stop destructive rename cleanup
- Changed: `backend/app/store.py` now allows many `(user_id, worker_id)` mappings on one worker, scopes cleanup to `user_id + worker_id`, and prevents `update_bot()` rename from wiping channels/user links.
- Changed: `backend/app/templates/admin/channel_user.html`, `backend/app/templates/admin/channel_users.html`, and `backend/app/templates/admin/user_of_bot.html` were rewritten in clean UTF-8 to remove mojibake on the admin pages tied to user/channel/BOT assignment.
- Verification: `python -m compileall backend/app`, smoke test script confirmed `update_bot()` rename preserves `user_worker_links/channels/channel_user_links`, removing one user from a shared worker only removes that user’s data on that worker, and `/admin/bot/userofbot` renders multiple users on the same VPS.

### 2026-04-03 21:34 - sort My Channel alphabetically inside each VPS group
- Changed: `backend/app/store.py` now sorts `connected_channels` by VPS group first, then by a diacritic-insensitive channel-name key (`unicodedata.normalize + casefold`) so names with Vietnamese accents still follow a natural `A -> Z` order inside each VPS cluster.
- Verification: `python -m compileall backend/app`, local dashboard context check confirmed channels on `62.72.46.42` render as `demo-user-youtube-channel`, `Lê Hoàng`, `Loki Lofi`, `Worker Channel`.

### 2026-04-03 18:50 - production full-sync hotfix and worker config contract repair
- Changed: production was resynced with the current local runtime by rolling `backend/app` back out to control-plane `82.197.71.6` and `workers/agent` to both worker VPSes after detecting a partial deploy where `store.py` expected RAM heartbeat fields but `backend/app/schemas.py` on the server had not been updated.
- Changed: `workers/agent/config.py` now includes the browser-session fields consumed by `workers/agent/control_plane.py` (`browser_public_base_url`, `browser_session_enabled`, `browser_display_base`, `browser_vnc_port_base`, `browser_web_port_base`, `browser_debug_port_base`) so worker services no longer crash at startup with `AttributeError`.
- Verification: `python -m compileall backend/app`, `python -m compileall workers/agent`, production `youtube-upload-web.service = active`, both `youtube-upload-worker.service = active`, and control-plane journal now shows `POST /api/workers/heartbeat ... 200 OK`.
## 2026-04-03

- Admin `Danh sách BOT` local: thêm cột `BotID`, `Group`, `Ngày tạo`, badge `Số kênh`, badge `Số user`, và dùng `created_at` thật của VPS/BOT thay cho `last_seen_at`.
- Admin `Danh sách BOT` local: polling live row data cập nhật lại `RAM`, `Disk`, `Băng thông` cùng metadata mới mỗi 3 giây và khi tab được focus lại.
- Admin custom select local: bỏ placeholder rỗng khỏi danh sách option thực và chỉnh seam dropdown để không còn lỗi góc nhọn lòi ra ở menu.
- Admin `Sửa user` local: manager field của role manager được khóa cứng bằng readonly display + hidden input, không còn bị JS coi là select tương tác.
- Admin `Danh sách BOT` local: thu gọn bảng theo shared VPS model mới bằng cách bỏ cột `User`, bỏ cột `BotID`, tách `Ngày tạo` thành 2 dòng ngày/giờ, và rút meta dòng BOT còn đúng 1 tên manager.
- Admin `Danh sách BOT` local: thu gọn thêm hai cột `Disk` và `Bandwith`, đổi formatter bandwidth còn `2` số sau dấu phẩy không kèm dấu phân tách hàng nghìn để nút tác vụ không bị ép ngang.
- 2026-04-03: Removed the OAuth column from the admin channel index and split BOT owner selection from the global manager filter so admin can assign a BOT to self while manager scope stays pinned to self.
- 2026-04-03: Added worker-side janitor cleanup (`workers/agent/cleanup.py`) and wired it into `workers/agent/main.py` so stale `job-*`, `browser-upload-runtime/*`, `outputs/*`, and orphan no-arg `Xvfb` processes are purged on startup and every hour.
- 2026-04-04: Unified BOT edit contract around owner binding instead of `Group`: `backend/app/store.py:update_bot()` no longer requires `Group`, admin BOT edit uses owner options (including self admin), manager BOT edit keeps manager locked and only changes user ownership.
- 2026-04-04: Rewrote `backend/app/templates/admin/worker_index.html` and `backend/app/templates/admin/channel_index.html` into ASCII-safe templates to stop propagating mojibake in local source while keeping the channel table free of the old OAuth column.
- 2026-04-04: Fixed BOT self-assignment flow on admin/manager surfaces: `bot_assignment` now exposes `admin-self` in the manager target branch, keeps `manager-self` visible in the user target branch, and `POST /admin/bot/assign` now persists desired-state assignment instead of redirecting without saving.
- 2026-04-04: Audited live admin/manager runtime and removed dead web BOT assignment artifacts: `bot_assignment.html`, `user_reset_password.html`, and their store-only context builders are gone; legacy web POST routes now redirect to canonical `Danh sách BOT` / `Sửa user` flows instead of mutating hidden state.
- 2026-04-04: Synced BOT/admin cleanup to app host `82.197.71.6`, removed dead production templates/backups from the live repo, and restarted `youtube-upload-web.service` on the cleaned runtime.
- 2026-04-04: Fixed the live `Cụm BOT VPS` row renderer so polling no longer prints literal `\u...` escape sequences in action labels, widened/wrapped the action cell to keep buttons aligned, and deprecated the remaining hidden BOT-mapping REST writes with `410 Gone`.
- 2026-04-04: Restored BOT `Group` as live metadata in the canonical `Danh sách BOT` edit modal; `backend/app/routers/web.py`, `backend/app/store.py`, and `backend/app/templates/admin/worker_index.html` now carry `Group` through the form again and stop worker heartbeat / manager-sync paths from overwriting a manually edited BOT group.
- 2026-04-04: Restored YouTube visibility parity with the old app: user job creation now carries `visibility` (`draft` / `private` / `unlisted` / `public`) from the dashboard into store + worker upload targets, and the browser uploader now splits draft telemetry from Review/Done publish flow while preserving upload progress + completion messaging.
- 2026-04-04: Polished the BOT edit modal copy to match the old admin/manager naming better: admin now shows `Managers`, manager keeps `Group`, hides the redundant manager-readonly row, and renames the user picker label to `Users`.
- 2026-04-04: Removed password prefill from admin user edit surfaces, stopped exposing/storing `password_plain` back into admin UI payloads, and simplified the admin user info column to a single username line.
- 2026-04-04: Aligned `/app` admin/manager sidebar shell with the shared admin navigation so the `Điều phối Render` tab keeps the same `Điều hướng` heading, icon rhythm, brand text, and footer profile treatment as the other admin tabs.
- 2026-04-04: Rolled YouTube browser upload back toward old-app parity: dashboard job creation is draft-only again, worker upload completion now follows the legacy Studio `[uploading]` progress signal, captures the Studio video URL when available, and cleans browser runtime + profile IndexedDB after upload.
- 2026-04-04: Removed the remaining non-draft upload branch from the live worker target contract and dashboard UI, deleting the unused OAuth/API uploader path so render jobs only expose the old draft-style upload flow again.
- 2026-04-04: Fixed a fast-upload regression in `workers/agent/browser_uploader.py`: draft uploads now complete when YouTube jumps straight from an early percent marker to `Saved as draft` / processing text or exposes the Studio video URL, instead of hanging forever on the last seen upload percentage.
- 2026-04-04: Tightened render job title validation to ASCII-only input: user dashboard and `/api/user/jobs` now accept only unaccented letters, digits, and spaces for `title`, and the dashboard script strips Vietnamese/special characters on input and paste.
- 2026-04-04: Tightened draft upload completion semantics again after audit: worker no longer completes just because draft/processing markers appear; it now waits until upload signals disappear together (`[uploading]`, cancel-upload control, percent marker) and stay gone briefly before reporting `Completed`.
- 2026-04-04: Rolled back the draft upload completion tightening on worker runtime, restoring the earlier legacy behavior that only completes after `.ytcp-video-upload-progress[uploading]` has been observed and then disappears.
- 2026-04-04: Hardened user workspace API calls to always send session cookies explicitly: `backend/app/static/js/user_dashboard.js` now routes internal fetches through a helper with `credentials: "include"` so `/api/user/*` actions do not intermittently drop `app_auth` during render/job requests.
- 2026-04-04: Audited live many-to-many user/VPS behavior: production state on `82.197.71.6` confirms one user can actively use two VPS at once (`worker-01` + `worker-02`) with channels split across both workers, while dry-run checks against the same runtime state confirm one worker can be shared by multiple users without breaking channel access, job creation, or browser-session port allocation.
- 2026-04-04: Promoted the shared-worker audit into a live runtime case on `82.197.71.6`: `user2` is now assigned to `worker-01` alongside `user`, and production bootstrap/dashboard data confirms the shared worker is visible while per-worker execution remains single-job-at-a-time because worker thread limits stay pinned to `1`.
- 2026-04-04: Replaced FIFO worker claim selection with per-worker round-robin by job owner in `backend/app/store.py`, while preserving the existing `1 active job per worker` gate; production verification on `82.197.71.6` now shows `worker-01` shared by `user` + `user2` and dry-run claim order on the live runtime resolves `user -> user2 -> user` on the same worker.
- 2026-04-04: Fixed worker-status dots in the user workspace channel/VPS cards: `backend/app/store.py` now maps `online -> emerald`, `busy -> amber`, and `offline -> rose` instead of collapsing every non-online state to slate gray, and the live app host has been restarted with the updated status-dot semantics.
- 2026-04-04: Added `docs/WORKER_RESILIENCE_COMPARISON.md`, a focused operations note comparing old SignalR bot behavior vs new HTTP worker behavior across network loss, restart, render/upload interruption, Telegram monitoring status, and a practical hardening roadmap split into `Dễ / Vừa / Mạnh`.
- 2026-04-04: Hardened worker/control-plane resilience: worker HTTP calls now retry with backoff, the worker runtime keeps a background heartbeat and re-registers after worker-missing/control-plane restart, control-plane starts a background offline monitor with delayed Telegram alerts after 180 seconds, and interrupted `uploading` jobs now only fail hard after upload has likely progressed past the safe requeue window.
- 2026-04-04: Configured the new Telegram alert bot locally with the operator chat id, confirmed `sendMessage` works end-to-end, and kept offline alert timing at `180s` with a `30s` monitor interval for worker disconnect notifications.
- 2026-04-04: Refined interrupted-job handling again: Telegram offline alerts now use clearer Vietnamese BOT-specific copy, and control-plane no longer flips `rendering/uploading` jobs immediately on a missing heartbeat entry; it waits for `WORKER_JOB_LEASE_SECONDS` before requeueing render or erroring progressed uploads.
- 2026-04-04: Fixed the user workspace `My Channel` status dot to refresh live without a full page reload: `/api/user/dashboard/live` now returns `connected_channels`, and `backend/app/static/js/user_dashboard.js` re-renders the channel list during polling while keeping delete/search bindings stable across repeated updates.
- 2026-04-04: Rolled the resilience changes onto live infrastructure: app host `82.197.71.6` now runs the background worker monitor + Telegram offline alert fields/env, both worker VPS now run the retry/re-register heartbeat runtime, and their `CONTROL_PLANE_URL` was switched from the Cloudflare-blocked domain to direct `http://82.197.71.6:8000` so workers can reconnect reliably.
- 2026-04-04: Simplified Telegram worker-offline alerts again: the message now omits `last_seen` and derived offline duration, keeping only BOT identity and the offline status line to avoid confusing time math during deploy/restart windows.
- 2026-04-04: Added a canonical control-plane worker bootstrap flow: admin `Danh sach BOT` now has a blue `Them BOT` modal that SSHes into a VPS with password or pasted SSH key, auto-allocates the next `worker-XX` id, enables browser/noVNC by default, and shares the same remote bootstrap helper with new CLI scripts `scripts/add_worker.py` and `scripts/add_worker.ps1`; `backend/requirements.txt` now includes `paramiko` and `.env*.example` documents `WORKER_BOOTSTRAP_*` settings.
- 2026-04-05: Upgraded BOT lifecycle ops in `Danh sach BOT`: `Them BOT` now queues an async provisioning task that appears immediately as a dimmed live row until the worker registers, while `Xoa BOT` now decommissions the VPS over SSH (stop/disable service, remove runtime/app/env) before clearing BOT state from control-plane; `backend/app/store.py` persists operation rows and minimal worker connection profiles so polling can render install/decommission status inline.
- 2026-04-05: Fixed same-VPS worker reprovisioning after live smoke failures: bootstrap now creates the virtualenv in the runtime dir instead of through the `.venv` symlink, remote shell scripts are normalized to LF before SSH upload so Windows CRLF does not break bash, failed install placeholders no longer permanently reserve the next `worker-XX`, decommission removes leftover `.legacy/.clone` app dirs, and `workers/agent/requirements.txt` now includes `selenium==4.32.0` so a clean worker install boots successfully from GitHub.
- 2026-04-05: Smoothed the operator UX around worker/browser setup again: user browser-session modal now enables `Đăng nhập Google` as soon as a `novnc_url` exists instead of waiting for a narrower status gate, worker browser runtime now treats Linux zombie PIDs as dead so stale noVNC sessions relaunch correctly, BOT install/decommission rows collapse into a 3-line compact placeholder that no longer stretches the admin table horizontally, and channel/job avatars now fall back to initials when external avatar URLs 404 or the YouTube channel has been terminated.
- 2026-04-05: Reverted the early-open noVNC button behavior after operator review: user workspace now waits for `awaiting_confirmation/confirmed` again before enabling `Đăng nhập Google`, while keeping the zombie-PID browser-runtime fix, compact BOT operation rows, and avatar fallbacks.
- 2026-04-05: Fixed a worker reprovision/browser-session regression exposed by reusing deleted BOT `109.123.233.131`: bootstrap now always creates real runtime roots for `.backup` and `worker-data`, worker config self-heals a dangling `WORKER_DATA_DIR` symlink target on startup, browser runtime falls back across Chromium binary names more safely, and bootstrap hard-fails if browser-session prerequisites (`Xvfb`, `openbox`, `x11vnc`, `websockify`, `noVNC`, Chromium) are still missing so newly added BOTs are guaranteed to be noVNC-ready before registration.
- 2026-04-05: Isolated browser-session state from host-level snap Chromium leftovers after comparing `109.123.233.131` with the cleaner `62.72.46.42`: browser sessions now launch with per-session `HOME`/`XDG_CONFIG_HOME`/`XDG_CACHE_HOME`, worker bootstrap/env generation prefers `google-chrome-stable` instead of the `chromium-browser` snap wrapper, and decommission now removes lingering `/root/snap/chromium` and Chromium/Chrome config/cache trees so deleting a BOT no longer leaks signed-in Google state into the next BOT/session.
- 2026-04-05: Fixed the follow-on upload regression from the browser-session isolation work: browser-session login and browser-based upload now share the same persistent per-profile `HOME`/`XDG_CONFIG_HOME`/`XDG_CACHE_HOME` roots under each channel profile instead of using a transient session-only home during channel connect, so new channel connections keep the Google/YouTube Studio login state that the uploader later reuses.
- 2026-04-05: Started a safer browser/profile alignment pass toward the old desktop-bot model without touching the live uploader path: new worker bootstrap defaults back to `chromium-browser` for future BOTs, `workers/agent/browser_runtime.py` now records the browser engine used to create each profile in `.browser-profile.json`, and the risky experimental uploader attach-mode patch was explicitly dropped so current upload behavior stays unchanged while future browser-session work can key off per-profile metadata.
- 2026-04-05: Rolled the safe browser-profile changes onto production: app host `82.197.71.6` now runs the latest worker bootstrap/decommission scripts, both worker VPS `62.72.46.42` and `109.123.233.131` were switched back to `BROWSER_SESSION_CHROMIUM_BIN=chromium-browser`, `workers/agent/browser_runtime.py` was synced live, and direct smoke launches on both workers confirmed fresh noVNC sessions return `HTTP 200` before the operator re-tests deleting and re-adding BOT `109`.
- 2026-04-05: Fixed a `chromium-browser` upload regression on worker `109.123.233.131`: browser upload no longer asks ChromeDriver to launch Chromium directly with the channel profile; it now launches Chromium manually with the same profile/XDG environment used by browser sessions, opens YouTube Studio on a dedicated remote-debugging port, and then attaches Selenium via `debuggerAddress`, which avoids the `SessionNotCreatedException: DevToolsActivePort file doesn't exist` crash path seen after re-adding BOT `109`.
- 2026-04-05: Fixed the next `chromium-browser` upload blocker after re-adding BOT `109`: new browser-upload jobs were staging `.mp4` files under `/opt/youtube-upload-lush/worker-data/...`, but live inspection on worker `109.123.233.131` showed YouTube Studio reporting `Không thể đọc tệp / Không thể đọc hoặc tìm thấy tệp` even though the file existed; `workers/agent/job_runner.py` now stages the upload file under `~/Downloads/youtube-upload-lush/<job-id>/...`, which matches what snap-backed Chromium can read reliably, and the live stuck job advanced from `8%` to `86%` immediately after re-attaching the same file from `/root/Downloads/...`.
- 2026-04-05: Hardened upload cleanup semantics after the live `job-d23f160b` incident on worker `109.123.233.131`: a worker restart during upload let control-plane mark the job `error` after the grace window while the operator still saw a half-finished draft in Studio, so `workers/agent/job_runner.py` now preserves both the rendered output file and the staged browser-upload file whenever the failure happened after upload had started, and only deletes those artifacts on the safe-success path (`cleanup_safe=True`).
- 2026-04-05: Reverted that upload-artifact retention after operator feedback: `workers/agent/job_runner.py` once again deletes the rendered output file and the staged browser-upload file when upload fails or the worker is interrupted, so failed YouTube uploads do not accumulate large `.mp4` leftovers on worker disks.
- 2026-04-05: Refined BOT operation UX in `Danh sách BOT`: failed SSH/bootstrap/decommission tasks no longer stay pinned as broken inline rows, control-plane now emits toast-style admin notifications for failed BOT operations and clears those failed tasks so operators can retry immediately, install/decommission progress rows now render as compact 3-line spinner cards with live step text from backend progress updates, and the delete modal removes the redundant red destructive warning card while normalizing visible Vietnamese copy with proper accents.
- 2026-04-05: Tightened BOT operation polish again: admin live polling now suppresses duplicate BOT-operation toasts by honoring the latest event cursor and de-duping event ids client-side, install-progress cards now use the indigo action tone to match primary admin buttons, and decommission-progress cards/status chips now use the same rose destructive tone as the `Xóa` action.
- 2026-04-05: Smoothed the user browser-session modal again: transient Chromium remote-debugging inspect errors are no longer surfaced as a red error card while the session is still progressing toward `awaiting_confirmation/confirmed`, and the user dashboard script cache key was bumped so operators reliably receive the updated behavior without stale JS.
- 2026-04-06: Rebased worker browser isolation onto a safer production path: worker services now run under the dedicated Linux user `ytworker`, admin BOT create/delete dialogs are password-only, and browser sessions/uploads now prefer the non-snap `google-chrome-stable` binary so canonical channel profiles stay in `worker-data/browser-runtime/browser-profiles/*` instead of leaking into snap wrapper state; live smoke on `109.123.233.131` confirmed fresh noVNC sessions now write only to the canonical profile root, while pre-existing wrapper-era profiles must be reconnected once under the new browser path.
- 2026-04-06: Tidied the final browser-profile hardening pass: `decommission_worker.sh` now also removes legacy staged uploads under `/root/Downloads/youtube-upload-lush`, and `workers/agent/browser_uploader.py` drops an older shadowed `_collect_upload_dialog_editors()` implementation so the uploader only keeps the newer shadow-DOM-aware dialog editor collector.
- 2026-04-06: Removed `--enable-automation` from both worker browser launch paths and replaced it with `--disable-blink-features=AutomationControlled` so Google Sign-in over noVNC no longer trips the visible automation banner and immediate `This browser or app may not be secure` rejection on fresh BOT/channel login flows.
- 2026-04-06: Fixed the real browser-session auto-confirm path on the live user dashboard: the active file [`backend/app/static/js/user_dashboard.js`](/D:/Youtube_BOT_UPLOAD/backend/app/static/js/user_dashboard.js) no longer instant-confirms the moment Studio is detected, but instead waits on an 8-second delayed auto-confirm window so Chromium has time to flush cookies/profile state before the app closes noVNC; the modal copy and script cache key in [`backend/app/templates/user_dashboard.html`](/D:/Youtube_BOT_UPLOAD/backend/app/templates/user_dashboard.html) were updated to explain the new grace period.
- 2026-04-06: Synced the user-supplied browser persistence follow-ups from GitHub onto live workers `62.72.46.42` and `109.123.233.131`: current worker runtime now includes the newer sign-in preference initialization (`signin.allowed_on_next_startup = False`, `First Run` sentinel) and the uploader no longer wipes `IndexedDB` at shutdown, with both worker services restarted and verified `active`.
- 2026-04-06: Rolled browser/login/upload behavior back toward the last operator-confirmed stable flow from commit `012e614`: the live user dashboard now instant auto-confirms browser sessions again, `workers/agent/browser_runtime.py` and `workers/agent/browser_uploader.py` were reverted to the older Chromium/profile handling path, while the newer decommission cleanup that fully removes leftover browser state when deleting a BOT was intentionally kept.
- 2026-04-06: Finished the `012e614` cleanup pass: worker service/bootstrap/decommission now run back under `root` instead of `ytworker`, dead legacy artifacts (`backend/app/user_dashboard.js`, `tmp-uvicorn-run.log`, unused `_delete_profile_indexeddb`) were removed, browser runtime now resolves only `chromium-browser`/`chromium`, and a defensive Xvfb display cleanup step was added so stale `/tmp/.X*-lock` leftovers from earlier sessions no longer block new noVNC launches on worker `62.72.46.42`.
- 2026-04-06: Fixed the immediate `SessionNotCreatedException: DevToolsActivePort file doesn't exist` regression after the `012e614` rollback by restoring an attach-mode uploader launch in `workers/agent/browser_uploader.py`: worker upload now starts Chromium manually with the channel profile under Xvfb/openbox, waits for a live remote-debugging port, and only then attaches Selenium via `debuggerAddress`, which avoids the snap-backed `chromium-browser` launch failure that was killing uploads at `0%` on both workers `62.72.46.42` and `109.123.233.131`.
- 2026-04-06: Restored the intended `DEC-010` admin workspace behavior on `Danh sách BOT`: admins can now assign a BOT/VPS directly to their own admin account from the BOT edit dialog without changing the BOT manager, so the same VPS can appear in `/app` for admin render orchestration while preserving the existing manager scope and avoiding the old “BOT đang có user hoặc kênh gắn kèm” guard unless the manager itself is actually changed.
- 2026-04-06: Tightened shared-VPS workspace isolation for privileged accounts: `channel_user_links` / `user_worker_links` now remain valid for `admin` and `manager`, `confirm_browser_session` refuses to bind a detected `channel_id` that is already linked to another account, admin BOT edit now folds the old `User dùng BOT` choice into the `Admin workspace` manager option, and per-account worker/channel counters now read from link tables instead of falling back to global admin/manager totals.
- 2026-04-06: Corrected the `Admin workspace` BOT edit flow so it no longer rewrites the BOT manager to the admin account: the admin option is now handled as a sentinel that only adds a self-workspace VPS link for the current admin while preserving the BOT's real manager, and if a BOT only has that temporary admin self-link plus no channels yet, switching it back to a real manager now auto-clears the self-link instead of tripping the old “BOT đang có user hoặc kênh gắn kèm” guard.
- 2026-04-06: Deployed and verified snap Chromium profile isolation on live workers `62.72.46.42` and `109.123.233.131`: `workers/agent/browser_runtime.py` now detects snap-backed `chromium-browser` and builds a per-profile runtime env that overrides `SNAP_USER_COMMON`, `SNAP_USER_DATA`, `SNAP_REAL_HOME`, and the `XDG_*` directories, while `workers/agent/browser_uploader.py` reuses the same env for upload so login and upload stop sharing the old global `/root/snap/chromium/common/chromium` cookie store; `scripts/bootstrap_worker.sh` was also updated on the app host to prefer non-snap Chromium for future BOT installs.
- 2026-04-06: Switched the live worker browser canonical path from snap-backed `chromium-browser` to native `google-chrome-stable`: `workers/agent/browser_runtime.py` now resolves Chrome Stable first, worker bootstrap defaults `BROWSER_SESSION_CHROMIUM_BIN=google-chrome-stable`, stale system `chromedriver` binaries are removed so Selenium Manager can resolve a matching driver at runtime, both workers `62.72.46.42` and `109.123.233.131` were migrated live to Chrome Stable 146 and verified `SNAP=False`, and fresh noVNC smoke launches completed successfully on both VPSes.
- 2026-04-06: Hardened Chrome Stable profile persistence on headless workers by adding `--password-store=basic` to both the noVNC login launch path and the upload launch path, avoiding Linux keyring-dependent cookie encryption drift that was making Chrome Stable profiles look logged out after restart; the patch was deployed live to workers `62.72.46.42` and `109.123.233.131`, both services were restarted, and direct process inspection on each VPS confirmed the running Chrome command line now includes `--password-store=basic`.
- 2026-04-06: Repaired a broken local edit in `workers/agent/browser_runtime.py` and finalized per-profile Chrome isolation for shared VPS use: `HOME`, `DBUS_SESSION_BUS_ADDRESS`, `XDG_CONFIG_HOME`, `XDG_CACHE_HOME`, `XDG_DATA_HOME`, and `XDG_RUNTIME_DIR` are now built deterministically from `profile_dir/session_dir` again, while the previous snap-specific overrides remain intact. The fixed file was recompiled and synced live to workers `62.72.46.42` and `109.123.233.131`.
- 2026-04-06: Tightened browser-session channel detection so sign-in redirects are no longer auto-confirmed as real Studio sessions: `workers/agent/browser_runtime.py` now only selects tabs whose actual hostname is `studio.youtube.com` and only extracts `channel_id` from true YouTube/Studio hosts, while `backend/app/static/js/user_dashboard.js` and `backend/app/store.py` now require a confirmable Studio URL before auto-confirm/manual confirm can connect a channel. This was deployed to app host `82.197.71.6` and both live workers.
- 2026-04-06: Audited the current shared-VPS profile flow without changing runtime code: the live control-plane still allows multiple workspace accounts on the same `worker_id`, channel browser profiles are persisted via `ChannelRecord.browser_profile_key/browser_profile_path` into `backend/app/data/app_state.db` and replayed to workers through `/api/workers/jobs/{job_id}/youtube-target`, worker janitor does not delete `browser-profiles/*`, and the remaining intentional guard is that a detected `channel_id` cannot be rebound to a different account because `ChannelRecord` is still global by YouTube channel id.
- 2026-04-06: Live-debugged the `manager` browser-profile reconnect path on `worker-02` and confirmed the newly saved profile persists valid Google/YouTube cookies across session confirm and browser shutdown, then immediately reopens into `studio.youtube.com/channel/.../videos?d=ud` under the same uploader-style Chromium flags without falling back to `ServiceLogin`.
- 2026-04-06: Hotfixed the live user dashboard auto-confirm behavior again: `backend/app/static/js/user_dashboard.js` no longer instant-confirms on the first poll that sees a valid Studio URL plus `detected_channel_id`, but now requires a 12-second stable window for the same `session_id + channel_id + current_url` before auto-confirming, reducing the chance that noVNC closes before the channel profile fully settles on disk. The updated JS was synced directly to app host `82.197.71.6`.
- 2026-04-06: Tightened the live browser-session modal guard on app host `82.197.71.6`: the real auto-confirm dwell stays at 12 seconds, but while that guard window is active the modal now locks `X`, `Đóng phiên`, manual `Đã đăng nhập`, and backdrop-close interactions, surfaces a clearer `Đang thêm kênh`/`Đang thêm kênh vào hệ thống. Vui lòng kiên nhẫn...` state, updates the warning copy to forbid closing the Studio tab early, and bumps the dashboard script cache key so operators pick up the new behavior after refresh.
- 2026-04-06: Refined the yellow guidance copy in the live add-channel modal on app host `82.197.71.6` so it now explicitly tells operators to wait until they are on the correct YouTube Studio page, return to the upload app, and keep the Studio tab open until the app confirms and closes the popup.
- 2026-04-06: Updated the same live add-channel warning copy once more so the phrase `Không được đóng tab đang mở trang Studio` is rendered in bold inside `backend/app/templates/user_dashboard.html`, making the no-close instruction more prominent without changing the surrounding auto-confirm logic.
- 2026-04-06: Adjusted that same bold warning phrase again in `backend/app/templates/user_dashboard.html` so the emphasized copy now reads `KHÔNG ĐƯỢC ĐÓNG TAB`, keeping the rest of the sentence unchanged while making the core prohibition visually stronger for operators.
- 2026-04-06: Refined the same warning sentence again so `đang mở trang Studio` is also bold in `backend/app/templates/user_dashboard.html`, making the protected Studio tab reference visually explicit while preserving the rest of the modal behavior.
- 2026-04-06: Rebalanced the user dashboard schedule picker in `backend/app/templates/user_dashboard.html` so the calendar button now uses the same 48px width as the upload buttons above, the calendar icon matches the 15px upload icon size, and the input gets symmetric extra padding to stay visually centered after the wider action slot change.
- 2026-04-06: Restored the schedule picker button colors in `backend/app/templates/user_dashboard.html` back to the original white/slate treatment while keeping the newer 48px action-slot width and 15px icon sizing, so the control remains visually balanced without inheriting the upload-button tint.
- 2026-04-07: Updated the admin BOT workspace to match the shared-VPS model: removed the `DS user` action from `backend/app/templates/admin/worker_index.html`, added a searchable checkbox dropdown in the BOT edit modal so admins and managers can see and update all users assigned to a VPS in one place, extended worker row payloads with `assigned_user_ids`, and upgraded both the form route and API route plus `store.update_bot()` to reconcile multi-user worker mappings instead of only appending a single `assigned_user_id`.
- 2026-04-07: Simplified the BOT edit user dropdown in `backend/app/templates/admin/worker_index.html` to look and behave like the older admin select: the menu now floats outside the modal so it is not clipped by the card/dialog, each row is reduced to a checkbox plus the user name, the extra card-like option styling and internal list scrolling were removed, and each moved checkbox is explicitly bound back to `edit-bot-form` so selected `UserIds` still submit correctly after the menu is appended to `document.body`.
- 2026-04-07: Fixed the manager BOT edit dropdown so out-of-scope assigned admins are no longer silently hidden. `backend/app/store.py` now exposes admin options to managers only when those admins are actually attached to workers inside that manager's scope and marks them as `scope_locked`, while `backend/app/templates/admin/worker_index.html` only shows those locked options when already checked and keeps them disabled, letting managers see the real assignment state for shared-VPS bots without being able to modify admin-owned bindings.
- 2026-04-07: Refined BOT edit semantics for shared VPS ownership in `backend/app/store.py`, `backend/app/routers/web.py`, `backend/app/routers/api_admin.py`, and `backend/app/templates/admin/worker_index.html`: the `Managers` dropdown no longer offers `Admin workspace`, the `Users` dropdown now defaults to real user accounts while only surfacing `manager/admin` entries when they are already attached to that BOT, locked manager-view items use a muted disabled visual instead of the active blue checkbox, labels for attached owner-like accounts now render as `username (manager|admin)`, and both web/API validation now preserve already-attached out-of-scope accounts for manager submissions while still allowing admins to remove those assignments.
- 2026-04-07: Updated shared-VPS BOT ownership again so the current `manager` or `admin` account is always available in the `Users` dropdown for self-assignment and self-removal. `backend/app/store.py` now marks the signed-in owner account as `self_assignable` instead of treating it like a locked out-of-scope assignment, and `backend/app/templates/admin/worker_index.html` uses that flag so self options stay visible and editable even when not already checked, while other attached owner-like accounts still use the locked muted state.
- 2026-04-07: Added a confirmed manager-transfer path for BOT edits: `backend/app/store.py` now supports purging all worker-bound user links, channels, browser sessions, profile cleanup tasks, and worker jobs before reassigning the BOT to a different manager, `backend/app/routers/web.py` and `backend/app/routers/api_admin.py` pass a new `confirm_manager_transfer_cleanup` flag through the web/API update routes, and `backend/app/templates/admin/worker_index.html` now shows a native browser confirm dialog before an admin can submit a manager change that will wipe the current manager's BOT data.
- 2026-04-07: Added per-user Telegram delivery plumbing for admin user edits and worker offline alerts. `backend/app/templates/admin/user_index.html` and `backend/app/templates/admin/user_edit.html` now expose a numeric `Telegram ID` field, `backend/app/routers/web.py` and `backend/app/routers/api_admin.py` preserve/update that field instead of resetting it, and `backend/app/store.py` now validates/stores per-user Telegram chat ids and sends worker offline alerts to the chat ids of users assigned to that worker before falling back to the legacy global env chat id.
- 2026-04-07: Upgraded the Telegram ID UX from manual copy/paste to a guided link flow. `backend/app/store.py` now issues temporary Telegram link codes and polls the notification bot via `getMe/getUpdates` until it sees `/start <code>`, `backend/app/routers/web.py` exposes lightweight JSON routes for creating and polling those link requests, and `backend/app/templates/admin/user_index.html` plus `backend/app/templates/admin/user_edit.html` now show a blue `Lấy Telegram ID` footer action and a dedicated helper modal that opens the bot, explains the steps, and auto-fills the numeric Telegram ID field once Telegram confirms the linked account.
- 2026-04-07: Refined the Telegram linking UX again so the success state now explicitly tells operators to close the popup, verify the Telegram ID field, and save, and `backend/app/store.py` now sends a Telegram confirmation message to the newly linked chat id when a user record is saved with a new or changed `Telegram ID`.
- 2026-04-07: Localized the Telegram bot notification copy in `backend/app/store.py` to proper Vietnamese with diacritics for all current app-originated bot messages, including the linked confirmation, unlinked confirmation, and worker offline warning messages.
- 2026-04-07: Added an explicit `BOT trống` owner option to the admin BOT edit modal so admins can remove the current manager from a VPS instead of only switching to another manager. The worker edit UI now submits a sentinel `__bot_empty__` value, shows a destructive confirm before removing the manager, and normalizes that sentinel back to `None` in both the web and API update routes. `backend/app/store.py` now accepts a blank manager for admin edits, reuses the existing worker-scope purge path to wipe user/channel/job/browser-session data when confirmed, and then persists the worker with no manager attached.
- 2026-04-07: Fixed the admin BOT-empty confirmation copy in `backend/app/templates/admin/worker_index.html` so the native browser dialog now uses real line breaks instead of showing literal `\n\n`, and corrected the Vietnamese wording to “Chọn BOT trống sẽ gỡ manager khỏi BOT này...” with a clean follow-up confirmation line.
- 2026-04-07: Refined the admin user workspace again so managers now see their own manager account inside the user list (without exposing a delete button for self), and the Telegram ID helper modal now surfaces a shareable deep link plus a copy-icon action instead of splitting the bot username and link code into separate fields. The rewritten Telegram dialog/script keeps the existing open-bot shortcut while making it easier for admins to copy and forward the full link to the person who needs to generate a Telegram ID.
- 2026-04-08: Removed the admin-only UI rule that hid or disabled the `Manager` field in user profile editing. The admin modal at `backend/app/templates/admin/user_index.html` now always keeps the manager select visible and enabled regardless of the edited account role, and the standalone `backend/app/templates/admin/user_edit.html` page now renders the same field for admins instead of only for plain `user` accounts. Manager-scoped viewers still keep the previous locked behavior.
- 2026-04-08: Tightened that user-edit behavior again to match the product rule: the `Manager` field should exist only for accounts whose role is `user`. The admin modal at `backend/app/templates/admin/user_index.html` now hides the manager field for edited `admin/manager` rows and disables the select unless the edited row is a `user`, while the standalone `backend/app/templates/admin/user_edit.html` page once again renders the manager select only for `user` records.
- 2026-04-08: Fixed a stale disabled-state regression in the admin user edit modal. `backend/app/templates/admin/user_index.html` still hides the `Manager` field for edited `admin/manager` rows, but the underlying select is no longer disabled just because the previous edit target was not a `user`; it now only locks for manager-scoped viewers, so opening `Sửa admin/manager` before `Sửa user` no longer leaves the user's manager field stuck in a disabled state.
- 2026-04-08: Refined admin/BOT operations in four places: `admin` and `manager` logins now always land on `/admin/user/index`, manager-created BOT installs now persist the real manager owner from the queued install task when the worker registers, worker connection profiles now keep the SSH auth captured at install time so BOT deletion can reuse saved credentials instead of prompting for root/password again, and the BOT list UI now deletes via a native browser confirm with both client-side and server-side notice dedupe so failed installs stop cleanly without repeated error spam.
- 2026-04-08: Changed BOT deletion to a no-SSH control-plane flow. `backend/app/store.py` now tracks `deleted_workers`, blocks deleted `worker_id`s from registering or heartbeating again, and exposes `delete_bot_without_ssh()` for immediate local cleanup; both admin delete routes now call that local path instead of building a decommission SSH request; and `workers/agent/control_plane.py` plus `workers/agent/main.py` now treat the “BOT đã bị xoá khỏi hệ thống” 403 as a terminal signal so an old worker process stops retrying instead of spamming reconnect attempts.
- 2026-04-08: Upgraded BOT deletion again into a hybrid no-reprompt flow: admin delete routes now first reuse any SSH password/key already saved from BOT creation for the old full remote decommission path, otherwise queue a `transport=self` decommission task so an online worker can uninstall itself on the VPS and callback the control-plane when cleanup finishes, and only fall back to immediate local deletion when the BOT is offline and there is no saved credential. Supporting changes added self-decommission task fields to `worker_operation_tasks`, worker-side poll/complete APIs, and a detached worker cleanup wrapper that runs `scripts/decommission_worker.sh` from `/tmp` before finalizing the BOT and tombstoning its `worker_id`.
- 2026-04-08: Fixed a self-decommission hang in the new BOT delete flow. The worker now launches VPS cleanup through a transient `systemd-run` unit instead of a child process inside `youtube-upload-worker.service`, preventing `systemctl stop youtube-upload-worker.service` from killing the cleanup script mid-flight, and the control-plane now re-offers stale `transport=self` decommission tasks after 20 seconds so a restarted worker can resume an interrupted self-uninstall instead of leaving the BOT stuck in `Đang gỡ BOT...`.
- 2026-04-08: Rolled the default BOT delete path back toward the pre-self-decommission behavior. Admin delete now prefers the saved SSH credential from BOT creation as the only automatic remote decommission path, keeps `delete_bot_without_ssh()` only for offline legacy rows that truly have no saved credential, and returns a clear error instead of queueing `transport=self` when an online BOT is missing its stored credential. The same patch also restores the missing `ssh_user` read in `backend/app/routers/web.py` for the admin BOT create form.
- 2026-04-08: Added per-actor Telegram notifications for BOT operations, but only after the operation truly finishes. `backend/app/store.py` now persists `requested_role` alongside `requested_by` in BOT operation tasks, builds Vietnamese completion messages that explicitly identify whether the actor was an `Admin` or `Manager`, and sends them to that actor’s saved Telegram chat id when BOT install completes on worker register, when BOT decommission finalizes, or when an offline legacy BOT is removed through the local fallback path. `backend/app/worker_bootstrap.py`, `backend/app/routers/web.py`, and `backend/app/routers/api_admin.py` now pass the acting user’s username and role into the queued install/decommission task metadata.
- 2026-04-08: Fixed a regression where BOT install completion Telegram alerts never fired. `backend/app/store.py::register_worker()` had been removing the queued install task before any completion notifier ran, so successful admin/manager BOT installs reached `Connected` without sending the promised Telegram message. The register path now snapshots the install task, removes it from state, saves the worker, and then immediately sends the completion Telegram to the actor’s saved chat id.
- 2026-04-08: Fixed the `Mở bot Telegram` action inside the Telegram-link modal. `backend/app/templates/admin/_telegram_link_script.html` had only been updating the visible deep-link text while leaving the action button anchored to `#`, so clicking the button reopened the current admin page instead of Telegram. The dialog now keeps both the visible link and the footer action pointed at the same deep-link URL and blocks clicks only when no link has been created yet.
- 2026-04-08: Fixed persistence of saved VPS credentials across app restarts. `backend/app/store.py::_restore_worker_connection_profiles()` now restores `auth_mode`, `password`, and `ssh_private_key` instead of only `vps_ip` and `ssh_user`; without this, newly added BOTs lost their saved SSH/password credentials on the next web-service restart and immediately failed the “delete without re-entering password” flow. Production state for `worker-01` and `worker-02` was also repaired so both current BOTs retain their saved root passwords again.
- 2026-04-08: Changed app Telegram alerts from per-actor delivery to broadcast delivery for all linked accounts. `backend/app/store.py` now sends BOT install/delete completion alerts and worker-offline alerts to every user in the app who has a valid linked `Telegram ID`, only falling back to the legacy global env chat id when no linked user exists. The BOT operation copy was also normalized to Vietnamese with diacritics, and the `Người thao tác` line now contains only the username instead of a prefixed role label.
- 2026-04-09: Refined Telegram alert routing again to match the final operational scope. BOT install/delete completion alerts now go to all linked `admin` accounts plus only the managers relevant to that BOT operation (the BOT owner manager and the acting manager if present), while worker-offline alerts now go to all linked `admin` accounts plus the manager who currently owns that BOT. The fallback `TELEGRAM_ALERT_CHAT_ID` remains only as an admin-side fallback when no admin account has linked Telegram yet.
- 2026-04-09: Fixed a Telegram recipient leak in `backend/app/store.py` where the legacy env fallback `TELEGRAM_ALERT_CHAT_ID` was still being appended even after one or more admin accounts had linked Telegram. This caused whichever chat owned the fallback env id to keep receiving alerts outside its manager scope. The admin-recipient helper now returns linked admin chat ids exclusively and only falls back to the env chat id when there are no linked admins at all.
- 2026-04-09: Fixed manager filtering drift in admin live APIs. `backend/app/routers/api_admin.py` now declares every `manager_ids` list query parameter with `Query(...)`, especially `/api/admin/bots`, so FastAPI consistently parses repeated `manager_ids` values from the URL and the live-refreshed BOT table stays aligned with the summary/filter chips instead of silently falling back to the unfiltered dataset.
- 2026-04-10: Repaired the mojibake source file `final_user_ui.html`. The document already had UTF-8 metadata, but much of its Vietnamese copy had been saved in double-decoded garbled form (`Äiá»u...`). The file has now been normalized back to readable Vietnamese text and saved again as `utf-8-sig`.
- 2026-04-10: Unified the admin live workspace onto a single canonical route. `backend/app/routers/web.py` now renders the admin live screen at `/admin/live`, keeps `/admin/live/index` only as a redirect to that canonical path, and redirects `/app/live` to `/admin/live` whenever an admin session is active so admin users cannot accidentally open the user live workspace under an admin shell. `backend/app/templates/admin/live_workspace.html` was updated so its filter form posts back to `/admin/live`.
- 2026-04-10: Restored admin workspace compatibility after the live-route unification. `backend/app/store.py` now accepts `workspace_mode` across the admin context builders used by `backend/app/routers/web.py`, rebuilds workspace-aware admin navigation/tabs, and provides a minimal `get_admin_live_workspace_context()` so `/admin/user/index` and `/admin/live` no longer crash with `Internal Server Error` when the updated live workspace routes are hit.
- 2026-04-10: Restored the approved live UI on the admin route. `backend/app/store.py::get_admin_live_workspace_context()` now feeds `/admin/live` with the same live dashboard visual language as the approved live workspace layout (the image-1 version) instead of the older split admin live template, so the admin live route is back on the expected design path.
- 2026-04-10: Fixed workspace navigation continuity for live/upload switching and exposed live navigation in the user sidebar. The admin workspace tabs now preserve the current module when switching between `Upload` and `Live Stream` (users, BOTs, channels, renders, role pages), and the user workspace sidebar now includes `Điều phối Live` backed by a concrete `get_user_live_workspace_view()` payload for `/app/live`.
- 2026-04-10: Removed the upload/live workspace switcher from the admin channel module. Because the live workspace does not own channel creation/management, `backend/app/store.py::_admin_workspace_tabs()` now suppresses the top workspace tab strip whenever the active admin page is in the `channels` module so the channel panels move up into that space.
- 2026-04-10: Added a preview/demo live row and tightened the live list table to wrap content instead of widening horizontally. `backend/app/store.py` now seeds one sample live-stream row for both admin and user live dashboards, and `backend/app/templates/user_live_dashboard.html` now uses a fixed-layout live table with wrapping text for long BOT names, stream keys, and other fields.
- 2026-04-10: Added explicit width classes for every column in the live list table. `backend/app/templates/user_live_dashboard.html` now defines one CSS width token per live table column (`live-col-stt`, `live-col-actions`, `live-col-bot`, `live-col-group`, `live-col-title`, `live-col-key`, `live-col-backup`, `live-col-type`, `live-col-timeline`, `live-col-log`, `live-col-status`) and applies them directly to the table header cells so column widths can be tuned from a single block instead of scattered Tailwind width utilities.
- 2026-04-10: Unified the live-list action buttons visually. `backend/app/templates/user_live_dashboard.html` now fixes `live-table-action-btn` to a shared 34px height with no wrapping so all four action buttons stay the same size, and the `Chi tiết` button now uses the same brand-blue visual treatment as the `Sửa` button.
- 2026-04-10: Simplified the live-list row cells by removing the secondary meta lines under `BOT live`, `Tên luồng`, `Khóa luồng`, and `BOT backup` in `backend/app/templates/user_live_dashboard.html`, leaving only the primary content line in each of those columns.
- 2026-04-10: Replaced the live workspace render list with a dedicated stream-oriented admin view. `backend/app/store.py` now serves `workspace=live` render pages from a separate `admin/live_render_index.html` template backed by `_demo_live_render_rows()` and `_live_summary_strip()`, and the table no longer reuses upload-job columns such as channel/source/queue. The live render table now reflects the legacy stream schema while grouping fields for the current UI: `Manager + User` as `Scope`, `BOT + Group` as `BOT live`, and `Live/Bắt đầu/Kết thúc` merged into a single `Timeline` column.
- 2026-04-10: Reduced the live render preview dataset to a single demo row. `backend/app/store.py::_demo_live_render_rows()` now returns one sample stream only, making visual review of `/admin/render/index?workspace=live` less noisy while the live runtime data source is still mocked.
- 2026-04-10: Corrected the live admin KPI strip and hardened live render table wrapping. `backend/app/store.py::_admin_shell_context()` now switches all `workspace_mode == "live"` admin pages to the live summary metrics (`Manager Trong Scope`, `BOT Đang Chạy`, `Tổng User`, `Đang Live`, `Chờ Lên Lịch`, `BOT Backup`) instead of the upload KPI set, and `backend/app/templates/admin/live_render_index.html` now explicitly overrides the shared admin table `white-space: nowrap` behavior so long live BOT names, stream titles, RTMP keys, and timeline lines wrap inside their columns instead of stretching the row horizontally.
- 2026-04-10: Added explicit width tokens and cleaned wording for the admin live-stream list. `backend/app/templates/admin/live_render_index.html` now starts with a dedicated width-token block and applies `live-render-col-*` classes to both header and body cells so column widths can be tuned from one place, while the panel title/note and empty state were renamed from `stream live` wording to `live stream` without mentioning the legacy app. The demo live-config badge in `backend/app/store.py::_demo_live_render_rows()` was also renamed to `BOT luồng chính`.
- 2026-04-10: Removed the non-essential `Manager Trong Scope` KPI from the admin live summary strip. `backend/app/store.py::_live_summary_strip()` now exposes five operational KPIs only (`BOT Đang Chạy`, `Tổng User`, `Đang Live`, `Chờ Lên Lịch`, `BOT Backup`) so the live KPI row distributes evenly and focuses on stream operations instead of manager scope metadata.
- 2026-04-10: Made the admin KPI strip distribute dynamically by item count instead of assuming six columns. `backend/app/templates/admin/_summary_strip.html` now uses auto-flow equal-width columns on medium screens and up, so live workspace summary rows with five KPIs stretch evenly across the panel instead of leaving a phantom sixth slot.
- 2026-04-10: Simplified the live-stream config column by removing the extra `BOT luồng chính` badge from `backend/app/templates/admin/live_render_index.html`, leaving only the live-duration/status badge in the `Cấu hình live` column while keeping the width-token column classes intact for further tuning.
- 2026-04-10: Renamed workspace navigation labels for clarity. `backend/app/store.py` now labels the upload workspace entry as `Điều phối Upload` instead of `Điều phối Render`, and the live entry is consistently titled `Điều phối Live Stream` across both admin and user sidebars.
- 2026-04-10: Started the backend unification of live stream into the existing FastAPI control-plane. `backend/app/schemas.py` now defines a shared `LiveStreamRecord`, and `backend/app/store.py` persists `live_streams` alongside users/workers/channels/jobs in the SQLite state snapshot so upload and live share the same account model. The admin/user live contexts and admin live-render table no longer depend on `_demo_live_*` helpers; they now map from canonical live-stream records scoped by `owner_user_id`, `manager_id`, and the selected primary/backup workers.
- 2026-04-11: Completed the first store-level CRUD pass for shared live streams. `backend/app/store.py` now exposes `list_live_streams()` alongside create/get/update/delete/status methods, normalizes persisted live-stream rows against current user-to-worker grants on load (including clearing invalid backup BOT assignments and refreshing owner/manager display metadata), and recomputes default live status correctly during updates instead of silently reusing stale prior status values.
- 2026-04-11: Corrected the live/backend domain split after the account unification. The control-plane still uses one shared `users`/role model, but live now operates on its own `live_workers` and `live_user_worker_links` instead of reusing upload BOT assignments; related admin JSON endpoints in `backend/app/routers/api_admin.py` now accept `workspace=live` so bot/user/channel/render API reads stay inside the live domain.
- 2026-04-11: Connected the live create forms to the real backend. `backend/app/routers/web.py` now handles `/app/live/create` and `/admin/live/create`, validates live datetime inputs, resolves the owner account from the selected primary live BOT, and persists records through `store.create_live_stream(...)`; `backend/app/templates/user_live_dashboard.html` now submits to the injected `live_form_action` instead of remaining a UI-only shell.
- 2026-04-11: Finished the first backend parity pass for live BOT management and live-stream row CRUD. `backend/app/store.py` now persists `live_role` (`primary`/`backup`) on live BOT assignments and enforces scope-aware admin/manager assignment rules, while `backend/app/routers/web.py` plus `backend/app/templates/user_live_dashboard.html` and `backend/app/templates/admin/live_render_index.html` now wire `edit/update/delete/detail` for live stream rows to the real `/app/live/*` and `/admin/live/*` routes instead of placeholder UI actions.
- 2026-04-11: Tightened the live BOT browser contract without inheriting upload bootstrap semantics. In `workspace=live`, `backend/app/templates/admin/worker_index.html` now treats the create modal as a live-only control-plane form (no SSH/no upload bootstrap copy), uses live-specific cleanup/assignment messaging, and consumes API success messages for delete/create flows; `backend/app/routers/api_admin.py` now returns a dedicated success message for live BOT creation. Route-level smoke checks confirmed admin can create/assign/delete live BOTs, manager can assign live BOTs to self and scoped users, and manager-to-admin assignment remains blocked with `403`.
- 2026-04-11: Audited admin/manager parity for the live workspace against upload. Shared account management (`/admin/user/*`) continues to work under `workspace=live`, live BOT assignment/delete flows were re-verified for both admin and manager scopes, manager-transfer cleanup on live BOTs was confirmed to purge old live assignments/streams after explicit confirmation, and the remaining deliberate differences were documented: the live `Danh sách Kênh` screen is still an empty shell, and `Thêm BOT live` only creates a control-plane record without running an install/bootstrap workflow.
- 2026-04-11: Removed `Danh sách Kênh` from the admin/manager live workspace. `backend/app/store.py` now hides the channel nav item in `workspace=live` and maps any workspace switch from the channel module back to `/admin/live`, while `backend/app/routers/web.py` turns `/admin/channel/index?workspace=live` into a redirect instead of rendering the old empty shell. The same pass also re-confirmed the legacy live flow from `D:/LiveStreamBOT-master`: live uses primary/backup BOT selection, backup delay, RTMP stream key, video/audio sources, start/end schedule, SignalR-dispatched `RenderCommand`, ffmpeg runtime on the BOT, and backup failover, with no channel-onboarding module in that domain.
- 2026-04-11: Locked the live runtime contract to the old app’s actual behavior while dropping obsolete resolution branching. `docs/DECISIONS_INDEX.md` and `docs/DECISIONS.md` now record that the rebuilt live runtime must not reintroduce `1080/4K`; effective quality comes from the input media/ffmpeg RTMP path, and the optional `audio_url` only overrides audio when present, otherwise the stream keeps the original audio embedded in the video source.
- 2026-04-11: Dung runtime live phase 1 tren framework hien tai. `backend/app/schemas.py` bo sung live worker payloads va runtime fields cho `LiveStreamRecord`; `backend/app/store.py` them contract rieng `/api/live-workers/*` voi lease/status machine `downloading -> preparing -> waiting -> streaming`; `backend/app/routers/api_worker.py` noi register/heartbeat/claim/progress/complete/fail; `workers/agent/control_plane.py` them live client; `workers/agent/live_runner.py` implement pipeline `download -> pre-render -> wait -> RTMP stream`; va `workers/agent/main.py` tach lazy import theo `WORKER_RUNTIME_MODE` de live worker khong phu thuoc upload/browser stack. Audit pass voi `compileall`, smoke API qua `TestClient`, import `workers.agent.main` OK, health check local `ok`.
- 2026-04-11: Hoan thien cleanup cho live runtime. `workers/agent/live_runner.py` nay ghi `activity.touch` trong `work_root/live-streams/<stream_id>` de danh dau luong con song, `workers/agent/cleanup.py` day them janitor cho thu muc `live-streams/*`, va `workers/agent/main.py` chay janitor startup/periodic ca trong `WORKER_RUNTIME_MODE=live`. Smoke cleanup xac nhan chi thu muc live stale bi xoa, thu muc con hoat dong duoc giu lai.
- 2026-04-11: Chot backup policy cua live theo app cu: luong co `EndTimeLive` chay primary + backup song song ngay tu dau; luong `24/7` moi failover tre theo `backup delay` va huy backup neu primary hoi phuc. Runtime moi se tai su dung lease/heartbeat model cua framework hien tai, nhung khong bien backup thanh upload-style requeue.
- 2026-04-11: Implemented live backup/stop runtime parity on top of the current control-plane contract. `backend/app/store.py` now manages hidden backup runtime clones, delayed failover for `24/7` streams, parallel backup clones for fixed-end streams, and stop routes for both admin and user workspaces; `fail_live_stream_runtime()` now downgrades primary streams with configured backup to `disconnected` so the failover policy can take over instead of immediately killing backup eligibility. Smoke checks confirmed fixed-end parallel backup, delayed 24/7 backup, primary recovery cleanup, primary-failure backup creation, and manual stop of both primary and backup clone.
- 2026-04-12: Rebuilt `live-youtube` on top of the latest `main` baseline by replaying the live-only commits onto `origin/main`, then reapplying the upload/admin hardening that had landed later on `main`. The synced branch now keeps the live workspace/runtime stack while also preserving the newer admin channel-user scope guard, last-admin delete protection, worker table overflow fixes, and current host/systemd bootstrap behavior from the main app.
- 2026-04-12: Restored the intended `24px` gap between the shared `Upload / Live Stream` tab strip and the first content panel on the admin `Danh sách BOT` and `Danh sách Render` screens by removing local `margin-top: 0 !important` overrides from `backend/app/templates/admin/worker_index.html` and `backend/app/templates/admin/render_index.html`. The same pass also aligned the live admin sidebar identity with upload by changing `backend/app/store.py` so the admin-shell live workspace now shows `Admin`/`Manager` in title case. Verification: `python -m compileall backend/app`, restart local `uvicorn` on `127.0.0.1:8015`, `curl http://127.0.0.1:8015/api/health`.
- 2026-04-12: Adjusted the admin workspace-switch tabs on `Người dùng` subpages so `Tạo user`, `Manager`, and `Admin` no longer trap `Upload / Live Stream` inside `/admin/user/*`. `backend/app/store.py::_admin_workspace_target_href()` now routes those subpages back to the actual workspace homes (`/app` for upload, `/admin/live` for live), while the base `Danh sách user` page still preserves module-scoped workspace switching. Verification: `python -m compileall backend/app`, restart local `uvicorn` on `127.0.0.1:8015`, `curl http://127.0.0.1:8015/api/health`.
- 2026-04-12: Refined the `Người dùng` workspace tabs to match the latest UX rule. `backend/app/store.py::_admin_workspace_target_href()` now always sends `Upload` to `/admin/user/index` and `Live Stream` to `/admin/user/index?workspace=live` throughout the user-management cluster, while `backend/app/store.py::_admin_workspace_tabs()` suppresses the blue active state on those two workspace tabs whenever the current subpage is `Tạo user`, `Manager`, or `Admin`. Verification: `python -m compileall backend/app`, restart local `uvicorn` on `127.0.0.1:8015`, `curl http://127.0.0.1:8015/api/health`.
- 2026-04-12: Unified the live app onto the same route pattern as upload. `backend/app/auth.py` now bridges `admin_auth` into `require_app_access()`, `backend/app/routers/web.py` keeps `/app/live` as the canonical live workspace and turns `/admin/live` into a compatibility redirect, while `backend/app/store.py::get_user_live_workspace_view()` now auto-enables the admin shell for `admin/manager` and the shared admin nav points `Điều phối Live Stream` to `/app/live`. Result: admin/manager can self-assign live BOTs in the admin modules, then operate the live app inside their own account via `/app/live` just like `/app` upload. Verification: `python -m compileall backend/app`; direct helper smoke for `require_app_access()` with admin/manager session payloads; direct context smoke for `get_user_live_workspace_view()` on admin/manager; `TestClient` redirect check `/admin/live -> /app/live`.
- 2026-04-12: Removed the upload-only `Danh sách Kênh` module completely from the live workspace and promoted live BOT operations to the same SSH bootstrap/decommission pipeline as upload. `backend/app/routers/web.py` and `backend/app/routers/api_admin.py` now redirect or reject every live-channel entrypoint instead of leaking upload channel flows into `workspace=live`, while `backend/app/worker_bootstrap.py`, `backend/app/store.py`, `scripts/bootstrap_worker.sh`, and `backend/app/templates/admin/worker_index.html` now install/decommission live BOTs as real workers with persisted SSH credentials, provisioning rows, workspace-aware cleanup, and `WORKER_RUNTIME_MODE=live`. Verification: `python -m compileall backend/app`, `python -m compileall workers/agent`, `node --check backend/app/static/js/admin_tables.js`, and smoke checks for `/app/live`, `/admin/*?workspace=live`, `/api/admin/channels*?workspace=live`, and `/api/admin/bots/install` on `127.0.0.1:8015`.
- 2026-04-12: Hardened fresh host deploys and rebuilt the isolated live preview environment on `82.197.71.6`. `scripts/bootstrap_host.sh` now creates runtime-backed `.venv`, `.backup`, and `backend-data` before linking them into the checkout, and it tolerates reruns after partial deploys by clearing the checkout `.venv` link before rebuilding runtime paths. The preview host was recreated cleanly at `/opt/youtube-upload-lush-live` + `/opt/youtube-upload-lush-live-runtime`, pinned to branch `codex/live-main-sync-20260412` on port `8010`, with `WORKER_BOOTSTRAP_BRANCH` aimed at that same preview branch so live BOT bootstrap/runtime tests use the exact same code as the preview control-plane. Verification: remote `systemctl status youtube-upload-web-live.service`, `curl http://127.0.0.1:8010/api/health`, and external `curl http://82.197.71.6:8010/api/health`.
- 2026-04-12: Optimized live BOT bootstrap so live VPS no longer installs the upload browser stack by default. `backend/app/worker_bootstrap.py::_build_worker_env_file()` now disables `WORKER_UPLOAD_TO_YOUTUBE` and `BROWSER_SESSION_ENABLED` when `runtime_mode=live`, which makes `scripts/bootstrap_worker.sh` skip the Chrome/noVNC/Xvfb package path on live workers. Verification: committed and pushed `cc014ef`, redeployed preview `https://live.jazzrelaxation.com`, cleaned `154.26.159.8`, and reinstalled a fresh live worker `live-worker-04` that reached `online` in about `35.3s` with `WORKER_RUNTIME_MODE=live`, `WORKER_UPLOAD_TO_YOUTUBE=false`, and `BROWSER_SESSION_ENABLED=0`.
- 2026-04-12: Restored the shared admin table language for the live workspace and stopped public/live environments from auto-seeding demo live BOT data. `backend/app/templates/admin/worker_index.html` and `backend/app/templates/admin/user_index.html` now expose sortable plain-text headers again so `backend/app/static/js/admin_tables.js` can rebuild the search/sort toolbar consistently, `backend/app/templates/admin/_layout.html` bumps the JS cache key so preview browsers fetch the updated table script immediately, and `backend/app/store.py` now gates live demo seeding behind `APP_ENABLE_LIVE_DEMO_SEED` with localhost URLs as the only implicit default. `.env.example` documents the new flag for deploys that should start with an empty live pool.
- 2026-04-12: Fixed the HTTPS mixed-content regression that was still breaking every live table on `live.jazzrelaxation.com`. The shared admin script/favicons were still rendered through `request.url_for('static', ...)`, which became `http://...` behind the reverse proxy, so browsers blocked `admin_tables.js` and the live pages lost the search toolbar plus sortable headers. The affected templates now use `request.app.url_path_for('static', ...)` so static assets stay scheme-relative (`/static/...`) on both HTTP localhost and HTTPS preview/public domains.
- 2026-04-12: Added a dedicated switch for BOT operation Telegram notifications. `backend/app/store.py` now honors `TELEGRAM_BOT_OPERATION_NOTIFICATIONS_ENABLED` when collecting recipients for add/delete/decommission BOT alerts, so preview/live environments can mute BOT-operation Telegram noise without disabling the broader Telegram integration contract.
