# 🏛️ Architecture Principles — Interview Questions

---

### 1. What is Layered Architecture?

**A:** Organizes the system into horizontal layers, each with a specific role. Each layer only depends on the layer directly below it.

```
┌─────────────────────────────┐
│       Presentation Layer    │  HTTP handlers, controllers, CLI
├─────────────────────────────┤
│       Application Layer     │  Use cases, orchestration, DTOs
├─────────────────────────────┤
│        Domain Layer         │  Business logic, entities, rules
├─────────────────────────────┤
│     Infrastructure Layer    │  Database, messaging, external APIs
└─────────────────────────────┘
Dependencies flow downward only →
```

**Benefits:** Separation of concerns, easier to swap implementations, testability.
**Drawbacks:** Can lead to anemic domain models, bypassing layers creates "lasagna code."

---

### 2. What is Clean Architecture?

**A:** Robert Martin's architecture where the domain is at the center with no outward dependencies. All dependencies point inward.

```
┌────────────────────────────────────┐
│ Frameworks & Drivers (outermost)   │  Web, DB, UI
│  ┌──────────────────────────────┐  │
│  │ Interface Adapters           │  │  Controllers, Repositories, Presenters
│  │  ┌────────────────────────┐  │  │
│  │  │ Application Rules      │  │  │  Use Cases (Interactors)
│  │  │  ┌──────────────────┐  │  │  │
│  │  │  │  Enterprise Rules │  │  │  │  Entities (Domain)
│  │  │  └──────────────────┘  │  │  │
│  │  └────────────────────────┘  │  │
│  └──────────────────────────────┘  │
└────────────────────────────────────┘

The Dependency Rule: source code dependencies must point inward only.
Domain knows NOTHING about databases, web frameworks, or UI.
```

```python
# Domain entity — no imports from infrastructure
class Order:
    def __init__(self, customer_id: str):
        self.customer_id = customer_id
        self.items = []
        self.status = "pending"

    def confirm(self):
        if not self.items: raise DomainError("Cannot confirm empty order")
        self.status = "confirmed"

# Use case — depends only on interfaces (not implementations)
class ConfirmOrderUseCase:
    def __init__(self, repo: OrderRepository, notifier: Notifier):
        self.repo = repo
        self.notifier = notifier

    def execute(self, order_id: str) -> None:
        order = self.repo.get(order_id)     # interface, not Postgres
        order.confirm()
        self.repo.save(order)
        self.notifier.notify(order)         # interface, not SMTP

# Infrastructure — implements the interfaces; depends on domain
class PostgresOrderRepository(OrderRepository): ...
class SmtpNotifier(Notifier): ...
```

---

### 3. What is Hexagonal Architecture (Ports & Adapters)?

**A:** The application core is at the center, surrounded by ports (interfaces it defines) and adapters (implementations of those ports).

```
               REST API Adapter
                      │
HTTP request ─────────┼──────── Port: IOrderController
                      │
              ┌───────▼────────┐
  Port:       │                │  Port:
  IOrderRepo ─┤  Application   ├─ IEventPublisher
              │     Core       │
  Port:       │                │  Port:
  IEmailSvc  ─┤                ├─ IPaymentGateway
              └───────┬────────┘
                      │
              Postgres Adapter / Kafka Adapter / Stripe Adapter
```

**Benefit:** The core can be tested without any infrastructure. Any adapter can be swapped without changing the core.

---

### 4. What is Domain-Driven Design (DDD)?

**A:** An approach to software development that aligns the model with the business domain. Key concepts:

**Ubiquitous Language:** Domain experts and developers share the same vocabulary. Code uses the business terms.

**Bounded Context:** A boundary within which a model applies consistently. Same word can mean different things in different contexts.

```
"Customer" in different bounded contexts:
  Sales context:     Customer = prospect + purchase history + segment
  Shipping context:  Customer = delivery address + contact info
  Support context:   Customer = ticket history + SLA tier

Each context has its own model, its own database, its own service.
They communicate via events, not shared tables.
```

**Aggregates:** Cluster of domain objects that must be consistent together. One aggregate = one unit of consistency.

```python
class Order:  # Aggregate Root — the entry point for all modifications
    def __init__(self):
        self._items: list[OrderItem] = []
        self._status = OrderStatus.DRAFT

    def add_item(self, product: Product, qty: int) -> None:
        if self._status != OrderStatus.DRAFT:
            raise DomainError("Cannot modify confirmed order")
        # Enforce invariants within the aggregate boundary
        if len(self._items) >= 50:
            raise DomainError("Order cannot have more than 50 items")
        self._items.append(OrderItem(product, qty))

    # External code NEVER accesses OrderItem directly
    # Must go through Order (the aggregate root)
```

---

### 5. What is CQRS?

**A:** Command Query Responsibility Segregation — separate the read model from the write model.

```
Traditional:
  Read: SELECT ... JOIN ... WHERE ...  → same model as write
  Write: INSERT/UPDATE via ORM        → same model as read

CQRS:
  Commands (write): → Domain model → Write DB → Publishes events
  Queries  (read):  → Read model   → Read DB (can be different schema/technology)

Benefits:
  - Read model optimized for queries (denormalized, can use Elasticsearch)
  - Write model enforces domain invariants
  - Read side can be scaled independently

Simple CQRS (same DB):
  Write: via domain model/ORM
  Read:  via raw SQL / projections / DTOs

Full CQRS (event-based):
  Write DB → Kafka events → Read DB (rebuilt from events)
```

---

### 6. What is Event-Driven Architecture?

**A:** Services communicate by producing and consuming events rather than making direct calls.

```
Synchronous (tight coupling):
  OrderService → HTTP → PaymentService → HTTP → InventoryService
  OrderService must wait, knows about PaymentService API

Event-Driven (loose coupling):
  OrderService → "OrderPlaced" event → Kafka topic
    ← PaymentService subscribes, processes independently
    ← InventoryService subscribes, processes independently
    ← NotificationService subscribes, sends confirmation

Benefits:
  - Services don't know about each other (loose coupling)
  - Failure isolation — payment service down doesn't block order creation
  - Scalability — each consumer scales independently
  - Temporal decoupling — can process at different rates

Drawbacks:
  - Eventual consistency (not immediately consistent)
  - Harder to debug (distributed, async)
  - Events must be versioned carefully
  - Idempotency required (events may be delivered more than once)
```

---

### 7. What is the difference between a Monolith and Microservices?

**A:**

| | Monolith | Microservices |
|--|---------|--------------|
| Deployment | Single unit | Independent services |
| Data | Shared database | Database per service |
| Communication | In-process calls | Network (HTTP/gRPC/events) |
| Team structure | One team or shared | Team per service |
| Latency | None (in-process) | Network overhead |
| Simplicity | Simple to develop, test | Complex distributed system |
| Fault isolation | Low | High |
| Scaling | Scale entire app | Scale individual services |

**Monolith first:** Start with a monolith. Extract services when you have clear seam boundaries and actual scaling needs — not before.

**Modular Monolith:** The best of both worlds — strict module boundaries within one process. Extract to services later when needed.

---

### 8. What is the CAP Theorem?

**A:** In a distributed system, you can only guarantee two of three:

```
C — Consistency: every read receives the most recent write or an error
A — Availability: every request receives a response (not necessarily the latest data)
P — Partition Tolerance: system continues despite network partitions

In practice: P is required (networks DO partition)
So the real choice is C vs A during a partition:

CP systems (consistency + partition tolerance):
  Refuse availability during partitions to maintain consistency
  Examples: HBase, Zookeeper, etcd, CockroachDB (with strong consistency)
  Use: financial transactions, leader election

AP systems (availability + partition tolerance):
  Return possibly stale data during partitions, eventually consistent
  Examples: DynamoDB, Cassandra, CouchDB
  Use: social feeds, product catalogs, shopping carts
```

**Modern nuance (PACELC):** Even without partitions, there's a trade-off between latency and consistency.

---

### 9. What is Coupling and Cohesion at the architectural level?

**A:**

**Coupling** — how much one module depends on another. High coupling = changes ripple everywhere.

```
Types of coupling (worst to best):
  Content coupling: one module modifies internal data of another
  Common coupling: multiple modules share global state
  Control coupling: one module controls flow of another (passing flags)
  Stamp coupling: sharing complex data structures
  Data coupling: passing only necessary data (best)
```

**Cohesion** — how related the responsibilities within a module are. High cohesion = module does one clear thing.

**Architectural cohesion example:**
```
Low cohesion service: "UserOrderPaymentService"
  - manages user accounts
  - processes orders
  - handles payments
  → Should be three services

High cohesion service: "OrderService"
  - creates orders
  - updates order status
  - queries orders
  → All about orders
```

---

### 10. What is a Bounded Context and how do you identify one?

**A:** A bounded context is a boundary within which a model (language, entities, rules) is internally consistent.

**How to identify:**
1. **Conway's Law** — your architecture will mirror your team structure. Draw org chart → draw service boundaries
2. **Different meanings** — when the same word means different things, you have different contexts
3. **Different change rates** — things that change together belong together
4. **Different consistency requirements** — shopping cart (eventual OK) vs payment (strong required) → different contexts

```
Identifying bounded contexts for an e-commerce system:
  Catalog:     products, descriptions, categories, search
  Inventory:   stock levels, reservations, warehouse locations
  Orders:      order lifecycle, line items, order history
  Payments:    payment methods, transactions, refunds
  Shipping:    addresses, carriers, tracking, delivery
  Users:       authentication, profiles, preferences
  Reviews:     ratings, comments, moderation

Each context owns its data, deploys independently.
They communicate via events or APIs — never via shared DB tables.
```

---

### 11. What is the Dependency Rule?

**A:** From Clean Architecture — source code dependencies can only point from outer circles to inner circles.

```
Policy (inner) must never know about mechanism (outer).
Domain must never know about database, web framework, or UI.

VIOLATION:
  class Order:  # domain entity
      def save(self):
          psycopg2.connect(...).execute("INSERT INTO orders...")
          # Domain knows about PostgreSQL!

CORRECT:
  class Order:  # domain entity — knows NOTHING about persistence
      def confirm(self): self.status = "confirmed"

  class OrderRepository:  # interface defined in domain
      def save(self, order: Order): ...

  class PostgresOrderRepository(OrderRepository):  # in infrastructure layer
      def save(self, order): psycopg2.connect(...).execute(...)
```
