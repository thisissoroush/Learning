# Chapter 3 — Coupling and Abstractions

> *"Choosing the right abstraction is tricky. It requires understanding what varies and what's stable."*

---

## 🎯 Core Concept

Not all abstractions are good. A bad abstraction is worse than no abstraction. This chapter teaches how to choose abstractions wisely by understanding coupling and testability.

---

## 🔗 Understanding Coupling

### Coupling = Dependencies

The more your code depends on other code, the harder it is to change.

```python
# ❌ Tightly coupled
class Allocate:
    def execute(self, order):
        # Depends on database
        product = database.query(Product).filter_by(sku=order.sku)
        # Depends on email
        if not batch:
            email.send_mail(...)
        # Can't test without database and email

# ✅ Loosely coupled
class Allocate:
    def __init__(self, repository, message_bus):
        self.repository = repository
        self.message_bus = message_bus
    
    def execute(self, order):
        # Depends on abstraction, not concrete implementation
        product = self.repository.get(order.sku)
        if not batch:
            self.message_bus.handle(OutOfStockEvent(order.sku))
        # Can test with FakeRepository and FakeMessageBus
```

---

## 🎯 When to Introduce Abstractions

### Start Concrete, Refactor to Abstract

**Rule:** Don't introduce an abstraction until you have two implementations.

```python
# Step 1: Concrete implementation
def allocate(orderid, sku, qty):
    session = create_session()
    product = session.query(Product).filter_by(sku=sku).first()
    ...
    session.commit()

# Step 2: Need to test? Introduce abstraction
class AbstractRepository(ABC):
    def get(self, sku): pass

class RealRepository(AbstractRepository):
    def get(self, sku):
        session = create_session()
        return session.query(Product).filter_by(sku=sku).first()

class FakeRepository(AbstractRepository):
    def __init__(self):
        self.products = {}
    
    def get(self, sku):
        return self.products.get(sku)

# Step 3: Refactor to use abstraction
def allocate(orderid, sku, qty, repository):
    product = repository.get(sku)
    ...
```

---

## ✅ Edge-to-Edge Testing

The key pattern for testing without mocks: **use real implementations of abstractions, only fake the expensive ones**.

```python
# ✅ GOOD: Test edge to edge with minimal fakes
def test_allocate():
    repository = FakeRepository()  # Fake (in-memory)
    repository.add(Product("RED-CHAIR", [Batch("batch1", "RED-CHAIR", 100)]))
    
    line = OrderLine("order1", "RED-CHAIR", 10)
    result = allocate(line, repository)  # Real domain logic
    
    assert result == "batch1"

# ❌ BAD: Over-mocked test
def test_allocate():
    repository = Mock()
    repository.get.return_value = Product(...)
    batch = Mock()
    batch.can_allocate.return_value = True
    
    # Now your test is testing mocks, not real code!
```

---

## 🏗️ The Abstraction Hierarchy

```
✅ Good abstraction:
   Narrow, specific interface (add, get, delete)
   Easy to implement concretely
   Easy to fake for tests
   
❌ Bad abstraction:
   Too broad (.query(), .filter(), .join(), ...)
   Hard to implement on new backends
   Difficult to replace with fake
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **Coupling** | Dependencies = change cost |
| **Two Implementations Rule** | Don't abstract until you need two versions |
| **Edge-to-Edge Testing** | Real code, fake external dependencies |
| **Narrow Interfaces** | Small, specific abstractions are better |
| **Avoid Over-Mocking** | Tests should test real code, not mocks |

---

*← [Back to Architecture Patterns](../README.md)*
