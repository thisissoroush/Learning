# Chapter 15 — Search

> *"Django's ORM provides powerful search capabilities through icontains lookups and Q objects for complex queries — no third-party search engine needed for most sites."*

---

## 🎯 Core Concept

Most Django sites don't need Elasticsearch or Solr. Django's ORM with **`icontains`** and **`Q objects`** handles the majority of search use cases. This chapter adds a working search feature to the Bookstore.

---

## 🔍 Basic Search: icontains

```python
# books/views.py
from django.db.models import Q
from django.views.generic import ListView
from .models import Book


class SearchResultsView(ListView):
    model = Book
    context_object_name = "book_list"
    template_name = "books/search_results.html"

    def get_queryset(self):
        query = self.request.GET.get("q")
        return Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )
```

### icontains vs iexact vs contains

```python
# contains — case-sensitive, substring match
Book.objects.filter(title__contains="harry")    # "Harry" won't match!

# icontains — case-insensitive, substring match
Book.objects.filter(title__icontains="harry")   # Matches "Harry", "HARRY", "harry"

# iexact — case-insensitive, exact match
Book.objects.filter(title__iexact="harry potter")  # Must be exact title
```

---

## 🔀 Q Objects — Complex Queries

Q objects allow combining conditions with `|` (OR), `&` (AND), `~` (NOT):

```python
# OR: books matching title OR author
Book.objects.filter(
    Q(title__icontains=query) | Q(author__icontains=query)
)

# AND: books that are cheap AND by this author
Book.objects.filter(
    Q(price__lt=20) & Q(author__icontains="Rowling")
)

# NOT: books NOT by this author
Book.objects.filter(~Q(author__icontains="Rowling"))

# Complex: (title match OR author match) AND affordable
Book.objects.filter(
    (Q(title__icontains=query) | Q(author__icontains=query))
    & Q(price__lt=50)
)
```

---

## 🔗 Search URL and Form

```python
# books/urls.py
urlpatterns = [
    path("", BookListView.as_view(), name="book_list"),
    path("<uuid:pk>/", BookDetailView.as_view(), name="book_detail"),
    path("search/", SearchResultsView.as_view(), name="search_results"),
]
```

```html
<!-- templates/_base.html - Add search form to navigation -->
<form action="{% url 'search_results' %}" method="get">
  <input name="q" type="text" placeholder="Search books...">
  <button type="submit">Search</button>
</form>
```

```html
<!-- templates/books/search_results.html -->
{% extends "_base.html" %}

{% block title %}Search{% endblock title %}

{% block content %}
  <h2>Search Results</h2>
  {% for book in book_list %}
    <div>
      <h3><a href="{{ book.get_absolute_url }}">{{ book.title }}</a></h3>
      <p>{{ book.author }}</p>
    </div>
  {% empty %}
    <p>No books found for your search.</p>
  {% endfor %}
{% endblock content %}
```

---

## 🔍 Full-Text Search with PostgreSQL

For larger datasets, PostgreSQL's built-in full-text search is more powerful:

```python
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

class SearchResultsView(ListView):
    def get_queryset(self):
        query = self.request.GET.get("q")
        search_vector = SearchVector("title", "author")  # Fields to search
        search_query = SearchQuery(query)
        return (
            Book.objects.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            )
            .filter(search=search_query)
            .order_by("-rank")  # Most relevant first
        )
```

Benefits of PostgreSQL full-text:
- Stemming (search "run" finds "running", "ran")
- Stop words (ignores "the", "a", "is")
- Relevance ranking

---

## 🧪 Testing Search

```python
# books/tests.py
class SearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.book = Book.objects.create(
            title="Harry Potter", author="JK Rowling", price="25.00"
        )

    def test_search_results_page(self):
        response = self.client.get(reverse("search_results") + "?q=potter")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Harry Potter")

    def test_search_by_author(self):
        response = self.client.get(reverse("search_results") + "?q=Rowling")
        self.assertContains(response, "Harry Potter")

    def test_search_no_results(self):
        response = self.client.get(reverse("search_results") + "?q=notexist")
        self.assertContains(response, "No books found")
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **icontains** | Case-insensitive substring search — good enough for most sites |
| **Q objects** | Combine conditions with `|` (OR), `&` (AND), `~` (NOT) |
| **GET parameters** | `request.GET.get("q")` reads ?q= from URL |
| **`{% empty %}`** | Django template tag for empty querysets |
| **PostgreSQL full-text** | Use for advanced: stemming, relevance ranking |
| **Search in navbar** | Put search form in `_base.html` for site-wide access |

---

*← [Back to Django for Professionals](../README.md)*
