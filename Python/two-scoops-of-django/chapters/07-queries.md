# Chapter 7 — Queries and the Database Layer

> *"Use the ORM as much as possible. It exists to make your code database-agnostic, readable, and safe from SQL injection."*

---

## 🎯 Core Concept

The Django ORM is one of the most powerful aspects of Django. This chapter covers how to write efficient, correct queries — using lazy evaluation, chaining, Q objects, and avoiding common pitfalls like N+1 queries and queryset evaluation in unexpected places.

---

## 🦥 Lazy QuerySets

Django QuerySets are **lazy** — they don't hit the database until you actually need the data:

```python
# This does NOT hit the database:
flavors = Flavor.objects.filter(is_published=True)
flavors = flavors.filter(category='chocolate')
flavors = flavors.order_by('name')

# Database hit happens HERE (iteration forces evaluation):
for flavor in flavors:
    print(flavor.name)

# Or: len(), list(), bool(), repr(), [slice], get()
count = len(flavors)    # Hits DB
count = flavors.count() # Single COUNT query (better!)
```

---

## 🔗 Queryset Chaining

```python
# Build queries incrementally — each filter() returns new queryset
published = Flavor.objects.filter(is_published=True)
chocolate = published.filter(category='chocolate')
top_chocolate = chocolate.order_by('-rating')[:10]

# Equivalent one-liner:
Flavor.objects.filter(is_published=True, category='chocolate').order_by('-rating')[:10]

# Both generate ONE SQL query with all conditions
```

---

## ❌ Common Pitfall: N+1 Queries

```python
# BAD: N+1 queries (1 for all orders + 1 per order for flavor)
orders = IceCreamOrder.objects.all()
for order in orders:
    print(order.flavor.name)  # ← DB hit every iteration!
# 100 orders = 101 queries!

# GOOD: select_related (single JOIN query)
orders = IceCreamOrder.objects.select_related('flavor')
for order in orders:
    print(order.flavor.name)  # ← No DB hit (already fetched)
# 100 orders = 1 query!
```

### When to Use What

```
select_related   → FK and OneToOne relationships
                   Follows foreign keys (forward)
                   Uses SQL JOIN

prefetch_related → ManyToMany and reverse FK
                   Separate query + Python join
                   Better for multiple or complex relationships
```

---

## 🔀 Q Objects for Complex Queries

```python
from django.db.models import Q

# OR conditions:
Flavor.objects.filter(
    Q(title__startswith='Chocolate') | Q(title__startswith='Vanilla')
)

# AND + OR combined:
Flavor.objects.filter(
    Q(is_published=True) & (Q(title__icontains='chocolate') | Q(price__lt=5))
)

# NOT:
Flavor.objects.filter(~Q(title__icontains='boring'))

# Dynamic queries:
conditions = Q()
if user_search:
    conditions |= Q(title__icontains=user_search)
if category:
    conditions &= Q(category=category)

Flavor.objects.filter(conditions)
```

---

## 📊 Aggregation and Annotation

```python
from django.db.models import Avg, Count, Max, Min, Sum

# Aggregate across ALL results:
stats = Flavor.objects.aggregate(
    avg_price=Avg('price'),
    total_count=Count('id'),
    max_price=Max('price'),
)
# Returns: {'avg_price': 4.5, 'total_count': 150, 'max_price': 12.99}

# Annotate: add computed value per result
flavors_with_review_count = Flavor.objects.annotate(
    review_count=Count('reviews')
).order_by('-review_count')

for flavor in flavors_with_review_count:
    print(f"{flavor.title}: {flavor.review_count} reviews")
```

---

## 🛡️ Raw SQL: Use Carefully

```python
# Option 1: extra() — avoid if possible (deprecated intent)
Flavor.objects.extra(
    select={'lower_title': 'lower(title)'}
)

# Option 2: RawSQL() — for expressions, not full queries
from django.db.models.expressions import RawSQL
Flavor.objects.annotate(
    lower_name=RawSQL('lower(title)', [])
)

# Option 3: Raw queries — last resort
Flavor.objects.raw('SELECT * FROM flavors_flavor WHERE is_published = %s', [True])

# Never ever do:
Flavor.objects.raw(f'SELECT * WHERE title = {user_input}')  # SQL INJECTION!
```

---

## 🏃 Queryset Performance Tips

```python
# 1. Use exists() instead of count() for boolean checks
if Flavor.objects.filter(is_published=True).exists():  # fast
if Flavor.objects.filter(is_published=True).count() > 0:  # slower

# 2. Use values() or values_list() when you don't need model instances
Flavor.objects.values('id', 'title')   # Returns dicts
Flavor.objects.values_list('id', flat=True)  # Returns list of IDs

# 3. Use iterator() for large querysets to avoid memory issues
for flavor in Flavor.objects.iterator():  # Streams from DB
    process(flavor)

# 4. Use only() or defer() to load specific fields
Flavor.objects.only('title', 'price')   # Load ONLY these
Flavor.objects.defer('description')     # Load all EXCEPT this
```

---

## 🔒 Database Transactions

```python
from django.db import transaction

# Wrap in a transaction:
@transaction.atomic
def create_order_with_payment(user, flavor, payment_info):
    order = Order.objects.create(user=user, flavor=flavor)
    payment = process_payment(payment_info)  # If this fails...
    order.payment = payment  # ...this won't be saved
    order.save()
    # If ANY exception: entire transaction rolled back

# Or as context manager:
with transaction.atomic():
    Order.objects.create(...)
    Payment.objects.create(...)
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **Lazy QuerySets** | Don't evaluate until you need results |
| **Chain filters** | Each filter() returns a new queryset — build incrementally |
| **select_related for FK** | Eliminate N+1 queries with a JOIN |
| **prefetch_related for M2M** | Separate query + Python join for complex relations |
| **Q objects** | Construct OR/AND/NOT conditions dynamically |
| **Aggregate vs Annotate** | aggregate() = one value; annotate() = value per row |
| **exists() over count()** | Faster for boolean existence checks |

---

*← [Back to Two Scoops of Django](../README.md)*
