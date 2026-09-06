# Chapter 5 — Pages App

> *"Testing can feel overwhelming at first, but it quickly becomes a bit boring. You'll use the same structure and techniques over and over again."*

---

## 🎯 Core Concept

Every webpage needs three things: a **URL**, a **View**, and a **Template**. This chapter builds the homepage for the Bookstore and establishes the **testing patterns** used throughout the book.

---

## 🏗️ The Django Request-Response Cycle

```
Browser → urls.py → views.py → templates/ → HTTP Response
  GET /       path("")    HomePageView    home.html
              include      TemplateView   extends _base.html
              pages.urls   renders
```

---

## 🗂️ Template Inheritance

```html
<!-- templates/_base.html -->
<!DOCTYPE html>
<html>
<head>
  <title>{% block title %}Bookstore{% endblock title %}</title>
</head>
<body>
  <div class="container">
    {% block content %}{% endblock content %}
  </div>
</body>
</html>
```

```html
<!-- templates/home.html -->
{% extends "_base.html" %}
{% block title %}Home{% endblock title %}
{% block content %}
  <h1>This is our home page.</h1>
{% endblock content %}
```

> **Why `_base.html` with underscore?** Convention: signals "inherited only, never rendered directly."

---

## 🔗 URLs and Views

```python
# django_project/urls.py
from django.urls import path, include
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("pages.urls")),
]

# pages/urls.py
from .views import HomePageView
urlpatterns = [path("", HomePageView.as_view(), name="home")]

# pages/views.py
from django.views.generic import TemplateView
class HomePageView(TemplateView):
    template_name = "home.html"
```

---

## 🧪 Testing Patterns

```python
# pages/tests.py
from django.test import SimpleTestCase
from django.urls import reverse, resolve
from .views import HomePageView

class HomepageTests(SimpleTestCase):
    def setUp(self):
        url = reverse("home")
        self.response = self.client.get(url)

    def test_url_exists_at_correct_location(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_homepage_template(self):
        self.assertTemplateUsed(self.response, "home.html")

    def test_homepage_contains_correct_html(self):
        self.assertContains(self.response, "home page")

    def test_homepage_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, "Hi there!")

    def test_homepage_url_resolves_homepageview(self):
        view = resolve("/")
        self.assertEqual(view.func.__name__, HomePageView.as_view().__name__)
```

### The 5-Test Pattern (Used for Every View)
1. URL exists at correct location (status 200)
2. Named URL works (reverse())
3. Correct template used
4. Page contains expected content
5. URL resolves to correct view class

### Running Tests

```bash
$ docker-compose exec web python manage.py test
# Ran 5 tests in 0.112s OK
```

---

## ⚙️ TEMPLATES Setting

```python
# settings.py
TEMPLATES = [{
    "DIRS": [BASE_DIR / "templates"],  # Project-wide templates directory
    "APP_DIRS": True,
    ...
}]
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **URL → View → Template** | The holy trinity of Django pages |
| **SimpleTestCase** | No database needed for static pages |
| **reverse()** | Never hardcode URLs in tests |
| **setUp()** | Put shared setup in setUp(), not in each test method |
| **5 tests per view** | URL, name, template, contains, resolves |

---

*← [Back to Django for Professionals](../README.md)*
