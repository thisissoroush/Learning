# Chapter 5 — Object-Oriented Programming

> *"OO is the ability, through polymorphism, to gain absolute control over every source code dependency in the system."*

---

## 🎯 Core Concept

OO's true power isn't encapsulation or inheritance — it's **polymorphism**, and specifically, how polymorphism enables **Dependency Inversion**. This gives architects complete control over the direction of source code dependencies.

---

## 🔍 The Three Pillars — Examined Critically

### Encapsulation?
- C had **perfect** encapsulation (header files = interface, .c files = hidden impl)
- C++ actually **weakened** encapsulation (member vars must be in header)
- Java/C# abolished header/impl split entirely → weaker encapsulation
- **Verdict: OO didn't invent encapsulation; it partially broke it**

### Inheritance?
- C programmers faked inheritance by ordering struct fields identically
- OO just made it more convenient and type-safe
- **Verdict: Half a point — OO made existing trick convenient**

### Polymorphism?
- Unix IO drivers used function pointers (FILE struct) for polymorphism since the 1950s
- OO made it **safe** and **convenient** — removing dangerous manual conventions
- **Verdict: The real win — safe, convenient polymorphism**

---

## 💡 Dependency Inversion — The Real Power

Before OO: source code dependencies followed the flow of control.

```
main() → calls → high-level functions → calls → low-level functions
  │                    │                              │
  └──── depends on ────┴──────── depends on ──────────┘
  (source code dependencies flow same direction as control)
```

With OO polymorphism, you can **invert** any dependency:

```
High-Level Policy          Low-Level Detail
┌─────────────┐            ┌──────────────┐
│   Business  │──uses──→  │  «interface» │
│   Rules     │            │   IDatabase  │
└─────────────┘            └──────┬───────┘
                                  │ implements
                           ┌──────▼───────┐
                           │  MySQL Impl  │
                           └──────────────┘

Arrow of dependency points UP (toward policy), not down toward detail.
```

**This means:**
- Database and UI can depend on business rules (not the reverse)
- Business rules can be compiled and deployed independently
- Teams can work independently on different components

---

## 🖼️ Example: Plugin Architecture

```
                ┌─────────────────┐
                │  Business Rules  │
                └────────┬────────┘
                         │ ← all dependencies point HERE
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │   Web UI  │  │ Database │  │  Mobile  │
    │ (plugin)  │  │ (plugin) │  │ (plugin) │
    └──────────┘  └──────────┘  └──────────┘
```

Business rules never mention UI or Database. They're plugins.

---

## 💡 Key Takeaways

- OO = disciplined polymorphism → safe dependency inversion
- Architects use OO to control **direction** of all source code dependencies
- This enables independently deployable and developable components
- The true definition: OO gives architects absolute control over dependency direction

---

*← [Back to Clean Architecture](../README.md)*
