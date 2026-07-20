# Chapter 14 — Component Coupling

> *"Allow no cycles in the component dependency graph."*

---

## 🎯 Core Concept

Three principles govern **relationships between components**. Violate them and you get build nightmares, "morning after syndrome," and systems that resist change.

---

## 🔄 ADP — Acyclic Dependencies Principle

**No cycles in the component dependency graph.**

### The "Morning After Syndrome"
You work all day, get code working, go home — then the next morning it's broken because someone changed something you depend on.

### Solution: Make Components a DAG (Directed Acyclic Graph)

```
Main ──► Controllers ──► Presenters ──► Views
              │
              ▼
         Interactors ──► Entities
              │
              ▼
           Database
```

Every arrow points **one direction only** — no cycles. This lets you:
- Build and test components independently
- Release components incrementally
- Trace impact of changes by following arrows backward

### Breaking Cycles

1. **Apply DIP** — insert an interface to invert the dependency
2. **Create a new component** — extract shared code both depend on

---

## 📐 SDP — Stable Dependencies Principle

**Depend in the direction of stability.**

### Stability Metrics
- **Fan-in**: incoming dependencies (makes component stable — others rely on it)
- **Fan-out**: outgoing dependencies (makes component unstable — affected by others)
- **I = Fan-out / (Fan-in + Fan-out)** → I=0 maximally stable, I=1 maximally unstable

### Rule
Dependencies should flow toward **lower I** (more stable) components. Don't let a stable component depend on a volatile one.

```
Unstable (I=1) ──► Stable (I=0)    ✅ Correct
Stable (I=0)   ──► Unstable (I=1)  ❌ Violation!
```

---

## 🏛️ SAP — Stable Abstractions Principle

**A component should be as abstract as it is stable.**

| Stability | Abstractness | Location | Status |
|---|---|---|---|
| Stable (I=0) | Abstract (A=1) | Upper-left | ✅ Ideal |
| Unstable (I=1) | Concrete (A=0) | Lower-right | ✅ Ideal |
| Stable (I=0) | Concrete (A=0) | Zone of Pain | ❌ Rigid, hard to extend |
| Unstable (I=1) | Abstract (A=1) | Zone of Uselessness | ❌ Unused abstractions |

### The Main Sequence
The line from (I=1, A=0) to (I=0, A=1) is the **Main Sequence** — the ideal zone. Keep components close to this line.

**Distance metric:** `D = |A + I - 1|` → aim for D ≈ 0

---

## 💡 Key Takeaways

- **ADP**: No cycles — use DAGs, break cycles with DIP or new components
- **SDP**: Dependencies flow toward stability (lower I)
- **SAP**: Stable components must be abstract to remain extensible
- Component structure is NOT designed top-down — it evolves as the system grows

---

*← [Back to Clean Architecture](../README.md)*
