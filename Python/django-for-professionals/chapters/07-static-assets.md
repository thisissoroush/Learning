# Chapter 7 — Static Assets

> *"Static assets are a core part of every website. In Django we must take additional steps so they are compiled and hosted efficiently in production."*

---

## 🎯 Core Concept

**Static files** (CSS, JavaScript, images) work differently in development vs production in Django. Understanding this distinction is essential for professional deployment. This chapter also integrates **Bootstrap** and **django-crispy-forms** for professional styling.

---

## 📁 Static Files in Django

### Development vs Production

```
DEVELOPMENT (DEBUG=True):
User → Django dev server → serves static files directly
Works fine, but slow for production

PRODUCTION (DEBUG=False):
User → Web server (nginx/WhiteNoise) → serves static files
Django should NOT serve static files in production!
```

### The Three Static File Settings

```python
# settings.py

# 1. Where Django looks for static files in each app
#    (automatic: <app>/static/)

# 2. Additional directories to search
STATICFILES_DIRS = [BASE_DIR / "static"]

# 3. Where collectstatic puts all static files for production
STATIC_ROOT = BASE_DIR / "staticfiles"

# 4. URL prefix for static files
STATIC_URL = "/static/"
```

### `collectstatic` — The Production Command

```bash
# Gathers ALL static files from all apps into STATIC_ROOT
$ python manage.py collectstatic

# Django gathers:
# - /static/ directories from each installed app
# - Directories listed in STATICFILES_DIRS
# And copies everything to STATIC_ROOT/
```

---

## 📂 Project Static File Structure

```
bookstore_project/
├── static/             ← Project-level static files (STATICFILES_DIRS)
│   ├── css/
│   │   └── base.css
│   ├── js/
│   │   └── main.js
│   └── images/
│       └── logo.png
├── staticfiles/        ← STATIC_ROOT (collectstatic output, git-ignored)
└── django_project/
    └── settings.py
```

---

## 🎨 Using Static Files in Templates

```html
<!-- templates/_base.html -->
{% load static %}
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="{% static 'css/base.css' %}">
</head>
<body>
  <img src="{% static 'images/logo.png' %}" alt="Logo">
  <script src="{% static 'js/main.js' %}"></script>
</body>
</html>
```

> **Always `{% load static %}` at top** of any template that uses static files.

---

## 🅱️ Adding Bootstrap

### Via CDN (Simplest)

```html
<!-- In _base.html <head> -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
      rel="stylesheet">

<!-- Before </body> -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js">
</script>
```

### Via Local Files (Production-safe, offline-capable)

```bash
# Download Bootstrap and place in static/
static/
├── css/
│   └── bootstrap.min.css
└── js/
    └── bootstrap.bundle.min.js
```

---

## 💅 django-crispy-forms

Transforms Django's `{{ form.as_p }}` into beautifully styled Bootstrap forms:

### Install

```
# requirements.txt
django-crispy-forms~=1.14
crispy-bootstrap5~=0.6
```

### Configure

```python
# settings.py
INSTALLED_APPS = [
    ...
    "crispy_forms",
    "crispy_bootstrap5",
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
```

### Use in Templates

```html
<!-- Before: ugly default Django form -->
{{ form.as_p }}

<!-- After: beautiful Bootstrap-styled form -->
{% load crispy_forms_tags %}
{{ form|crispy }}
```

---

## 📊 Static Files Flow Diagram

![Static Assets Flow](../images/07-static-assets.png)

---

## 🧪 Testing Static Assets

```python
# pages/tests.py
class AboutPageTests(SimpleTestCase):
    def setUp(self):
        url = reverse("about")
        self.response = self.client.get(url)

    def test_about_page_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_about_page_template(self):
        self.assertTemplateUsed(self.response, "about.html")

    def test_about_page_contains_correct_html(self):
        self.assertContains(self.response, "About")
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **STATIC_URL** | URL prefix for serving static files |
| **STATICFILES_DIRS** | Where Django searches for project-level static files |
| **STATIC_ROOT** | Where `collectstatic` dumps everything for production |
| **`{% load static %}`** | Required at top of every template using static files |
| **Don't serve static in prod** | Use WhiteNoise, nginx, or S3 instead |
| **crispy-forms** | Effortless Bootstrap styling for any Django form |

---

*← [Back to Django for Professionals](../README.md)*
