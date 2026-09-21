# Key Takeaways — Architecture Patterns with Python

> *Harry Percival & Bob Gregory — O'Reilly, 2020*

---

## 🏆 The One Sentence

> **Write code where business logic stays pure and decoupled by inverting dependencies: domain models don't know about databases; instead, databases adapt through repositories, services, and domain events.**

---

## 🎯 Part I: Building Domain-Driven Architecture

### 1. Domain Model First

PORO (Plain Old Python Object) with zero ORM dependencies. Let behavior drive design.

### 2. Dependency Inversion

Both depend on abstractions, not low-level on high-level.

```
❌ Business Logic → ORM → Database
✅ Business Logic ← Repository ← ORM
```

### 3. Repository Pattern

Abstract away persistence. Use add(), get(). Hide SQL.

```python
class AbstractRepository(ABC):
    @abstractmethod
    def add(self, product): pass
    @abstractmethod
    def get(self, sku) -> Product: pass
```

Swap real for fake in tests. Test domain without database.

### 4. Service Layer

Functions representing use cases. Orchestration only.

```python
def allocate(orderid, sku, qty, uow) -> str:
    with uow:
        product = uow.products.get(sku)
        batchref = product.allocate(OrderLine(orderid, sku, qty))
        uow.commit()
        return batchref
```

### 5. Unit of Work

Abstract transactions with context managers.

```python
with uow:
    product = uow.products.get(sku)
    product.allocate(line)
    uow.commit()  # All-or-nothing
```

### 6. Aggregate Pattern

One aggregate = one repository. Batches accessed through Product, not directly.

**Optimistic concurrency:** version_number prevents lost updates.

---

## 🎯 Part II: Event-Driven Architecture

### 7. Domain Events

Raise events, don't call side effects.

```python
self.events.append(OutOfStock(sku=line.sku))
```

### 8. Message Bus

Dict mapping events to handlers.

```python
HANDLERS = {
    OutOfStock: [send_notification_handler],
}
```

### 9. Commands vs Events

Commands = intent. Events = facts. Many handlers per event.

### 10. UoW Publishes Events

After commit, events collected and published automatically.

### 11. Internal vs External Events

Internal = message bus. External = Redis, Kafka.

### 12. CQRS

Write model (domain, normalized) vs read model (denormalized, fast).

---

## 🧪 Testing: High Gear (90%) vs Low Gear (10%)

High gear: pure domain + service, no infrastructure.
Low gear: service + fake repos.
E2E: through full stack.

---

*← [Back to Architecture Patterns](README.md)*
