# Key Takeaways — Django for Professionals

> *William S. Vincent — 2022*

---

## 🏆 The One Sentence

> **Professional Django is the same framework, configured correctly: PostgreSQL, Docker, custom User model, environment variables, HTTPS, and a real email service.**

---

## 🐳 Infrastructure

### 1. Docker from Day One
- Virtual envs isolate Python packages; Docker isolates **everything** (OS, DB, services)
- Layer caching: stable deps first (`pip install`), changing code last (`COPY . .`)
- Two files = identical environment: `Dockerfile` + `docker-compose.yml`

### 2. Always PostgreSQL
- Django default SQLite ≠ production PostgreSQL behavior
- Docker service name = hostname: `HOST: "db"` not `"localhost"`

### 3. Environment Variables Are Non-Negotiable
- **Never commit**: `SECRET_KEY`, passwords, API keys to Git
- `.env` locally (gitignored) + `environs[django]` to read them in settings

---

## 👤 User Model

### 4. Custom User Model: Do This First
```python
# Before ANY migration:
class CustomUser(AbstractUser): pass
AUTH_USER_MODEL = "accounts.CustomUser"
```
**Missing this = pain forever.** Always `get_user_model()`, never import User directly.

---

## 🔐 Authentication & Permissions

### 5. django-allauth for Production Auth
- Email-only login, verification, social auth — minimal code
- `ACCOUNT_AUTHENTICATION_METHOD = "email"` — professionals use email

### 6. Three Permission Levels
```
LoginRequiredMixin     → Is user logged in?
PermissionRequiredMixin → Does user have "books.add_book"?
get_object() override  → Does user own THIS specific object?
```

---

## 🗃️ Models

### 7. Use UUIDs for Public-Facing PKs
```python
id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
```
Integers reveal count and enable easy enumeration.

### 8. Always Define get_absolute_url()
```python
def get_absolute_url(self):
    return reverse("book_detail", args=[str(self.id)])
```

---

## 🧪 Testing

### 9. The 5-Test Pattern for Every View
1. URL returns 200 status  2. Named URL works  3. Correct template
4. Contains expected text  5. Resolves to correct view class

### 10. Test Both Auth States
```python
# Logged in → 200; Logged out → 302 (redirect to login)
```

### 11. setUpTestData vs setUp
`setUpTestData` runs ONCE per class (fast); `setUp` runs before each test (slow).

---

## ⚡ Performance

### 12. Fix N+1 Queries
```python
# select_related for FK/OneToOne (JOIN):
Review.objects.select_related("book", "author").all()

# prefetch_related for reverse FK/M2M (2 queries):
Book.objects.prefetch_related("reviews").all()
```

### 13. Measure Before Optimizing
Use `django-debug-toolbar` to find actual bottlenecks. Never guess.

---

## 🔒 Security

### 14. Run Deployment Checklist
```bash
$ python manage.py check --deploy   # Fix every warning
```

### 15. Production Security Must-Haves
```python
DEBUG = False
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"
```

---

## 🚀 Deployment

### 16. Gunicorn + WhiteNoise
```python
# Production server (NOT runserver):
# gunicorn django_project.wsgi --workers 4

# Static files middleware:
MIDDLEWARE = ["..SecurityMiddleware", "whitenoise.middleware.WhiteNoiseMiddleware", ...]
```

### 17. The Production Checklist
```
☐ DEBUG = False        ☐ PostgreSQL (not SQLite)
☐ SECRET_KEY from env  ☐ Gunicorn (not runserver)
☐ ALLOWED_HOSTS set    ☐ WhiteNoise or S3 for static
☐ HTTPS configured     ☐ Email service configured
☐ check --deploy passes
```

---

## 📐 Professional Django Stack

```
Internet → HTTPS → Heroku → Gunicorn → Django
                                          ├── WhiteNoise (static files)
                                          ├── PostgreSQL (database)
                                          └── S3 (media files)
```

---

*"The difference between a toy app and a professional app is configuration, testing, and deployment."*
