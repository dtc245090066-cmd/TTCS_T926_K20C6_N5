HỆ THỐNG QUẢN LÝ KHÁCH SẠN / PHÒNG CHO THUÊ
1. Giới thiệu
Hệ thống Quản lý Khách sạn / Phòng cho thuê được xây dựng nhằm hỗ trợ người dùng quản lý phòng, quá trình cho thuê – trả phòng, thông tin cá nhân, thể loại phòng và doanh thu.
Tài liệu README.md này được xây dựng dựa trên Product Backlog của dự án TTCS_T926_K20C6. Nội dung mô tả phạm vi nghiệp vụ và các yêu cầu chức năng của hệ thống; không mặc định rằng toàn bộ chức năng đã được hoàn thành trong mã nguồn.
2. Mục tiêu dự án
Hệ thống hướng tới các mục tiêu chính:
- Quản lý danh sách phòng cho thuê.
- Theo dõi trạng thái phòng theo thời gian thực tế sử dụng.
- Thực hiện nghiệp vụ cho thuê và trả phòng.
- Quản lý thể loại phòng.
- Quản lý thông tin tài khoản cá nhân.
- Hỗ trợ đổi mật khẩu.
- Theo dõi số lượng phòng theo từng trạng thái.
- Lọc phòng theo trạng thái.
- Thống kê doanh thu theo tháng và theo năm.
- Xuất báo cáo doanh thu ra PDF.
3. Phạm vi chức năng
3.1. Quản lý tài khoản
Hệ thống hỗ trợ:
- Đăng nhập bằng email và mật khẩu.
- Đăng xuất khỏi hệ thống.
- Lưu trạng thái đăng nhập bằng session.
- Đổi mật khẩu.
- Cập nhật thông tin cá nhân.
- Upload ảnh đại diện.
3.2. Quản lý phòng
Người dùng có thể:
- Xem danh sách phòng.
- Thêm mới phòng.
- Cập nhật thông tin phòng.
- Xóa phòng.
- Theo dõi trạng thái phòng.
- Xem số lượng phòng theo trạng thái.
- Lọc danh sách phòng theo trạng thái.
Thông tin cơ bản của một phòng gồm:
- Mã phòng.
- Mô tả ngắn.
- Hình ảnh.
- Thể loại phòng.
- Giá thuê.
- Trạng thái phòng.
Các thể loại phòng được đề cập trong backlog:
- Phòng đơn.
- Phòng đôi.
- Phòng VIP.
3.3. Quản lý thuê và trả phòng
Hệ thống hỗ trợ:
- Cho thuê phòng đang trống.
- Ghi nhận thời gian bắt đầu thuê theo thời gian hệ thống.
- Chọn thời gian trả phòng.
- Tính thời gian thuê.
- Tính số tiền phải trả dựa trên thời gian thuê và giá phòng.
- Trả phòng.
- Chuyển trạng thái phòng về phòng trống sau khi trả.
3.4. Quản lý thể loại phòng
Người dùng có thể:
- Xem danh sách thể loại phòng.
- Thêm thể loại phòng.
- Cập nhật thể loại phòng.
- Xóa thể loại phòng.
3.5. Thống kê doanh thu
Hệ thống hỗ trợ:
- Xem doanh thu của năm hiện tại theo 12 tháng.
- Hiển thị tổng doanh thu của 12 tháng.
- Chọn năm cần xem.
- Xem doanh thu từng tháng của năm được chọn.
- Xuất bảng thống kê doanh thu sang PDF.
4. Quy trình sử dụng chính
4.1. Đăng nhập
Người dùng
    ↓
Nhập email và mật khẩu
    ↓
Hệ thống kiểm tra thông tin
    ↓
Đúng ─────────────→ Tạo session → Vào trang chủ
    ↓
Sai
    ↓
Thông báo sai tài khoản hoặc mật khẩu
4.2. Thêm phòng
Quản lý phòng
    ↓
Chọn Thêm mới
    ↓
Nhập thông tin phòng
    ↓
Upload hình ảnh
    ↓
Chọn thể loại phòng
    ↓
Kiểm tra dữ liệu
    ↓
Lưu phòng
4.3. Cho thuê phòng
Danh sách phòng
    ↓
Chọn phòng trống
    ↓
Chọn Cho thuê
    ↓
Hiển thị thông tin phòng
    ↓
Ghi nhận giờ bắt đầu thuê
    ↓
Chọn thời gian trả
    ↓
Tính thời gian thuê và số tiền
    ↓
Lưu
    ↓
Cập nhật trạng thái phòng thành Đã cho thuê
4.4. Trả phòng
Danh sách phòng
    ↓
Chọn phòng đang được thuê
    ↓
Chọn Trả phòng
    ↓
Hoàn tất nghiệp vụ
    ↓
Cập nhật trạng thái phòng thành Phòng trống
4.5. Thống kê doanh thu
Menu Thống kê thu nhập
    ↓
Chọn năm
    ↓
Hệ thống tổng hợp doanh thu theo 12 tháng
    ↓
Hiển thị bảng thống kê
    ↓
Hiển thị tổng doanh thu
    ↓
Có thể Export PDF
5. Quy tắc nghiệp vụ
BR-01 — Xác thực người dùng
Người dùng phải đăng nhập thành công trước khi truy cập trang chủ và các chức năng của hệ thống.
BR-02 — Lưu trạng thái đăng nhập
Sau khi đăng nhập thành công, hệ thống sử dụng session để lưu trạng thái đăng nhập và thông tin người dùng.
BR-03 — Trạng thái phòng mặc định
Khi thêm mới một phòng, trạng thái mặc định của phòng là Phòng trống.
BR-04 — Không xóa phòng đang cho thuê
Phòng có trạng thái Đã cho thuê không được phép xóa.
BR-05 — Màu hiển thị trạng thái
Theo backlog:
- Phòng trống: nền màu xanh.
- Phòng đã có người thuê: nền màu đỏ.
BR-06 — Cho thuê phòng
Chức năng Cho thuê được thực hiện từ danh sách phòng và áp dụng cho phòng có thể cho thuê.
BR-07 — Thời gian bắt đầu thuê
Khi cho thuê phòng, hệ thống tự động sử dụng thời gian hiện tại của hệ thống làm thời gian bắt đầu thuê.
BR-08 — Tính tiền thuê
Theo backlog:
Tiền phải trả = Thời gian thuê × Giá phòng
Đơn vị tính cụ thể của thời gian thuê và giá phòng cần được thống nhất trong quá trình thiết kế/triển khai.
BR-09 — Trả phòng
Chỉ phòng đang được thuê mới hiển thị hoặc cho phép thực hiện chức năng Trả phòng.
BR-10 — Sau khi trả phòng
Khi hoàn tất trả phòng, trạng thái phòng được cập nhật thành Phòng trống.
BR-11 — Email cá nhân
Email được hiển thị trong thông tin cá nhân nhưng không được phép cập nhật.
BR-12 — Thống kê doanh thu
Doanh thu được thống kê theo từng tháng trong năm và gồm đủ 12 tháng.
6. Product Backlog
ID	User Story / Feature	Priority	Sprint	Story Point
1	Đăng nhập bằng tài khoản đã tạo	High	1	3
2	Đăng xuất khỏi hệ thống	High	1	1
3	Thêm mới phòng cho thuê	High	1	5
4	Xóa phòng	High	1	3
5	Xem danh sách phòng	High	1	3
6	Cập nhật thông tin phòng	High	1	5
7	Cho thuê phòng	High	Chưa phân Sprint	Chưa ước lượng
8	Trả phòng	High	Chưa phân Sprint	Chưa ước lượng
9	Đổi mật khẩu	High	Chưa phân Sprint	Chưa ước lượng
10	Cập nhật thông tin cá nhân	High	Chưa phân Sprint	Chưa ước lượng
11	Xem số lượng phòng theo trạng thái	High	Chưa phân Sprint	Chưa ước lượng
12	Lọc phòng theo trạng thái	High	Chưa phân Sprint	Chưa ước lượng
13	Xem thống kê thu nhập	High	Chưa phân Sprint	Chưa ước lượng
14	Xem thống kê thu nhập theo năm	High	Chưa phân Sprint	Chưa ước lượng
15	Export thống kê thu nhập	High	Chưa phân Sprint	Chưa ước lượng
16	Hiển thị danh sách thể loại phòng	Chưa xác định	1	3
17	Thêm thể loại phòng	Chưa xác định	1	3
18	Cập nhật thể loại phòng	Chưa xác định	1	3
19	Xóa thể loại phòng	Chưa xác định	1	2


Tổng quan Sprint 1
Sprint 1 hiện bao gồm các backlog item:
#1, #2, #3, #4, #5, #6, #16, #17, #18, #19
Tổng Story Point:
3 + 1 + 5 + 3 + 3 + 5 + 3 + 3 + 3 + 2 = 31 Story Points
7. Chi tiết yêu cầu và tiêu chí nghiệm thu
US-01 — Đăng nhập
User Story
Là người dùng, tôi muốn có thể đăng nhập vào hệ thống bằng tài khoản đã tạo.

Mô tả
- Người dùng phải đăng nhập mới truy cập được trang chủ.
- Sử dụng session để lưu trạng thái đăng nhập và thông tin người đăng nhập.
Acceptance Criteria
- Đăng nhập bằng email và mật khẩu.
- Thông báo khi sai tài khoản hoặc mật khẩu.
- Đăng nhập thành công vào hệ thống khi thông tin hợp lệ.
US-02 — Đăng xuất
User Story
Là người dùng, tôi muốn có thể đăng xuất khỏi hệ thống.

Acceptance Criteria đề xuất theo hành vi của chức năng
- Người dùng có thể chọn chức năng đăng xuất.
- Phiên đăng nhập hiện tại được kết thúc.
- Người dùng không còn truy cập được các chức năng yêu cầu đăng nhập nếu chưa đăng nhập lại.
Backlog gốc chưa mô tả chi tiết Acceptance Criteria cho hạng mục này.

US-03 — Thêm mới phòng
User Story
Là người dùng, tôi muốn thêm mới phòng cho thuê.

Thông tin phòng
- Mã phòng.
- Mô tả ngắn.
- Hình ảnh.
- Thể loại phòng: đơn, đôi, VIP.
- Giá thuê.
- Trạng thái mặc định: phòng trống.
Acceptance Criteria
- Có chức năng Thêm mới trong khu vực Quản lý phòng.
- Hiển thị form thêm phòng.
- Cho phép upload ảnh.
- Có thể chọn thể loại phòng.
- Các trường dữ liệu phải được validate.
- Phòng mới có trạng thái mặc định là phòng trống.
US-04 — Xóa phòng
User Story
Là người dùng, tôi muốn xóa một phòng.

Quy tắc
- Không được xóa phòng đang cho thuê.
Acceptance Criteria
- Có nút Xóa tại danh sách phòng.
- Hiển thị xác nhận trước khi xóa.
- Không cho phép xóa phòng đang cho thuê.
- Thông báo khi xóa thành công.
US-05 — Xem danh sách phòng
User Story
Là người dùng, tôi muốn xem danh sách phòng.

Acceptance Criteria
Danh sách phòng được hiển thị tại trang chủ theo dạng lưới và thể hiện:
- Mã phòng.
- Trạng thái phòng.
- Giờ vào.
- Giờ ra.
Quy ước màu theo backlog:
Trạng thái	Màu hiển thị
Phòng trống	Xanh
Đã có người thuê	Đỏ


US-06 — Cập nhật thông tin phòng
User Story
Là người dùng, tôi muốn cập nhật thông tin một phòng.

Acceptance Criteria
- Có nút cập nhật tại danh sách phòng.
- Form cập nhật hiển thị dữ liệu hiện tại của phòng.
- Cho phép chỉnh sửa thông tin.
- Cho phép upload/thay đổi ảnh.
- Validate các trường bắt buộc.
- Thông báo khi cập nhật thành công.
US-07 — Cho thuê phòng
User Story
Là người dùng, tôi muốn cho thuê phòng.

Acceptance Criteria
- Có nút Cho thuê tại trang danh sách phòng.
- Khi chọn cho thuê, hiển thị đầy đủ thông tin phòng.
- Tự động lấy thời gian hệ thống làm giờ bắt đầu thuê.
- Cho phép chọn thời gian trả phòng.
- Tính thời gian thuê.
- Tính giá phải trả theo công thức đã quy định.
- Validate dữ liệu trước khi lưu.
- Sau khi lưu, quay lại danh sách phòng.
- Trạng thái phòng được cập nhật phù hợp với việc đã cho thuê.
US-08 — Trả phòng
User Story
Là người dùng, tôi muốn trả phòng.

Acceptance Criteria
- Chỉ phòng đã cho thuê mới có chức năng Trả phòng.
- Khi trả phòng thành công, trạng thái phòng được cập nhật thành Phòng trống.
US-09 — Đổi mật khẩu
User Story
Là người dùng, tôi muốn đổi mật khẩu của mình.

Acceptance Criteria
- Có chức năng thay đổi mật khẩu trong menu.
- Hiển thị form thay đổi mật khẩu.
- Nhập mật khẩu mới.
- Xác nhận mật khẩu mới.
- Validate các trường bắt buộc.
- Thông báo khi cập nhật thành công.
US-10 — Cập nhật thông tin cá nhân
User Story
Là người dùng, tôi muốn cập nhật thông tin cá nhân.

Thông tin cá nhân
- Tên.
- Ngày sinh.
- Email.
- Số điện thoại.
- Ảnh đại diện.
Quy tắc
- Email không được phép cập nhật.
Acceptance Criteria
- Có chức năng cập nhật thông tin cá nhân trong menu.
- Form hiển thị thông tin hiện tại.
- Cho phép chỉnh sửa các trường được phép.
- Cho phép upload ảnh.
- Validate dữ liệu bắt buộc.
- Thông báo khi cập nhật thành công.
US-11 — Xem số lượng phòng theo trạng thái
User Story
Là người dùng, tôi muốn xem số lượng phòng theo trạng thái.

Acceptance Criteria
- Hiển thị số lượng phòng theo từng trạng thái.
- Thông tin số lượng được hiển thị cùng khu vực danh sách phòng.
US-12 — Lọc phòng theo trạng thái
User Story
Là người dùng, tôi muốn lọc phòng theo trạng thái.

Acceptance Criteria
- Người dùng chọn/click vào số lượng phòng của một trạng thái.
- Hệ thống hiển thị danh sách các phòng thuộc trạng thái được chọn.
US-13 — Xem thống kê thu nhập
User Story
Là người dùng, tôi muốn xem thống kê thu nhập.

Acceptance Criteria
- Có menu Thống kê thu nhập.
- Hiển thị thống kê của năm hiện tại.
- Hiển thị đủ 12 tháng.
- Bảng gồm tối thiểu hai cột:
Cột	Nội dung
Tháng	Tháng thống kê
Tổng tiền	Tổng doanh thu của tháng


- Hiển thị tổng doanh thu của cả 12 tháng.
US-14 — Xem thống kê thu nhập theo năm
User Story
Là người dùng, tôi muốn xem thống kê thu nhập theo năm.

Acceptance Criteria
- Thực hiện tại trang Thống kê thu nhập.
- Cho phép chọn năm cần xem.
- Hiển thị doanh thu theo từng tháng của năm được chọn.
US-15 — Export thống kê thu nhập
User Story
Là người dùng, tôi muốn export thống kê thu nhập.

Acceptance Criteria
- Trang thống kê có nút Export PDF.
- Khi chọn Export PDF, hệ thống tạo file PDF chứa bảng thống kê thu nhập.
US-16 — Danh sách thể loại phòng
User Story
Là người dùng, tôi muốn hiển thị danh sách thể loại phòng.

Backlog gốc chưa mô tả chi tiết Description và Acceptance Criteria cho hạng mục này.

US-17 — Thêm thể loại phòng
User Story
Là người dùng, tôi muốn thêm thể loại phòng.

Backlog gốc chưa mô tả chi tiết Description và Acceptance Criteria cho hạng mục này.

US-18 — Cập nhật thể loại phòng
User Story
Là người dùng, tôi muốn cập nhật thể loại phòng.

Backlog gốc chưa mô tả chi tiết Description và Acceptance Criteria cho hạng mục này.

US-19 — Xóa thể loại phòng
User Story
Là người dùng, tôi muốn xóa thể loại phòng.

Backlog gốc chưa mô tả chi tiết Description và Acceptance Criteria cho hạng mục này.

8. Trạng thái phòng
Theo các yêu cầu hiện có, hệ thống tối thiểu có hai trạng thái:
Trạng thái	Ý nghĩa
AVAILABLE / Phòng trống	Phòng chưa có người thuê và có thể cho thuê
RENTED / Đã cho thuê	Phòng đang có người thuê


Tên mã trạng thái trong bảng trên chỉ là cách đặt tên gợi ý khi triển khai. Backlog hiện chỉ quy định ý nghĩa nghiệp vụ bằng tiếng Việt.
9. Validate dữ liệu
Các form có yêu cầu kiểm tra dữ liệu gồm:
- Đăng nhập.
- Thêm phòng.
- Cập nhật phòng.
- Cho thuê phòng.
- Đổi mật khẩu.
- Cập nhật thông tin cá nhân.
Một số nguyên tắc validate nên được áp dụng khi triển khai:
- Không để trống trường bắt buộc.
- Email phải đúng định dạng.
- Giá thuê phải là số hợp lệ và không âm.
- Mã phòng không được để trống.
- Mật khẩu mới và xác nhận mật khẩu phải trùng nhau.
- File upload phải được kiểm tra định dạng phù hợp.
- Thời gian trả không được nhỏ hơn thời gian bắt đầu thuê.
Các quy tắc validate chi tiết ngoài phần đã ghi trong backlog cần được nhóm thống nhất trước khi triển khai.

10. Gợi ý cấu trúc màn hình
Đăng nhập
│
└── Trang chủ / Danh sách phòng
    │
    ├── Tổng quan trạng thái phòng
    ├── Lọc phòng theo trạng thái
    ├── Thêm phòng
    ├── Cập nhật phòng
    ├── Xóa phòng
    ├── Cho thuê phòng
    └── Trả phòng

Menu
│
├── Quản lý phòng
├── Quản lý thể loại phòng
├── Thống kê thu nhập
│   ├── Xem theo năm
│   └── Export PDF
├── Thông tin cá nhân
├── Đổi mật khẩu
└── Đăng xuất
11. Cấu trúc dữ liệu nghiệp vụ gợi ý
Dựa trên backlog, hệ thống tối thiểu cần quản lý các nhóm dữ liệu sau:
User
- id
- name
- date_of_birth
- email
- phone
- avatar
- password
Room
- id
- room_code
- description
- image
- room_type
- rental_price
- status
RoomType
- id
- name
- description
Rental
- id
- room_id
- check_in_time
- check_out_time
- rental_duration
- total_amount
Đây là cấu trúc dữ liệu định hướng dựa trên nghiệp vụ trong backlog, không phải thiết kế cơ sở dữ liệu bắt buộc.

12. Yêu cầu phi chức năng nên áp dụng
Backlog chủ yếu mô tả yêu cầu chức năng. Khi triển khai thực tế, dự án nên bổ sung các yêu cầu phi chức năng sau:
- Giao diện dễ sử dụng và thống nhất.
- Các thao tác thêm, sửa, xóa có thông báo kết quả rõ ràng.
- Các thao tác xóa dữ liệu cần xác nhận.
- Dữ liệu đầu vào phải được validate cả phía giao diện và phía server.
- Mật khẩu không lưu ở dạng văn bản thuần.
- Chức năng yêu cầu đăng nhập phải kiểm tra session.
- File upload cần giới hạn loại file và kích thước.
- Thao tác thống kê cần trả kết quả chính xác theo dữ liệu thuê phòng.
- File PDF xuất ra phải đọc được và thể hiện đúng bảng thống kê.
13. Cài đặt và chạy dự án
Product Backlog hiện chưa cung cấp thông tin về công nghệ, framework, cơ sở dữ liệu hoặc câu lệnh khởi chạy dự án.
Sau khi nhóm xác định công nghệ, cập nhật phần này theo mẫu:
# Clone repository
git clone <repository-url>

# Di chuyển vào thư mục dự án
cd <project-folder>

# Cài đặt dependency
<install-command>

# Cấu hình môi trường
<environment-setup>

# Chạy dự án
<run-command>
Không nên điền câu lệnh cụ thể khi công nghệ của dự án chưa được xác nhận.
14. Quy trình Git đề xuất cho nhóm
Mỗi chức năng nên được thực hiện trên một branch riêng:
git checkout main
git pull origin main
git checkout -b feature/<ten-chuc-nang>
Ví dụ:
git checkout -b feature/login
git checkout -b feature/room-management
git checkout -b feature/room-type
git checkout -b feature/rental
git checkout -b feature/revenue-report
Sau khi hoàn thành:
git add .
git commit -m "feat: implement <feature-name>"
git push -u origin feature/<ten-chuc-nang>
Sau đó tạo Pull Request để kiểm tra trước khi merge vào main.
15. Quy ước commit đề xuất
Loại	Ý nghĩa
feat	Thêm chức năng mới
fix	Sửa lỗi
docs	Sửa tài liệu
style	Thay đổi giao diện/định dạng không ảnh hưởng logic
refactor	Cải tiến cấu trúc code
test	Thêm hoặc sửa test
chore	Công việc cấu hình, dependency hoặc bảo trì


Ví dụ:
feat: add login feature
feat: add room creation
fix: prevent deleting rented room
feat: add revenue report
docs: update README
16. Definition of Done đề xuất
Một Product Backlog Item được xem là hoàn thành khi:
- Chức năng đáp ứng Acceptance Criteria.
- Validate dữ liệu hoạt động đúng.
- Không làm hỏng chức năng hiện có.
- Giao diện hiển thị đúng yêu cầu.
- Đã kiểm tra luồng thành công và luồng lỗi.
- Code đã được commit lên branch chức năng.
- Pull Request đã được review.
- Đã merge vào nhánh chính theo quy trình của nhóm.
17. Các nội dung backlog cần làm rõ thêm
Một số hạng mục trong backlog chưa có đầy đủ Description hoặc Acceptance Criteria:
- US-02 — Đăng xuất.
- US-05 — Xem danh sách phòng.
- US-06 — Cập nhật phòng chưa có Description riêng.
- US-09 — Đổi mật khẩu chưa mô tả yêu cầu kiểm tra mật khẩu cũ.
- US-11 — Xem số lượng phòng theo trạng thái.
- US-16 đến US-19 — Quản lý thể loại phòng.
- Đơn vị tính thời gian và giá tiền khi cho thuê.
- Quy tắc làm tròn tiền thuê.
- Thời điểm doanh thu được ghi nhận.
- Quy tắc xóa thể loại phòng đang được phòng sử dụng.
- Quy tắc trùng mã phòng.
- Quy định định dạng và kích thước ảnh upload.
Nhóm nên thống nhất các nội dung trên trước khi triển khai để tránh mỗi thành viên hiểu yêu cầu theo một cách khác nhau.
18. Phạm vi tài liệu
README này được xây dựng từ Product Backlog hiện tại của dự án và phản ánh yêu cầu nghiệp vụ, không phải báo cáo tiến độ thực tế.
Các mục như công nghệ sử dụng, cấu trúc thư mục, database schema, hướng dẫn cài đặt chính xác và trạng thái hoàn thành cần được cập nhật theo mã nguồn thực tế của nhóm.
19. License
Dự án phục vụ mục đích học tập/thực hành. Thông tin giấy phép sử dụng có thể được bổ sung khi nhóm thống nhất.
Project: TTCS_T926_K20C6
Document: README.md
Nguồn yêu cầu: Product Backlog dự án quản lý khách sạn / phòng cho thuê
