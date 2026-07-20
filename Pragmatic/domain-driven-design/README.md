# Domain-Driven Design: Tackling Complexity in the Heart of Software

> **Author:** Eric Evans  
> **Year:** 2003  
> **Category:** Software Design / Domain Modeling

---

## 📖 About This Book

Domain-Driven Design (DDD) is the foundational text for building complex software that actually reflects the business it serves. Eric Evans argues that the primary challenge in software development is not technical — it's understanding the domain deeply enough to model it well.

The book introduces a philosophy, a vocabulary, and a set of patterns that connect domain experts, developers, and the code itself into a unified whole. It's not about a specific language or framework; it's about **how you think** about software.

> *"The heart of software is its ability to solve domain-related problems for its user."*

---

## 🗺️ Book Structure

### Part I — Putting the Domain Model to Work

| Chapter | Topic |
|---------|-------|
| [01](chapters/01-crunching-knowledge.md) | Crunching Knowledge |
| [02](chapters/02-communication-and-language.md) | Communication and the Use of Language |
| [03](chapters/03-binding-model-and-implementation.md) | Binding Model and Implementation |

### Part II — The Building Blocks of a Model-Driven Design

| Chapter | Topic |
|---------|-------|
| [04](chapters/04-isolating-the-domain.md) | Isolating the Domain |
| [05](chapters/05-a-model-expressed-in-software.md) | A Model Expressed in Software |
| [06](chapters/06-the-life-cycle-of-a-domain-object.md) | The Life Cycle of a Domain Object |
| [07](chapters/07-using-the-language-extended-example.md) | Using the Language: An Extended Example |

### Part III — Refactoring Toward Deeper Insight

| Chapter | Topic |
|---------|-------|
| [08](chapters/08-breakthrough.md) | Breakthrough |
| [09](chapters/09-making-implicit-concepts-explicit.md) | Making Implicit Concepts Explicit |
| [10](chapters/10-supple-design.md) | Supple Design |
| [11](chapters/11-applying-analysis-patterns.md) | Applying Analysis Patterns |
| [12](chapters/12-relating-design-patterns-to-the-model.md) | Relating Design Patterns to the Model |
| [13](chapters/13-refactoring-toward-deeper-insight.md) | Refactoring Toward Deeper Insight |

### Part IV — Strategic Design

| Chapter | Topic |
|---------|-------|
| [14](chapters/14-maintaining-model-integrity.md) | Maintaining Model Integrity |
| [15](chapters/15-distillation.md) | Distillation |
| [16](chapters/16-large-scale-structure.md) | Large-Scale Structure |
| [17](chapters/17-bringing-the-strategy-together.md) | Bringing the Strategy Together |

---

## ⚡ The Core Patterns at a Glance

### Building Blocks (Tactical Patterns)

```
┌─────────────────────────────────────────────────────────────┐
│                    DOMAIN LAYER                             │
│                                                             │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │  ENTITY  │    │ VALUE OBJECT │    │    SERVICE       │  │
│  │          │    │              │    │                  │  │
│  │ Has ID   │    │ No identity  │    │ Stateless op     │  │
│  │ Mutable  │    │ Immutable    │    │ not natural to   │  │
│  │ Tracked  │    │ Replaceable  │    │ Entity/Value     │  │
│  └──────────┘    └──────────────┘    └──────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    AGGREGATE                         │  │
│  │  ┌──────────┐                                        │  │
│  │  │   Root   │ ← only entry point from outside        │  │
│  │  │  Entity  │                                        │  │
│  │  └──────────┘                                        │  │
│  │       │── Internal Entity                            │  │
│  │       └── Value Object                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │ FACTORY  │    │  REPOSITORY  │    │    MODULE        │  │
│  │          │    │              │    │                  │  │
│  │ Creates  │    │ Finds/stores │    │ Groups related   │  │
│  │ complex  │    │ aggregates   │    │ concepts         │  │
│  │ objects  │    │ by query     │    │ high cohesion    │  │
│  └──────────┘    └──────────────┘    └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Strategic Patterns

```
┌──────────────────────────────────────────────────────────────┐
│                    STRATEGIC DESIGN                          │
│                                                              │
│  ┌─────────────────┐      ┌──────────────────────────────┐  │
│  │  BOUNDED        │      │       CONTEXT MAP            │  │
│  │  CONTEXT        │      │                              │  │
│  │                 │ ──── │  Shows relationships between  │  │
│  │  Clear model    │      │  contexts:                   │  │
│  │  boundary       │      │  · Shared Kernel             │  │
│  │  single team    │      │  · Customer/Supplier         │  │
│  └─────────────────┘      │  · Conformist                │  │
│                           │  · Anti-Corruption Layer     │  │
│  ┌─────────────────┐      │  · Separate Ways             │  │
│  │  CORE DOMAIN    │      │  · Open Host Service         │  │
│  │                 │      │  · Published Language        │  │
│  │  The part that  │      └──────────────────────────────┘  │
│  │  differentiates │                                        │
│  │  your product   │      ┌──────────────────────────────┐  │
│  └─────────────────┘      │  LARGE-SCALE STRUCTURE       │  │
│                           │  · System Metaphor           │  │
│  ┌─────────────────┐      │  · Responsibility Layers     │  │
│  │  GENERIC        │      │  · Knowledge Level           │  │
│  │  SUBDOMAIN      │      │  · Pluggable Components      │  │
│  │                 │      └──────────────────────────────┘  │
│  │  Necessary but  │                                        │
│  │  not your edge  │                                        │
│  └─────────────────┘                                        │
└──────────────────────────────────────────────────────────────┘
```

### The Ubiquitous Language Bridge

```
Domain Experts  ←─────────────────────────────→  Developers
       │                                                │
       │         UBIQUITOUS LANGUAGE                   │
       │    (shared vocabulary from the model)          │
       │                                                │
       └──────────────── CODE ──────────────────────────┘
                  (model lives here too)
```

---

## 🎯 Key Takeaways

See the full distilled summary → **[key-takeaways.md](key-takeaways.md)**

---

## 💬 Memorable Quotes

> *"The heart of software is its ability to solve domain-related problems for its user."*

> *"It is not just the knowledge in a domain expert's head; it is a rigorously organized and selective abstraction of that knowledge."*

> *"Domain modeling is not a matter of making as 'realistic' a model as possible."*

> *"Design a portion of the software system to reflect the domain model in a very literal way, so that mapping is obvious."*

> *"A change in the Ubiquitous Language is a change to the model."*

> *"If the design, or some central part of it, does not map to the domain model, that model is of little value."*

---

*← [Back to Pragmatic](../README.md)*
