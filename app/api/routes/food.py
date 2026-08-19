"""Food routes: list, detail, scan."""

import logging

from fastapi import APIRouter, File, HTTPException, Request, UploadFile, status

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
async def scan_food(
    request: Request,
    image: UploadFile = File(..., description="Ảnh món ăn"),
) -> ScanResponse:
    """Nhận ảnh từ frontend, xử lý bằng OpenCV, trả về thông tin dinh dưỡng.

    Food detection ở đây là MOCK (xem food_service.mock_detect_food).
    """
    request_id = getattr(request.state, "request_id", "?")
    logger.info(
        "[%s] Nhận file: tên='%s' | content_type='%s'",
        request_id,
        image.filename,
        image.content_type,
    )

    # Chặn sớm các file rõ ràng không phải ảnh (pdf, txt, ...)
    if image.content_type is None or not image.content_type.startswith("image/"):
        logger.warning(
            "[%s] Từ chối file '%s': content_type='%s' không phải image/*",
            request_id,
            image.filename,
            image.content_type,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is not an image",
        )

    image_bytes = await image.read()
    logger.info("[%s] Đọc được %d bytes từ file upload", request_id, len(image_bytes))

    try:
        return food_service.scan_food(image_bytes)
    except InvalidImageError as exc:
        # OpenCV không decode được -> lỗi từ phía client
        logger.warning("[%s] Ảnh không hợp lệ: %s", request_id, exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:  # lỗi ngoài dự kiến -> 500
        # exc_info tự động -> log full traceback, biết chính xác dòng nào lỗi
        logger.exception("[%s] Lỗi không mong muốn khi scan ảnh", request_id)
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
