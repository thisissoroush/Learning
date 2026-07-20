# Chapters 15–17 — Distillation, Large-Scale Structure & Bringing Strategy Together

---

# Chapter 15 — Distillation

> *"The most important concepts in the domain must be distilled from the clutter, elevated to a high visibility status, and protected from dilution."*

## 🎯 Core Concept

Not all parts of a domain are equally important. **Distillation** is the process of separating the essential from the generic — finding what makes your domain unique and protecting it from the noise of everything else.

---

## ⭐ CORE DOMAIN

The **Core Domain** is the part of the model that makes your business distinctive and valuable. It's where you should invest your best developers and deepest thinking.

```
E-Commerce Company Domain Map:

┌─────────────────────────────────────────────────┐
│  Core Domain: RECOMMENDATION ENGINE              │
│  → This is the unique competitive advantage      │
│  → Best developers, deepest models here          │
└─────────────────────────────────────────────────┘

┌──────────────────────┐  ┌──────────────────────┐
│  Generic Subdomain   │  │  Generic Subdomain   │
│  PAYMENT PROCESSING  │  │  EMAIL NOTIFICATIONS │
│  → Buy or outsource  │  │  → Use a library     │
└──────────────────────┘  └──────────────────────┘

┌──────────────────────┐
│  Supporting Domain   │
│  PRODUCT CATALOG     │
│  → Custom but not    │
│    your advantage    │
└──────────────────────┘
```

**Questions to identify your Core Domain:**
- What would make this software worthless if done badly?
- What can't you buy off the shelf?
- Where is the deep domain expertise concentrated?

---

## 🔧 GENERIC SUBDOMAINS

Parts of the domain that are necessary but not distinctive. They solve general problems that many businesses face.

```
Generic Subdomains:
  ✓ Authentication & authorization
  ✓ Payment processing
  ✓ Email/notification delivery
  ✓ Tax calculation
  ✓ Currency conversion
  ✓ Logging and monitoring

Strategy: Buy, outsource, or use open-source for these.
Don't build them as if they're your core domain.
```

**The key insight:** Building a generic subdomain as if it were your core domain is a waste of your best resources. The goal is to minimize what you custom-build in these areas.

---

## 📄 DOMAIN VISION STATEMENT

A short document (one page) that describes the Core Domain — what it is, what makes it distinctive, and what value it provides.

```
Domain Vision Statement Template:

[Your system] will [primary purpose].
Unlike [alternative approaches], it will [key differentiator].
The Core Domain focuses on [core concepts], which provides [business value].
[Supporting subdomains] enable this but are not themselves the competitive advantage.
```

This statement helps the team:
- Prioritize development effort
- Communicate the core value to new team members
- Make decisions about what to build vs. buy

---

## 🎯 HIGHLIGHTED CORE

Mark the core domain elements clearly in the codebase — through naming conventions, package structure, or explicit documentation. Make it impossible for a developer to miss what matters most.

```
Package structure signaling Core:

com.company.core/          ← Core Domain (star treatment)
  recommendation/
  pricing/
  
com.company.support/       ← Supporting Domain (solid work)
  catalog/
  inventory/
  
com.company.generic/       ← Generic Subdomains (buy/outsource)
  payment/
  email/
```

---

## 🔩 COHESIVE MECHANISMS

Sometimes a part of the domain has a formalized procedure or algorithm that's complex but well-understood. Extract it as a **Cohesive Mechanism** — a separate module with a narrow, intention-revealing interface that hides the complexity.

```java
// Complex routing algorithm → extract as Cohesive Mechanism
interface RouteCalculator {
    Route findOptimalRoute(Location from, Location to, Constraints constraints);
}

// The implementation can be very complex (graph algorithms, etc.)
// but the interface is simple and focused
```

---

## 💡 Key Takeaways — Chapter 15

| Concept | Action |
|---------|--------|
| Core Domain | Identify it, protect it, invest in it |
| Generic Subdomains | Buy or use existing solutions |
| Domain Vision Statement | Write it, keep it visible |
| Highlighted Core | Make core elements visually obvious in code |
| Cohesive Mechanisms | Extract complex algorithms behind simple interfaces |

---

# Chapter 16 — Large-Scale Structure

> *"A large system needs some organizing principle beyond what models and bounded contexts provide—some way for people to understand the system as a whole."*

## 🎯 Core Concept

Even with well-designed Bounded Contexts, large systems need **large-scale structure** — high-level patterns that let developers understand how the whole system fits together without knowing every detail.

---

## 🔄 EVOLVING ORDER

Large-scale structure should **emerge** from the system, not be imposed from above by architects who haven't built it yet. Start with minimal structure, let it grow naturally, and refactor the structure as you learn.

```
Wrong approach: architect designs complete layering scheme upfront
→ Teams must fit into structure they didn't design
→ Structure doesn't fit actual domain needs

Right approach: structure emerges from development
→ Teams identify patterns that repeat across contexts
→ Structure is formalized only when clearly useful
```

---

## 🏗️ SYSTEM METAPHOR

A vivid metaphor that captures the essence of the system's design. When the metaphor is apt, it guides design decisions intuitively.

```
Example: "Our system is like an assembly line"
→ Each stage transforms the product
→ Items flow in one direction
→ Each station has a specific responsibility
→ Inspection gates check quality before passing forward

This metaphor guides: naming, sequencing, dependencies, error handling
```

The metaphor works when it's **naturally shared** by the team — not forced. If you need to explain why the metaphor applies, it's not working.

---

## 📚 RESPONSIBILITY LAYERS

Partition the system into layers that correspond to different **levels of abstraction** in the domain. Each layer has a clear responsibility, and higher layers build on lower ones.

```
Example — Banking System Layers:

┌─────────────────────────────────────────┐
│  DECISION LAYER                         │
│  Credit decisions, risk assessment      │
│  (uses all layers below)               │
├─────────────────────────────────────────┤
│  POLICY LAYER                           │
│  Business rules, regulatory compliance  │
├─────────────────────────────────────────┤
│  OPERATIONAL LAYER                      │
│  Transactions, accounts, balances       │
├─────────────────────────────────────────┤
│  POTENTIAL LAYER                        │
│  Customers, products, agreements        │
└─────────────────────────────────────────┘
```

Each layer:
- Has a clear name that communicates its purpose
- Contains cohesive domain concepts
- References layers below, not above
- Gives developers a framework for placing new concepts

---

## 🔌 PLUGGABLE COMPONENT FRAMEWORK

When many interchangeable components need to work together without tight coupling, define an abstract framework they all plug into.

```
Example: Data Processing Pipeline

Interface: DataTransformer
  - transform(DataSet input): DataSet

Multiple pluggable implementations:
  - FilterTransformer
  - AggregationTransformer  
  - EnrichmentTransformer
  - ValidationTransformer

Pipeline assembles them dynamically — components don't know about each other.
```

---

## 💡 Key Takeaways — Chapter 16

```
LARGE-SCALE STRUCTURE principles:

  Minimize: Don't add structure until it's clearly needed
  Evolve: Let structure emerge from actual development experience
  Communicate: The structure must help people understand the system
  Restrain: Too rigid structure is worse than none
```

---

# Chapter 17 — Bringing the Strategy Together

> *"Strategic design is about making choices that enable a large system or large organization to maintain the integrity of its models."*

## 🎯 Core Concept

Strategic design brings together Bounded Contexts, Distillation, and Large-Scale Structure. This chapter shows how they interact and provides guidance for making strategic decisions as a team.

---

## 🔗 How the Three Strategies Interact

```
DISTILLATION identifies the Core Domain
      │
      ▼
BOUNDED CONTEXTS protect each model's integrity
      │
      ▼
LARGE-SCALE STRUCTURE gives the whole system coherence

All three work together:
  • The Core Domain may span one or more Bounded Contexts
  • The Context Map shows how Bounded Contexts relate
  • Large-Scale Structure (like Responsibility Layers) may span Contexts
```

---

## 👥 Who Sets the Strategy?

Strategic design decisions shouldn't come from a top-down architecture team disconnected from development. They should come from **leaders who are close to the code**.

```
Productive patterns:
  ✓ Senior developers who work in the system make structural decisions
  ✓ Architecture team facilitates discussion, doesn't mandate
  ✓ Strategy emerges from application development experience
  ✓ Small teams working closely make better strategic decisions

Anti-patterns:
  ✗ Architecture team dictates structure without building
  ✗ "Master plan" designed upfront and handed down
  ✗ Strategic decisions made by people far from the code
```

---

## 🚀 Six Essentials for Strategic Design

1. **Decisions are made by people with understanding of the domain and technical realities**
2. **The strategy is a tool for the development teams**, not an end in itself
3. **Structure evolves** — commit to revisiting and changing it
4. **Minimalism** — the least structure that works
5. **Context Maps are maintained** — kept current as the system changes
6. **Core Domain gets the investment** — best people, deepest models

---

## ⚠️ Beware the Master Plan

The temptation is always to design the whole thing upfront — a grand architecture that everything fits into. This always fails for the same reasons:

```
Why master plans fail:
  → Understanding of the domain changes as you build it
  → Technical constraints aren't known until you encounter them
  → The system reveals its own best structure over time
  → Structure imposed from outside doesn't fit the team's mental model

What works instead:
  → Identify the Core Domain early and protect it
  → Let context boundaries emerge from natural seams
  → Refine structure continuously based on experience
  → Keep structure minimal — add only what provides clear value
```

---

## 💡 Final Key Takeaways — Chapter 17

| Strategy | Purpose | Anti-pattern |
|----------|---------|-------------|
| Bounded Contexts | Protect model integrity | Trying to unify everything into one model |
| Distillation | Focus effort on what matters | Treating all code as equally important |
| Large-Scale Structure | Help people understand the whole | Imposing structure before you understand the domain |
| Evolving Order | Keep structure honest | Rigid upfront architecture |

```
THE STRATEGIC DDD MINDSET:

  "What is the heart of this software?"
       → Find the Core Domain
  
  "Where are the natural boundaries?"
       → Define Bounded Contexts
  
  "How do parts relate?"
       → Build the Context Map
  
  "What high-level pattern makes the system coherent?"
       → Identify or evolve Large-Scale Structure
  
  "Is our structure still serving us?"
       → Continuously refine
```

---

*← [Back to Domain-Driven Design](../README.md)*
