from __future__ import annotations

import io
import os
import re
import shlex
from dataclasses import dataclass
from pathlib import Path
from threading import Thread

try:
    import paramiko
except ImportError:  # pragma: no cover - runtime dependency on deploy host
    paramiko = None


ROOT_DIR = Path(__file__).resolve().parents[2]
SCRIPT_DIR = ROOT_DIR / "scripts"
BOOTSTRAP_SCRIPT_PATH = SCRIPT_DIR / "bootstrap_worker.sh"
GIT_LAYOUT_SCRIPT_PATH = SCRIPT_DIR / "git_runtime_layout.sh"
DECOMMISSION_SCRIPT_PATH = SCRIPT_DIR / "decommission_worker.sh"
DEFAULT_REPO_URL = "https://github.com/shinemusicllc/Youtube_Upload_Lush.git"
DEFAULT_BRANCH = "main"
DEFAULT_APP_DIR = "/opt/youtube-upload-lush"
DEFAULT_RUNTIME_DIR = "/opt/youtube-upload-lush-runtime"


class WorkerBootstrapError(RuntimeError):
    pass


@dataclass(slots=True)
class WorkerBootstrapRequest:
    vps_ip: str
    ssh_user: str
    control_plane_url: str
    shared_secret: str
    worker_id: str
    worker_name: str
    manager_name: str = "system"
    group: str = ""
    password: str | None = None
    ssh_private_key: str | None = None
    repo_url: str = DEFAULT_REPO_URL
    branch: str = DEFAULT_BRANCH
    app_dir: str = DEFAULT_APP_DIR
    runtime_dir: str = DEFAULT_RUNTIME_DIR
    browser_public_base_url: str | None = None
    capacity: int = 1
    threads: int = 1
    heartbeat_seconds: int = 15
    poll_seconds: int = 5
    connect_timeout: int = 20


@dataclass(slots=True)
class WorkerBootstrapResult:
    worker_id: str
    worker_name: str
    vps_ip: str
    service_enabled: str
    service_active: str


@dataclass(slots=True)
class WorkerDecommissionRequest:
    vps_ip: str
    ssh_user: str
    password: str | None = None
    ssh_private_key: str | None = None
    app_dir: str = DEFAULT_APP_DIR
    runtime_dir: str = DEFAULT_RUNTIME_DIR
    connect_timeout: int = 20


@dataclass(slots=True)
class WorkerDecommissionResult:
    vps_ip: str
    service_enabled: str
    service_active: str


def suggest_next_worker_id(existing_worker_ids: list[str] | tuple[str, ...] | set[str]) -> str:
    max_suffix = 0
    for raw_value in existing_worker_ids:
        match = re.fullmatch(r"worker-(\d+)", str(raw_value or "").strip(), flags=re.IGNORECASE)
        if not match:
            continue
        max_suffix = max(max_suffix, int(match.group(1)))
    return f"worker-{max_suffix + 1:02d}"


def build_worker_bootstrap_control_plane_url(fallback_url: str | None = None) -> str:
    configured = str(os.getenv("WORKER_BOOTSTRAP_CONTROL_PLANE_URL", "")).strip()
    if configured:
        return configured.rstrip("/")
    fallback = str(fallback_url or "").strip()
    if fallback:
        return fallback.rstrip("/")
    raise WorkerBootstrapError("Chua co WORKER_BOOTSTRAP_CONTROL_PLANE_URL de bootstrap worker.")


def build_worker_bootstrap_request(
    *,
    vps_ip: str,
    ssh_user: str,
    shared_secret: str,
    control_plane_url: str,
    worker_id: str,
    manager_name: str,
    password: str | None = None,
    ssh_private_key: str | None = None,
    repo_url: str | None = None,
    branch: str | None = None,
) -> WorkerBootstrapRequest:
    normalized_ip = str(vps_ip or "").strip()
    if not normalized_ip:
        raise WorkerBootstrapError("VPS IP la bat buoc.")
    normalized_user = str(ssh_user or "").strip() or "root"
    normalized_key = str(ssh_private_key or "").strip()
    normalized_password = str(password or "").strip()
    if not normalized_key and not normalized_password:
        raise WorkerBootstrapError("Can nhap password hoac SSH key de bootstrap worker.")
    return WorkerBootstrapRequest(
        vps_ip=normalized_ip,
        ssh_user=normalized_user,
        password=normalized_password or None,
        ssh_private_key=normalized_key or None,
        control_plane_url=build_worker_bootstrap_control_plane_url(control_plane_url),
        shared_secret=str(shared_secret or "").strip(),
        worker_id=str(worker_id or "").strip(),
        worker_name=normalized_ip,
        manager_name=str(manager_name or "").strip() or "system",
        group="",
        repo_url=str(repo_url or os.getenv("WORKER_BOOTSTRAP_REPO_URL", DEFAULT_REPO_URL)).strip() or DEFAULT_REPO_URL,
        branch=str(branch or os.getenv("WORKER_BOOTSTRAP_BRANCH", DEFAULT_BRANCH)).strip() or DEFAULT_BRANCH,
        browser_public_base_url=f"http://{normalized_ip}",
    )


def build_worker_decommission_request(
    *,
    vps_ip: str,
    ssh_user: str,
    password: str | None = None,
    ssh_private_key: str | None = None,
) -> WorkerDecommissionRequest:
    normalized_ip = str(vps_ip or "").strip()
    if not normalized_ip:
        raise WorkerBootstrapError("VPS IP la bat buoc.")
    normalized_user = str(ssh_user or "").strip() or "root"
    normalized_key = str(ssh_private_key or "").strip()
    normalized_password = str(password or "").strip()
    if not normalized_key and not normalized_password:
        raise WorkerBootstrapError("Can nhap password hoac SSH key de go worker khoi VPS.")
    return WorkerDecommissionRequest(
        vps_ip=normalized_ip,
        ssh_user=normalized_user,
        password=normalized_password or None,
        ssh_private_key=normalized_key or None,
    )


def _ensure_runtime_dependency() -> None:
    if paramiko is None:
        raise WorkerBootstrapError("Thieu dependency `paramiko`. Hay cai lai backend requirements truoc.")
    if not BOOTSTRAP_SCRIPT_PATH.exists():
        raise WorkerBootstrapError(f"Khong tim thay script bootstrap: {BOOTSTRAP_SCRIPT_PATH}")
    if not GIT_LAYOUT_SCRIPT_PATH.exists():
        raise WorkerBootstrapError(f"Khong tim thay script runtime layout: {GIT_LAYOUT_SCRIPT_PATH}")
    if not DECOMMISSION_SCRIPT_PATH.exists():
        raise WorkerBootstrapError(f"Khong tim thay script decommission: {DECOMMISSION_SCRIPT_PATH}")


def _load_private_key(raw_key: str):
    key_text = str(raw_key or "").strip()
    if not key_text:
        raise WorkerBootstrapError("SSH key rong.")
    last_error: Exception | None = None
    for key_type in (
        getattr(paramiko, "Ed25519Key", None),
        getattr(paramiko, "RSAKey", None),
        getattr(paramiko, "ECDSAKey", None),
        getattr(paramiko, "DSSKey", None),
    ):
        if key_type is None:
            continue
        try:
            return key_type.from_private_key(io.StringIO(key_text))
        except Exception as exc:  # pragma: no cover - parser branch depends on key type
            last_error = exc
    raise WorkerBootstrapError(f"SSH key khong hop le: {last_error or 'unknown error'}")


def _connect_client(request: WorkerBootstrapRequest):
    _ensure_runtime_dependency()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    connect_kwargs = {
        "hostname": request.vps_ip,
        "username": request.ssh_user,
        "timeout": request.connect_timeout,
        "banner_timeout": request.connect_timeout,
        "auth_timeout": request.connect_timeout,
        "look_for_keys": False,
        "allow_agent": False,
    }
    if request.ssh_private_key:
        connect_kwargs["pkey"] = _load_private_key(request.ssh_private_key)
    else:
        connect_kwargs["password"] = request.password
    try:
        client.connect(**connect_kwargs)
        return client
    except paramiko.AuthenticationException as exc:
        client.close()
        raise WorkerBootstrapError("Dang nhap SSH that bai.") from exc
    except Exception as exc:  # pragma: no cover - network/runtime path
        client.close()
        raise WorkerBootstrapError(f"Khong ket noi duoc VPS {request.vps_ip}: {exc}") from exc


def _run_remote_command(client, command: str) -> tuple[int, str, str]:
    stdin, stdout, stderr = client.exec_command(command)
    exit_code = stdout.channel.recv_exit_status()
    return exit_code, stdout.read().decode("utf-8", errors="replace"), stderr.read().decode("utf-8", errors="replace")


def _upload_remote_script(sftp, local_path: Path, remote_path: str) -> None:
    content = local_path.read_bytes().replace(b"\r\n", b"\n")
    with sftp.file(remote_path, "wb") as remote_file:
        remote_file.write(content)


def _build_worker_env_file(request: WorkerBootstrapRequest) -> str:
    browser_public_base_url = str(request.browser_public_base_url or f"http://{request.vps_ip}").rstrip("/")
    return "\n".join(
        [
            f"CONTROL_PLANE_URL={request.control_plane_url}",
            f"WORKER_SHARED_SECRET={request.shared_secret}",
            f"WORKER_ID={request.worker_id}",
            f"WORKER_NAME={request.worker_name}",
            f"WORKER_MANAGER={request.manager_name}",
            "WORKER_GROUP=",
            f"WORKER_CAPACITY={request.capacity}",
            f"WORKER_THREADS={request.threads}",
            f"WORKER_HEARTBEAT_SECONDS={request.heartbeat_seconds}",
            f"WORKER_POLL_SECONDS={request.poll_seconds}",
            "WORKER_SIMULATE_JOBS=false",
            "WORKER_EXECUTE_JOBS=true",
            "WORKER_SIMULATE_STEP_SECONDS=2.5",
            "WORKER_UPLOAD_TO_YOUTUBE=true",
            "WORKER_KEEP_JOB_DIRS=false",
            "YOUTUBE_UPLOAD_CHUNK_BYTES=8388608",
            "BROWSER_SESSION_ENABLED=1",
            f"BROWSER_SESSION_PUBLIC_BASE_URL={browser_public_base_url}",
            "BROWSER_SESSION_DISPLAY_BASE=90",
            "BROWSER_SESSION_VNC_PORT_BASE=15900",
            "BROWSER_SESSION_WEB_PORT_BASE=16080",
            "BROWSER_SESSION_DEBUG_PORT_BASE=19220",
            "BROWSER_SESSION_BIND_HOST=0.0.0.0",
            "BROWSER_SESSION_START_URL=https://studio.youtube.com",
            "BROWSER_SESSION_NOVNC_WEB_DIR=/usr/share/novnc",
            "BROWSER_SESSION_CHROMIUM_BIN=google-chrome-stable",
            "WORKER_NETWORK_RETRY_BASE_SECONDS=3",
            "WORKER_NETWORK_RETRY_MAX_SECONDS=30",
            "WORKER_PROGRESS_RETRY_ATTEMPTS=3",
            "",
        ]
    )


def bootstrap_worker_via_ssh(request: WorkerBootstrapRequest) -> WorkerBootstrapResult:
    if not request.shared_secret:
        raise WorkerBootstrapError("Worker shared secret dang rong.")
    client = _connect_client(request)
    temp_dir = ""
    try:
        exit_code, stdout, stderr = _run_remote_command(client, "mktemp -d /tmp/youtube-worker-bootstrap-XXXXXX")
        if exit_code != 0:
            raise WorkerBootstrapError(stderr.strip() or stdout.strip() or "Khong tao duoc thu muc tam tren VPS.")
        temp_dir = stdout.strip()
        if not temp_dir:
            raise WorkerBootstrapError("Khong nhan duoc duong dan thu muc tam tren VPS.")

        sftp = client.open_sftp()
        try:
            remote_bootstrap_script = f"{temp_dir}/bootstrap_worker.sh"
            remote_layout_script = f"{temp_dir}/git_runtime_layout.sh"
            remote_env_file = f"{temp_dir}/youtube-upload-worker.env"
            _upload_remote_script(sftp, BOOTSTRAP_SCRIPT_PATH, remote_bootstrap_script)
            _upload_remote_script(sftp, GIT_LAYOUT_SCRIPT_PATH, remote_layout_script)
            with sftp.file(remote_env_file, "w") as remote_file:
                remote_file.write(_build_worker_env_file(request))
        finally:
            sftp.close()

        sudo_prefix = "" if request.ssh_user == "root" else "sudo "
        chmod_command = "chmod 755 {bootstrap} {layout}".format(
            bootstrap=shlex.quote(remote_bootstrap_script),
            layout=shlex.quote(remote_layout_script),
        )
        install_env_command = "{sudo}install -m 600 {src} /etc/youtube-upload-worker.env".format(
            sudo=sudo_prefix,
            src=shlex.quote(remote_env_file),
        )
        bootstrap_command = (
            "{sudo}env APP_DIR={app_dir} RUNTIME_DIR={runtime_dir} REPO_URL={repo_url} BRANCH={branch} "
            "bash {script}"
        ).format(
            sudo=sudo_prefix,
            app_dir=shlex.quote(request.app_dir),
            runtime_dir=shlex.quote(request.runtime_dir),
            repo_url=shlex.quote(request.repo_url),
            branch=shlex.quote(request.branch),
            script=shlex.quote(remote_bootstrap_script),
        )
        for command in (chmod_command, install_env_command, bootstrap_command):
            exit_code, stdout, stderr = _run_remote_command(client, command)
            if exit_code != 0:
                message = stderr.strip() or stdout.strip() or f"Remote command failed: {command}"
                raise WorkerBootstrapError(message)

        _, enabled_stdout, _ = _run_remote_command(
            client,
            f"{sudo_prefix}systemctl is-enabled youtube-upload-worker.service",
        )
        _, active_stdout, active_stderr = _run_remote_command(
            client,
            f"{sudo_prefix}systemctl is-active youtube-upload-worker.service",
        )
        service_enabled = enabled_stdout.strip() or "unknown"
        service_active = active_stdout.strip() or active_stderr.strip() or "unknown"
        if service_active != "active":
            _, status_stdout, status_stderr = _run_remote_command(
                client,
                f"{sudo_prefix}systemctl status youtube-upload-worker.service --no-pager -n 40",
            )
            raise WorkerBootstrapError(
                (status_stderr.strip() or status_stdout.strip() or "Worker service khong active sau bootstrap.")
            )
        return WorkerBootstrapResult(
            worker_id=request.worker_id,
            worker_name=request.worker_name,
            vps_ip=request.vps_ip,
            service_enabled=service_enabled,
            service_active=service_active,
        )
    finally:
        if temp_dir:
            _run_remote_command(client, f"rm -rf {shlex.quote(temp_dir)}")
        client.close()


def decommission_worker_via_ssh(request: WorkerDecommissionRequest) -> WorkerDecommissionResult:
    client = _connect_client(request)
    temp_dir = ""
    try:
        exit_code, stdout, stderr = _run_remote_command(client, "mktemp -d /tmp/youtube-worker-decommission-XXXXXX")
        if exit_code != 0:
            raise WorkerBootstrapError(stderr.strip() or stdout.strip() or "Khong tao duoc thu muc tam tren VPS.")
        temp_dir = stdout.strip()
        if not temp_dir:
            raise WorkerBootstrapError("Khong nhan duoc duong dan thu muc tam tren VPS.")

        remote_script = f"{temp_dir}/decommission_worker.sh"
        sftp = client.open_sftp()
        try:
            _upload_remote_script(sftp, DECOMMISSION_SCRIPT_PATH, remote_script)
        finally:
            sftp.close()

        sudo_prefix = "" if request.ssh_user == "root" else "sudo "
        chmod_command = f"chmod 755 {shlex.quote(remote_script)}"
        decommission_command = (
            "{sudo}env APP_DIR={app_dir} RUNTIME_DIR={runtime_dir} bash {script}"
        ).format(
            sudo=sudo_prefix,
            app_dir=shlex.quote(request.app_dir),
            runtime_dir=shlex.quote(request.runtime_dir),
            script=shlex.quote(remote_script),
        )
        for command in (chmod_command, decommission_command):
            exit_code, stdout, stderr = _run_remote_command(client, command)
            if exit_code != 0:
                message = stderr.strip() or stdout.strip() or f"Remote command failed: {command}"
                raise WorkerBootstrapError(message)

        enabled_code, enabled_stdout, enabled_stderr = _run_remote_command(
            client,
            f"{sudo_prefix}systemctl is-enabled youtube-upload-worker.service",
        )
        active_code, active_stdout, active_stderr = _run_remote_command(
            client,
            f"{sudo_prefix}systemctl is-active youtube-upload-worker.service",
        )
        service_enabled = (enabled_stdout.strip() or enabled_stderr.strip() or "not-found") if enabled_code != 0 else (
            enabled_stdout.strip() or "unknown"
        )
        service_active = (active_stdout.strip() or active_stderr.strip() or "inactive") if active_code != 0 else (
            active_stdout.strip() or "unknown"
        )
        return WorkerDecommissionResult(
            vps_ip=request.vps_ip,
            service_enabled=service_enabled,
            service_active=service_active,
        )
    finally:
        if temp_dir:
            _run_remote_command(client, f"rm -rf {shlex.quote(temp_dir)}")
        client.close()


def _run_worker_install_operation(store, operation_id: str, request: WorkerBootstrapRequest) -> None:
    try:
        store.update_worker_operation(
            operation_id,
            status="running",
            message=f"Dang ket noi SSH vao {request.vps_ip} va cai worker service...",
        )
        result = bootstrap_worker_via_ssh(request)
        store.update_worker_operation(
            operation_id,
            status="awaiting_registration",
            message=(
                f"Da cai worker service tren {result.vps_ip}. Dang cho BOT "
                "ket noi lai voi control-plane..."
            ),
        )
    except Exception as exc:
        store.update_worker_operation(
            operation_id,
            status="failed",
            message=str(exc),
        )


def start_worker_install_operation(
    *,
    store,
    request: WorkerBootstrapRequest,
    ssh_user: str,
    manager_id: str | None,
    manager_name: str,
    group: str = "",
) -> dict:
    task = store.enqueue_worker_install_operation(
        worker_id=request.worker_id,
        worker_name=request.worker_name,
        vps_ip=request.vps_ip,
        ssh_user=ssh_user,
        manager_id=manager_id,
        manager_name=manager_name,
        group=group,
    )
    Thread(
        target=_run_worker_install_operation,
        args=(store, str(task.get("id") or ""), request),
        name=f"worker-install-{request.worker_id}",
        daemon=True,
    ).start()
    return task


def _run_worker_decommission_operation(
    store,
    operation_id: str,
    worker_id: str,
    request: WorkerDecommissionRequest,
) -> None:
    try:
        store.update_worker_operation(
            operation_id,
            status="running",
            message=f"Dang stop service va don app tren VPS {request.vps_ip}...",
        )
        decommission_worker_via_ssh(request)
        store.finalize_decommissioned_bot(worker_id, operation_id)
    except Exception as exc:
        store.update_worker_operation(
            operation_id,
            status="failed",
            message=str(exc),
        )


def start_worker_decommission_operation(
    *,
    store,
    worker_id: str,
    request: WorkerDecommissionRequest,
    ssh_user: str,
) -> dict:
    task = store.enqueue_worker_decommission_operation(
        worker_id=worker_id,
        vps_ip=request.vps_ip,
        ssh_user=ssh_user,
    )
    Thread(
        target=_run_worker_decommission_operation,
        args=(store, str(task.get("id") or ""), worker_id, request),
        name=f"worker-decommission-{worker_id}",
        daemon=True,
    ).start()
    return task
