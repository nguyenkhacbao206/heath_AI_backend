"""Food service - business logic cho food & scan."""

import logging
import time

from app.data.foods import FOODS
from app.schemas.food import Food, ImageInfo, ScanResponse
from app.services import opencv_service, sample_matcher
from app.services.opencv_service import ProcessedImage

logger = logging.getLogger(__name__)


class FoodNotFoundError(Exception):
    """Ném ra khi food_id không tồn tại trong mock data."""


def _build_food(data: dict) -> Food:
    """Dựng Food từ mock data, gắn thêm đường dẫn ảnh nếu có ảnh mẫu."""
    filename = sample_matcher.image_filename(data["id"])
    image_url = f"/static/foods/{filename}" if filename else None
    if filename is None:
        logger.debug("Món '%s' chưa có ảnh mẫu -> image_url = null", data["id"])
    return Food(**data, image_url=image_url)


def list_foods() -> list[Food]:
    """Trả về toàn bộ món ăn trong mock data."""
    foods = [_build_food(food) for food in FOODS.values()]
    logger.info("Trả về danh sách %d món: %s", len(foods), [f.id for f in foods])
    return foods


def get_food(food_id: str) -> Food:
    """Lấy một món theo id.

    Raises:
        FoodNotFoundError: nếu id không tồn tại.
    """
    food = FOODS.get(food_id)
    if food is None:
        logger.warning(
            "Không tìm thấy món '%s'. Các id hợp lệ: %s", food_id, list(FOODS.keys())
        )
        raise FoodNotFoundError(f"Food '{food_id}' not found")

    logger.info("Tìm thấy món '%s' (%s)", food_id, food["name"])
    return _build_food(food)


def mock_detect_food(processed: ProcessedImage) -> tuple[str, str]:
    """MOCK food detection - KHÔNG phải AI, KHÔNG nhận diện món ăn thật.

    Thứ tự ưu tiên:
      1. Ảnh trùng / gần giống một ảnh mẫu trong app/data/sample_images/
         -> trả đúng món của ảnh mẫu đó (đây là cách demo có kết quả cố định).
      2. Không khớp mẫu nào -> chọn theo độ sáng trung bình, chỉ để luôn có
         kết quả trả về. Cùng một ảnh luôn cho cùng kết quả nên dễ test.

    ĐÂY LÀ ĐIỂM DUY NHẤT CẦN THAY KHI GẮN AI MODEL THẬT.

    Args:
        processed: ảnh đã qua OpenCV (dùng processed.image nếu gắn model).

    Returns:
        (food_id, method) - method dùng để debug: "exact" | "features" | "fallback".
    """
    matched = sample_matcher.match(processed.image, processed.sha1)
    if matched is not None:
        food_id, method = matched
        logger.info("Nhận dạng: '%s' (bằng %s)", food_id, method)
        return food_id, method

    # Fallback: không có ảnh mẫu nào khớp
    food_ids = list(FOODS.keys())
    brightness = int(processed.image.mean())  # 0..255
    food_id = food_ids[brightness % len(food_ids)]
    logger.warning(
        "FALLBACK: ảnh không giống mẫu nào -> chọn '%s' theo độ sáng trung bình %d",
        food_id,
        brightness,
    )
    return food_id, "fallback"


def scan_food(image_bytes: bytes) -> ScanResponse:
    """Xử lý ảnh upload rồi trả về thông tin dinh dưỡng.

    Flow: process_image() -> mock_detect_food() -> nutrition data.

    Raises:
        opencv_service.InvalidImageError: ảnh không hợp lệ.
    """
    started = time.perf_counter()
    logger.info("=== BẮT ĐẦU SCAN (%.1f KB) ===", len(image_bytes) / 1024)

    processed = opencv_service.process_image(image_bytes)
    food_id, matched_by = mock_detect_food(processed)
    food = get_food(food_id)

    logger.info(
        "=== SCAN XONG: %s | %d kcal | %s | tổng %.0fms ===",
        food.name,
        food.calories,
        matched_by,
        (time.perf_counter() - started) * 1000,
    )

    return ScanResponse(
        success=True,
        food=food,
        image=ImageInfo(width=processed.width, height=processed.height),
        matched_by=matched_by,
    )
