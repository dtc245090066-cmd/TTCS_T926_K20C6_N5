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

### Khôi phục mật khẩu qua email

Đăng ký không yêu cầu email xác minh. Chức năng **Quên mật khẩu** sử dụng liên kết một lần, hết hạn sau 15 phút; chức năng **Đổi mật khẩu** trong hồ sơ vẫn yêu cầu đăng nhập và mật khẩu hiện tại.

Thêm các biến sau vào `.env` (xem `.env.example`), giữ nguyên các cấu hình khác:

```dotenv
APP_BASE_URL=http://127.0.0.1:5000
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=dia-chi-gui@example.com
SMTP_PASSWORD=mat-khau-ung-dung-cua-nha-cung-cap-email
```

SMTP dùng STARTTLS. Khi triển khai, đặt `APP_BASE_URL` thành địa chỉ HTTPS thực tế mà người nhận email có thể truy cập. Không đưa mật khẩu SMTP thật vào Git. Nếu thiếu cấu hình hoặc gửi email thất bại, giao diện vẫn trả thông báo chung để không tiết lộ tài khoản tồn tại.

Mỗi email được gửi tối đa 5 yêu cầu/giờ; mỗi IP tối đa 20 yêu cầu gửi và 30 lần kiểm tra/đặt lại mỗi giờ. Giới hạn lưu trong SQLite và vẫn có hiệu lực sau khi khởi động lại. Hệ thống dùng IP kết nối trực tiếp; nếu triển khai sau reverse proxy, cần cấu hình proxy tin cậy trước khi dùng IP người dùng để giới hạn.

Kiểm thử tự động (SMTP được giả lập, không gửi email thật):

```powershell
python -m unittest discover -s tests -p test_password_reset.py -v
python -m unittest discover -s tests -p test_registration.py -v
python -m unittest discover -s tests -p test_profile_update.py -v
```

Kiểm thử thực tế: chạy `python app.py`, chọn **Quên mật khẩu**, nhập email tài khoản, mở liên kết trong email, nhập và xác nhận mật khẩu mới, sau đó đăng nhập lại. Liên kết đã sử dụng hoặc quá 15 phút phải bị từ chối. Hai bảng phụ `password_resets` và `password_reset_limits` được tạo tự động khi khởi động; không xóa dữ liệu tài khoản hiện có.

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

## 14. Kiểm tra biểu đồ thu nhập

Chạy `python -m pip install -r requirements.txt`, sau đó `python app.py` và mở địa chỉ Flask in trong terminal. Đăng nhập rồi vào **Thống kê thu nhập**.

- Biểu đồ nằm dưới bảng 12 tháng, dùng chung dữ liệu từ `/api/revenue-statistics?year=...` với bảng và tổng năm.
- Giữ nguyên cách tính của `DashboardService.get_monthly_revenue`: cộng `bookings.total` theo tháng `check_out`, với trạng thái `booked`, `checked_in`, `checked_out`.
- Đổi năm và đối chiếu bảng với tooltip; tháng không có doanh thu bằng 0. Năm trống có thông báo riêng.
- Thử màn hình rộng và điện thoại; nhấn **Xuất PDF** để kiểm tra báo cáo có biểu đồ.
- Chart.js đang được tải qua CDN nên cần mạng; nếu không tải được thư viện, bảng và xuất PDF vẫn sử dụng được.

Kiểm thử tự động (dữ liệu kiểm thử nằm trong cơ sở dữ liệu tạm, không sửa dữ liệu khách sạn):

```powershell
python -m unittest discover -s tests -p test_revenue_statistics.py
node --check static/js/app.js
node tests/test_revenue_chart.cjs
```

Kiểm thử JavaScript kiểm tra dữ liệu, định dạng tiền, nhãn responsive, vòng đời biểu đồ, phản hồi đến sai thứ tự và dữ liệu lỗi. Cần kiểm tra trực tiếp trên trình duyệt để xác nhận bố cục và thao tác tải PDF.

## 15. Lịch sử đặt phòng từ biểu đồ doanh thu

- Đăng nhập bằng tài khoản `manager` hoặc `staff`, chọn năm ở **Thống kê thu nhập**, rồi bấm cột hoặc liên kết tên tháng. Ví dụ tháng 11 năm 2026 mở `/booking-history?year=2026&month=11`.
- Lịch sử lọc theo **ngày trả phòng**, cùng điều kiện ngày với báo cáo. Danh sách gồm cả đơn hủy; thẻ doanh thu chỉ cộng trạng thái `booked`, `checked_in`, `checked_out`, giống biểu đồ. Thẻ tổng giá trị đơn gồm cả đơn hủy và được ghi rõ riêng. Các thẻ tổng quan tính cả tháng, không đổi theo tìm kiếm/lọc danh sách.
- Tìm theo mã đơn, tên khách (không phân biệt hoa thường tiếng Việt) hoặc số điện thoại; lọc trạng thái và xem từng trang 20 đơn. Danh sách sắp xếp ngày trả phòng giảm dần, rồi ID giảm dần.
- **Xem chi tiết** mở modal thông tin thật. Dữ liệu liên hệ và loại phòng lấy từ bản ghi khách hàng/phòng hiện có, không phải bản chụp lịch sử. Số đêm là chênh lệch ngày, không dùng để tính lại tổng tiền đã lưu.
- Chưa có trường thanh toán, giá phòng tại lúc đặt, số khách, dịch vụ, giảm giá hay lịch sử trạng thái trong cơ sở dữ liệu: hiển thị `—`, không suy đoán. Bộ lọc thanh toán chỉ hỗ trợ “Tất cả” / “Chưa có dữ liệu”. Không suy ra đã thanh toán từ trạng thái đã trả phòng.
- Nút quay lại khôi phục năm thống kê. Liên kết tên tháng trong bảng dùng được với bàn phím và tháng doanh thu bằng 0.

Route/API mới:

| Đường dẫn | Chức năng |
| --- | --- |
| `GET /booking-history` | Trang lịch sử, không chứa sẵn thông tin khách hàng |
| `GET /api/booking-history?year=2026&month=11` | Tổng quan tháng và danh sách; hỗ trợ `search`, `status`, `payment`, `page` |
| `GET /api/booking-history/<id>` | Chi tiết đơn |

Hai API kiểm tra tài khoản còn tồn tại và có vai trò `manager` hoặc `staff` trong cơ sở dữ liệu ở mỗi yêu cầu, thống nhất với chức năng xem đặt phòng của nhân viên. API trả 401 khi chưa đăng nhập, 403 khi không đủ quyền, và không cho cache dữ liệu. Quyền của các chức năng cũ được giữ nguyên. Các trường lọc sai trả 400; chi tiết không tồn tại trả 404.

```powershell
python -m unittest discover -s tests -p test_booking_history.py
python -m unittest discover -s tests -p test_revenue_statistics.py
node tests/test_revenue_chart.cjs
node tests/test_booking_history.cjs
```

Kiểm tra thủ công: chọn năm 2026 → tháng 11 → đối chiếu tổng tháng → tìm tên/mã → lọc trạng thái → mở chi tiết → quay lại đúng năm. Thử tháng trống, tài khoản `staff`, màn hình điện thoại (bảng cuộn ngang) và xuất PDF thống kê. Chức năng PDF thống kê hiện có được giữ nguyên; modal chi tiết chưa thêm xuất PDF riêng.
