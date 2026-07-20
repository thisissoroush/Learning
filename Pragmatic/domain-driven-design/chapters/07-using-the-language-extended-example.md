# Chapter 7 — Using the Language: An Extended Example

> *"The model and the design are a single thing — any change to the code is a change to the model."*

---

## 🎯 Core Concept

This chapter walks through a real cargo shipping system showing how all the Part II building blocks work together: Entities, Value Objects, Aggregates, Factories, Repositories, Services, and Modules. It's a living demonstration of Model-Driven Design in practice — including the back-and-forth of discovering the right design.

---

## 🚢 The Shipping Domain

**Initial requirements:**
1. Track key handling of customer cargo
2. Book cargo in advance
3. Send invoices automatically when cargo reaches certain points

**Key domain objects:**

| Object | Type | Why |
|--------|------|-----|
| `Customer` | Entity | Has identity across multiple shipments |
| `Cargo` | Entity | Each piece of cargo is distinct (tracking ID) |
| `HandlingEvent` | Entity | Specific real-world events (loading, unloading) |
| `CarrierMovement` | Entity | A specific scheduled trip |
| `Location` | Entity | Globally unique places |
| `DeliverySpecification` | Value Object | Just describes the goal — no identity needed |
| `DeliveryHistory` | Entity | Borrowed identity from Cargo |

---

## 🔍 Refining Associations

The first model has many bidirectional associations. Simplifying them reveals domain insight:

```
BEFORE (bidirectional):
  Customer ◄──────► Cargo
  CarrierMovement ◄──► HandlingEvent

AFTER (directional — better):
  Customer (no reference to Cargo — use Repository query instead)
  HandlingEvent ──► CarrierMovement (read in this direction only)
```

**Insight:** A Customer doesn't "own" a list of all Cargoes. That would make Customer objects huge and tightly coupled to shipping. Use a Repository query to find a Customer's Cargoes when needed.

---

## 📦 Aggregate Boundaries

```
┌─────────────────────────────────┐
│     CARGO AGGREGATE             │
│  ┌──────────┐ ┌───────────────┐ │
│  │  Cargo   │ │DeliveryHistory│ │
│  │  (Root)  │ │               │ │
│  └──────────┘ └───────────────┘ │
│  ┌─────────────────────────────┐│
│  │   DeliverySpecification     ││
│  └─────────────────────────────┘│
└─────────────────────────────────┘

HandlingEvent: its own Aggregate (needs to be created without contending with Cargo)
Customer, Location, CarrierMovement: their own Aggregates
```

**Key decision:** `HandlingEvent` gets its own Aggregate because:
- Creating a HandlingEvent (logging an incident) should be a quick, low-contention operation
- If HandlingEvent was inside the Cargo Aggregate, every incident would lock the Cargo

---

## 🗃️ Repositories Selected

Only Aggregate Roots that the application needs to look up directly get Repositories:

| Repository | Why Needed |
|-----------|------------|
| `CustomerRepository` | Booking app needs to select customers by role |
| `CargoRepository` | Tracking queries, incident logging |
| `LocationRepository` | User must select destinations |
| `CarrierMovementRepository` | Incident logging needs to find which movement |

No `DeliveryHistory` Repository (accessed through Cargo). No `HandlingEvent` Repository initially (later added when needed for the collection refactoring).

---

## 🔄 A Key Refactoring: The Collection vs. Query Trade-off

**Original design:** `DeliveryHistory` holds a Java `List` of `HandlingEvents`.

**Problem discovered:** Adding a `HandlingEvent` requires modifying `DeliveryHistory`, which is inside the `Cargo` Aggregate. This creates contention: logging incidents competes with booking changes on the same Cargo.

**Refactoring:** Replace the collection with a Repository query.

```
BEFORE:
  DeliveryHistory → List<HandlingEvent>  (stored in memory/DB)
  
  Adding HandlingEvent: modifies DeliveryHistory → locks Cargo Aggregate!

AFTER:
  HandlingEvent has its own Repository
  DeliveryHistory.getEvents() → HandlingEventRepository.findByCargo(cargo)
  
  Adding HandlingEvent: only modifies its own Aggregate — no Cargo contention!
```

This is a **design trade-off** within the same model. The model doesn't change — just how the association is implemented.

---

## 🧩 Modules That Tell a Story

```
shipping/    ← Cargo, Itinerary, Router, Transport Schedule
customer/    ← Customer, Agreement, Contact
billing/     ← Invoice, Pricing Model, Bill of Lading
```

These module names are part of the Ubiquitous Language. "Let's talk about the billing module" immediately sets context for any team member.

---

## 🔌 Integrating an External System (Anticorruption Layer)

A Sales Management System handles allocation: how much cargo of each type the company will book.

Rather than coupling the booking system directly to the Sales Management System's model, an **Allocation Checker** acts as an Anticorruption Layer:

```
Booking Application
       │
       ▼
Allocation Checker ──► Sales Management System (external)
  (our domain terms)      (their terms/model)
  
AllocationChecker.deriveEnterpriseSegment(cargo)
AllocationChecker.mayAccept(cargo, quantityBooked)
```

The `EnterpriseSegment` — a Value Object — captures the business concept of "category for allocation purposes." It's defined in our model's terms, translated by the Allocation Checker to whatever the Sales System needs.

---

## 💡 Key Takeaways

| Decision | Lesson |
|---------|--------|
| Directional associations | Traverse only the direction domain logic requires |
| Aggregate boundaries from domain needs | Contention problems reveal wrong boundaries |
| Repositories only for needed Aggregate Roots | Don't create repositories "just in case" |
| Collection vs. query is an implementation detail | The model stays the same either way |
| External systems get Anticorruption Layers | Never let another system's model pollute yours |
| Modules named after domain concepts | They tell the story of the business |

---

*← [Back to Domain-Driven Design](../README.md)*
