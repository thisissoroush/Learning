# Chapter 12 — Transactional Sagas

> *"A saga is a long story of heroic achievement — and distributed transactions certainly qualify."*

---

## 🎯 Core Concept

A **transactional saga** is a pattern for managing distributed transactions across multiple services when ACID transactions are not possible. Instead of one big atomic transaction, a saga is a sequence of local transactions — each with a corresponding **compensating transaction** to undo the work if something goes wrong later.

The key variables that define a saga pattern are three dimensions: **Communication** (sync/async), **Consistency** (atomic/eventual), and **Coordination** (orchestrated/choreographed).

---

## 🔤 The Three Dimensions

```
Communication: Synchronous (s) or Asynchronous (a)
Consistency:   Atomic (a) or Eventual (e)
Coordination:  Orchestrated (o) or Choreographed (c)

Each saga pattern = one combination of these three letters
```

---

## 📚 The 8 Saga Patterns

### 1. Epic Saga `(sao)` — Synchronous + Atomic + Orchestrated

```
Orchestrator calls each service synchronously.
All participants must succeed or the orchestrator calls compensating transactions.

High coupling. Very high risk of cascading failures.
Use only for simple, well-understood workflows needing strict consistency.
```

| Coupling | Very High | Data Consistency | Strong |
|----------|-----------|-----------------|--------|
| Responsiveness | Poor | Complexity | Low |

---

### 2. Phone Tag Saga `(sac)` — Synchronous + Atomic + Choreographed

```
Each service calls the next synchronously (chain of calls).
No central orchestrator — each service is responsible for calling the next.

Like a phone chain: A calls B, B calls C, C calls D...
If D fails, D tells C, C tells B, B tells A → compensating transactions unwind
```

| Coupling | High | Data Consistency | Strong |
|----------|------|-----------------|--------|
| Responsiveness | Poor | Complexity | Medium |

---

### 3. Fairy Tale Saga `(seo)` — Synchronous + Eventual + Orchestrated

```
Orchestrator calls services synchronously but accepts eventual consistency.
Services respond quickly without waiting for downstream effects.

Good middle ground: centralized control with relaxed consistency.
```

| Coupling | High | Data Consistency | Eventual |
|----------|------|-----------------|---------|
| Responsiveness | Medium | Complexity | Medium |

---

### 4. Time Travel Saga `(sec)` — Synchronous + Eventual + Choreographed

```
Services call each other synchronously but accept eventual consistency.
Each service fires-and-forgets after calling the next.

Relatively low coupling given synchronous nature.
Good for workflows where eventual consistency is acceptable.
```

| Coupling | Medium | Data Consistency | Eventual |
|----------|--------|-----------------|---------|
| Responsiveness | Medium | Complexity | Medium |

---

### 5. Fantasy Fiction Saga `(aao)` — Asynchronous + Atomic + Orchestrated

```
Orchestrator sends async messages to each service.
Waits for confirmation before proceeding.
Still needs atomic-like consistency (complex with async).

Very high complexity to ensure atomicity with async communication.
```

| Coupling | High | Data Consistency | Strong (attempted) |
|----------|------|-----------------|-------------------|
| Responsiveness | Good | Complexity | Very High |

---

### 6. Horror Story `(aac)` — Asynchronous + Atomic + Choreographed

```
Services communicate asynchronously in a chain while trying to maintain atomicity.

This combination is extremely hard to get right.
Almost impossible to guarantee atomicity with async choreography.
Avoid unless you have very strong reasons.
```

| Coupling | Medium | Data Consistency | Very Hard to guarantee |
|----------|--------|-----------------|----------------------|
| Responsiveness | Good | Complexity | Extreme |

---

### 7. Parallel Saga `(aeo)` — Asynchronous + Eventual + Orchestrated

```
Orchestrator sends async messages.
Services respond eventually.
Orchestrator tracks state and continues when all responses received.

Good balance: low coupling, orchestrator provides visibility,
eventual consistency is acceptable.

Popular choice for complex workflows.
```

| Coupling | Low | Data Consistency | Eventual |
|----------|-----|-----------------|---------|
| Responsiveness | Very Good | Complexity | Medium |

---

### 8. Anthology Saga `(aec)` — Asynchronous + Eventual + Choreographed

```
Pure event-driven choreography with eventual consistency.
Most decoupled, most scalable, hardest to understand.

Best for independent domains that rarely need to know about each other.
Very low coupling but complex to debug and trace.
```

| Coupling | Very Low | Data Consistency | Eventual |
|----------|----------|-----------------|---------|
| Responsiveness | Excellent | Complexity | High (visibility) |

---

## 🗺️ Pattern Selection Matrix

| Pattern | Code | Coupling | Consistency | Coordination | Best For |
|---------|------|----------|-------------|--------------|----------|
| Epic Saga | `sao` | Very High | Strong | Orchestrated | Simple, strict workflows |
| Phone Tag | `sac` | High | Strong | Choreographed | Sequential strict workflows |
| Fairy Tale | `seo` | High | Eventual | Orchestrated | Orchestrated + relaxed |
| Time Travel | `sec` | Medium | Eventual | Choreographed | Medium coupling needs |
| Fantasy Fiction | `aao` | High | Strong | Orchestrated | Async but strict (complex) |
| Horror Story | `aac` | Medium | Strong | Choreographed | Avoid if possible |
| **Parallel Saga** | **`aeo`** | **Low** | **Eventual** | **Orchestrated** | **Most practical choice** |
| Anthology Saga | `aec` | Very Low | Eventual | Choreographed | Independent domains |

---

## 🔄 Compensating Transactions

Every saga step must have an undo operation:

```
Forward workflow:        Compensating transactions (if step 3 fails):
  1. Place Order    →    Cancel Order
  2. Reserve Stock  →    Release Stock Reservation
  3. Charge Card    ✗    (failed — trigger compensations)
  
  Orchestrator runs:
    Release Stock Reservation (undo step 2)
    Cancel Order (undo step 1)
```

**Key principle:** Design compensating transactions *before* implementing the forward path.

---

## 🔧 Saga State Machines

Track workflow progress with a state machine:

```
States: STARTED → ORDER_PLACED → STOCK_RESERVED → PAYMENT_FAILED
                                                         ↓
                             STOCK_RELEASED ← COMPENSATION_STARTED
                                  ↓
                             ORDER_CANCELLED → COMPLETED
```

Each state transition is stored persistently so sagas can resume after failures.

---

## 💡 Key Takeaways

| Insight | Implication |
|---------|-------------|
| There is no single "saga pattern" — there are 8 | Choose based on your actual coupling, consistency, and coordination needs |
| Parallel Saga (aeo) is the most practical for most cases | Async + eventual + orchestrated balances visibility with decoupling |
| Design compensating transactions first | Every forward step must have a defined undo operation |
| Saga state machines prevent lost workflow progress | Persist state so you can resume after failures |
| Atomic consistency across services is very expensive | Default to eventual consistency unless business absolutely requires atomic |

---

*← [Back to Software Architecture: The Hard Parts](../README.md)*
