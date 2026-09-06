# Chapter 11 — Books App

> *"Use UUIDs instead of sequential integers for primary keys — they're harder to guess and expose nothing about your data volume."*

---

## 🎯 Core Concept

This chapter builds the core **Books** feature. Key professional decisions: use **UUIDs** as primary keys and structure with Django's Model-View-Template pattern with testing at each step.

---

## 🔑 UUIDs vs Integer Primary Keys

```
Integer PKs:              UUID PKs:
/books/1/                 /books/550e8400-e29b-41d4-a716-446655440000/
/books/2/                 /books/6ba7b810-9dad-11d1-80b4-00c04fd430c8/

Integers reveal: total count, enumerate all objects
UUIDs: unguessable, safe for public URLs, distributed-friendly
```

---

## 🗃️ The Book Model

```python
# books/models.py
import uuid
from django.db import models
from django.urls import reverse

class Book(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    cover = models.ImageField(upload_to="covers/", blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("book_detail", args=[str(self.id)])
```

---

## 👁️ Views and URLs

```python
# books/views.py
from django.views.generic import ListView, DetailView
from .models import Book

class BookListView(ListView):
    model = Book
    context_object_name = "book_list"
    template_name = "books/book_list.html"

class BookDetailView(DetailView):
    model = Book
    context_object_name = "book"
    template_name = "books/book_detail.html"
```

```python
# books/urls.py
urlpatterns = [
    path("", BookListView.as_view(), name="book_list"),
    path("<uuid:pk>/", BookDetailView.as_view(), name="book_detail"),  # <uuid:pk> validates UUID
]
```

---

## 🧪 Testing

```python
# books/tests.py
class BookTests(TestCase):
    @classmethod
    def setUpTestData(cls):   # Runs ONCE per class (faster than setUp)
        cls.book = Book.objects.create(
            title="Harry Potter", author="JK Rowling", price="25.00"
        )

    def test_book_list_view(self):
        response = self.client.get(reverse("book_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Harry Potter")

    def test_book_detail_view(self):
        response = self.client.get(self.book.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Harry Potter")
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **UUIDs for PKs** | Secure, unguessable primary keys |
| **`<uuid:pk>` URL converter** | Django auto-validates UUID format in URLs |
| **get_absolute_url()** | Define URL on model, use everywhere (DRY) |
| **setUpTestData** | Faster than setUp — creates objects once per class |
| **context_object_name** | Rename `object_list` to something meaningful |

---

*← [Back to Django for Professionals](../README.md)*
