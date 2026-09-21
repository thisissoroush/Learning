# Chapter 5 — Testing and Profiling

> **Project:** `protoapp`

---

## 🎯 What This Chapter Covers

How to properly test FastAPI apps with pytest — including overriding dependencies (swapping the real database for a test one), writing fixtures, structuring tests, and load-testing with Locust to find where your app breaks under real traffic.

---

## 🧠 The Testing Challenge — Dependencies

The biggest hurdle in FastAPI testing is **dependencies**. Your endpoint uses `Depends(get_db)` which opens a real PostgreSQL connection. In tests you want:
- A test database (SQLite in-memory or a test PostgreSQL schema)
- No side effects between tests (each test gets a fresh state)
- No network calls to external services

FastAPI solves this with `app.dependency_overrides`. You swap the real dependency for a test version — your endpoint code is unchanged, but it gets a test database instead.

---

## 🏗️ The App Under Test

```python
# protoapp/main.py
from fastapi import FastAPI, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from protoapp.database import Item, get_db_session
import logging

logger = logging.getLogger("uvicorn")
app = FastAPI()

class ItemSchema(BaseModel):
    name: str
    color: str

# Log every request using middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url.path} from {request.client.host}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

@app.get("/home")
def read_main():
    return {"message": "Hello World"}

@app.post("/items", response_model=int, status_code=status.HTTP_201_CREATED)
def add_item(item: ItemSchema, db: Session = Depends(get_db_session)):
    db_item = Item(name=item.name, color=item.color)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item.id      # return just the ID

@app.get("/items/{item_id}", response_model=ItemSchema)
def get_item(item_id: int, db: Session = Depends(get_db_session)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

---

## 🧪 Setting Up Tests — Fixtures and Overrides

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from protoapp.database import Base
from protoapp.main import app, get_db_session

# Use an in-memory SQLite database for tests — fast, isolated, no cleanup needed
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite-specific
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")   # function scope = fresh for each test
def db_session():
    """
    Create all tables before the test, drop them after.
    This guarantees each test starts with a completely clean database.
    """
    Base.metadata.create_all(bind=engine)   # create tables
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)  # destroy everything after test

@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a TestClient where the real database dependency is replaced
    with the test database session.
    """
    # This is the key: override the real dependency with the test one
    def override_get_db():
        try:
            yield db_session    # yields the test session instead of a real DB session
        finally:
            pass                # session lifecycle managed by db_session fixture

    app.dependency_overrides[get_db_session] = override_get_db

    # TestClient handles the lifespan (startup/shutdown) of the app
    with TestClient(app) as test_client:
        yield test_client

    # Clean up overrides after the test
    app.dependency_overrides.clear()
```

---

## ✅ Writing Good Tests

```python
# tests/test_main.py
from fastapi.testclient import TestClient

class TestHomepage:
    def test_returns_200(self, client: TestClient):
        response = client.get("/home")
        assert response.status_code == 200

    def test_returns_hello_world(self, client: TestClient):
        response = client.get("/home")
        assert response.json() == {"message": "Hello World"}


class TestItems:
    def test_create_item_returns_id(self, client: TestClient):
        """Creating an item should return its database ID."""
        response = client.post("/items", json={"name": "Widget", "color": "blue"})

        assert response.status_code == 201
        item_id = response.json()
        assert isinstance(item_id, int)    # should be an integer, not a string
        assert item_id > 0

    def test_create_and_retrieve_item(self, client: TestClient):
        """Full round-trip: create then fetch by id."""
        create_resp = client.post("/items", json={"name": "Gadget", "color": "red"})
        item_id = create_resp.json()

        get_resp = client.get(f"/items/{item_id}")
        assert get_resp.status_code == 200
        data = get_resp.json()
        assert data["name"] == "Gadget"
        assert data["color"] == "red"

    def test_get_nonexistent_item_returns_404(self, client: TestClient):
        response = client.get("/items/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_items_are_isolated_between_tests(self, client: TestClient):
        """This test proves the db fixture is fresh — item from previous test is gone."""
        # If tests shared state, this would find the item created above
        response = client.get("/items/1")
        assert response.status_code == 404   # fresh database — no items

    def test_create_item_validates_required_fields(self, client: TestClient):
        """Missing required fields should return 422, not 500."""
        response = client.post("/items", json={"name": "Only Name"})  # missing color
        assert response.status_code == 422
        errors = response.json()["detail"]
        # Pydantic tells us exactly which field failed
        field_names = [e["loc"][-1] for e in errors]
        assert "color" in field_names

    def test_multiple_items_are_independent(self, client: TestClient):
        """Create multiple items, verify each has its own ID."""
        id1 = client.post("/items", json={"name": "First", "color": "red"}).json()
        id2 = client.post("/items", json={"name": "Second", "color": "blue"}).json()
        id3 = client.post("/items", json={"name": "Third", "color": "green"}).json()

        assert id1 != id2 != id3    # all different IDs
        assert client.get(f"/items/{id2}").json()["name"] == "Second"
```

---

## 🔧 Testing with Authentication

```python
# tests/test_auth.py
import pytest

@pytest.fixture
def auth_headers(client: TestClient) -> dict:
    """Get auth headers for a test user — reusable across tests."""
    # Register and login
    client.post("/auth/register", json={"username": "testuser", "password": "secret"})
    login_resp = client.post("/auth/token", data={
        "username": "testuser",
        "password": "secret"
    })
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_protected_endpoint_requires_auth(client: TestClient):
    """Without a token, protected endpoints return 401."""
    response = client.get("/users/me")
    assert response.status_code == 401

def test_protected_endpoint_with_valid_token(client: TestClient, auth_headers: dict):
    """With a valid token, we get the user's info."""
    response = client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_expired_token_returns_401(client: TestClient):
    """An expired or malformed token should return 401."""
    headers = {"Authorization": "Bearer definitely.not.a.real.token"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 401
```

---

## 📊 Load Testing with Locust

Unit tests verify correctness. Locust verifies **performance** — how many concurrent users can your app handle before it breaks?

```python
# locustfile.py
from locust import HttpUser, task, between
import random

class ProtoAppUser(HttpUser):
    """
    Simulates a real user of the app.
    wait_time = how long to pause between actions (simulates real user think time)
    """
    host = "http://localhost:8000"
    wait_time = between(1, 3)    # wait 1-3 seconds between requests

    def on_start(self):
        """Called once when this simulated user starts — like a browser session."""
        # Create some items to work with
        self.created_ids = []
        for i in range(3):
            resp = self.client.post("/items", json={"name": f"item_{i}", "color": "blue"})
            if resp.status_code == 201:
                self.created_ids.append(resp.json())

    @task(3)    # weight 3: this task runs 3x more often than weight-1 tasks
    def browse_items(self):
        """Most users browse more than they create."""
        if self.created_ids:
            item_id = random.choice(self.created_ids)
            self.client.get(f"/items/{item_id}", name="/items/[id]")

    @task(1)
    def create_item(self):
        """Some users create new items."""
        colors = ["red", "blue", "green", "yellow", "purple"]
        resp = self.client.post("/items", json={
            "name": f"item_{random.randint(1000, 9999)}",
            "color": random.choice(colors),
        })
        if resp.status_code == 201:
            self.created_ids.append(resp.json())

    @task(2)
    def visit_home(self):
        self.client.get("/home")
```

```bash
# Start your app
uvicorn protoapp.main:app --host 0.0.0.0 --port 8000

# Run Locust — opens browser at http://localhost:8089
locust -f locustfile.py

# Headless mode for CI:
# 50 users, ramp up at 5/second, run for 60 seconds
locust -f locustfile.py --headless -u 50 -r 5 --run-time 60s
```

**What to look for in results:**

| Metric | Good | Warning | Bad |
|--------|------|---------|-----|
| Failure rate | 0% | <1% | >1% |
| p95 latency | <200ms | <500ms | >1s |
| RPS | Stable | Stable | Dropping |
| Errors | None | Timeouts | 500s |

---

## 🔑 Key Takeaways

| Concept | The "why" |
|---------|-----------|
| `dependency_overrides[get_db] = test_db` | Swap real DB for test DB without changing any endpoint code |
| `scope="function"` + `drop_all()` | Each test gets a fresh database — prevents test order dependency |
| SQLite `:///:memory:` | Fastest possible test DB — lives in RAM, auto-destroyed |
| Group tests in classes | `TestItems`, `TestAuth` — easier to `pytest -k TestItems` to run one group |
| `response.json()["detail"]` | FastAPI validation errors live here — check both status code AND error body |
| `@task(weight)` in Locust | Higher weight = runs more often — model realistic usage patterns |
| `name="/items/[id]"` in Locust | Groups parameterized URLs in reports — otherwise each ID shows separately |
