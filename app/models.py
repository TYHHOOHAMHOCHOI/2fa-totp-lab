from flask_login import UserMixin
from app import db


class User(UserMixin, db.Model):
    """Bảng người dùng — lưu thông tin xác thực và TOTP secret."""

    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    totp_secret   = db.Column(db.String(64), nullable=False)
    is_2fa_setup  = db.Column(db.Boolean, default=False, nullable=False)
    
    # Các cột hỗ trợ chống Replay Attack
    last_used_totp      = db.Column(db.String(6), nullable=True)
    last_totp_timestamp = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<User {self.username} | 2FA: {self.is_2fa_setup}>'
