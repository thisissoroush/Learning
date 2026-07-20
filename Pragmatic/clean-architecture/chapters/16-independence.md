# Chapter 16 — Independence

> *"A good architecture allows a system to be born as a monolith, grow into independently deployable units, and then slide all the way back if needed."*

---

## 🎯 Core Concept

Good architecture supports **four dimensions of independence**: use cases, operation, development, and deployment. Achieving all four means decoupling layers and use cases.

---

## 📐 Decoupling Layers

Separate things that change for **different reasons**:
- **UI** — changes for user-facing reasons
- **Application-specific business rules** — validate inputs, control flows
- **Application-independent business rules** — interest calculations, inventory logic
- **Database** — schema, query language, storage engine

Each layer changes at a different rate and for different reasons → separate them.

---

## ✂️ Decoupling Use Cases

Use cases are **vertical slices** through horizontal layers. Each use case touches UI, business rules, and database — but separately.

```
         Add Order │ Delete Order │ View Order
         ──────────┼──────────────┼──────────
UI       [add UI]  │  [del UI]   │ [view UI]
Rules    [add BL]  │  [del BL]   │ [view BL]
DB       [add DB]  │  [del DB]   │ [view DB]
```

This lets new use cases be added without interfering with old ones.

---

## ⚙️ Decoupling Modes

Three levels of decoupling:

| Mode | Mechanism | Communication | When to Use |
|---|---|---|---|
| **Source level** | Separate modules/packages | Function calls (monolith) | Early project stages |
| **Deployment level** | Separate JARs/DLLs | Function calls + IPC | When teams need independence |
| **Service level** | Separate processes/services | Network packets | When scaling operationally |

**Uncle Bob's preference**: decouple at source level first, evolve to service level only if operationally necessary.

---

## ⚠️ True vs. Accidental Duplication

Not all similar-looking code is real duplication:
- **True duplication** — every change to one requires change to the other → eliminate
- **Accidental duplication** — looks similar now but will diverge over time → **keep separate**

Resist merging use case code just because the screens look similar today.

---

## 💡 Key Takeaways

- Decouple **layers** (horizontal) and **use cases** (vertical) independently
- Choose the right **decoupling mode** for where you are in the project lifecycle
- Don't confuse **true duplication** with **accidental duplication**
- Good architecture lets you slide between monolith ↔ services as needs change

---

*← [Back to Clean Architecture](../README.md)*
