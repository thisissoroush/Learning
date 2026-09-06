# Chapter 17 — Security

> *"Security is not a feature to add at the end. Run Django's deployment checklist early and often."*

---

## 🎯 Core Concept

Django provides **excellent security out of the box**, but many protections are disabled in development. This chapter shows how to enable them for production.

---

## 🔑 Django's Deployment Checklist

```bash
$ python manage.py check --deploy
# Reveals all security warnings before deploying
```

---

## 🔒 Production Security Settings

```python
# settings.py
DEBUG = False
SECURE_SSL_REDIRECT = True           # HTTP → HTTPS redirect
SECURE_HSTS_SECONDS = 31536000       # HTTPS-only for 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SESSION_COOKIE_SECURE = True         # Cookies over HTTPS only
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"             # No iframe embedding
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
```

---

## 🛡️ Django's Built-in Protections

### CSRF — Cross-Site Request Forgery
```html
<form method="post">
  {% csrf_token %}  <!-- Required on ALL forms -->
</form>
```

### XSS — Cross-Site Scripting
```html
{{ user_input }}
<!-- Auto-escaped: <script> → &lt;script&gt; (displayed as text) -->
<!-- Only use |safe when you FULLY trust the content -->
```

### SQL Injection
```python
# ORM is SAFE (parameterized):
Book.objects.filter(title=user_input)

# NEVER do raw SQL with user input:
# Book.objects.raw(f"SELECT * WHERE title='{user_input}'")  ← DANGEROUS
```

### Clickjacking
```python
X_FRAME_OPTIONS = "DENY"  # Block iframe embedding
```

---

## 🔐 Admin Hardening

```python
# urls.py — change the admin URL from the default /admin/
urlpatterns = [
    path("secret-admin-123/", admin.site.urls),  # Non-standard!
]
```

---

## 📊 Security Layer Overview

```
Internet → HTTPS → LoadBalancer → SecurityMiddleware → Django App
                                  ├── HSTS, SSL redirect
                                  ├── CSRF middleware
                                  ├── XSS auto-escaping
                                  └── Clickjacking headers
```

---

## 💡 Key Takeaways

| Feature | Setting | Purpose |
|---------|---------|---------|
| HTTPS | `SECURE_SSL_REDIRECT` | Force all traffic to HTTPS |
| HSTS | `SECURE_HSTS_SECONDS` | Browser remembers HTTPS-only |
| CSRF | `{% csrf_token %}` | Prevent cross-site form attacks |
| XSS | Auto-escaping | Template variables safe by default |
| SQL injection | ORM | Parameterized queries always |
| Clickjacking | `X_FRAME_OPTIONS` | Block iframe embedding |
| Admin URL | Custom path | Harder to find and attack |

---

*← [Back to Django for Professionals](../README.md)*
