# Chapter 4 — Flask API and Service Layer

> *"The service layer is a thin boundary around our domain model that mediates between the web framework and the business logic."*

---

## 🎯 Core Concept

The service layer defines your use cases as simple functions. It's the API between adapters (Flask) and domain logic. Thin Flask views call service layer functions, which call the domain model.

---

## 🏗️ The Three-Layer Structure

```
Flask View (Adapter)
    ↓
Service Layer Function (Use Case)
    ↓
Domain Model (Business Logic)
    ↓
Repository (Persistence)
```

---

## 📝 Example: Flask View

```python
@app.route('/allocate', methods=['POST'])
def allocate_endpoint():
    line = OrderLine(
        request.json['orderid'],
        request.json['sku'],
        request.json['qty'],
    )
    
    try:
        batchref = allocate(
            request.json['orderid'],
            request.json['sku'],
            request.json['qty'],
            repo=repository,
        )
    except InvalidSku as e:
        return {'error': str(e)}, 400
    except OutOfStock as e:
        return {'error': str(e)}, 400
    
    return {'batchref': batchref}, 201
```

### The Service Layer Function

```python
def allocate(orderid: str, sku: str, qty: int, repo) -> str:
    """
    Allocate an order line to a batch.
    This is the single use case for order allocation.
    """
    product = repo.get(sku=sku)
    if product is None:
        raise InvalidSku(f'Invalid sku {sku}')
    
    line = OrderLine(orderid, sku, qty)
    batchref = product.allocate(line)
    repo.add(product)
    return batchref
```

---

## ✅ Benefits of the Service Layer

| Benefit | How |
|---------|-----|
| **Thin adapters** | Flask views are just HTTP plumbing |
| **Reusable logic** | Use same service function in CLI, API, tests |
| **Testable at high level** | Test service + domain without Flask |
| **Single use case source** | All use cases in one place |
| **Clear API** | Service functions define what your app does |

---

## 🧪 Testing Without Flask

```python
# No Flask needed! Just call the service function
def test_allocate():
    repo = FakeRepository()
    repo.add(Product("RED-CHAIR", [Batch("batch1", "RED-CHAIR", 100)]))
    
    result = allocate("order1", "RED-CHAIR", 10, repo)
    assert result == "batch1"

def test_allocate_invalid_sku():
    repo = FakeRepository()
    
    with pytest.raises(InvalidSku):
        allocate("order1", "NONEXISTENT", 10, repo)
```

---

## 📁 Folder Structure

```
src/
├── allocation/
│   ├── domain/
│   │   ├── __init__.py
│   │   └── model.py          # Entity, Value Object, Aggregate
│   ├── service_layer/
│   │   ├── __init__.py
│   │   └── services.py       # Service layer functions (use cases)
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── orm.py            # ORM mapping
│   │   └── repository.py     # Repository implementation
│   └── entrypoints/
│       ├── __init__.py
│       └── flask_app.py      # Flask views
└── tests/
    ├── unit/
    │   └── test_services.py
    ├── integration/
    │   └── test_repository.py
    └── e2e/
        └── test_api.py
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **Service Layer** | Defines use cases as functions |
| **Thin Adapters** | Flask/Django views are only HTTP plumbing |
| **Separation** | Domain logic separate from web logic |
| **Testability** | Service functions testable without Flask |
| **Reusability** | Same service works for API, CLI, tests |

---

*← [Back to Architecture Patterns](../README.md)*
