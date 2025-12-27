# ---------- builder stage ----------
FROM python:3.12-alpine AS builder

WORKDIR /app

# Build dependencies only
RUN apk add --no-cache --virtual .build-deps \
    gcc musl-dev mariadb-connector-c-dev \
    && apk add --no-cache \
    bzip2-dev libffi-dev openssl-dev zlib-dev

# Copy requirements and install Python packages
COPY requirements.txt .

# Install packages; pymongo will be built from source
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Clean up unnecessary files to reduce layer size
RUN find /install -type d -name "tests" -exec rm -rf {} + \
    && find /install -type d -name "__pycache__" -exec rm -rf {} + \
    && rm -rf /install/*.dist-info/__pycache__

# ---------- runtime stage ----------
FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Runtime libraries only
RUN apk add --no-cache mariadb-connector-c

# Copy Python packages from builder
COPY --from=builder /install /usr/local

# Copy your app code
COPY main.py .

# Run the app
CMD ["python", "main.py"]
