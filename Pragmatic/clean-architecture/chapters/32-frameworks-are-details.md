# Chapter 32 — Frameworks Are Details

> *"Don't marry the framework. You can use it — just don't couple to it."*

---

## 🎯 Core Concept

Frameworks are powerful tools, but they are **details** — not architectures. When you let a framework dictate your architecture, you've given up control of your own system.

---

## 💍 The Asymmetric Marriage

The relationship between you and a framework is deeply unequal:

| You | Framework Author |
|-----|-----------------|
| Must conform to framework conventions | Writes for their own problems |
| Must upgrade when framework changes | Makes no commitment to you |
| Risks lock-in for entire app lifetime | Gains users/validation |
| Bears all the architectural risk | Bears none |

---

## ⚠️ The Risks of Coupling to a Framework

```
❌ Framework in your Entities (innermost circle)
   → Your domain objects extend framework classes
   → Your business rules import framework annotations (@Entity, @Autowired)
   → Framework version changes break your core logic
```

```
✅ Framework as a plugin (outermost circle)
   → Business rules have no framework imports
   → Framework wires things together in Main
   → You can swap frameworks without touching core
```

---

## 🏗️ The Right Approach

```
┌─────────────────────────────────────┐
│         Framework / Rails / Spring  │  ← outermost circle
│  ┌───────────────────────────────┐  │
│  │    Interface Adapters         │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │     Use Cases           │  │  │
│  │  │  ┌───────────────────┐  │  │  │
│  │  │  │    Entities       │  │  │  │  ← no framework here!
│  │  │  └───────────────────┘  │  │  │
│  │  └─────────────────────────┘  │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

---

## 💡 Practical Example

```java
// ❌ Wrong: Framework invades your business object
@Entity
@Table(name = "orders")
public class Order {
    @Id
    private Long id;
    // business logic mixed with ORM annotations
}

// ✅ Right: Plain domain object, framework stays outside
public class Order {
    private OrderId id;
    private Money total;
    // pure business logic, no framework imports
}
```

---

## 💡 Key Takeaways

- Frameworks are tools to use, not architectures to conform to
- Never let framework code reach your Entities or Use Cases
- Use frameworks in the outermost layer; inject at Main
- Treat adopting a framework as a long-term commitment — choose carefully
- Some frameworks you must marry (STL, Java stdlib) — that's okay, but be conscious

---

*← [Back to Clean Architecture](../README.md)*
