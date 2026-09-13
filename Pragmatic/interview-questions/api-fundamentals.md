# 🔌 API & Integration Fundamentals — Interview Questions

---

### 1. What is REST and what are its constraints?

**A:** REST (Representational State Transfer) is an architectural style for distributed systems, defined by Roy Fielding. Six constraints:

1. **Client-Server** — separation of concerns; UI and data storage independent
2. **Stateless** — each request contains all information needed; no session on server
3. **Cacheable** — responses must declare cacheability
4. **Uniform Interface** — standardized way to interact (resource identification, manipulation through representations, self-descriptive messages, HATEOAS)
5. **Layered System** — client doesn't know if it's talking to the server or a proxy
6. **Code on Demand** (optional) — server can send executable code

```
RESTful URL design:
  Resources are nouns, not verbs:
  ✅ GET /orders           — list orders
  ✅ GET /orders/42        — get specific order
  ✅ POST /orders          — create order
  ✅ PUT /orders/42        — replace order 42
  ✅ PATCH /orders/42      — partial update
  ✅ DELETE /orders/42     — delete order
  ✅ GET /orders/42/items  — nested resource

  ❌ GET /getOrders
  ❌ POST /createOrder
  ❌ GET /orders/delete?id=42
```

---

### 2. What are the HTTP methods and their semantics?

**A:**

| Method | Idempotent | Safe | Use |
|--------|-----------|------|-----|
| GET | ✅ | ✅ | Retrieve resource |
| HEAD | ✅ | ✅ | GET without body (check existence) |
| PUT | ✅ | ❌ | Replace entire resource |
| DELETE | ✅ | ❌ | Delete resource |
| POST | ❌ | ❌ | Create resource / non-idempotent action |
| PATCH | ❌ | ❌ | Partial update |
| OPTIONS | ✅ | ✅ | CORS preflight, capability discovery |

**Safe** = doesn't modify server state
**Idempotent** = multiple identical requests = same result as one request

---

### 3. What are HTTP status codes and what do the ranges mean?

**A:**

```
1xx — Informational
  100 Continue

2xx — Success
  200 OK
  201 Created          — after POST/PUT that creates a resource (include Location header)
  204 No Content       — success with no body (DELETE, PATCH with no return)
  206 Partial Content  — range requests

3xx — Redirection
  301 Moved Permanently  — SEO-safe permanent redirect
  302 Found              — temporary redirect
  304 Not Modified       — cache still valid (ETags)

4xx — Client Error (caller's fault)
  400 Bad Request        — malformed request, validation failure
  401 Unauthorized       — not authenticated (login required)
  403 Forbidden          — authenticated but not authorized
  404 Not Found          — resource doesn't exist
  405 Method Not Allowed — GET on a POST-only endpoint
  409 Conflict           — duplicate, concurrent modification
  410 Gone               — permanently removed
  422 Unprocessable Entity — valid format but semantic errors (validation)
  429 Too Many Requests  — rate limited

5xx — Server Error (our fault)
  500 Internal Server Error — generic server error
  502 Bad Gateway        — upstream service returned invalid response
  503 Service Unavailable — overloaded or maintenance
  504 Gateway Timeout    — upstream service didn't respond in time
```

---

### 4. What is the difference between REST, RPC, and GraphQL?

**A:**

| | REST | RPC (gRPC) | GraphQL |
|--|------|-----------|---------|
| Model | Resources | Procedures/methods | Graph of types |
| Protocol | HTTP | HTTP/2 + protobuf | HTTP |
| Schema | Optional (OpenAPI) | Required (.proto) | Required |
| Fetching | Fixed shapes | Fixed shapes | Client-specified |
| Over-fetching | Common | Common | Solved |
| Under-fetching | Common (N+1 HTTP) | Common | Solved |
| Versioning | URL or header | Package versioning | Schema evolution |
| Use for | Public APIs, web | Internal services, streaming | Complex frontends |

```graphql
# GraphQL — client asks for exactly what it needs
query GetUser($id: ID!) {
  user(id: $id) {
    name
    email
    orders(last: 5) {
      id
      total
      status
    }
    # No over-fetching: don't request address, phone, etc.
  }
}
```

---

### 5. What are Webhooks and how do they differ from polling?

**A:**

**Polling:** Client repeatedly asks "anything new?"
```
Client → GET /api/events?since=lastId → Server
Client → GET /api/events?since=lastId → Server (1 second later)
Client → GET /api/events?since=lastId → Server (1 second later)
# Mostly returns empty responses — wasteful
```

**Webhooks:** Server pushes to client when something happens
```
Client registers: POST /webhooks { url: "https://myapp.com/hooks", events: ["payment.success"] }
Later:
Payment happens → Server → POST https://myapp.com/hooks { event: "payment.success", ... }
# Only when there's data — efficient
```

**Webhook implementation concerns:**
```python
# 1. Verify signatures (ensure webhook came from the expected source)
def verify_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)

# 2. Respond fast (return 200 immediately, process async)
@app.post("/webhooks/payment")
async def handle_payment_webhook(request: Request):
    body = await request.body()
    verify_webhook(body, request.headers["X-Signature"], WEBHOOK_SECRET)
    background_tasks.add_task(process_payment_event, json.loads(body))
    return {"status": "ok"}  # respond immediately

# 3. Be idempotent (webhooks can be delivered more than once)
# 4. Handle retries (retry on non-2xx response)
```

---

### 6. What is API versioning and what are the strategies?

**A:**

```
Strategy 1: URL versioning (most visible, easiest to test)
  /v1/orders
  /v2/orders
  Pros: explicit, cacheable, easy to route
  Cons: URL "should represent resource not version"

Strategy 2: Header versioning
  Accept: application/vnd.myapi.v2+json
  API-Version: 2
  Pros: clean URLs
  Cons: harder to test in browser, less discoverable

Strategy 3: Query parameter
  /orders?version=2
  Pros: easy to test
  Cons: not RESTful, clutters URLs

Strategy 4: No versioning (additive only)
  Never break, only add
  Pros: simple
  Cons: can't remove anything, schema bloat

Best practice:
  - Use URL versioning for public APIs (simple, cacheable)
  - Deprecate old versions with Sunset + Deprecation headers
  - Keep v1 alive until usage metrics hit zero
  - Give 6-12 months migration window
```

---

### 7. What is pagination and what are the strategies?

**A:**

```python
# Strategy 1: Offset pagination (simple, SQL-natural)
GET /orders?page=3&size=20
# SQL: SELECT * FROM orders LIMIT 20 OFFSET 40

# Problems with offset:
# - COUNT(*) for total pages is expensive on large tables
# - If items added during pagination, you get skips or duplicates
# - Deep offsets (page 10000) require scanning 200,000 rows

# Strategy 2: Cursor/keyset pagination (efficient, consistent)
GET /orders?after=order-id-xyz&size=20
# SQL: SELECT * FROM orders WHERE id > 'order-id-xyz' ORDER BY id LIMIT 20

# Response includes next cursor:
{
  "items": [...],
  "next_cursor": "order-id-abc",  # null if last page
  "has_more": true
}

# Benefits:
# - O(1) regardless of page depth
# - Consistent (no skips/duplicates with concurrent writes)
# - Can use on any ordered field

# Strategy 3: Time-based (for event streams)
GET /events?before=2024-01-15T10:00:00Z&size=100
```

---

### 8. What is rate limiting and how is it implemented?

**A:**

```
Why rate limiting:
  - Prevent abuse / DoS
  - Ensure fair usage across clients
  - Protect backend services

Strategies:
  Fixed Window:  count requests in [0:00-0:59], reset at 1:00
    Simple but allows burst at window boundary

  Sliding Window: count requests in last 60 seconds at any point
    More accurate, no boundary burst

  Token Bucket:  tokens added at rate R, max capacity C
    Allows bursts up to C, average rate = R

  Leaky Bucket:  requests queued, processed at fixed rate
    Smooths traffic, no bursts
```

```python
# Response headers (standard)
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100        # requests per window
X-RateLimit-Remaining: 0      # remaining in current window
X-RateLimit-Reset: 1704067260 # Unix timestamp when window resets
Retry-After: 45               # seconds until retry is safe
```

---

### 9. What is the difference between Authentication and Authorization?

**A:**

```
Authentication (AuthN): Who are you?
  - Verifying identity
  - "Prove you are Alice"
  - Username/password, OAuth token, certificate, MFA

Authorization (AuthZ): What are you allowed to do?
  - Verifying permissions
  - "Alice can read orders but not delete users"
  - RBAC, ABAC, ACL, scopes

Order matters: Authenticate first, then authorize
```

```
Common authentication mechanisms:
  Session: server stores state in session, client has session cookie
  JWT: stateless — server issues signed token, client sends it on each request
  API Key: static key for machine-to-machine
  OAuth 2.0: delegated authorization (login with Google)
  mTLS: mutual TLS certificate authentication

Authorization models:
  RBAC (Role-Based): User → Roles → Permissions
  ABAC (Attribute-Based): Policy evaluates attributes of user, resource, environment
  ACL (Access Control List): per-resource list of permitted users/roles
  Scopes (OAuth): token carries specific permissions (read:orders, write:inventory)
```

---

### 10. What is synchronous vs asynchronous communication?

**A:**

**Synchronous:** Caller blocks until response received.
```
Client ──HTTP request──→ Server
       ←──HTTP response── Server
Client continues...

When to use: response needed to proceed, simple workflows, user-facing operations
Cons: tight coupling, cascading failures, latency chains
```

**Asynchronous:** Caller sends request and continues; response comes later (if at all).
```
Publisher ──event/command──→ Broker → Consumer (processes independently)
Publisher continues immediately

When to use: long-running operations, fan-out, decoupled services
Cons: harder to debug, eventual consistency, idempotency required
```

```
Patterns:
  Request/Reply async:
    Sender → message with replyTo queue
    Receiver → processes → sends response to replyTo
    Sender polls / subscribes to replyTo

  Fire and Forget:
    Sender → message → done (no response expected)

  Publish/Subscribe:
    Publisher → topic → multiple subscribers (fan-out)

  Event Sourcing:
    Events are the source of truth; state is derived from events
```

---

### 11. What is idempotency in APIs?

**A:** An API call is idempotent if calling it multiple times with the same input produces the same result and side effects as calling it once.

```
HTTP method idempotency:
  GET, PUT, DELETE: idempotent by spec
  POST, PATCH: NOT idempotent by spec

Idempotency keys for POST (safe retry):
  Client generates unique idempotency key per request:
  POST /payments
  Idempotency-Key: f47ac10b-58cc-4372-a567-0e02b2c3d479

  Server:
    1. Check if key has been seen
    2. If yes: return cached response
    3. If no: process, store key+response, return response

  Client can safely retry on timeout/error — server deduplicates
```

```python
# Stripe-style idempotency implementation
@app.post("/payments")
async def create_payment(request: Request, body: PaymentRequest):
    idempotency_key = request.headers.get("Idempotency-Key")

    if idempotency_key:
        # Check cache
        cached = await redis.get(f"idem:{idempotency_key}")
        if cached:
            return json.loads(cached)  # return cached response

    result = await payment_service.charge(body)

    if idempotency_key:
        # Cache for 24 hours
        await redis.setex(f"idem:{idempotency_key}", 86400, json.dumps(result))

    return result
```
