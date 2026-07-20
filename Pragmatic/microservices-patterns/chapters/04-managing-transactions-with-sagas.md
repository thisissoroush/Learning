# Chapter 4 — Managing Transactions with Sagas

> *"Sagas are mechanisms to maintain data consistency in a microservice architecture without having to use distributed transactions."*

---

## 🎯 Core Concept

ACID transactions are the foundation of data consistency in a monolith. In microservices, each service owns its own database — so traditional distributed transactions (2PC/XA) don't work at scale. The **Saga pattern** is the solution: a sequence of local transactions coordinated using asynchronous messaging. The tradeoff is losing **Isolation** — and countermeasures are how we cope with that.

---

## ❌ Why Distributed Transactions (2PC/XA) Don't Work

Traditional approach: **X/Open XA Two-Phase Commit**

```
Coordinator        Service A          Service B
     │──prepare──▶│                  │
     │──prepare──────────────────────▶│
     │◀──ready────│                  │
     │◀──ready────────────────────────│
     │──commit──▶│                  │
     │──commit────────────────────────▶│

Problems:
  1. Many NoSQL DBs and modern brokers don't support XA
  2. Availability = product of all participants
     (99.5% × 99.5% × 99.5% = 98.5%)
  3. CAP theorem: choose availability OR consistency
```

---

## 🎭 Pattern: Saga

> A saga is a **sequence of local transactions** where each step publishes a message or event to trigger the next step.

```
Create Order Saga
┌──────────────────────────────────────────────────┐
│  Step 1: Order Service        → Create Order     │
│  Step 2: Consumer Service     → Verify Consumer  │
│  Step 3: Kitchen Service      → Create Ticket    │
│  Step 4: Accounting Service   → Authorize Card   │
│  Step 5: Kitchen Service      → Approve Ticket   │
│  Step 6: Order Service        → Approve Order    │
└──────────────────────────────────────────────────┘

Each step commits to its local DB.
If step N fails → compensating transactions for steps 1..N-1
```

**Sagas are ACD** (not ACID) — they lack Isolation.

---

## 🔄 Compensating Transactions

When a step fails, the saga **rolls back** by executing compensating transactions in reverse order.

```
Normal flow:    T1 → T2 → T3 → T4 (FAILS)
Rollback flow:            C3 → C2 → C1

Create Order Saga compensation map:
┌──────┬────────────────────┬─────────────────────┐
│ Step │ Transaction        │ Compensating Txn    │
├──────┼────────────────────┼─────────────────────┤
│  1   │ createOrder()      │ rejectOrder()       │
│  2   │ verifyConsumer()   │ — (read-only)       │
│  3   │ createTicket()     │ rejectTicket()      │
│  4   │ authorizeCard()    │ — (pivot)           │
│  5   │ approveTicket()    │ — (retriable)       │
│  6   │ approveOrder()     │ — (retriable)       │
└──────┴────────────────────┴─────────────────────┘
```

Three transaction types in a saga:
- **Compensatable**: can be rolled back (steps 1–3)
- **Pivot**: go/no-go point — if it succeeds, saga completes (step 4)
- **Retriable**: always succeed, no rollback needed (steps 5–6)

---

## 🎪 Saga Coordination: Choreography

**No central controller.** Participants react to each other's events.

```
CHOREOGRAPHY — Create Order Saga (happy path)

Order Service ──OrderCreated event──▶ Consumer Service
                                     │ ──ConsumerVerified──▶
                                     │
                                     ▼
              ──OrderCreated event──▶ Kitchen Service
                                     │ ──TicketCreated──▶
                                     ▼
                                     Accounting Service
              ──OrderCreated──▶     │ ──CreditCardAuthorized──▶
                                     ▼
              ◀──CreditCardAuthorized── Kitchen Service
                                     (approve ticket)
              ◀──CreditCardAuthorized── Order Service
                                     (approve order)
```

**Pros**: Simple, no single point of control, loose coupling  
**Cons**: Hard to understand as a whole, cyclic dependencies between services, distributed logic

---

## 🎯 Saga Coordination: Orchestration (Recommended)

**A central orchestrator** tells each participant what to do using command/reply messaging.

```
ORCHESTRATION — Create Order Saga

                    ┌─────────────────────────┐
                    │  CreateOrderSaga         │
                    │  (state machine)         │
                    └────────────┬────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼
Consumer Service          Kitchen Service          Accounting Service
  verifyConsumer()          createTicket()          authorizeCard()
  ──reply──▶               ──reply──▶               ──reply──▶
        │                        │                        │
        └────────────────────────┴────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  Orchestrator receives   │
                    │  all replies and decides │
                    │  next steps              │
                    └─────────────────────────┘
```

### State Machine Model

The orchestrator is modeled as a **state machine**:

```
[Verifying Consumer]
       │ ConsumerVerified
       ▼
[Creating Ticket]
       │ TicketCreated         │ Ticket creation failed
       ▼                        ▼
[Authorizing Card]         [Rejecting Order]
       │ Card Authorized        │ → final state: Order Rejected
       ▼
[Approving Ticket]
       │
       ▼
[Approving Order]
       │
       ▼
  Order Approved ← final state
```

**Pros**: No cyclic dependencies, clear logic in one place, simpler domain objects  
**Cons**: Risk of centralizing too much — keep orchestrators focused on sequencing, not business logic

---

## ⚠️ Handling Lack of Isolation

Sagas lack isolation — concurrent sagas can interfere. Three anomalies:

| Anomaly | What Happens |
|---------|-------------|
| **Lost updates** | Saga A overwrites Saga B's changes |
| **Dirty reads** | Saga reads data mid-update by another saga |
| **Fuzzy reads** | Same data read twice gives different results |

### Countermeasures

| Countermeasure | How It Works |
|----------------|-------------|
| **Semantic Lock** | Mark record with `*_PENDING` state while updating |
| **Commutative Updates** | Design ops executable in any order (debit/credit) |
| **Pessimistic View** | Reorder saga steps to reduce dirty read risk |
| **Reread Value** | Re-read record before updating to detect changes |
| **Version File** | Record operations, reorder to handle out-of-order |
| **By Value** | Use distributed transactions only for high-risk operations |

### Semantic Lock Example (most common)

```
Order States:
  APPROVAL_PENDING → being created (locked)
  APPROVED         → creation complete (lock released)
  REVISION_PENDING → being revised (locked)
  CANCEL_PENDING   → being cancelled (locked)
  CANCELLED        → cancelled (lock released)

If another saga tries to modify an order in *_PENDING state:
  Option A: Return error (client retries)
  Option B: Block until lock released
  Option C: Detect and rollback (deadlock prevention)
```

---

## 🔧 Implementation: CreateOrderSaga in Java

The author uses the **Eventuate Tram Saga** framework. Here's the structure:

```java
// Saga orchestrator definition using DSL
public class CreateOrderSaga implements SimpleSaga<CreateOrderSagaState> {

  private SagaDefinition<CreateOrderSagaState> sagaDefinition =
    step()
      .withCompensation(orderService.reject,
                        state::makeRejectOrderCommand)
    .step()
      .invokeParticipant(consumerService.validate,
                         state::makeValidateConsumerCommand)
    .step()
      .invokeParticipant(kitchenService.create,
                         state::makeCreateTicketCommand)
      .onReply(CreateTicketReply.class,
               state::handleCreateTicketReply)
      .withCompensation(kitchenService.cancel,
                        state::makeCancelTicketCommand)
    .step()
      .invokeParticipant(accountingService.authorize,
                         state::makeAuthorizeCommand)
    .step()
      .invokeParticipant(kitchenService.approve,
                         state::makeApproveTicketCommand)
    .step()
      .invokeParticipant(orderService.approve,
                         state::makeApproveOrderCommand)
    .build();
}
```

```
Key classes:
┌────────────────────────┐    ┌────────────────────────┐
│ CreateOrderSaga        │    │ CreateOrderSagaState    │
│ (orchestrator logic)   │    │ (persisted saga data)  │
│ - sagaDefinition       │    │ - orderId              │
│ - getSagaDefinition()  │    │ - orderDetails         │
└────────────────────────┘    │ - ticketId             │
                              │ + make*Command()       │
                              └────────────────────────┘

┌────────────────────────┐    ┌────────────────────────┐
│ KitchenServiceProxy    │    │ SagaManager            │
│ (typed endpoint def)   │    │ (framework)            │
│ - create               │    │ - persists saga state  │
│ - confirmCreate        │    │ - sends messages       │
│ - cancel               │    │ - handles replies      │
└────────────────────────┘    └────────────────────────┘
```

---

## 💡 Key Takeaways

| Insight | Implication |
|---------|-------------|
| Distributed transactions (2PC) don't scale in microservices | Use Sagas instead |
| Sagas maintain eventual consistency, not immediate | Design UIs/clients to handle pending states |
| Choreography = decentralized; Orchestration = centralized | Use orchestration for complex sagas |
| Model orchestrators as state machines | Easier to reason about, test, and debug |
| Sagas lack isolation — design for it | Use semantic locks (*_PENDING states) proactively |
| Compensating transactions are explicit rollbacks | Not all steps need one (retriable and pivot steps don't) |

---

*← [Back to Microservices Patterns](../README.md)*
