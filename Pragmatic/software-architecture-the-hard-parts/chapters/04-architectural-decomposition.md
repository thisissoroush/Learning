# Chapter 4 — Architectural Decomposition

> *"How do you eat an elephant? One bite at a time."* — but doing so randomly leads to the Elephant Migration Anti-Pattern.

---

## 🎯 Core Concept

Once you decide *why* to break apart a monolith (Chapter 3), you need to decide *how*. Two main approaches exist: **component-based decomposition** (structured, incremental) and **tactical forking** (pragmatic, deletion-based). The choice depends on how well-structured the existing codebase is.

**Critical first step:** Determine if the codebase is even decomposable.

---

## 🔍 Is the Codebase Decomposable?

### The Big Ball of Mud Anti-Pattern

A codebase with no internal structure — event handlers wired directly to database calls, no namespaces, no modularity — is a **Big Ball of Mud**. It may not be worth decomposing; it may need a full rewrite.

### Coupling Metrics to Assess Decomposability

**Afferent (Ca) and Efferent (Ce) Coupling:**

```
Afferent Coupling (Ca)              Efferent Coupling (Ce)
─────────────────────               ──────────────────────
Incoming connections                Outgoing connections
"Who depends on me?"                "Who do I depend on?"

High Ca = widely used component     High Ce = fragile, volatile component
Hard to change without impact       Breaks when dependencies change
```

**Abstractness (A):**
```
A = (sum of abstract elements) / (sum of abstract + concrete elements)
```
- Near 0 → all concrete implementation, hard to understand
- Near 1 → all abstract, easy to understand but nothing does anything

**Instability (I):**
```
I = Ce / (Ce + Ca)
```
- Near 0 → stable (many dependents, few dependencies)
- Near 1 → unstable (few dependents, many dependencies — breaks easily)

### Distance from the Main Sequence

```
D = |A + I - 1|

         A (Abstractness)
         1 ┤
           │  Zone of         ╲
           │  Uselessness      ╲  Main Sequence
           │  (too abstract)    ╲  (ideal zone)
         0 ├───────────────────────────────── I (Instability)
           0                                  1
                          Zone of Pain
                          (too concrete, rigid)
```

**Decision rule:** If many components fall in the "Zone of Pain" (low A, low I) — they're rigid and tightly coupled. Decomposing them is risky. Consider tactical forking or rewrite instead.

---

## 🌳 Decision Tree: Which Approach?

```
Is the codebase decomposable?
        │
        ├─ NO → Consider rewrite
        │
        └─ YES
               │
               Is source code structured with clear component boundaries?
               │
               ├─ NO → Tactical Forking
               │
               └─ YES → Component-Based Decomposition
```

---

## 🔨 Approach 1: Component-Based Decomposition

**Core idea:** Incrementally refactor the codebase, moving components into well-defined domains, then extract those domains into separate services.

This approach produces a **service-based architecture** as a stepping stone (or final destination) to microservices.

### Why Service-Based Architecture First?

```
Migration Path
──────────────
Monolith → Service-Based Architecture → Microservices (if needed)

Advantages of the intermediate step:
  ✓ No database decomposition required yet
  ✓ No containerization required
  ✓ No operational automation required
  ✓ Technical migration only (no business/org changes needed)
  ✓ Learn domain boundaries before committing to fine-grained services
```

### Build Services from Components, Not Individual Classes

```
WRONG approach:
  class OrderService
  class OrderRepository     } → directly become microservices
  class OrderValidator

RIGHT approach:
  ss.order.*  (entire package/namespace) → becomes Order Service
```

---

## 🍴 Approach 2: Tactical Forking

**Core idea:** Clone the entire monolith, give each team a copy, and have them *delete* what they don't need. Inspired by sculptors: "remove the marble that isn't supposed to be there."

### Why Deletion Is Easier Than Extraction

```
Extraction (hard):
  Monolith → Try to pull out Order module
  → Discover Order depends on Customer
  → Customer depends on Billing
  → Billing depends on Order
  → Cyclic dependency! Stuck.

Deletion (easier):
  Clone monolith → Delete Survey code → compile → Survey gone!
  Remaining dependencies still work (just less of them)
```

### Tactical Forking Process

```
Step 1: Clone the monolith for each desired service
┌─────────────────┐     ┌─────────────────┐
│   Full Clone    │     │   Full Clone    │
│  (for Team A)   │     │  (for Team B)   │
└─────────────────┘     └─────────────────┘

Step 2: Each team deletes what they don't need
┌─────────────────┐     ┌─────────────────┐
│ Hexagon+Square  │     │     Circle      │
│ Domain code     │     │   Domain code   │
│ (rest deleted)  │     │  (rest deleted) │
└─────────────────┘     └─────────────────┘

Step 3: Two coarse-grained services emerge
```

### Trade-Offs

| | Component-Based | Tactical Forking |
|---|---|---|
| **Best for** | Structured codebase | Big Ball of Mud |
| **Speed** | Slower (methodical) | Faster (start immediately) |
| **Code quality** | Better (refactoring) | Lower (just less code) |
| **Shared code** | Handled explicitly | Duplicated across forks |
| **Analysis needed** | Yes, upfront | Minimal |
| **Result** | Clean services | Coarse-grained services with leftover code |

---

## 🏢 Sysops Squad Saga: Choosing an Approach

After analyzing metrics, Addison found that:
- Most components lie along the main sequence (decomposable ✓)
- Code is structured with well-defined component boundaries (component-based ✓)
- Significant shared infrastructure code (logging, security, DB calls)

**Decision: Component-Based Decomposition**

```
ADR: Migration Using Component-Based Decomposition

Rejected: Tactical Forking
  - Would require defining service boundaries upfront
  - Would create duplicate code across forked apps
  - Shared functionality nightmare

Chosen: Component-Based Decomposition
  - Well-defined component boundaries already exist
  - Reduces duplication risk
  - Service boundaries emerge naturally from component grouping
  - Safer, more controlled incremental migration
  
Consequences:
  - Will take longer than tactical forking
  - Teams work collaboratively to identify boundaries
```

---

## 💡 Key Takeaways

| Insight | Implication |
|---------|-------------|
| "Eat the elephant one bite at a time" alone = Elephant Migration Anti-Pattern | Random decomposition leads to distributed monolith, not microservices |
| Assess decomposability *before* committing to an approach | Use coupling metrics (Ca, Ce, A, I, D) to understand the codebase |
| Component-based decomposition = structured, incremental | Best when code already has some organization |
| Tactical forking = pragmatic, deletion-based | Best for chaotic codebases with no clear structure |
| Service-based architecture is a valid stepping stone | Don't jump straight to microservices — learn domain boundaries first |

---

*← [Back to Software Architecture: The Hard Parts](../README.md)*
