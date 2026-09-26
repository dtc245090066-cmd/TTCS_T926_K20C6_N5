# Hệ thống quản lý phòng cho thuê

Ứng dụng hỗ trợ quản lý tài khoản, phòng và thể loại phòng; theo dõi quá trình cho thuê, trả phòng; tổng hợp doanh thu và xuất báo cáo PDF.

> Tài liệu này mô tả yêu cầu chức năng được cung cấp cho dự án, không khẳng định các chức năng đã hoàn tất trong mã nguồn.

---

## Mục lục

- [Tổng quan](#tổng-quan)
- [Chức năng](#chức-năng)
- [Quy trình sử dụng](#quy-trình-sử-dụng)
- [Quy tắc nghiệp vụ](#quy-tắc-nghiệp-vụ)
- [Danh sách yêu cầu](#danh-sách-yêu-cầu)
- [Tiêu chí nghiệm thu](#tiêu-chí-nghiệm-thu)
- [Cài đặt và chạy dự án](#cài-đặt-và-chạy-dự-án)

---

## Tổng quan

Hệ thống dành cho người dùng có tài khoản để quản lý hoạt động cho thuê phòng.

Sau khi đăng nhập, người dùng có thể:

- Xem danh sách phòng trên trang chủ.
- Quản lý thông tin phòng.
- Quản lý thể loại phòng.
- Thực hiện cho thuê phòng.
- Thực hiện trả phòng.
- Theo dõi trạng thái phòng.
- Xem thống kê doanh thu theo năm.
- Xuất báo cáo doanh thu ra PDF.
- Quản lý thông tin tài khoản cá nhân.

### Phạm vi tài liệu

README hiện mô tả 19 yêu cầu chức năng trong bảng đặc tả được cung cấp.

Tài liệu gốc chưa nêu rõ:

- Công nghệ sử dụng.
- Framework.
- Cơ sở dữ liệu.
- Cấu trúc mã nguồn.
- Tên ứng dụng chính thức.
- Cách triển khai.
- Tiến độ thực hiện các chức năng.

---

## Chức năng

### 1. Tài khoản và hồ sơ

#### Đăng nhập

Người dùng đăng nhập bằng:

- Email.
- Mật khẩu.

Nếu thông tin đăng nhập không chính xác, hệ thống hiển thị thông báo lỗi.

#### Kiểm soát truy cập

Người dùng chỉ được phép truy cập trang chủ và các chức năng quản lý sau khi đăng nhập thành công.

Phiên đăng nhập được duy trì bằng session.

#### Đăng xuất

Người dùng có thể đăng xuất khỏi hệ thống.

Sau khi đăng xuất, phiên đăng nhập hiện tại phải được hủy.

#### Đổi mật khẩu

Người dùng có thể thay đổi mật khẩu của tài khoản.

Hệ thống yêu cầu:

- Nhập mật khẩu mới.
- Xác nhận mật khẩu mới.
- Kiểm tra dữ liệu trước khi lưu.

#### Cập nhật hồ sơ cá nhân

Người dùng có thể cập nhật:

- Họ và tên.
- Ngày sinh.
- Số điện thoại.
- Ảnh đại diện.

Email đăng nhập không được phép chỉnh sửa.

---

### 2. Phòng cho thuê

#### Xem danh sách phòng

Danh sách phòng được hiển thị dưới dạng lưới trên trang chủ.

Mỗi phòng có thể hiển thị:

- Mã phòng.
- Trạng thái.
- Giờ vào.
- Giờ ra.
- Hình ảnh.
- Giá thuê.
- Thể loại phòng.

#### Thêm phòng

Người dùng có thể thêm phòng mới với các thông tin:

| Thuộc tính | Mô tả |
|---|---|
| Mã phòng | Mã định danh của phòng |
| Mô tả | Mô tả ngắn về phòng |
| Hình ảnh | Ảnh đại diện của phòng |
| Thể loại phòng | Phòng đơn, phòng đôi, phòng VIP |
| Giá thuê | Giá cho thuê phòng |
| Trạng thái | Trạng thái hiện tại của phòng |

Phòng mới mặc định có trạng thái:

```text
Phòng trống
```

#### Cập nhật phòng

Người dùng có thể cập nhật thông tin của phòng.

Hệ thống phải kiểm tra các trường bắt buộc trước khi lưu.

#### Tải ảnh phòng

Khi thêm hoặc sửa phòng, người dùng có thể tải hình ảnh lên hệ thống.

Hệ thống cần kiểm tra dữ liệu trước khi lưu.

#### Xóa phòng

Người dùng có thể xóa phòng sau khi xác nhận.

Không cho phép xóa phòng đang được thuê.

#### Theo dõi trạng thái phòng

Hệ thống hiển thị số lượng phòng theo từng trạng thái.

| Trạng thái | Màu hiển thị |
|---|---|
| Phòng trống | Xanh |
| Đã cho thuê | Đỏ |

Người dùng có thể chọn trạng thái để lọc danh sách phòng.

---

### 3. Cho thuê và trả phòng

#### Cho thuê phòng

Từ danh sách phòng, người dùng chọn:

```text
Cho thuê
```

Hệ thống hiển thị thông tin phòng và cho phép nhập thời điểm trả dự kiến.

Thời điểm bắt đầu thuê được lấy tự động từ thời gian hệ thống.

```text
Thời gian bắt đầu thuê = Thời gian hiện tại của hệ thống
```

Hệ thống tính thời lượng thuê:

```text
Thời lượng thuê = Thời điểm trả dự kiến - Thời điểm bắt đầu
```

Số tiền dự kiến được tính dựa trên thời lượng thuê và giá phòng.

```text
Tiền thuê = Thời lượng thuê × Giá phòng
```

Trước khi lưu, hệ thống phải kiểm tra dữ liệu hợp lệ.

Sau khi lưu thành công, người dùng được chuyển về danh sách phòng.

#### Trả phòng

Chỉ phòng đang được thuê mới hiển thị chức năng:

```text
Trả phòng
```

Sau khi trả phòng:

- Lượt thuê được kết thúc.
- Trạng thái phòng được cập nhật.
- Phòng chuyển về trạng thái trống.
- Dữ liệu liên quan được sử dụng để tính doanh thu.

---

### 4. Thể loại phòng

Hệ thống hỗ trợ quản lý thể loại phòng.

Các chức năng bao gồm:

- Xem danh sách thể loại phòng.
- Thêm thể loại phòng.
- Cập nhật thể loại phòng.
- Xóa thể loại phòng.

Các thể loại phòng được nêu trong yêu cầu gồm:

- Phòng đơn.
- Phòng đôi.
- Phòng VIP.

---

### 5. Thống kê thu nhập

Hệ thống cung cấp chức năng thống kê doanh thu theo năm.

#### Thống kê năm hiện tại

Hệ thống hiển thị bảng doanh thu gồm 12 tháng.

| Tháng | Tổng tiền |
|---|---:|
| Tháng 1 | ... |
| Tháng 2 | ... |
| Tháng 3 | ... |
| ... | ... |
| Tháng 12 | ... |

Bên dưới bảng hiển thị tổng doanh thu của cả năm.

#### Thống kê theo năm

Người dùng có thể chọn một năm khác để xem doanh thu.

Khi thay đổi năm, hệ thống cập nhật doanh thu của 12 tháng tương ứng.

#### Xuất báo cáo PDF

Người dùng có thể xuất bảng thống kê doanh thu hiện tại thành tệp PDF.

Báo cáo cần phản ánh đúng:

- Năm đang được chọn.
- Doanh thu từng tháng.
- Tổng doanh thu của năm.

---

## Quy trình sử dụng

Quy trình sử dụng chính của hệ thống:

```text
Đăng nhập
    |
    v
Trang chủ
    |
    +--------------------+
    |                    |
    v                    v
Quản lý phòng      Quản lý thể loại
    |
    v
Chọn phòng trống
    |
    v
Cho thuê phòng
    |
    v
Nhập thời gian trả dự kiến
    |
    v
Tính thời lượng và tiền thuê
    |
    v
Lưu lượt thuê
    |
    v
Phòng chuyển sang trạng thái đã thuê
    |
    v
Trả phòng
    |
    v
Phòng chuyển về trạng thái trống
    |
    v
Cập nhật doanh thu
    |
    v
Thống kê / Xuất PDF
```

Quy trình tổng quát:

1. Đăng nhập bằng tài khoản hợp lệ để truy cập trang chủ.
2. Tạo các thể loại phòng cần thiết.
3. Thêm phòng với thông tin, hình ảnh và giá thuê.
4. Theo dõi trạng thái các phòng trên trang chủ.
5. Lọc danh sách để tìm phòng trống.
6. Chọn phòng và thực hiện cho thuê.
7. Kiểm tra thời gian thuê và số tiền dự kiến.
8. Lưu thông tin lượt thuê.
9. Khi khách kết thúc thời gian thuê, thực hiện trả phòng.
10. Phòng được chuyển về trạng thái trống.
11. Mở chức năng thống kê để xem doanh thu.
12. Chọn năm cần xem.
13. Xuất báo cáo PDF khi cần.

---

## Quy tắc nghiệp vụ

| Mã | Quy tắc |
|---|---|
| BR-01 | Người dùng phải đăng nhập trước khi truy cập trang chủ và các chức năng quản lý. |
| BR-02 | Phòng mới mặc định ở trạng thái trống. |
| BR-03 | Không được xóa phòng đang cho thuê. |
| BR-04 | Chỉ phòng đang cho thuê mới có thao tác Trả phòng. |
| BR-05 | Email trong hồ sơ cá nhân không được chỉnh sửa. |
| BR-06 | Thời điểm bắt đầu thuê được lấy từ thời gian hệ thống khi lập lượt thuê. |
| BR-07 | Thời lượng thuê và tiền thuê được tính từ thời điểm bắt đầu, thời điểm trả đã chọn và giá phòng. |
| BR-08 | Các biểu mẫu thêm, sửa, cho thuê và đổi mật khẩu phải kiểm tra dữ liệu trước khi lưu. |

### Các quy tắc cần thống nhất trước khi triển khai

Một số nội dung chưa được quy định rõ trong yêu cầu ban đầu:

- Giá thuê được tính theo giờ, ngày hay đơn vị khác.
- Cách làm tròn thời lượng thuê.
- Thời điểm ghi nhận doanh thu.
- Cách xử lý lịch sử thuê khi xóa phòng.
- Cách xử lý khi xóa thể loại phòng đang được sử dụng.
- Quy định định dạng và dung lượng ảnh tải lên.
- Quy định dữ liệu bắt buộc của từng biểu mẫu.

Các nội dung này cần được thống nhất trước khi triển khai chính thức.

---

## Danh sách yêu cầu

| ID | Nhóm | Yêu cầu |
|---|---|---|
| US-01 | Tài khoản | Đăng nhập |
| US-02 | Tài khoản | Đăng xuất |
| US-03 | Phòng | Thêm phòng |
| US-04 | Phòng | Xóa phòng |
| US-05 | Phòng | Xem danh sách phòng |
| US-06 | Phòng | Cập nhật phòng |
| US-07 | Thuê phòng | Cho thuê phòng |
| US-08 | Thuê phòng | Trả phòng |
| US-09 | Tài khoản | Đổi mật khẩu |
| US-10 | Tài khoản | Cập nhật thông tin cá nhân |
| US-11 | Phòng | Xem số lượng phòng theo trạng thái |
| US-12 | Phòng | Lọc phòng theo trạng thái |
| US-13 | Báo cáo | Xem thu nhập 12 tháng của năm hiện tại |
| US-14 | Báo cáo | Xem thu nhập theo năm được chọn |
| US-15 | Báo cáo | Xuất thống kê thu nhập ra PDF |
| US-16 | Thể loại phòng | Xem danh sách thể loại |
| US-17 | Thể loại phòng | Thêm thể loại |
| US-18 | Thể loại phòng | Cập nhật thể loại |
| US-19 | Thể loại phòng | Xóa thể loại |

---

## Tiêu chí nghiệm thu

### Tài khoản

- Đăng nhập đúng đưa người dùng vào hệ thống.
- Đăng nhập sai hiển thị thông báo lỗi.
- Người dùng chưa đăng nhập không được truy cập các trang yêu cầu xác thực.
- Sau khi đăng xuất, phiên đăng nhập phải được hủy.
- Đổi mật khẩu phải kiểm tra mật khẩu và xác nhận mật khẩu.
- Hồ sơ cá nhân chỉ cho phép sửa các trường được quy định.
- Email không được chỉnh sửa.

### Phòng

- Phòng mới có trạng thái trống.
- Hình ảnh tải lên thành công và hiển thị đúng.
- Biểu mẫu không cho lưu dữ liệu không hợp lệ.
- Không được xóa phòng đang cho thuê.
- Xóa phòng đủ điều kiện phải có bước xác nhận.
- Sau khi thêm, sửa hoặc xóa phải có thông báo kết quả.

### Danh sách và trạng thái phòng

- Danh sách phòng hiển thị đúng mã phòng.
- Hiển thị đúng trạng thái phòng.
- Hiển thị giờ vào và giờ ra khi có dữ liệu.
- Số lượng phòng theo trạng thái phải khớp với dữ liệu.
- Bộ lọc phải trả về đúng danh sách phòng theo trạng thái đã chọn.
- Phòng trống và phòng đang thuê được phân biệt trực quan.

### Cho thuê và trả phòng

- Chỉ phòng trống mới được thực hiện cho thuê.
- Thời gian bắt đầu thuê được lấy đúng từ hệ thống.
- Thời gian trả dự kiến phải hợp lệ.
- Thời lượng thuê được tính đúng theo quy tắc nghiệp vụ.
- Số tiền được tính đúng theo thời lượng và giá thuê.
- Sau khi cho thuê, trạng thái phòng được cập nhật.
- Chỉ phòng đang thuê mới có chức năng trả phòng.
- Sau khi trả phòng, trạng thái phòng chuyển về trống.

### Thống kê

- Báo cáo hiển thị đủ 12 tháng.
- Doanh thu từng tháng phải chính xác.
- Tổng doanh thu năm phải chính xác.
- Khi đổi năm, dữ liệu được cập nhật tương ứng.
- Tệp PDF chứa đúng bảng thống kê đang xem.

### Thể loại phòng

- Hiển thị đúng danh sách thể loại phòng.
- Thêm thể loại thành công khi dữ liệu hợp lệ.
- Cập nhật thể loại thành công.
- Xóa thể loại theo đúng các quy tắc dữ liệu đã thống nhất.

---

## Cài đặt và chạy dự án

Tài liệu đầu vào hiện mới cung cấp danh sách yêu cầu chức năng.

Chưa có thông tin đầy đủ về:

- Ngôn ngữ lập trình.
- Framework.
- Hệ quản trị cơ sở dữ liệu.
- Phiên bản môi trường.
- Biến môi trường.
- Cấu trúc thư mục.
- Lệnh khởi tạo cơ sở dữ liệu.
- Lệnh chạy ứng dụng.
- Lệnh chạy kiểm thử.

Do đó chưa thể cung cấp chính xác các lệnh cài đặt và chạy dự án.

Khi mã nguồn được đưa lên repository, phần này nên được bổ sung theo cấu trúc sau:

### Yêu cầu môi trường

```text
Ngôn ngữ:
Framework:
Database:
Phiên bản:
```

### Clone repository

```bash
git clone <repository-url>
cd <project-folder>
```

### Cài đặt thư viện

```bash
# Bổ sung lệnh cài đặt tương ứng với công nghệ của dự án.
```

### Cấu hình môi trường

Tạo tệp cấu hình môi trường từ tệp mẫu:

```text
.env.example
```

Không đưa mật khẩu, API key hoặc thông tin nhạy cảm thật lên GitHub.

### Khởi tạo cơ sở dữ liệu

```bash
# Bổ sung lệnh migration hoặc tạo database.
```

### Chạy ứng dụng

```bash
# Bổ sung lệnh chạy ứng dụng.
```

### Chạy kiểm thử

```bash
# Bổ sung lệnh chạy test nếu dự án có kiểm thử.
```

---

## Lưu ý

README được biên soạn dựa trên 19 User Story trong tài liệu yêu cầu được cung cấp.

Nội dung README cần tiếp tục được cập nhật khi:

- Công nghệ của dự án được xác định.
- Cấu trúc mã nguồn được hoàn thiện.
- Quy tắc nghiệp vụ được thống nhất.
- Các chức năng được triển khai thực tế.
- Có hướng dẫn cài đặt và triển khai chính thức.