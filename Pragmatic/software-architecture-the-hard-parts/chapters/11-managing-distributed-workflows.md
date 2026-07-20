# Chapter 11 — Managing Distributed Workflows

> *"Orchestration gives you control. Choreography gives you freedom. Neither is free."*

---

## 🎯 Core Concept

When multiple services collaborate to complete a business workflow, someone must coordinate that work. Two fundamental styles exist: **Orchestration** (a central controller tells each service what to do) and **Choreography** (services react to events and coordinate themselves). Each has profound trade-offs.

---

## 🎼 Orchestration Communication Style

A dedicated **orchestrator service** knows the full workflow and directs each participant.

```
                    ┌───────────────────┐
                    │   Orchestrator    │
                    │  (Workflow Owner) │
                    └────────┬──────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
    1. Place Order    2. Reserve Stock   3. Charge Card
          │                  │                  │
    ┌─────▼──────┐    ┌──────▼─────┐    ┌──────▼─────┐
    │Order Service│   │Inventory   │    │Payment     │
    └────────────┘   │Service     │    │Service     │
                     └────────────┘    └────────────┘
```

**What the orchestrator knows:**
- The full sequence of steps
- What to call next (and with what data)
- How to handle failures (compensating calls)
- Current state of the entire workflow

**Benefits:**
- Easy to track workflow state (all in one place)
- Easier error handling and compensating transactions
- Centralized audit trail
- Simple to understand the full flow

**Shortcomings:**
- Orchestrator becomes a bottleneck and single point of failure
- High coupling: orchestrator knows every participant service
- Changes to workflow logic require orchestrator changes
- Can become a "god service" over time

---

## 💃 Choreography Communication Style

Services react to events — no central coordinator. Each service knows what to do when it sees a particular event.

```
Order Service:
  Receives: PlaceOrder request
  Commits: order
  Publishes: OrderPlaced event
  
Inventory Service:
  Subscribes to: OrderPlaced
  Commits: stock reservation
  Publishes: StockReserved event

Payment Service:
  Subscribes to: StockReserved
  Commits: payment
  Publishes: PaymentProcessed event

Shipping Service:
  Subscribes to: PaymentProcessed
  Schedules: shipment
  Publishes: ShipmentScheduled event
```

**Benefits:**
- Highly decoupled — services don't know about each other
- Easy to add new services (just subscribe to existing events)
- No single point of failure
- Natural asynchrony and scalability

**Shortcomings:**
- **Workflow state is distributed** — hard to answer "where is this order?"
- Error handling complexity — compensating events must propagate backward
- Testing is harder (integration tests must trace event chains)
- Business logic is hidden in event handlers across services

### Workflow State Management in Choreography

The biggest challenge: *Who knows the current state of the whole workflow?*

```
Solution 1: Query each service
  GET /orders/{id} → Order Service: "placed"
  GET /inventory/{id} → Inventory: "reserved"
  GET /payments/{id} → Payment: "processed"
  (expensive, slow, requires knowing all participants)

Solution 2: State store (saga state machine)
  A separate state service or event store tracks which
  events have been processed for each workflow instance.
  
  workflow_state:
    order_id: 12345
    events_received: [OrderPlaced, StockReserved, PaymentProcessed]
    current_status: "awaiting_shipment"
```

---

## ⚖️ Trade-Offs Comparison

| Dimension | Orchestration | Choreography |
|-----------|--------------|--------------|
| **Coupling** | High (orchestrator knows all) | Low (services know only events) |
| **State visibility** | Easy (centralized) | Hard (distributed) |
| **Error handling** | Easier (one place) | Harder (compensating events chain) |
| **Scalability** | Limited by orchestrator | Highly scalable |
| **Extensibility** | Orchestrator must change | Just add new subscriber |
| **Testing** | Easier | Harder |
| **Workflow understanding** | Easy to read | Must trace event chain |

### When to Choose Each

**Orchestration is better when:**
- Workflow has complex error handling requirements
- You need clear audit trails for compliance
- Workflow steps have strict ordering requirements
- The team prioritizes clarity over decoupling

**Choreography is better when:**
- Services need to evolve independently
- Workflow is naturally event-driven
- You need maximum scalability and fault isolation
- Adding new workflow participants frequently

---

## 🔀 Hybrid Approach

Use orchestration within a bounded context, choreography between bounded contexts:

```
Within "Order Fulfillment" domain:
  Orchestrator manages: Place → Reserve → Charge → Ship
  (tight workflow, needs audit trail)

Between domains:
  OrderFulfilled event → triggers:
    Notification Domain (send confirmation email) 
    Analytics Domain (record sale metrics)
    Loyalty Domain (award points)
  (choreography — each domain reacts independently)
```

---

## 💡 Key Takeaways

| Insight | Implication |
|---------|-------------|
| Orchestration = control at the cost of coupling | Use when workflow correctness and traceability matter most |
| Choreography = freedom at the cost of visibility | Use when service independence and scalability matter most |
| State management is choreography's hardest problem | Plan a state tracking solution before adopting choreography |
| Neither pattern is universally superior | Choose based on domain characteristics, not preference |
| Hybrid approaches often make sense | Orchestrate within tight domains, choreograph between loose ones |

---

*← [Back to Software Architecture: The Hard Parts](../README.md)*
