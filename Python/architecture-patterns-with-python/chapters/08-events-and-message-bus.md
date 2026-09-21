# Chapter 8 — Events and the Message Bus

> *"Instead of having our model call side effects directly, we record domain events and let a message bus dispatch them to handlers."*

---

## 🎯 Core Concept

Domain models should not call email.send() or logging.info() directly. Instead, raise domain events and let handlers deal with side effects. This decouples the domain from infrastructure.

---

## 📢 Domain Events

A domain event is a record of something that happened in the business domain.

```python
# ✅ GOOD: Raise an event instead of calling side effects
class Product:
    def __init__(self, sku, batches):
        self.sku = sku
        self.batches = batches
        self.events = []  # ← Collect events here
    
    def allocate(self, line: OrderLine) -> str:
        try:
            batch = next(b for b in self.batches if b.can_allocate(line))
            batch.allocate(line)
            return batch.reference
        except StopIteration:
            self.events.append(OutOfStock(sku=line.sku))  # ← Just record it
            return None

# Event definition
@dataclass
class OutOfStock:
    sku: str
```

---

## 📫 Message Bus

Maps events to handler functions.

```python
def send_out_of_stock_notification(event: OutOfStock, uow):
    email.send_mail(
        'stock@made.com',
        f'Out of stock for {event.sku}',
    )

HANDLERS = {
    OutOfStock: [send_out_of_stock_notification],
}

def handle(event, uow):
    for handler in HANDLERS[type(event)]:
        handler(event, uow)
```

---

## 🔄 Full Flow with UoW

```python
def allocate(orderid, sku, qty, uow):
    with uow:
        product = uow.products.get(sku=sku)
        product.allocate(OrderLine(orderid, sku, qty))
        uow.commit()
        
        # After successful commit, publish events
        for event in product.events:
            handle(event, uow)
        
        product.events = []  # Clear for next use
```

---

## ✅ Benefits

| Benefit | How |
|---------|-----|
| **Pure domain** | Domain model knows nothing about email/logging |
| **Multiple handlers** | Many things can react to one event |
| **Easy to test** | Check event was raised, don't test side effects |
| **Decoupling** | New features (handlers) don't require domain changes |

---

## 🧪 Testing

```python
def test_out_of_stock_event_raised():
    uow = FakeUnitOfWork()
    product = Product("RARE-ITEM", [Batch("batch1", "RARE-ITEM", 5)])
    uow.products.add(product)
    
    product.allocate(OrderLine("order1", "RARE-ITEM", 10))  # Over capacity
    
    # Check the event was recorded
    assert len(product.events) == 1
    assert isinstance(product.events[0], OutOfStock)
    assert product.events[0].sku == "RARE-ITEM"
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **Domain Events** | Record what happened, don't cause side effects |
| **Message Bus** | Dispatch events to handlers |
| **Decoupling** | Domain doesn't know about email, logging, etc. |
| **Multiple Handlers** | One event, many handlers |
| **Testability** | Test event raised, not email sent |

---

*← [Back to Architecture Patterns](../README.md)*
