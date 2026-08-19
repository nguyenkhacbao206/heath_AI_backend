"""Food service - business logic cho food & scan."""

from app.data.foods import FOODS
from app.schemas.food import Food, ImageInfo, ScanResponse
from app.services import opencv_service, sample_matcher
from app.services.opencv_service import ProcessedImage


class FoodNotFoundError(Exception):
    """Ném ra khi food_id không tồn tại trong mock data."""


def _build_food(data: dict) -> Food:
    """Dựng Food từ mock data, gắn thêm đường dẫn ảnh nếu có ảnh mẫu."""
    filename = sample_matcher.image_filename(data["id"])
    image_url = f"/static/foods/{filename}" if filename else None
    return Food(**data, image_url=image_url)


def list_foods() -> list[Food]:
    """Trả về toàn bộ món ăn trong mock data."""
    return [_build_food(food) for food in FOODS.values()]


def get_food(food_id: str) -> Food:
    """Lấy một món theo id.

    Raises:
        FoodNotFoundError: nếu id không tồn tại.
    """
    food = FOODS.get(food_id)
    if food is None:
        raise FoodNotFoundError(f"Food '{food_id}' not found")
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
        (food_id, method) - method dùng để debug: "exact" | "histogram" | "fallback".
    """
    matched = sample_matcher.match(processed.image, processed.sha1)
    if matched is not None:
        return matched

    # Fallback: không có ảnh mẫu nào khớp
    food_ids = list(FOODS.keys())
    brightness = int(processed.image.mean())  # 0..255
    return food_ids[brightness % len(food_ids)], "fallback"


def scan_food(image_bytes: bytes) -> ScanResponse:
    """Xử lý ảnh upload rồi trả về thông tin dinh dưỡng.

    Flow: process_image() -> mock_detect_food() -> nutrition data.

    Raises:
        opencv_service.InvalidImageError: ảnh không hợp lệ.
    """
    processed = opencv_service.process_image(image_bytes)

    food_id, matched_by = mock_detect_food(processed)
    food = get_food(food_id)

    return ScanResponse(
        success=True,
        food=food,
        image=ImageInfo(width=processed.width, height=processed.height),
        matched_by=matched_by,
    )
