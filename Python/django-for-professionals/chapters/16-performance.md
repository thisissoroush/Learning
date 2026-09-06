# Chapter 16 — Performance

> *"Premature optimization is the root of all evil — but so is ignoring performance until your site is down. Use django-debug-toolbar first to find what's actually slow."*

---

## 🎯 Core Concept

Performance optimization follows a clear process: **measure first, then optimize**. The tools: django-debug-toolbar to find problems, `select_related`/`prefetch_related` to fix N+1 queries, database indexes to speed up lookups, and caching to avoid DB hits entirely.

---

## 🔍 Step 1: django-debug-toolbar

The most valuable Django performance tool. Shows every query, its timing, template rendering time, cache hits, and more.

### Installation

```python
# requirements.txt
django-debug-toolbar~=3.4

# settings.py
INSTALLED_APPS = [
    ...
    "debug_toolbar",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",  # First!
    ...
]

INTERNAL_IPS = ["127.0.0.1"]
```

```python
# django_project/urls.py
import debug_toolbar

urlpatterns = [
    path("__debug__/", include(debug_toolbar.urls)),
    ...
]
```

### What the Toolbar Shows

```
SQL Queries:    "You are making 47 queries to render this page"
                ↓ Fix with select_related/prefetch_related

Duplicates:     "Query X was called 13 times with identical SQL"
                ↓ Fix with caching

Templates:      "10 templates rendered in 23ms"

Cache:          "3 hits, 0 misses"
```

---

## ⚡ Step 2: Eliminate N+1 Queries

### The N+1 Problem

```python
# Bad: N+1 queries
books = Book.objects.all()          # Query 1: get all books
for book in books:
    reviews = book.reviews.all()    # Query 2, 3, 4... (one per book!)
                                    # 100 books = 101 queries!
```

### Fix with select_related (for ForeignKey / OneToOne)

```python
# Good: 2 queries total (JOIN)
books = Book.objects.select_related("author").all()

# Example: getting reviews with their authors
reviews = Review.objects.select_related("author", "book").all()
# Fetches Review + related Author + related Book in one query
```

### Fix with prefetch_related (for ManyToMany / reverse FK)

```python
# Good: 2 queries total (separate query + Python join)
books = Book.objects.prefetch_related("reviews").all()
# Query 1: all books
# Query 2: all reviews for those books
# Python joins them

for book in books:
    book.reviews.all()  # No extra queries! Already prefetched
```

---

## 📊 Database Indexes

Indexes dramatically speed up queries on large tables:

```python
# books/models.py
class Book(models.Model):
    title = models.CharField(max_length=200, db_index=True)  # Index this field
    author = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        indexes = [
            models.Index(fields=["title"]),          # Single field
            models.Index(fields=["author", "price"]),  # Composite index
        ]
```

### When to Add Indexes

```
Add index when:          Don't index:
- Filter by this field   - Fields rarely queried
- Order by this field    - Small tables (< 1000 rows)
- Join on this field     - Frequently written fields (slows writes)
                         - Boolean fields (low selectivity)

Django auto-indexes:
- Primary keys (always)
- ForeignKey fields (always)
- Fields with unique=True
```

---

## 💾 Caching

Store expensive computation results to avoid repeating them:

```python
# settings.py (Memcached)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
        "LOCATION": "127.0.0.1:11211",
    }
}

# Or Redis (more common today)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
    }
}
```

### Cache the Whole Page (Per-View Caching)

```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache for 15 minutes
def book_list(request):
    ...

# For CBVs:
from django.utils.decorators import method_decorator

class BookListView(ListView):
    @method_decorator(cache_page(60 * 15))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
```

### Cache Specific Data (Low-Level API)

```python
from django.core.cache import cache

def get_expensive_result():
    # Try cache first
    result = cache.get("expensive_key")
    if result is None:
        # Cache miss: compute it
        result = some_expensive_computation()
        cache.set("expensive_key", result, timeout=300)  # 5 minutes
    return result
```

---

## 🖼️ Front-End Performance

```python
# Compress/minify CSS and JS
pip install django-compressor

# settings.py
INSTALLED_APPS += ["compressor"]
STATICFILES_FINDERS = [
    ...
    "compressor.finders.CompressorFinder",
]
COMPRESS_ENABLED = not DEBUG
```

```html
{% load compress %}
{% compress css %}
<link rel="stylesheet" href="{% static 'css/styles.css' %}">
<link rel="stylesheet" href="{% static 'css/extra.css' %}">
{% endcompress %}
<!-- Outputs single, minified, fingerprinted CSS file -->
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **Measure first** | django-debug-toolbar reveals actual bottlenecks |
| **N+1 queries** | The most common Django performance bug |
| **select_related** | Fix FK/OneToOne N+1 with SQL JOIN |
| **prefetch_related** | Fix reverse FK/M2M N+1 with separate query + Python join |
| **Indexes** | Add to fields used in filter(), order_by(), JOIN |
| **Caching** | Last resort: cache expensive results in Redis/Memcached |

---

*← [Back to Django for Professionals](../README.md)*
