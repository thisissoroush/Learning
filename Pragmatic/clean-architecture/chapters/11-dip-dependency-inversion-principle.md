# Chapter 11 — DIP: The Dependency Inversion Principle

> *"High-level policy should not depend on low-level details. Details should depend on policies."*

---

## 🎯 Core Concept

The most flexible systems depend on **abstractions**, not concretions. Source code dependencies should point toward stable abstract interfaces — never toward volatile, frequently-changing implementations.

---

## 📐 The Rule

In statically typed languages: `import`, `use`, and `include` statements should reference **interfaces or abstract classes** — never concrete implementations.

---

## 🔀 Dependency Inversion Diagram

```
┌─────────────────────────────────────────┐
│         Abstract Side (stable)           │
│  Application ──► ServiceFactory (iface) │
│  Application ──► Service (iface)         │
└──────────────────────┬──────────────────┘
            curved boundary
┌──────────────────────▼──────────────────┐
│         Concrete Side (volatile)         │
│  ServiceFactoryImpl ──► ConcreteImpl     │
└─────────────────────────────────────────┘
```

All source code dependencies cross the boundary **pointing toward abstractions**. Flow of control crosses in the opposite direction — that's the inversion.

---

## 📋 Practical Rules

| Rule | Explanation |
|---|---|
| Don't refer to volatile concrete classes | Use abstract interfaces instead |
| Don't derive from volatile concrete classes | Inheritance is the strongest coupling |
| Don't override concrete functions | You inherit their dependencies too |
| Never mention volatile concrete names | Even in strings or comments, avoid hard-coding |

---

## 🏭 Abstract Factory Pattern

Since you can't avoid creating objects at some point, use **Abstract Factories**:

```java
// Application code (abstract side)
ServiceFactory factory = ...;
Service svc = factory.makeSvc(); // never mentions ConcreteImpl

// Main/Concrete side
ServiceFactoryImpl implements ServiceFactory {
    Service makeSvc() { return new ConcreteImpl(); }
}
```

`Main` is the only component that knows about concrete things — it's the "dirtiest" component.

---

## 💡 Key Takeaways

- Depend on abstractions, not concretions — especially for volatile things
- Stable things (like `String` in Java) are OK to depend on concretely
- Use Abstract Factory to isolate object creation from the rest of the system
- DIP is the architectural glue that makes all other principles work together

---

*← [Back to Clean Architecture](../README.md)*
