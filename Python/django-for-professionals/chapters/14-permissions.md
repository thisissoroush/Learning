# Chapter 14 — Permissions

> *"By default in Django, access to views is unrestricted. Use mixins and decorators to restrict access to authenticated users, and groups/permissions for fine-grained control."*

---

## 🎯 Core Concept

**Authorization** is about controlling who can access what. Django provides three levels: (1) login required, (2) group-based permissions, (3) object-level permissions. This chapter covers all three using the Bookstore.

---

## 🔐 Level 1: Login Required

### For Class-Based Views — LoginRequiredMixin

```python
# books/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from .models import Book


class BookListView(LoginRequiredMixin, ListView):
    model = Book
    context_object_name = "book_list"
    template_name = "books/book_list.html"
    login_url = "/accounts/login/"          # Where to redirect unauthenticated users


class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    context_object_name = "book"
    template_name = "books/book_detail.html"
    login_url = "/accounts/login/"
```

> **Mixin order matters!** `LoginRequiredMixin` must be FIRST in the inheritance list.

### For Function-Based Views — @login_required

```python
from django.contrib.auth.decorators import login_required

@login_required
def my_view(request):
    ...
```

---

## 🔐 Level 2: Permission-Based Access

Django's permission system: every model auto-gets 4 permissions:
```
app_label.add_modelname      ← Can create
app_label.view_modelname     ← Can view
app_label.change_modelname   ← Can edit
app_label.delete_modelname   ← Can delete
```

### PermissionRequiredMixin

```python
# books/views.py
from django.contrib.auth.mixins import PermissionRequiredMixin


class BookCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Book
    permission_required = "books.add_book"   # Only users with this permission
    ...


class BookUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Book
    permission_required = "books.change_book"
    ...
```

### Granting Permissions

```python
# In Django Admin:
# Users → select user → Permissions section
# OR
# Groups → create group → assign permissions → add users to group
```

---

## 👥 Groups — Assign Permissions in Bulk

```
Django Admin → Groups → Create "editors" group
                        → Add permissions:
                          ✓ books | book | Can add book
                          ✓ books | book | Can change book
                          ✗ books | book | Can delete book

→ Add users to "editors" group
→ All group members get all group permissions
```

---

## 🔐 Level 3: Object-Level Permissions

Django's built-in permissions are model-level ("can any user edit any book?"). For object-level ("can this user edit only their own book?"), use custom logic:

```python
class BookUpdateView(LoginRequiredMixin, UpdateView):
    model = Book

    def get_object(self):
        obj = super().get_object()
        if obj.owner != self.request.user:
            raise PermissionDenied   # or redirect
        return obj
```

---

## 🧪 Testing Permissions

```python
# books/tests.py
class BookTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="testuser", email="test@email.com", password="testpass123"
        )
        cls.special_user = get_user_model().objects.create_user(
            username="specialuser", email="special@email.com", password="testpass123"
        )
        cls.book = Book.objects.create(
            title="Harry Potter", author="JK Rowling", price="25.00"
        )

    def test_book_list_view_for_logged_in_user(self):
        self.client.login(email="test@email.com", password="testpass123")
        response = self.client.get(reverse("book_list"))
        self.assertEqual(response.status_code, 200)

    def test_book_list_view_for_logged_out_user(self):
        self.client.logout()
        response = self.client.get(reverse("book_list"))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertRedirects(response, "%s?next=/books/" % (reverse("account_login"),))
```

---

## 📊 Permission Flow

```
Request arrives at BookDetailView
         ↓
LoginRequiredMixin checks: is user authenticated?
  ├── No  → redirect to /accounts/login/?next=/books/uuid/
  └── Yes ↓
PermissionRequiredMixin checks: has books.view_book permission?
  ├── No  → 403 Forbidden
  └── Yes ↓
View executes normally → 200 OK
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **LoginRequiredMixin** | Restrict any CBV to authenticated users |
| **Mixin order** | LoginRequiredMixin must come FIRST |
| **PermissionRequiredMixin** | Fine-grained control: `"books.add_book"` |
| **Groups** | Assign multiple permissions to multiple users at once |
| **Object-level** | Override `get_object()` for per-object access control |
| **Test both auth states** | Test logged-in (200) AND logged-out (302) |

---

*← [Back to Django for Professionals](../README.md)*
