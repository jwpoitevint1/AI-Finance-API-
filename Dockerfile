# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /app

# Install build deps only if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app

# Copy installed packages
COPY --from=builder /install /usr/local

# Copy source code
COPY . .

ENV PORT=8000
EXPOSE 8000

# Adjust entrypoint to match your project layout
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
