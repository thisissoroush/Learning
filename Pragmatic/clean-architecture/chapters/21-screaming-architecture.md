# Chapter 21 — Screaming Architecture

> *"Your architecture should tell readers about the system, not about the frameworks you used."*

---

## 🎯 Core Concept

When someone opens your codebase, the top-level structure should immediately communicate **what the system does** — not what framework it uses.

---

## 🏛️ The Analogy

A house blueprint screams **"HOME"**. A library blueprint screams **"LIBRARY"**.

Does your codebase scream **"Health Care System"** or **"Rails App"**?

```
Bad top-level structure:
  /controllers
  /models
  /views
  /migrations
  → Screams "Rails"

Good top-level structure:
  /orders
  /inventory
  /billing
  /customers
  → Screams "E-Commerce System"
```

---

## ⚠️ Frameworks Are Tools, Not Ways of Life

- Frameworks are useful, but they are **tools**
- Don't let a framework dictate your architecture
- Use frameworks at arm's length — they belong in the **outer circles**
- Your use cases should be testable **without** any framework running

---

## ✅ A Testable Architecture

If your architecture screams use cases:
- You can unit test business rules **without a web server**
- You can unit test business rules **without a database**
- Entity objects are plain objects with **no framework dependencies**

---

## 💡 Key Takeaways

- Architecture communicates intent: it should scream the **domain**, not the tools
- Frameworks are options — keep them replaceable
- Use cases should be fully testable in isolation
- The web, the DB, the framework are all **details**

---

*← [Back to Clean Architecture](../README.md)*
