# LumiHotel — Hệ thống quản lý khách sạn

## 1. Giới thiệu

**LumiHotel** là hệ thống quản lý khách sạn được xây dựng nhằm hỗ trợ nhân viên và quản trị viên thực hiện các nghiệp vụ quản lý phòng, đặt phòng, tài khoản và theo dõi tình trạng hoạt động của khách sạn.

Hệ thống sử dụng **Python Flask** cho backend, **SQLite** để lưu trữ dữ liệu và **HTML/CSS/JavaScript** cho giao diện người dùng.

---

## 2. Công nghệ sử dụng

- Python
- Flask
- SQLite
- HTML5
- CSS3
- JavaScript
- Jinja2
- Flask Session
- Werkzeug Password Hashing

---

## 3. Cấu trúc dự án

```text
LumiHotel/
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

### Chức năng của từng thành phần

**`app.py`**

File chạy chính của hệ thống, chịu trách nhiệm:

- Khởi tạo Flask.
- Cấu hình Session.
- Điều hướng trang.
- Xây dựng các API.
- Nhận yêu cầu từ giao diện.
- Gọi các service xử lý nghiệp vụ.

**`backend/database.py`**

Quản lý cơ sở dữ liệu SQLite:

- Kết nối cơ sở dữ liệu.
- Tạo bảng.
- Khởi tạo dữ liệu.
- Thực thi truy vấn.
- Đóng kết nối sau khi xử lý.

**`backend/services.py`**

Chứa các nghiệp vụ chính của hệ thống.

Các service hiện có:

- `AuthService`: quản lý đăng nhập và đăng ký tài khoản.
- `RoomService`: quản lý thông tin phòng.
- `BookingService`: quản lý đặt phòng.
- `DashboardService`: thống kê dữ liệu tổng quan.

**`templates/index.html`**

Giao diện chính của hệ thống LumiHotel.

**`static/app.js`**

Xử lý các thao tác phía người dùng và giao tiếp với Flask API.

**`static/css/style.css`**

Quản lý toàn bộ giao diện, màu sắc, bố cục và khả năng responsive.

**`hotel_management.db`**

Cơ sở dữ liệu SQLite của hệ thống.

---

## 4. Kiến trúc hoạt động

```text
Người dùng
    ↓
Trình duyệt
    ↓
HTML + CSS + JavaScript
    ↓
Flask API - app.py
    ↓
Business Services
    ↓
Database Layer
    ↓
SQLite Database
```

Khi người dùng thực hiện một thao tác trên giao diện, JavaScript gửi yêu cầu đến Flask API.

Flask tiếp nhận yêu cầu và chuyển dữ liệu đến lớp Service để xử lý nghiệp vụ.

Sau đó Service làm việc với lớp Database để đọc hoặc cập nhật dữ liệu trong SQLite.

Kết quả được trả lại cho giao diện và hiển thị cho người dùng.

---

## 5. Chức năng hệ thống

### 5.1. Quản lý tài khoản

Hệ thống hỗ trợ:

- Đăng nhập.
- Đăng xuất.
- Đăng ký tài khoản nhân viên.
- Lưu trạng thái đăng nhập bằng Flask Session.
- Mã hóa mật khẩu trước khi lưu vào cơ sở dữ liệu.

---

## 5.2. Dashboard

Dashboard giúp người dùng nhanh chóng theo dõi hoạt động của khách sạn.

Thông tin hiển thị gồm:

- Tổng số phòng.
- Số phòng trống.
- Số phòng đang có khách.
- Tình trạng buồng phòng.
- Số lượt đặt phòng.
- Doanh thu.

---

## 5.3. Quản lý phòng

Hệ thống cho phép:

- Thêm phòng mới.
- Xem danh sách phòng.
- Cập nhật thông tin phòng.
- Xóa phòng.
- Xem trạng thái phòng.
- Lọc phòng theo trạng thái.

Một số trạng thái phòng:

```text
Trống
Đã đặt
Đang ở
Đang vệ sinh
Bảo trì
```

Phòng chỉ được phép xóa khi không có khách đang sử dụng hoặc không tồn tại đặt phòng liên quan.

---

## 5.4. Quản lý đặt phòng

Hệ thống hỗ trợ:

- Tạo đặt phòng.
- Chọn phòng.
- Nhập thông tin khách hàng.
- Chọn ngày nhận phòng.
- Chọn ngày trả phòng.
- Xem danh sách đặt phòng.
- Theo dõi trạng thái đặt phòng.

---

## 5.5. Thống kê

Hệ thống tổng hợp một số thông tin quan trọng phục vụ quản lý:

- Tổng số phòng.
- Phòng đang sử dụng.
- Phòng còn trống.
- Số lượt đặt phòng.
- Tỷ lệ sử dụng phòng.
- Doanh thu khách sạn.

---

## 6. Giao diện

LumiHotel sử dụng phong cách giao diện khách sạn hiện đại với các màu chủ đạo:

- Nâu.
- Kem.
- Vàng.
- Trắng.

Thiết kế tập trung vào:

- Giao diện trực quan.
- Dễ thao tác.
- Phù hợp với nghiệp vụ quản lý khách sạn.
- Hiển thị tốt trên nhiều kích thước màn hình.
- Responsive cho máy tính và thiết bị di động.

---

## 7. Tài khoản quản trị mặc định

```text
Email: admin@lumihotel.local
Mật khẩu: Hotel2026@
```

Tài khoản này dùng để đăng nhập và kiểm tra hệ thống trong quá trình phát triển.

Khi triển khai thực tế nên thay đổi mật khẩu mặc định.

---

## 8. Hướng dẫn cài đặt 
### Bước 2: Tạo môi trường Python
```
python -m venv .venv
```
### Bước 3: Kích hoạt môi trường
```
.\.venv\Scripts\Activate.ps1
```
### Bước 4: Cài thư viện
```
pip install -r requirements.txt
```
### Bước 5: Chạy hệ thống
```
python app.py
```
Nếu chạy thành công, hệ thống sẽ khởi động tại:

```text
http://127.0.0.1:5000
```

Mở trình duyệt và truy cập địa chỉ trên để sử dụng LumiHotel.

---

## 9. Cơ sở dữ liệu

LumiHotel sử dụng:

```text
SQLite
```

File cơ sở dữ liệu:

```text
hotel_management.db
```

Cơ sở dữ liệu được khởi tạo tự động khi chạy hệ thống lần đầu.

Không cần cài đặt MySQL Server hoặc cấu hình một máy chủ cơ sở dữ liệu riêng.

---

## 10. Bảo mật

Hệ thống áp dụng một số biện pháp bảo mật cơ bản:

- Mật khẩu không lưu dưới dạng văn bản thuần.
- Mật khẩu được hash trước khi lưu.
- Session được sử dụng để xác định người dùng đang đăng nhập.
- Các API quan trọng yêu cầu người dùng phải đăng nhập.
- Backend kiểm tra dữ liệu trước khi cập nhật cơ sở dữ liệu.

---

## 11. Hướng phát triển

LumiHotel có thể tiếp tục mở rộng thêm các module:

```text
CustomerService
InvoiceService
HotelService
CheckInService
CheckOutService
PaymentService
EmployeeService
ReportService
```

Các chức năng dự kiến:

- Quản lý khách hàng.
- Check-in.
- Check-out.
- Quản lý dịch vụ khách sạn.
- Quản lý hóa đơn.
- Thanh toán.
- Quản lý nhân viên.
- Báo cáo doanh thu.
- Thống kê công suất phòng.
- Quản lý loại phòng.
- Phân quyền tài khoản.
- Xuất hóa đơn PDF.
- Tích hợp chatbot AI hỗ trợ nhân viên.

---

## 12. Mục tiêu của LumiHotel

LumiHotel hướng đến xây dựng một hệ thống quản lý khách sạn:

- Dễ sử dụng.
- Dễ bảo trì.
- Có cấu trúc rõ ràng.
- Có thể mở rộng.
- Quản lý dữ liệu tập trung.
- Hỗ trợ nhân viên thực hiện nghiệp vụ nhanh chóng.
- Giảm các thao tác quản lý thủ công.

---

## 13. Tác giả

**Dự án:** LumiHotel — Hệ thống quản lý khách sạn

**Mục đích:** Xây dựng hệ thống quản lý khách sạn bằng Flask và SQLite.  