# Key Takeaways — Clean Architecture

> *Robert C. Martin (Uncle Bob) — 2018*

---

## 🏆 The One Sentence

> **The goal of software architecture is to minimize the human resources required to build and maintain the required system.**

---

## 🧱 Part I — Introduction

### 1. Design and Architecture Are the Same Thing
- There is **no difference** between design and architecture — they form a continuous fabric from high-level structure down to low-level details
- Good design = **low and stable effort** over the lifetime of the system
- "The only way to go fast is to go well" — messy code is always slower, even in the short term

### 2. Behavior vs. Structure
- Software has **two values**: behavior (urgent) and structure (important)
- A program that **works but can't change** will eventually become useless
- A program that **doesn't work but is easy to change** can be fixed
- Developers must **fight for the architecture** — it's their professional responsibility

---

## 🧩 Part II — Programming Paradigms

### 3 Paradigms — What They Remove, Not Add

| Paradigm | Removes | Why It Matters |
|----------|---------|----------------|
| **Structured** | `goto` statements | Enables testable functional decomposition |
| **Object-Oriented** | Function pointers for polymorphism | Safe dependency inversion |
| **Functional** | Mutable variables / assignment | Eliminates race conditions |

- Each paradigm **restricts** something — together they cover function, component separation, and data management
- Software is composed of: **sequence, selection, iteration, and indirection** — nothing more

---

## 🔷 Part III — SOLID Principles

### SRP — Single Responsibility Principle
- A module should have **one and only one actor** (group of people) as its reason to change
- Violation symptom: accidental duplication, painful merges
- Fix: separate classes by actor; use Facade pattern to simplify access

### OCP — Open-Closed Principle
- Software should be **open for extension, closed for modification**
- Achieved by: separating things that change for different reasons (SRP) + ordering dependencies (DIP)
- Higher-level components are **most protected**; lower-level details depend on them

### LSP — Liskov Substitution Principle
- Subtypes must be **substitutable** for their base types without breaking the program
- LSP violations force ugly special-case `if` statements that pollute the architecture
- Applies beyond inheritance: REST services, interfaces, duck-typed languages

### ISP — Interface Segregation Principle
- **Don't depend on things you don't use**
- Depending on a module that carries unneeded baggage creates unnecessary coupling
- Especially critical at the architectural level — don't include frameworks that drag in dependencies

### DIP — Dependency Inversion Principle
- High-level policy should **not depend on low-level details** — details depend on policy
- Use **abstract interfaces** instead of concrete classes for volatile things
- Use **Abstract Factory** pattern to create concrete objects without depending on them
- The boundary between abstract and concrete is the architectural boundary

---

## 📦 Part IV — Component Principles

### Cohesion (what goes IN a component)

| Principle | Rule | Effect |
|-----------|------|--------|
| **REP** — Reuse/Release Equivalence | Group things that are released together | Components have a purpose |
| **CCP** — Common Closure | Group things that change together | Minimize impact of changes |
| **CRP** — Common Reuse | Don't force users to depend on unused things | Keep components lean |

- CCP and REP make components **larger** (inclusive)
- CRP makes components **smaller** (exclusive)
- Good architects balance the tension based on project maturity

### Coupling (how components connect)

- **ADP — Acyclic Dependencies**: No cycles in the component dependency graph — use DIP or a new intermediate component to break cycles
- **SDP — Stable Dependencies**: Depend in the direction of stability; volatile components shouldn't be depended on by stable ones
- **SAP — Stable Abstractions**: Stable components should be abstract; unstable components should be concrete
- **Main Sequence**: Plot components on the A/I graph — stay near the line connecting (0,1) and (1,0); avoid Zone of Pain and Zone of Uselessness

---

## 🏛️ Part V — Architecture

### What Architecture Is
- Architecture = the **shape** of a system: how it's divided into components, arranged, and made to communicate
- Primary purpose: **support the lifecycle** (development, deployment, operation, maintenance)
- Strategy: **leave as many options open as possible, for as long as possible**
- A good architect **maximizes the number of decisions not yet made**

### The Clean Architecture Layers

```
┌─────────────────────────────────────┐
│   Frameworks & Drivers (outermost)  │  ← Web, DB, UI
├─────────────────────────────────────┤
│      Interface Adapters             │  ← Controllers, Presenters, Gateways
├─────────────────────────────────────┤
│      Application Business Rules     │  ← Use Cases
├─────────────────────────────────────┤
│  Enterprise Business Rules (inner)  │  ← Entities
└─────────────────────────────────────┘
           ↑ Dependencies point INWARD only
```

### The Dependency Rule
> **Source code dependencies must point only inward, toward higher-level policies.**  
> Nothing in an inner circle can know anything about an outer circle.

### Boundaries
- Boundaries separate software elements — drawn where things **change at different rates or for different reasons**
- Boundary types: monolith (source-level), deployment components (JAR/DLL), local processes, services
- Draw boundaries between: Business Rules ↔ Database, Business Rules ↔ UI, Business Rules ↔ Frameworks

### Business Rules
- **Entities** = Critical Business Rules + Critical Business Data (independent of automation)
- **Use Cases** = application-specific rules that orchestrate entities (not entities themselves)
- Use cases should not know about the UI, database, or delivery mechanism
- Request/Response models should be **plain data structures** — not framework types

### Key Architectural Insights
- **Screaming Architecture**: Your folder structure should scream "Health Care System" not "Rails"
- **Frameworks are tools**, not ways of life — keep them at arm's length
- **The database is a detail** — the data model matters; the DB technology does not
- **The web is a detail** — it's just an I/O device; decouple your business logic from it
- **Tests are system components** — follow the Dependency Rule; avoid the Fragile Tests Problem
- **The Main component** is the dirtiest, outermost plugin that bootstraps everything

### Services
- Services alone don't define architecture — boundaries and the Dependency Rule do
- Microservices are not automatically decoupled — shared data creates coupling
- Services should have **internal component architectures** following the Dependency Rule
- Cross-cutting concerns can break functional service decomposition (Kitty Problem)

---

## 🔧 Part VI — Details

| Detail | Rule |
|--------|------|
| Database | Treat as a plugin — put behind an interface |
| Web | Just an I/O device — decouple business rules |
| Frameworks | "Date them before you marry them" — never couple core to framework |
| Embedded | Use HAL (Hardware Abstraction Layer) + OSAL — make software testable off-target |

---

## 💡 Top 10 Principles to Remember

1. **The only way to go fast is to go well** — clean code is never slower
2. **Architecture = minimize human resources** over the system's lifetime
3. **Dependency Rule**: source code always points inward toward higher-level policy
4. **Separate what changes for different reasons** — SRP at every level
5. **Depend on abstractions, not concretions** — DIP everywhere
6. **Leave options open** — defer decisions about DB, framework, delivery mechanism
7. **No cycles** in component dependency graphs — they make everything harder
8. **Stable things should be abstract; unstable things should be concrete** — SAP
9. **Use tests as a first-class system component** — design for testability
10. **The compiler is your best architecture enforcer** — use access modifiers

---

## 📐 Visual: The Main Sequence

```
A (Abstractness)
1 │ (0,1) Zone of Uselessness
  │  \
  │   \  ← Main Sequence (good zone)
  │    \
  │     \
0 │──────\──── (1,0) Zone of Pain
  0       1   I (Instability)

D = |A + I - 1|  → should be close to 0
```

---

*"If you think good architecture is expensive, try bad architecture."*  
— Brian Foote and Joseph Yoder
