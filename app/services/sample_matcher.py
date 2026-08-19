"""So khớp ảnh upload với các ảnh mẫu trong app/data/sample_images/.

Đây KHÔNG phải AI, không có model, không training. Chỉ là 2 kỹ thuật OpenCV cơ bản:
  1. So sánh hash của file  -> upload đúng file mẫu thì chắc chắn ra đúng món.
  2. ORB feature matching   -> CHỤP LẠI ảnh mẫu (bằng camera, khác góc, khác
     ánh sáng, bị cắt cúp) vẫn nhận ra được.

ORB là thuật toán dò đặc trưng cổ điển có sẵn trong OpenCV: nó tìm các điểm góc
đặc trưng trên ảnh rồi đếm xem 2 ảnh có bao nhiêu điểm khớp nhau.

Quy ước: TÊN FILE (bỏ phần đuôi) chính là food_id.
    app/data/sample_images/mi_quang.jpg        -> "mi_quang"
    app/data/sample_images/pho_bo_tai_nam.jpg  -> "pho_bo_tai_nam"

Thêm ảnh mẫu mới chỉ cần copy file vào thư mục, không phải sửa code.
"""

import hashlib
import logging
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# app/data/sample_images/
SAMPLE_DIR: Path = Path(__file__).resolve().parent.parent / "data" / "sample_images"

SUPPORTED_SUFFIXES: set[str] = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

# Ảnh được thu nhỏ về cạnh này trước khi dò đặc trưng (cho nhanh và ổn định)
WORK_SIZE: int = 640

# Số đặc trưng ORB tối đa lấy trên mỗi ảnh
ORB_FEATURES: int = 1000

# Tỉ lệ của Lowe's ratio test - lọc các cặp khớp không chắc chắn
RATIO_TEST: float = 0.75

# Số điểm khớp tối thiểu để coi là cùng một ảnh.
# Đo thực tế trên 2 ảnh mẫu: ảnh đúng đạt 162-1000 điểm kể cả khi bị crop 55%,
# xoay 20°, chụp xiên hay lệch cân bằng trắng; ảnh sai chỉ 2-10 điểm.
MIN_GOOD_MATCHES: int = 25


@dataclass
class Sample:
    """Một ảnh mẫu đã được nạp sẵn vào bộ nhớ."""

    food_id: str
    filename: str
    sha1: str
    descriptors: np.ndarray | None


# Cache: chỉ đọc thư mục ảnh mẫu một lần
_samples: list[Sample] | None = None


def sha1_of(data: bytes) -> str:
    """Hash nội dung file để so khớp tuyệt đối."""
    return hashlib.sha1(data).hexdigest()


def describe(image: np.ndarray) -> np.ndarray | None:
    """Dò các điểm đặc trưng ORB của ảnh.

    Trả None nếu ảnh quá trơn (tường trắng, ảnh mờ tịt...) - không có gì để dò.
    """
    height, width = image.shape[:2]
    scale = WORK_SIZE / max(height, width)
    if scale < 1:
        image = cv2.resize(
            image, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_AREA
        )

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Tạo mới mỗi lần gọi cho an toàn khi FastAPI chạy nhiều request song song
    orb = cv2.ORB_create(nfeatures=ORB_FEATURES)
    _, descriptors = orb.detectAndCompute(gray, None)
    return descriptors


def count_good_matches(query: np.ndarray | None, reference: np.ndarray | None) -> int:
    """Đếm số điểm đặc trưng khớp chắc chắn giữa 2 ảnh."""
    if query is None or reference is None or len(query) < 2 or len(reference) < 2:
        return 0

    matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
    good = 0
    for pair in matcher.knnMatch(query, reference, k=2):
        # Lowe's ratio test: chỉ nhận khi điểm khớp tốt nhất vượt trội điểm thứ nhì
        if len(pair) == 2 and pair[0].distance < RATIO_TEST * pair[1].distance:
            good += 1
    return good


def load_samples(force_reload: bool = False) -> list[Sample]:
    """Nạp toàn bộ ảnh mẫu trong SAMPLE_DIR (có cache).

    Thư mục rỗng hoặc không tồn tại là hợp lệ - khi đó scan sẽ dùng fallback.
    """
    global _samples
    if _samples is not None and not force_reload:
        return _samples

    samples: list[Sample] = []
    if SAMPLE_DIR.is_dir():
        for path in sorted(SAMPLE_DIR.iterdir()):
            if path.suffix.lower() not in SUPPORTED_SUFFIXES:
                continue

            data = path.read_bytes()
            image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
            if image is None:
                logger.warning("Bỏ qua ảnh mẫu không đọc được: %s", path.name)
                continue

            descriptors = describe(image)
            n_features = 0 if descriptors is None else len(descriptors)
            logger.info(
                "  + ảnh mẫu '%s' <- %s (%dx%d, %d đặc trưng)",
                path.stem,
                path.name,
                image.shape[1],
                image.shape[0],
                n_features,
            )
            if n_features < MIN_GOOD_MATCHES:
                logger.warning(
                    "    ảnh mẫu '%s' quá ít đặc trưng (%d) -> khó nhận dạng",
                    path.stem,
                    n_features,
                )

            samples.append(
                Sample(
                    food_id=path.stem,  # tên file = food_id
                    filename=path.name,
                    sha1=sha1_of(data),
                    descriptors=descriptors,
                )
            )

    logger.info(
        "Đã nạp %d ảnh mẫu: %s", len(samples), [s.food_id for s in samples] or "(trống)"
    )
    _samples = samples
    return _samples


def image_filename(food_id: str) -> str | None:
    """Tên file ảnh mẫu của một món, dùng để dựng image_url."""
    for sample in load_samples():
        if sample.food_id == food_id:
            return sample.filename
    return None


def match(image: np.ndarray, image_sha1: str) -> tuple[str, str] | None:
    """Tìm món ăn tương ứng với ảnh upload.

    Args:
        image: ảnh BGR đã qua OpenCV.
        image_sha1: hash của file gốc frontend gửi lên.

    Returns:
        (food_id, method) với method là "exact" hoặc "features",
        hoặc None nếu không ảnh mẫu nào đủ giống.
    """
    samples = load_samples()
    if not samples:
        logger.warning("Không có ảnh mẫu nào để so khớp")
        return None

    # 1) Trùng file tuyệt đối - nhanh, không cần xử lý ảnh
    logger.debug("So hash: ảnh gửi lên sha1=%s", image_sha1[:12])
    for sample in samples:
        if sample.sha1 == image_sha1:
            logger.info("KHỚP TUYỆT ĐỐI: trùng hash với ảnh mẫu '%s'", sample.food_id)
            return sample.food_id, "exact"
    logger.debug("Không trùng hash ảnh mẫu nào -> chuyển sang so đặc trưng ORB")

    # 2) So khớp đặc trưng ORB, lấy ảnh mẫu có nhiều điểm khớp nhất
    started = time.perf_counter()
    descriptors = describe(image)
    if descriptors is None:
        logger.warning("Ảnh gửi lên không dò được đặc trưng nào (quá trơn/mờ?)")
        return None
    logger.debug("Ảnh gửi lên có %d đặc trưng ORB", len(descriptors))

    best_id: str | None = None
    best_score = 0
    for sample in samples:
        score = count_good_matches(descriptors, sample.descriptors)
        logger.info("  so với '%s': %d điểm khớp", sample.food_id, score)
        if score > best_score:
            best_score, best_id = score, sample.food_id

    logger.info(
        "Gần nhất: '%s' với %d điểm khớp (cần >= %d) | mất %.0fms",
        best_id,
        best_score,
        MIN_GOOD_MATCHES,
        (time.perf_counter() - started) * 1000,
    )

    if best_id is not None and best_score >= MIN_GOOD_MATCHES:
        return best_id, "features"

    logger.warning(
        "Không ảnh mẫu nào đạt ngưỡng %d điểm -> ảnh này không giống mẫu nào",
        MIN_GOOD_MATCHES,
    )
    return None
