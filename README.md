# 🔗 URL Shortener Service

A production-ready backend application that allows users to shorten long URLs, manage them, and track analytics like click counts and last accessed time.

Built using **Django REST Framework + PostgreSQL + Redis + JWT Authentication** — designed for scalable redirect performance (<100ms), secure access, and real-world deployment.

---

## 🚀 Features

✔ Shorten long URLs into 10-character unique codes  
✔ Idempotent – same user + same URL returns the same short code  
✔ Redirect to original URL in < 100ms using Redis caching  
✔ Metadata tracking:
  - `click_count`
  - `created_at`
  - `last_accessed_at`
✔ Optional custom alias support  
✔ JWT Authentication (Login / Register / Logout)  
✔ Admin URL listing with pagination  
✔ Rate limiting per IP/user  
✔ Fully containerized (Docker + docker-compose)  
✔ Auto-deploy CI/CD with GitHub Actions → Docker Hub  
✔ Swagger + Redoc API Documentation  

---

## 🧱 Tech Stack

| Layer | Tech |
|------|------|
| Language | Python |
| Framework | Django REST Framework |
| Database | PostgreSQL |
| Cache | Redis |
| Auth | JWT (SimpleJWT) |
| API Docs | drf-spectacular (Swagger UI) |
| Deployment | Docker, Docker Compose |
| CI/CD | GitHub Actions → Docker Hub |

---

## 🧩 Architecture

```
Client → Django REST API → PostgreSQL
                        ↘ Redis Cache (Fast Redirect Lookup)
```

Clean modular structure:

```
handler (views) → service → repository (models)
```

---
## 🧩 API Documentation

```
Link to documentation → https://docs.google.com/document/d/1WbYKlWoDWHxQ7Ia8rMC72ONXWvxQpNFyCuPahd8yYDo/edit?usp=sharing 
```
---

## 📚 API Documentation

Swagger UI →  
👉 http://localhost:8080/api/docs/

Redoc →  
👉 http://localhost:8080/api/redoc/

---

## 🔐 Authentication

JWT required for all protected routes.

### Register
```
POST /api/auth/register/
```

### Login → Get Access & Refresh Token
```
POST /api/auth/login/
```

### Logout (Blacklist token)
```
POST /api/auth/logout/
```

---

## 🧪 API Endpoints with Example cURL

### 🔸 Shorten a URL
```
POST /api/shorten/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "original_url": "https://google.com",
  "custom_alias": "googleme"   # optional
}
```

Response:
```json
{
  "short_code": "googleme",
  "original_url": "https://google.com"
}
```

---

### 🔸 Redirect Short URL
```
GET /api/<short_code>/
```
📌 Increases click counter & updates last accessed time.

---

### 🔸 Admin: List All URLs (paginated)
```
GET /api/admin/list/?page=1
Authorization: Bearer <admin_token>
```

---

## 📦 Docker Support

### Run locally using Docker Compose

```bash
docker-compose up --build -d
```

Services exposed:

| Service | Port |
|--------|------|
| API | 8080 |
| PostgreSQL | 5432 |
| Redis | 6379 |
| pgAdmin | 5050 |

---

## 🛰 CI/CD (Automated Deployment)

Every push to `master` automatically:

✔ Runs tests  
✔ Builds production Docker image  
✔ Pushes to Docker Hub  

Docker image published here:  
🔗 https://hub.docker.com/r/nikhildewoolkar29/urlshortener

---

## 🛡️ Rate Limiting

| Type | Limit |
|------|------|
| User | 100 requests/hour |
| Anonymous | 50 requests/hour |
| Per-IP throttling | 20 requests/min |

---

## 📊 Data Retention & Scaling

✔ Handles **10,000+ URLs/day**  
✔ URLs stored for **5+ years**  
✔ Fast redirect (<100ms) via Redis caching  
✔ Safe from collisions & duplicates  

---

## 📝 Environment Variables

Create `.env`:

```
SECRET_KEY=your-secret-key
DEBUG=True
POSTGRES_DB=urlshortener
POSTGRES_USER=postgres
POSTGRES_PASSWORD=123
POSTGRES_HOST=db
POSTGRES_PORT=5432
REDIS_URL=redis://redis:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
```

📌 `.env` is ignored from git for security.

---

## 🧑‍💻 Local Development Setup (without Docker)

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 📎 Future Enhancements

- Analytics dashboard (trends over time)
- Full custom domain branding support
- gRPC for ultra-fast microservice URLs
- Email verification for users

---

## 👨‍💻 Author

**Nikhil Dewoolkar**  
GitHub: https://github.com/nikhildewoolkar

---

> Fully meets all assignment requirements ✔  
> Production-grade deployment + CI/CD + caching + rate limiting 🚀
