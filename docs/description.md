# Hệ thống Quản lý Chi tiêu cho Tập thể / Tổ chức

Ứng dụng web quản lý thu, chi, hạn mức và báo cáo tài chính cho tập thể / tổ chức, xây dựng bằng **Python 3.11, Flask, Flask-SQLAlchemy, SQLite, Flask-Login, Waitress và Bootstrap 5**. Ứng dụng dùng cấu trúc **Application Factory + Blueprint**, chạy trên Windows và Raspberry Pi; host và port được cấu hình bằng biến môi trường.

> Đây là phiên bản phục vụ học tập và chạy thử trên máy cá nhân. Tài khoản mẫu và dữ liệu được tạo bởi `seed.py` chỉ để demo; hãy đổi mật khẩu và cấu hình `SECRET_KEY` trước khi đưa vào sử dụng với dữ liệu thật.

## 1. Tính năng chính

### Xác thực và phân quyền
- Đăng nhập / đăng xuất bằng tài khoản do quản trị viên cấp.
- Mật khẩu được băm bằng cơ chế của Werkzeug, không lưu mật khẩu dạng văn bản gốc.
- Hai vai trò: `admin` (quản trị viên) và `user` (thành viên).
- Quản trị viên có thể tạo tài khoản, sửa tên, đổi mật khẩu, phân quyền và khóa/mở khóa tài khoản.
- Thành viên xem được giao dịch cá nhân của mình và giao dịch thuộc quỹ chung. Quản trị viên có thể xem toàn bộ giao dịch.
- Mỗi biểu mẫu POST đều được bảo vệ bằng CSRF token. Thành viên chỉ được sửa/xóa giao dịch do chính mình tạo; quản trị viên có quyền quản lý mọi giao dịch.

### Giao dịch và danh mục
- Ghi nhận cả **thu nhập** và **chi tiêu**. Loại giao dịch được xác định theo loại danh mục.
- Thêm, sửa và xóa giao dịch; thông tin gồm ngày, số tiền, danh mục, mục đích/ghi chú và nguồn tiền.
- Nguồn tiền hiện hỗ trợ `personal` (cá nhân) và `common` (quỹ chung tập thể / tổ chức). “Ngân sách đơn vị” trong yêu cầu ban đầu chưa được triển khai thành nguồn riêng.
- Từ chối số tiền âm, bằng 0, không hợp lệ hoặc vượt giới hạn; ngày và danh mục cũng được kiểm tra phía máy chủ.
- Hỗ trợ lọc lịch sử theo ngày bắt đầu/kết thúc, loại giao dịch, nguồn tiền, danh mục và thành viên (đối với quản trị viên).
- Quản trị viên có thể thêm hoặc ẩn danh mục thu/chi. Danh mục đã được dùng trong lịch sử vẫn được giữ lại để đảm bảo dữ liệu cũ có thể đọc được.

### Hạn mức và cảnh báo
- Hạn mức theo tuần (ISO), tháng hoặc quý.
- Hạn mức cho từng thành viên hoặc cho quỹ chung.
- Tự tính tổng chi trong kỳ và tỷ lệ sử dụng hạn mức; cảnh báo trên giao diện khi tổng chi vượt hạn mức.
- Hạn mức chỉ cộng các giao dịch có danh mục loại `expense`, không cộng thu nhập.

### Báo cáo và xuất dữ liệu
- Xem báo cáo theo ngày, tuần, tháng, năm hoặc khoảng thời gian tùy chọn.
- Tổng hợp tổng thu, tổng chi, chênh lệch thu - chi, chi tiêu theo ngày và theo danh mục.
- Xuất báo cáo giao dịch ra **Excel (`.xlsx`)** hoặc **CSV UTF-8**. File Excel gồm sheet tổng quan và sheet giao dịch.
- Bảng điều khiển hiển thị chỉ số tháng hiện tại, biểu đồ chi tiêu theo ngày, hạn mức đang hiệu lực và các giao dịch gần đây.

## 2. Công nghệ

| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ | Python 3.11 |
| Web framework | Flask 3.1 |
| WSGI server | Waitress 3.0.2 khi `FLASK_DEBUG=0` |
| Kiến trúc | Flask Application Factory + Blueprint; tách route, model, template và tiện ích nghiệp vụ |
| ORM / CSDL | Flask-SQLAlchemy, SQLAlchemy 2.x, SQLite |
| Xác thực | Flask-Login, Werkzeug password hashing |
| Bảo vệ biểu mẫu | Flask-WTF CSRFProtect |
| Giao diện | Jinja2, Bootstrap 5, Bootstrap Icons, Chart.js |
| Xuất Excel | openpyxl |
| Cấu hình môi trường | python-dotenv |

## 3. Cấu trúc thư mục

```text
quan-li-chi-tieu-refresh/
├── app/
│   ├── __init__.py             # create_app(), đăng ký extension/blueprint/filter
│   ├── config.py               # Cấu hình Flask và SQLite
│   ├── extensions.py           # db, login_manager, csrf
│   ├── models.py               # Role, User, Category, Expense, Budget
│   ├── utils.py                # Phân quyền, kiểm tra dữ liệu, tính hạn mức
│   ├── auth/
│   │   └── routes.py           # Đăng nhập / đăng xuất
│   ├── main/
│   │   └── routes.py           # Bảng điều khiển
│   ├── transactions/
│   │   └── routes.py           # Danh sách, thêm, sửa, xóa giao dịch
│   ├── budgets/
│   │   └── routes.py           # Xem / quản lý hạn mức
│   ├── reports/
│   │   └── routes.py           # Báo cáo, xuất XLSX / CSV
│   ├── admin/
│   │   └── routes.py           # Tài khoản và danh mục
│   ├── templates/              # Giao diện Jinja2
│   └── static/css/style.css    # CSS tùy chỉnh
├── instance/
│   └── .gitkeep                # SQLite và bản sao lưu được lưu cục bộ, không đưa lên Git
├── data/
│   └── mau_cau_truc_du_lieu.xlsx # Mẫu Excel cấu trúc giao dịch để thu thập dữ liệu
├── tests/
│   └── test_app.py             # Smoke test cơ bản
├── .env.example                # Mẫu cấu hình môi trường
├── .gitignore                  # Loại trừ venv, .env, SQLite, cache
├── requirements.txt            # Thư viện chạy ứng dụng
├── run.py                      # Waitress khi debug tắt; Flask development server khi debug bật
├── backup_db.py                # Sao lưu SQLite và kiểm tra tính toàn vẹn
├── seed.py                     # Tạo CSDL và dữ liệu demo
└── README.md
```

## 4. Thiết kế cơ sở dữ liệu

Các tên bảng và trường cốt lõi bám sát hồ sơ dự án. Một số trường bổ sung được dùng để đáp ứng yêu cầu khóa tài khoản, quản lý danh mục, các chu kỳ tuần/quý và phân biệt hạn mức quỹ chung.

### `Role` — vai trò

| Trường | Kiểu / ràng buộc | Ý nghĩa |
|---|---|---|
| `idRole` | Integer, PK | Mã vai trò |
| `roleName` | String, unique | `admin` hoặc `user` |
| `description` | String | Mô tả quyền |

### `User` — tài khoản thành viên

| Trường | Kiểu / ràng buộc | Ý nghĩa |
|---|---|---|
| `idUser` | Integer, PK | Mã người dùng |
| `username` | String, unique, index | Tên đăng nhập |
| `password` | String | Chuỗi băm mật khẩu |
| `hoten` | String | Họ và tên |
| `idRole` | Integer, FK → `Role.idRole` | Vai trò |
| `is_active_account` | Boolean, bổ sung | Trạng thái khóa/mở tài khoản |
| `created_at` | DateTime, bổ sung | Thời điểm tạo tài khoản |

### `Category` — danh mục

| Trường | Kiểu / ràng buộc | Ý nghĩa |
|---|---|---|
| `idCategory` | Integer, PK | Mã danh mục |
| `nameCategory` | String | Tên danh mục |
| `type` | String | `expense` hoặc `income` |
| `is_active` | Boolean, bổ sung | Ẩn danh mục mà không làm mất lịch sử giao dịch |

Cặp (`nameCategory`, `type`) là duy nhất.

### `Expense` — giao dịch thu/chi

| Trường | Kiểu / ràng buộc | Ý nghĩa |
|---|---|---|
| `idExpense` | Integer, PK | Mã giao dịch |
| `idUser` | Integer, FK → `User.idUser` | Người ghi nhận giao dịch |
| `idCategory` | Integer, FK → `Category.idCategory` | Danh mục xác định loại thu/chi |
| `date` | Date | Ngày giao dịch |
| `amount` | Numeric(14,2) | Số tiền dương; loại giao dịch lấy từ `Category.type` |
| `purpose` | String | Mục đích / ghi chú |
| `source` | String | `personal` hoặc `common` |
| `created_at`, `updated_at` | DateTime, bổ sung | Thời điểm tạo / cập nhật |

### `Budget` — hạn mức

| Trường | Kiểu / ràng buộc | Ý nghĩa |
|---|---|---|
| `idBudget` | Integer, PK | Mã hạn mức |
| `idUser` | Integer, FK → `User.idUser`, nullable | Thành viên được áp dụng; `NULL` nếu là quỹ chung |
| `amountLimit` | Numeric(14,2) | Hạn mức tối đa |
| `month` | Integer, nullable | Tháng hoặc tháng bắt đầu của kỳ |
| `year` | Integer | Năm áp dụng |
| `source` | String, bổ sung | `personal` hoặc `common` |
| `period_type` | String, bổ sung | `weekly`, `monthly` hoặc `quarterly` |
| `period_number` | Integer, bổ sung | Số tuần ISO, tháng hoặc quý |
| `created_at` | DateTime, bổ sung | Thời điểm tạo hạn mức |

### Quan hệ chính

```text
Role 1 ───── n User
User 1 ───── n Expense
Category 1 ─ n Expense
User 1 ───── n Budget (hạn mức cá nhân)
Budget với idUser = NULL (hạn mức quỹ chung)
```

Mật khẩu được lưu dưới dạng chuỗi băm. Không lưu dữ liệu đăng nhập thô vào CSDL.

### Mẫu Excel thu thập dữ liệu

Tệp [`data/mau_cau_truc_du_lieu.xlsx`](data/mau_cau_truc_du_lieu.xlsx) có các sheet hướng dẫn, giao dịch mẫu (kèm các dòng trống để điền) và danh mục tham khảo. Tệp được cung cấp để thu thập/kiểm tra cấu trúc dữ liệu; ứng dụng hiện **chưa hỗ trợ import Excel trực tiếp**. Dữ liệu demo thực sự trong SQLite được tạo bằng `python seed.py`.

## 5. Yêu cầu trước khi cài đặt

- Windows 10/11.
- Python **3.11.x** đã cài đặt và có thể gọi bằng lệnh `py -3.11` hoặc `python`.
- Kết nối Internet ở bước đầu để tải các package Python và thư viện giao diện từ CDN.
- Git nếu muốn commit và đẩy mã nguồn lên GitHub.

Kiểm tra Python:

```powershell
py -3.11 --version
```

Nếu lệnh không chạy, hãy cài Python 3.11 từ trang chính thức `https://www.python.org/downloads/`, chọn tùy chọn thêm Python vào PATH khi cài đặt.

## 6. Cài đặt trên Windows

### Bước 1 — giải nén hoặc clone dự án

Nếu có file ZIP, giải nén vào một thư mục thuận tiện, ví dụ `D:\Projects\quan-li-chi-tieu-refresh` rồi mở Terminal tại thư mục đó.

Nếu dự án đã nằm trên GitHub:

```powershell
git clone <URL_REPOSITORY>
cd quan-li-chi-tieu-refresh
```

### Bước 2 — tạo môi trường ảo

**PowerShell:**

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Nếu PowerShell chặn script kích hoạt, chỉ cho phép trong cửa sổ hiện tại:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

**Command Prompt (cmd):**

```bat
py -3.11 -m venv .venv
.venv\Scripts\activate.bat
```

Sau khi kích hoạt thành công, đầu dòng terminal thường có tiền tố `(.venv)`.

### Bước 3 — cài thư viện

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Nếu tải package bị lỗi do mạng, thử lại khi mạng ổn định. Chạy lệnh trong đúng thư mục có `requirements.txt` và bảo đảm môi trường `.venv` đã được kích hoạt.

### Bước 4 — tạo cấu hình môi trường

**PowerShell:**

```powershell
Copy-Item .env.example .env
```

**cmd:**

```bat
copy .env.example .env
```

Mở `.env` và thay `SECRET_KEY` bằng một chuỗi ngẫu nhiên dài. Giữ `FLASK_DEBUG=0` để chạy Waitress; chỉ đặt `FLASK_DEBUG=1` tạm thời khi cần debug local. Ví dụ có thể tạo khóa ngẫu nhiên bằng lệnh:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Dán kết quả vào `SECRET_KEY` trong `.env`. Giữ `DATABASE_URL=sqlite:///family_expenses.db` nếu muốn đặt CSDL tại `instance/family_expenses.db`. Có thể đặt `FLASK_HOST` và `FLASK_PORT`; mặc định ứng dụng chỉ nghe trên `127.0.0.1:5000`. Launcher Linux bật host `0.0.0.0` để truy cập LAN và luôn tắt debug.

### Bước 5 — tạo CSDL và dữ liệu mẫu

```powershell
python seed.py
```

Lệnh sẽ tạo các bảng SQLite, 5 tài khoản mẫu, danh mục, hạn mức và mặc định 360 giao dịch rải trên khoảng 90 ngày. Nếu muốn tạo số lượng khác:

```powershell
python seed.py --transactions 420
```

Nếu cơ sở dữ liệu đã chứa tài khoản, script sẽ không ghi đè dữ liệu hiện tại. Muốn **xóa toàn bộ dữ liệu hiện tại và tạo lại dữ liệu demo**, chạy:

```powershell
python seed.py --reset
```

> `--reset` là thao tác phá hủy dữ liệu. Không sử dụng với dữ liệu thật.

Nếu chỉ cần tạo các bảng trống mà không tạo dữ liệu demo:

```powershell
flask --app run.py init-db
```

`db.create_all()` tạo bảng còn thiếu, nhưng không tự động cập nhật cấu trúc của bảng đã tồn tại. Khi thay đổi model sau này, hãy dùng Flask-Migrate/Alembic hoặc tạo migration phù hợp; không chạy `--reset` trên dữ liệu cần giữ.

### Bước 6 — khởi chạy ứng dụng

```powershell
python run.py
```

Mở trình duyệt tại:

- Ứng dụng: `http://127.0.0.1:5000`
- Có thể dùng `http://localhost:5000` tương đương.

Dừng server bằng `Ctrl + C` trong terminal.

## 7. Sao lưu và khôi phục SQLite

Khi ứng dụng đang chạy hoặc đã dừng, tạo bản sao lưu nhất quán bằng SQLite backup API:

```powershell
python backup_db.py
```

Bản sao lưu được ghi vào `instance/backups/` và kiểm tra bằng `PRAGMA integrity_check`. Thư mục này bị loại khỏi Git. Hãy chép bản sao lưu sang thiết bị lưu trữ khác để phòng hỏng hoặc mất Raspberry Pi.

Để khôi phục, dừng ứng dụng, giữ lại database hiện tại để có thể quay lui, rồi chép file `.sqlite3` cần khôi phục về đúng đường dẫn SQLite đang dùng (mặc định `instance/family_expenses.db`). Khởi động lại ứng dụng và đăng nhập kiểm tra dữ liệu.

## 8. Tài khoản demo

| Vai trò | Tên đăng nhập | Mật khẩu ban đầu |
|---|---|---|
| Quản trị viên | `admin` | `admin12345` |
| Thành viên | `member1` | `member12345` |
| Thành viên | `member2` | `member12345` |
| Thành viên | `member3` | `member12345` |
| Thành viên | `member4` | `member12345` |

Đây là thông tin demo cố định để tiện chấm thử. Đổi mật khẩu hoặc tạo tài khoản mới trước khi đưa dữ liệu thật vào hệ thống.

## 9. Luồng sử dụng gợi ý

1. Đăng nhập bằng tài khoản `admin`.
2. Vào **Quản trị → Tài khoản thành viên** để tạo hoặc khóa/mở khóa tài khoản.
3. Vào **Quản trị → Danh mục thu/chi** để bổ sung danh mục phù hợp.
4. Vào **Hạn mức → Thiết lập hạn mức** để đặt hạn mức cá nhân theo thành viên hoặc hạn mức cho quỹ chung.
5. Các thành viên vào **Giao dịch → Thêm giao dịch** để nhập các khoản thu/chi.
6. Theo dõi cảnh báo trên bảng điều khiển và trang hạn mức.
7. Vào **Báo cáo** để lọc thời gian, xem tổng thu/chi rồi chọn xuất Excel hoặc CSV.

## 10. Kiểm tra nhanh

Kiểm tra cú pháp tất cả file Python:

```powershell
python -m compileall app run.py seed.py init_admin.py backup_db.py
```

Nếu đã cài `pytest`, có thể chạy kiểm thử:

```powershell
python -m pip install pytest
python -m pytest
```

Kiểm thử tập trung vào tạo ứng dụng, đăng nhập, phân quyền, giới hạn giao dịch theo thành viên/nguồn quỹ và kiểm tra số tiền.

## 11. Git và GitHub

Tệp `.gitignore` đã loại trừ `.venv`, `.env`, CSDL SQLite, cache Python và cấu hình IDE để tránh đưa bí mật hoặc dữ liệu cá nhân lên GitHub.

Repository này dùng `chatgpt-work` làm branch làm việc. Trước khi commit, kiểm tra branch và `git status`; không đưa `.env`, SQLite hoặc bản sao lưu vào Git.

```powershell
git switch chatgpt-work
git status
```

## 12. Chạy trên Raspberry Pi / LAN

Tạo `.env` với `SECRET_KEY` riêng, `FLASK_DEBUG=0`, và database SQLite trên bộ nhớ lưu trữ bền vững. `run_admin.sh` khởi tạo admin chỉ khi database chưa có dữ liệu; nếu đã có dữ liệu thì giữ nguyên. `run_demo.sh` yêu cầu xác nhận trước khi xóa và tạo lại dữ liệu demo.

Launcher Linux đặt `FLASK_HOST=0.0.0.0`, `FLASK_PORT=5000` và `FLASK_DEBUG=0`. Khi debug tắt, `run.py` dùng Waitress với hai thread. Chỉ mở cổng trong mạng tin cậy; không chuyển tiếp trực tiếp ra Internet.

Khi chỉ chạy HTTP trong LAN, giữ `SESSION_COOKIE_SECURE=0`; chỉ đặt `1` nếu ứng dụng được phục vụ hoàn toàn qua HTTPS.

Chạy thủ công trên Windows hoặc Linux:

```powershell
python run.py
```

Mặc định app nghe trên `127.0.0.1:5000`. Muốn truy cập LAN trên Windows, đặt `FLASK_HOST=0.0.0.0` và giới hạn truy cập bằng firewall. Bootstrap, Bootstrap Icons và Chart.js hiện tải từ CDN nên trình duyệt cần Internet để hiển thị đầy đủ giao diện.

## 13. Phạm vi và điểm cần phát triển tiếp

- Giao dịch hiện được nhập thủ công; chưa kết nối API ngân hàng/ví điện tử.
- Chưa có ứng dụng điện thoại độc lập hoặc nhận diện hóa đơn qua camera.
- Chưa hỗ trợ đa tiền tệ, hiện mặc định VNĐ.
- Chưa có audit log đầy đủ cho mọi thay đổi và chưa tích hợp quy trình quên mật khẩu qua email.
- Chưa có import Excel trực tiếp; file mẫu chỉ phục vụ thu thập dữ liệu.
- Nguồn tiền hiện chỉ gồm `personal` và `common`; “ngân sách đơn vị” cần được bổ sung nếu vẫn là yêu cầu bắt buộc.
- Khi mở rộng quy mô, nên bổ sung migration database, phân trang cho danh sách giao dịch lớn, kiểm thử nghiệp vụ sâu hơn và dùng PostgreSQL nếu tải ghi đồng thời tăng.

## 14. Tài liệu tham khảo kỹ thuật

- Flask: <https://flask.palletsprojects.com/>
- Flask application factories: <https://flask.palletsprojects.com/en/stable/patterns/appfactories/>
- Flask-SQLAlchemy: <https://flask-sqlalchemy.palletsprojects.com/>
- Flask-Login: <https://flask-login.readthedocs.io/>
- Flask-WTF / CSRF: <https://flask-wtf.readthedocs.io/>
- Bootstrap: <https://getbootstrap.com/>
- openpyxl: <https://openpyxl.readthedocs.io/>
