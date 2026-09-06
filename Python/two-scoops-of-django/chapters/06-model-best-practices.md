# Chapter 6 — Model Best Practices

> *"Models are the heart of your Django application. Getting them right is essential — bad models lead to bad architecture that's hard to fix later."*

---

## 🎯 Core Concept

Django models are more than database tables. They're the authoritative definition of your data structure AND the place for data-related business logic. This chapter covers model design principles: inheritance choices, field conventions, managers, and the "fat models" philosophy.

---

## 🏗️ Model Inheritance: Three Options

```
Option 1: Abstract Base Classes     (most common)
Option 2: Multi-table Inheritance   (avoid — creates hidden JOINs)
Option 3: Proxy Models              (for different behavior, same table)
```

### Option 1: Abstract Base Classes (Recommended)

```python
# Use when: multiple models share common fields
from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base class for timestamped records."""
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True   # ← NO database table created for this!


class IceCreamFlavor(TimeStampedModel):
    """Inherits created + modified from TimeStampedModel."""
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    # Database table: only IceCreamFlavor fields
    # No separate TimeStampedModel table!
```

### Option 2: Multi-table Inheritance (Generally Avoid)

```python
class Place(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=80)

class Restaurant(Place):  # ← Creates JOIN behind the scenes
    serves_hot_dogs = models.BooleanField(default=False)

# Every query on Restaurant requires a JOIN with Place!
# Hidden performance cost that surprises developers
```

### Option 3: Proxy Models

```python
class MyUser(AbstractUser):
    pass

class ActiveUser(MyUser):
    """Same table as MyUser, but with different default manager."""
    class Meta:
        proxy = True

    objects = ActiveUserManager()  # Only shows active users
```

---

## 📋 Field Best Practices

### null and blank Rules

```python
# Strings (CharField, TextField): use blank=True, NOT null=True
name = models.CharField(max_length=100, blank=True)
# Empty string is better than NULL for text fields

# Non-string fields: null=True IS appropriate
price = models.DecimalField(max_digits=6, decimal_places=2, null=True)
# NULL means "unknown price" (different from "price is 0")

# DateTimeField: null=True is fine for optional dates
end_date = models.DateTimeField(null=True, blank=True)
```

### Choices as Class Attributes

```python
# Good: Constants defined on the model
class IceCreamOrder(models.Model):
    VANILLA = 'vn'
    CHOCOLATE = 'ch'
    STRAWBERRY = 'st'

    FLAVOR_CHOICES = [
        (VANILLA, 'Vanilla'),
        (CHOCOLATE, 'Chocolate'),
        (STRAWBERRY, 'Strawberry'),
    ]

    flavor = models.CharField(max_length=2, choices=FLAVOR_CHOICES)

# Access as:
IceCreamOrder.objects.filter(flavor=IceCreamOrder.CHOCOLATE)
# Not: filter(flavor='ch')  ← Magic string, breaks on refactor!
```

### Django 3.x Enumeration Types

```python
class IceCreamOrder(models.Model):
    class Flavors(models.TextChoices):
        VANILLA = 'vn', 'Vanilla'
        CHOCOLATE = 'ch', 'Chocolate'
        STRAWBERRY = 'st', 'Strawberry'

    flavor = models.CharField(max_length=2, choices=Flavors.choices)

# Usage:
IceCreamOrder.objects.filter(flavor=IceCreamOrder.Flavors.CHOCOLATE)
```

---

## 🧑‍💼 Fat Models Philosophy

> *"Put more logic in models (and utility modules). Keep views thin and templates dumb."*

```
Fat Models:              Logic belongs here
Utility Modules:         Shared/complex business logic
Thin Views:              Should only handle HTTP concerns
Stupid Templates:        Only presentation, minimal logic
```

### Example: Moving Logic to the Model

```python
# Bad: Business logic in view
def ice_cream_view(request):
    flavor = Flavor.objects.get(pk=pk)
    avg_rating = Review.objects.filter(flavor=flavor).aggregate(avg=Avg('rating'))
    related = Flavor.objects.filter(category=flavor.category).exclude(pk=pk)[:5]
    ...

# Good: Business logic in model/manager
class Flavor(models.Model):
    @property
    def average_rating(self):
        return self.reviews.aggregate(avg=Avg('rating'))['avg']

    def get_related_flavors(self):
        return Flavor.objects.filter(
            category=self.category
        ).exclude(pk=self.pk)[:5]

# View becomes thin:
def ice_cream_view(request):
    flavor = Flavor.objects.get(pk=pk)
    # All logic encapsulated in model
```

---

## 📊 Custom Model Managers

```python
class PublishedManager(models.Manager):
    """Manager that only returns published flavors."""
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)


class Flavor(models.Model):
    title = models.CharField(max_length=100)
    is_published = models.BooleanField(default=False)

    objects = models.Manager()        # Default manager
    published = PublishedManager()    # Custom manager

# Usage:
Flavor.objects.all()           # All flavors
Flavor.published.all()         # Only published flavors
```

---

## 💡 Key Takeaways

| Practice | Why |
|----------|-----|
| **Abstract base classes** | Share fields without hidden JOINs |
| **blank=True not null=True for strings** | Empty string is better than NULL for text |
| **Choices as class constants** | Avoid magic strings, refactor safely |
| **Fat models, thin views** | Business logic belongs in models, not views |
| **Custom managers** | Named querysets that communicate intent |
| **TimeStampedModel everywhere** | created/modified fields on all models |

---

*← [Back to Two Scoops of Django](../README.md)*
