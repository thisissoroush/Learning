# Chapter 6 — Unit of Work Pattern

> *"The unit of work pattern provides a way to control the lifecycle of database transactions."*

---

## 🎯 Core Concept

The Unit of Work pattern abstracts a database transaction as a Python context manager. It groups multiple repository operations into a single atomic unit: everything commits together, or everything rolls back.

---

## 📦 The Pattern

```python
class AbstractUnitOfWork(ABC):
    products: AbstractRepository
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.rollback()
    
    @abstractmethod
    def commit(self):
        pass
    
    @abstractmethod
    def rollback(self):
        pass

class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory):
        self.session_factory = session_factory
    
    def __enter__(self):
        self.session = self.session_factory()
        self.products = SqlAlchemyRepository(self.session)
        return super().__enter__()
    
    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()
    
    def commit(self):
        self.session.commit()
    
    def rollback(self):
        self.session.rollback()

class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.products = FakeRepository()
        self.committed = False
    
    def commit(self):
        self.committed = True
    
    def rollback(self):
        pass
```

---

## 🎯 Usage: Atomic Operations

```python
def allocate(orderid, sku, qty, uow: AbstractUnitOfWork) -> str:
    with uow:
        product = uow.products.get(sku=sku)
        line = OrderLine(orderid, sku, qty)
        batchref = product.allocate(line)
        uow.commit()  # All changes committed atomically
        return batchref

# If an exception happens, __exit__ calls rollback() automatically
def reallocate(orderid, sku, qty, uow):
    with uow:
        product = uow.products.get(sku=sku)
        product.deallocate(OrderLine(orderid, sku, qty))  # Might fail
        uow.commit()
        # If deallocate() raised an exception, commit never happens
```

---

## ✅ Benefits

| Benefit | How |
|---------|-----|
| **Atomicity** | All-or-nothing transactions |
| **Rollback Safety** | Automatic rollback on exception |
| **Grouped repositories** | All repos in one place |
| **Testability** | FakeUnitOfWork for tests |

---

## 🧪 Testing with FakeUnitOfWork

```python
def test_allocate():
    uow = FakeUnitOfWork()
    uow.products.add(Product("RED-CHAIR", [Batch("batch1", "RED-CHAIR", 100)]))
    
    result = allocate("order1", "RED-CHAIR", 10, uow)
    
    assert result == "batch1"
    assert uow.committed  # Verify commit was called
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **Context Manager** | Idiomatic Python for scope management |
| **Atomic Operations** | Commit all repositories at once |
| **Automatic Rollback** | Exception in context exits safely |
| **Grouped Repos** | UoW holds all repository references |
| **Testable** | FakeUnitOfWork provides mock transactions |

---

*← [Back to Architecture Patterns](../README.md)*
