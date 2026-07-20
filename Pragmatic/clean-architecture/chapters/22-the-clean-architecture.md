# Chapter 22 — The Clean Architecture

> *"The Dependency Rule: Source code dependencies must point only inward, toward higher-level policies."*

---

## 🎯 Core Concept

The Clean Architecture unifies Hexagonal Architecture, DCI, and BCE into one diagram with **concentric circles** and a single rule: **dependencies always point inward**.

---

## 🔵 The Four Circles

```
┌─────────────────────────────────────────────┐
│  Frameworks & Drivers (Web, DB, UI)         │  ← Outermost (details)
│  ┌───────────────────────────────────────┐  │
│  │  Interface Adapters                   │  │
│  │  (Controllers, Presenters, Gateways)  │  │
│  │  ┌─────────────────────────────────┐  │  │
│  │  │  Use Cases                      │  │  │
│  │  │  ┌───────────────────────────┐  │  │  │
│  │  │  │  Entities                 │  │  │  │
│  │  │  │  (Business Rules)         │  │  │  │
│  │  │  └───────────────────────────┘  │  │  │
│  │  └─────────────────────────────────┘  │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
         All arrows point INWARD ↑
```

### Layer Responsibilities

| Layer | Role | Examples |
|-------|------|---------|
| **Entities** | Enterprise business rules | Loan, Order, User objects |
| **Use Cases** | App-specific business rules | CreateLoan, PlaceOrder |
| **Interface Adapters** | Convert formats | Controllers, Presenters, Gateways |
| **Frameworks & Drivers** | External tools/details | Spring, MySQL, Angular |

---

## 📏 The Dependency Rule

- **Nothing in an inner circle can know anything about an outer circle**
- Inner circles cannot mention names, classes, or functions from outer circles
- Data passed inward must be converted to formats the inner circle expects

---

## 🔄 Crossing Boundaries

Flow of control: **Controller → Use Case → Presenter**

But source code dependencies must point inward. Solution: **Dependency Inversion**

```
Controller → UseCase (interface) ← UseCaseInteractor
                                      ↓
                            OutputPort (interface) ← Presenter
```

---

## 💡 Key Takeaways

- 4 circles: Entities → Use Cases → Interface Adapters → Frameworks
- The **Dependency Rule** is the single law: always point inward
- Use **DIP** to invert control flow when needed
- Each layer is independently testable and replaceable

---

*← [Back to Clean Architecture](../README.md)*
