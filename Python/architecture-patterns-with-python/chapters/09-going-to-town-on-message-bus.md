# Chapter 9 — Going to Town on the Message Bus

> *"Once you have a message bus, you realize that everything can be an event handler. Your service layer becomes an orchestrator of events."*

---

## 🎯 Core Concept

The message bus becomes your primary control flow. Service functions become event handlers. Chain events to create complex workflows.

---

## 🎪 Service Layer as Event Handlers

Instead of services calling the domain, services HANDLE events from the domain.

```python
# ❌ BEFORE: Service layer calls domain
def allocate(orderid, sku, qty, uow):
    with uow:
        product = uow.products.get(sku)
        product.allocate(OrderLine(orderid, sku, qty))
        uow.commit()

# ✅ AFTER: Service layer is an event handler
def allocate_order(event: AllocateOrderCommand, uow):
    with uow:
        product = uow.products.get(event.sku)
        product.allocate(OrderLine(event.orderid, event.sku, event.qty))
        uow.commit()

HANDLERS = {
    AllocateOrderCommand: [allocate_order],
}
```

---

## 🔗 Event Chains

One event can trigger another event, which triggers another handler.

```python
# Event 1: Batch quantity changed
class BatchQuantityChanged:
    batchref: str
    new_qty: int

# Handler: Check if reallocation needed
def change_batch_quantity(event: BatchQuantityChanged, uow):
    with uow:
        batch = uow.batches.get(reference=event.batchref)
        product = batch.product
        
        if batch.available_quantity < 0:
            # This line raises an event!
            product.events.append(
                AllocationRequired(
                    orderid='order-123',
                    sku=product.sku,
                    qty=10,
                )
            )
        uow.commit()

# The AllocationRequired event is then handled by allocate_order()
HANDLERS = {
    BatchQuantityChanged: [change_batch_quantity],
    AllocationRequired: [allocate_order],
}
```

---

## 🧪 Testing Event Chains

```python
def test_reallocates_if_necessary():
    uow = FakeUnitOfWork()
    uow.products.add(Product("CHAIR", [
        Batch("batch1", "CHAIR", 100),
        Batch("batch2", "CHAIR", 50),
    ]))
    
    # Event 1: Allocate
    allocate_order(
        AllocateOrderCommand("order1", "CHAIR", 60),
        uow,
    )
    
    # Event 2: Batch quantity changed (triggers reallocation)
    change_batch_quantity(
        BatchQuantityChanged("batch1", 50),
        uow,
    )
    
    # Verify reallocation happened
    product = uow.products.get("CHAIR")
    assert len(product.events) == 1
    assert isinstance(product.events[0], AllocationRequired)
```

---

## 📊 Event-Driven Flow

```
User Request
    ↓
AllocateOrderCommand
    ↓
MessageBus.handle()
    ↓
allocate_order() handler
    ↓
Domain raises AllocationRequired event
    ↓
UoW.commit()
    ↓
MessageBus.handle(AllocationRequired)
    ↓
change_batch_quantity() handler
    ↓
More events raised...
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **Service = Handler** | Services are now event handlers |
| **Event Chains** | Events can trigger more events |
| **Control Flow** | Message bus drives application |
| **Decoupling** | Handlers don't call each other |
| **Testability** | Test event chains in isolation |

---

*← [Back to Architecture Patterns](../README.md)*
