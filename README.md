Hệ thống quản lý phòng cho thuê

Ứng dụng hỗ trợ quản lý tài khoản, phòng và thể loại phòng; theo dõi quá trình cho thuê, trả phòng; tổng hợp doanh thu và xuất báo cáo PDF. Tài liệu này mô tả yêu cầu chức năng được cung cấp cho dự án, không khẳng định các chức năng đã hoàn tất trong mã nguồn.

Mục lục

Tổng quan

Chức năng

Quy trình sử dụng

Quy tắc nghiệp vụ

Danh sách yêu cầu

Tiêu chí nghiệm thu

Cài đặt và chạy dự án

Tổng quan

Hệ thống dành cho người dùng có tài khoản quản lý phòng cho thuê. Sau khi đăng nhập, người dùng xem danh sách phòng trên trang chủ, cập nhật phòng và thể loại phòng, thực hiện cho thuê/trả phòng, xem thống kê doanh thu theo năm.

Phạm vi tài liệu: 19 yêu cầu trong bảng đặc tả được cung cấp. Tài liệu gốc chưa nêu công nghệ, cấu trúc mã nguồn, tên ứng dụng chính thức, cách triển khai hoặc tiến độ thực hiện.

Chức năng

1. Tài khoản và hồ sơ

Đăng nhập bằng email và mật khẩu; thông báo khi thông tin đăng nhập không đúng.

Chỉ cho phép vào trang chủ sau khi đăng nhập; duy trì phiên đăng nhập bằng session.

Đăng xuất khỏi hệ thống.

Đổi mật khẩu: nhập mật khẩu mới, xác nhận và kiểm tra dữ liệu trước khi lưu.

Cập nhật họ tên, ngày sinh, số điện thoại và ảnh đại diện; email không được chỉnh sửa.

2. Phòng cho thuê

Xem danh sách phòng dạng lưới trên trang chủ. Mỗi phòng hiển thị mã phòng, trạng thái, giờ vào và giờ ra khi có dữ liệu tương ứng.

Thêm hoặc cập nhật phòng với các thông tin: mã phòng, mô tả ngắn, hình ảnh, thể loại phòng, giá thuê và trạng thái.

Tải ảnh lên khi thêm hoặc sửa phòng; kiểm tra dữ liệu bắt buộc trước khi lưu.

Xóa phòng sau khi xác nhận; chặn xóa phòng đang được thuê.

Hiển thị số lượng phòng theo trạng thái và lọc danh sách khi chọn một trạng thái.

Phân biệt trạng thái trực quan: phòng trống màu xanh, phòng đã cho thuê màu đỏ.

3. Cho thuê và trả phòng

Từ danh sách phòng, chọn Cho thuê để xem thông tin phòng và nhập thời điểm trả dự kiến.

Tự lấy thời điểm bắt đầu thuê từ thời gian hệ thống, tính thời lượng thuê và số tiền dự kiến theo giá phòng.

Kiểm tra dữ liệu trước khi lưu, sau đó quay lại danh sách phòng.

Chỉ hiển thị thao tác Trả phòng với phòng đang được thuê; sau khi trả, trạng thái phòng chuyển về phòng trống.

4. Thể loại phòng

Xem danh sách, thêm, sửa và xóa thể loại phòng.

Các thể loại được nêu trong yêu cầu: phòng đơn, phòng đôi và phòng VIP.

5. Thống kê thu nhập

Xem bảng doanh thu gồm 12 tháng của năm hiện tại, với hai cột Tháng và Tổng tiền, cùng tổng cả năm.

Chọn năm khác để xem doanh thu theo từng tháng của năm đó.

Xuất bảng thống kê đang xem thành tệp PDF.

Quy trình sử dụng

Đăng nhập bằng tài khoản hợp lệ để truy cập trang chủ.

Tạo các thể loại phòng và thêm phòng với thông tin, ảnh và giá thuê.

Theo dõi trạng thái phòng, lọc để tìm phòng trống và thực hiện cho thuê.

Kiểm tra thời gian và số tiền dự kiến trước khi lưu lượt thuê.

Khi kết thúc lượt thuê, thao tác trả phòng để phòng trở lại trạng thái trống.

Mở mục thống kê, chọn năm cần xem và xuất PDF khi cần báo cáo.

Quy tắc nghiệp vụ

Mã

Quy tắc

BR-01

Người dùng phải đăng nhập trước khi truy cập trang chủ và các chức năng quản lý.

BR-02

Phòng mới mặc định ở trạng thái trống.

BR-03

Không được xóa phòng đang cho thuê.

BR-04

Chỉ phòng đang cho thuê mới có thao tác Trả phòng.

BR-05

Email trong hồ sơ cá nhân không được chỉnh sửa.

BR-06

Thời điểm bắt đầu thuê được lấy từ thời gian hệ thống khi lập lượt thuê.

BR-07

Thời lượng thuê và tiền thuê được tính từ thời điểm bắt đầu, thời điểm trả đã chọn và giá phòng; đơn vị thời gian tính giá phải được thống nhất trong triển khai.

BR-08

Các biểu mẫu thêm, sửa, cho thuê và đổi mật khẩu phải kiểm tra dữ liệu trước khi lưu.

Cần chốt trước khi lập trình: giá thuê tính theo giờ, ngày hay đơn vị khác; cách làm tròn thời lượng; thời điểm ghi nhận doanh thu; cách xử lý lịch sử thuê khi xóa phòng/thể loại phòng. Bảng yêu cầu gốc chưa quy định các chi tiết này.

Danh sách yêu cầu

ID

Nhóm

Yêu cầu

US-01

Tài khoản

Đăng nhập

US-02

Tài khoản

Đăng xuất

US-03

Phòng

Thêm phòng

US-04

Phòng

Xóa phòng

US-05

Phòng

Xem danh sách phòng

US-06

Phòng

Cập nhật phòng

US-07

Thuê phòng

Cho thuê phòng

US-08

Thuê phòng

Trả phòng

US-09

Tài khoản

Đổi mật khẩu

US-10

Tài khoản

Cập nhật thông tin cá nhân

US-11

Phòng

Xem số lượng phòng theo trạng thái

US-12

Phòng

Lọc phòng theo trạng thái

US-13

Báo cáo

Xem thu nhập 12 tháng của năm hiện tại

US-14

Báo cáo

Xem thu nhập theo năm được chọn

US-15

Báo cáo

Xuất thống kê thu nhập ra PDF

US-16

Thể loại phòng

Xem danh sách thể loại

US-17

Thể loại phòng

Thêm thể loại

US-18

Thể loại phòng

Cập nhật thể loại

US-19

Thể loại phòng

Xóa thể loại

Tiêu chí nghiệm thu

Đăng nhập đúng đưa người dùng vào hệ thống; đăng nhập sai hiển thị lỗi; sau đăng xuất không còn truy cập được trang yêu cầu xác thực.

Phòng mới có trạng thái trống; ảnh được tải lên và hiển thị; biểu mẫu từ chối dữ liệu không hợp lệ.

Xóa phòng đang cho thuê bị chặn; xóa phòng đủ điều kiện cần xác nhận và có thông báo kết quả.

Danh sách phòng thể hiện đúng mã, trạng thái và thời gian liên quan; bộ lọc và số lượng theo trạng thái khớp với dữ liệu.

Lượt thuê lấy đúng giờ bắt đầu, tính thời lượng và số tiền theo quy tắc đã thống nhất; trả phòng cập nhật trạng thái về trống.

Báo cáo có đủ 12 tháng, tổng năm chính xác; đổi năm cập nhật số liệu; PDF chứa bảng đang xem.

Hồ sơ cho phép sửa các trường được phép, không cho sửa email; đổi mật khẩu kiểm tra xác nhận.

Danh sách và các thao tác thêm, sửa, xóa thể loại phòng hoạt động theo quy tắc dữ liệu đã thống nhất.

Cài đặt và chạy dự án

Tài liệu đầu vào chỉ có danh sách yêu cầu, chưa có mã nguồn hoặc thông tin về ngôn ngữ lập trình, framework, cơ sở dữ liệu và biến môi trường. Vì vậy chưa thể cung cấp lệnh cài đặt/chạy chính xác. Khi đưa README này vào repository, hãy bổ sung:

Yêu cầu môi trường và phiên bản công cụ.

Lệnh tải mã nguồn và cài đặt thư viện.

Cách cấu hình biến môi trường và cơ sở dữ liệu; cung cấp tệp cấu hình mẫu, không đưa mật khẩu thật vào repository.

Lệnh khởi tạo dữ liệu, chạy ứng dụng và chạy kiểm thử (nếu có).

Địa chỉ truy cập, cách tạo tài khoản ban đầu và hình ảnh giao diện thực tế.

README được biên soạn từ bảng 19 user story được cung cấp; cần cập nhật theo mã nguồn và các quyết định nghiệp vụ chính thức của dự án.
