import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = REPO_ROOT / "multi_pdf_rag"
BACKEND_MODULE = "multi_pdf_rag.app.main:app"
FRONTEND_SCRIPT = PACKAGE_ROOT / "frontend" / "streamlit_app.py"

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

    # Small delay to give the backend time to start
    time.sleep(2)

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
