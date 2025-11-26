FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    git gcc libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app code
COPY . .

# Expose port
ENV PORT=8000
EXPOSE 8000

# Launch SGLang server with Qwen model
CMD ["python", "-m", "sglang.launch_server", "--model-path", "Qwen/Qwen2.5-1.8B", "--reasoning-parser", "qwen3"]
