"""Middleware và exception handler - log mọi request và mọi lỗi."""

import logging
import time
import uuid

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("app.request")


def register_logging(app: FastAPI) -> None:
    """Gắn middleware log request + các handler log lỗi vào app."""

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log mỗi request: đường dẫn, status, thời gian xử lý."""
        request_id = uuid.uuid4().hex[:8]
        request.state.request_id = request_id  # để route/service dùng chung

        client = request.client.host if request.client else "?"
        logger.info(
            "[%s] --> %s %s | từ %s", request_id, request.method, request.url.path, client
        )

        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            elapsed = (time.perf_counter() - started) * 1000
            # exc_info=True -> in đầy đủ traceback để biết lỗi ở dòng nào
            logger.exception(
                "[%s] <-- LỖI CHƯA XỬ LÝ %s %s | %.1fms",
                request_id,
                request.method,
                request.url.path,
                elapsed,
            )
            raise

        elapsed = (time.perf_counter() - started) * 1000
        level = logging.WARNING if response.status_code >= 400 else logging.INFO
        logger.log(
            level,
            "[%s] <-- %s %s | %.1fms",
            request_id,
            response.status_code,
            request.url.path,
            elapsed,
        )
        return response

    @app.exception_handler(RequestValidationError)
    async def on_validation_error(request: Request, exc: RequestValidationError):
        """Client gửi dữ liệu sai định dạng (thiếu field image, sai kiểu...)."""
        request_id = getattr(request.state, "request_id", "?")
        logger.warning(
            "[%s] 422 dữ liệu gửi lên không hợp lệ tại %s: %s",
            request_id,
            request.url.path,
            exc.errors(),
        )
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.exception_handler(StarletteHTTPException)
    async def on_http_error(request: Request, exc: StarletteHTTPException):
        """Các lỗi chủ động ném ra bằng HTTPException (400, 404...)."""
        request_id = getattr(request.state, "request_id", "?")
        logger.warning(
            "[%s] %s tại %s: %s", request_id, exc.status_code, request.url.path, exc.detail
        )
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(Exception)
    async def on_unhandled_error(request: Request, exc: Exception):
        """Lỗi ngoài dự kiến - log full traceback, trả 500 gọn cho client."""
        request_id = getattr(request.state, "request_id", "?")
        logger.exception("[%s] 500 lỗi server tại %s", request_id, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "request_id": request_id},
        )
