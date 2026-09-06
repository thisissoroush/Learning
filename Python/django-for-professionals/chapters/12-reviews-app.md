# Chapter 12 — Reviews App

> *"A ForeignKey relationship connects two models, creating a one-to-many relationship: one book can have many reviews."*

---

## 🎯 Core Concept

This chapter adds a **Reviews** feature to the Bookstore — users can leave reviews on books. The core skill: **ForeignKey relationships** between models, and how to display related data in templates and the admin.

---

## 🔗 ForeignKey: One Book → Many Reviews

```
Book Model               Review Model
────────────────         ──────────────────────────
id (UUID, PK)            id (auto)
title                    book ──────→ Book.id (FK)
author                   review (text)
price                    author ─────→ CustomUser.id (FK)
```

### The Review Model

```python
# reviews/models.py
from django.contrib.auth import get_user_model
from django.db import models

from books.models import Book


class Review(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,  # Delete reviews when book is deleted
        related_name="reviews",    # Access reviews from book: book.reviews.all()
    )
    review = models.CharField(max_length=255)
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.review
```

---

## 🗑️ on_delete Options

```python
on_delete=models.CASCADE    # Delete Review when Book deleted (most common)
on_delete=models.PROTECT    # Prevent Book deletion if reviews exist
on_delete=models.SET_NULL   # Set book=NULL (requires null=True)
on_delete=models.SET_DEFAULT # Set to default value
on_delete=models.DO_NOTHING  # Let DB handle it (risky!)
```

---

## ⚙️ Admin Configuration

```python
# reviews/admin.py
from django.contrib import admin
from .models import Review


class ReviewInline(admin.TabularInline):
    """Show reviews inline within the Book admin page."""
    model = Review
    extra = 1    # Show 1 empty form for adding new reviews


class BookAdmin(admin.ModelAdmin):
    inlines = [ReviewInline]
    list_display = ["title", "author", "price"]


# Update books/admin.py to use ReviewInline
from books.admin import BookAdmin  # Import updated admin
```

### Inline Admin Result
When you view a Book in admin, you see its reviews right there on the same page — no need to navigate to a separate Reviews section.

---

## 📄 Displaying Reviews in Templates

```html
<!-- templates/books/book_detail.html -->
{% extends "_base.html" %}

{% block content %}
  <h2>{{ book.title }}</h2>
  <p>By {{ book.author }} — ${{ book.price }}</p>

  <h3>Reviews</h3>
  {% for review in book.reviews.all %}
    <div>
      <p>{{ review.review }}</p>
      <small>by {{ review.author }}</small>
    </div>
  {% empty %}
    <p>No reviews yet.</p>
  {% endfor %}
{% endblock content %}
```

> **`book.reviews.all`** works because of `related_name="reviews"` on the ForeignKey.

---

## 🧪 Testing Reviews

```python
# reviews/tests.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from books.models import Book
from .models import Review


class ReviewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="reviewuser",
            email="reviewuser@email.com",
            password="testpass123",
        )
        cls.book = Book.objects.create(
            title="Harry Potter",
            author="JK Rowling",
            price="25.00",
        )
        cls.review = Review.objects.create(
            book=cls.book,
            author=cls.user,
            review="An excellent read!",
        )

    def test_review_listing(self):
        self.assertEqual(f"{self.review.book}", "Harry Potter")
        self.assertEqual(f"{self.review.author}", "reviewuser")
        self.assertEqual(f"{self.review.review}", "An excellent read!")

    def test_review_appears_on_book_page(self):
        response = self.client.get(self.book.get_absolute_url())
        self.assertContains(response, "An excellent read!")
```

---

## 🔄 Related Object Access Patterns

```python
# Access book's reviews in Python code:
book = Book.objects.get(pk=some_uuid)
book.reviews.all()          # All reviews for this book
book.reviews.count()        # Number of reviews
book.reviews.filter(...)    # Filter reviews

# Access review's book:
review = Review.objects.get(pk=1)
review.book.title           # "Harry Potter"
review.author.email         # Author's email

# Optimize with select_related:
reviews = Review.objects.select_related("book", "author").all()
# Fetches all related data in single JOIN query
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **ForeignKey** | One-to-many: one book has many reviews |
| **on_delete=CASCADE** | Most common: delete child when parent deleted |
| **related_name** | Name the reverse relation: `book.reviews.all()` |
| **get_user_model()** | Always use this, never `from auth.models import User` |
| **TabularInline** | Show related objects inline in admin |
| **select_related** | Avoid N+1 queries when accessing related objects |

---

*← [Back to Django for Professionals](../README.md)*
