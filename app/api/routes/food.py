"""Food routes: list, detail, scan."""

import logging

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.schemas.food import Food, FoodListResponse, ScanResponse
from app.services import food_service
from app.services.opencv_service import InvalidImageError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/foods", tags=["foods"])


@router.get("", response_model=FoodListResponse)
def get_foods() -> FoodListResponse:
    """Danh sách toàn bộ món ăn (mock data)."""
    return FoodListResponse(foods=food_service.list_foods())


# Khai báo /scan TRƯỚC /{food_id} để tránh nhầm "scan" thành food_id
@router.post("/scan", response_model=ScanResponse)
async def scan_food(image: UploadFile = File(..., description="Ảnh món ăn")) -> ScanResponse:
    """Nhận ảnh từ frontend, xử lý bằng OpenCV, trả về thông tin dinh dưỡng.

    Food detection ở đây là MOCK (xem food_service.mock_detect_food).
    """
    # Chặn sớm các file rõ ràng không phải ảnh (pdf, txt, ...)
    if image.content_type is None or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is not an image",
        )

    image_bytes = await image.read()

    try:
        return food_service.scan_food(image_bytes)
    except InvalidImageError as exc:
        # OpenCV không decode được -> lỗi từ phía client
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:  # lỗi ngoài dự kiến -> 500
        logger.exception("Unexpected error while scanning food")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from exc


@router.get("/{food_id}", response_model=Food)
def get_food(food_id: str) -> Food:
    """Thông tin một món theo id. Trả 404 nếu không tồn tại."""
    try:
        return food_service.get_food(food_id)
    except food_service.FoodNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Food '{food_id}' not found",
        ) from exc
