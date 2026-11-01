# Cài Python 3.11 trên Raspberry Pi OS / Debian 13 Trixie

Dự án này cần Python 3.11. Trên Debian 13 Trixie, Python mặc định của hệ thống là 3.13, và gói `python3-venv` cũng đi theo phiên bản Python 3.13 mặc định đó. Vì vậy, cách ổn định nhất là cài một bản Python 3.11 riêng, rồi tạo virtual environment của dự án bằng đúng bản đó.

## Cách khuyên dùng: build CPython 3.11 từ source

### 1) Kiểm tra hiện trạng

```bash
python3 --version
python3.11 --version
```

Nếu `python3.11` chưa có, tiếp tục các bước bên dưới.

### 2) Cài các gói cần thiết để build

```bash
sudo apt update
sudo apt install -y \
    build-essential \
    wget \
    ca-certificates \
    libssl-dev \
    zlib1g-dev \
    libncursesw5-dev \
    libreadline-dev \
    libsqlite3-dev \
    libgdbm-dev \
    libbz2-dev \
    libexpat1-dev \
    liblzma-dev \
    tk-dev \
    uuid-dev
```

### 3) Tải và biên dịch Python 3.11

```bash
cd /tmp
PYVER=3.11.18
wget https://www.python.org/ftp/python/${PYVER}/Python-${PYVER}.tgz
tar -xf Python-${PYVER}.tgz
cd Python-${PYVER}
./configure --prefix=/opt/python-3.11
make -j1
sudo make altinstall
```

`make altinstall` là lựa chọn an toàn vì không ghi đè lên `python3` của hệ thống.
Pi Zero 2 W có khoảng 512 MB RAM và đang dùng zram; build một job (`-j1`) để giảm áp lực bộ nhớ. Không cài `dphys-swapfile` theo hướng dẫn cũ và không thay Python hệ thống của Trixie.

### 4) Kiểm tra bản cài đặt

```bash
/opt/python-3.11/bin/python3.11 --version
```

Nếu lệnh trên in ra `Python 3.11.x` là đã ổn.

### 5) Tạo virtual environment cho dự án

```bash
cd /duong/dan/den/thu_muc_du_an
/opt/python-3.11/bin/python3.11 -m venv .venv
.venv/bin/python -m pip install --upgrade pip wheel
.venv/bin/python -m pip install -r requirements.txt
```

### 6) Chạy ứng dụng trên Raspberry Pi

`requirements.txt` cài Waitress cùng các thư viện ứng dụng. Khi `FLASK_DEBUG=0` (mặc định), `run.py` dùng Waitress; launcher Linux đặt `FLASK_DEBUG=0`, bind `0.0.0.0:5000` để truy cập trong LAN.

Bootstrap, Bootstrap Icons và Chart.js được đóng gói trong `app/static/vendor/`, nên giao diện không cần truy cập CDN. Chỉ cần Internet lúc đầu để tải package Python; sau khi cài `requirements.txt`, ứng dụng có thể chạy trong mạng nội bộ không có Internet.

```bash
FLASK_HOST=0.0.0.0 FLASK_PORT=5000 FLASK_DEBUG=0 .venv/bin/python run.py
```

Hoặc dùng script sẵn có:

```bash
./run_admin.sh
./run_demo.sh
```

`run_admin.sh` chỉ khởi tạo admin nếu database chưa có dữ liệu; lần chạy sau sẽ giữ nguyên database. `run_demo.sh` xóa database demo cũ chỉ sau khi bạn xác nhận. Có thể sao lưu bằng `python backup_db.py` hoặc vào **Quản trị → Sao lưu database**; bản sao lưu nằm trong `instance/backups/`. Khôi phục qua giao diện chưa được hỗ trợ.

## Gợi ý nhanh nếu muốn làm lại từ đầu

```bash
rm -rf .venv
/opt/python-3.11/bin/python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Lưu ý

- Không nên thay thế Python hệ thống của Trixie bằng Python 3.11.
- Với dự án này, hãy luôn tạo `.venv` bằng đúng `python3.11`.
- Nếu lệnh `python3.11` không có sẵn sau khi build, kiểm tra lại bước `sudo make altinstall` và đường dẫn `/opt/python-3.11/bin`.
