# 🧪 Testing in Python — Interview Questions (Junior → Architect)

Covers pytest, unittest.mock, FastAPI/Django testing, testcontainers, and testing strategy.

---

## 🟢 Junior Level

---

### 1. What is pytest and how do you write a basic test?

**A:**

```python
# test_calculator.py
def add(a: int, b: int) -> int:
    return a + b

def test_add():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, 1) == 0

def test_add_zero():
    assert add(0, 0) == 0

# Run
# pytest                        # all tests
# pytest test_calculator.py     # specific file
# pytest -v                     # verbose
# pytest -k "test_add"          # filter by name
# pytest -x                     # stop on first failure
# pytest --tb=short             # shorter traceback
```

---

### 2. How do you use pytest fixtures?

**A:**

```python
import pytest

@pytest.fixture
def user():
    """Provides a test user."""
    return {"id": 1, "name": "Alice", "email": "alice@test.com"}

@pytest.fixture
def db():
    """Sets up and tears down a test database."""
    connection = create_test_db_connection()
    run_migrations(connection)
    yield connection  # teardown happens after yield
    connection.execute("DROP SCHEMA public CASCADE")
    connection.close()

def test_create_order(db, user):
    order = create_order(db, user_id=user["id"])
    assert order["user_id"] == user["id"]

# Scope — how often fixture is created
@pytest.fixture(scope="session")   # once per test session
@pytest.fixture(scope="module")    # once per module
@pytest.fixture(scope="class")     # once per class
@pytest.fixture(scope="function")  # default — once per test

# autouse — apply to all tests automatically
@pytest.fixture(autouse=True)
def reset_state():
    yield
    cleanup_global_state()
```

---

### 3. How do you parameterize tests?

**A:**

```python
import pytest

@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (-1, 1, 0),
    (0, 0, 0),
    (100, -50, 50),
])
def test_add(a, b, expected):
    assert add(a, b) == expected

# Multiple parameter sets
@pytest.mark.parametrize("email", [
    "",
    "not-an-email",
    "missing@",
    "@nodomain.com",
])
def test_invalid_email(email):
    with pytest.raises(ValueError, match="invalid email"):
        validate_email(email)

# Parametrize with IDs for readable output
@pytest.mark.parametrize("status,expected_msg", [
    pytest.param("pending",   "Order is pending",   id="pending"),
    pytest.param("shipped",   "Order is shipped",   id="shipped"),
    pytest.param("delivered", "Order is delivered", id="delivered"),
])
def test_order_message(status, expected_msg):
    assert get_order_message(status) == expected_msg
```

---

### 4. How do you mock dependencies with `unittest.mock`?

**A:**

```python
from unittest.mock import MagicMock, patch, call

# Patch a function in another module
def test_send_email():
    with patch("myapp.services.email_client.send") as mock_send:
        mock_send.return_value = {"message_id": "abc-123"}

        result = send_welcome_email("alice@example.com")

        mock_send.assert_called_once_with(
            to="alice@example.com",
            subject="Welcome!",
            body=mock_send.call_args.kwargs["body"]
        )
        assert result["message_id"] == "abc-123"

# Patch as decorator
@patch("myapp.services.db.get_user")
@patch("myapp.services.email_client.send")
def test_service(mock_send, mock_get_user):
    mock_get_user.return_value = User(id=1, email="alice@example.com")
    mock_send.return_value = {"sent": True}
    # decorators applied bottom-up — mock_send is inner, mock_get_user is outer

# MagicMock
mock_repo = MagicMock()
mock_repo.find_by_id.return_value = User(id=42)
mock_repo.save.side_effect = DatabaseError("Connection failed")

svc = UserService(repo=mock_repo)
with pytest.raises(DatabaseError):
    svc.update(user_id=42, name="Bob")

mock_repo.find_by_id.assert_called_once_with(42)
```

---

### 5. How do you test for exceptions?

**A:**

```python
import pytest

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_invalid_user():
    with pytest.raises(ValueError) as exc_info:
        User(name="", email="alice@example.com")

    assert "name cannot be empty" in str(exc_info.value)
    assert exc_info.type == ValueError

# Check exception message with match (regex)
with pytest.raises(ValueError, match=r"age must be \d+"):
    User(name="Alice", age=-5)

# Ensure exception is NOT raised
def test_valid_user():
    user = User(name="Alice", email="alice@example.com")  # no exception
    assert user.name == "Alice"
```

---

## 🟡 Mid Level

---

### 6. How do you test FastAPI endpoints?

**A:**

```python
from fastapi.testclient import TestClient
import pytest

@pytest.fixture
def client(app):
    return TestClient(app)

@pytest.fixture
def auth_client(client, user_token):
    client.headers = {"Authorization": f"Bearer {user_token}"}
    return client

def test_create_user(client):
    resp = client.post("/users/", json={"name": "Alice", "email": "alice@test.com"})
    assert resp.status_code == 201
    assert resp.json()["name"] == "Alice"
    assert "id" in resp.json()

def test_create_user_duplicate_email(client):
    client.post("/users/", json={"name": "Alice", "email": "alice@test.com"})
    resp = client.post("/users/", json={"name": "Bob", "email": "alice@test.com"})
    assert resp.status_code == 409

def test_get_user_not_found(client):
    resp = client.get("/users/99999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "User not found"

def test_requires_auth(client):
    resp = client.get("/me")
    assert resp.status_code == 401

def test_authenticated_endpoint(auth_client):
    resp = auth_client.get("/me")
    assert resp.status_code == 200

# Override dependency for testing
from myapp.deps import get_db
from myapp.main import app

def override_get_db():
    yield test_db_session

app.dependency_overrides[get_db] = override_get_db
```

---

### 7. How do you test Django views and APIs?

**A:**

```python
import pytest
from django.test import Client, TestCase
from rest_framework.test import APIClient
from django.urls import reverse

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def auth_api_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

def test_list_orders(auth_api_client, user):
    Order.objects.create(user=user, total=100)
    Order.objects.create(user=user, total=200)

    url = reverse("order-list")
    resp = auth_api_client.get(url)

    assert resp.status_code == 200
    assert resp.data["count"] == 2
    assert len(resp.data["results"]) == 2

def test_create_order(auth_api_client, user):
    url = reverse("order-list")
    resp = auth_api_client.post(url, {
        "customer_id": str(user.id),
        "items": [{"product_id": "p1", "quantity": 2}]
    }, format="json")

    assert resp.status_code == 201
    assert Order.objects.filter(user=user).count() == 1

# Django TestCase (transactional rollback per test)
class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", "alice@test.com", "pass")

    def test_order_total(self):
        order = Order.objects.create(user=self.user)
        OrderItem.objects.create(order=order, price=50, quantity=3)
        order.refresh_from_db()
        self.assertEqual(order.total, 150)
```

---

### 8. How do you use `pytest-asyncio` for async tests?

**A:**

```python
import pytest
import asyncio
import pytest_asyncio

# Mark individual async tests
@pytest.mark.asyncio
async def test_async_fetch():
    result = await fetch_user(user_id=1)
    assert result.name == "Alice"

# Configure asyncio mode globally (pytest.ini or conftest.py)
# asyncio_mode = "auto"  # all async tests run automatically

@pytest_asyncio.fixture
async def async_db():
    db = await create_async_test_db()
    yield db
    await db.close()

@pytest.mark.asyncio
async def test_create_user_async(async_db):
    user = await create_user_async(async_db, name="Alice")
    assert user.id is not None

# Test async FastAPI with httpx
from httpx import AsyncClient, ASGITransport

@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        resp = await ac.get("/users/1")
    assert resp.status_code == 200
```

---

### 9. How do you use testcontainers-python?

**A:**

```python
import pytest
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
from testcontainers.kafka import KafkaContainer

@pytest.fixture(scope="session")
def postgres():
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg

@pytest.fixture(scope="session")
def db_engine(postgres):
    from sqlalchemy import create_engine
    engine = create_engine(postgres.get_connection_url())
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()

@pytest.fixture
def db_session(db_engine):
    with Session(db_engine) as session:
        yield session
        session.rollback()  # rollback after each test

def test_user_repository(db_session):
    repo = UserRepository(db_session)
    user = repo.save(User(name="Alice", email="alice@test.com"))
    assert user.id is not None

    found = repo.get_by_email("alice@test.com")
    assert found.name == "Alice"

# Multiple containers
@pytest.fixture(scope="session")
def kafka():
    with KafkaContainer() as k:
        yield k

@pytest.fixture(scope="session")
def redis():
    with RedisContainer() as r:
        yield r
```

---

### 10. What is `conftest.py` and how do you use it?

**A:**

```python
# conftest.py — shared fixtures available to all tests in the directory

import pytest
from myapp import create_app
from myapp.models import db as _db

@pytest.fixture(scope="session")
def app():
    app = create_app({"TESTING": True, "DATABASE_URL": "sqlite:///:memory:"})
    yield app

@pytest.fixture(scope="session")
def client(app):
    return app.test_client()

@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()

@pytest.fixture
def user(db):
    u = User(name="Alice", email="alice@test.com")
    db.session.add(u)
    db.session.commit()
    return u

# conftest.py can be nested — each directory can have its own
# tests/
# ├── conftest.py           ← shared fixtures
# ├── test_users.py
# ├── integration/
# │   ├── conftest.py       ← integration-specific fixtures
# │   └── test_db.py
```

---

## 🔴 Senior Level

---

### 11. How do you test with mocked time?

**A:**

```python
from freezegun import freeze_time
from datetime import datetime

@freeze_time("2024-01-15 10:00:00")
def test_order_expires_after_24h():
    order = Order.create()
    assert order.expires_at == datetime(2024, 1, 16, 10, 0, 0)

# Dynamic freeze
with freeze_time("2024-01-15") as frozen:
    order = Order.create()
    frozen.move_to("2024-01-16 00:00:01")  # advance time
    assert order.is_expired()

# pytest-freezegun fixture
@pytest.fixture
def mock_time(freezer):
    freezer.move_to("2024-01-15 09:00:00")
    return freezer

def test_session_expiry(mock_time):
    session = create_session()
    mock_time.tick(delta=timedelta(hours=25))
    assert session.is_expired()
```

---

### 12. How do you implement property-based testing with Hypothesis?

**A:**

```python
from hypothesis import given, strategies as st, assume, settings

@given(st.integers(), st.integers())
def test_add_commutative(a: int, b: int):
    assert add(a, b) == add(b, a)

@given(st.text(min_size=1, max_size=100))
def test_slugify_always_lowercase(text: str):
    result = slugify(text)
    assert result == result.lower()

@given(
    st.builds(
        User,
        name=st.text(min_size=1, max_size=100),
        age=st.integers(min_value=0, max_value=150),
        email=st.emails(),
    )
)
def test_user_serialization_roundtrip(user: User):
    data = user.to_dict()
    restored = User.from_dict(data)
    assert restored == user

# Custom strategies
valid_order_items = st.lists(
    st.builds(OrderItem, quantity=st.integers(min_value=1, max_value=100)),
    min_size=1, max_size=20
)

@given(items=valid_order_items)
def test_order_total_always_positive(items):
    order = Order(items=items)
    assert order.total > 0
```

---

## 🏛️ Architect Level

---

### 13. How do you design a test strategy for a Python microservices system?

**A:**

**Test pyramid:**
```
         /\
        /E2E\           ← playwright, httpx against staging
       /------\
      /Contract\        ← pact-python consumer-driven contracts
     /----------\
    / Integration\      ← testcontainers (real Postgres, Redis, Kafka)
   /--------------\
  /   Unit Tests   \    ← pytest + mocks (fast, many)
 /------------------\
```

**CI strategy:**
```yaml
# .github/workflows/test.yml
jobs:
  unit:
    runs-on: ubuntu-latest
    steps:
      - run: pytest tests/unit -v --tb=short -q

  integration:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
    steps:
      - run: pytest tests/integration -v --timeout=60

  contract:
    runs-on: ubuntu-latest
    steps:
      - run: pytest tests/contract  # publish to Pact Broker
```

**Contract testing with pact-python:**
```python
from pact import Consumer, Provider

pact = Consumer("web-frontend").has_pact_with(Provider("order-service"))

def test_get_order_contract():
    (pact
     .given("order 'ord-1' exists")
     .upon_receiving("a request to get an order")
     .with_request(method="GET", path="/api/orders/ord-1")
     .will_respond_with(200, body={
         "id": "ord-1",
         "total": Like(99.99),
         "status": Term(r"(pending|confirmed|shipped)", "pending"),
     }))

    with pact:
        result = order_client.get_order("ord-1")
        assert result["id"] == "ord-1"
```

---

### 14. How do you measure and enforce test coverage?

**A:**

```bash
# Run with coverage
pytest --cov=myapp --cov-report=html --cov-report=term-missing

# Coverage report
# Name                Stmts   Miss  Cover
# myapp/services.py      45      3    93%
# myapp/models.py        30      0   100%
# TOTAL                 250     15    94%

# Enforce minimum coverage (fail if below)
pytest --cov=myapp --cov-fail-under=80

# .coveragerc — exclude generated/config code
[coverage:run]
source = myapp
omit =
    */migrations/*
    */tests/*
    */conftest.py
    myapp/settings*.py

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    if TYPE_CHECKING:
    raise NotImplementedError
    ...

# In pyproject.toml
[tool.pytest.ini_options]
addopts = "--cov=myapp --cov-fail-under=80"
```
