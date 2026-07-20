# Chapter 24 — Partial Boundaries

> *"It is one of the functions of an architect to decide where an architectural boundary might one day exist, and whether to fully or partially implement that boundary."*

---

## 🎯 Core Concept

Full architectural boundaries are **expensive**. Sometimes you anticipate needing one but don't want to pay the full cost yet. Enter **partial boundaries**.

---

## 🔧 Three Strategies

### 1. Skip the Last Step
Do all the work: create the interfaces, data structures, and dependency management — but deploy everything as a single component. You get the design without the operational overhead.

```
[Component A] ──interface──▶ [Component B]
       └──────── same .jar file ──────────┘
```

### 2. One-Dimensional Boundary (Strategy Pattern)
Use an interface to separate client from implementation, but without a reciprocal boundary:

```
Client ──▶ ServiceBoundary (interface) ◀── ServiceImpl
```
Risk: nothing prevents backward coupling without discipline.

### 3. Facade Pattern
Even simpler — the `Facade` class routes calls but the client can still reach through it:

```
Client ──▶ Facade ──▶ ServiceA, ServiceB, ServiceC
```
Least protection; highest risk of accidental coupling.

---

## ⚖️ Trade-offs

| Strategy | Setup Cost | Maintenance | Protection |
|----------|-----------|-------------|------------|
| Skip Last Step | High | Low | High |
| Strategy Pattern | Medium | Medium | Medium |
| Facade | Low | Low | Low |

---

## 💡 Key Takeaways

- Don't always build full boundaries — they cost time and complexity
- Partial boundaries **hold a place** for future full boundaries
- Choose the level of protection based on likelihood of change
- Watch for degradation: partial boundaries rot without discipline

---

*← [Back to Clean Architecture](../README.md)*
