# Chapter 7 — Aggregates and Consistency Boundaries

> *"An aggregate is a cluster of domain objects that can be treated as a single unit. The aggregate root is the only object that should be referenced from outside the aggregate."*

---

## 🎯 Core Concept

Aggregates define consistency boundaries. You never fetch a Batch directly; you fetch a Product and access its batches through it. One aggregate = one repository.

---

## 📦 The Aggregate Pattern

```python
class Product:  # ← Aggregate root
    def __init__(self, sku: str, batches: List[Batch]):
        self.sku = sku
        self.batches = batches  # ← Internal; don't access directly
        self.version_number = 0

# ❌ BAD: Direct access to internals
batch = batch_repository.get(id=1)  # No! Batches should be accessed through Product

# ✅ GOOD: Access through aggregate root
product = product_repository.get(sku="RED-CHAIR")
batch = product.batches[0]  # Access through Product
```

---

## 🔒 Consistency Boundaries

The aggregate root enforces business rules. You can't create invalid states.

```python
class Product:
    def allocate(self, line: OrderLine) -> str:
        try:
            batch = next(
                b for b in self.batches
                if b.can_allocate(line)
            )
            batch.allocate(line)
            return batch.reference
        except StopIteration:
            raise OutOfStock(f'Out of stock for {line.sku}')

# The aggregate ensures: you can't allocate more than available quantity
# You can't get into a bad state
```

---

## 🔄 Optimistic Concurrency

Use version numbers to detect lost updates when multiple processes update the same aggregate.

```python
class Product:
    def __init__(self, sku, batches):
        self.sku = sku
        self.batches = batches
        self.version_number = 0  # ← Incremented on each change

def allocate(orderid, sku, qty, uow):
    with uow:
        product = uow.products.get(sku)  # version_number = 5
        product.allocate(OrderLine(orderid, sku, qty))
        product.version_number += 1  # version_number = 6
        uow.commit()
        # Database updates WHERE version_number = 5
        # If someone else updated it, the update fails (no rows affected)

# SQL generated:
# UPDATE products SET version_number=6 WHERE sku='RED-CHAIR' AND version_number=5
```

---

## 📋 Aggregate Rules

1. **One root:** Product is the root; Batch is internal
2. **One repository:** `uow.products`, not `uow.batches`
3. **External references:** Use IDs, not objects
4. **Version number:** Detect concurrent updates

```python
class Product:
    def __init__(self, sku, batches, version_number=0):
        self.sku = sku
        self.batches = batches
        self.version_number = version_number
    
    def allocate(self, line):
        batch = next(b for b in self.batches if b.can_allocate(line))
        batch.allocate(line)
        self.version_number += 1  # Always increment
        return batch.reference
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **Aggregate Root** | Only thing accessed from outside |
| **Consistency Boundary** | Rules enforced at the root |
| **One Repository** | Per aggregate root, not per entity |
| **Version Number** | Detect concurrent updates |
| **Encapsulation** | Internal state is private |

---

*← [Back to Architecture Patterns](../README.md)*
