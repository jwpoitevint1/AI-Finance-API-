FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for building wheels
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    make \
    libffi-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway sets $PORT automatically
ENV PORT=8000
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
