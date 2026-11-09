# Hệ thống Quản lý Chi tiêu Tập thể / Tổ chức

Quản lí bởi ChatGPT và Codex

Ứng dụng web Flask giúp một tập thể hoặc tổ chức ghi nhận thu chi, theo dõi ngân sách và xem báo cáo tài chính. Ứng dụng dùng SQLite, hỗ trợ chạy trên Windows và Raspberry Pi/Linux; giao diện Bootstrap được lưu cục bộ để sử dụng trong mạng nội bộ không cần CDN.

## Tính năng

- Đăng nhập, phân quyền quản trị viên và thành viên; mật khẩu được lưu dưới dạng băm.
- Quản lý tài khoản thành viên và danh mục thu/chi.
- Thêm, sửa, xóa giao dịch; hỗ trợ nguồn `personal` (cá nhân), `common` (quỹ chung) và `unit` (ngân sách đơn vị).
- Hạn mức theo tuần, tháng hoặc quý; cảnh báo khi sử dụng từ 80% hoặc vượt mức.
- Bảng tổng quan, lọc báo cáo theo thời gian, nguồn tiền và thành viên; xuất Excel hoặc CSV UTF-8.
- Nhập giao dịch từ tệp `.xlsx` theo mẫu sau bước xem trước.
- Nhật ký hoạt động quản trị, sao lưu SQLite từ giao diện hoặc dòng lệnh.

## Công nghệ và cấu trúc

- Python 3.11, Flask, Flask-SQLAlchemy, SQLAlchemy, Flask-Login và Flask-WTF.
- SQLite làm cơ sở dữ liệu mặc định; Waitress chạy ứng dụng khi `FLASK_DEBUG=0`.
- Cấu trúc Flask Application Factory + Blueprint; các phần chính nằm trong `app/`.

Các bảng nghiệp vụ gồm `User`, `Role`, `Category`, `Expense` và `Budget`. `AuditLog` lưu dấu vết thao tác quản trị và tài chính, không lưu giá trị mật khẩu. SQLite được lưu mặc định tại `instance/expense.db`. Một số trường bổ sung phục vụ khóa tài khoản, ẩn danh mục, nguồn ngân sách và chu kỳ hạn mức.

## Chạy trên Windows

Cài Python 3.11, mở PowerShell tại thư mục dự án rồi chạy:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Mở `.env`, đổi `SECRET_KEY` thành chuỗi ngẫu nhiên riêng. Tạo dữ liệu mẫu và chạy ứng dụng:

```powershell
python seed.py
python run.py
```

Mở `http://127.0.0.1:5000`. Dừng ứng dụng bằng `Ctrl+C` trong terminal. Để chạy trên LAN, đặt `FLASK_HOST=0.0.0.0` trong môi trường chạy ứng dụng và giới hạn truy cập bằng firewall.

## Chạy trên Raspberry Pi / Linux

Tạo môi trường bằng Python 3.11 và cài dependencies:

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Sau khi tạo `.env` với `SECRET_KEY` riêng, dùng `./run_admin.sh` để khởi tạo tài khoản quản trị nếu CSDL còn trống và chạy server trên LAN. Script `./run_demo.sh` tạo lại dữ liệu demo và yêu cầu xác nhận trước khi xóa dữ liệu cũ. Hướng dẫn cài Python 3.11 trên Debian 13 Trixie có trong [docs/python311-trixie.md](docs/python311-trixie.md).

## Tài khoản và dữ liệu demo

`python seed.py` tạo dữ liệu demo nếu CSDL chưa có tài khoản. Tài khoản mẫu:

| Vai trò | Tên đăng nhập | Mật khẩu ban đầu |
|---|---|---|
| Quản trị viên | `admin` | `admin12345` |
| Thành viên | `member1` đến `member4` | `member12345` |

Đây là thông tin thử nghiệm; hãy đổi mật khẩu trước khi nhập dữ liệu thật. Không dùng `python seed.py --reset` trên CSDL cần giữ vì lệnh này xóa dữ liệu hiện có.

## Sao lưu và khôi phục

Quản trị viên có thể tạo và tải bản sao lưu từ **Quản trị → Sao lưu database**. Có thể tạo bản sao từ dòng lệnh:

```powershell
python backup_db.py
```

Bản sao được kiểm tra toàn vẹn và lưu trong `instance/backups/`. Khôi phục qua giao diện chưa được hỗ trợ; hãy dừng ứng dụng và làm theo hướng dẫn trong phần sao lưu và khôi phục của [docs/description.md](docs/description.md).

## Tài liệu dự án

- [Mô tả tính năng, cấu trúc, cài đặt và phạm vi dự án](docs/description.md)
- [Hồ sơ dự án](docs/quan-li-chi-tieu-refresh.txt)
- [Cấu trúc thư mục](docs/project-structure.txt)
- [Hướng dẫn Raspberry Pi OS / Debian 13 Trixie](docs/python311-trixie.md)

## Giới hạn hiện tại

Ứng dụng chưa kết nối ngân hàng hoặc ví điện tử, chưa có ứng dụng di động độc lập, chưa hỗ trợ đa tiền tệ hay nhiều đơn vị độc lập trong cùng một CSDL. Chức năng khôi phục bản sao lưu cần thực hiện thủ công.
