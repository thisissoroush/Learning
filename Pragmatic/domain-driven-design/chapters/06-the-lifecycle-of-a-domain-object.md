# Chapter 6 — The Life Cycle of a Domain Object

> *"Aggregates mark off the scope within which invariants have to be maintained at every stage of the life cycle."*

---

## 🎯 Core Concept

Domain objects aren't just static data structures — they have **life cycles**. They're created, they change state, they're stored, retrieved, and eventually deleted. Managing this life cycle without letting it overwhelm the domain model requires three patterns: **Aggregates**, **Factories**, and **Repositories**.

```
Life Cycle:
  [Create] ──► [Active/Modify] ──► [Store] ──► [Retrieve] ──► [Archive/Delete]
  FACTORY         AGGREGATE        REPOSITORY   REPOSITORY      AGGREGATE
```

---

## 🔒 AGGREGATES — Taming the Object Web

In a rich domain model, objects reference each other creating a tangled web. This creates two problems:
1. **Integrity:** How do you enforce invariants that span multiple objects?
2. **Consistency:** How do you prevent concurrent users from corrupting data?

**The solution: Aggregates** — clusters of objects treated as a single unit for data changes.

```
┌─────────────────────────────────────────────┐
│              AGGREGATE BOUNDARY             │
│                                             │
│  ┌─────────────┐     ┌──────────────┐       │
│  │  <<ROOT>>   │────►│  Tire (x4)   │       │
│  │    Car      │     │  local ID    │       │
│  │  global ID  │     └──────────────┘       │
│  └─────────────┘                            │
│                                             │
│  External objects can only reference        │
│  the Root — never internal objects          │
└─────────────────────────────────────────────┘
        ↑
     Customer (external) can reference Car,
     but NOT individual Tires directly
```

**Aggregate rules:**
- One **Aggregate Root** (an Entity with global identity)
- External objects can **only hold references to the root**
- Internal objects have local identity (meaningful only inside the aggregate)
- Invariants for the entire aggregate are enforced with every transaction
- Only Aggregate Roots are retrieved from the database directly

**Purchase Order example:**

The PO and its Line Items form one aggregate. The invariant is: "sum of line items ≤ approved limit." This invariant must hold after every transaction.

If two users edit different line items simultaneously, they could both save valid-looking changes that together violate the limit. Solution: **lock the entire PO** (the aggregate root) during editing, not individual line items.

But locking too broadly creates contention. The fix: copy Part prices into Line Items instead of referencing Parts directly. This makes the PO aggregate self-contained — Part changes don't invalidate the PO's invariants.

---

## 🏭 FACTORIES — Encapsulating Object Creation

Complex object creation pollutes client code with knowledge of internals. A **Factory** encapsulates the creation process.

```
WITHOUT FACTORY:
  Client must know:
  - Which class to instantiate
  - What arguments to pass
  - What invariants to enforce during creation
  - How to wire up internal objects
  
WITH FACTORY:
  Client says: "Give me a new Order"
  Factory handles all the complexity
```

**Two factory approaches:**

1. **Factory Method** — on an existing object (e.g., `BrokerageAccount.newBuyOrder(security, shares)`)
2. **Standalone Factory** — a dedicated object for creating complex Aggregates

```java
// Factory Method on Aggregate Root
class BrokerageAccount {
    public TradeOrder newBuyOrder(String security, int shares) {
        // validates, creates, wires up the new TradeOrder
        // BrokerageAccount knows the rules for creating a valid order
        TradeOrder order = new TradeOrder(this.accountId, BUY, security, shares);
        return order;
    }
}
```

**Factory rules:**
- Each creation method is **atomic** — produces a fully valid object or throws an exception
- Factory is **abstracted to the type desired**, not the concrete class created
- For Entities: assign identity during creation (or reconstitution)
- For Value Objects: ensure all attributes are set at creation

---

## 🗄️ REPOSITORIES — Managing the Middle of the Life Cycle

To use an object, you need a reference to it. You can get one by: (1) creating it, (2) traversing an association from another object, or (3) **querying a Repository**.

A **Repository** provides the illusion of an in-memory collection of all objects of a type. You ask it for objects; it handles all the database machinery.

```
Without Repository:
  client ──SQL query──► DB ──result set──► factory ──► object
  (client is thinking about database, not domain)

With Repository:
  client ──"find order by id"──► Repository ──► object
  (client is thinking about domain concepts)
```

**Repository interfaces:**
```java
interface OrderRepository {
    Order findByTrackingId(String id);
    Collection<Order> findByCustomer(Customer customer);
    Collection<Order> findPendingOrders();
    void add(Order order);
    void remove(Order order);
}
```

**Repository advantages:**
- Simple, intention-revealing interface — client code reads like domain concepts
- Decouples domain from database technology
- Easy to substitute with in-memory implementation for testing
- Communicates which Aggregate Roots have global access

**Repository rules:**
- Provide Repositories only for **Aggregate Roots** that need direct access
- Leave transaction control to the client
- The Repository may delegate reconstitution to a Factory

---

## 💡 Key Takeaways

| Pattern | Purpose | Key Rule |
|---------|---------|----------|
| **Aggregate** | Enforce invariants, manage consistency | Only Root has global identity; external refs only to Root |
| **Factory** | Encapsulate complex creation | Atomic creation, abstract to desired type |
| **Repository** | Access persistent objects | Collection-like interface hiding all DB details |

```
LIFECYCLE FLOW:
  
  User Request
       │
       ▼
  Repository.find() ──── if not found ──► Factory.create()
       │                                        │
       ▼                                        │
  Aggregate Root ◄───────────────────────────────┘
       │
       ▼
  Business operations (invariants enforced)
       │
       ▼
  Repository.save() → Database
```

---

*← [Back to Domain-Driven Design](../README.md)*
