"""Start the ValveGuard API and thin client on loopback for a laptop demo.

Judges can run this from a notebook or as:

    python notebooks/launch_demo.py
"""

from __future__ import annotations

import argparse
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

_NOTEBOOKS = Path(__file__).resolve().parent
if str(_NOTEBOOKS) not in sys.path:
    sys.path.insert(0, str(_NOTEBOOKS))

from _paths import CLIENT_DIR, ROOT


API_HOST = "127.0.0.1"
API_PORT = 8000
CLIENT_PORT = 4173
READY_URL = f"http://{API_HOST}:{API_PORT}/health/ready"
CLIENT_URL = f"http://{API_HOST}:{CLIENT_PORT}"
LOGIN_EMAIL = "clinician@valveguard.demo"
LOGIN_PASSWORD = "1234"


def port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.4)
        return sock.connect_ex((host, port)) == 0


def wait_ready(url: str, timeout_s: float = 40.0) -> str:
    deadline = time.time() + timeout_s
    last_error = "timed out"
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                return response.read().decode("utf-8")
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = str(exc)
            time.sleep(0.5)
    raise RuntimeError(f"API did not become ready at {url}: {last_error}")


def _popen(args: list[str]) -> subprocess.Popen:
    kwargs: dict = {
        "cwd": str(ROOT),
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    return subprocess.Popen(args, **kwargs)


def ensure_servers(*, open_browser: bool = False) -> dict[str, str]:
    """Start missing loopback servers. Safe to call if they already run."""

    started: list[str] = []
    python = sys.executable
    if not port_open(API_HOST, API_PORT):
        _popen([python, "-m", "backend"])
        started.append("api")
    if not port_open(API_HOST, CLIENT_PORT):
        if not CLIENT_DIR.is_dir():
            raise FileNotFoundError(f"missing client directory: {CLIENT_DIR}")
        _popen(
            [
                python,
                "-m",
                "http.server",
                str(CLIENT_PORT),
                "--directory",
                str(CLIENT_DIR),
            ]
        )
        started.append("client")

    body = wait_ready(READY_URL)
    if open_browser:
        webbrowser.open(CLIENT_URL)
    return {
        "api": READY_URL,
        "client": CLIENT_URL,
        "login_email": LOGIN_EMAIL,
        "login_password": LOGIN_PASSWORD,
        "started": ",".join(started) or "already-running",
        "ready_body": body,
        "repo": str(ROOT),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Launch ValveGuard on 127.0.0.1 for a laptop demo."
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open the default browser.",
    )
    args = parser.parse_args()
    info = ensure_servers(open_browser=not args.no_browser)
    print("ValveGuard demo")
    print("  repo   ", info["repo"])
    print("  API    ", info["api"])
    print("  client ", info["client"])
    print("  login  ", info["login_email"], "/", info["login_password"])
    print("  start  ", info["started"])
    print("Use 127.0.0.1, not localhost. Do not bind 0.0.0.0.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
