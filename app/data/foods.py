"""Mock food database.

Chỉ là dict trong bộ nhớ - không dùng database, không dùng ORM.

Muốn thêm món mới:
  1. Thêm một entry vào FOODS bên dưới (key = food_id).
  2. Bỏ ảnh mẫu của món đó vào app/data/sample_images/<food_id>.jpg
     -> quét đúng ảnh đó sẽ ra đúng món này.
"""

from typing import Any, Dict

# key = food_id
FOODS: Dict[str, Dict[str, Any]] = {
    "mi_quang": {
        "id": "mi_quang",
        "name": "Mì Quảng",
        "calories": 370,
        "protein": 30,
        "carbs": 11,
        "fat": 16,
        "health_score": 75,
        "meal_type": "Bữa sáng",
        "category": "Mỳ",
        "description": (
            "Mì Quảng sợi vàng ăn kèm thịt gà, tôm, rau sống và đậu phộng rang, "
            "chan ít nước dùng đậm vị."
        ),
        "warning": (
            "HEALTH AI khuyên bạn nên chạy bộ 20p để tiêu hao năng lượng "
            "sau khi ăn món ăn này"
        ),
        "macros": [
            {
                "key": "protein",
                "label": "Đạm (Protein)",
                "value": 30,
                "unit": "g",
                "percent": 85,
                "note": "85% mục tiêu bữa trưa",
            },
            {
                "key": "carbs",
                "label": "Tinh bột (Carbs)",
                "value": 11,
                "unit": "g",
                "percent": 35,
                "note": "Thấp so với trung bình",
            },
            {
                "key": "fat",
                "label": "Chất béo (Fat)",
                "value": 16,
                "unit": "g",
                "percent": 50,
                "note": "Chất béo không bão hoà tốt",
            },
        ],
        "analysis": [
            "Bữa này cân đối về đạm nhưng tổng năng lượng ở mức khá cao cho bữa sáng.",
            "Phần đậu phộng và nước dùng là nguồn chất béo chính, "
            "nên ăn vừa phải nếu bạn đang kiểm soát cân nặng.",
        ],
        "advice": (
            "– Hãy hạn chế ăn những đồ ăn có nhiều đạm như hải sản vì gần đây bạn "
            "đang gặp vấn đề về gout chân, đồ ăn nhiều đạm sẽ làm triệu chứng của bạn "
            "chuyển biến nghiêm trọng hơn.\n"
            "– Tiếp theo, lời khuyên chân thành nhất cho bạn, hãy chạy bộ 20p cho tối nay "
            "để tiêu hao bớt lượng năng lượng bạn đã nạp trong ngày."
        ),
        "ingredients": [
            {"name": "Mì Quảng sợi (150g)", "calories": 210},
            {"name": "Thịt gà & tôm (80g)", "calories": 120},
            {"name": "Rau sống & đậu phộng", "calories": 40},
        ],
    },
    "pho_bo_tai_nam": {
        "id": "pho_bo_tai_nam",
        "name": "Phở bò tái nạm (Hương vị Hà Nội)",
        "calories": 310,
        "protein": 20,
        "carbs": 11,
        "fat": 16,
        "health_score": 75,
        "meal_type": "Bữa sáng",
        "category": "Mỳ",
        "description": (
            "Phở bò Hà Nội với bánh phở, thịt bò tái và nạm, "
            "nước dùng ninh xương, hành lá và rau thơm."
        ),
        "warning": "Món ăn này là thịt tái nên có nồng độ LDL cholesterol cao",
        "macros": [
            {
                "key": "protein",
                "label": "Đạm (Protein)",
                "value": 20,
                "unit": "g",
                "percent": 85,
                "note": "85% mục tiêu bữa trưa",
            },
            {
                "key": "carbs",
                "label": "Tinh bột (Carbs)",
                "value": 11,
                "unit": "g",
                "percent": 35,
                "note": "Thấp so với trung bình",
            },
            {
                "key": "fat",
                "label": "Chất béo (Fat)",
                "value": 16,
                "unit": "g",
                "percent": 50,
                "note": "Chất béo không bão hoà tốt",
            },
        ],
        "analysis": [
            "Bữa sáng này đạt điểm 7.5/10 — protein rất tốt, nhưng lượng natri hơi cao.",
            "Hai điều chỉnh nhỏ cho lần sau:\n"
            "• Chừa lại khoảng 1/3 bánh phở → giảm ~90 kcal mà vẫn no, vì phần protein "
            "từ thịt bò mới là thứ giữ bạn no đến trưa.\n"
            "• Xin thêm một đĩa rau sống và vắt chanh thay vì thêm nước mắm → "
            "tăng chất xơ, không tăng natri.",
            "Hôm nay nhớ uống thêm 500ml nước so với bình thường "
            "để cân bằng lượng muối này nhé.",
            "Cộng lại: 1.020 kcal cho cả ngày.",
        ],
        "advice": (
            "Hãy hạn chế ăn những đồ ăn có nhiều thịt đỏ như thế này vì nó sẽ gia tăng "
            "nồng độ cholesterol gây ra tình trạng tim mạch về sau này."
        ),
        "ingredients": [
            {"name": "Bánh phở (150g)", "calories": 190},
            {"name": "Thịt bò tái & nạm (70g)", "calories": 95},
            {"name": "Nước dùng, hành & rau thơm", "calories": 25},
        ],
    },
    "com_ga": {
        "id": "com_ga",
        "name": "Cơm gà",
        "calories": 520,
        "protein": 32,
        "carbs": 58,
        "fat": 16,
        "health_score": 70,
        "meal_type": "Bữa trưa",
        "category": "Cơm",
        "description": "Cơm nấu với nước luộc gà, ăn kèm thịt gà xé và rau sống.",
        "warning": "Khẩu phần cơm khá lớn, nên ăn kèm nhiều rau để cân bằng đường huyết.",
        "macros": [
            {
                "key": "protein",
                "label": "Đạm (Protein)",
                "value": 32,
                "unit": "g",
                "percent": 90,
                "note": "90% mục tiêu bữa trưa",
            },
            {
                "key": "carbs",
                "label": "Tinh bột (Carbs)",
                "value": 58,
                "unit": "g",
                "percent": 80,
                "note": "Cao so với trung bình",
            },
            {
                "key": "fat",
                "label": "Chất béo (Fat)",
                "value": 16,
                "unit": "g",
                "percent": 50,
                "note": "Ở mức vừa phải",
            },
        ],
        "analysis": [
            "Lượng đạm tốt cho bữa trưa, nhưng tinh bột chiếm phần lớn năng lượng.",
            "Nếu buổi chiều ít vận động, bạn có thể chừa lại 1/3 phần cơm.",
        ],
        "advice": "Ăn rau trước, cơm sau để giảm tốc độ tăng đường huyết.",
        "ingredients": [
            {"name": "Cơm (200g)", "calories": 260},
            {"name": "Thịt gà xé (120g)", "calories": 200},
            {"name": "Rau sống & nước chấm", "calories": 60},
        ],
    },
    "hamburger": {
        "id": "hamburger",
        "name": "Hamburger",
        "calories": 550,
        "protein": 25,
        "carbs": 45,
        "fat": 30,
        "health_score": 55,
        "meal_type": "Bữa trưa",
        "category": "Đồ ăn nhanh",
        "description": "Bánh mì kẹp thịt bò xay, phô mai, rau xà lách và sốt.",
        "warning": "Món ăn nhiều chất béo bão hoà, không nên ăn quá 1 lần/tuần.",
        "macros": [
            {
                "key": "protein",
                "label": "Đạm (Protein)",
                "value": 25,
                "unit": "g",
                "percent": 70,
                "note": "70% mục tiêu bữa trưa",
            },
            {
                "key": "carbs",
                "label": "Tinh bột (Carbs)",
                "value": 45,
                "unit": "g",
                "percent": 65,
                "note": "Ở mức trung bình",
            },
            {
                "key": "fat",
                "label": "Chất béo (Fat)",
                "value": 30,
                "unit": "g",
                "percent": 90,
                "note": "Cao - chủ yếu là chất béo bão hoà",
            },
        ],
        "analysis": [
            "Chất béo chiếm gần một nửa tổng năng lượng của món này.",
            "Nếu đã ăn món này, buổi tối nên chọn bữa nhẹ nhiều rau.",
        ],
        "advice": "Bỏ bớt sốt và phô mai có thể giảm khoảng 120 kcal.",
        "ingredients": [
            {"name": "Bánh mì burger", "calories": 150},
            {"name": "Thịt bò xay (110g)", "calories": 280},
            {"name": "Phô mai & sốt", "calories": 120},
        ],
    },
    "pizza": {
        "id": "pizza",
        "name": "Pizza",
        "calories": 285,
        "protein": 12,
        "carbs": 36,
        "fat": 10,
        "health_score": 60,
        "meal_type": "Bữa tối",
        "category": "Đồ ăn nhanh",
        "description": "Một miếng pizza đế mỏng với phô mai và sốt cà chua.",
        "warning": "Lượng natri trong phô mai và sốt khá cao.",
        "macros": [
            {
                "key": "protein",
                "label": "Đạm (Protein)",
                "value": 12,
                "unit": "g",
                "percent": 35,
                "note": "Thấp so với mục tiêu bữa tối",
            },
            {
                "key": "carbs",
                "label": "Tinh bột (Carbs)",
                "value": 36,
                "unit": "g",
                "percent": 55,
                "note": "Ở mức trung bình",
            },
            {
                "key": "fat",
                "label": "Chất béo (Fat)",
                "value": 10,
                "unit": "g",
                "percent": 40,
                "note": "Ở mức vừa phải",
            },
        ],
        "analysis": [
            "Số liệu tính cho 1 miếng - ăn 3 miếng là đã gần 900 kcal.",
            "Đạm thấp nên bạn sẽ nhanh đói lại.",
        ],
        "advice": "Ăn kèm một phần salad để tăng chất xơ và no lâu hơn.",
        "ingredients": [
            {"name": "Đế bánh", "calories": 130},
            {"name": "Phô mai (40g)", "calories": 110},
            {"name": "Sốt cà chua & topping", "calories": 45},
        ],
    },
}
