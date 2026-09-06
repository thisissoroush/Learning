# Chapter 18 — Deployment

> *"Deployment is where 'it works on my machine' meets reality. Docker makes this process repeatable and reliable."*

---

## 🎯 Core Concept

Professional Django deployment requires: a **production-grade web server** (Gunicorn), **static file serving** (WhiteNoise), **real database** (PostgreSQL on Heroku), and **environment variables** for all secrets. Docker makes this entire process reproducible.

---

## 🏗️ PaaS vs IaaS

```
PaaS (Platform as a Service):        IaaS (Infrastructure as a Service):
─────────────────────────────────────────────────────────────────────
Heroku, Railway, Render               AWS EC2, DigitalOcean Droplets

You provide: code + Dockerfile        You provide: everything from OS up
Provider manages: servers, OS         You manage: servers, OS, scaling

Pros: Fast to start, less ops         Pros: Maximum control, cheaper at scale
Cons: Less control, pricier/unit      Cons: More DevOps knowledge required

Best for: Early-stage projects        Best for: High-scale production
```

---

## 📦 WhiteNoise — Serving Static Files in Production

In production (DEBUG=False), Django won't serve static files. WhiteNoise makes it work without a separate web server:

```
# requirements.txt
whitenoise~=6.0
```

```python
# settings.py
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Right after Security!
    ...
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
```

WhiteNoise:
- Serves compressed static files efficiently
- Adds cache headers automatically
- Works with Gunicorn (no nginx needed for static files)

---

## 🦄 Gunicorn — Production WSGI Server

Django's `runserver` is **only for development**. Gunicorn is the production-grade WSGI server:

```
# requirements.txt
gunicorn~=20.1
```

```bash
# Run with Gunicorn (instead of runserver)
$ gunicorn django_project.wsgi -b 0.0.0.0:$PORT --workers 4
```

```yaml
# docker-compose-prod.yml
services:
  web:
    build: .
    command: gunicorn django_project.wsgi -b 0.0.0.0:$PORT  # Changed!
    environment:
      - PORT=8000
```

### How Many Workers?

```
Rule of thumb: (2 × CPU cores) + 1
2-core server → 5 workers
4-core server → 9 workers
```

---

## 🌐 Deploying to Heroku

### Prerequisites

```bash
# Install Heroku CLI
# Create account at heroku.com

# Login
$ heroku login

# Create app
$ heroku create bookstore-app-name

# Check remote was added
$ git remote -v
```

### Required Files

**Procfile** — tells Heroku how to run your app:
```
web: gunicorn django_project.wsgi --log-file -
```

**runtime.txt** — specifies Python version:
```
python-3.10.4
```

### Environment Variables on Heroku

```bash
# Set all env vars (don't commit .env to Heroku!)
$ heroku config:set DEBUG=False
$ heroku config:set DJANGO_SECRET_KEY=your-production-key
$ heroku config:set ALLOWED_HOSTS=.herokuapp.com

# Heroku automatically adds DATABASE_URL when PostgreSQL is added
$ heroku addons:create heroku-postgresql:hobby-dev
```

### Deploy

```bash
# Push to Heroku (deploys automatically)
$ git push heroku main

# Run migrations on Heroku
$ heroku run python manage.py migrate

# Create superuser on Heroku
$ heroku run python manage.py createsuperuser

# View logs
$ heroku logs --tail
```

---

## 🐳 Production docker-compose.yml

```yaml
# docker-compose-prod.yml
version: "3.9"

services:
  web:
    build: .
    command: gunicorn django_project.wsgi -b 0.0.0.0:8000
    ports:
      - 80:8000
    env_file:
      - .env.prod     # Production env file (never committed)
    depends_on:
      - db

  db:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=yourdbpassword

volumes:
  postgres_data:
```

---

## ⚙️ ALLOWED_HOSTS

```python
# settings.py
# In production, set to your actual domains
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS",
                default=["localhost", "127.0.0.1"])

# For Heroku:
ALLOWED_HOSTS = [".herokuapp.com", "yourdomain.com"]
```

---

## 📊 Production Architecture

![Deployment Architecture](../images/18-deployment.png)

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **Gunicorn** | Replaces Django dev server in production |
| **WhiteNoise** | Serves static files without nginx |
| **Procfile** | Tells Heroku/PaaS how to start your app |
| **ALLOWED_HOSTS** | Set to real domains, never `*` in production |
| **heroku run** | Execute commands on production server |
| **heroku logs --tail** | Real-time production logs |
| **Never use runserver in prod** | It's slow, insecure, single-threaded |

---

*← [Back to Django for Professionals](../README.md)*
