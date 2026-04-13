from flask import (Blueprint, render_template, redirect, url_for,
                   request, session, flash)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.models import User
from app.auth import (generate_totp_secret, get_totp_uri,
                      generate_qr_base64, verify_totp)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        if not username or not password:
            flash('Vui lòng điền đầy đủ thông tin.', 'error')
            return render_template('register.html')

        if len(username) < 3 or len(username) > 30:
            flash('Tên đăng nhập phải từ 3–30 ký tự.', 'error')
            return render_template('register.html')

        if password != confirm:
            flash('Mật khẩu xác nhận không khớp.', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('Mật khẩu phải có ít nhất 6 ký tự.', 'error')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại. Vui lòng chọn tên khác.', 'error')
            return render_template('register.html')

        # Tạo TOTP secret và lưu user mới
        totp_secret = generate_totp_secret()
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            totp_secret=totp_secret,
            is_2fa_setup=False
        )
        db.session.add(user)
        db.session.commit()

        session['setup_2fa_user_id'] = user.id
        flash('Đăng ký thành công! Hãy thiết lập Google Authenticator.', 'success')
        return redirect(url_for('auth.setup_2fa'))

    return render_template('register.html')


@auth_bp.route('/setup-2fa', methods=['GET', 'POST'])
def setup_2fa():
    user_id = session.get('setup_2fa_user_id')
    if not user_id:
        flash('Phiên làm việc hết hạn. Vui lòng đăng ký lại.', 'error')
        return redirect(url_for('auth.register'))

    user = User.query.get(user_id)
    if not user:
        session.pop('setup_2fa_user_id', None)
        return redirect(url_for('auth.register'))

    if request.method == 'POST':
        user.is_2fa_setup = True
        db.session.commit()
        session.pop('setup_2fa_user_id', None)
        flash('Thiết lập 2FA thành công! Bạn có thể đăng nhập.', 'success')
        return redirect(url_for('auth.login'))

    # Tạo QR code Base64
    uri    = get_totp_uri(user.username, user.totp_secret)
    qr_b64 = generate_qr_base64(uri)

    # Format secret key theo nhóm 4 ký tự cho dễ nhập tay
    secret_formatted = ' '.join(
        user.totp_secret[i:i+4]
        for i in range(0, len(user.totp_secret), 4)
    )

    return render_template('setup_2fa.html',
                           username=user.username,
                           totp_secret=user.totp_secret,
                           secret_formatted=secret_formatted,
                           qr_image=qr_b64)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'error')
            return render_template('login.html', step=1)

        if not user.is_2fa_setup:
            # User chưa setup 2FA → chuyển về setup
            session['setup_2fa_user_id'] = user.id
            flash('Tài khoản chưa thiết lập 2FA. Vui lòng quét QR.', 'warning')
            return redirect(url_for('auth.setup_2fa'))

        # Mật khẩu đúng → lưu session tạm, yêu cầu OTP
        session['otp_user_id'] = user.id
        return redirect(url_for('auth.verify_otp'))

    return render_template('login.html', step=1)



# XÁC THỰC OTP 
@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    user_id = session.get('otp_user_id')
    if not user_id:
        flash('Phiên xác thực hết hạn. Vui lòng đăng nhập lại.', 'error')
        return redirect(url_for('auth.login'))

    user = User.query.get(user_id)
    if not user:
        session.pop('otp_user_id', None)
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        # Ghép 6 ô digit
        digits   = [request.form.get(f'd{i}', '') for i in range(1, 7)]
        otp_code = ''.join(digits).strip()

        if not otp_code or len(otp_code) != 6 or not otp_code.isdigit():
            flash('Vui lòng nhập đủ 6 chữ số OTP.', 'error')
            return render_template('login.html', step=2, username=user.username)

        if verify_totp(user.totp_secret, otp_code):
            session.pop('otp_user_id', None)
            login_user(user, remember=False)
            flash(f'Chào mừng trở lại, {user.username}! 🎉', 'success')
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Mã OTP không hợp lệ hoặc đã hết hạn. Thử lại!', 'error')
            return render_template('login.html', step=2, username=user.username)

    return render_template('login.html', step=2, username=user.username)


# QUÊN MẬT KHẨU
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    Trong môi trường Lab: người dùng nhập username + mật khẩu mới.
    Sau khi đặt lại vẫn phải dùng OTP từ Google Authenticator để login.
    """
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        username     = request.form.get('username', '').strip().lower()
        new_password = request.form.get('new_password', '')
        confirm      = request.form.get('confirm_password', '')

        if not username or not new_password:
            flash('Vui lòng điền đầy đủ thông tin.', 'error')
            return render_template('forgot_password.html')

        if new_password != confirm:
            flash('Mật khẩu xác nhận không khớp.', 'error')
            return render_template('forgot_password.html')

        if len(new_password) < 6:
            flash('Mật khẩu phải có ít nhất 6 ký tự.', 'error')
            return render_template('forgot_password.html')

        user = User.query.filter_by(username=username).first()
        if not user:
            # Không tiết lộ user có tồn tại hay không (security best practice)
            flash('Nếu username tồn tại, mật khẩu đã được cập nhật thành công!', 'info')
            return render_template('forgot_password.html')

        # Cập nhật mật khẩu mới
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()

        flash('Mật khẩu đã được đặt lại thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html')


# DASHBOARD
@auth_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)


# ĐĂNG XUẤT
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất thành công.', 'info')
    return redirect(url_for('auth.login'))
