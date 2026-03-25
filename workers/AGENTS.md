# Workers AGENTS

## Pham vi
- `workers/agent/` la khu vuc worker Python phia VPS.
- Worker uu tien nhiem vu `register / heartbeat / claim / progress / complete`.

## Build / Test
- Syntax: `python -m compileall workers/agent`
- Smoke test co the dung `python workers/agent/main.py` voi env stub hoac mock control plane.

## Coding conventions
- Worker phai outbound-only, chu dong goi control plane.
- Khong hardcode secret hay host URL trong code; doc qua env.
- FFmpeg/render pipeline ve sau phai tach file/module rieng, khong nhot het vao `main.py`.

## Safety rules
- Khong de worker phu thuoc session browser local.
- Khong mount storage tu host app sang worker.
