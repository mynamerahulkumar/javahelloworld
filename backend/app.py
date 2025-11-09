"""
Production entrypoint for the FastAPI backend.

This keeps the container command simple (`python app.py`) while
re-using the logging/setup performed in `main.py`.
"""
import os
import uvicorn  # type: ignore

# Importing `main` executes its module-level logging/config setup
import main  # noqa: F401


def run() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8501"))
    workers = int(os.getenv("BACKEND_WORKERS", "1"))
    log_level = os.getenv("UVICORN_LOG_LEVEL", "info")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=False,
        workers=workers if workers > 0 else 1,
    )


if __name__ == "__main__":
    run()

