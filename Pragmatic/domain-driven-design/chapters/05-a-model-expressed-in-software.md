# Chapter 5 — A Model Expressed in Software

> *"Does an object represent something with continuity and identity, or is it an attribute that describes the state of something else?"*

---

## 🎯 Core Concept

The domain model must live in software through concrete building blocks. This chapter introduces the fundamental distinctions that shape every domain object: **Entities**, **Value Objects**, **Services**, and **Modules**. Getting these distinctions right is what makes a model-driven design work in practice.

---

## 🔗 Associations

Every association in the model must have a corresponding mechanism in the code. But associations are expensive — they create dependencies, increase complexity, and require maintenance.

**Three ways to tame associations:**

1. **Impose traversal direction** — most associations only need to go one way
2. **Add a qualifier** — reduce multiplicity (e.g., "country has one president *at a time*")
3. **Eliminate unnecessary associations** — if you don't need it, remove it

```
BIDIRECTIONAL (complex):          UNIDIRECTIONAL (simpler):
Country ◄──────► President        Country ──────► President
(each needs to know the other)    (Country knows its presidents,
                                   President doesn't reference Country)

QUALIFIED (most precise):
Country ──[at time period]──► President
(one president per time period — constraint embedded in model)
```

---

## 🏷️ ENTITIES (Reference Objects)

An **Entity** is an object defined primarily by its **identity**, not its attributes. It has a thread of continuity through time — it can change its attributes completely while remaining "the same thing."

```
Customer Entity:
  - Name can change (got married)
  - Address can change (moved)
  - Phone can change (new number)
  - ...but it's STILL THE SAME CUSTOMER
  
  Identity is tracked by: customerID (immutable)
```

**When something is an Entity:**
- Two objects with identical attributes are still distinct (two different bank transactions for the same amount)
- You need to track it across state changes
- It has a meaningful life cycle

**Modeling Entities:**
- Keep Entity definitions **sparse** — only what's needed to establish identity and life cycle
- Move attributes into Value Objects where possible
- Focus on the Entity's core purpose: maintaining continuity

```java
// Entity — identity matters, tracked by ID
class Customer {
    private final String customerId;  // immutable identity
    private String name;               // can change
    private Address address;           // can change
    
    // equals() based on customerId, not attributes
}
```

---

## 💎 VALUE OBJECTS

A **Value Object** is an object defined entirely by its **attributes**. It has no identity. Two Value Objects with the same attributes are interchangeable.

```
Color("Red") == Color("Red")
// These are the same — doesn't matter which instance you have
// If you lose one, just create another with the same attributes
```

**Examples:** Money, Date ranges, Addresses (sometimes), Colors, Coordinates

**Key properties:**
- **No identity** — you don't track which instance you have
- **Immutable** — never change a Value Object; replace it with a new one
- **Safely shareable** — because they're immutable, multiple objects can reference the same instance

```java
// Value Object — no identity, immutable
final class Money {
    private final BigDecimal amount;
    private final Currency currency;
    
    // Constructor sets all fields
    // No setters — immutable
    // equals() based on amount + currency
    
    public Money add(Money other) {
        // Returns a NEW Money, doesn't mutate this
        return new Money(this.amount.add(other.amount), this.currency);
    }
}
```

**Is Address an Entity or Value Object?** It depends on context:
- Mail-order company: Address is a Value Object (just a description of a place)
- Electric utility: Address is an Entity (it has a service contract, a history)

---

## ⚙️ SERVICES

Some operations don't naturally belong to any Entity or Value Object. When you force them onto an object, that object becomes bloated and confusing.

A **Service** is a stateless operation that represents a significant domain action.

**Three characteristics of a good Service:**
1. The operation relates to a domain concept that isn't natural to an Entity or Value Object
2. The interface is defined in terms of other domain model elements
3. The operation is **stateless** — any client can use any instance without caring about history

```
Domain Service example — Funds Transfer:
  - Not naturally on Account (involves TWO accounts + global rules)
  - Not an Entity (no identity, no state)
  - Pure operation: transfer(fromAccount, toAccount, amount)

Application Service example — Export to Spreadsheet:
  - "File formats" don't exist in the banking domain
  - This is an application concern, not a domain concern
```

**Service layers:**

| Layer | Example |
|-------|---------|
| **Infrastructure** | EmailSender, FileStorage |
| **Domain** | FundsTransferService, EncryptionService |
| **Application** | ExportToSpreadsheetService, NotificationCoordinator |

---

## 📦 MODULES (Packages)

Modules organize related concepts into cohesive groups. The **names of modules enter the Ubiquitous Language** — they communicate what part of the domain you're in.

**The goal:** Low coupling between modules, high cohesion within them — but driven by **domain concepts**, not technical categories.

```
✗ BAD (technical partitioning):
  com.example.entities/     ← Entity and Value Object mixed
  com.example.services/     ← all services together
  com.example.repositories/ ← all repos together

✓ GOOD (domain partitioning):
  com.example.shipping/     ← cargo, routing, itinerary
  com.example.billing/      ← invoices, payment, pricing
  com.example.customer/     ← customer profile, contact
```

---

## 💡 Key Takeaways

| Pattern | Question to Ask | Implication |
|---------|----------------|-------------|
| **Entity** | Does it need to be tracked through changes? | Give it a stable identity; keep definition lean |
| **Value Object** | Do we only care about what it is, not which one? | Make it immutable; share freely |
| **Service** | Does this operation belong on any object? | Create a stateless, named service |
| **Module** | What story does the grouping tell? | Name modules after domain concepts |

```
QUICK DECISION GUIDE:

Q: Does it have a life cycle and continuous identity?
├── YES → Entity (give it an ID)
└── NO → Q: Does it describe something?
          ├── YES → Value Object (make it immutable)
          └── NO → Q: Is it a significant domain operation?
                    ├── YES → Service (stateless, in domain layer)
                    └── NO → reconsider the design
```

---

*← [Back to Domain-Driven Design](../README.md)*
