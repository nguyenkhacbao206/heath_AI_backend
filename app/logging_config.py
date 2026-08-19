"""Cấu hình logging cho toàn bộ app.

Log ra 2 nơi:
  - console (stdout)
  - file logs/app.log (tự xoay vòng khi quá 5MB, giữ 3 file cũ)

Đổi mức log bằng biến môi trường LOG_LEVEL, ví dụ:
    $env:LOG_LEVEL = "DEBUG"; uvicorn app.main:app --reload
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR: Path = Path(__file__).resolve().parent.parent / "logs"
LOG_FILE: Path = LOG_DIR / "app.log"

LOG_FORMAT: str = "%(asctime)s | %(levelname)-7s | %(name)-28s | %(message)s"
DATE_FORMAT: str = "%H:%M:%S"


def setup_logging() -> None:
    """Bật logging cho toàn app. Gọi một lần lúc khởi động."""
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    # Console Windows mặc định là cp1252 -> in tiếng Việt sẽ lỗi UnicodeEncodeError.
    # Ép stdout sang UTF-8 để log tiếng Việt hiển thị bình thường.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    LOG_DIR.mkdir(exist_ok=True)
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()  # tránh log bị nhân đôi khi --reload
    root.addHandler(console_handler)
    root.addHandler(file_handler)

    # Cho log của uvicorn đi chung định dạng với log của app
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True

    logging.getLogger(__name__).info(
        "Logging đã bật | mức=%s | file=%s", level_name, LOG_FILE
    )
