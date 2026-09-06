# Chapter 9 — Environment Variables

> *"Never store secrets in source code. Environment variables are the professional way to handle configuration that changes between environments."*

---

## 🎯 Core Concept

**Configuration should be stored in the environment, not in code.** This is Principle #3 of the [12-Factor App](https://12factor.net/config). Secrets like `SECRET_KEY`, database passwords, and API keys must never be committed to Git.

---

## ❌ The Wrong Way (What Beginners Do)

```python
# settings.py — NEVER DO THIS
SECRET_KEY = "django-insecure-abc123xyz"       # Committed to Git!
DEBUG = True
DATABASES = {
    "default": {
        "PASSWORD": "mypassword123",           # Exposed in repo!
    }
}
SENDGRID_API_KEY = "SG.abc123xyz"             # API key in code!
```

If this code is on GitHub (even private), your secrets are at risk.

---

## ✅ The Right Way — Environment Variables

```
Development (.env file, NOT committed):        Production (server env vars):
SECRET_KEY=abc123xyz                    →      $ heroku config:set SECRET_KEY=abc123xyz
DEBUG=True                              →      $ heroku config:set DEBUG=False
DATABASE_URL=postgres://...             →      Set by Heroku automatically
SENDGRID_API_KEY=SG.xxx                →      $ heroku config:set SENDGRID_API_KEY=...
```

---

## 📦 environs[django]

The `environs` library makes reading environment variables clean and type-safe:

```
# requirements.txt
environs[django]~=9.5
```

```python
# settings.py
from environs import Env

env = Env()
env.read_env()  # Read .env file in development

# Now read variables with type casting
SECRET_KEY = env("SECRET_KEY")             # str
DEBUG = env.bool("DEBUG", default=False)   # bool (safe default)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")  # list

# Database from DATABASE_URL environment variable
DATABASES = {"default": env.dj_db_url("DATABASE_URL")}
```

---

## 📄 The .env File — For Local Development Only

```bash
# .env (NEVER commit this!)
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://postgres@db/postgres
```

**Always add `.env` to `.gitignore`:**

```gitignore
# .gitignore
.env
```

---

## 🔑 The SECRET_KEY

Django uses `SECRET_KEY` to sign cookies, sessions, and CSRF tokens. If it's exposed:

```
Attacker knows your SECRET_KEY →
  - Can forge session cookies (log in as any user)
  - Can forge CSRF tokens
  - Can decrypt signed data

Always:
  - Generate a new key for each environment
  - Never commit it to Git
  - Rotate it if ever exposed (invalidates all sessions)
```

### Generating a New Secret Key

```python
# Generate in Python shell:
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

---

## ⚙️ Complete Settings Pattern

```python
# django_project/settings.py
from pathlib import Path
from environs import Env

env = Env()
env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent

# From environment
SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# Database from single DATABASE_URL env var
DATABASES = {"default": env.dj_db_url("DATABASE_URL",
             default="postgres://postgres@db/postgres")}
```

---

## 🐳 Environment Variables in Docker

```yaml
# docker-compose.yml
version: "3.9"

services:
  web:
    build: .
    command: python /code/manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/code
    ports:
      - 8000:8000
    env_file:        # Load from .env file automatically
      - .env
    depends_on:
      - db

  db:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - "POSTGRES_HOST_AUTH_METHOD=trust"

volumes:
  postgres_data:
```

---

## 🚨 Handling Missing Variables

```python
# settings.py

# If SECRET_KEY is missing from environment, raise ImproperlyConfigured
import environ
env = environ.Env(
    DEBUG=(bool, False)
)
try:
    SECRET_KEY = env("DJANGO_SECRET_KEY")
except Exception:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY environment variable not set!")
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **Never commit secrets** | Use environment variables for any sensitive value |
| **`environs[django]`** | Clean, type-safe way to read env vars |
| **`.env` + `.gitignore`** | Local env file that's never committed |
| **`env.bool()`** | Type casting prevents string "True" vs bool True bugs |
| **`dj_db_url`** | Parses `DATABASE_URL` string into Django DATABASES dict |
| **Rotate if exposed** | Changing SECRET_KEY invalidates all sessions |

---

*← [Back to Django for Professionals](../README.md)*
