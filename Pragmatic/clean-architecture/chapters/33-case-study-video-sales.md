# Chapter 33 — Case Study: Video Sales

> *"The architecture should tell readers about the system, not about the frameworks used."*

---

## 🎯 Core Concept

This chapter applies all the book's principles to a real system: a video sales website (like cleancoders.com). It shows how to move from actors and use cases to a full component architecture.

---

## 👤 Step 1: Identify Actors & Use Cases

Four main actors drive all changes in this system:

| Actor | Example Use Cases |
|-------|-------------------|
| **Viewer** | View catalog, stream video |
| **Purchaser** | Buy license, download video |
| **Author** | Upload video, add descriptions |
| **Admin** | Add series, set prices |

> **SRP insight:** Each actor is a separate source of change. Partition the system so one actor's changes don't ripple to others.

---

## 🏗️ Step 2: Component Architecture

The system is divided following Clean Architecture layers:

```
┌─────────────────────────────────────────────────┐
│                    Views                         │
│  (Viewer Views | Purchaser Views | Admin Views)  │
├─────────────────────────────────────────────────┤
│                  Presenters                      │
│  (Catalog Presenter | Purchase Presenter | ...)  │
├─────────────────────────────────────────────────┤
│                  Controllers                     │
├─────────────────────────────────────────────────┤
│                  Interactors                     │  ← Use Cases
├─────────────────────────────────────────────────┤
│         Entities (Video, License, User)          │  ← Business Rules
├─────────────────────────────────────────────────┤
│              Database / Utilities                │
└─────────────────────────────────────────────────┘
```

Each actor group gets its **own slice** through all layers.

---

## 🔗 Step 3: Dependency Management

```
Flow of control:  Controller → Interactor → Presenter → View
Direction of deps: all point INWARD toward higher-level policy
```

- Open arrows (using) = flow of control direction  
- Closed arrows (inheritance) = point against flow of control (OCP)

---

## 📦 Deployment Flexibility

The component structure allows flexible deployment:

```
Option A: One jar per actor group (6 jars)
Option B: 5 jars — views, presenters, interactors, controllers, utilities
Option C: 2 jars — UI + everything else
Option D: Monolith
Option E: Microservices
```

The architecture supports **all of them** without restructuring code.

---

## 💡 Key Takeaways

- Start with actors and use cases, not technology choices
- Each actor = a separate axis of change = separate component grouping
- SRP and Dependency Rule together create a system that naturally separates concerns
- Good architecture keeps deployment options open — you choose based on operational needs
- Components become the unit of independent deployability

---

*← [Back to Clean Architecture](../README.md)*
