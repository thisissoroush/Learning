# Architecture Patterns with Python

> **Authors:** Harry Percival & Bob Gregory  
> **Publisher:** O'Reilly Media, 2020  
> **Category:** Software Architecture / TDD / DDD / Python

---

## 📖 About This Book

*Architecture Patterns with Python* is the definitive guide to building maintainable, testable Python applications using **domain-driven design (DDD), test-driven development (TDD), and event-driven architecture**. The book walks through a complete furniture allocation system, demonstrating how to structure code so that business logic stays **pure, decoupled, and infinitely testable**.

The core thesis: **behavior should come first, and drive storage requirements.** Not the other way around.

---

## 📚 Chapters

| # | Chapter | Core Concepts | Key Pattern |
|---|---------|--------------|------------|
| [00](chapters/00-introduction.md) | Introduction | Design failures, DIP, layering, domain model | Dependency Inversion |
| [01](chapters/01-domain-modeling.md) | Domain Modeling | Entity, Value Object, Domain Service | TDD first, behavior-driven |
| [02](chapters/02-repository-pattern.md) | Repository Pattern | Abstraction over persistence, inverting ORM | Ports & Adapters |
| [03](chapters/03-coupling-and-abstractions.md) | Coupling & Abstractions | Choosing abstractions, testability | Edge-to-edge testing |
| [04](chapters/04-service-layer.md) | Flask API & Service Layer | Use cases, thin adapters, DIP in action | Clear API boundary |
| [05](chapters/05-tdd-high-low-gear.md) | TDD in High/Low Gear | Test pyramid, shifting tests, E2E minimization | Unit vs integration tests |
| [06](chapters/06-unit-of-work.md) | Unit of Work Pattern | Atomic operations, context manager, SQLAlchemy | Transaction boundaries |
| [07](chapters/07-aggregates.md) | Aggregates & Consistency | Consistency boundaries, optimistic locking | Version numbers |
| [08](chapters/08-events-and-message-bus.md) | Events & Message Bus | Domain events, pub/sub, event handlers | UoW publishes events |
| [09](chapters/09-going-to-town-on-message-bus.md) | Going to Town on Message Bus | Event handlers as primary flow, event chains | Event-driven usefulness |
| [10](chapters/10-commands-and-command-handler.md) | Commands & Command Handler | Commands vs Events, exception handling | Command = intent |
| [11](chapters/11-event-driven-microservices.md) | Event-Driven Architecture | Redis pub/sub, external events, integration | Temporal decoupling |
| [12](chapters/12-cqrs.md) | CQRS | Read model vs write model, denormalization | Separate read/write paths |
| [13](chapters/13-dependency-injection.md) | Dependency Injection & Bootstrap | Explicit DI, bootstrap script, wiring | DI pattern conclusion |

---

## ⚡ Core Concepts at a Glance

### The Three-Layered Architecture (Inverted)

```
┌─────────────────────────────────────────┐
│  ADAPTERS (Flask, Django, CLI, HTTP)    │  Input/Output
├─────────────────────────────────────────┤
│  SERVICE LAYER (Use Cases)              │  Pure business logic
├─────────────────────────────────────────┤
│  DOMAIN MODEL (Entities, Values, Agg)   │  Core logic
├─────────────────────────────────────────┤
│  REPOSITORIES (Abstract & Concrete)     │  Abstraction layer
├─────────────────────────────────────────┤
│  ORM / Storage (SQLAlchemy, Postgres)   │  Low-level details
└─────────────────────────────────────────┘

KEY: Business logic is ISOLATED in the middle.
     It depends on abstractions (Repos), not on the database.
```

---

## 🎯 Key Takeaways

→ [View all key takeaways](key-takeaways.md)

**The 5 most important lessons:**

1. **Domain Model First** — Model the business, not the database.
2. **Dependency Inversion** — Both depend on abstractions, not the other way around.
3. **Repository Pattern** — Abstract persistence completely; use fakes for testing.
4. **Service Layer** — Define clear use case boundaries.
5. **Events & Message Bus** — Decouple with domain events.

---

## 🖼️ Architecture Diagrams

| Diagram | Concept |
|---------|---------|
| ![Overview](images/00-architecture-overview.png) | Full system layered architecture |
| ![Domain](images/01-domain-model.png) | Entity vs Value Object structure |
| ![Repository](images/02-repository-pattern.png) | Inverted dependency: ORM on Domain |
| ![Service](images/04-service-layer.png) | Request → Service → Domain → Repo |
| ![UoW](images/06-unit-of-work.png) | Context manager & transaction lifecycle |
| ![Aggregate](images/07-aggregates.png) | Consistency boundary & version numbers |
| ![Events](images/08-events-message-bus.png) | Event flow: raise → collect → publish |
| ![Microservices](images/11-event-driven-microservices.png) | Redis pub/sub integration |
| ![CQRS](images/12-cqrs.png) | Read model vs write model |

---

*← [Back to Python](../README.md)*
