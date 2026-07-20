# Chapter 4 — Isolating the Domain

> *"Isolating the domain implementation is a prerequisite for domain-driven design."*

---

## 🎯 Core Concept

Domain logic is the most valuable part of your software — it encodes the knowledge that makes your product work. But it's typically a small fraction of the total codebase, buried under UI code, database code, and infrastructure concerns. To apply DDD, you must **isolate the domain** so it can be developed and evolved independently.

---

## 🏗️ Layered Architecture

The standard solution is **Layered Architecture**: organize code into layers where each layer only depends on layers below it.

```
┌─────────────────────────────────────────┐
│           USER INTERFACE                │
│  (Presentation / Views / Controllers)   │
│  Shows info to users, interprets input  │
└───────────────────┬─────────────────────┘
                    │ depends on
┌───────────────────▼─────────────────────┐
│           APPLICATION LAYER             │
│  Coordinates tasks, delegates to domain │
│  No business rules here — thin!         │
└───────────────────┬─────────────────────┘
                    │ depends on
┌───────────────────▼─────────────────────┐
│  ★  DOMAIN LAYER  ★                     │
│  Business concepts, rules, state        │
│  The heart of the software              │
│  ENTITIES, VALUE OBJECTS, SERVICES      │
└───────────────────┬─────────────────────┘
                    │ depends on
┌───────────────────▼─────────────────────┐
│         INFRASTRUCTURE LAYER            │
│  Database, messaging, email, file I/O   │
│  Technical capabilities for all layers  │
└─────────────────────────────────────────┘
```

**The critical rule:** Each layer depends only on layers below it. Domain layer knows nothing about UI or infrastructure.

---

## 💰 Banking Example: Funds Transfer

What belongs where in a funds transfer feature?

| Layer | Responsibility |
|-------|---------------|
| **UI** | Render the form, capture account numbers and amount |
| **Application** | Receive the request, coordinate the transaction, notify user |
| **Domain** | Enforce "every credit has a matching debit" rule; update account balances |
| **Infrastructure** | Write to database, send email confirmation |

The business rule — "every credit has a matching debit" — lives in the **Domain Layer**. The Application Layer merely coordinates which domain objects to call.

---

## 🔑 Why Domain Isolation Matters

Without isolation, domain logic ends up **scattered**:
- Business rules embedded in UI event handlers
- Validation logic duplicated across multiple screens
- Database queries containing business logic
- No single place to look for "how does this business rule work?"

The result: changing a business rule means hunting through UI code, stored procedures, and application logic simultaneously. Testing is nearly impossible.

With isolation: the domain layer is **testable independently** of UI and database. Business rules change in one place. The model can evolve.

---

## ⚠️ The Smart UI Anti-Pattern

For simple CRUD applications — where the domain has almost no logic — there's a valid alternative: **Smart UI**. Put all business logic directly in the UI. Use a relational database as the shared store. Build with 4GL-style tools.

```
SMART UI:
  ┌──────────────────────────────┐
  │   UI + Business Logic        │
  │   (everything in one place)  │
  └──────────────┬───────────────┘
                 │
  ┌──────────────▼───────────────┐
  │   Relational Database        │
  └──────────────────────────────┘
```

**When Smart UI is legitimate:**
- Simple applications dominated by data entry/display
- Team lacks object-modeling experience
- Short time lines with modest expectations
- Business logic is truly minimal

**When Smart UI is dangerous:**
- Complex domain with real business rules
- Team wants to grow or evolve the application
- Domain concepts need to be reused

> **Warning:** Smart UI and layered architecture are mutually exclusive choices. You cannot gradually migrate from Smart UI to Model-Driven Design — you must rebuild.

---

## 🧩 Relating the Layers

Layers must communicate without breaking isolation:

- **UI → Application:** Direct calls (MVC pattern, application facade)
- **Application → Domain:** Direct calls to domain objects and services
- **Domain → Infrastructure:** Abstract interfaces (ports) — domain defines the interface, infrastructure implements it
- **Infrastructure → Domain:** Events or callbacks only — infrastructure should not call domain directly

```
Domain defines:  interface AccountRepository { Account find(String id); }
Infrastructure:  class SqlAccountRepository implements AccountRepository { ... }
```

The domain never imports from infrastructure. Infrastructure imports from domain.

---

## 💡 Key Takeaways

| Insight | Implication |
|---------|-------------|
| Domain logic is precious but small | Protect it by isolating it in its own layer |
| Layered Architecture is the standard solution | UI → Application → Domain → Infrastructure |
| Domain layer knows nothing about UI or DB | No import statements to frameworks in domain classes |
| Smart UI is a valid alternative for simple apps | But it's a dead end for complex domains |
| Smart UI and MDD are mutually exclusive | Choose early — migration is a full rebuild |

---

*← [Back to Domain-Driven Design](../README.md)*
