# Key Takeaways — Microservices Patterns

> *By Chris Richardson — the definitive guide to building production-grade microservice systems*

---

## 🏛️ Architecture Fundamentals

### 1. Monoliths Aren't Evil — But They Have Limits
A monolith is the right choice when starting out. It becomes problematic when:
- The codebase is so large no one understands it all
- Deployment takes hours and requires the whole team
- Scaling one component means scaling everything
- The tech stack can't evolve because everything is coupled

**The rule**: Start monolithic, migrate to microservices when complexity demands it.

---

### 2. Microservices = Functional Decomposition Along Business Lines
Services map to business capabilities or DDD subdomains — *not* technical layers.

```
❌ Wrong: UserController Service, DatabaseAccess Service, BusinessLogic Service
✅ Right: Order Service, Restaurant Service, Delivery Service, Accounting Service
```

Each service:
- Has its own database (no sharing)
- Has a well-defined API (no bypassing)
- Is owned by one small team
- Can be independently deployed and scaled

---

### 3. Scale Cube: Three Dimensions of Scale
```
Y-axis: Functional decomposition → Microservices (the focus of this book)
X-axis: Horizontal duplication → Run multiple instances behind load balancer
Z-axis: Data partitioning → Route requests by user/tenant/shard
```

---

## 🔌 Inter-Service Communication

### 4. Prefer Async Messaging Over Sync REST for Inter-Service Calls
```
Synchronous (REST/gRPC):
  - Simple, familiar
  - Reduces availability: A→B→C means if C is down, A fails
  - Tight coupling: A must know B's location

Asynchronous (Messaging):
  - Loose coupling: producers don't know consumers
  - Higher availability: broker buffers messages
  - Complex: need message broker, handle duplicates
  
Rule: Use REST for external APIs, use messaging for inter-service communication
```

### 5. Circuit Breaker Prevents Cascade Failures
```
Without circuit breaker:
  Order Service waits for unresponsive Inventory Service
  → Thread pool exhausts
  → Order Service becomes unresponsive
  → API Gateway becomes unresponsive
  → System-wide outage

With circuit breaker (Hystrix):
  After 5 failures → open circuit
  → Fail fast with fallback
  → Try again after 30 seconds
  → Protects the rest of the system
```

### 6. Transactional Outbox Solves the "Dual Write" Problem
```
Problem: How to update DB AND publish event atomically?
         (without distributed transactions)

Solution: Write event to OUTBOX table in same DB transaction
          Separate MessageRelay reads OUTBOX and publishes to broker
          
Result: Guaranteed at-least-once delivery, no distributed transactions needed
```

---

## 💾 Data Management

### 7. Database Per Service is Non-Negotiable
Each service owns its data. No other service may access its DB directly.

```
Benefits:
  - Loose coupling: schema changes don't affect other services
  - No lock contention between services
  - Right database for the job (SQL, NoSQL, Redis)

Cost:
  - Can't do cross-service joins
  - No ACID across services → must use Sagas
```

### 8. Sagas Maintain Consistency Across Services
```
Saga = sequence of local transactions + compensating transactions

Create Order Saga:
  1. Create Order (PENDING)         → compensate: Reject Order
  2. Verify Consumer                → compensate: -
  3. Create Kitchen Ticket          → compensate: Reject Ticket
  4. Authorize Credit Card (PIVOT)  → if fails, run compensations
  5. Approve Ticket                 → (retriable - always succeeds)
  6. Approve Order                  → (retriable - always succeeds)

Rule: One saga per operation that spans multiple services
```

### 9. Two Saga Coordination Styles: Choose Wisely

| Style | When to Use | Watch Out For |
|-------|-------------|---------------|
| **Choreography** | Simple sagas, few participants | Cyclic dependencies, hard to trace |
| **Orchestration** | Complex sagas, many participants | Don't put business logic in orchestrator |

---

## 🧩 Business Logic Design

### 10. DDD Aggregates Are the Building Block of Microservices
```
Aggregate rules:
  1. Only access via aggregate root (no direct access to internals)
  2. Reference other aggregates by ID (no object references)
  3. One transaction = one aggregate

Benefits in microservices:
  - Aggregates define service transaction boundaries
  - No cross-service object references
  - Natural unit for event sourcing
```

### 11. Event Sourcing: Store Events, Not State
```
Traditional: Store current state → lose history
Event Sourcing: Store events → replay to get current state

Events (immutable append-only):
  OrderCreated { orderId, consumerId, restaurantId, items }
  OrderApproved { orderId, approvedAt }
  OrderCancelled { orderId, reason, cancelledAt }

Benefits: Full audit trail, event replay, temporal queries
Cost: Eventual consistency, query complexity (need CQRS)
```

### 12. CQRS Separates Read and Write Models
```
Write side: Commands → Aggregate → Events → Event Store
Read side:  Events → Projections → Query-optimized views

Use API Composition for simple queries across services
Use CQRS when a service needs data owned by multiple services
```

---

## 🚪 External APIs

### 13. API Gateway is the Entry Point — Always
```
Never expose internal services directly to external clients.

API Gateway responsibilities:
  - Route requests to correct service
  - Aggregate data from multiple services (API composition)
  - Authenticate (validate JWT)
  - Rate limiting and caching
  - Protocol translation (external REST → internal gRPC)
```

### 14. BFF Pattern: One Gateway Per Client Type
```
Mobile app → Mobile BFF (compact, battery-efficient responses)
Browser   → Web BFF (richer data, more features)
3rd party → Public API (versioned, stable, documented)
```

---

## 🧪 Testing

### 15. The Test Pyramid for Microservices
```
      /E2E\           ← Few: test critical happy paths only
     /──────\
    / Component\      ← Some: test service in isolation with stubs
   /────────────\
  / Integration  \    ← More: test service + real DB/broker
 /────────────────\
/ Unit Tests        \ ← Many: test individual classes fast
```

### 16. Consumer-Driven Contract Tests Bridge the Gap
```
Instead of: "Let's spin up all 10 services to test integration"
Use:        "Let's verify contracts between service pairs"

Consumer defines what it expects → Contract
Provider verifies it satisfies the contract
Both can deploy independently if contracts pass
```

---

## 🏭 Production Readiness

### 17. Observability is Not Optional in Distributed Systems
You need all six:
1. **Health Check API** — load balancer routing
2. **Log Aggregation** — centralized search (ELK stack)
3. **Distributed Tracing** — follow a request through N services (Zipkin)
4. **Application Metrics** — dashboards and alerts (Prometheus/Grafana)
5. **Exception Tracking** — deduplicated alerts (Sentry)
6. **Audit Logging** — who did what, when

### 18. JWT Access Tokens for Security
```
Client → API Gateway (authenticates, gets JWT)
JWT propagated to all services in headers
Each service validates JWT signature locally
No auth service call per request → no extra latency
```

---

## 🚀 Deployment

### 19. Containers + Kubernetes is the Standard
```
Docker: Package service as immutable image
Kubernetes: Orchestrate containers at scale
  - Rolling deployments (zero downtime)
  - Auto-scaling
  - Service discovery (DNS-based)
  - ConfigMaps and Secrets for configuration
  
Service Mesh (Istio): Advanced traffic management, canary releases
```

---

## 🔄 Migration

### 20. Strangle the Monolith — Don't Rewrite It
```
Do:
  ✅ Stop adding features to the monolith
  ✅ Implement all new features as microservices
  ✅ Extract one capability at a time, incrementally
  ✅ Use Anti-Corruption Layer to protect new service models

Don't:
  ❌ Attempt a "big bang" rewrite
  ❌ Try to extract everything at once
  ❌ Share databases between monolith and services (temporarily ok, long-term bad)
```

---

## 🧭 The Bottom Line

The microservice architecture is **not free**. You trade:
- Simple ACID transactions → for Sagas
- Simple queries → for CQRS and API composition
- Simple deployment → for containers and orchestration
- Easy debugging → for distributed tracing and log aggregation

You get in return:
- **Velocity**: Small teams ship independently and fast
- **Scalability**: Scale only what needs scaling
- **Resilience**: Failures are isolated, not systemic
- **Technology freedom**: Right tool for each service

> **Use microservices when the complexity of distributed systems is less than the complexity of a monolith that has outgrown itself.**

---

*← [Back to Microservices Patterns](README.md)*
