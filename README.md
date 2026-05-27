# 📚 Smart Library API

A production-ready Library Management REST API built with Django REST Framework, featuring JWT authentication, async task processing, and automated overdue notifications.

## 🚀 Features

- **JWT Authentication** — Secure login with access/refresh token rotation and blacklisting
- **Book Management** — Browse books with pagination, filtering by genre and author
- **Borrow & Return System** — Race-condition-safe borrowing using database-level row locking (`select_for_update`)
- **Automated Overdue Notifications** — Celery Beat runs a daily task at midnight to detect overdue books and email users
- **Async Email Pipeline** — Welcome emails and borrow confirmations sent asynchronously via Celery
- **API Documentation** — Interactive Swagger UI and ReDoc available out of the box
- **Rate Throttling** — Per-user and per-endpoint throttling to prevent abuse
- **Admin Panel** — Fully configured Django admin for managing books, users, and borrow records
- **Test Suite** — Unit tests covering registration, login, borrowing, and edge cases (no copies, wrong credentials, unauthenticated access)

### 🔬 Planned: Semantic Book Search (RAG)
Planned feature to allow users to search books by plot description using vector embeddings (transformers + similarity matching). Deprioritized due to model loading time — will be added as an async background process.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 6.0, Django REST Framework |
| Auth | JWT (SimpleJWT) — access 15min, refresh 7 days |
| Database | PostgreSQL |
| Async Tasks | Celery + Redis |
| Task Scheduling | Celery Beat (cron) |
| API Docs | drf-spectacular (Swagger + ReDoc) |
| Email | SMTP with HTML templates |

---

## 📡 API Endpoints

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/register/` | Register a new user | No |
| POST | `/api/login/` | Login and get JWT tokens | No |
| POST | `/api/token/refresh/` | Refresh access token | No |
| GET | `/api/books/` | List all available books (paginated) | No |
| POST | `/api/books/borrow/<book_id>/` | Borrow a book | Yes |
| POST | `/api/books/return/<borrow_id>/` | Return a borrowed book | Yes |
| GET | `/api/borrowed_books/` | View your borrow history | Yes |
| GET | `/api/docs/` | Swagger UI | No |
| GET | `/api/redoc/` | ReDoc UI | No |

---

## ⚙️ Local Setup

### Prerequisites
- Python 3.10+
- PostgreSQL
- Redis

### 1. Clone the repository
```bash
git clone https://github.com/Vallal123/library_management.git
cd library_management
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
```
Fill in your `.env` file:
```env
SECRET_KEY=your-secret-key

# Database
ENGINE=django.db.backends.postgresql
NAME=library_db
USER=your_db_user
PASS=your_db_password
HOST=localhost
PORT=5432

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your@email.com
EMAIL_HOST_PASSWORD=your_app_password
```

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Create superuser
```bash
python manage.py createsuperuser
```

### 7. Start Redis (required for Celery)
```bash
redis-server
```

### 8. Start Celery worker (new terminal)
```bash
celery -A config worker --loglevel=info
```

### 9. Start Celery Beat scheduler (new terminal)
```bash
celery -A config beat --loglevel=info
```

### 10. Run the development server
```bash
python manage.py runserver
```

Visit `http://localhost:8000/api/docs/` for the interactive API documentation.

---

## 🧪 Running Tests

```bash
python manage.py test
```

Tests cover:
- User registration (success, duplicate email, missing fields)
- Login (valid credentials, invalid credentials)
- Book listing (pagination, active/inactive filtering)
- Borrowing (success, no copies available, unauthenticated)

---

## 🏗️ Project Structure

```
library_management/
├── config/
│   ├── settings.py       # Django settings with Celery, JWT, throttling config
│   ├── celery.py         # Celery app setup
│   └── urls.py           # Root URL configuration
├── library/
│   ├── models.py         # User, Book, Author, Genre, BorrowRecord
│   ├── views.py          # API views
│   ├── serializers.py    # DRF serializers
│   ├── tasks.py          # Celery async tasks
│   ├── email_services.py # Email sending service
│   ├── permissions.py    # Custom DRF permissions
│   ├── pagination.py     # Custom pagination
│   ├── admin.py          # Django admin configuration
│   ├── tests.py          # Unit tests
│   └── urls.py           # App URL patterns
├── templates/
│   └── email/            # HTML email templates
├── .env.example
├── requirements.txt
└── manage.py
```

---

## 🔒 Security Highlights

- All secrets loaded from environment variables via `python-dotenv`
- JWT tokens with short-lived access (15 min) and rotating refresh tokens
- Rate limiting on auth endpoints (5/min) to prevent brute force
- Database-level constraints prevent negative or inconsistent book counts
- `select_for_update()` prevents race conditions during concurrent borrows

---

## 👨‍💻 Author

**Vallal** — [github.com/Vallal123](https://github.com/Vallal123)