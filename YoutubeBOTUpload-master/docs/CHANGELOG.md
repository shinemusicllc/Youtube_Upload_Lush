# CHANGELOG

### 2026-03-23 22:45 - project bootstrap for architecture review
- Added: initial project memory files under `docs/`.
- Changed: documented current repo root and high-level module map.
- Fixed: N/A
- Affected files: `docs/PROJECT_CONTEXT.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: establishes project memory for later analysis; low risk because docs-only.

### 2026-03-23 23:18 - architecture review and stack recommendation
- Added: analysis notes in project worklog for current media pipeline and auth bottlenecks.
- Changed: documented that Google Drive / OneDrive is currently a source-link pipeline, not managed app storage.
- Fixed: clarified the real blocker for VPS deployment is the Windows/Selenium upload worker rather than the web dashboard itself.
- Affected files: `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: improves decision-making for migration planning; low implementation risk because docs-only.

### 2026-03-23 23:31 - greenfield stack recommendation
- Added: recommended fresh-start architecture focused on web API + workers for VPS deployment.
- Changed: captured a design decision favoring Python worker-based services over the current desktop bot model.
- Fixed: clarified the trade-off between Python stability and Go-level resource efficiency.
- Affected files: `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: guides future rebuild direction; low risk because docs-only.

### 2026-03-23 23:42 - youtube oauth flow clarification
- Added: worklog note for account connection and upload-token selection explanation.
- Changed: clarified the runtime model from browser-session switching to per-channel token usage.
- Fixed: reduced ambiguity around how multi-account upload routing would work after migration.
- Affected files: `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: improves architectural clarity for future auth design; low risk because docs-only.

### 2026-03-23 23:52 - network strategy clarification for uploads
- Added: decision and worklog notes for upload egress design.
- Changed: formalized preference for stable business IP identity over anonymous or rotating proxy behavior.
- Fixed: clarified that multi-channel scale should be handled with compliance, quota, and tenant isolation rather than IP-evasion tactics.
- Affected files: `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: improves infrastructure planning and lowers future account-risk; low risk because docs-only.

### 2026-03-24 00:01 - old bot ip behavior clarification
- Added: worklog note about legacy Selenium networking behavior.
- Changed: documented that the old bot uses persistent browser profiles, not incognito.
- Fixed: clarified that the legacy upload flow normally exits through the host machine or VPS IP unless optional proxy wiring is explicitly supplied.
- Affected files: `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: improves migration and operations understanding; low risk because docs-only.

### 2026-03-24 00:08 - profile-vs-token model comparison
- Added: worklog note for side-by-side comparison of old and new upload models.
- Changed: summarized architectural trade-offs between browser-profile automation and OAuth token usage.
- Fixed: improved decision clarity for migration planning.
- Affected files: `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: supports architecture choice with clearer operational framing; low risk because docs-only.

### 2026-03-24 00:17 - hybrid render architecture recommendation
- Added: decision and worklog notes for hybrid deployment architecture.
- Changed: formalized preference for local high-storage workers when render artifacts are large.
- Fixed: clarified that tunnels should carry control traffic, not bulk media transfer.
- Affected files: `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: improves infrastructure cost planning and throughput expectations; low risk because docs-only.

### 2026-03-24 00:29 - vps capacity inspection
- Added: worklog note with live VPS capacity and storage observations.
- Changed: grounded render-capacity guidance in actual VPS metrics instead of assumptions.
- Fixed: clarified that this VPS is better suited to single-job remux workloads than heavy concurrent 4K transcoding.
- Affected files: `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: improves deployment sizing decisions; low risk because docs-only.

### 2026-03-24 00:36 - workload clarification for 4k loop jobs
- Added: worklog note for the clarified concat/remux workload profile.
- Changed: adjusted capacity reasoning to emphasize low CPU pressure and disk-first constraints.
- Fixed: reduced ambiguity between 4K transcoding and 4K loop-extension jobs.
- Affected files: `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: improves workload-fit assessment for the inspected VPS; low risk because docs-only.

### 2026-03-24 09:20 - frontend reuse and redesign decision
- Added: `docs/UI_SYSTEM.md` summarizing the current UI stack and patterns.
- Changed: captured the decision to preserve workflow/information architecture while rebuilding the UI layer.
- Fixed: clarified what parts of the old frontend are reusable versus what should be replaced.
- Affected files: `docs/UI_SYSTEM.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, `docs/CHANGELOG.md`
- Impact/Risk: improves frontend planning clarity before implementation; low risk because docs-only.

### 2026-03-24 13:05 - legacy ui source review and fleet architecture update
- Added: source-level review notes for the old admin and user UI based on Razor views/layouts.
- Changed: project memory now reflects the central control-plane VPS plus worker-VPS fleet model and the shift to user self-service YouTube OAuth.
- Fixed: removed ambiguity caused by relying on noisy exported HTML snapshots instead of the actual view source.
- Impact/Risk: future frontend and architecture planning should treat worker pools, assignments, and self-service channel connection as core product concepts.

### 2026-03-25 14:30 - admin ui redesign to elevated saas style
- Added: `elevated-admin.css` containing design tokens (fonts, spacing, rounded-2xl, shadows).
- Changed: Migrated `_Layout.cshtml` and all CRUD views (`User`, `Channel`, `ManagerBOT`, `Render`) from basic Bootstrap to a modern Tailwind-powered UI pattern with KPI badge strips and elevated table containers.
- Fixed: Replaced legacy cards with streamlined data layouts and compact action buttons.
- Affected files: `wwwroot/css/elevated-admin.css`, all `Areas/Admin/Views/*/*.cshtml`.
- Impact/Risk: Medium. Pure UI change utilizing existing DOM structures, but heavily modifies visual classes. Requires full browser testing to ensure no custom JS/Ajax binds were broken.
