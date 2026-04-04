# Infra Runtime

## Responsibility
- Chua packaging va deploy surface cho host app va worker: Docker, Caddy, systemd, bootstrap script, runtime layout.

## Entry Points
- Host image/runtime: `infra/docker/host/Dockerfile`, `infra/docker/host/docker-compose.yml`
- Reverse proxy/TLS: `infra/caddy/*`
- Services: `infra/systemd/*`
- Bootstrap/deploy helpers: `scripts/*`

## Key Files
- `infra/docker/host/Dockerfile`
- `infra/docker/host/docker-compose.yml`
- `infra/caddy/*`
- `infra/systemd/*`
- `scripts/bootstrap_host.sh`

## Depends On
- Root `.env*`
- Backend app runtime
- Worker services
- Production host topology

## Used By
- Control-plane host
- Worker VPS
- Git-first deploy workflow

## Invariants
- Infra khong chua business logic.
- Runtime artifact (`.env`, `.venv`, data, backups`) phai tach khoi source checkout.
- Production deploy uu tien `git-first checkout` + runtime symlink, khong tro lai copy tay source vo tinh.

## Known Pitfalls
- Drift local/GitHub/VPS tung la pain point lon; task deploy/sync can ghi ro source of truth.
- Caddy/domain/port thay doi de anh huong app khac tren host chung; phai cap nhat file example va script lien quan.
- Mirror nguoc tu VPS khong duoc keo runtime artifact vao repo.

## Related Decisions
- `DEC-001`
- `DEC-003`
- `DEC-004`
