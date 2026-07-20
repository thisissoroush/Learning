# Chapter 9 — Data Ownership and Distributed Transactions

> *"Who owns the data? Everything else follows from that answer."*

---

## 🎯 Core Concept

In distributed architectures, **data ownership** determines which service has the right to write to a table. This sounds simple but creates complex problems when multiple services need the same data. Getting ownership right is foundational — then you must handle the inevitable distributed transaction challenges that come next.

---

## 🗂️ Assigning Data Ownership

**Rule:** The service that **writes** to a table *owns* that table. Readers must ask the owner.

### Three Ownership Scenarios

**Single Ownership** — one service writes, others read via API:
```
Order Service owns: orders table
  ✓ Clean, simple
  ✓ No conflicts

Other services read: call Order Service API to get order data
```

**Common Ownership** — reference data used by everyone:
```
Product Catalog: read by Inventory, Orders, Billing, Shipping...

Best approach:
  Product Catalog Service owns the table
  All others call it for reads
```

**Joint Ownership** — multiple services need to *write* to the same table:
```
Order table written by:
  Order Service (creates orders)
  Inventory Service (updates inventory-related order fields)
  Shipping Service (updates shipping status)

This is the hard problem. Four techniques to resolve it:
```

---

## 🔧 Joint Ownership Techniques

### Technique 1: Table Split

Divide the table along ownership lines:

```
Before (joint ownership problem):
  orders table: (id, customer_id, status, inventory_status, ship_date, total)
  
After (split by ownership):
  orders table    → Order Service owns (id, customer_id, status, total)
  inventory_orders → Inventory Service owns (order_id, inventory_status)
  shipments       → Shipping Service owns (order_id, ship_date, track_num)
```

**When to use:** When columns have clear ownership boundaries.

### Technique 2: Data Domain

Combine services that share data into a single "data domain" (they share the same DB schema but deploy independently):

```
Order Service   ─▶ ┌─────────────────────┐
Inventory Svc   ─▶ │   orders schema     │
Shipping Svc    ─▶ └─────────────────────┘

All three services have write access to the orders schema.
The schema is the bounded context.
```

**When to use:** When the data is genuinely shared and splitting is too complex.

### Technique 3: Delegate

Assign a single "primary owner" — all writes go through them:

```
Inventory Service wants to update order status:
  ✗ Direct write to orders table
  ✓ Call Order Service API → Order Service writes it

Order Service is the delegate (primary owner).
Inventory Service delegates writes through it.
```

**When to use:** When one service has the most complete picture of the entity.

### Technique 4: Service Consolidation

If joint ownership is pervasive → merge the services:

```
Order Service + Inventory Service + Shipping Service
→ Merged into: Fulfillment Service

Fulfillment Service owns all fulfillment-related tables.
No more joint ownership problem.
```

**When to use:** When the coupling is so tight that splitting provides no real benefit.

---

## 🔄 Distributed Transactions

### The ACID vs. BASE Spectrum

```
ACID (traditional DB):                BASE (distributed):
─────────────────────                 ────────────────────
Atomic (all or nothing)              Basically Available
Consistent (always valid state)      Soft state
Isolated (no interference)           Eventually Consistent
Durable (committed = permanent)

Monolith DB: ACID is free ✓
Distributed services: ACID is expensive or impossible
```

### Why Distributed ACID is Hard

```
Two-Phase Commit (2PC) across services:

Phase 1: "Can you commit?" 
  Service A: "Yes"  Service B: "Yes"  Service C: "Yes"

Phase 2: "Commit now"
  Service A: COMMITTED ✓
  Service B: COMMITTED ✓
  Service C: NETWORK FAILURE → unknown state ✗

2PC problems:
  - Coordinator is a single point of failure
  - Services are locked during the protocol
  - Network failures leave inconsistent state
```

---

## ⏱️ Eventual Consistency Patterns

### Pattern 1: Background Synchronization

```
Service A commits its changes.
A background process periodically syncs data to Service B.

Timeline:
  T=0:  Service A commits Order (status = "PAID")
  T=0:  Service B still shows Order status = "PENDING" (stale)
  T=30s: Background sync runs → Service B updated ✓

Trade-offs:
  ✓ Services are decoupled
  ✓ Simple to implement
  ✗ Data lag (30s or more of inconsistency)
  ✗ Hard to determine when data is "current enough"
```

### Pattern 2: Orchestrated Request-Based

```
Orchestrator coordinates the workflow:

  ┌─────────────┐
  │ Orchestrator│
  └──────┬──────┘
         │ 1. Insert Order
    ┌────▼────┐
    │Order Svc│ ← commits
    └────┬────┘
         │ 2. Reserve Inventory  
    ┌────▼────┐
    │Inventory│ ← commits
    └────┬────┘
         │ 3. Schedule Shipping
    ┌────▼────┐
    │Shipping │ ← commits
    └─────────┘

If Shipping fails:
  Orchestrator calls COMPENSATING TRANSACTIONS:
  - Inventory Service: cancel reservation
  - Order Service: mark order as failed
```

### Pattern 3: Event-Based (Choreography)

```
Services react to events — no central orchestrator:

  Order Service:
    1. Commits order
    2. Publishes: OrderCreated event

  Inventory Service:
    Subscribes to OrderCreated
    1. Reserves inventory
    2. Publishes: InventoryReserved event

  Shipping Service:
    Subscribes to InventoryReserved
    1. Schedules shipment
    2. Publishes: ShipmentScheduled event

  If Inventory fails:
    Publishes: InventoryFailed event
    Order Service subscribes → marks order cancelled
```

---

## ⚖️ Eventual Consistency Comparison

| Pattern | Coupling | Complexity | Data Lag | Best For |
|---------|----------|------------|----------|----------|
| Background Sync | Low | Low | High (seconds-minutes) | Non-critical data sync |
| Orchestrated | Medium | Medium | Low (seconds) | Complex workflows needing tracking |
| Event-Based | Low | High | Low (seconds) | Loosely coupled domains |

---

## 💡 Key Takeaways

| Insight | Implication |
|---------|-------------|
| Data ownership must be determined before service boundaries | Don't design service boundaries without also designing data ownership |
| Joint ownership is the enemy — resolve it with one of four techniques | Table split, data domain, delegate, or consolidate |
| Distributed ACID is effectively impossible at scale | Design for eventual consistency from the start |
| Compensating transactions are the distributed rollback | Every write in a distributed workflow needs a compensating "undo" operation |
| Event-based patterns decouple services but increase complexity | Choose based on how independently services need to evolve |

---

*← [Back to Software Architecture: The Hard Parts](../README.md)*
