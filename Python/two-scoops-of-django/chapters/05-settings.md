# Chapter 5 — Settings and Requirements Files

> *"Never have a local_settings.py that's not under version control. Never hardcode secrets. Always separate configuration from code."*

---

## 🎯 Core Concept

Django settings are a critical source of bugs, security holes, and team friction. This chapter establishes the **definitive way** to manage settings: multiple files per environment, secrets in environment variables, and dynamic path calculation.

---

## ❌ The Anti-Pattern: local_settings.py

Many tutorials suggest this:

```python
# settings.py
try:
    from local_settings import *    # ← DON'T DO THIS!
except ImportError:
    pass
```

**Why it's bad:**
- `local_settings.py` is excluded from version control (gitignored)
- Different machines have different local settings
- "Settings sprawl" — every developer has different behavior
- Debugging becomes impossible: "what settings are you actually using?"

---

## ✅ The Right Way: Multiple Settings Files

```
config/settings/
├── __init__.py
├── base.py         ← Everything shared across environments
├── local.py        ← Development only (DEBUG, dev tools)
├── staging.py      ← Staging server settings
└── production.py   ← Production server settings
```

### base.py — The Common Foundation

```python
# config/settings/base.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Apps (same everywhere)
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    ...
    "myapp.flavors",
    "myapp.stores",
]

# Database (URL provided by environment)
import environ
env = environ.Env()
DATABASES = {"default": env.db("DATABASE_URL")}
```

### local.py — Development Settings

```python
# config/settings/local.py
from .base import *

DEBUG = True

INSTALLED_APPS += [
    "debug_toolbar",       # Only in development
    "django_extensions",   # Only in development
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

INTERNAL_IPS = ["127.0.0.1"]
```

### production.py — Production Settings

```python
# config/settings/production.py
from .base import *

DEBUG = False

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Email via real SMTP
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST")
```

### Using the Right Settings File

```bash
# Development
$ export DJANGO_SETTINGS_MODULE=config.settings.local
$ python manage.py runserver

# Production (set in server environment)
$ export DJANGO_SETTINGS_MODULE=config.settings.production
$ gunicorn config.wsgi
```

---

## 🔑 Separate Configuration from Code (12-Factor)

Secrets and environment-specific settings belong in **environment variables**, not in code:

```python
# BAD: Hardcoded in settings.py (committed to Git!)
SECRET_KEY = "abc123insecure"
DATABASE_URL = "postgres://user:password@localhost/mydb"

# GOOD: From environment
import environ
env = environ.Env()

SECRET_KEY = env("DJANGO_SECRET_KEY")
DATABASE_URL = env("DATABASE_URL")
```

### Handling Missing Environment Variables

```python
from django.core.exceptions import ImproperlyConfigured

def get_env_variable(var_name):
    """Get an environment variable or raise an exception."""
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = f"Set the {var_name} environment variable"
        raise ImproperlyConfigured(error_msg)

SECRET_KEY = get_env_variable("DJANGO_SECRET_KEY")
```

---

## 📦 Split Requirements Files

Match your settings split with requirements:

```
requirements/
├── base.txt         ← Used by all environments
├── local.txt        ← Development tools
└── production.txt   ← Production extras
```

```
# requirements/base.txt
Django==3.2.13
psycopg2-binary==2.9.3
django-environ==0.8.1

# requirements/local.txt
-r base.txt         ← Includes everything from base
django-debug-toolbar==3.2.4
factory-boy==3.2.1

# requirements/production.txt
-r base.txt
gunicorn==20.1.0
whitenoise==6.0.0
```

```bash
# Install for development:
$ pip install -r requirements/local.txt

# Install for production:
$ pip install -r requirements/production.txt
```

---

## 📂 Dynamic File Paths with Pathlib

```python
# BAD: Hardcoded (breaks on any machine but the author's!)
MEDIA_ROOT = '/Users/pydanny/twoscoops_project/media'
STATIC_ROOT = '/Users/pydanny/twoscoops_project/staticfiles'

# GOOD: Dynamic using Pathlib
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent

MEDIA_ROOT = BASE_DIR / "media"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
TEMPLATES = [{"DIRS": [BASE_DIR / "templates"]}]
```

---

## 💡 Key Takeaways

| Practice | Why |
|----------|-----|
| **Multiple settings files** | Environment-specific config, all under version control |
| **No local_settings.py** | Settings sprawl, impossible to debug team issues |
| **Secrets in environment** | Never commit passwords/API keys to Git |
| **Split requirements files** | Dev tools stay out of production |
| **Pathlib for paths** | Dynamic, portable, works on any machine |
| **`-r base.txt` in local/prod** | DRY: local and production inherit from base |

---

*← [Back to Two Scoops of Django](../README.md)*
