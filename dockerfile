# Stage 1: Install dependencies
FROM python:3.12-slim AS builder
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime container
FROM python:3.12-slim
WORKDIR /app

COPY --from=builder /usr/local /usr/local
COPY . .

ENV DJANGO_SETTINGS_MODULE=urlshortener.settings
EXPOSE 8080

CMD ["gunicorn", "urlshortener.wsgi:application", "--bind", "0.0.0.0:8080"]