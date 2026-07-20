# Chapter 6 — Developing Business Logic with Event Sourcing

> *"Event sourcing is an event-centric way to structure the business logic and persist domain objects."*

---

## 🎯 Core Concept

**Event Sourcing** flips the traditional persistence model. Instead of storing the *current state* of an entity, you store the *sequence of events* that led to that state. The current state is derived by replaying those events. This makes event history a first-class citizen and provides a natural audit log.

---

## ❌ Problems with Traditional Persistence

| Problem | Description |
|---------|-------------|
| **No history** | Current state overwrites past — no audit trail |
| **Object-relational impedance mismatch** | Object graphs don't map cleanly to tables |
| **Missing events** | Temporal queries ("what was the state at T?") are hard |
| **Dual-write** | Updating DB and publishing events requires two-phase commit or outbox |

---

## 🔄 How Event Sourcing Works

```
Traditional: Store current state
  ORDERS table: { orderId, status=APPROVED, total=25.00, ... }

Event Sourcing: Store history of events
  EVENTS table:
    1. OrderCreated     { orderId, items, consumer }
    2. CreditCardAuthorized { orderId, amount }
    3. OrderApproved    { orderId }

Derive current state by replaying:
  new Order().apply(OrderCreated)
             .apply(CreditCardAuthorized)
             .apply(OrderApproved)
             → Order { status=APPROVED, total=25.00, ... }
```

### The Aggregate + Event Sourcing Pattern

```java
public class Order {
  // State derived from events
  private OrderState state;
  private List<OrderLineItem> lineItems;
  private Long consumerId;

  // Command method — validates and returns events
  public List<DomainEvent> approve() {
    switch (state) {
      case APPROVAL_PENDING:
        return singletonList(new OrderApproved());
      default:
        throw new UnsupportedOperationException();
    }
  }

  // Event handler — applies event to state (no side effects)
  public void apply(OrderApproved event) {
    this.state = APPROVED;
  }
}
```

Command methods validate → return events  
Apply methods update state → pure functions (no validation)

---

## 🗄️ Event Store

The event store is the database for event-sourced aggregates:

```
Event Store operations:
  1. Load aggregate: fetch all events for aggregateId → replay → current state
  2. Save aggregate: append new events to the stream

EVENTS table:
┌───────────────────────────────────────────────────────────┐
│ event_id │ aggregate_type │ aggregate_id │ event_type │ data │
├───────────────────────────────────────────────────────────┤
│    1     │ Order          │ 123          │ OrderCreated  │ {...}│
│    2     │ Order          │ 123          │ OrderApproved │ {...}│
│    3     │ Order          │ 124          │ OrderCreated  │ {...}│
└───────────────────────────────────────────────────────────┘
```

**Optimistic locking**: use event version number to prevent concurrent updates

---

## 📸 Snapshots for Performance

Replaying thousands of events is slow. Solution: **periodic snapshots**.

```
Load with snapshot:
  1. Load latest snapshot for aggregateId
  2. Load only events AFTER snapshot version
  3. Apply events to snapshot → current state

Snapshot table:
  { aggregateId, version, state_json }
```

---

## 🔄 Event Sourcing + Sagas

Event sourcing integrates naturally with sagas:

**Choreography-based sagas**: event store publishes events → other services subscribe  
**Orchestration-based sagas**: saga orchestrator also stored as event-sourced aggregate

```
Saga orchestrator stored as events:
  SagaCreated { sagaId, initialState }
  SagaStepCompleted { sagaId, step, result }
  SagaCompleted { sagaId }

→ Saga is fully auditable and recoverable
```

---

## ✅ Benefits and ❌ Drawbacks

### Benefits
- Built-in audit log — history is the source of truth
- Natural publishing of domain events — no outbox needed
- Temporal queries — "what was state at time T?"
- Enables event-driven architecture
- Avoids ORM complexity

### Drawbacks
- Unfamiliar programming model — learning curve
- Querying current state requires CQRS views (see ch. 7)
- Evolving event schemas is challenging
- Eventual consistency of derived views
- Event store tooling is less mature than RDBMS

---

## 💡 Key Takeaways

| Insight | Implication |
|---------|-------------|
| Events are the source of truth | Current state is derived, not stored |
| Command methods return events; apply methods update state | Clean separation of validation and state mutation |
| Event sourcing solves the dual-write problem naturally | Events are persisted atomically with aggregate state |
| Snapshots prevent performance degradation | Add them when replaying becomes slow |
| Use with CQRS for efficient queries | Event store is not designed for ad-hoc queries |

---

*← [Back to Microservices Patterns](../README.md)*
