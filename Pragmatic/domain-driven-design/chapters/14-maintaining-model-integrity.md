# Chapter 14 — Maintaining Model Integrity

> *"The most fundamental requirement for a model is that it be internally consistent—its terms always have the same meaning, and it contains no contradictory rules."*

---

## 🎯 Core Concept

As systems grow, a single unified model becomes impossible to maintain. Different teams, subsystems, and legacy integrations create **multiple models** that must coexist. This chapter introduces patterns for keeping each model internally consistent while managing how they interact.

---

## 🗺️ BOUNDED CONTEXT

A **Bounded Context** is an explicit boundary within which a domain model applies. Inside that boundary, every term in the Ubiquitous Language has a specific, unambiguous meaning. Outside the boundary, the same word might mean something different.

```
E-Commerce System:

┌────────────────────────────────┐  ┌────────────────────────────────┐
│  Sales Context                 │  │  Fulfillment Context           │
│                                │  │                                │
│  Customer: someone who buys    │  │  Customer: shipping address    │
│  Product: what they want       │  │  Product: physical item to box │
│  Order: purchase intent        │  │  Order: pick/pack instruction  │
│                                │  │                                │
└────────────────────────────────┘  └────────────────────────────────┘
```

The word "Customer" means different things in each context. **That's fine** — as long as each context has its own clear model, and the translation between them is explicit.

**Key rules for Bounded Contexts:**
- One team owns one context
- The model is unified within the context
- Crossing the boundary requires explicit translation
- Name the context and mark it on diagrams

---

## 🔄 CONTINUOUS INTEGRATION

Within a single Bounded Context, the model can fragment as different developers work on different parts. **Continuous Integration** at the model level — frequently merging and testing — prevents this fragmentation.

```
Without CI:
  Developer A's "Product" diverges from Developer B's "Product"
  → Two competing models in the same context
  → Confusion, bugs, conflicting code

With CI:
  Frequent merges force team to reconcile differences
  → One coherent model
  → Conflicts surface quickly and get resolved
```

---

## 🗺️ CONTEXT MAP

A **Context Map** is a document (often a diagram) that shows:
- All the Bounded Contexts in your system
- How they relate to each other
- What kind of relationship each boundary has

```
Context Map Example:

[Sales Context] ──── Shared Kernel ──── [CRM Context]
      │
      │ Customer/Supplier
      ▼
[Fulfillment Context]
      │
      │ Anticorruption Layer
      ▼
[Legacy ERP System]
```

---

## 🤝 Relationships Between Bounded Contexts

### Shared Kernel
Two contexts share a small subset of the model. Changes to the shared part require agreement from both teams.

```
Sales + CRM share: Customer identity (ID + basic profile)
Both teams own it together, both must approve changes.
```

### Customer/Supplier Development Teams
One context (downstream) depends on another (upstream). The upstream team provides what the downstream needs.

```
Fulfillment (downstream) depends on Sales (upstream) for order data.
Sales defines the interface; Fulfillment adapts to it.
```

### Conformist
The downstream team simply conforms to the upstream model, even if it's not ideal. Used when the upstream has no incentive to collaborate.

```
Your app conforms to the payment provider's API model.
You adopt their terms (Transaction, Charge, Refund) even if they don't match your domain perfectly.
```

### Anticorruption Layer (ACL)
When integrating with a legacy system or external system with a very different model, create a translation layer that insulates your model from theirs.

```java
// Without ACL: your domain gets polluted
public Order createOrderFromLegacyData(LegacyOrderRecord record) {
    // your Order class now knows about LegacyOrderRecord format
    order.setLegacyId(record.getOldStyleId());  // ← corruption!
}

// With ACL: translation happens at the boundary
class LegacySystemAdapter {
    public Order translate(LegacyOrderRecord record) {
        return new Order(
            OrderId.of(record.getOldStyleId()),
            translateCustomer(record.getClientData()),
            translateLineItems(record.getItems())
        );
    }
}
```

### Separate Ways
Sometimes the best choice is no integration at all. Two contexts solve the same problem independently. High effort of integration is not worth the benefit.

### Open Host Service
Define a protocol that gives access to your context as a set of services. Publish the protocol so multiple clients can use it.

### Published Language
A well-documented, shared language that different contexts use to communicate (e.g., standard XML schema, event formats).

---

## 💡 Key Takeaways

```
BOUNDED CONTEXT quick guide:
  ✓ Draw explicit boundaries around each model
  ✓ Name the context
  ✓ One team, one context (ideally)
  ✓ The Ubiquitous Language applies only within the context

CONTEXT MAP quick guide:
  ✓ Document all contexts and their relationships
  ✓ Choose the right relationship type for each boundary
  ✓ Anticorruption Layer when integrating messy legacy systems
  ✓ Shared Kernel only for the smallest shared subset
```

| Pattern | Use When |
|---------|----------|
| Shared Kernel | Two teams can collaborate on a small shared model |
| Customer/Supplier | Clear upstream/downstream dependency |
| Conformist | Upstream won't adapt; downstream must conform |
| Anticorruption Layer | Legacy/external system has a very different model |
| Separate Ways | Integration cost > integration benefit |
| Open Host Service | Providing services to many downstream contexts |

---

*← [Back to Domain-Driven Design](../README.md)*
