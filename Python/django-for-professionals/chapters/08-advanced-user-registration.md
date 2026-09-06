# Chapter 8 — Advanced User Registration

> *"django-allauth is the gold standard for authentication in Django. It handles email verification, social authentication, and custom email-only login out of the box."*

---

## 🎯 Core Concept

**django-allauth** replaces Django's built-in authentication with a production-grade system that supports email-only login, email verification, social authentication (Google, GitHub, etc.), and much more — all with minimal code.

---

## 🔐 Why django-allauth?

```
Built-in django.contrib.auth:           django-allauth:
────────────────────────────────────────────────────────────
Username required                       Email-only login ✓
No email verification                   Email verification ✓
No social auth                          Google, GitHub, Twitter ✓
No email-only login                     Configurable ✓
Basic password validation               Advanced validation ✓
```

---

## 📦 Installation

```
# requirements.txt
django-allauth~=0.50
```

```python
# settings.py
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",      # Required by allauth
    # Third-party
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # Local
    "accounts",
    "pages",
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",  # Default
    "allauth.account.auth_backends.AuthenticationBackend",  # Allauth
)
```

---

## ⚙️ Key allauth Settings

```python
# settings.py

# Use email as the primary login identifier
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True

# Require email verification before login?
# "mandatory" = must verify, "optional" = can skip, "none" = no verification
ACCOUNT_EMAIL_VERIFICATION = "mandatory"

# Where to go after login
LOGIN_REDIRECT_URL = "home"
ACCOUNT_LOGOUT_REDIRECT = "home"
```

---

## 🔗 URL Configuration

```python
# django_project/urls.py
urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),   # Replaces django.contrib.auth.urls
    path("", include("pages.urls")),
]
```

allauth provides many more URLs than the built-in auth:
```
/accounts/login/
/accounts/logout/
/accounts/signup/
/accounts/email/          ← Manage email addresses
/accounts/confirm-email/  ← Email verification
/accounts/password/change/
/accounts/password/reset/
/accounts/social/         ← Social auth (if configured)
```

---

## 📧 Email-Only Authentication

```python
# settings.py
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
```

Now users log in with email + password instead of username + password.

### Email Backend for Development

```python
# settings.py
# During development, print emails to console instead of actually sending
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
```

When users sign up, the confirmation email appears in your docker-compose logs.

---

## 🎨 Customizing allauth Templates

allauth looks for templates in `templates/account/`:

```
templates/
└── account/
    ├── login.html          ← Override login page
    ├── logout.html         ← Override logout page
    ├── signup.html         ← Override signup page
    ├── email.html          ← Manage email addresses
    └── email_confirm.html  ← Email confirmation page
```

```html
<!-- templates/account/login.html -->
{% extends "_base.html" %}
{% load crispy_forms_tags %}

{% block title %}Log In{% endblock title %}

{% block content %}
  <h2>Log In</h2>
  <form method="post">
    {% csrf_token %}
    {{ form|crispy }}
    <button class="btn btn-success" type="submit">Log In</button>
  </form>
  <p>Don't have an account? <a href="{% url 'account_signup' %}">Sign Up</a></p>
{% endblock content %}
```

---

## 🌐 Social Authentication (Google Example)

```python
# settings.py
INSTALLED_APPS += ["allauth.socialaccount.providers.google"]

# Configure in Django admin:
# Sites > example.com (update to actual domain)
# Social Applications > Add > Google > Enter Client ID + Secret
```

> Setting up social auth requires creating OAuth apps on each provider's developer console.

---

## 🧪 Testing with allauth

```python
# accounts/tests.py
class SignUpPageTests(TestCase):
    username = "newuser"
    email = "newuser@email.com"

    def setUp(self):
        url = reverse("account_signup")
        self.response = self.client.get(url)

    def test_signup_template(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "account/signup.html")
        self.assertContains(self.response, "Sign Up")
```

> **Note:** allauth URL names are prefixed with `account_`: `account_login`, `account_logout`, `account_signup`

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **allauth replaces built-in auth** | More features, better extensibility |
| **Email-only login** | Professional sites prefer email over username |
| **django.contrib.sites** | Required for allauth — SITE_ID = 1 |
| **Two AUTHENTICATION_BACKENDS** | Django's default + allauth's backend |
| **Console email backend** | See emails in docker-compose logs during development |
| **allauth URL names** | Prefixed with `account_` — not the same as built-in |

---

*← [Back to Django for Professionals](../README.md)*
