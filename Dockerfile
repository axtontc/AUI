# Multi-stage production-ready Dockerfile for GUI-enabled AUI automation
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Install system GUI dependencies for Xvfb, Playwright, and PyAutoGUI
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    xauth \
    xdotool \
    scrot \
    python3-tk \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy python dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Install Playwright browser binaries with their system dependencies
RUN playwright install --with-deps chromium

# Copy application files
COPY . .

# Set up virtual display environment variable for Xvfb
ENV DISPLAY=:99
ENV PYTHONUNBUFFERED=1

# Expose OTEL grpc default port in case we run a collector inside
EXPOSE 4317

# Start Xvfb virtual frame buffer and run the application
CMD Xvfb :99 -screen 0 1280x1024x24 & pytest tests/
