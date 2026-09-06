# Chapter 28 — Security Best Practices

> *"Security is not something you add at the end. It must be built in from the beginning."*

---

## 🎯 Core Concept

Django has excellent security built-in, but you must know what's there and what you need to configure. This chapter is a comprehensive reference for Django security: XSS, CSRF, SQL injection, clickjacking, HTTPS, and more.

---

## 🛡️ Django's Built-in Security Features

```
✅ XSS protection:         Template auto-escaping
✅ CSRF protection:        {% csrf_token %} on all forms
✅ SQL injection:           ORM parameterized queries
✅ Clickjacking:           X-Frame-Options middleware
✅ Password hashing:       PBKDF2 with SHA256 (default)
✅ Secure cookies:         SESSION_COOKIE_SECURE = True
✅ SSL redirect:           SECURE_SSL_REDIRECT = True
✅ Admin lockdown:         Custom URL, IP restriction
```

---

## ❌ XSS — Cross-Site Scripting

```html
<!-- Django auto-escapes by default: -->
{{ user_content }}
<!-- <script>alert('xss')</script> → &lt;script&gt;... (safe) -->

<!-- Only bypass when content is TRUSTED and SANITIZED: -->
{{ content|safe }}

<!-- Content Security Policy header (settings.py): -->
# SECURE_CONTENT_TYPE_NOSNIFF = True
# Add CSP headers via django-csp package
```

---

## 🔐 CSRF — Cross-Site Request Forgery

```html
<!-- Every form that modifies data MUST have: -->
<form method="post">
  {% csrf_token %}
</form>

<!-- For AJAX requests: -->
headers: { 'X-CSRFToken': getCookie('csrftoken') }
```

```python
# When CSRF is legitimately needed to be disabled (use VERY carefully):
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def api_webhook(request):
    """External webhook that sends its own signature."""
    verify_signature(request)  # MUST verify some other way!
```

---

## 🗄️ SQL Injection

```python
# SAFE: ORM parameterizes all queries
Flavor.objects.filter(title=user_input)   # ← SAFE always

# SAFE: Raw with parameters
Flavor.objects.raw("SELECT * FROM flavors WHERE title = %s", [user_input])

# DANGEROUS: f-strings in raw SQL
Flavor.objects.raw(f"SELECT * WHERE title = '{user_input}'")  # ← NEVER!
cursor.execute(f"SELECT * FROM flavors WHERE title = '{user_input}'")  # ← NEVER!
```

---

## 🔒 Production Security Settings

```python
# settings/production.py

# HTTPS
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookies
SESSION_COOKIE_SECURE = True    # Session cookie HTTPS only
CSRF_COOKIE_SECURE = True       # CSRF cookie HTTPS only

# Clickjacking
X_FRAME_OPTIONS = "DENY"       # No <iframe> embedding

# Content type sniffing
SECURE_CONTENT_TYPE_NOSNIFF = True

# Referrer policy
SECURE_REFERRER_POLICY = "same-origin"
```

---

## 🔑 Password Management

```python
# settings.py — Django's password validators
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Password hashers (ordered by preference)
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",  # Best (argon2 package needed)
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",  # Default
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
]
```

---

## 🔐 Admin Security

```python
# 1. Use non-default URL for admin
urlpatterns = [
    path("secret-staff-access-23/", admin.site.urls),  # Not /admin/!
]

# 2. Restrict admin access to staff only (default) - never compromise this

# 3. Use django-admin-honeypot
pip install django-admin-honeypot
# Fake admin at /admin/ logs all unauthorized attempts

# 4. Two-factor auth for admin
pip install django-two-factor-auth
```

---

## 📦 Dependency Security

```bash
# Check for known vulnerabilities
$ pip install safety
$ safety check

# Or use pip-audit
$ pip install pip-audit
$ pip-audit

# Run regularly in CI/CD
```

---

## 💡 Key Takeaways

| Threat | Django Protection | Your Action |
|--------|------------------|-------------|
| XSS | Auto-escaping | Never `|safe` untrusted content |
| CSRF | CSRF middleware | `{% csrf_token %}` on all forms |
| SQL injection | ORM | Never raw SQL with user input |
| Clickjacking | X-Frame-Options | `X_FRAME_OPTIONS = "DENY"` |
| HTTPS | SSL redirect | `SECURE_SSL_REDIRECT = True` |
| Cookie theft | Secure cookies | `SESSION_COOKIE_SECURE = True` |
| Admin attacks | Custom URL + 2FA | Non-standard admin URL |
| Dependency vulnerabilities | pip-audit | Regular scanning in CI |

---

*← [Back to Two Scoops of Django](../README.md)*
