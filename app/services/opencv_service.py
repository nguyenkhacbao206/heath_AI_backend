"""OpenCV service.

Nhiệm vụ của file này CHỈ là xử lý ảnh cơ bản:
  - decode bytes -> ảnh
  - kiểm tra ảnh hợp lệ
  - lấy width / height
  - resize nếu ảnh quá lớn
  - hash nội dung file (để so khớp ảnh mẫu)

KHÔNG có nhận diện món ăn ở đây. OpenCV không phải AI model.
"""

from dataclasses import dataclass

import cv2
import numpy as np

from app.services.sample_matcher import sha1_of

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
    if not image_bytes:
        raise InvalidImageError("Empty image file")

    # bytes -> numpy array 1 chiều -> ảnh BGR
    buffer = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)

    # imdecode trả None nếu dữ liệu không phải ảnh hợp lệ
    if image is None:
        raise InvalidImageError("Invalid image file")

    height, width = image.shape[:2]

    # Resize nếu ảnh quá lớn, giữ nguyên tỉ lệ
    if max(width, height) > MAX_SIZE:
        scale = MAX_SIZE / max(width, height)
        new_size = (int(width * scale), int(height * scale))
        image = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)

    # width/height trả về là kích thước ảnh GỐC frontend gửi lên
    return ProcessedImage(
        width=width,
        height=height,
        image=image,
        sha1=sha1_of(image_bytes),
    )
