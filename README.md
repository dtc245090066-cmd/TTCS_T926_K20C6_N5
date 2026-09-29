# LumiHotel — Quản lý khách sạn theo cấu trúc TTCS

Project này là bản **QLKS LumiHotel đã được sửa lại theo kiến trúc của project TTCS `ttcs-k20c6-n1`**.

## 1. Cấu trúc

```text
QLKS_LumiHotel_TTCS_Structure/
├── app.py
├── hotel_management.db
├── README.md
├── requirements.txt
├── backend/
│   ├── database.py
│   └── services.py
├── templates/
│   └── index.html
└── static/
    ├── app.js
    ├── css/
    │   └── style.css
    └── images/
        └── design-reference.png
```

Luồng xử lý:

```text
Browser
   ↓
templates/index.html + static/app.js
   ↓
app.py (Flask API)
   ↓
backend/services.py
   ↓
backend/database.py
   ↓
hotel_management.db (SQLite)
```

## 2. Những phần đã chuyển theo TTCS

- `app.py` chỉ điều phối route/API.
- `backend/database.py` chịu trách nhiệm SQLite, tạo bảng và dữ liệu mẫu.
- `backend/services.py` chứa nghiệp vụ:
  - `AuthService`: đăng nhập/đăng ký.
  - `RoomService`: CRUD phòng.
  - `BookingService`: tạo và xem đặt phòng.
  - `DashboardService`: tổng hợp số liệu dashboard.
- Session Flask giữ trạng thái đăng nhập.
- Mật khẩu được lưu bằng hash.
- Frontend gọi API thay vì giữ danh sách phòng/đặt phòng trong biến Python.

## 3. Chức năng hiện có

- Đăng nhập / đăng xuất.
- Đăng ký tài khoản nhân viên.
- Dashboard.
- SQLite thật.
- Quản lý phòng: thêm, xem, cập nhật, xóa phòng trống.
- Lọc trạng thái phòng.
- Đặt phòng.
- Danh sách đặt phòng.
- Thống kê số phòng, phòng trống, phòng đang ở, buồng phòng, doanh thu.
- Giao diện LumiHotel nâu/kem/vàng, responsive.

## 4. Tài khoản demo

```text
Email:    admin@lumihotel.local
Mật khẩu: Hotel@123
```

## 5. Chạy trên Windows PowerShell

```powershell
cd "D:\QLKS_LumiHotel_TTCS_Structure"

python -m venv .venv

.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

python app.py
```

Mở:

```text
http://127.0.0.1:5000
```

## 6. Lưu ý

`hotel_management.db` được tự tạo/cập nhật khi chạy lần đầu. Không cần cài MySQL.

Project được thiết kế để tiếp tục mở rộng theo cùng kiến trúc:
`CustomerService`, `InvoiceService`, `ServiceService`, `CheckInService`, `CheckOutService`.
