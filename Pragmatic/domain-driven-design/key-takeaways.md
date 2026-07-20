# Key Takeaways — Domain-Driven Design

> *by Eric Evans*

---

## 🌟 The Big Idea

Software complexity often lives in the **domain** — the business problem being solved — not the technology. DDD is a philosophy: put the domain model at the center of everything, and let it drive the design, the code, and the team's communication.

---

## 🏛️ Foundational Principles

### 1. The Model IS the Design
Don't have a separate analysis model and a design model. They become inconsistent. Have **one model** that drives both understanding and implementation.

```
❌ Analysis model (whiteboard) ≠ Design model (code)
✅ One model: expressed in code, talked about in meetings, refined by everyone
```

### 2. Ubiquitous Language is Non-Negotiable
Every team member — developers AND domain experts — must use the **exact same words** for the same concepts. When the language changes, the model changes. When the model changes, the code changes.

```
Same word = same concept everywhere:
  In conversations ✓
  In diagrams ✓  
  In code (class names, method names) ✓
  In tests ✓
  In documentation ✓
```

### 3. Knowledge Crunching is Collaborative
You cannot learn the domain by reading requirements documents. You must sit with domain experts, build prototypes, watch them react, and refine — repeatedly.

```
Waterfall: Business → Analyst → Developer (knowledge lost at each step)
DDD:       Business + Developer together → evolving shared model
```

---

## 🧱 Building Block Patterns

| Pattern | What It Is | When to Use |
|---------|-----------|-------------|
| **Entity** | Object with identity that persists | When "same instance" matters (Customer, Order) |
| **Value Object** | Immutable descriptor; no identity | When only the attributes matter (Money, Address) |
| **Service** | Stateless operation not owned by any object | Domain operation that spans multiple objects |
| **Aggregate** | Cluster of objects with one root | To enforce invariants and define consistency boundaries |
| **Factory** | Creates complex objects/aggregates | When construction logic is complex or needs encapsulation |
| **Repository** | In-memory illusion for persistent objects | Access to Aggregate roots; hides data storage details |
| **Module** | Named grouping of cohesive concepts | To tell the story of the domain at a coarser grain |

### The Aggregate Rule (Most Important Building Block)
```
One Aggregate = One consistency boundary

Rules:
  ✓ Only the Aggregate Root can be referenced from outside
  ✓ All invariants within the Aggregate enforced on every transaction
  ✓ Only Aggregate Roots get Repositories
  ✓ Keep Aggregates small — small == easier to keep consistent
```

---

## 🔍 Refactoring Toward Deeper Insight

### Make Implicit Concepts Explicit
Every time an expert uses a word you don't have in the model — that's a concept trying to surface.

```
Expert keeps saying "eligibility" → Add an Eligibility class/Specification
Guard clause repeated everywhere → Extract as named Constraint or Policy
```

### The Specification Pattern
```java
// Instead of duplicating rules:
if (customer.age > 18 && customer.creditScore > 700 && !customer.hasDefaults()) ...

// Make the rule explicit and reusable:
Specification<Customer> eligible = new LoanEligibilitySpec();
if (eligible.isSatisfiedBy(customer)) ...
```

### Supple Design — Make Code Inviting
- **Intention-Revealing Interfaces**: Name things for what they do, not how
- **Side-Effect-Free Functions**: Separate computation from state changes
- **Closure of Operations**: `Money.plus(Money) → Money` — chainable, predictable

### Breakthroughs Happen
After grinding iterative refinement, suddenly a deeper model becomes visible. It eliminates complexity and makes impossible things easy. **Recognize these moments and act on them aggressively.**

---

## 🗺️ Strategic Design (The Most Underappreciated Part)

### Bounded Context
Every large system has multiple models. Each model must live within an **explicit boundary** where its language is consistent.

```
❌ One giant model for everything → impossible to maintain
✅ Explicit Bounded Contexts → each internally consistent

Sales Context: Customer = someone who buys
Fulfillment Context: Customer = destination address
→ Same word, different models, explicit boundary between them
```

### Context Map — Draw It
```
[Your BC] ──── Shared Kernel ──── [Partner BC]
    │
    │ Anticorruption Layer
    ▼
[Legacy System]
    │
    │ Conformist
    ▼
[External API]
```

### Distillation — Not All Code is Equal
```
Core Domain:        WHERE YOUR BUSINESS WINS → best people, deepest models
Supporting Domain:  Necessary but not unique → solid engineering
Generic Subdomain:  Solved problems → buy or use open-source
```

**Most teams treat all their code equally. DDD says that's wrong.** Ruthlessly identify your Core Domain and concentrate your best work there.

---

## 💡 The Most Actionable Lessons

1. **Start with the language** — Get developers and domain experts talking, then name everything they discuss

2. **Protect your domain layer** — Business logic must not bleed into UI, database, or infrastructure code

3. **Aggregate roots = transaction boundaries** — One aggregate, one transaction. Size them carefully.

4. **Repositories are not DAOs** — They provide a collection-like illusion, not just CRUD. They know about Aggregates.

5. **Draw a Context Map on day one** — Know where your boundaries are before you build across them

6. **Find the Core Domain** — What would make your software worthless if done badly? That's your core. Invest there.

7. **Don't unify what shouldn't be unified** — Forcing a single model across the whole enterprise creates a model that serves no one well

8. **Model and implementation must stay in sync** — If the code diverges from the model, you have no model

---

## 📊 DDD in One Diagram

```
                    STRATEGIC DESIGN
              ┌─────────────────────────┐
              │  Bounded Context        │
              │  ┌───────────────────┐  │
              │  │  CORE DOMAIN  ⭐  │  │
              │  │                   │  │
              │  │  Entities         │  │
              │  │  Value Objects    │  │    Context Map
              │  │  Aggregates       │  │◄──────────────► [Other BC]
              │  │  Services         │  │
              │  │  Repositories     │  │
              │  │  Factories        │  │
              │  └───────────────────┘  │
              │                         │
              │  Ubiquitous Language    │
              └─────────────────────────┘
                          │
              ┌───────────┴────────────┐
              │  LAYERED ARCHITECTURE  │
              │  UI / Application /    │
              │  Domain / Infrastructure│
              └────────────────────────┘
```

---

## 📚 Companion Reading

- *Implementing Domain-Driven Design* — Vaughn Vernon (practical implementation guide)
- *Domain-Driven Design Distilled* — Vaughn Vernon (shorter, more accessible intro)
- *Patterns of Enterprise Application Architecture* — Martin Fowler (technical infrastructure patterns)
- *Analysis Patterns* — Martin Fowler (reusable domain patterns)

---

*← [Back to Domain-Driven Design](README.md)*
