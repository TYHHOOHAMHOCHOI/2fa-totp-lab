# Tổng quan Dự án: 2FA TOTP Lab

Tài liệu này cung cấp cái nhìn tổng quát về chức năng của từng file trong dự án mà không đi sâu vào chi tiết mã nguồn.

## 📁 Thư mục gốc (Root)

*   **`.dockerignore`**: Danh sách các file và thư mục bị bỏ qua khi xây dựng Docker Image để tối ưu dung lượng và bảo mật.
*   **`.env`**: Lưu trữ các biến môi trường cấu hình dự án như Secret Key của Flask và thông tin kết nối Cơ sở dữ liệu.
*   **`Dockerfile`**: Chứa các chỉ dẫn để đóng gói ứng dụng Flask vào một Container, bao gồm cài đặt môi trường Python và các thư viện cần thiết.
*   **`README.md`**: Tài liệu hướng dẫn sử dụng, cài đặt và vận hành dự án dành cho người dùng.
*   **`docker-compose.yml`**: File cấu hình để chạy đồng thời nhiều Container (Ứng dụng Flask và Cơ sở dữ liệu PostgreSQL) một cách tự động.
*   **`requirements.txt`**: Danh sách tất cả các thư viện Python mà dự án sử dụng (Flask, SQLAlchemy, PyOTP, v.v.).
*   **`run.py`**: Điểm khởi đầu của ứng dụng. File này gọi hàm khởi tạo ứng dụng và bắt đầu chạy Web Server.

## 📁 Thư mục `app/` (Mã nguồn chính)

*   **`__init__.py`**: Thiết lập ứng dụng Flask (App Factory), cấu hình các tiện ích mở rộng (Database, Login Manager) và đăng ký các luồng xử lý (Blueprints).
*   **`auth.py`**: Chứa logic xử lý chuyên sâu về bảo mật 2FA, bao gồm tạo mã bí mật TOTP, tạo mã QR Code và kiểm tra tính hợp lệ của mã OTP.
*   **`models.py`**: Định nghĩa cấu trúc bảng trong Cơ sở dữ liệu (Database Schema), cụ thể là bảng người dùng để lưu thông tin đăng nhập và khóa bí mật 2FA.
*   **`routes.py`**: Xử lý các đường dẫn URL của trang web. Đây là nơi điều hướng người dùng qua các chức năng đăng ký, đăng nhập, thiết lập 2FA, đổi mật khẩu và trang Dashboard.

## 📁 Thư mục `app/static/` (Tài nguyên tĩnh)

*   **`style.css`**: File định dạng giao diện cho toàn bộ trang web (màu sắc, bố cục, hiệu ứng), giúp ứng dụng trông hiện đại và chuyên nghiệp.

## 📁 Thư mục `app/templates/` (Giao diện HTML)

*   **`base.html`**: Khung cơ bản của trang web, chứa các thành phần chung như Header, Footer và các tệp CSS/JS dùng chung cho tất cả các trang khác.
*   **`dashboard.html`**: Giao diện hiển thị sau khi người dùng đăng nhập thành công.
*   **`forgot_password.html`**: Giao diện cho phép người dùng đặt lại mật khẩu trong môi trường Lab.
*   **`login.html`**: Giao diện đăng nhập, bao gồm cả bước nhập tên/mật khẩu và bước nhập mã OTP.
*   **`register.html`**: Giao diện đăng ký tài khoản mới.
*   **`setup_2fa.html`**: Giao diện hướng dẫn người dùng thiết lập 2FA (hiển thị mã QR và khóa bí mật để quét bằng Google Authenticator).
