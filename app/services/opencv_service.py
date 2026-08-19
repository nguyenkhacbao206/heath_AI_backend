"""OpenCV service.

Nhiệm vụ của file này CHỈ là xử lý ảnh cơ bản:
  - decode bytes -> ảnh
  - kiểm tra ảnh hợp lệ
  - lấy width / height
  - resize nếu ảnh quá lớn
  - hash nội dung file (để so khớp ảnh mẫu)

KHÔNG có nhận diện món ăn ở đây. OpenCV không phải AI model.
"""

import logging
import time
from dataclasses import dataclass

import cv2
import numpy as np

from app.services.sample_matcher import sha1_of

logger = logging.getLogger(__name__)

# Cạnh dài nhất tối đa sau khi resize (giảm chi phí xử lý ảnh lớn từ camera)
MAX_SIZE: int = 1024


class InvalidImageError(Exception):
    """Ném ra khi bytes gửi lên không phải là ảnh đọc được."""


@dataclass
class ProcessedImage:
    """Kết quả xử lý ảnh, dùng cho tầng service phía trên."""

    width: int  # width gốc của ảnh
    height: int  # height gốc của ảnh
    image: np.ndarray  # ảnh (đã resize nếu cần) - dùng cho bước detect
    sha1: str  # hash của file gốc


def process_image(image_bytes: bytes) -> ProcessedImage:
    """Đọc và xử lý ảnh bằng OpenCV.

    Args:
        image_bytes: nội dung file ảnh do frontend upload.

    Returns:
        ProcessedImage chứa kích thước gốc, ảnh đã chuẩn hoá và hash file.

    Raises:
        InvalidImageError: nếu file rỗng hoặc OpenCV không decode được.
    """
    started = time.perf_counter()
    logger.debug("Bắt đầu xử lý ảnh, nhận %d bytes", len(image_bytes))

    if not image_bytes:
        logger.warning("File ảnh rỗng (0 byte)")
        raise InvalidImageError("Empty image file")

    # bytes -> numpy array 1 chiều -> ảnh BGR
    buffer = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)

    # imdecode trả None nếu dữ liệu không phải ảnh hợp lệ
    if image is None:
        logger.warning(
            "cv2.imdecode() trả None -> không phải ảnh hợp lệ (%d bytes)", len(image_bytes)
        )
        raise InvalidImageError("Invalid image file")

    height, width = image.shape[:2]
    logger.info("Đọc ảnh OK: %dx%d, %.1f KB", width, height, len(image_bytes) / 1024)

    # Resize nếu ảnh quá lớn, giữ nguyên tỉ lệ
    if max(width, height) > MAX_SIZE:
        scale = MAX_SIZE / max(width, height)
        new_size = (int(width * scale), int(height * scale))
        image = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
        logger.info("Ảnh quá lớn -> resize về %dx%d", new_size[0], new_size[1])
    else:
        logger.debug("Ảnh không cần resize (cạnh lớn nhất <= %d)", MAX_SIZE)

    image_sha1 = sha1_of(image_bytes)
    logger.debug(
        "Xử lý ảnh xong trong %.1fms | sha1=%s",
        (time.perf_counter() - started) * 1000,
        image_sha1[:12],
    )

    # width/height trả về là kích thước ảnh GỐC frontend gửi lên
    return ProcessedImage(width=width, height=height, image=image, sha1=image_sha1)
