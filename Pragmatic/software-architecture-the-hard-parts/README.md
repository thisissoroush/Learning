# Software Architecture: The Hard Parts

**Authors:** Neal Ford, Mark Richards, Pramod Sadalage & Zhamak Dehghani  
**Publisher:** O'Reilly Media, 2022  
**Focus:** Trade-off analysis for distributed architectures — microservices, data decomposition, sagas, contracts, and analytical data

---

## 📖 What This Book Is About

Most architecture books tell you the "best practice." This book is different: it openly admits there are **no best practices** in software architecture — only trade-offs in context. The authors collected the hardest problems they kept setting aside while writing other books and tackled each one through systematic trade-off analysis.

The book follows a fictional company called **Penultimate Electronics** and their Sysops Squad application — a monolithic ticketing system being migrated to a distributed architecture. Every concept is grounded in this real-world saga.

The central skill this book builds: **How to find the least worst combination of trade-offs** for any architectural decision you face.

---

## 🏗️ Book Structure

```
Part I: Pulling Things Apart
  Chapters 1–7: Understanding coupling, breaking apart monoliths, decomposing data

Part II: Putting Things Back Together  
  Chapters 8–15: Reuse, data ownership, distributed workflows, sagas, contracts, analytics
```

---

## 📚 Chapters

### Part I — Pulling Things Apart

| Chapter | Topic | Core Concept |
|---------|-------|-------------|
| [Ch. 1](chapters/01-no-best-practices.md) | No "Best Practices" | Trade-off analysis is the job; ADRs and fitness functions |
| [Ch. 2](chapters/02-discerning-coupling.md) | Discerning Coupling | Architecture quantum; static vs. dynamic coupling; 3D communication space |
| [Ch. 3](chapters/03-architectural-modularity.md) | Architectural Modularity | 5 drivers for breaking apart systems: maintainability, testability, deployability, scalability, fault tolerance |
| [Ch. 4](chapters/04-architectural-decomposition.md) | Architectural Decomposition | Component-based decomposition vs. tactical forking; abstractness/instability metrics |
| [Ch. 5](chapters/05-component-decomposition-patterns.md) | Component-Based Decomposition Patterns | 6 patterns: identify & size → gather common → flatten → dependencies → domains → domain services |
| [Ch. 6](chapters/06-pulling-apart-operational-data.md) | Pulling Apart Operational Data | Data disintegrators/integrators; 5-step data decomposition; 8 database types |
| [Ch. 7](chapters/07-service-granularity.md) | Service Granularity | 6 disintegrators + 4 integrators; finding equilibrium |

### Part II — Putting Things Back Together

| Chapter | Topic | Core Concept |
|---------|-------|-------------|
| [Ch. 8](chapters/08-reuse-patterns.md) | Reuse Patterns | Code replication → shared library → shared service → sidecar/service mesh |
| [Ch. 9](chapters/09-data-ownership-and-distributed-transactions.md) | Data Ownership & Distributed Transactions | Single/common/joint ownership; eventual consistency patterns |
| [Ch. 10](chapters/10-distributed-data-access.md) | Distributed Data Access | 4 patterns: interservice, column replication, replicated caching, data domain |
| [Ch. 11](chapters/11-managing-distributed-workflows.md) | Managing Distributed Workflows | Orchestration vs. choreography; state management |
| [Ch. 12](chapters/12-transactional-sagas.md) | Transactional Sagas | 8 saga patterns (sao through aec); compensating transactions; state machines |
| [Ch. 13](chapters/13-contracts.md) | Contracts | Strict vs. loose contracts; tolerant reader; stamp coupling |
| [Ch. 14](chapters/14-managing-analytical-data.md) | Managing Analytical Data | Data warehouse → data lake → data mesh; data product quantum |
| [Ch. 15](chapters/15-build-your-own-trade-off-analysis.md) | Build Your Own Trade-Off Analysis | MECE lists; out-of-context trap; the trade-off analysis template |

---

## 🔑 Key Concepts at a Glance

### Architecture Quantum
An independently deployable artifact with **high functional cohesion**, **high static coupling**, and **synchronous dynamic coupling**. Shared databases = shared quantum. This is the fundamental unit of analysis for distributed systems.

```
Monolith: 1 quantum (always)
Microservices with shared DB: 1 quantum (!)
Microservices with separate DBs: N quanta (true independence)
```

### The 3 Dimensions of Dynamic Coupling
```
Communication  × Consistency  × Coordination
─────────────    ───────────    ─────────────
Synchronous      Atomic         Orchestrated
Asynchronous     Eventual       Choreographed
```
These 3 dimensions × 2 choices each = **8 saga patterns**.

### Service Granularity Balance
```
Disintegrators          Integrators
(split the service)     (keep it together)
────────────────────    ──────────────────
Weak cohesion           ACID transactions needed
Volatile code areas     Too much inter-service calls
Scaling differences     Shared domain code
Fault isolation         Data relationships
Security boundaries
Extensibility expected
```

### The 8 Saga Patterns
| Pattern | Code | Best For |
|---------|------|---------|
| Epic Saga | `sao` | Simple strict workflows |
| Phone Tag | `sac` | Sequential strict chains |
| Fairy Tale | `seo` | Orchestrated + eventual |
| Time Travel | `sec` | Choreographed eventual |
| Fantasy Fiction | `aao` | Async + atomic (complex) |
| Horror Story | `aac` | Avoid |
| **Parallel Saga** | **`aeo`** | **Most practical** |
| Anthology Saga | `aec` | Most decoupled |

---

## 💡 Key Takeaways

→ [Full key-takeaways document](key-takeaways.md)

**Top 7 principles:**
1. There are no best practices — only trade-offs in context
2. Coupling is dosage — the amount determines if it's poison or medicine
3. Move to service-based architecture first, then microservices only where needed
4. Data decomposition is harder than code decomposition — plan carefully
5. Design compensating transactions before implementing forward paths
6. Parallel Saga (`aeo`) is the most practical saga pattern for most cases
7. The goal is the **least worst combination of trade-offs**, not the best solution

---

## 🔗 Related Books in This Repo

- [Microservices Patterns](../microservices-patterns/README.md) — Implementation patterns for microservices
- [Domain-Driven Design](../domain-driven-design/README.md) — Bounded contexts and domain modeling
- [Clean Architecture](../clean-architecture/README.md) — Component boundaries and dependency rules
