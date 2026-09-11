# 🏛️ Python — Architect-Level Interview Questions

---

## 1. How would you architect a high-traffic Python/Django web application?

**A:**

**Serving tier:**
- **Gunicorn** (sync workers) or **Uvicorn** (async ASGI) behind **Nginx**
- Gunicorn: `--workers $(2 * CPU + 1)`, `--worker-class gevent` for I/O-heavy
- ASGI stack: Django 4.1+ + Uvicorn + `httptools` for async views

**Caching strategy:**
- Redis: page fragments, expensive querysets, session store
- CDN (Cloudflare): static assets, public cacheable responses
- Database query cache: `select_related`/`prefetch_related`, indexed columns

**Task queue:** Celery + Redis/RabbitMQ for async work

**Database:**
- Primary + read replicas (Django `DATABASE_ROUTERS`)
- PgBouncer connection pooler
- Partitioned tables for time-series or large fact tables

**Horizontal scaling:**
```
Users → CloudFlare CDN → Nginx LB → Gunicorn pods (K8s)
                                 → Celery workers
                                 → Redis (cache + broker)
                                 → Postgres (primary + replicas)
```

---

## 2. How do you approach service decomposition and inter-service communication in a Python microservices architecture?

**A:**

**Decomposition principles:**
- Align services to bounded contexts (DDD)
- Each service: owns its data, deployable independently, small enough to be rewritten in 2 weeks

**Synchronous communication:**
```python
# gRPC with Python (grpcio + protobuf)
# Strong typing, bidirectional streaming, efficient binary format
import grpc
from protos import order_pb2_grpc, order_pb2

channel = grpc.aio.insecure_channel("order-service:50051")
stub = order_pb2_grpc.OrderServiceStub(channel)
order = await stub.GetOrder(order_pb2.GetOrderRequest(id=order_id))
```

**Asynchronous communication:**
```python
# Kafka via confluent-kafka or aiokafka
from aiokafka import AIOKafkaProducer
producer = AIOKafkaProducer(bootstrap_servers="kafka:9092")
await producer.send("order-events", value=event_bytes)
```

**API Gateway:** Kong, AWS API Gateway, or custom FastAPI gateway for external traffic — handles auth, rate limiting, routing.

---

## 3. How do you handle database migrations in a CI/CD pipeline for Python/Django?

**A:**

**Migration strategy:**
1. Migrations run as a separate step **before** deploying new code
2. Migrations must be **backward-compatible** (expand-contract):
   - Never drop/rename a column and use it in the same deploy
   - Add new column (nullable or with default) → deploy code → backfill → remove old column in a later deploy

**Zero-downtime migration example:**
```python
# Step 1: Add nullable column (deploy migration first)
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(
            model_name="user",
            name="email_verified",
            field=models.BooleanField(null=True),  # nullable — safe
        ),
    ]

# Step 2: Deploy new code that writes to both old + new field
# Step 3: Backfill: UPDATE users SET email_verified = false WHERE email_verified IS NULL
# Step 4: Make non-nullable in a later migration
```

**In CI:**
```bash
python manage.py migrate --check   # fail if unapplied migrations
python manage.py migrate           # run as K8s Job before rollout
```

---

## 4. How do you design a resilient task queue system with Celery?

**A:**

**Reliability configuration:**
```python
# celery.py
app = Celery("myapp")
app.conf.update(
    task_acks_late=True,           # ack after completion, not on receipt
    task_reject_on_worker_lost=True,  # requeue if worker dies mid-task
    worker_prefetch_multiplier=1,  # one task per worker (fairness)
    task_serializer="json",
    result_backend="redis://redis:6379/0",
    task_track_started=True,
)

@app.task(
    bind=True,
    max_retries=5,
    default_retry_delay=60,
    autoretry_for=(TransientError,),
    retry_backoff=True,
    retry_jitter=True,
)
def process_payment(self, order_id: str):
    try:
        payment_gateway.charge(order_id)
    except PaymentGatewayError as exc:
        raise self.retry(exc=exc)
```

**Idempotency:** Every task must be safe to run multiple times — use DB upserts, check-and-set, or idempotency keys.

**Priority queues:**
```python
app.conf.task_routes = {
    "tasks.send_email": {"queue": "low"},
    "tasks.process_payment": {"queue": "critical"},
}
```

---

## 5. How do you implement event sourcing in Python?

**A:**

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol
import uuid

@dataclass
class DomainEvent:
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class OrderCreated(DomainEvent):
    order_id: str = ""
    customer_id: str = ""

class Order:
    def __init__(self):
        self._events: list[DomainEvent] = []
        self.status = None

    def create(self, customer_id: str) -> "Order":
        event = OrderCreated(order_id=str(uuid.uuid4()), customer_id=customer_id)
        self._apply(event)
        return self

    def _apply(self, event: DomainEvent):
        self._events.append(event)
        if isinstance(event, OrderCreated):
            self.status = "created"

    @classmethod
    def from_events(cls, events: list[DomainEvent]) -> "Order":
        order = cls()
        for event in events:
            order._apply(event)
        order._events.clear()  # only uncommitted events
        return order
```

**Store:** Append-only event table (Postgres), or EventStoreDB, or custom Redis Streams implementation.

---

## 6. How do you handle observability in a Python microservices fleet?

**A:**

**OpenTelemetry (standard):**
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

DjangoInstrumentor().instrument()
RequestsInstrumentor().instrument()

tracer = trace.get_tracer(__name__)

def process_order(order_id: str):
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)
        # ... work
```

**Metrics (Prometheus):**
```python
from prometheus_client import Counter, Histogram, start_http_server

REQUEST_LATENCY = Histogram("http_request_duration_seconds", "...", ["method", "endpoint"])
ERROR_COUNT = Counter("http_errors_total", "...", ["status_code"])

@REQUEST_LATENCY.labels(method="GET", endpoint="/orders").time()
def my_view(request): ...
```

**Structured logging:**
```python
import structlog

log = structlog.get_logger()
log.info("order_created", order_id=order_id, customer_id=cid, amount=amount)
# Output: {"event": "order_created", "order_id": "...", "timestamp": "..."}
```

---

## 7. How do you design a data pipeline in Python for high-volume data processing?

**A:**

**Small-medium volume (< 1M records/hour):** Celery + Postgres

**Medium-large volume:** Apache Airflow (orchestration) + Pandas/Polars (transformation)

```python
# Airflow DAG
from airflow.decorators import dag, task
from datetime import datetime
import polars as pl

@dag(schedule="@hourly", start_date=datetime(2024, 1, 1))
def order_pipeline():

    @task
    def extract() -> str:
        df = pl.read_database("SELECT * FROM orders WHERE created_at > NOW() - INTERVAL '1 hour'", conn)
        df.write_parquet("/tmp/orders.parquet")
        return "/tmp/orders.parquet"

    @task
    def transform(path: str) -> str:
        df = pl.read_parquet(path)
        result = df.groupby("customer_id").agg(pl.col("total").sum().alias("revenue"))
        result.write_parquet("/tmp/revenue.parquet")
        return "/tmp/revenue.parquet"

    @task
    def load(path: str):
        df = pl.read_parquet(path)
        df.write_database("revenue_summary", conn, if_exists="append")

    load(transform(extract()))
```

**High volume:** Apache Kafka + Faust (Python stream processing) or PySpark.

---

## 8. How do you govern API design across multiple Python services?

**A:**

**API-first design:**
- Define OpenAPI spec before implementation
- Use `Spectral` to lint specs for consistency rules
- Generate client SDKs from spec (openapi-generator)

**FastAPI (OpenAPI native):**
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Order Service", version="2.0.0")

class OrderRequest(BaseModel):
    customer_id: str
    items: list[OrderItem]

@app.post("/v2/orders", response_model=OrderResponse, status_code=201)
async def create_order(order: OrderRequest) -> OrderResponse:
    ...
# Auto-generates /docs (Swagger UI) and /openapi.json
```

**Versioning strategy:**
- URL: `/v1/`, `/v2/` — simple, explicit
- Deprecation: `Sunset` header + monitoring of v1 usage metrics
- Breaking changes: new major version; additive changes in same version

**Contract testing (Schemathesis):**
```bash
schemathesis run http://api:8000/openapi.json --checks all
```

---

## 9. How do you approach testing strategy at scale in Python?

**A:**

**Test pyramid:**
- **Unit (70%):** Pure functions, domain logic — fast, isolated, `pytest`
- **Integration (20%):** DB, cache, external calls — `pytest` + `testcontainers`
- **E2E (10%):** Critical user flows — `playwright` or `httpx` against real stack

**Test isolation:**
```python
# testcontainers — real DB in Docker for integration tests
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="session")
def pg():
    with PostgresContainer("postgres:16") as pg:
        yield pg.get_connection_url()
```

**Property-based testing:**
```python
from hypothesis import given, strategies as st

@given(st.integers(min_value=1), st.integers(min_value=1))
def test_add_commutative(a, b):
    assert add(a, b) == add(b, a)
```

**Mutation testing:**
```bash
mutmut run  # checks if tests catch code mutations
mutmut results
```

**CI strategy:** Unit on every push (< 2 min), integration on PR, E2E on main branch merge.

---

## 10. How do you handle security at the architecture level in a Python ecosystem?

**A:**

**Dependency security:**
```bash
pip audit              # check for known vulnerabilities
safety check           # alternative scanner
pip-audit --fix        # auto-upgrade where safe
```

**Code security:**
```bash
bandit -r myapp/ -ll   # static analysis for common security issues
semgrep --config=auto  # pattern-based security rules
```

**Secrets management:**
- Never in env files in source control
- Use AWS Secrets Manager / HashiCorp Vault / Azure Key Vault
- `python-dotenv` for local dev only; rotate regularly

**Runtime hardening:**
- Django: `DEBUG=False`, `SECURE_*` settings, `ALLOWED_HOSTS`
- Rate limiting: `django-ratelimit` or API gateway
- Input validation: Pydantic models for every external input boundary
- Parameterized queries — Django ORM by default; audit any raw SQL
- `Content-Security-Policy` header via `django-csp`

**Supply chain:**
- Pin exact versions in `requirements.txt` + `pip-compile`
- Audit Docker base images with `trivy`
- SBOM generation in CI: `syft`
