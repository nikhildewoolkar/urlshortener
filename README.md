# 🔗 URL Shortener with Django, PostgreSQL, Redis & Docker

A scalable URL Shortener service built using:
- **Django + Django REST Framework**
- **PostgreSQL** (persistent storage)
- **Redis** (caching for fast redirects)
- **JWT Authentication** (secure login/API access)
- **Docker + Docker Compose** (isolated environment)

---

## 🚀 Features

| Feature | Status |
|--------|:-----:|
| User Registration & Login (JWT) | ✅ |
| URL Shortening | ✅ |
| Rate Limiting | ✅ |
| Redis Caching | ✅ |
| URL Redirect UI | ✅ |
| Admin Panel | ✅ |
| Dockerized Infra | 🚀 |

---

## 🛠 Tech Stack

| Component | Technology |
|----------|------------|
| Backend | Django, DRF |
| Auth | JWT (SimpleJWT) |
| Cache | Redis |
| Database | PostgreSQL |
| Deployment | Docker, Gunicorn |

---

## 📦 Installation

### 🔹 Clone Repository
```bash
git clone https://github.com/nikhildewoolkar/urlshortener
cd urlshortener
🐳 Run Using Docker
bash
Copy code
docker-compose up --build -d
Start fresh (recommended while debugging)
bash
Copy code
docker-compose down -v
docker-compose up --build -d
🧬 Apply Migrations Inside Docker
bash
Copy code
docker-compose exec web python manage.py migrate
🧑‍💼 Create Admin User
bash
Copy code
docker-compose exec web python manage.py createsuperuser
Admin URL:
👉 http://localhost:8080/admin/

🌍 API Endpoints
Method	Endpoint	Description	Auth
POST	/api/register/	Register new user	❌
POST	/api/token/	Login (get JWT)	❌
POST	/api/token/refresh/	Refresh token	✔️
POST	/api/shorten/	Create short URL	✔️
GET	/<short_code>/	Redirect to full URL	❌
GET	/api/urls/	List user URLs	✔️

🧪 Test with cURL
bash
Copy code
curl -X POST http://localhost:8080/api/shorten/ \
     -H "Authorization: Bearer <TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"original_url": "https://google.com"}'
🔧 ENV Configuration (.env.docker)
ini
Copy code
SECRET_KEY=your-secret-key
DEBUG=true
POSTGRES_DB=urlshortener
POSTGRES_USER=postgres
POSTGRES_PASSWORD=123
POSTGRES_HOST=db
POSTGRES_PORT=5432
REDIS_URL=redis://redis:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
🗄 PGAdmin (Optional)
Open → http://localhost:5050/

Field	Value
Host	db
User	postgres
Password	123
DB Name	urlshortener

📊 Architecture
pgsql
Copy code
User → Django API → Redis Cache → PostgreSQL
                 ↓ (cache miss)
            Redirect Service
✨ Future Enhancements
Analytics (click counts, timestamp)

Custom short codes

Frontend UI

Expiry feature

📝 License
MIT License © 2025 — Nikhil Dewoolkar

❤️ Contribute
Pull requests are welcome!
If you like this project ⭐ star the repo!

yaml
Copy code

---

### 👍 Ready to push!

If you want, I can:
✓ Add GitHub badges  
✓ Add beautiful diagram images  
✓ Add a full Postman collection  
✓ Rewrite in super-clean professional English

Would you like me to **auto-commit + push** this README to your GitHub repo? (You can provide permission token or I can guide you step-by-step.)
