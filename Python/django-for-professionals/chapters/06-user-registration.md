# Chapter 6 — User Registration

> *"Django's built-in auth app provides login, logout, and password management for free. You only need to build sign up yourself."*

---

## 🎯 Core Concept

Django ships with a complete authentication system (`django.contrib.auth`). This chapter wires up **login**, **logout**, and **sign up** for the Bookstore. The key insight: Django handles login/logout for you — you only need to create the sign-up view.

---

## 🔐 What django.contrib.auth Provides

```
django.contrib.auth includes:
├── User model          (replaced by CustomUser in Ch. 4)
├── Login view          ← Built-in, just wire up the URL
├── Logout view         ← Built-in, just wire up the URL
├── Password change     ← Built-in
├── Password reset      ← Built-in (requires email setup)
├── LoginRequired mixin ← Restrict views to logged-in users
└── SignUp view         ← NOT built-in! You build this
```

---

## 🔗 Wiring Up Auth URLs

```python
# django_project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),  # Login/Logout
    path("accounts/", include("accounts.urls")),             # Sign Up
    path("", include("pages.urls")),
]
```

`django.contrib.auth.urls` provides these URL patterns automatically:
```
accounts/login/          name="login"
accounts/logout/         name="logout"
accounts/password_change/ name="password_change"
accounts/password_reset/  name="password_reset"
```

---

## 📝 Building the Sign-Up View

### View

```python
# accounts/views.py
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CustomUserCreationForm


class SignupPageView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")    # Redirect to login after signup
    template_name = "registration/signup.html"
```

### URL

```python
# accounts/urls.py
from django.urls import path
from .views import SignupPageView

urlpatterns = [
    path("signup/", SignupPageView.as_view(), name="signup"),
]
```

### Template

```html
<!-- templates/registration/signup.html -->
{% extends "_base.html" %}

{% block title %}Sign Up{% endblock title %}

{% block content %}
  <h2>Sign Up</h2>
  <form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Sign Up</button>
  </form>
{% endblock content %}
```

---

## 🔒 Login and Logout Templates

Django's built-in views need templates at specific locations:

```
templates/
└── registration/
    ├── login.html          ← For login view
    ├── signup.html         ← Our custom sign up view
    └── logged_out.html     ← After logout (or redirect)
```

```html
<!-- templates/registration/login.html -->
{% extends "_base.html" %}

{% block title %}Log In{% endblock title %}

{% block content %}
  <h2>Log In</h2>
  <form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Log In</button>
  </form>
{% endblock content %}
```

---

## ⚙️ Auth Redirect Settings

```python
# settings.py

# Where to go after login (if no ?next= parameter)
LOGIN_REDIRECT_URL = "home"

# Where to go after logout
LOGOUT_REDIRECT_URL = "home"
```

---

## 🌐 Showing Login State in Templates

```html
<!-- templates/_base.html -->
<nav>
  {% if user.is_authenticated %}
    <span>Hi, {{ user.username }}!</span>
    <a href="{% url 'logout' %}">Log Out</a>
  {% else %}
    <a href="{% url 'login' %}">Log In</a>
    <a href="{% url 'signup' %}">Sign Up</a>
  {% endif %}
</nav>
```

---

## 🧪 Testing Authentication

```python
# accounts/tests.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse, resolve

from .forms import CustomUserCreationForm
from .views import SignupPageView


class SignUpPageTests(TestCase):
    def setUp(self):
        url = reverse("signup")
        self.response = self.client.get(url)

    def test_signup_template(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "registration/signup.html")
        self.assertContains(self.response, "Sign Up")

    def test_signup_form(self):
        form = self.response.context.get("form")
        self.assertIsInstance(form, CustomUserCreationForm)

    def test_signup_view(self):
        view = resolve("/accounts/signup/")
        self.assertEqual(view.func.__name__, SignupPageView.as_view().__name__)
```

---

## 🔄 The Complete Auth Flow

```
User visits /accounts/signup/
  → Fills out form → POST → creates account
  → Redirects to /accounts/login/

User visits /accounts/login/
  → Enters credentials → POST → authenticates
  → Redirects to home (LOGIN_REDIRECT_URL)

User visits /accounts/logout/
  → Session cleared
  → Redirects to home (LOGOUT_REDIRECT_URL)
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **Auth is mostly built-in** | Login, logout, password — all free with Django |
| **Only sign up needs building** | CreateView + UserCreationForm = 10 lines |
| **reverse_lazy for class-based views** | Use `reverse_lazy()` not `reverse()` in class attributes |
| **LOGIN_REDIRECT_URL** | Controls where users go after login |
| **{% if user.is_authenticated %}** | The template check for logged-in state |
| **Test the form, not just the view** | Verify the right form class is in context |

---

*← [Back to Django for Professionals](../README.md)*
