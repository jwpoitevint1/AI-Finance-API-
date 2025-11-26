FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y gcc libffi-dev git curl
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .
ENV PORT=8000
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
