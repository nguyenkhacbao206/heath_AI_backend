"""FastAPI application entrypoint.

Chạy: uvicorn app.main:app --reload
Swagger: http://127.0.0.1:8000/docs
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Bật logging TRƯỚC khi import các module khác để không sót log lúc khởi động
from app.logging_config import setup_logging

setup_logging()

from app.api.router import api_router  # noqa: E402
from app.middleware import register_logging  # noqa: E402
from app.services.sample_matcher import SAMPLE_DIR, load_samples  # noqa: E402

logger = logging.getLogger(__name__)

# Frontend React (Vite) chạy ở cổng 5173
ALLOWED_ORIGINS: list[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app = FastAPI(
    title="Food Scanner API",
    description="Demo backend: nhận ảnh món ăn, xử lý bằng OpenCV, trả nutrition (mock data).",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Log mọi request + mọi lỗi
register_logging(app)

app.include_router(api_router)

# Phục vụ ảnh món ăn để frontend hiển thị trong card kết quả
# -> http://127.0.0.1:8000/static/foods/pho_bo_tai_nam.jpg
app.mount("/static/foods", StaticFiles(directory=SAMPLE_DIR), name="food-images")


@app.on_event("startup")
def on_startup() -> None:
    """Nạp sẵn ảnh mẫu lúc khởi động để request đầu tiên không bị chậm."""
    logger.info("Server đang khởi động...")
    logger.info("CORS cho phép: %s", ALLOWED_ORIGINS)
    logger.info("Thư mục ảnh mẫu: %s", SAMPLE_DIR)

    samples = load_samples(force_reload=True)
    if not samples:
        logger.warning(
            "KHÔNG có ảnh mẫu nào trong %s -> mọi ảnh scan sẽ rơi vào fallback",
            SAMPLE_DIR,
        )

    logger.info("Server sẵn sàng. Swagger: http://127.0.0.1:8000/docs")


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    """Thông tin nhanh về API."""
    return {"message": "Food Scanner API", "docs": "/docs"}
