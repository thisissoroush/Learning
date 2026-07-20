# Chapter 25 — Layers and Boundaries

> *"You must see the future. You must guess—intelligently."*

---

## 🎯 Core Concept

Real systems have more than three layers (UI, business rules, database). Architectural boundaries exist **everywhere** — the architect must decide which to implement, partially implement, or ignore.

---

## 🎮 Hunt the Wumpus Example

A simple text adventure game reveals hidden boundaries:

```
TextDelivery ──▶ Language API ──▶ GameRules ──▶ DataStorage
    (SMS/Shell)   (EN/ES)        (highest level)  (Flash/Cloud)
```

- **GameRules** = highest-level component (farthest from I/O)
- Each layer defines an API that the layer above owns
- Dependencies always point **upward** toward higher-level policy

---

## 🔀 Multiple Data Streams

As complexity grows, systems split into multiple streams:

```
User ──▶ TextDelivery ──▶ Language ──▶ GameRules
                                           │
                                      DataStorage
                                      Network (multiplayer)
```

Each stream is an axis of change → potential boundary.

---

## ⚖️ The Architect's Dilemma

| Option | Risk |
|--------|------|
| Implement all boundaries upfront | Over-engineering |
| Ignore boundaries | Expensive to add later |
| **Watch and implement at inflection point** | ✅ Best approach |

**The inflection point:** when the cost of implementing a boundary becomes less than the cost of ignoring it.

---

## 💡 Key Takeaways

- Architectural boundaries exist at every axis of change — not just the obvious three
- You don't decide once — you **watch, monitor, and implement** as friction appears
- The Hunt the Wumpus example shows that even trivial programs have hidden boundary complexity
- Good architects continuously weigh cost of implementation vs. cost of ignorance

---

*← [Back to Clean Architecture](../README.md)*
