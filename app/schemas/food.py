"""Pydantic schemas cho food & scan API."""

from pydantic import BaseModel, Field


class Macro(BaseModel):
    """Một dòng macro trong UI (đạm / tinh bột / chất béo)."""

    key: str = Field(..., examples=["protein"])
    label: str = Field(..., examples=["Đạm (Protein)"])
    value: int = Field(..., description="số gram")
    unit: str = "g"
    percent: int = Field(..., ge=0, le=100, description="% để vẽ thanh progress")
    note: str = Field(..., examples=["85% mục tiêu bữa trưa"])


class Ingredient(BaseModel):
    """Một dòng trong khối 'Chi tiết thành phần'."""

    name: str = Field(..., examples=["Bánh phở (150g)"])
    calories: int


class Food(BaseModel):
    """Thông tin đầy đủ của một món ăn (mock data)."""

    # --- các field cơ bản (giữ nguyên contract ban đầu) ---
    id: str = Field(..., examples=["pho_bo_tai_nam"])
    name: str = Field(..., examples=["Phở bò tái nạm (Hương vị Hà Nội)"])
    calories: int = Field(..., description="kcal / khẩu phần")
    protein: int = Field(..., description="gram")
    carbs: int = Field(..., description="gram")
    fat: int = Field(..., description="gram")

    # --- các field phục vụ UI card kết quả ---
    health_score: int = Field(..., ge=0, le=100, description="Điểm sức khoẻ")
    meal_type: str = Field(..., examples=["Bữa sáng"])
    category: str = Field(..., examples=["Mỳ"])
    description: str
    warning: str = Field(..., description="Cảnh báo hiển thị ở dòng chữ đỏ")
    image_url: str | None = Field(
        None,
        description="Đường dẫn ảnh món ăn (None nếu chưa có ảnh mẫu)",
        examples=["/static/foods/pho_bo_tai_nam.jpg"],
    )
    macros: list[Macro] = Field(..., description="Chi tiết macro kèm % và ghi chú")
    analysis: list[str] = Field(..., description="Các đoạn của khối 'Phân tích'")
    advice: str = Field(..., description="Nội dung mục 'Lời khuyên'")
    ingredients: list[Ingredient]


class FoodListResponse(BaseModel):
    """Response cho GET /api/foods."""

    foods: list[Food]


class ImageInfo(BaseModel):
    """Kích thước ảnh gốc do frontend gửi lên."""

    width: int
    height: int


class ScanResponse(BaseModel):
    """Response cho POST /api/foods/scan."""

    success: bool = True
    food: Food
    image: ImageInfo
    matched_by: str = Field(
        ...,
        description="Cách chọn ra món: 'exact' (trùng ảnh mẫu), 'histogram' (giống ảnh mẫu), 'fallback' (không khớp mẫu nào)",
        examples=["exact"],
    )
