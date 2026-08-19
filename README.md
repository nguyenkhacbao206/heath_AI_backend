# Food Scanner API (Demo Backend)

Backend demo cho ứng dụng **Food Scanner**: frontend chụp/quét ảnh món ăn, gửi lên backend,
backend đọc ảnh bằng **OpenCV** và trả về thông tin dinh dưỡng dưới dạng JSON.

> ⚠️ Đây là bản **demo**: không dùng AI/ML, không database, không authentication.
> Phần nhận diện món ăn là **mock logic**, OpenCV chỉ dùng để đọc/kiểm tra/resize ảnh.

## Tech stack

- Python 3.11+
- FastAPI + Uvicorn
- OpenCV (`opencv-python`) + NumPy
- Pydantic (schemas)
- Mock data lưu trong Python (không database, không ORM)

## Cấu trúc project

```text
.
├── app/
│   ├── main.py                  # FastAPI app, CORS, include router
│   ├── api/
│   │   ├── router.py            # gom route dưới prefix /api
│   │   └── routes/
│   │       ├── health.py        # GET /api/health
│   │       └── food.py          # GET/POST các route /api/foods
│   ├── services/
│   │   ├── food_service.py      # business logic + mock_detect_food()
│   │   ├── opencv_service.py    # decode / validate / resize ảnh
│   │   └── sample_matcher.py    # so khớp ảnh upload với ảnh mẫu (hash + ORB)
│   ├── schemas/
│   │   └── food.py              # Food, Macro, Ingredient, ImageInfo, ScanResponse
│   └── data/
│       ├── foods.py             # mock data các món ăn
│       └── sample_images/       # <-- BỎ ẢNH MÓN ĂN VÀO ĐÂY
├── requirements.txt
├── .gitignore
└── README.md
```

## Cài đặt & chạy

### 1. Clone project

```bash
git clone <repo-url>
cd heath_AI_backend
```

### 2. Tạo virtual environment

```bash
python -m venv venv
```

### 3. Activate environment (Windows)

PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Command Prompt (cmd):

```cmd
venv\Scripts\activate.bat
```

Git Bash / macOS / Linux:

```bash
source venv/Scripts/activate     # Windows (Git Bash)
source venv/bin/activate         # macOS / Linux
```

> Nếu PowerShell báo lỗi execution policy:
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

### 4. Cài dependencies

```bash
pip install -r requirements.txt
```

### 5. Chạy server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server chạy tại: <http://127.0.0.1:8000>

### 6. Mở Swagger

<http://127.0.0.1:8000/docs>

Tại đây có thể test trực tiếp mọi API, kể cả upload ảnh cho `/api/foods/scan`.

## API

| Method | Endpoint                | Mô tả                          |
| ------ | ----------------------- | ------------------------------ |
| GET    | `/api/health`           | Health check                   |
| GET    | `/api/foods`            | Danh sách các món ăn           |
| GET    | `/api/foods/{food_id}`  | Chi tiết một món (404 nếu sai) |
| POST   | `/api/foods/scan`       | Upload ảnh → nutrition         |

`food_id` hợp lệ: `mi_quang`, `pho_bo_tai_nam`.

### 7. Test API `/api/foods`

```bash
curl http://127.0.0.1:8000/api/foods
```

Trả về mảng `foods`, mỗi phần tử là một object `Food` đầy đủ
(xem cấu trúc ở phần `/api/foods/scan` bên dưới).

Lấy một món:

```bash
curl http://127.0.0.1:8000/api/foods/pho_bo_tai_nam
```

### 8. Test API `/api/foods/scan`

Field name bắt buộc là `image`, gửi dạng `multipart/form-data`.

```bash
curl -X POST http://127.0.0.1:8000/api/foods/scan -F "image=@food.jpg"
```

```json
{
  "success": true,
  "matched_by": "features",
  "food": {
    "id": "pho_bo_tai_nam",
    "name": "Phở bò tái nạm (Hương vị Hà Nội)",
    "calories": 310,
    "protein": 20,
    "carbs": 11,
    "fat": 16,
    "health_score": 75,
    "meal_type": "Bữa sáng",
    "category": "Mỳ",
    "description": "Phở bò Hà Nội với bánh phở, thịt bò tái và nạm...",
    "warning": "Món ăn này là thịt tái nên có nồng độ LDL cholesterol cao",
    "image_url": "/static/foods/pho_bo_tai_nam.jpg",
    "macros": [
      { "key": "protein", "label": "Đạm (Protein)", "value": 20, "unit": "g",
        "percent": 85, "note": "85% mục tiêu bữa trưa" }
    ],
    "analysis": ["Bữa sáng này đạt điểm 7.5/10 — protein rất tốt..."],
    "advice": "Hãy hạn chế ăn những đồ ăn có nhiều thịt đỏ...",
    "ingredients": [
      { "name": "Bánh phở (150g)", "calories": 190 }
    ]
  },
  "image": {
    "width": 1280,
    "height": 720
  }
}
```

(`macros` có đủ 3 phần tử, `analysis` / `ingredients` rút gọn cho ngắn.)

Gọi từ frontend React:

```js
const formData = new FormData();
formData.append("image", file); // file từ <input type="file"> hoặc camera

const res = await fetch("http://127.0.0.1:8000/api/foods/scan", {
  method: "POST",
  body: formData, // KHÔNG tự set Content-Type, browser tự thêm boundary
});
const data = await res.json();
```

## Error handling

| Trường hợp                    | HTTP | Response                                       |
| ----------------------------- | ---- | ---------------------------------------------- |
| Không gửi field `image`       | 422  | `{"detail": [...]}` (FastAPI validation)       |
| File không phải ảnh           | 400  | `{"detail": "Uploaded file is not an image"}`  |
| OpenCV không đọc được ảnh     | 400  | `{"detail": "Invalid image file"}`             |
| File rỗng                     | 400  | `{"detail": "Empty image file"}`               |
| `food_id` không tồn tại       | 404  | `{"detail": "Food 'xxx' not found"}`           |
| Lỗi không mong muốn           | 500  | `{"detail": "Internal server error"}`          |

## CORS

Đã mở sẵn cho frontend React (Vite):

- `http://localhost:5173`
- `http://127.0.0.1:5173`

Thêm origin khác trong `ALLOWED_ORIGINS` tại [app/main.py](app/main.py).

## Ảnh mẫu — làm sao quét ảnh X thì ra món X

Thả ảnh món ăn vào `app/data/sample_images/`, **đặt tên file trùng với `food_id`**:

```text
app/data/sample_images/
├── mi_quang.jpg          -> quét ảnh này ra món "mi_quang"
└── pho_bo_tai_nam.jpg    -> quét ảnh này ra món "pho_bo_tai_nam"
```

Không phải sửa code — thêm file là chạy. Nhớ **restart server** vì ảnh mẫu được
cache lúc khởi động. Định dạng hỗ trợ: `.jpg` `.jpeg` `.png` `.webp` `.bmp`

Khi scan, backend chọn món theo thứ tự:

| Thứ tự | Cách làm                                                  | `matched_by` |
| ------ | --------------------------------------------------------- | ------------ |
| 1      | Hash file trùng ảnh mẫu (upload đúng file đó)             | `exact`      |
| 2      | ORB feature matching — chụp lại ảnh mẫu vẫn nhận ra       | `features`   |
| 3      | Không khớp mẫu nào → chọn theo độ sáng ảnh                | `fallback`   |

Bước 2 dùng `cv2.ORB_create()` + `cv2.BFMatcher()` — thuật toán dò đặc trưng cổ
điển có sẵn trong OpenCV, **không phải AI, không có model, không training**. Nó
tìm các điểm góc đặc trưng rồi đếm xem 2 ảnh khớp nhau bao nhiêu điểm.

Đo thực tế trên 2 ảnh mẫu, ảnh đúng đạt **162–1000 điểm khớp** kể cả khi bị
resize, cắt còn 55%, xoay 20°, chụp xiên, chỉnh sáng ±35 hay lệch cân bằng trắng;
ảnh sai chỉ **2–10 điểm**, ảnh không liên quan **0–1 điểm**. Ngưỡng đang đặt 25.

> **Demo thế nào cho chắc:** cho camera chụp lại chính ảnh mẫu (in ra giấy hoặc
> mở trên màn hình khác) — vẫn nhận đúng. Hoặc upload thẳng file ảnh mẫu → luôn
> rơi vào nhánh `exact`.
>
> **Giới hạn:** chụp một tô phở *thật ngoài đời* (khác hoàn toàn ảnh mẫu) thì
> không nhận ra được — việc đó cần AI thật. Khi đó API trả `fallback`.

Thư mục để trống vẫn chạy bình thường (mọi ảnh sẽ ra `fallback`).

## Ảnh món ăn cho frontend

Ảnh trong `sample_images/` được serve tĩnh, và mọi response đều kèm `image_url`:

```json
{ "id": "mi_quang", "name": "Mì Quảng", "image_url": "/static/foods/mi_quang.jpg" }
```

Frontend ghép với base URL để hiển thị:

```js
<img src={`http://127.0.0.1:8000${food.image_url}`} />
```

`image_url` là `null` nếu món đó chưa có ảnh mẫu.

## Flow của `/api/foods/scan`

```text
POST /api/foods/scan  (multipart: image)
        ↓
food.py            → kiểm tra content-type, đọc bytes
        ↓
food_service.scan_food()
        ↓
opencv_service.process_image()   → decode, validate, width/height, resize, hash
        ↓
food_service.mock_detect_food()  → MOCK
        ↓
sample_matcher.match()           → hash + ORB, so với sample_images/
        ↓
food_service.get_food()          → nutrition từ FOODS
        ↓
ScanResponse (JSON)
```

## Thay mock detection bằng AI model

Chỉ cần sửa **một hàm duy nhất**: `mock_detect_food()` trong
[app/services/food_service.py](app/services/food_service.py).

Hàm nhận `ProcessedImage` (ảnh đã qua OpenCV) và trả về `(food_id, method)`.
Thay thân hàm bằng model inference thật, giữ nguyên chữ ký — route, schema và API
contract không đổi. Khi đó có thể xoá luôn `sample_matcher.py` và thư mục
`sample_images/`.

```python
def mock_detect_food(processed: ProcessedImage) -> tuple[str, str]:
    food_id = model.predict(processed.image)   # -> "pho_bo_tai_nam"
    return food_id, "model"
```
