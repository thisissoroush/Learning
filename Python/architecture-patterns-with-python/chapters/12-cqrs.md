# Chapter 12 — Command-Query Responsibility Segregation (CQRS)

> *"Your domain model is optimized for writing. Your read model should be optimized for reading. They don't have to be the same."*

---

## 🎯 Core Concept

CQRS separates read and write models. The write model (domain) is normalized and transactional. The read model is denormalized and fast.

---

## 📝 The Problem

### ❌ One Model Does It All

```python
# A single model trying to do both:
class Product:
    def __init__(self, sku, batches):
        self.sku = sku
        self.batches = batches
    
    def allocate(self, line):
        # Good for writing: complex business logic
        batch = next(b for b in self.batches if b.can_allocate(line))
        batch.allocate(line)
        return batch.reference
    
    def get_all_allocations(self):
        # Bad for reading: requires joins, lots of computation
        return [
            {'orderid': alloc.orderid, 'batchref': batch.reference}
            for batch in self.batches
            for alloc in batch.allocations
        ]
```

### ✅ Separate Models

```
Write (Domain Model)          Read (Denormalized View)
┌────────────────┐           ┌──────────────────┐
│ Product        │           │ allocations_view │
│ - batches      │   Event   │ - orderid        │
│ - allocate()   │ ─────────→│ - sku            │
│                │  Handler  │ - batchref       │
│ (normalized)   │           │ (denormalized)   │
└────────────────┘           └──────────────────┘
```

---

## 🎯 Write Model (Domain)

Normalized, complex, transactional. Enforces business rules.

```python
class Product:
    def allocate(self, line):
        batch = next(b for b in self.batches if b.can_allocate(line))
        batch.allocate(line)
        self.events.append(OrderAllocatedEvent(line.orderid, batch.reference))
        return batch.reference
```

---

## 📖 Read Model (Denormalized View)

Fast, flat, no joins. Updated by event handlers.

```python
# Table: allocations_view
#  orderid | sku       | batchref
# ─────────┼───────────┼──────────
#  order1  | RED-CHAIR | batch-001
#  order2  | RED-CHAIR | batch-001

# Query (very fast):
def get_allocations_for_order(orderid, session):
    return session.execute(
        'SELECT orderid, sku, batchref FROM allocations_view WHERE orderid = :orderid',
        {'orderid': orderid}
    )
```

---

## 🔄 Keeping Them In Sync

Event handler updates the read model.

```python
def update_allocations_view(event: OrderAllocatedEvent, uow):
    """Event handler that keeps the read model in sync."""
    uow.session.execute(
        'INSERT INTO allocations_view (orderid, sku, batchref) '
        'VALUES (:orderid, :sku, :batchref)',
        {
            'orderid': event.orderid,
            'sku': event.sku,
            'batchref': event.batchref,
        }
    )
    uow.commit()

HANDLERS = {
    OrderAllocatedEvent: [update_allocations_view],
}
```

---

## ✅ Benefits

| Benefit | How |
|---------|-----|
| **Write performance** | Domain optimized for correctness |
| **Read performance** | Denormalized views are fast |
| **Scalability** | Read replicas can be separate |
| **Flexibility** | Can change read model without affecting writes |

---

## ⚠️ Trade-offs

| Cost | When |
|------|------|
| **Eventual consistency** | Read model lags behind write model |
| **Complexity** | Need to keep models in sync |
| **Data duplication** | Denormalized data takes space |

---

## 🧪 Testing CQRS

```python
def test_allocations_view_updated():
    uow = FakeUnitOfWork()
    
    # Write: allocate an order
    product = Product("RED-CHAIR", [Batch("batch1", "RED-CHAIR", 100)])
    uow.products.add(product)
    product.allocate(OrderLine("order1", "RED-CHAIR", 10))
    uow.commit()
    
    # Update read model
    event = product.events[0]
    update_allocations_view(event, uow)
    
    # Read: query the view
    allocations = uow.session.execute(
        'SELECT * FROM allocations_view WHERE orderid = :orderid',
        {'orderid': 'order1'}
    )
    assert len(allocations) == 1
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **Write model** | Domain; normalized; transactional |
| **Read model** | Denormalized; fast; event-driven |
| **Event handlers** | Keep read model in sync |
| **Eventual consistency** | Reads may lag slightly |
| **When to use** | Complex domains with many reads |

---

*← [Back to Architecture Patterns](../README.md)*
