# Chapter 20 — Styling and Deploying an App

> **Part II: Project — Learning Log (3/3)**

---

## 🎯 What This Chapter Covers

Styling with Bootstrap via django-bootstrap5, preparing for production, and deploying to Platform.sh.

---

## 🎨 Styling with Bootstrap (django-bootstrap5)

```bash
pip install django-bootstrap5
```

```python
# settings.py
INSTALLED_APPS = [
    ...
    'django_bootstrap5',
    'learning_logs',
    'users',
]
```

```html
<!-- base.html — Bootstrap-styled -->
{% load django_bootstrap5 %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Learning Log</title>
  {% bootstrap_css %}
  {% bootstrap_javascript %}
</head>
<body>
  <nav class="navbar navbar-expand-md navbar-light bg-light mb-4 border">
    <div class="container-fluid">
      <a class="navbar-brand" href="{% url 'learning_logs:index' %}">
        Learning Log
      </a>
      <div class="collapse navbar-collapse">
        <ul class="navbar-nav me-auto mb-2 mb-md-0">
          <li class="nav-item">
            <a class="nav-link" href="{% url 'learning_logs:topics' %}">
              Topics
            </a>
          </li>
        </ul>
        {% if user.is_authenticated %}
          <span class="text-muted">Hello, {{ user.username }}.</span>
          <a href="{% url 'logout' %}" class="btn btn-outline-secondary btn-sm ms-2">
            Log out
          </a>
        {% else %}
          <a href="{% url 'users:register' %}" class="btn btn-outline-secondary btn-sm ms-2">
            Register
          </a>
          <a href="{% url 'login' %}" class="btn btn-outline-secondary btn-sm ms-2">
            Log in
          </a>
        {% endif %}
      </div>
    </div>
  </nav>
  <main class="container">
    {% block content %}{% endblock content %}
  </main>
</body>
</html>
```

---

## ⚙️ Production Settings

```python
# settings.py — production configuration
DEBUG = False

ALLOWED_HOSTS = ['*']   # will be restricted by Platform.sh config

# Static files
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# Secret key from environment variable
import os
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-for-local-use-only')
```

```bash
# Collect static files for deployment
python manage.py collectstatic
```

---

## 🚀 Deployment to Platform.sh

```yaml
# .platform/routes.yaml
"https://{default}/":
  type: upstream
  upstream: "ll_project:http"

# .platform/services.yaml
db:
  type: postgresql:14
  disk: 1024

# .platform.app.yaml
name: ll_project
type: python:3.11
disk: 512

relationships:
  database: "db:postgresql"

web:
  commands:
    start: "gunicorn ll_project.wsgi:application"

hooks:
  build: |
    pip install -r requirements.txt
    python manage.py collectstatic --no-input
  deploy: |
    python manage.py migrate
```

```bash
# requirements.txt for production
Django>=4.2
django-bootstrap5>=23.3
gunicorn>=21.2
psycopg2>=2.9
dj-database-url>=2.1

# Deploy
platform push
platform url   # get the live URL
```

---

## 🔧 Environment-Based Configuration

```python
# settings.py — full production-ready config
import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# Database — use DATABASE_URL env var in production
if os.environ.get('DATABASE_URL'):
    DATABASES = {'default': dj_database_url.config()}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

---

## 🔑 Key Takeaways

- `django-bootstrap5`: install, add to `INSTALLED_APPS`, use `{% load django_bootstrap5 %}` + `{% bootstrap_css %}`
- Bootstrap `container`, `navbar`, `btn`, `card` classes give professional styling instantly
- `DEBUG = False` in production; `ALLOWED_HOSTS` must include your domain
- `python manage.py collectstatic` gathers all static files to `STATIC_ROOT` for the web server to serve
- Environment variables (SECRET_KEY, DATABASE_URL) separate config from code — 12-factor app
- Gunicorn is the WSGI server for production (not Django's dev server)
- `python manage.py migrate` runs automatically on deploy via `hooks.deploy` in Platform.sh config
