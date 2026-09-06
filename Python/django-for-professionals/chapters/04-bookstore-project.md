# Chapter 4 — Bookstore Project

> *"The most important single thing to do when starting a new Django project: always use a custom user model."*

---

## 🎯 Core Concept

This chapter starts the main Bookstore project. The **#1 rule** of every professional Django project: **always create a custom User model before your first migration**. Missing this is one of the most painful mistakes a Django developer can make.

---

## ⚠️ The Custom User Model Rule

### Why It's Mandatory

```
Default User model:
  - Fields: username, email, first_name, last_name, password
  - Can't be changed after running migrate
  
The Problem:
  1. You start a project → run migrate → default User model locked in
  2. Later: "We need email-only login (no username)"
  3. Now you're stuck: Django tightly binds auth to this specific model
  4. Workaround: painful OneToOneField "profile" models
  
The Solution:
  Create AbstractUser subclass BEFORE first migrate
```

### The Golden Rule
> **NEVER run `python manage.py migrate` before creating a custom User model.**

---

## 🏗️ Building the Custom User Model

### Step 1: Create the Accounts App

```bash
$ docker-compose exec web python manage.py startapp accounts
```

### Step 2: Define the Custom User Model

```python
# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    pass  # No extra fields yet — but we CAN add them later!
```

> **Why `AbstractUser` vs `AbstractBaseUser`?**
> - `AbstractUser` — keeps all existing fields (username, email, etc.), easiest to extend
> - `AbstractBaseUser` — start from scratch, maximum flexibility, much more work

### Step 3: Register in Settings

```python
# django_project/settings.py
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    ...
    "accounts",          # Add your accounts app
]

# The magic line — tells Django which model is "the user"
AUTH_USER_MODEL = "accounts.CustomUser"
```

### Step 4: Custom Forms (for Admin)

```python
# accounts/forms.py
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ("email", "username",)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ("email", "username",)
```

> **Always use `get_user_model()`** instead of importing `User` directly. This returns whatever model is set as `AUTH_USER_MODEL`.

### Step 5: Register in Admin

```python
# accounts/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm

CustomUser = get_user_model()


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ["email", "username", "is_superuser"]
```

### Step 6: Migrate (Now Safe!)

```bash
$ docker-compose exec web python manage.py makemigrations accounts
$ docker-compose exec web python manage.py migrate
```

---

## 🔍 Creating a Superuser

```bash
$ docker-compose exec web python manage.py createsuperuser
# Username: bookstoreAdmin
# Email: admin@email.com
# Password: testpass123
```

Now visit `http://127.0.0.1:8000/admin/` and you'll see your custom user in the admin.

---

## 🧪 Testing the Custom User

```python
# accounts/tests.py
from django.contrib.auth import get_user_model
from django.test import TestCase


class CustomUserTests(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="testuser",
            email="testuser@email.com",
            password="testpass123",
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "testuser@email.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username="superadmin",
            email="superadmin@email.com",
            password="testpass123",
        )
        self.assertEqual(admin_user.username, "superadmin")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
```

---

## 📊 Project Structure After Chapter 4

```
bookstore_project/
├── accounts/
│   ├── admin.py        ← CustomUserAdmin
│   ├── apps.py
│   ├── forms.py        ← CustomUserCreationForm, CustomUserChangeForm
│   ├── migrations/
│   │   └── 0001_initial.py
│   ├── models.py       ← CustomUser(AbstractUser)
│   ├── tests.py        ← User creation tests
│   └── views.py
├── django_project/
│   ├── settings.py     ← AUTH_USER_MODEL = "accounts.CustomUser"
│   ├── urls.py
│   └── wsgi.py
├── Dockerfile
├── docker-compose.yml
├── manage.py
└── requirements.txt
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **Custom User model first** | Do this before ANY migration — no exceptions |
| **AbstractUser is easiest** | Extends Django's existing user, add fields as needed |
| **AUTH_USER_MODEL in settings** | One setting to rule all user references |
| **get_user_model()** | Never import User directly — always use this function |
| **Test create_user AND create_superuser** | Two different code paths, both need tests |

---

*← [Back to Django for Professionals](../README.md)*
