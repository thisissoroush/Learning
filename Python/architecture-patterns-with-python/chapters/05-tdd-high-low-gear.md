# Chapter 5 — TDD in High and Low Gear

> *"High gear: drive fast by testing at the highest level. Low gear: slow, detailed tests when you need precision."*

---

## 🎯 Core Concept

TDD has two speeds. High gear tests exercise service layer + domain (fast, many of them). Low gear tests exercise integration with infrastructure (slower, fewer of them).

---

## 🏎️ The Test Pyramid

```
     /\
    /  \  ← E2E (1-5 tests, slowest)
   /────\
  /      \
 /────────\  ← Integration (10-20 tests)
/          \
/────────────\
   Unit Tests (50-100 tests, fastest)
```

**Principle:** Write as many unit tests as possible. Minimize integration and E2E.

---

## ⚡ High Gear: Unit Tests

Test domain + service layer with FakeRepository. No database.

```python
# HIGH GEAR: Fast unit test
def test_allocate_returns_batch_ref():
    repo = FakeRepository()
    repo.add(Product("RED-CHAIR", [Batch("batch1", "RED-CHAIR", 100)]))
    
    result = allocate("order1", "RED-CHAIR", 10, repo)
    
    assert result == "batch1"

def test_allocate_raises_out_of_stock():
    repo = FakeRepository()
    repo.add(Product("RED-CHAIR", [Batch("batch1", "RED-CHAIR", 5)]))
    
    with pytest.raises(OutOfStock):
        allocate("order1", "RED-CHAIR", 10, repo)
```

**Speed:** Milliseconds. Can run hundreds per second.

---

## 🔧 Low Gear: Integration Tests

Test service layer + real repository + database.

```python
# LOW GEAR: Slower integration test
def test_allocate_integrates_with_database():
    session = create_session()
    repo = SqlAlchemyRepository(session)
    
    product = Product("RED-CHAIR", [Batch("batch1", "RED-CHAIR", 100)])
    repo.add(product)
    session.commit()
    
    result = allocate("order1", "RED-CHAIR", 10, repo)
    
    assert result == "batch1"
    # Verify persisted to database
    retrieved = session.query(Product).filter_by(sku="RED-CHAIR").first()
    assert len(retrieved.batches[0].allocations) == 1
```

**Speed:** Seconds (one database roundtrip per test).

---

## 🌍 E2E: Through the Full Stack

Test through Flask API.

```python
# E2E: Full stack test (through Flask)
def test_allocate_api():
    response = client.post('/allocate', json={
        'orderid': 'order1',
        'sku': 'RED-CHAIR',
        'qty': 10,
    })
    
    assert response.status_code == 201
    assert response.json == {'batchref': 'batch1'}
```

**Speed:** Several seconds (network, database, Flask overhead).

---

## 📊 Test Counts (Typical)

| Layer | Count | Total Time |
|-------|-------|-----------|
| Unit | 80 | < 1 second |
| Integration | 15 | 5-10 seconds |
| E2E | 5 | 10-20 seconds |

Running all: ~30 seconds.

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **High Gear** | Service + domain, no database (fast) |
| **Low Gear** | Service + real repository (slower) |
| **Test Pyramid** | 80% unit, 15% integration, 5% E2E |
| **Refactoring Safety** | Unit tests let you refactor domain fearlessly |
| **E2E Minimalism** | Just enough to ensure integration works |

---

*← [Back to Architecture Patterns](../README.md)*
