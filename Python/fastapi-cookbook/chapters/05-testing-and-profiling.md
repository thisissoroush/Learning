# Chapter 5 — Testing and Profiling

> **Project:** `protoapp`
> **Source:** [GitHub](https://github.com/PacktPublishing/FastAPI-Cookbook/tree/main/Chapter05)

---

## 🎯 What This Chapter Covers

Testing FastAPI apps with pytest and `TestClient`, writing fixtures, load testing with Locust, and request logging via middleware.

---

## 🏗️ The ProtoApp

```python
from fastapi import Depends, FastAPI, HTTPException, Request, status
from sqlalchemy.orm import Session
from protoapp.database import Item, SessionLocal
from protoapp.logging import client_logger

app = FastAPI()

@app.get("/home")
def read_main():
    return {"message": "Hello World"}

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/item", response_model=int, status_code=status.HTTP_201_CREATED)
def add_item(item: ItemSchema, db_session: Session = Depends(get_db_session)):
    db_item = Item(name=item.name, color=item.color)
    db_session.add(db_item)
    db_session.commit()
    db_session.refresh(db_item)
    return db_item.id

@app.get("/item/{item_id}", response_model=ItemSchema)
def get_item(item_id: int, db_session: Session = Depends(get_db_session)):
    item_db = db_session.query(Item).filter(Item.id == item_id).first()
    if item_db is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item_db

# HTTP middleware for logging every request
@app.middleware("http")
async def log_requests(request: Request, call_next):
    client_logger.info(
        f"method: {request.method}, "
        f"call: {request.url.path}, "
        f"ip: {request.client.host}"
    )
    response = await call_next(request)
    return response
```

---

## 🧪 Testing with pytest

### conftest.py — Shared Fixtures

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from protoapp.database import Base, Item
from main import app, get_db_session

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db_session] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

### Writing Tests

```python
from fastapi.testclient import TestClient

def test_read_home(client):
    response = client.get("/home")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_add_item(client):
    response = client.post("/item", json={"name": "Widget", "color": "blue"})
    assert response.status_code == 201
    item_id = response.json()
    assert isinstance(item_id, int)

def test_get_item(client):
    # Create first
    create_resp = client.post("/item", json={"name": "Widget", "color": "red"})
    item_id = create_resp.json()

    # Then retrieve
    get_resp = client.get(f"/item/{item_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Widget"

def test_get_item_not_found(client):
    response = client.get("/item/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

def test_add_item_invalid(client):
    # Missing required field
    response = client.post("/item", json={"name": "Widget"})
    assert response.status_code == 422   # Validation error
```

### Key Testing Patterns

```python
# 1. dependency_overrides — swap real DB with test DB
app.dependency_overrides[get_db_session] = override_get_db

# 2. scope="function" — fresh DB per test (isolation)
# scope="module" — shared DB across test file (faster but less isolated)

# 3. TestClient as context manager — handles lifespan events
with TestClient(app) as client:
    response = client.get("/home")

# 4. Test auth — pass token in headers
response = client.get("/protected", headers={"Authorization": "Bearer mytoken"})
```

---

## 📊 Load Testing with Locust

```python
# locustfile.py
from locust import HttpUser, task

class ProtoappUser(HttpUser):
    host = "http://localhost:8000"

    @task
    def hello_world(self):
        self.client.get("/home")

    @task
    def get_item(self):
        self.client.get("/item/1")
```

```bash
# Run Locust (opens web UI at http://localhost:8089)
locust -f locustfile.py

# Or headless: 10 users, 2 spawn rate, run 60s
locust -f locustfile.py --headless -u 10 -r 2 --run-time 60s --host http://localhost:8000
```

**What Locust measures:**
- **RPS** — requests per second
- **p50/p95/p99 latency** — percentile response times
- **Failure rate** — % of failed requests
- **Peak concurrent users** before degradation

---

## 🔑 Key Takeaways

- `dependency_overrides` swaps real dependencies in tests — the clean way to isolate DB, auth, config
- Use in-memory SQLite (`sqlite:///:memory:`) for fast, isolated DB tests
- `scope="function"` fixture + `drop_all()` in teardown = clean state per test
- `@app.middleware("http")` intercepts every request — good for logging, timing, tracing
- `call_next(request)` in middleware passes the request to the actual handler; middleware wraps it
- Locust simulates real user traffic with configurable concurrency — find your breaking point before production
