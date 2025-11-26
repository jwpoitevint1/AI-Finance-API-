FROM python:3.11-slim

WORKDIR /app

# Install only the essentials (no need for full build toolchain now)
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8000
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
