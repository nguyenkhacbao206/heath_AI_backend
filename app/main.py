"""FastAPI application entrypoint.

Chạy: uvicorn app.main:app --reload
Swagger: http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.services.sample_matcher import SAMPLE_DIR

# Frontend React (Vite) chạy ở cổng 5173
ALLOWED_ORIGINS: list[str] = [
    "http://localhost:8081",
    "http://127.0.0.1:8081",
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

app.include_router(api_router)

# Phục vụ ảnh món ăn để frontend hiển thị trong card kết quả
# -> http://127.0.0.1:8000/static/foods/pho_bo_tai_nam.jpg
app.mount("/static/foods", StaticFiles(directory=SAMPLE_DIR), name="food-images")


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    """Thông tin nhanh về API."""
    return {"message": "Food Scanner API", "docs": "/docs"}
