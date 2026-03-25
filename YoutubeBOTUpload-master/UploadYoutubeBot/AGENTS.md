# AGENTS

## Differences From Root

- This folder is Windows-only and targets `net6.0-windows7.0` with WPF.
- Browser automation currently relies on ChromeDriver, Selenium profiles, and persisted channel/account state.
- Media processing uses bundled FFmpeg binaries and should be treated as a local worker/runtime concern.

## Local Debug Workflow

- Start with `Works/MainWork*.cs` to understand orchestration.
- Check `SeleniumProfiles/ChromeProfile.cs` and `SeleniumProfiles/YoutubeProfile.cs` for login/upload breakages.
- Check `Helpers/DownloadHelper.cs` for Google Drive / OneDrive download issues.

## Safety

- Do not assume this module can be moved to Linux unchanged.
- Avoid changing selectors/auth flow in YouTube automation without validating fallback behavior.
