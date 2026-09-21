# Chapter 1 — Domain Modeling

> *"Most developers have never seen a domain model, only a data model."*

---

## 🎯 Core Concept

Domain modeling captures business rules in code as plain Python objects, BEFORE you think about persistence, HTTP, or infrastructure. Use TDD to build testable domain models.

---

## 📦 Entity, Value Object, and Domain Service

### Entity

Object with identity. Two orders with the same data are different.

```python
class Order:
    def __init__(self, orderid: str, sku: str, qty: int):
        self.orderid = orderid  # ← The identity
        self.sku = sku
        self.qty = qty
    
    def __eq__(self, other):
        return self.orderid == other.orderid  # Identity-based
```

### Value Object

Object without identity. Equality is content-based.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Batch:
    reference: str
    sku: str
    qty: int
    eta: date = None
    
    def can_allocate(self, line) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty
```

### Domain Service

Function for logic that doesn't belong to a single entity.

```python
def allocate(line: OrderLine, batches: List[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(f'Out of stock for sku {line.sku}')
```

---

## 🧪 Test-Driven Domain Modeling

```python
def test_prefers_earliest_batch():
    earliest = Batch("batch1", "SPOON", 100, eta=tomorrow)
    medium = Batch("batch2", "SPOON", 100, eta=next_week)
    
    line = OrderLine("order1", "SPOON", 10)
    allocate(line, [medium, earliest])
    
    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100

def test_raises_out_of_stock():
    batch = Batch("batch1", "RARE-ITEM", 10)
    line = OrderLine("order1", "RARE-ITEM", 20)
    
    with pytest.raises(OutOfStock):
        allocate(line, [batch])
```

The test expresses the business rule. The code implements it.

---

## 🏗️ The Allocation Domain

```python
@dataclass(frozen=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int

@dataclass(frozen=True)
class Batch:
    reference: str
    sku: str
    qty: int
    eta: date = None
    allocations: List[OrderLine] = field(default_factory=list)
    
    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty
    
    @property
    def available_quantity(self) -> int:
        return self.qty - sum(line.qty for line in self.allocations)
    
    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self.allocations.append(line)
    
    def __lt__(self, other):
        """For sorting: earlier ETA comes first."""
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta < other.eta

class Product:
    def __init__(self, sku: str, batches: List[Batch]):
        self.sku = sku
        self.batches = batches
    
    def allocate(self, line: OrderLine) -> str:
        try:
            batch = next(b for b in sorted(self.batches) if b.can_allocate(line))
            batch.allocate(line)
            return batch.reference
        except StopIteration:
            raise OutOfStock(f'Out of stock for sku {line.sku}')

class OutOfStock(Exception):
    pass
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **Entity** | Identity-based equality |
| **Value Object** | Content-based equality |
| **Domain Service** | Orchestrates multiple entities |
| **TDD First** | Tests encode business rules |
| **Zero Infrastructure** | Import only stdlib |

---

*← [Back to Architecture Patterns](../README.md)*
