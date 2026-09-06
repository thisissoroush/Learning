# Chapter 1 — Coding Style

> *"Code is read far more often than it is written. Write for the reader."*

---

## 🎯 Core Concept

Consistent, readable code is the foundation of every successful Django project. This chapter establishes the **style rules** the rest of the book builds on — following PEP 8, managing imports correctly, and following Django's own coding conventions.

---

## 📏 PEP 8 — The Python Style Bible

All Django projects follow [PEP 8](https://pep8.org/) — Python's official style guide:

```python
# Good: snake_case for variables and functions
ice_cream_flavor = "chocolate"
def get_flavor_count():
    return Flavor.objects.count()

# Good: PascalCase for classes
class IceCreamStore(models.Model):
    pass

# Good: UPPER_CASE for constants
MAX_SCOOPS = 5

# Bad: camelCase for Python variables
iceCreamFlavor = "chocolate"  # ← JavaScript style, not Python!
```

### The 79-Character Line Limit

PEP 8 recommends max 79 characters per line. When breaking long lines:

```python
# Long import — break with parentheses
from django.db.models import (
    BooleanField, CharField,
    DateTimeField, ForeignKey,
)

# Long function call — break with continuation
result = some_function(
    argument_one,
    argument_two,
    argument_three,
)
```

---

## 📦 Import Order

Django projects follow a specific import ordering:

```python
# 1. Standard library imports
import os
from datetime import datetime

# 2. Related third-party imports
import requests
from django.db import models
from django.contrib.auth.models import AbstractUser

# 3. Local application imports (relative)
from .models import Flavor
from .utils import get_flavor_name

# Separate each section with a blank line!
```

### Explicit Relative Imports

```python
# WRONG: Absolute import inside the same app
from cones.models import WaffleCone  # Breaks if you rename 'cones' app

# RIGHT: Relative import within the same app
from .models import WaffleCone   # ← This is portable!
```

Why relative imports? If you rename your app or move it, relative imports keep working. Absolute imports break.

---

## ❌ Avoid `import *`

```python
# BAD: Wildcard imports pollute namespace
from django.db.models import *
from django.conf import *

# If two modules both export "Model", which one do you get?
# Python can't tell you — neither can the reader!

# GOOD: Explicit imports
from django.db import models
from django.conf import settings
```

The one exception: `from myapp.views.flavors import *` in an `__init__.py` to re-export. But even then, use sparingly.

---

## 🔡 Django-Specific Naming Conventions

```python
# URL patterns: use underscores, not dashes
urlpatterns = [
    path("ice-cream/", views.ice_cream_list, name="ice_cream_list"),  # name: underscore ✓
    # path("ice-cream/", views.iceCreamList, name="ice-cream-list"),  # ← BAD
]

# Template blocks: use underscores
{% block content %}     ← Good
{% block page_content %}  ← Good
{% block page-content %}  ← Bad! Dashes in block names
```

---

## 💡 The Core Philosophy

```
Readable > Clever
Explicit > Implicit
Consistent > Perfect
```

### The Ice Cream Metaphor (Used Throughout the Book)

The authors use ice cream examples throughout because:
- Everyone understands ice cream
- It's a neutral domain (not biased toward any industry)
- It's fun!

```python
# Examples you'll see throughout the book:
class IceCreamStore(models.Model):
    flavor = models.CharField(max_length=100)
    scoops = models.IntegerField()

class WaffleCone(models.Model):
    store = models.ForeignKey(IceCreamStore, on_delete=models.CASCADE)
```

---

## 💡 Key Takeaways

| Rule | Why |
|------|-----|
| **Follow PEP 8** | Team consistency, readable code |
| **Import order: stdlib → third-party → local** | Predictable structure |
| **Relative imports within an app** | Portability when renaming |
| **Never `import *`** | Namespace pollution, hidden dependencies |
| **Underscores in URL names and template blocks** | Django convention |
| **snake_case for variables, PascalCase for classes** | Python convention |

---

*← [Back to Two Scoops of Django](../README.md)*
