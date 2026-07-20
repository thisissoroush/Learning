# Chapter 5 — Designing Business Logic in a Microservice Architecture

> *"The Aggregate pattern structures a service's business logic as a collection of aggregates."*

---

## 🎯 Core Concept

Business logic is the heart of any service. In microservices, the challenge is that business logic can't span services the way it does in a monolith. The **DDD Aggregate pattern** is the key building block — it defines explicit boundaries, enforces invariants, and fits perfectly within the one-transaction-per-aggregate rule that microservices require.

---

## 📋 Two Patterns for Organizing Business Logic

### 1. Transaction Script (Procedural)

```
┌──────────────────┐      ┌──────────────────┐
│   OrderService   │      │   Order (DTO)    │
│  createOrder()   │─────▶│  - orderId       │
│  cancelOrder()   │      │  - lineItems     │
│  reviseOrder()   │      │  - status        │
└──────────────────┘      └──────────────────┘
  Classes with behavior    Classes with only state
```

**Use when**: Simple CRUD operations, low-complexity logic  
**Don't use when**: Complex invariants, many business rules

### 2. Domain Model (Object-Oriented) ✅ Preferred

```
┌──────────────────────────────────┐
│   Order (Entity)                 │
│  - orderId, status, lineItems   │
│  + create() [factory]           │
│  + cancel()                     │
│  + revise()                     │
│  + approve()                    │
└──────────────────────────────────┘
     Business logic INSIDE the object
```

**Use when**: Complex business rules, multiple invariants, rich domain

---

## 🧩 DDD Tactical Patterns

| Pattern | Description | Example |
|---------|-------------|---------|
| **Entity** | Object with persistent identity | Order, Consumer |
| **Value Object** | Object defined by its attributes | Money, Address |
| **Aggregate** | Cluster of objects treated as a unit | Order + LineItems |
| **Repository** | Accesses persistent aggregates | OrderRepository |
| **Service** | Business logic not in entities | OrderService |
| **Factory** | Creates complex objects | Order.create() |
| **Domain Event** | Something notable that happened | OrderCreated |

---

## 🏰 The DDD Aggregate Pattern

An aggregate is a **cluster of objects** with a single **root entity**. All external access goes through the root.

```
Order Aggregate (Boundary = dashed box)
┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐
│  ┌─────────────────┐                          │
│  │  Order (ROOT)   │ ← external access only   │
│  │  - orderId      │   goes through here       │
│  │  - status       │                          │
│  │  + approve()    │                          │
│  │  + cancel()     │                          │
│  └────────┬────────┘                          │
│           │ has many                          │
│  ┌────────▼────────┐  ┌─────────────────┐    │
│  │ OrderLineItem   │  │ DeliveryInfo    │    │
│  │ - menuItemId    │  │ - address       │    │
│  │ - quantity      │  │ - time          │    │
│  │ - price         │  └─────────────────┘    │
│  └─────────────────┘                          │
└ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘
```

### Three Aggregate Rules

**Rule 1**: Only the aggregate **root** can be referenced from outside  
→ No `orderLineItemRepo.save(lineItem)` — always `orderRepo.save(order)`

**Rule 2**: Inter-aggregate references use **primary keys**, not object references  
```java
// Wrong: Order holds a Consumer object
Order { Consumer consumer; }

// Right: Order holds consumer's ID
Order { Long consumerId; }  // ← loose coupling
```

**Rule 3**: **One transaction = one aggregate**  
→ Updating multiple aggregates requires a Saga

### Why Aggregates Fit Microservices

```
Traditional ORM problem:
  Order.getConsumer() → lazy loads Consumer → spans service boundary! ❌

Aggregate solution:
  Order has consumerId (Long) → no cross-service object reference ✅
  One transaction per aggregate → fits microservice transaction model ✅
```

---

## 📣 Domain Events

A **domain event** signals that something happened — an aggregate changed state.

```
Why publish events?
  → Other services need to react (Sagas)
  → Maintain CQRS views
  → Notify external systems
  → Audit trail

Order Domain Events:
  OrderCreated       → trigger Create Order Saga
  OrderApproved      → notify consumer
  OrderCancelled     → update delivery, accounting
  OrderShipped       → notify consumer
```

### Generating Events

```java
public class Order {
  public static ResultWithEvents<Order> createOrder(
      long consumerId, Restaurant restaurant, List<OrderLineItem> lineItems) {

    Order order = new Order(consumerId, restaurant.getId(), lineItems);
    List<DomainEvent> events = singletonList(
        new OrderCreated(lineItems, restaurant.getName())
    );
    return new ResultWithEvents<>(order, events);
  }
}
```

The service collects events from the aggregate and publishes them after the transaction commits.

### Event Enrichment

Two approaches for event payloads:

| Approach | Description | Trade-off |
|----------|-------------|-----------|
| **Thin events** | Only IDs, consumers fetch details | Consumers make extra queries |
| **Fat events** | Include full snapshot of state | Simpler consumers, larger events |

---

## 🛒 Order Aggregate — Full Example

```
Order State Machine:
APPROVAL_PENDING
    │ authorize card success
    ▼
APPROVED
    │ customer requests cancel
    ▼
CANCEL_PENDING
    │ safe to cancel
    ▼
CANCELLED

Methods on Order aggregate root:
  + approve()        → APPROVAL_PENDING → APPROVED
  + reject()         → APPROVAL_PENDING → REJECTED
  + cancel()         → APPROVED → CANCEL_PENDING
  + confirmCancel()  → CANCEL_PENDING → CANCELLED
  + undoCancel()     → CANCEL_PENDING → APPROVED
  + revise()         → APPROVED → REVISION_PENDING
```

---

## 🍳 Kitchen Service Ticket Aggregate

```
Ticket (Kitchen Service's view of an Order):
┌──────────────────────────────────────┐
│  Ticket                              │
│  - ticketId                          │
│  - orderId (FK to Order aggregate)  │
│  - status: CREATE_PENDING →          │
│            AWAITING_ACCEPTANCE →    │
│            ACCEPTED → PREPARING →   │
│            READY_FOR_PICKUP →        │
│            PICKED_UP                 │
│  - lineItems                         │
│  - prepareByTime                     │
│                                      │
│  + accept()                          │
│  + preparing()                       │
│  + readyForPickup()                  │
└──────────────────────────────────────┘
```

The Ticket aggregate is *Kitchen Service's* domain model — not a copy of the Order, but a service-specific view of what matters for kitchen operations.

---

## 💡 Key Takeaways

| Insight | Implication |
|---------|-------------|
| Use Domain Model pattern for complex business logic | Transaction Script only for simple CRUD |
| Aggregates are the unit of consistency | Enforce invariants via aggregate root methods |
| One transaction per aggregate — by design | Cross-aggregate updates = Sagas |
| Inter-aggregate refs use primary keys | Prevents accidental cross-service coupling |
| Domain events are the glue between services | Every aggregate state change = potential event |
| Each service has its own domain model | Order in Order Service ≠ Ticket in Kitchen Service |

---

*← [Back to Microservices Patterns](../README.md)*
