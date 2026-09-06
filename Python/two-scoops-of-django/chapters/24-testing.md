# Chapter 24 — Testing Stinks and Is a Waste of Money!

> *"Testing saves money, jobs, and lives. Every hour writing tests saves hours debugging in production."*

---

## 🎯 Core Concept

The chapter title is sarcastic. Testing is one of the most valuable investments. Untested code leads to production bugs and developer fear of change.

---

## 📁 Test Structure

```
myapp/
└── tests/
    ├── test_models.py
    ├── test_views.py
    ├── test_forms.py
    ├── test_api.py
    └── test_utils.py
```

---

## ✍️ Each Test Tests ONE Thing

```python
# GOOD: Focused tests
def test_flavor_creation(self):
    flavor = Flavor.objects.create(title="Vanilla", scoops_left=10)
    self.assertEqual(flavor.title, "Vanilla")

def test_flavor_str_representation(self):
    flavor = Flavor.objects.create(title="Chocolate")
    self.assertEqual(str(flavor), "Chocolate")

# BAD: Testing everything at once in one test
def test_all_the_things(self): ...
```

---

## 🔧 Use Request Factory for Views

```python
from django.test import RequestFactory, TestCase

class FlavorViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user("test", password="test123")

    def test_detail_view(self):
        request = self.factory.get(f"/flavors/{self.flavor.pk}/")
        request.user = self.user
        response = FlavorDetailView.as_view()(request, pk=self.flavor.pk)
        self.assertEqual(response.status_code, 200)
```

**RequestFactory = faster unit tests (no middleware)**
**TestClient = full integration tests (with middleware)**

---

## 📋 What to Test

```
✓ Every model method (especially get_absolute_url, clean)
✓ Every custom form validator
✓ Every view: both success AND failure paths
✓ Every API endpoint: auth and no-auth
✓ Permissions: logged-in (200) and logged-out (302)
✓ Error paths: invalid data, missing objects (404)
```

---

## 🎭 Mock External Services

```python
from unittest.mock import patch

@patch("myapp.views.send_activation_email")
def test_signup_sends_email(self, mock_send_email):
    self.client.post(reverse("signup"), {"email": "test@example.com"})
    mock_send_email.assert_called_once()  # Was it called? With correct args?
    # Tests remain isolated — no real emails sent!
```

---

## 📊 Test Coverage

```bash
$ pip install coverage
$ coverage run -m pytest
$ coverage report -m   # Shows % per file
$ coverage html        # Open htmlcov/index.html for details

# Aim for 80%+ meaningful coverage
# 100% can be counterproductive (testing trivial code)
```

---

## 💡 Key Takeaways

| Practice | Why |
|----------|-----|
| **Each test = one behavior** | Clear failure messages, easy debugging |
| **RequestFactory for unit tests** | Faster, no middleware overhead |
| **Test failure paths** | Most bugs hide in error handling |
| **Mock external services** | Tests shouldn't send real emails |
| **Coverage as guide** | 80%+ is good; 100% can be overkill |
| **CI runs tests on every commit** | Catch regressions immediately |

---

*← [Back to Two Scoops of Django](../README.md)*
