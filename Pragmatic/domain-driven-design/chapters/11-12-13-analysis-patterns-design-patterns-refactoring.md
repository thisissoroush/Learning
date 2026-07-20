# Chapters 11–13 — Analysis Patterns, Design Patterns & Refactoring Toward Deeper Insight

---

# Chapter 11 — Applying Analysis Patterns

> *"Analysis patterns offer the promise of accelerating your work by giving you a head start in modeling complex domains."*

## 🎯 Core Concept

**Analysis patterns** are documented solutions to common modeling problems in recurring domain types (accounting, trading, healthcare, etc.). They're not code — they're conceptual models with known trade-offs, proven in real projects.

The key book for this is Martin Fowler's *Analysis Patterns* (1996). Rather than reinventing solutions to common domain problems, teams can draw on these proven patterns.

## 🔍 How to Use Analysis Patterns

1. **Recognize the domain type** — Is this an accounting system? A scheduling system? A measurement system?
2. **Find the pattern** — Look for documented patterns that match
3. **Adapt, don't copy** — The pattern is a starting point; refine it to match your specific domain
4. **Translate into your language** — Express the pattern using your Ubiquitous Language

## 📐 Example: Quantity Pattern

A common pattern in many domains is tracking measurable quantities with their units:

```java
// Instead of: double weight = 5.0; (ambiguous — kg? lbs?)
// Use the Quantity pattern:

class Quantity {
    private final BigDecimal amount;
    private final Unit unit;
    
    public Quantity add(Quantity other) {
        // handles unit conversion
    }
    
    public Quantity convertTo(Unit targetUnit) { ... }
}
```

This pattern appears in chemistry, physics, e-commerce, manufacturing — anywhere measurements matter.

## 💡 Key Point

Analysis patterns are inputs to knowledge crunching, not outputs. They help you **ask better questions** of domain experts and **recognize** when your model is heading somewhere that others have documented.

---

# Chapter 12 — Relating Design Patterns to the Model

> *"Design patterns can be applied to the domain model, not just to the technical layers."*

## 🎯 Core Concept

GoF (Gang of Four) design patterns are usually taught as technical patterns. But many of them directly model domain concepts when applied at the domain layer.

## 🔀 STRATEGY (a.k.a. POLICY)

In the domain, the **Strategy** pattern becomes a **Policy** — an interchangeable business rule or algorithm.

```java
// The overbooking example from Chapter 1:

// BEFORE: rule buried in code
if ((voyage.bookedCargoSize() + cargo.size()) <= voyage.capacity() * 1.1) { ... }

// AFTER: Policy makes it explicit and swappable
interface OverbookingPolicy {
    boolean isAllowed(Cargo cargo, Voyage voyage);
}

class TenPercentOverbookingPolicy implements OverbookingPolicy {
    public boolean isAllowed(Cargo cargo, Voyage voyage) {
        return cargo.size() + voyage.bookedCargoSize()
               <= voyage.capacity() * 1.1;
    }
}

// Different policies for different routes/seasons:
class NoOverbookingPolicy implements OverbookingPolicy { ... }
class FifteenPercentPolicy implements OverbookingPolicy { ... }
```

**When to use:** When a business rule or algorithm varies, and domain experts talk about different "policies" or "strategies."

## 🌳 COMPOSITE

The **Composite** pattern models part-whole hierarchies — things that contain other things of the same type.

```
Geographic structure:
  Region → contains → [Region, Location, Location, ...]
  
Sales territory:
  SalesTerritory → contains → [SalesTerritory, Account, ...]
```

```java
interface SalesComponent {
    Money totalRevenue();
    boolean contains(Account account);
}

class SalesTerritory implements SalesComponent {
    private List<SalesComponent> children; // can be sub-territories or accounts
    
    public Money totalRevenue() {
        return children.stream()
            .map(SalesComponent::totalRevenue)
            .reduce(Money.ZERO, Money::add);
    }
}
```

## 💡 Key Point

When you apply a design pattern at the domain level, the **pattern name becomes part of the Ubiquitous Language**. "That's the OverbookingPolicy" is a meaningful statement everyone on the team understands.

---

# Chapter 13 — Refactoring Toward Deeper Insight

> *"The process of refactoring toward a deeper model is ongoing — it doesn't end when you've 'found' the model."*

## 🎯 Core Concept

Refactoring in DDD isn't just cleaning up code — it's continuously discovering and expressing deeper domain understanding. The trigger is always a new insight, not just a code smell.

## 🚀 How It Starts

Refactoring toward deeper insight can be triggered by:
- **Awkward expression** — Something is hard to say in the current model
- **Missed concept** — A domain expert uses a term that doesn't appear anywhere in the code
- **Contradictions** — Two parts of the model have conflicting assumptions
- **Hindsight from implementation** — Writing the code reveals a model that doesn't work

## 👥 Exploration Teams

On larger projects, sometimes a small **exploration team** (2-3 people) spends focused time on a difficult modeling problem — experimenting with model alternatives without the pressure of delivering features. This is a legitimate investment.

## ⚡ The Process

```
New insight emerges
       │
       ▼
Explore model alternatives  ←──── Pair with domain expert
       │
       ▼
Find a better model
       │
       ▼
Refactor code to reflect it ←──── Many small steps (micro-refactorings)
       │
       ▼
Verify with domain experts
       │
       ▼
Look for the next insight
```

## 🎯 Focus on Basics

Even during deep refactoring:
- Keep the Ubiquitous Language updated
- Keep Aggregates tight
- Keep the domain layer isolated
- Keep tests passing

The **fundamentals don't change**. What changes is the depth of the concepts in the model.

## 💡 Key Takeaways

| Principle | Meaning |
|-----------|---------|
| Analysis patterns accelerate discovery | Don't reinvent common domain models |
| Design patterns belong in domain models | Strategy, Composite, etc. express domain concepts |
| Pattern names enter Ubiquitous Language | "That's a Policy" means something concrete |
| Refactoring is ongoing discovery | There's no final model — just deeper insight |
| Small teams can explore difficult areas | Exploration teams reduce risk of big misses |

---

*← [Back to Domain-Driven Design](../README.md)*
