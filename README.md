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
>
> ```bash
> docker-compose down          # Tắt, giữ data
> docker-compose down -v       # Tắt và xóa database
> ```

---

## 📋 Luồng Sử Dụng

```
1. Đăng ký    → http://localhost:8080/register
2. Quét QR    → http://localhost:8080/setup-2fa  (dùng Google Authenticator)
3. Đăng nhập  → http://localhost:8080/login      (nhập pass → nhập mã OTP 6 số)
4. Dashboard  → http://localhost:8080/dashboard
5. Quên MK    → http://localhost:8080/forgot-password
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
