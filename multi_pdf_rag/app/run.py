import os
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = REPO_ROOT / "multi_pdf_rag"
BACKEND_MODULE = "multi_pdf_rag.app.main:app"
FRONTEND_SCRIPT = PACKAGE_ROOT / "frontend" / "streamlit_app.py"


def wait_for_backend(url: str, process: subprocess.Popen, timeout: int = 120):
    deadline = time.time() + timeout
    last_error = None

    while time.time() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Backend exited early with code {process.returncode}")

        try:
            with urlopen(url, timeout=3) as response:
                if response.status < 500:
                    return
        except URLError as exc:
            last_error = exc
        except TimeoutError as exc:
            last_error = exc

        time.sleep(2)

    raise RuntimeError(f"Backend did not become ready at {url}: {last_error}")


if __name__ == "__main__":
    backend_host = os.getenv("BACKEND_HOST", "127.0.0.1")
    backend_port = os.getenv("BACKEND_PORT", "8000")
    frontend_host = os.getenv("STREAMLIT_HOST", "0.0.0.0")
    frontend_port = os.getenv("PORT", os.getenv("STREAMLIT_PORT", "8501"))
    reload_backend = os.getenv("UVICORN_RELOAD", "false").lower() == "true"

    backend_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        BACKEND_MODULE,
        "--host",
        backend_host,
        "--port",
        backend_port,
    ]
    if reload_backend:
        backend_cmd.append("--reload")

    backend = subprocess.Popen(
        backend_cmd,
        cwd=str(REPO_ROOT)
    )

    wait_for_backend(f"http://127.0.0.1:{backend_port}/api/health", backend)

    # Start Streamlit frontend using the same interpreter
    frontend = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(FRONTEND_SCRIPT),
            "--server.address",
            frontend_host,
            "--server.port",
            frontend_port,
            "--server.headless",
            "true",
        ],
        cwd=str(REPO_ROOT)
    )

    backend.wait()
    frontend.wait()
