from __future__ import annotations

import argparse
import os
import socket
import sys
import threading
import time
import webbrowser
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path


def _detect_project_root() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(getattr(sys, "_MEIPASS")).resolve()
    return Path(__file__).resolve().parents[2]


def _detect_runtime_root(project_root: Path) -> Path:
    if getattr(sys, "frozen", False):
        runtime_root = Path(sys.executable).resolve().parent / "runtime"
    else:
        runtime_root = project_root
    runtime_root.mkdir(parents=True, exist_ok=True)
    return runtime_root


def _port_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock.connect_ex((host, port)) != 0


def _choose_port(host: str, preferred: int) -> int:
    if preferred > 0 and _port_available(host, preferred):
        return preferred
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return int(sock.getsockname()[1])


def _wait_for_health(host: str, port: int, timeout_seconds: float = 12.0) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            conn = HTTPConnection(host, port, timeout=2)
            conn.request("GET", "/health")
            response = conn.getresponse()
            body = response.read().decode("utf-8", errors="ignore")
            conn.close()
            if response.status == 200 and "\"ok\": true" in body:
                return True
        except Exception:
            time.sleep(0.2)
    return False


def _start_embedded_server(host: str, port: int) -> tuple[ThreadingHTTPServer, threading.Thread]:
    from a13_starter.api_server import A13RequestHandler
    from a13_starter.src.analysis_storage import init_storage

    init_storage()
    server = ThreadingHTTPServer((host, port), A13RequestHandler)
    thread = threading.Thread(target=server.serve_forever, name="a13-desktop-server", daemon=True)
    thread.start()
    return server, thread


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Launch the A13 CareerLoop desktop shell.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--title", default="CareerLoop A13")
    parser.add_argument("--width", type=int, default=1480)
    parser.add_argument("--height", type=int, default=960)
    parser.add_argument("--smoke-test", action="store_true", help="Start the embedded server, verify health, then exit.")
    parser.add_argument("--browser-fallback", action="store_true", help="Open the system browser instead of a desktop webview.")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    project_root = _detect_project_root()
    runtime_root = _detect_runtime_root(project_root)
    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)
    os.environ.setdefault("A13_PROJECT_ROOT", str(project_root))
    os.environ.setdefault("A13_RUNTIME_DIR", str(runtime_root))

    host = args.host
    port = _choose_port(host, args.port)
    server, thread = _start_embedded_server(host, port)
    app_url = f"http://{host}:{port}/"

    try:
        if not _wait_for_health(host, port):
            raise RuntimeError(f"Embedded server failed to become healthy on {app_url}")

        if args.smoke_test:
            print(f"[SMOKE] server_ready {app_url}")
            return 0

        if args.browser_fallback:
            webbrowser.open(app_url)
            print(f"[BROWSER] {app_url}")
            try:
                while thread.is_alive():
                    time.sleep(0.5)
            except KeyboardInterrupt:
                return 0
            return 0

        import webview

        webview.create_window(
            args.title,
            app_url,
            width=max(1200, args.width),
            height=max(760, args.height),
            min_size=(1100, 720),
            text_select=True,
        )
        webview.start()
        return 0
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    raise SystemExit(main())
