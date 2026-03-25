# PROJECT_CONTEXT

## Overview

- Project root: `D:\Youtube_BOT_UPLOAD\YoutubeBOTUpload-master`
- Solution type: multi-project `.NET` solution for YouTube upload/render management.
- Current runtime shape:
  - `BaseSource.AppUI`: ASP.NET Core MVC/Razor web dashboard for users/admins.
  - `BaseSource.API`: ASP.NET Core Web API + SignalR + background services.
  - `BaseSource.Services` / `BaseSource.Data` / `BaseSource.Shared*`: business logic, EF Core, shared contracts.
  - `UploadYoutubeBot`: Windows WPF desktop bot using Selenium, FFmpeg, SignalR and cloud storage helpers.
- Current media workflow (observed from code):
  - Users/admins manage channels, renders and bot assignments through web UI.
  - Source music/video links are validated from Google Drive / OneDrive links.
  - Desktop bot downloads media, renders output with FFmpeg, then uploads to YouTube through automated Chrome/YouTube Studio flow.

## Primary Constraints

- Upload flow currently depends on Windows + Chrome + Selenium profile state.
- Database currently targets SQL Server through EF Core.
- There is no dedicated test project detected in the solution.
- Deploying the whole current architecture to a Linux VPS is not straightforward because `UploadYoutubeBot` targets `net6.0-windows7.0`.

## Known Domains

- Web management: account, admin, channel, render history, bot assignment.
- Media processing: download from cloud links, render/merge, schedule work.
- Upload automation: YouTube Studio browser automation with Chrome profiles.
- Realtime communication: SignalR hubs between server and bot/dashboard.

## Current Task Focus

- Understand how the current app works end-to-end.
- Evaluate architecture and bottlenecks for VPS deployment.
- Recommend a more suitable stack and migration direction.
- Assess whether YouTube upload can avoid browser-based login and how to reduce auth friction.
- Current planning direction has shifted toward a central control-plane VPS plus a pool of worker VPS nodes that only perform media concat/upload work.
- Frontend planning is to preserve old admin information flows where useful, while modernizing dashboard/table UX and allowing end users to self-connect YouTube OAuth in the new system.
