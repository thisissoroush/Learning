# Chapter 10 — Commands and Command Handlers

> *"Commands represent intent. Events represent facts. Commands can fail. Events have already happened."*

---

## 🎯 Core Concept

Distinguish between Commands (intent to do something) and Events (facts about what happened). They have different semantics, especially around error handling.

---

## ⚔️ Commands vs Events

| Command | Event |
|---------|-------|
| Intent: "Please do X" | Fact: "X happened" |
| Can fail and raise exceptions | Has already occurred |
| Should succeed or raise | No exceptions |
| Usually one handler | Many handlers can listen |
| Synchronous | Can be async |

```python
# Command: Intent to allocate
class AllocateOrderCommand:
    orderid: str
    sku: str
    qty: int

# Event: Allocation already happened
@dataclass
class OrderAllocatedEvent:
    orderid: str
    batchref: str

# Event: Allocation failed
@dataclass
class OutOfStockEvent:
    sku: str
```

---

## 🎯 Command Handlers

Handle commands by executing domain logic and raising events.

```python
def handle_allocate_order(
    cmd: AllocateOrderCommand,
    uow: AbstractUnitOfWork,
):
    with uow:
        product = uow.products.get(sku=cmd.sku)
        
        if product is None:
            raise InvalidSku(f'Invalid sku {cmd.sku}')
        
        line = OrderLine(cmd.orderid, cmd.sku, cmd.qty)
        batchref = product.allocate(line)
        
        if batchref is None:
            # Instead of raising, product already added OutOfStockEvent
            pass
        else:
            product.events.append(
                OrderAllocatedEvent(cmd.orderid, batchref)
            )
        
        uow.commit()

COMMAND_HANDLERS = {
    AllocateOrderCommand: handle_allocate_order,
}
```

---

## 🚨 Exception Handling

Commands can raise exceptions. Events should not.

```python
# ✅ GOOD: Command handler raises on error
def handle_allocate_order(cmd, uow):
    with uow:
        product = uow.products.get(sku=cmd.sku)
        if product is None:
            raise InvalidSku(f'Invalid sku {cmd.sku}')  # ← Raise!
        # ...

# ✅ GOOD: Event handler publishes new events instead of raising
def handle_out_of_stock_event(event: OutOfStockEvent, uow):
    # Don't raise exceptions
    # Instead, create compensating events or side effects
    email.send_mail(
        'stock@made.com',
        f'Out of stock for {event.sku}',
    )  # ← Just do it, don't raise
```

---

## 🧪 Testing Command Handlers

```python
def test_handle_allocate_order():
    uow = FakeUnitOfWork()
    uow.products.add(Product("RED-CHAIR", [Batch("batch1", "RED-CHAIR", 100)]))
    
    cmd = AllocateOrderCommand("order1", "RED-CHAIR", 10)
    handle_allocate_order(cmd, uow)
    
    product = uow.products.get("RED-CHAIR")
    assert len(product.events) == 1
    assert isinstance(product.events[0], OrderAllocatedEvent)

def test_handle_allocate_invalid_sku():
    uow = FakeUnitOfWork()
    
    cmd = AllocateOrderCommand("order1", "NONEXISTENT", 10)
    
    with pytest.raises(InvalidSku):
        handle_allocate_order(cmd, uow)
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **Commands** | Intent; can fail; raise exceptions |
| **Events** | Facts; immutable; no exceptions |
| **Handlers** | Commands raise events; events don't |
| **Semantics** | Different error handling strategies |
| **Testability** | Test both success and failure cases |

---

*← [Back to Architecture Patterns](../README.md)*
