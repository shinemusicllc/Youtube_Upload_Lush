# UI_SYSTEM

## Current UI Snapshot

- Primary web UI is server-rendered Razor with Bootstrap 4 and the Stisla admin theme.
- Main admin/user shells share the same sidebar/topbar structure and utility stack:
  - Bootstrap 4
  - Font Awesome
  - DataTables
  - Select2
  - jQuery-driven modals and actions
- Typography is primarily `Nunito` in the Stisla theme.
- Primary accent color is `#6777ef`.
- Supporting semantic colors:
  - success `#47c363`
  - info `#3abaf4`
  - warning `#ffa426`
  - danger `#fc544b`

## Visual Characteristics

- Layout pattern: left sidebar + top navbar + card-based content area.
- Components used heavily:
  - cards
  - badge status pills
  - striped data tables
  - modal forms
  - select2 dropdowns
  - small stat summary blocks
- Form styling is compact and bootstrap-like with 42px field height and low-radius controls.

## UX Characteristics

- Admin information architecture already exists and is useful:
  - user management
  - bot management
  - channel management
  - render/job management
- User information architecture already exists and is useful:
  - create render job
  - choose channel
  - view render status/progress/history
  - profile/account page
- Status communication is explicit and valuable:
  - Pending
  - Schedule
  - Queueing
  - Downloading
  - Rendering
  - Uploading
  - Completed
  - Cancelled
  - Error

## Current Design Issues

- Visual language is dated and fragmented.
- Login page uses a different marketing-style bundle from the main app shell, so the product feels inconsistent.
- UI depends on older jQuery-era plugins and patterns.
- Dense tables and modal-first CRUD make the admin area harder to scale cleanly.
- Existing design is serviceable for workflow discovery, but not a good base for a modern rewrite.

## Guidance For Rewrite

- Preserve the current information architecture and workflow concepts.
- Rebuild the layout, components, spacing, and interactions from scratch in a modern frontend stack.
- Keep one coherent design system across admin and user surfaces.
- Avoid reusing old Stisla/Bootstrap 4 presentation directly; reuse behavior and domain structure instead.
