# Chapter 23 — Presenters and Humble Objects

> *"At each architectural boundary, we are likely to find the Humble Object pattern lurking somewhere nearby."*

---

## 🎯 Core Concept

The **Humble Object Pattern** separates hard-to-test behavior from easy-to-test behavior. It naturally emerges at every architectural boundary.

---

## 🧩 The Pattern

Split code at boundaries into two pieces:
- **Humble Object** — hard to test (e.g., the View that pushes strings to the screen)
- **Testable Object** — easy to test (e.g., the Presenter that formats the data)

```
┌──────────────────┐         ┌──────────────────┐
│   Use Case       │──data──▶│   Presenter      │  ← TESTABLE
│   (Interactor)   │         │   (formats data) │
└──────────────────┘         └────────┬─────────┘
                                      │ ViewModel
                                      ▼
                             ┌──────────────────┐
                             │   View           │  ← HUMBLE
                             │   (just renders) │
                             └──────────────────┘
```

---

## 🎨 Presenters and Views

| Role | Responsibility | Testable? |
|------|---------------|-----------|
| **Presenter** | Formats data into strings/flags for display | ✅ Yes |
| **View** | Pushes ViewModel data to the screen | ❌ Hard |

**Rule:** The View does almost nothing — just maps ViewModel to screen. All logic lives in the Presenter.

---

## 🗄️ Database Gateways

Between use cases and the database live **gateway interfaces**:
- Use cases call gateway interfaces (testable — stubs can be injected)
- Concrete implementations (humble objects) use SQL/ORM directly

---

## 💡 Key Takeaways

- The Humble Object pattern naturally marks **architectural boundaries**
- Separate what is hard to test (I/O, UI, DB) from what is easy to test (logic)
- Presenters are testable; Views are humble
- Database gateways decouple use cases from SQL — the implementation is humble

---

*← [Back to Clean Architecture](../README.md)*
