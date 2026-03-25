# AGENTS

## Build / Test / Lint

- Build solution: `dotnet build YoutubeBOTUpload.sln`
- Run API only: `dotnet run --project BaseSource.API`
- Run App UI only: `dotnet run --project BaseSource.AppUI`
- Build desktop bot: `dotnet build UploadYoutubeBot/UploadYoutubeBot.csproj`
- Tests: no dedicated test project detected yet.
- Lint: no repo-wide lint configuration detected yet.

## Coding Conventions

- Keep shared contracts in `BaseSource.Shared`, `BaseSource.SharedSignalrData`, and `BaseSource.ViewModels`.
- Keep EF Core entities/configurations/migrations inside `BaseSource.Data`.
- Keep business logic in `BaseSource.Services`; controllers should stay thin.
- Treat `UploadYoutubeBot` as Windows-specific automation code; avoid leaking Selenium/UI concerns into server projects.
- Avoid changing public API routes, SignalR contracts, DTO shapes, or DB schema without an explicit migration/update plan.

## Module Boundaries

- `BaseSource.AppUI` depends on API clients and view models, not directly on EF Core/data access.
- `BaseSource.API` depends on services and data, and exposes HTTP + SignalR endpoints.
- `BaseSource.Services` may depend on `BaseSource.Data`, `BaseSource.Shared`, `BaseSource.ViewModels`, and shared SignalR contracts.
- `UploadYoutubeBot` may depend on shared contracts/helpers but should not directly depend on web UI code.

## Debug Workflow

- Reproduce issues by identifying whether they belong to AppUI, API/service, or desktop bot.
- For render/upload problems, inspect `UploadYoutubeBot/Works`, `UploadYoutubeBot/SeleniumProfiles`, and SignalR interactions first.
- For role/auth/admin problems, inspect `BaseSource.API`, `BaseSource.Services/Services/User*`, and AppUI controllers/views.
- For cloud-link problems, inspect Google Drive / OneDrive helpers in shared/services/bot download flow.

## Regression Checklist

- Confirm solution still builds.
- Confirm auth/role flows still distinguish Admin, Manager, User.
- Confirm SignalR hub contracts remain compatible between API and bot.
- Confirm render/download/upload flow still respects existing DTO/queue contracts.

## Refactor Safety

- Do not change upload/account contracts or DB schema silently.
- Do not assume the desktop bot can run cross-platform without replacing Windows/WPF/Selenium-specific pieces.
- Any migration away from Selenium/Chrome profiles needs a staged fallback because current production behavior depends on it.
