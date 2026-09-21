# Chapter 2 — Repository Pattern

> *"The repository pattern is an abstraction over persistent storage. It hides the boring details of data access by pretending that all of our data is in memory."*

---

## 🎯 Core Concept

Instead of scattering SQL queries throughout your code, abstract them behind a simple interface: add() and get(). This is the Repository pattern — it inverts the dependency between domain and database.

---

## ❌ The Problem: ORM Coupling

**Traditional approach:** Domain model inherits from ORM.

```python
# BAD: Domain model depends on SQLAlchemy
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    sku = Column(String(255), primary_key=True)
    batches = relationship('Batch')  # ← ORM-specific
```

Problem: 
- Can't test without a database
- Can't use the model without SQLAlchemy
- Can't easily switch to a different ORM

---

## ✅ The Solution: Invert the Dependency

**Repository pattern:** ORM depends on domain model, not vice versa.

```python
# 1. Domain model: pure Python, no ORM
class Product:
    def __init__(self, sku: str, batches: List[Batch]):
        self.sku = sku
        self.batches = batches
    
    def allocate(self, line: OrderLine) -> str:
        ...

# 2. Abstract repository (port)
class AbstractRepository(ABC):
    @abstractmethod
    def add(self, product: Product):
        pass
    
    @abstractmethod
    def get(self, sku: str) -> Product:
        pass

# 3. Concrete repository (adapter)
class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session
    
    def add(self, product):
        self.session.add(product)
    
    def get(self, sku):
        return self.session.query(Product).filter_by(sku=sku).first()

# 4. Fake repository (for tests)
class FakeRepository(AbstractRepository):
    def __init__(self):
        self.products = {}
    
    def add(self, product):
        self.products[product.sku] = product
    
    def get(self, sku):
        return self.products.get(sku)
```

---

## 🎯 Using the Repository

```python
# Service layer depends only on AbstractRepository
def allocate(orderid, sku, qty, repository):
    product = repository.get(sku)
    line = OrderLine(orderid, sku, qty)
    batchref = product.allocate(line)
    repository.add(product)
    return batchref

# In tests: inject FakeRepository
def test_allocate():
    repo = FakeRepository()
    repo.add(Product("RED-CHAIR", [Batch("batch1", "RED-CHAIR", 100)]))
    
    result = allocate("order1", "RED-CHAIR", 10, repo)
    assert result == "batch1"

# In production: inject SqlAlchemyRepository
def main():
    session = create_session()
    repo = SqlAlchemyRepository(session)
    result = allocate("order1", "RED-CHAIR", 10, repo)
```

---

## 🏗️ Ports and Adapters

**Port:** The abstract interface (AbstractRepository).
**Adapter:** The concrete implementation (SqlAlchemy, Fake, CSV-based, etc.).

```
Domain Model ← Abstract Repository (Port)
                 ↑
         ┌───────┼───────┐
         │       │       │
      Fake   SQLAlchemy  CSV
   (Adapter) (Adapter)  (Adapter)
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **ORM Coupling** | Traditional approach couples domain to database |
| **Repository** | Abstracts persistence behind add() and get() |
| **Inversion** | ORM depends on domain, not vice versa |
| **Testability** | FakeRepository enables unit testing without database |
| **Flexibility** | Swap implementations (Fake → SQLAlchemy → MongoDB) |

---

*← [Back to Architecture Patterns](../README.md)*
