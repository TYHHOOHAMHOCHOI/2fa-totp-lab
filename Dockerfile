# ─── Dockerfile — 2FA TOTP Lab ────────────────────────────────────
# Base image: Python 3.9 slim
# ──────────────────────────────────────────────────────────────────
FROM python:3.9-slim

LABEL maintainer="2FA TOTP Lab" \
      description="Web Demo Xác Thực Đa Nhân Tố — Đồ Án An Toàn Thông Tin"

# Biến môi trường
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

# Tạo non-root user (bảo mật)
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Thư mục làm việc
WORKDIR /app

# Cài dependencies hệ thống (cần cho psycopg2 và Pillow/qrcode)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libzbar0 \
    && rm -rf /var/lib/apt/lists/*

# Cài Python dependencies (layer này được cache nếu requirements không đổi)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Đổi owner
RUN chown -R appuser:appgroup /app
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/')" || exit 1

# Khởi động với Gunicorn (production WSGI server)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "60", "run:app"]
