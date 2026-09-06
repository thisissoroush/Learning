# Key Takeaways — Two Scoops of Django 3.x

> *Daniel Feldroy & Audrey Feldroy — 2021*

---

## 🏆 The One Sentence

> **Write Django like a professional: fat models, thin views, stupid templates, split settings, same database everywhere, test everything.**

---

## 📐 Core Philosophy

### 1. Fat Models, Thin Views, Stupid Templates
```
Fat Models:      Business logic lives here
Utility Modules: Shared complex logic
Thin Views:      Only HTTP concerns
Stupid Templates: Only presentation — minimal logic
```

### 2. Same Database Everywhere
```
Development: PostgreSQL → Production: PostgreSQL
NEVER: SQLite dev → PostgreSQL prod (hidden bugs!)
```

---

## 🏗️ Project Structure

### 3. Three-Level Layout
```
Repository Root/ → Django Project Root/ → Configuration Root/
```

### 4. Split Settings by Environment
```python
config/settings/base.py       # Common to all
config/settings/local.py      # Dev: DEBUG=True, debug_toolbar
config/settings/production.py # HTTPS, strict security
# Never: local_settings.py (not in VCS = settings sprawl)
```

### 5. Split Requirements to Match
```
requirements/base.txt        # Shared
requirements/local.txt       # -r base.txt + dev tools
requirements/production.txt  # -r base.txt + gunicorn
```

---

## 📱 App Design

### 6. Golden Rule: One App = One Task
- If you can't describe it in one sentence → split it
- Name apps clearly: `flavors/` not `stuff/`

---

## 🗃️ Models

### 7. Abstract Base Classes
```python
class TimeStampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True
```

### 8. Choices as Class Constants
```python
class Order(models.Model):
    class Flavors(models.TextChoices):
        CHOCOLATE = 'ch', 'Chocolate'
    flavor = models.CharField(max_length=2, choices=Flavors.choices)
# Order.objects.filter(flavor=Order.Flavors.CHOCOLATE)
```

### 9. Null/Blank Rules
```python
name = models.CharField(max_length=100, blank=True)     # Strings: blank, NOT null
end_date = models.DateTimeField(null=True, blank=True)  # Others: null OK
```

---

## 🔗 URLs and Views

### 10. Always Use URL Namespaces
```python
path("flavors/", include("flavors.urls", namespace="flavors"))
# Template: {% url "flavors:detail" pk=flavor.pk %}
```

### 11. Never Use locals() as Context
```python
# WRONG: return render(request, "t.html", locals())
# RIGHT: return render(request, "t.html", {"flavor": flavor, "ratings": ratings})
```

---

## 📝 Forms

### 12. Five Form Patterns
1. Simple ModelForm
2. Custom validators (`validators=` list)
3. `clean_field()` — single field
4. `clean()` — cross-field validation
5. Multiple forms per model (different roles)

---

## 🗄️ Queries

### 13. Fix N+1 Queries
```python
Review.objects.select_related("book", "author")   # FK → JOIN
Book.objects.prefetch_related("reviews")           # M2M → 2 queries
```

---

## 🔒 Security

### 14. Production Security
```python
DEBUG = False; SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SESSION_COOKIE_SECURE = True; CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"
```

### 15. Never Raw SQL with User Input
```python
# SAFE: Flavor.objects.filter(title=user_input)
# NEVER: cursor.execute(f"SELECT * WHERE title='{user_input}'")
```

---

## 🧪 Testing

### 16. Always Test Failure Paths
```python
def test_unauthenticated(self):
    response = self.client.get(reverse("protected"))
    self.assertEqual(response.status_code, 302)  # Redirect to login
```

### 17. Mock External Services
```python
@patch("myapp.views.send_email")
def test_sends_email(self, mock_email):
    mock_email.assert_called_once()
```

---

## 📐 Visual: The Architecture

```
HTTP Request → URLconf (namespaced) → Thin View → Template (stupid)
                                          ↓
                                    Fat Model
                                    ├── Validation
                                    ├── Business Logic
                                    ├── Custom Managers
                                    └── get_absolute_url()
                                          ↓
                                    PostgreSQL
```

---

*"Keep it simple, keep it working, keep it tested."*
