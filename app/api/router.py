"""Gom toàn bộ route dưới prefix /api."""

from fastapi import APIRouter

from app.api.routes import food, health

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(food.router)
