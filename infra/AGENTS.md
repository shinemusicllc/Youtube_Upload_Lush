# Infra AGENTS

## Pham vi
- `infra/docker/`: build/runtime cho host app.
- `infra/caddy/`: reverse proxy/TLS.
- `infra/systemd/`: service files cho worker.

## Rule
- Infra chi chua packaging va service config, khong chua business logic.
- Moi bien moi truong production phai co file example di kem.
- Truoc khi doi port/domain/secret, cap nhat file example va script bootstrap lien quan.
