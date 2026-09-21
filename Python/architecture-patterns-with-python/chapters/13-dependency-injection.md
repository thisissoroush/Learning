# Chapter 13 — Dependency Injection and Bootstrapping

> *"Explicit dependencies are better than implicit ones. Make wiring explicit in a bootstrap script."*

---

## 🎯 Core Concept

Instead of singletons, globals, or import-time initialization, use explicit dependency injection via a bootstrap script. This makes all dependencies visible and testable.

---

## ❌ The Problem: Implicit Dependencies

```python
# BAD: Global database session
session = create_session()

def allocate_order(cmd):
    # Hidden dependency on global session!
    product = session.query(Product).filter_by(sku=cmd.sku).first()
    product.allocate(...)
    session.commit()

# Hard to test, hard to change, hard to reason about
```

---

## ✅ The Solution: Explicit Dependencies

```python
# GOOD: Pass dependencies explicitly
def allocate_order(cmd, uow):
    # Dependencies are clear!
    with uow:
        product = uow.products.get(cmd.sku)
        product.allocate(...)
        uow.commit()

# Now you can test with FakeUnitOfWork
# And wire different implementations at runtime
```

---

## 🔌 Bootstrap Script

Centralized place to wire everything up.

```python
# src/allocation/bootstrap.py

def bootstrap(start_orm=True):
    """Build and wire the application."""
    
    if start_orm:
        start_mappers()
    
    session_factory = create_session_factory()
    
    def get_unit_of_work():
        return SqlAlchemyUnitOfWork(session_factory)
    
    uow = get_unit_of_work()
    
    message_bus = messagebus.MessageBus(
        uow=uow,
        handlers={
            commands.AllocateOrderCommand: [
                handlers.allocate_order_handler,
            ],
            events.OutOfStockEvent: [
                handlers.send_notification_handler,
            ],
        },
    )
    
    return message_bus, uow

# In Flask:
message_bus, uow = bootstrap()

@app.route('/allocate', methods=['POST'])
def allocate_endpoint():
    cmd = commands.AllocateOrderCommand(
        request.json['orderid'],
        request.json['sku'],
        request.json['qty'],
    )
    message_bus.handle(cmd)
    return '', 201

# In tests:
message_bus, uow = bootstrap(start_orm=False)
```

---

## 🏭 Dependency Injection Patterns

### 1. Constructor Injection

```python
class AllocationHandler:
    def __init__(self, uow: AbstractUnitOfWork, email_service):
        self.uow = uow
        self.email = email_service
    
    def handle(self, cmd):
        with self.uow:
            ...
            self.email.send(...)
```

### 2. Closures / Partials

```python
from functools import partial

def allocate_order_handler(cmd, uow):
    with uow:
        ...

# Bind uow at bootstrap time
allocate_with_uow = partial(allocate_order_handler, uow=real_uow)

# In tests:
allocate_with_uow_fake = partial(allocate_order_handler, uow=fake_uow)
```

### 3. Service Locator (Avoid!)

```python
# ❌ NOT RECOMMENDED: Makes dependencies implicit again
class ServiceLocator:
    _services = {}
    
    @classmethod
    def register(cls, name, service):
        cls._services[name] = service
    
    @classmethod
    def get(cls, name):
        return cls._services[name]

def allocate(cmd):
    uow = ServiceLocator.get('uow')  # ← Hidden dependency!
    ...
```

---

## 🧪 Testing with Explicit Dependencies

```python
def test_allocate():
    # Build test dependencies explicitly
    fake_uow = FakeUnitOfWork()
    fake_email = FakeEmailService()
    
    # Inject into handler
    handler = AllocationHandler(fake_uow, fake_email)
    
    cmd = AllocateOrderCommand('order1', 'RED-CHAIR', 10)
    handler.handle(cmd)
    
    # Verify behavior
    assert fake_email.sent_count == 0  # No allocation, no email
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **Explicit** | Pass dependencies, don't hide them |
| **Bootstrap** | Centralized wiring script |
| **Constructor injection** | Cleanest pattern |
| **Closures/Partials** | Good for functional style |
| **Service locator** | Avoid; makes deps implicit again |

---

*← [Back to Architecture Patterns](../README.md)*
