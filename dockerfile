# Stage 1: Install dependencies
FROM python:3.12-alpine AS builder

# Dockerfile for Alpine-based image

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apk add --no-cache build-base postgresql-dev

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt

# Runtime image
FROM python:3.12-alpine

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apk add --no-cache postgresql-libs

COPY --from=builder /install /usr/local
COPY . .

EXPOSE 8080

CMD ["gunicorn", "urlshortener.wsgi:application", "--bind", "0.0.0.0:8080", "--workers", "3"]
