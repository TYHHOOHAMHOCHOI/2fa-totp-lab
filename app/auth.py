"""
auth.py — TOTP Helper Functions
Các hàm tiện ích liên quan đến xác thực TOTP (Google Authenticator).
"""
import io
import base64

import pyotp
import qrcode
from qrcode.image.pure import PyPNGImage


APP_NAME = "2FA-Lab"


def generate_totp_secret() -> str:
    """Tạo một Base32 secret key ngẫu nhiên."""
    return pyotp.random_base32()


def get_totp_uri(username: str, secret: str) -> str:
    """
    Tạo URI chuẩn để Google Authenticator có thể đọc.
    """
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=username,
        issuer_name=APP_NAME
    )


def generate_qr_base64(uri: str) -> str:
    """
    Tạo ảnh QR Code từ URI và encode thành Base64 để nhúng vào HTML <img>.
    Trả về chuỗi: 'data:image/png;base64,...'
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#1d6ef5", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    b64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{b64_data}"


def verify_totp(secret: str, otp_code: str) -> bool:
    """
    Xác minh mã OTP 6 số.
    valid_window=1 cho phép mã của chu kỳ trước/sau (30s) để tránh lỗi giờ lệch nhau.
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(otp_code, valid_window=1)
