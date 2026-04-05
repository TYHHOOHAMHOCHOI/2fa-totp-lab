# 2FA TOTP Lab 🔐

**Web Demo Xác Thực Đa Nhân Tố (2FA/TOTP)** — Đồ Án An Toàn Thông Tin

Minh họa việc tích hợp **Google Authenticator** vào ứng dụng Web bằng Python Flask + PostgreSQL + Docker.

---

## 🚀 Khởi Chạy Nhanh

### Yêu cầu
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) đang chạy
- Port `8080` và `5433` chưa bị chiếm

### Chạy dự án

```bash
# 1. Vào thư mục dự án
cd 2fa-totp-lab

# 2. Build và khởi động (lần đầu ~2-3 phút)
docker-compose up --build

# 3. Truy cập trên trình duyệt
# http://localhost:8080
```

> **Tắt hệ thống:**
> ```bash
> docker-compose down          # Tắt, giữ data
> docker-compose down -v       # Tắt và xóa database
> ```

---

## 📋 Luồng Sử Dụng (Test Flow)

```
1. Đăng ký    → http://localhost:8080/register
2. Quét QR    → http://localhost:8080/setup-2fa  (dùng Google Authenticator)
3. Đăng nhập  → http://localhost:8080/login      (nhập pass → nhập mã OTP 6 số)
4. Dashboard  → http://localhost:8080/dashboard
5. Quên MK    → http://localhost:8080/forgot-password
```

---

## 🏗️ Cấu Trúc Dự Án

```
2fa-totp-lab/
├── app/
│   ├── __init__.py         # Flask app factory
│   ├── models.py           # SQLAlchemy User model
│   ├── auth.py             # TOTP helpers (pyotp, qrcode)
│   ├── routes.py           # 7 routes (register, setup-2fa, login, verify-otp,
│   │                       #           forgot-password, dashboard, logout)
│   ├── static/
│   │   └── style.css       # CSS "Digital Vault" (trắng + xanh #1d6ef5)
│   └── templates/
│       ├── base.html       # Layout chung
│       ├── register.html   # Đăng ký
│       ├── setup_2fa.html  # Quét QR Code
│       ├── login.html      # Đăng nhập 2 bước
│       ├── forgot_password.html  # Quên mật khẩu
│       └── dashboard.html  # Trang chủ sau login
├── run.py                  # Entry point
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker image (python:3.9-slim)
├── docker-compose.yml      # 2 services: db (PostgreSQL) + web (Flask)
├── .env                    # Environment variables
└── README.md
```

---

## 🔌 Các API Endpoints

| Method | Route | Chức năng |
|--------|-------|-----------|
| GET/POST | `/register` | Đăng ký tài khoản mới |
| GET/POST | `/setup-2fa` | Hiển thị QR + xác nhận |
| GET/POST | `/login` | Đăng nhập bước 1 (pass) |
| GET/POST | `/verify-otp` | Đăng nhập bước 2 (OTP) |
| GET/POST | `/forgot-password` | **Quên mật khẩu** |
| GET | `/dashboard` | Trang chủ (cần login) |
| GET | `/logout` | Đăng xuất |

---

## 🗄️ Cơ Sở Dữ Liệu

Bảng `users`:

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `id` | SERIAL PK | Auto-increment |
| `username` | VARCHAR(80) UNIQUE | Tên đăng nhập |
| `password_hash` | VARCHAR(255) | Bcrypt hash |
| `totp_secret` | VARCHAR(64) | Base32 TOTP secret |
| `is_2fa_setup` | BOOLEAN | Đã quét QR chưa |

---

## 🛠️ Tech Stack

| Layer | Công nghệ |
|-------|-----------|
| **UI** | HTML/CSS (Jinja2 templates) — Design "Digital Vault" |
| **Backend** | Python 3.9 + Flask + Flask-Login |
| **Database** | PostgreSQL 13 |
| **TOTP** | `pyotp` (RFC 6238) + `qrcode` + `Pillow` |
| **Security** | `werkzeug.security` (bcrypt hash) |
| **Container** | Docker + Docker Compose |
| **WSGI** | Gunicorn |

---

## 🔐 Giải Thích Bảo Mật

### Xác thực TOTP
```
User secret: ABCDEFGHIJKLMNOP (Base32)
├── Google Authenticator lưu secret
├── Mỗi 30 giây: OTP = HMAC-SHA1(secret, timestamp/30) % 10^6
└── Server dùng pyotp.TOTP(secret).verify(otp, valid_window=1)
```

### Quên Mật Khẩu (Lab Mode)
```
⚠️ Môi trường Lab: Không cần email/SMS OTP
   → Nhập username + mật khẩu mới → Hash bcrypt → Cập nhật DB
   → Vẫn cần mã TOTP từ Google Authenticator khi đăng nhập lại!
```

---

## 📸 Stitch MCP UI Screens

Giao diện được thiết kế bằng **Stitch MCP** (Google AI):

- Project ID: `3939806826634478629`
- Screen 1 (Register): `0bef4f45f0d2454a8f75ffd1bbdc7629`
- Screen 2 (Setup 2FA): `cf7a678f06ee45b18a41cd5b5ea82da5`
- Screen 3 (Login): `e288265fd0cd42c29a8390fc5cf2081a`
- Screen 4 (Forgot PW): `f32ed216b5f94cf794e18f542a9ff0a9`
