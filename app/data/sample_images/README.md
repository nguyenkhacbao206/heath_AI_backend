# Ảnh mẫu (sample images)

Bỏ ảnh món ăn vào đây để khi scan đúng/gần đúng ảnh đó, API trả về đúng món.

**Quy ước: tên file (bỏ đuôi) = `food_id` trong `app/data/foods.py`.**

```text
app/data/sample_images/
├── mi_quang.jpg          -> trả về món "mi_quang"
└── pho_bo_tai_nam.jpg    -> trả về món "pho_bo_tai_nam"
```

Định dạng hỗ trợ: `.jpg` `.jpeg` `.png` `.webp` `.bmp`

Thêm/đổi ảnh xong nhớ **restart server** (ảnh mẫu được cache lúc chạy lần đầu).
Thư mục để trống cũng không sao — khi đó scan sẽ dùng fallback.
