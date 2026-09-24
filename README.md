# 🏨 HỆ THỐNG QUẢN LÝ KHÁCH SẠN

## 📌 Giới thiệu

**Hệ thống Quản lý Khách sạn** là ứng dụng hỗ trợ nhân viên và quản lý khách sạn thực hiện các nghiệp vụ quản lý phòng, cho thuê – trả phòng, theo dõi trạng thái phòng, quản lý khách hàng và thống kê doanh thu.

Dự án được phát triển theo phương pháp **Agile/Scrum**, sử dụng **Product Backlog**, User Story, Story Point và chia chức năng theo từng Sprint để thuận tiện cho quá trình phát triển, kiểm thử và nghiệm thu.

---

## 🎯 Mục tiêu dự án

Hệ thống được xây dựng nhằm:

* Số hóa quy trình quản lý phòng khách sạn.
* Giảm thao tác thủ công trong quá trình cho thuê và trả phòng.
* Theo dõi nhanh trạng thái phòng theo thời gian thực.
* Quản lý thông tin khách thuê và lịch sử thuê phòng.
* Tự động tính tiền thuê phòng.
* Hỗ trợ quản lý theo dõi doanh thu theo tháng và năm.
* Phân quyền chức năng phù hợp với từng loại người dùng.
* Đảm bảo dữ liệu được quản lý tập trung, chính xác và dễ tra cứu.

---

## 👥 Người dùng hệ thống

Hệ thống gồm hai nhóm người dùng chính:

### Quản lý

Có quyền quản lý toàn bộ hệ thống, bao gồm:

* Quản lý phòng.
* Theo dõi hoạt động thuê phòng.
* Quản lý tài khoản nhân viên.
* Xem lịch sử thuê.
* Xem thống kê doanh thu.
* Xuất báo cáo.

### Lễ tân / Nhân viên khách sạn

Thực hiện các nghiệp vụ hằng ngày như:

* Đăng nhập hệ thống.
* Xem sơ đồ phòng.
* Kiểm tra trạng thái phòng.
* Cho khách thuê phòng.
* Trả phòng.
* Tra cứu thông tin khách hàng.
* Xem lịch sử thuê theo quyền được cấp.

---

## ⚙️ Chức năng chính

### 🔐 1. Xác thực và tài khoản

* Đăng nhập bằng email và mật khẩu.
* Đăng xuất khỏi hệ thống.
* Quản lý phiên đăng nhập.
* Đổi mật khẩu.
* Cập nhật thông tin cá nhân.
* Phân quyền Quản lý và Lễ tân.
* Quản lý tài khoản nhân viên.
* Hỗ trợ quên mật khẩu qua email trong phiên bản mở rộng.

### 🛏️ 2. Quản lý phòng

* Thêm phòng mới.
* Cập nhật thông tin phòng.
* Xóa hoặc xóa mềm phòng.
* Quản lý mã phòng, loại phòng và giá thuê.
* Các loại phòng gồm:

  * Phòng Đơn.
  * Phòng Đôi.
  * Phòng VIP.
* Tìm kiếm phòng theo mã phòng, loại phòng hoặc mức giá.

### 🟢 3. Sơ đồ và trạng thái phòng

Trang chủ hiển thị các phòng dưới dạng lưới để nhân viên dễ dàng theo dõi.

Phòng được chia thành hai trạng thái chính:

* **Phòng trống**
* **Đã cho thuê**

Hệ thống đồng thời hiển thị:

* Tổng số phòng.
* Số phòng đang trống.
* Số phòng đang được thuê.
* Bộ lọc phòng theo trạng thái.

### 📝 4. Thuê và trả phòng

Hệ thống hỗ trợ toàn bộ quy trình thuê phòng:

**Cho thuê phòng → Ghi nhận khách hàng → Ghi nhận thời gian thuê → Trả phòng → Tính tiền → Cập nhật trạng thái phòng**

Thông tin phiếu thuê bao gồm:

* Mã phòng.
* Họ tên khách hàng.
* Số điện thoại.
* CMND/CCCD.
* Giờ nhận phòng.
* Giờ trả dự kiến.
* Giờ trả thực tế.
* Giá thuê tại thời điểm thuê.
* Số giờ thuê.
* Thành tiền.
* Trạng thái phiếu thuê.

Ngoài ra, hệ thống có thể mở rộng:

* Gia hạn thời gian thuê.
* Hủy phiếu thuê.
* In hóa đơn PDF.
* Xem lịch sử thuê phòng.

### 💰 5. Thống kê và báo cáo

Quản lý có thể:

* Xem doanh thu theo từng tháng.
* Chọn năm cần thống kê.
* Xem tổng doanh thu trong năm.
* Xuất báo cáo doanh thu ra PDF.
* Xem biểu đồ doanh thu theo tháng.

Doanh thu chỉ được ghi nhận đối với các phiếu thuê đã hoàn tất trả phòng.

### 👤 6. Quản lý khách hàng

Hỗ trợ tra cứu khách hàng thông qua:

* Số điện thoại.
* CMND/CCCD.

Thông tin tra cứu có thể bao gồm:

* Họ tên khách.
* Thông tin liên hệ.
* Số lần thuê phòng.
* Danh sách và lịch sử các lần thuê.

---

## 📋 Một số quy tắc nghiệp vụ

* Mỗi phòng có một **mã phòng duy nhất**.
* Mã phòng không được thay đổi sau khi tạo.
* Phòng mới mặc định ở trạng thái **Phòng trống**.
* Phòng đang được thuê không thể cho thuê thêm cho khách khác.
* Phòng đang cho thuê không được xóa.
* Giờ nhận phòng được lấy tự động theo thời gian của hệ thống.
* Giá thuê tại thời điểm tạo phiếu được lưu lại và không bị ảnh hưởng khi giá phòng thay đổi sau đó.
* Thời gian thuê được tính theo giờ và làm tròn lên.
* Thành tiền được tính theo công thức:

```text
Thành tiền = Số giờ thuê × Giá thuê tại thời điểm thuê
```

* Doanh thu chỉ được ghi nhận khi phiếu thuê có trạng thái **Đã trả**.
* Email tài khoản đăng nhập phải là duy nhất.
* Mật khẩu được lưu dưới dạng mã hóa/băm, không lưu mật khẩu dạng văn bản thuần.

---

## 🗂️ Các nhóm chức năng của dự án

Dự án được chia thành các Epic chính:

| Epic | Nội dung               |
| ---- | ---------------------- |
| E01  | Xác thực & Tài khoản   |
| E02  | Quản lý phòng          |
| E03  | Sơ đồ & Theo dõi phòng |
| E04  | Thuê & Trả phòng       |
| E05  | Thống kê & Báo cáo     |
| E06  | Khách hàng             |
| E07  | Nền tảng kỹ thuật      |

---

## 🚀 Kế hoạch phát triển

Dự án được triển khai theo nhiều Sprint.

### Sprint 1

* Thiết lập môi trường phát triển.
* Thiết kế cơ sở dữ liệu.
* Tạo dữ liệu mẫu.
* Đăng nhập.
* Đăng xuất.
* Hiển thị sơ đồ phòng.
* Thêm phòng mới.

### Sprint 2

* Cho thuê phòng.
* Trả phòng.
* Cập nhật phòng.
* Xóa phòng.
* Hiển thị thống kê trạng thái phòng.

### Sprint 3

* Lọc phòng theo trạng thái.
* Thống kê doanh thu.
* Chọn năm thống kê.
* Đổi mật khẩu.
* Cập nhật thông tin cá nhân.
* Xem lịch sử thuê.

### Sprint 4

* Xuất báo cáo PDF.
* Phân quyền người dùng.
* Rà soát bảo mật.
* Kiểm thử tích hợp.
* Nghiệm thu và triển khai hệ thống.

---

## 🔒 Bảo mật

Hệ thống hướng tới các yêu cầu bảo mật cơ bản:

* Mật khẩu được băm trước khi lưu vào cơ sở dữ liệu.
* Kiểm tra quyền trước khi truy cập chức năng.
* Quản lý trạng thái đăng nhập bằng session.
* Sử dụng truy vấn có tham số để hạn chế SQL Injection.
* Kiểm tra và xác thực dữ liệu đầu vào.
* Hạn chế người dùng truy cập các chức năng không thuộc quyền của mình.

---

## 📌 Phạm vi phiên bản hiện tại

Phiên bản đầu tập trung vào các nghiệp vụ cốt lõi:

**Đăng nhập → Quản lý phòng → Theo dõi trạng thái phòng → Cho thuê → Trả phòng → Lịch sử thuê → Thống kê doanh thu.**

Một số chức năng nâng cao như **đặt phòng trước**, quản lý khách hàng chuyên sâu hoặc các tính năng mở rộng khác sẽ được xem xét trong những phiên bản tiếp theo.

---

## 👨‍💻 Phát triển dự án

Dự án được quản lý mã nguồn bằng **Git/GitHub** và áp dụng quy trình làm việc theo nhánh:

```text
main
develop
feature/*
```

Mỗi chức năng được phát triển trên một nhánh riêng trước khi kiểm thử và tích hợp vào nhánh chính.

---

## 📄 Tài liệu dự án

Các tài liệu chính của dự án bao gồm:

* Product Backlog.
* Sprint Plan.
* Quy trình nghiệp vụ.
* Từ điển dữ liệu.
* Quy tắc nghiệp vụ.
* Thiết kế cơ sở dữ liệu / ERD.
* Tài liệu kiểm thử.
* Hướng dẫn sử dụng và triển khai.

---

## 📜 License

Dự án được xây dựng phục vụ mục đích **học tập và thực hành phát triển phần mềm**.
