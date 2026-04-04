from __future__ import annotations

import argparse
import getpass
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.store import store
from backend.app.worker_bootstrap import (  # noqa: E402
    WorkerBootstrapError,
    bootstrap_worker_via_ssh,
    build_worker_bootstrap_request,
    build_worker_bootstrap_control_plane_url,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap a new worker VPS and register it to the control-plane.")
    parser.add_argument("--vps-ip", required=True, help="Worker VPS public IP.")
    parser.add_argument("--ssh-user", default="root", help="SSH user, defaults to root.")
    parser.add_argument("--password", help="SSH password.")
    parser.add_argument("--ssh-key-file", help="Path to an SSH private key file.")
    parser.add_argument("--manager-name", default="system", help="Initial WORKER_MANAGER value.")
    parser.add_argument("--control-plane-url", help="Control-plane URL used by the worker.")
    parser.add_argument("--branch", help="Git branch/ref to bootstrap on the worker.")
    parser.add_argument("--repo-url", help="Git repository URL for bootstrap.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ssh_key = ""
    if args.ssh_key_file:
        ssh_key = Path(args.ssh_key_file).expanduser().read_text(encoding="utf-8")

    password = args.password or ""
    if not ssh_key and not password:
        password = getpass.getpass("SSH password: ").strip()

    worker_id = store.suggest_next_worker_bootstrap_id()
    control_plane_url = build_worker_bootstrap_control_plane_url(args.control_plane_url)

    try:
        request = build_worker_bootstrap_request(
            vps_ip=args.vps_ip,
            ssh_user=args.ssh_user,
            password=password or None,
            ssh_private_key=ssh_key or None,
            shared_secret=store.get_worker_shared_secret(),
            control_plane_url=control_plane_url,
            worker_id=worker_id,
            manager_name=args.manager_name,
            repo_url=args.repo_url,
            branch=args.branch,
        )
        result = bootstrap_worker_via_ssh(request)
    except WorkerBootstrapError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    print(f"worker_id={result.worker_id}")
    print(f"worker_name={result.worker_name}")
    print(f"vps_ip={result.vps_ip}")
    print(f"service_enabled={result.service_enabled}")
    print(f"service_active={result.service_active}")
    print("Bootstrap thanh cong. Worker se tu register voi control-plane khi service len.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
