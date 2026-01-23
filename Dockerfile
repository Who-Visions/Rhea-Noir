# --- Stage 1: Build Flutter Web ---
# Use an official Flutter image for building
FROM ghcr.io/cirruslabs/flutter:3.27.1 AS builder

WORKDIR /src

# Copy the Flutter project
COPY rhea_mobile_command/ ./rhea_mobile_command/
WORKDIR /src/rhea_mobile_command

# Build for Web
# We inject the BRIDGE_URL to point to the origin (relative or absolute)
# Since it's served from same domain, relative or default is fine.
# We hardcode the production URL as default fallback.
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
