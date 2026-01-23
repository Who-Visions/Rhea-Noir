# --- Stage 1: Build Flutter Web ---
# Use stable channel for maximum reliability
FROM ghcr.io/cirruslabs/flutter:stable AS builder

WORKDIR /src

# Copy the Flutter project
# Copying everything to rule out path issues
COPY . .
WORKDIR /src/rhea_mobile_command

# Clean and Build
# List files to verify context
RUN echo "Current Directory:" && pwd && ls -la
RUN echo "Lib Directory:" && ls -la lib/ || echo "LIB NOT FOUND"

RUN flutter clean
RUN flutter pub get
RUN flutter build web --release --dart-define=BRIDGE_URL=https://rhea-noir-145241643240.us-central1.run.app

# --- Stage 2: Python API + Serving ---
FROM python:3.12-slim

WORKDIR /app

# Install System Dependencies (if needed)
# RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python Application Code
COPY . .

# Copy Built Web Assets from Stage 1
# Locate them at /app/static for FastAPI to serve
COPY --from=builder /src/rhea_mobile_command/build/web /app/static

# Environment Config
ENV PORT=8080
EXPOSE 8080

# Run Uvicorn
CMD ["sh", "-c", "uvicorn rhea_server:app --host 0.0.0.0 --port ${PORT}"]
