# Hệ thống quản lý chi tiêu tập thể và tổ chức

Ứng dụng web hỗ trợ tập thể, nhóm và tổ chức ghi nhận các khoản thu chi, theo dõi hạn mức và tổng hợp tình hình tài chính. Dự án hướng đến việc thay thế ghi chép thủ công bằng một quy trình tập trung, có phân quyền và lưu lại lịch sử hoạt động.

## Chức năng chính

- Đăng nhập và phân quyền giữa quản trị viên và thành viên.
- Quản lý tài khoản thành viên và danh mục thu, chi.
- Tạo, xem, cập nhật và xóa giao dịch thu chi theo quyền được cấp.
- Phân loại giao dịch theo nguồn tiền: cá nhân (`personal`), quỹ chung (`common`) và ngân sách đơn vị (`unit`).
- Thiết lập hạn mức theo tuần, tháng hoặc quý; theo dõi mức sử dụng và cảnh báo khi gần hoặc vượt hạn mức.
- Lọc giao dịch và xem báo cáo theo thời gian, nguồn tiền, danh mục và thành viên phù hợp với quyền truy cập.
- Xuất báo cáo ra Excel (`.xlsx`) và CSV UTF-8; nhập giao dịch từ Excel theo mẫu với bước xem trước.
- Ghi nhật kí các thao tác quan trọng và tạo bản sao lưu cơ sở dữ liệu SQLite.

## Công nghệ và kiến trúc

Dự án sử dụng Python 3.11, Flask, Flask-SQLAlchemy, SQLAlchemy, SQLite, Flask-Login, Flask-WTF, Waitress, Bootstrap 5, Bootstrap Icons, Chart.js và openpyxl. Ứng dụng được tổ chức theo mô hình Flask Application Factory kết hợp Blueprint, tách các phần xác thực, giao dịch, hạn mức, báo cáo và quản trị.

Giao diện Bootstrap, Bootstrap Icons và Chart.js được lưu trong dự án để không phụ thuộc CDN khi sử dụng. Ứng dụng có thể chạy trên Windows và Linux, bao gồm Raspberry Pi, với host và port được cấu hình qua biến môi trường.

## Phạm vi sử dụng

Phiên bản hiện tại tập trung vào quản lý thu chi cho một tập thể hoặc tổ chức trong một cơ sở dữ liệu. Hạn mức hỗ trợ theo tuần, tháng và quý. Các giao dịch dùng nguồn chung được chia sẻ theo quyền truy cập hiện có.

Ứng dụng chưa kết nối ngân hàng hoặc ví điện tử, chưa hỗ trợ đa tiền tệ hay nhiều tổ chức độc lập trong cùng hệ thống. Khôi phục bản sao lưu hiện cần thực hiện thủ công.

Dự án được xây dựng phục vụ học tập và trình diễn chức năng quản lý thu chi trên môi trường cục bộ.
