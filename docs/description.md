# Hệ thống Quản lý Chi tiêu cho Tập thể / Tổ chức

Ứng dụng web quản lý thu, chi, hạn mức và báo cáo tài chính cho tập thể / tổ chức, xây dựng bằng **Python 3.11, Flask, Flask-SQLAlchemy, SQLite, Flask-Login, Waitress và Bootstrap 5**. Ứng dụng dùng cấu trúc **Application Factory + Blueprint**, chạy trên Windows và Raspberry Pi; host và port được cấu hình bằng biến môi trường.

> Đây là phiên bản phục vụ học tập và chạy thử trên máy cá nhân. Tài khoản mẫu và dữ liệu được tạo bởi `seed.py` chỉ để demo; hãy đổi mật khẩu và cấu hình `SECRET_KEY` trước khi đưa vào sử dụng với dữ liệu thật.

## 1. Tính năng chính

### Xác thực và phân quyền
- Đăng nhập / đăng xuất bằng tài khoản do quản trị viên cấp.
- Mật khẩu được băm bằng cơ chế của Werkzeug, không lưu mật khẩu dạng văn bản gốc.
- Hai vai trò: `admin` (quản trị viên) và `user` (thành viên).
- Quản trị viên có thể tạo tài khoản, sửa tên, đổi mật khẩu, phân quyền và khóa/mở khóa tài khoản.
- Thành viên xem được giao dịch cá nhân của mình và các giao dịch dùng chung thuộc quỹ chung hoặc ngân sách đơn vị. Quản trị viên có thể xem toàn bộ giao dịch.
- Mỗi biểu mẫu POST đều được bảo vệ bằng CSRF token. Thành viên chỉ được sửa/xóa giao dịch do chính mình tạo; quản trị viên có quyền quản lý mọi giao dịch.

### Giao dịch và danh mục
- Ghi nhận cả **thu nhập** và **chi tiêu**. Loại giao dịch được xác định theo loại danh mục.
- Thêm, sửa và xóa giao dịch; thông tin gồm ngày, số tiền, danh mục, mục đích/ghi chú và nguồn tiền.
- Nguồn tiền hỗ trợ `personal` (cá nhân), `common` (quỹ chung) và `unit` (ngân sách đơn vị). Hai nguồn dùng chung được hiển thị cho mọi thành viên.
- Cảnh báo giao dịch trùng ngày, số tiền, danh mục và nguồn; nguồn cá nhân so sánh cùng người ghi nhận, còn nguồn dùng chung so sánh toàn nguồn. Người dùng có thể kiểm tra rồi xác nhận nếu đây là giao dịch riêng.
- Danh sách giao dịch được phân trang 25 dòng mỗi trang.
- Quản trị viên có thể import tệp `.xlsx` theo mẫu sau bước xem trước (tối đa 8 MB / 5.000 dòng); dòng lỗi và dòng trùng bị bỏ qua, mã giao dịch được CSDL tự tạo. Dữ liệu xem trước hết hạn sau 24 giờ.
- Từ chối số tiền âm, bằng 0, không hợp lệ hoặc vượt giới hạn; ngày và danh mục cũng được kiểm tra phía máy chủ.
- Hỗ trợ lọc lịch sử theo ngày bắt đầu/kết thúc, loại giao dịch, nguồn tiền, danh mục và thành viên (đối với quản trị viên).
- Quản trị viên có thể thêm, sửa, ẩn và xóa danh mục chưa được sử dụng. Danh mục đã gắn với giao dịch không thể xóa cứng để giữ lịch sử; có thể sửa hoặc ẩn. Đổi loại danh mục sẽ ảnh hưởng cách giao dịch cũ được thống kê.

### Hạn mức và cảnh báo
- Hạn mức theo tuần (ISO), tháng hoặc quý.
- Hạn mức cho từng thành viên, quỹ chung hoặc ngân sách đơn vị.
- Tự tính tổng chi trong kỳ và tỷ lệ sử dụng hạn mức; cảnh báo khi đạt từ 80% và khi vượt hạn mức.
- Hạn mức chỉ cộng các giao dịch có danh mục loại `expense`, không cộng thu nhập.

### Báo cáo và xuất dữ liệu
- Xem báo cáo theo ngày, tuần, tháng, năm hoặc khoảng thời gian tùy chọn.
- Tổng hợp tổng thu, tổng chi, chênh lệch thu - chi, chi tiêu theo ngày và theo danh mục.
- Xuất báo cáo giao dịch ra **Excel (`.xlsx`)** hoặc **CSV UTF-8**. File Excel gồm sheet tổng quan và sheet giao dịch.
- Bảng điều khiển hiển thị chỉ số tháng hiện tại, biểu đồ chi tiêu theo ngày, hạn mức đang hiệu lực và các giao dịch gần đây.
- Báo cáo phân trang chi tiết 25 dòng mỗi trang; số liệu tổng hợp và tệp xuất vẫn tính toàn bộ giao dịch theo bộ lọc.

### Audit log và sao lưu
- Nhật ký quản trị ghi nhận thay đổi tài khoản, danh mục, hạn mức, giao dịch, import và sao lưu; không ghi nội dung mật khẩu.
- Quản trị viên tạo và tải bản sao SQLite đã kiểm tra toàn vẹn từ menu **Quản trị → Sao lưu database**. Bản sao cũng được giữ trong `instance/backups/`; khôi phục qua giao diện chưa được hỗ trợ.

### Chạy giao diện offline
- Bootstrap, Bootstrap Icons và Chart.js được đóng gói trong `app/static/vendor/`; giao diện không cần truy cập CDN sau khi cài package Python.

### Sao lưu database
- Quản trị viên có thể tạo bản SQLite từ menu **Quản trị → Sao lưu database**.
- Bản sao được kiểm tra tính toàn vẹn, lưu vào `instance/backups/` trên máy chủ và gửi xuống trình duyệt. Mỗi lần tạo giữ lại một file mới; cần quản lý dung lượng và lưu bản cần giữ ở thiết bị khác.
- Khôi phục từ giao diện chưa được hỗ trợ; hiện cần dừng ứng dụng và khôi phục thủ công.

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
│   ├── backups.py              # Tạo và kiểm tra bản sao lưu SQLite
│   ├── importer.py             # Đọc, kiểm tra và áp dụng import Excel
│   ├── extensions.py           # db, login_manager, csrf
│   ├── models.py               # Role, User, Category, Expense, Budget, AuditLog
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
│   │   └── routes.py           # Tài khoản, danh mục, sao lưu, import và audit log
│   ├── templates/              # Giao diện Jinja2, gồm các trang quản trị danh mục
│   └── static/
│       ├── css/style.css       # CSS tùy chỉnh
│       └── vendor/             # Bootstrap, Bootstrap Icons, Chart.js dùng offline
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
| `source` | String | `personal`, `common` hoặc `unit` |
| `created_at`, `updated_at` | DateTime, bổ sung | Thời điểm tạo / cập nhật |

### `Budget` — hạn mức

| Trường | Kiểu / ràng buộc | Ý nghĩa |
|---|---|---|
| `idBudget` | Integer, PK | Mã hạn mức |
| `idUser` | Integer, FK → `User.idUser`, nullable | Thành viên được áp dụng; `NULL` nếu là hạn mức dùng chung |
| `amountLimit` | Numeric(14,2) | Hạn mức tối đa |
| `month` | Integer, nullable | Tháng hoặc tháng bắt đầu của kỳ |
| `year` | Integer | Năm áp dụng |
| `source` | String, bổ sung | `personal`, `common` hoặc `unit` |
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
AuditLog lưu nhật ký thao tác quản trị, liên kết người thực hiện nếu tài khoản còn tồn tại
```

### `AuditLog` — nhật ký thao tác

| Trường | Ý nghĩa |
|---|---|
| `actor_id`, `actor_name` | Tài khoản thực hiện và tên đăng nhập được chụp lại tại thời điểm thao tác |
| `action` | `create`, `update`, `delete`, `activate`, `deactivate`, `import` hoặc `backup` |
| `entity_type`, `entity_id` | Loại đối tượng và mã đối tượng liên quan |
| `details` | Chi tiết JSON; không lưu giá trị mật khẩu |
| `created_at` | Thời điểm ghi nhật ký |

Bảng này được tạo bổ sung an toàn khi khởi động để hỗ trợ các database cũ; các bảng nghiệp vụ hiện có không bị thay đổi.

Mật khẩu được lưu dưới dạng chuỗi băm. Không lưu dữ liệu đăng nhập thô vào CSDL.

### Mẫu Excel thu thập dữ liệu

Tệp [`data/mau_cau_truc_du_lieu.xlsx`](data/mau_cau_truc_du_lieu.xlsx) có các sheet hướng dẫn, giao dịch mẫu (kèm các dòng trống để điền) và danh mục tham khảo. Quản trị viên có thể nhập sheet “Giao dịch” trực tiếp sau bước xem trước; cần đối chiếu đúng mã thành viên và danh mục trong CSDL. Dữ liệu demo thực sự trong SQLite được tạo bằng `python seed.py`.

## 5. Yêu cầu trước khi cài đặt

- Windows 10/11.
- Python **3.11.x** đã cài đặt và có thể gọi bằng lệnh `py -3.11` hoặc `python`.
- Kết nối Internet ở bước đầu để tải các package Python; các thư viện giao diện đã được đóng gói trong dự án.
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

Mặc định app nghe trên `127.0.0.1:5000`. Muốn truy cập LAN trên Windows, đặt `FLASK_HOST=0.0.0.0` và giới hạn truy cập bằng firewall. Bootstrap, Bootstrap Icons và Chart.js được phục vụ từ `app/static/vendor/`, nên giao diện không cần Internet sau khi package Python đã cài xong.

## 13. Phạm vi và điểm cần phát triển tiếp

- Giao dịch hiện được nhập thủ công; chưa kết nối API ngân hàng/ví điện tử.
- Chưa có ứng dụng điện thoại độc lập hoặc nhận diện hóa đơn qua camera.
- Chưa hỗ trợ đa tiền tệ, hiện mặc định VNĐ.
- Audit log hiện ghi nhận các thao tác quản trị và thay đổi tài chính đã liệt kê; chưa có luồng quên mật khẩu qua email.
- Import hiện hỗ trợ `.xlsx` theo mẫu và giới hạn upload 8 MB / 5.000 dòng; chưa hỗ trợ CSV hoặc ánh xạ cột tùy ý.
- Nguồn `unit` là phạm vi dùng chung trong một CSDL, chưa hỗ trợ nhiều đơn vị độc lập trong cùng hệ thống.
- Khi đổi cấu trúc bảng trong tương lai, nên bổ sung công cụ migration; khi tải ghi đồng thời tăng, cân nhắc PostgreSQL.

## 14. Tài liệu tham khảo kỹ thuật

- Flask: <https://flask.palletsprojects.com/>
- Flask application factories: <https://flask.palletsprojects.com/en/stable/patterns/appfactories/>
- Flask-SQLAlchemy: <https://flask-sqlalchemy.palletsprojects.com/>
- Flask-Login: <https://flask-login.readthedocs.io/>
- Flask-WTF / CSRF: <https://flask-wtf.readthedocs.io/>
- Bootstrap: <https://getbootstrap.com/>
- openpyxl: <https://openpyxl.readthedocs.io/>
