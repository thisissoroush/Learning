# Chapter 6 — Functional Programming

> *"Variables in functional languages do not vary."*

---

## 🎯 Core Concept

Functional programming imposes discipline on **variable assignment**. Immutable variables eliminate entire categories of concurrency bugs — race conditions, deadlocks, and concurrent update problems cannot exist if nothing is ever mutated.

---

## 🔄 Immutability and Architecture

All concurrency problems stem from **mutable state**:

```
Race conditions        → two threads write same variable simultaneously
Deadlocks              → two threads wait for each other's locks
Concurrent updates     → shared mutable data gets corrupted

Functional solution:   No mutation = none of these problems exist
```

---

## ⚖️ Segregation of Mutability

Since pure immutability isn't always practical, the compromise is to **segregate**:

```
┌─────────────────────────────┐
│    Immutable Components      │  ← pure functions, no side effects
│    (most of the app)         │       easy to test, safe to parallelize
└──────────────┬──────────────┘
               │ communicate with
┌──────────────▼──────────────┐
│    Mutable Components        │  ← carefully guarded state
│    (small, isolated)         │       protected by transactional memory
└─────────────────────────────┘
```

**Rule:** Push as much processing as possible into immutable components.

---

## 📖 Event Sourcing

Instead of storing **current state**, store only **transactions**:

```
Traditional:
  Account balance = $500  (mutable, can be corrupted)

Event Sourcing:
  Deposit $1000
  Withdraw $200
  Withdraw $300
  ──────────────
  Balance = $500  (computed, never mutated, fully auditable)
```

No updates or deletes → no concurrent update issues → effectively immutable.

> This is exactly how your source control system works.

---

## 💡 Key Takeaways

- FP = discipline on assignment → variables don't change
- Immutability eliminates race conditions, deadlocks, concurrent update bugs
- Segregate mutable from immutable components; minimize mutable parts
- Event sourcing is a practical path to immutability at scale

---

*← [Back to Clean Architecture](../README.md)*
