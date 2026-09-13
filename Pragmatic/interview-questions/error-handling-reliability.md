# 🛡️ Error Handling & Reliability — Interview Questions

---

### 1. What is the difference between exceptions and error return values?

**A:**

**Exceptions** (Java, Python, C#): signal exceptional conditions by unwinding the call stack.
- Pros: can't be silently ignored at the call site, separate error path from happy path
- Cons: invisible in method signature, can be misused as control flow, performance overhead

**Error return values** (Go, C, Rust): return error as an explicit value alongside the result.
- Pros: errors are explicit in the type signature, forces callers to handle them
- Cons: easy to ignore (check for `err != nil` fatigue), clutters happy path

```go
// Go — explicit error return
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, fmt.Errorf("divide by zero")
    }
    return a / b, nil
}

result, err := divide(10, 0)
if err != nil {
    // forced to handle — can't ignore without explicit _
    return err
}
```

```python
# Python — exceptions
def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("divide by zero")
    return a / b

# Easy to forget try/except — error silently propagates up
result = divide(10, 0)  # crashes here if not caught
```

**Rust's Result<T, E>:** Combines both — type-safe, explicit, but forces handling via `.unwrap()`, `.expect()`, `?` operator.

---

### 2. What is Fail Fast?

**A:** Detect and report errors as early as possible. Don't continue in an invalid state — fail immediately with a clear error.

```python
# FAIL SLOW — error shows up 200 lines later, confusing
def send_report(config):
    data = fetch_data()
    processed = transform(data)
    formatted = format_report(processed, config["template"])  # KeyError here — but why?

# FAIL FAST — validate at entry point
def send_report(config: dict):
    if "template" not in config:
        raise ValueError("config.template is required")   # clear, immediate, useful message
    if "output_path" not in config:
        raise ValueError("config.output_path is required")

    data = fetch_data()  # only runs if config is valid
```

**System-level fail fast:**
- Health checks at startup (fail to start rather than fail at runtime)
- Circuit breaker opens on failures (stops cascading)
- Strict input validation at API boundaries

---

### 3. What is the Retry pattern?

**A:** Automatically retry failed operations with the expectation that transient failures will resolve.

```python
import time, random
from functools import wraps

def retry(max_attempts=3, backoff_base=1.0, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        raise  # exhausted retries
                    # Exponential backoff with jitter
                    delay = backoff_base * (2 ** attempt) + random.uniform(0, 0.5)
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_attempts=5, backoff_base=0.5, exceptions=(ConnectionError, TimeoutError))
def call_payment_service(order_id: str):
    return http_client.post("/charge", json={"order_id": order_id})
```

**Retry anti-patterns:**
- Retry on non-transient errors (e.g., 400 Bad Request — retrying won't help)
- Retry without backoff — thundering herd problem
- Retry without idempotency — duplicate payments, orders

---

### 4. What is the Circuit Breaker pattern?

**A:** Prevents repeated calls to a failing service. After N failures, "opens" the circuit — subsequent calls fail immediately without hitting the service. After a timeout, allows limited calls to test recovery.

```
States:
  CLOSED → normal operation, track failures
         → N failures in window → OPEN

  OPEN → fast-fail all calls immediately (don't hit service)
       → after timeout → HALF-OPEN

  HALF-OPEN → allow limited "probe" calls through
            → success → CLOSED (recovered)
            → failure → OPEN again
```

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, reset_timeout=60):
        self.failures = 0
        self.threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.state = "CLOSED"
        self.last_failure_time = None

    def call(self, fn, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.reset_timeout:
                self.state = "HALF-OPEN"
            else:
                raise CircuitOpenError("Circuit is open — service unavailable")

        try:
            result = fn(*args, **kwargs)
            if self.state == "HALF-OPEN":
                self.state = "CLOSED"
                self.failures = 0
            return result
        except Exception:
            self.failures += 1
            self.last_failure_time = time.time()
            if self.failures >= self.threshold:
                self.state = "OPEN"
            raise
```

---

### 5. What is the Bulkhead pattern?

**A:** Isolate different parts of the system so a failure in one doesn't cascade to others. Named after ship watertight compartments.

```
Without bulkhead:
  Single thread pool → all services share it
  PaymentService gets slow → fills the thread pool
  → UserService, OrderService also blocked → entire system down

With bulkhead:
  Payment thread pool (10 threads) — isolated
  Order thread pool (20 threads)   — isolated
  User thread pool (15 threads)    — isolated
  PaymentService slowdown → only payment pool exhausted
  → UserService, OrderService unaffected
```

```java
// Resilience4j BulkHead
BulkheadConfig config = BulkheadConfig.custom()
    .maxConcurrentCalls(10)          // max 10 concurrent calls to payment service
    .maxWaitDuration(Duration.ofMillis(100))  // wait max 100ms for slot
    .build();

Bulkhead paymentBulkhead = Bulkhead.of("payment", config);

Supplier<PaymentResult> decoratedCall = Bulkhead
    .decorateSupplier(paymentBulkhead, () -> paymentService.charge(amount));
```

---

### 6. What is Idempotency?

**A:** An operation is idempotent if performing it multiple times has the same effect as performing it once.

```python
# NOT idempotent — calling twice charges twice
def charge_customer(customer_id: str, amount: float):
    payment_gateway.charge(customer_id, amount)
    db.insert("payments", customer_id=customer_id, amount=amount)

# IDEMPOTENT — safe to retry
def charge_customer(customer_id: str, amount: float, idempotency_key: str):
    # Check if already processed
    if db.exists("payments", idempotency_key=idempotency_key):
        return db.get("payments", idempotency_key=idempotency_key)

    result = payment_gateway.charge(customer_id, amount, idempotency_key=idempotency_key)
    db.insert("payments",
        idempotency_key=idempotency_key,
        customer_id=customer_id,
        amount=amount,
        result=result
    )
    return result
```

**HTTP methods and idempotency:**
- `GET, HEAD, OPTIONS, PUT, DELETE` — idempotent (by spec)
- `POST` — NOT idempotent (creates new resource each time)
- `PATCH` — NOT idempotent by default (depends on implementation)

---

### 7. What is Graceful Degradation?

**A:** System continues to operate (in reduced capacity) when some components fail, rather than failing completely.

```python
class ProductService:
    def get_product_page(self, product_id: str) -> dict:
        product = self.product_repo.get(product_id)  # required — fail hard if unavailable

        # Optional features — degrade gracefully
        try:
            recommendations = self.recommendation_service.get(product_id)
        except ServiceUnavailableError:
            recommendations = []  # show page without recommendations

        try:
            reviews = self.review_service.get(product_id)
        except Exception:
            reviews = None  # show "reviews temporarily unavailable"

        try:
            inventory = self.inventory_service.check(product_id)
        except Exception:
            inventory = {"status": "availability_unknown"}  # best-effort

        return {
            "product": product,
            "recommendations": recommendations,  # empty if unavailable
            "reviews": reviews,                  # null if unavailable
            "inventory": inventory,              # degraded info if unavailable
        }
```

---

### 8. What is Defensive Programming?

**A:** Write code that anticipates misuse and handles unexpected inputs gracefully.

```go
func ProcessOrder(order *Order, items []OrderItem) error {
    // Validate inputs — don't trust callers
    if order == nil {
        return fmt.Errorf("order cannot be nil")
    }
    if len(items) == 0 {
        return fmt.Errorf("order must have at least one item")
    }
    for i, item := range items {
        if item.Quantity <= 0 {
            return fmt.Errorf("item[%d].Quantity must be positive, got %d", i, item.Quantity)
        }
        if item.Price < 0 {
            return fmt.Errorf("item[%d].Price cannot be negative, got %.2f", i, item.Price)
        }
    }

    // Enforce invariants throughout
    total := 0.0
    for _, item := range items {
        total += item.Price * float64(item.Quantity)
    }
    if total > MaxOrderTotal {
        return fmt.Errorf("order total %.2f exceeds maximum %.2f", total, MaxOrderTotal)
    }

    return processValidatedOrder(order, items, total)
}
```

---

### 9. What is Timeout and why is it critical?

**A:** Every external call (HTTP, DB, RPC) must have a timeout. Without it, one slow dependency can exhaust all threads/connections and bring down the entire system.

```python
# NO TIMEOUT — dangerous
response = requests.get("http://payment-service/charge", json=payload)
# If payment service hangs for 10 minutes, this thread is stuck for 10 minutes
# Under load, all threads stuck → no more requests can be handled

# WITH TIMEOUT — safe
try:
    response = requests.post(
        "http://payment-service/charge",
        json=payload,
        timeout=(3.05, 10)  # (connect_timeout, read_timeout) in seconds
    )
except requests.Timeout:
    raise PaymentTimeoutError("Payment service timed out after 10s")
except requests.ConnectionError:
    raise PaymentUnavailableError("Cannot reach payment service")
```

**Timeout hierarchy:** Set timeouts at every level — HTTP client, DB connection, DB query, message consumer.

---

### 10. What is error propagation and error wrapping?

**A:** Errors should be propagated up with context added at each layer, preserving the original error for inspection.

```go
// Bad — original error lost
func processOrder(orderID string) error {
    order, err := getOrder(orderID)
    if err != nil {
        return fmt.Errorf("error processing order") // context-free
    }
    // ...
}

// Good — error wrapped with context, original preserved
func processOrder(orderID string) error {
    order, err := getOrder(orderID)
    if err != nil {
        return fmt.Errorf("processOrder: getOrder(%s): %w", orderID, err)
        // "processOrder: getOrder(abc-123): sql: no rows in result set"
    }
    // ...
}

// Caller can inspect original error
if errors.Is(err, sql.ErrNoRows) {
    return ErrOrderNotFound
}
```

```python
# Python exception chaining
try:
    result = db.query("SELECT * FROM orders WHERE id = %s", order_id)
except DatabaseError as e:
    raise OrderRepositoryError(f"Failed to fetch order {order_id}") from e  # chains original
# Stack trace shows both errors
```

---

### 11. What is observability and what are its three pillars?

**A:** Observability is the ability to understand what's happening inside a system from its external outputs.

**Three pillars:**

```
1. Logs — discrete events with context
   { "level": "ERROR", "message": "Payment failed", "order_id": "abc-123",
     "customer_id": "cust-456", "amount": 99.99, "error": "Card declined",
     "trace_id": "xyz-789", "timestamp": "2024-01-15T10:30:00Z" }

2. Metrics — aggregated numerical measurements over time
   payment_requests_total{status="success"} 15234
   payment_requests_total{status="failed"} 42
   payment_duration_seconds{quantile="0.99"} 2.3
   → Alert: error rate > 1%, p99 latency > 3s

3. Traces — end-to-end request path across services
   [User Request] → [API Gateway 2ms] → [Order Service 50ms]
                                              → [DB Query 30ms]
                                              → [Payment Service 15ms]
   → Identifies exactly where time is spent
```

**Good log practices:**
- Structured logging (JSON, not string interpolation)
- Always include trace ID for correlation across services
- Log at boundaries (entry, exit, errors) not inside loops
- Never log PII (passwords, credit cards, SSNs)

---

### 12. What is the difference between availability, reliability, and resilience?

**A:**

| Term | Definition | Metric |
|------|-----------|--------|
| **Availability** | System is operational and accessible | Uptime % (99.9% = 8.7h/year downtime) |
| **Reliability** | System performs its intended function without failure | MTBF (Mean Time Between Failures) |
| **Resilience** | System recovers quickly from failures | MTTR (Mean Time To Recovery) |

```
High availability: 99.99% uptime (4.38 min/year downtime)
  Achieved by: redundancy, load balancing, no single points of failure

High reliability: rarely fails
  Achieved by: quality software, testing, chaos engineering

High resilience: fails fast, recovers fast
  Achieved by: circuit breakers, retries, health checks, automated recovery

Netflix example: unreliable infrastructure (AWS instances fail) + resilient software
→ High availability despite unreliable components
```

**SLO/SLA/SLI:**
- **SLI** (Indicator) — actual measurement: p99 latency = 245ms
- **SLO** (Objective) — internal target: p99 latency < 500ms
- **SLA** (Agreement) — external contractual commitment with penalties
