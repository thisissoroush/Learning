# Clean Architecture: A Craftsman's Guide to Software Structure and Design

> **Author:** Robert C. Martin (Uncle Bob)  
> **Year:** 2018  
> **Category:** Software Architecture / Design Principles

---

## 📖 About This Book

Clean Architecture distills 50+ years of software engineering wisdom into timeless, language-agnostic principles for structuring software systems. Uncle Bob argues that the rules of software architecture haven't changed since Alan Turing wrote the first machine code — only our understanding of them has improved.

The central goal: **minimize the human resources required to build and maintain a system**. Good architecture keeps software soft — easy to change, extend, and understand throughout its entire lifetime.

---

## 🗺️ Book Structure

### Part I — Introduction
| Chapter | Topic |
|---------|-------|
| [01](chapters/01-what-is-design-and-architecture.md) | What Is Design and Architecture? |
| [02](chapters/02-a-tale-of-two-values.md) | A Tale of Two Values |

### Part II — Programming Paradigms
| Chapter | Topic |
|---------|-------|
| [03](chapters/03-paradigm-overview.md) | Paradigm Overview |
| [04](chapters/04-structured-programming.md) | Structured Programming |
| [05](chapters/05-object-oriented-programming.md) | Object-Oriented Programming |
| [06](chapters/06-functional-programming.md) | Functional Programming |

### Part III — Design Principles (SOLID)
| Chapter | Topic |
|---------|-------|
| [07](chapters/07-srp-single-responsibility-principle.md) | SRP: The Single Responsibility Principle |
| [08](chapters/08-ocp-open-closed-principle.md) | OCP: The Open-Closed Principle |
| [09](chapters/09-lsp-liskov-substitution-principle.md) | LSP: The Liskov Substitution Principle |
| [10](chapters/10-isp-interface-segregation-principle.md) | ISP: The Interface Segregation Principle |
| [11](chapters/11-dip-dependency-inversion-principle.md) | DIP: The Dependency Inversion Principle |

### Part IV — Component Principles
| Chapter | Topic |
|---------|-------|
| [12](chapters/12-components.md) | Components |
| [13](chapters/13-component-cohesion.md) | Component Cohesion |
| [14](chapters/14-component-coupling.md) | Component Coupling |

### Part V — Architecture
| Chapter | Topic |
|---------|-------|
| [15](chapters/15-what-is-architecture.md) | What Is Architecture? |
| [16](chapters/16-independence.md) | Independence |
| [17](chapters/17-boundaries-drawing-lines.md) | Boundaries: Drawing Lines |
| [18](chapters/18-boundary-anatomy.md) | Boundary Anatomy |
| [19](chapters/19-policy-and-level.md) | Policy and Level |
| [20](chapters/20-business-rules.md) | Business Rules |
| [21](chapters/21-screaming-architecture.md) | Screaming Architecture |
| [22](chapters/22-the-clean-architecture.md) | The Clean Architecture |
| [23](chapters/23-presenters-and-humble-objects.md) | Presenters and Humble Objects |
| [24](chapters/24-partial-boundaries.md) | Partial Boundaries |
| [25](chapters/25-layers-and-boundaries.md) | Layers and Boundaries |
| [26](chapters/26-the-main-component.md) | The Main Component |
| [27](chapters/27-services-great-and-small.md) | Services: Great and Small |
| [28](chapters/28-the-test-boundary.md) | The Test Boundary |
| [29](chapters/29-clean-embedded-architecture.md) | Clean Embedded Architecture |

### Part VI — Details
| Chapter | Topic |
|---------|-------|
| [30](chapters/30-the-database-is-a-detail.md) | The Database Is a Detail |
| [31](chapters/31-the-web-is-a-detail.md) | The Web Is a Detail |
| [32](chapters/32-frameworks-are-details.md) | Frameworks Are Details |
| [33](chapters/33-case-study-video-sales.md) | Case Study: Video Sales |
| [34](chapters/34-the-missing-chapter.md) | The Missing Chapter |

---

## ⚡ Core Ideas at a Glance

### The Dependency Rule
```
         ┌──────────────────────────┐
         │  Frameworks & Drivers    │
         │  ┌────────────────────┐  │
         │  │ Interface Adapters │  │
         │  │  ┌─────────────┐  │  │
         │  │  │  Use Cases  │  │  │
         │  │  │  ┌───────┐  │  │  │
         │  │  │  │Entity │  │  │  │
         │  │  │  └───────┘  │  │  │
         │  │  └─────────────┘  │  │
         │  └────────────────────┘  │
         └──────────────────────────┘
              ← Dependencies point INWARD
```

### SOLID in One Line Each
- **SRP**: One actor, one reason to change
- **OCP**: Extend without modifying
- **LSP**: Subtypes must be substitutable
- **ISP**: Don't depend on what you don't use
- **DIP**: High-level policy never depends on low-level detail

### The Three Component Cohesion Principles
- **REP**: Release together → group together
- **CCP**: Change together → group together (SRP for components)
- **CRP**: Don't depend on what you don't need (ISP for components)

---

## 🎯 Key Takeaways

See the full summary → **[key-takeaways.md](key-takeaways.md)**

---

## 💬 Memorable Quotes

> *"The only way to go fast, is to go well."*

> *"A good architect maximizes the number of decisions not made."*

> *"If you think good architecture is expensive, try bad architecture."*

> *"Your architecture should tell readers about the system, not about the frameworks you used."*

> *"The database is a detail. The web is a detail. Frameworks are details."*

---

*← [Back to Pragmatic](../README.md)*
