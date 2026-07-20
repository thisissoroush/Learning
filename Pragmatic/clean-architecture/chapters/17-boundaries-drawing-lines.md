# Chapter 17 — Boundaries: Drawing Lines

> *"Draw lines between things that matter and things that don't."*

---

## 🎯 Core Concept

Architectural boundaries separate software elements, restricting what each side knows about the other. Lines are drawn to **defer decisions** and **protect business logic** from premature coupling.

---

## 🚫 Premature Decisions Kill Systems

Two cautionary stories:
- **Company P**: Built a 3-tier distributed architecture before knowing if they'd ever need a server farm. They never did — but paid the complexity cost forever.
- **Company W**: An "architect" imposed full enterprise SOA on a small fleet-management app. Adding a contact name required calling ServiceRegistry, firing CreateContact messages, and updating 3 services.

**The lesson**: Over-engineering from premature decisions multiplies development effort enormously.

---

## ✅ The FitNesse Success Story

FitNesse delayed choosing a database by putting **all data access behind an interface** (`WikiPage`). Over 18 months of development:
- No schema issues
- No DB connection issues
- All tests ran fast (no DB to slow them)

Eventually used flat files. One customer added MySQL support themselves — in a day.

> *"Drawing boundary lines helped us delay decisions, and ultimately saved enormous time and headaches."*

---

## 📐 Where to Draw Lines

```
  BusinessRules ──uses──> DatabaseInterface
                                 ▲
                          DatabaseAccess
                                 │
                            (Database)
```

- **BusinessRules** know nothing about the database
- **Database** component depends on BusinessRules (through the interface)
- The arrow points toward the more important component

### What Doesn't Matter to What
| Element | Doesn't Care About |
|---|---|
| Business Rules | GUI, database, framework |
| GUI | Business rules internals |
| Database | Business rules internals |

---

## 🔌 Plugin Architecture

When you draw boundaries correctly, you get a **plugin architecture**: the database and UI plug into business rules, not the other way around.

```
[Web UI] ──────┐
[Console UI] ──┤──> [Business Rules] <── [MySQL DB]
[Mobile UI] ───┘                    <── [Flat Files]
```

Business rules are immune to changes in UI or DB choices.

---

## 💡 Key Takeaways

- Boundaries separate things that **change at different rates and for different reasons**
- Draw lines **between things that matter and things that don't** to the core
- The goal: defer detail decisions as long as possible
- Good architecture = **plugin architecture** where business rules are the core

---

*← [Back to Clean Architecture](../README.md)*
