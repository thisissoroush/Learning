# Chapter 0 — Introduction

> *"Why do our designs go wrong? Broadly, because we haven't been clear about what the problem we're solving is."*

---

## 🎯 Core Concept

This chapter sets the philosophical foundation. It explains **why most Python applications end up as a "ball of mud"** and introduces the tools to prevent it: **Dependency Inversion Principle (DIP)**, **Layering**, **Encapsulation**, and **Domain Modeling**.

---

## 🏢 Why Do Our Designs Go Wrong?

### The Ball of Mud Problem

Most applications end up as an undifferentiated mass where:
- Business logic is scattered across views, models, and utilities
- You can't tell the difference between domain concepts and database schema
- Changing one thing breaks three others
- Tests are either missing, slow, or coupled to the database

### The Root Causes

**1. Lack of Abstraction**
- Database directly imported into domain
- ORM classes are the only representation of business concepts
- No boundary between what's in memory and what's persisted

**2. Mixed Responsibilities**
- Views contain business logic
- Models contain both domain logic and persistence concerns
- Everything depends on everything else

**3. Coupling to Infrastructure**
- Business logic can't be tested without a database
- Can't change the ORM without rewriting the domain
- Can't reuse domain logic with a different interface (API vs CLI)

---

## 🔄 The Dependency Inversion Principle

**The Problem:** Traditional layered architecture has high-level modules depending on low-level modules.

```
Traditional Layering:
┌─────────────────────────────┐
│  Web Framework (Flask)      │
├─────────────────────────────┤
│  Business Logic             │  ← Depends on ORM
├─────────────────────────────┤
│  ORM (SQLAlchemy)           │  ← Depends on Database
├─────────────────────────────┤
│  Database (PostgreSQL)      │
└─────────────────────────────┘

Problem: Business logic is tightly coupled to the ORM.
Can't change ORM without rewriting business logic.
```

**The Solution:** Invert the dependencies. Both high-level and low-level depend on abstractions.

```
Inverted Architecture:
┌─────────────────────────────┐
│  Web Framework (Flask)      │
├─────────────────────────────┤
│  Business Logic             │
├─────────────────────────────┤
│  Abstract Repository        │  ← Abstraction layer
├─────────────────────────────┤
│  ORM (SQLAlchemy)           │  ← Concrete implementation
├─────────────────────────────┤
│  Database (PostgreSQL)      │
└─────────────────────────────┘

Benefit: Business logic depends on abstraction, not concrete ORM.
Can swap ORM or database without changing business logic.
```

---

## 🎯 Three Key Principles

### 1. Encapsulation

Hide internal details behind a clear interface.

```python
# ❌ Bad: exposing internals
product.batches[0].qty = 100

# ✅ Good: through a method
product.change_batch_quantity(batch_id, 100)
```

### 2. Abstraction

Define an interface (abstract class) that specifies what a component should do, without saying how.

```python
class AbstractRepository(ABC):
    @abstractmethod
    def add(self, obj): pass
    @abstractmethod
    def get(self, id): pass
```

### 3. Layering

Organize code into distinct layers with clear responsibilities and dependencies.

```
Domain Model   ← Pure business logic, no external dependencies
↓
Service Layer  ← Use cases, orchestration
↓
Adapters       ← Web framework, database, external systems
```

---

## 📐 The Domain Model

The **domain** is the problem you're trying to solve. Your authors work for an online furniture retailer; the domain is purchasing, procurement, and logistics.

A **domain model** is a representation of that problem in code.

```python
# This IS the domain model:
class Product:
    def allocate(self, line: OrderLine) -> str:
        ...  # Business logic for allocating orders to batches

class Batch:
    def can_allocate(self, line: OrderLine) -> bool:
        ...  # Business logic for checking available quantity

class OrderLine:
    def __init__(self, orderid: str, sku: str, qty: int):
        ...
```

The domain model should be:
- **Free of infrastructure concerns** (no database, no HTTP, no file I/O)
- **Testable in memory** (no setup, no teardown, no database)
- **Expressive of business concepts** (uses language the business understands)

---

## 🏗️ The Architecture We're Building

This book introduces **four design patterns** that work together:

1. **Repository** — Abstraction over persistent storage
2. **Service Layer** — Defines use case boundaries
3. **Unit of Work** — Atomic transactions
4. **Aggregate** — Consistency boundaries

And in Part II:

5. **Domain Events** — Decouple with events
6. **Message Bus** — Route events to handlers
7. **CQRS** — Separate read and write models

All of these serve one purpose: **keeping domain logic pure and decoupled from infrastructure**.

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **Ball of Mud** | Happens when responsibilities are mixed and coupling is high |
| **Dependency Inversion** | High-level AND low-level depend on abstractions |
| **Encapsulation** | Hide details behind clear interfaces |
| **Domain Model** | Pure business logic, zero infrastructure dependencies |
| **Layering** | Domain → Service → Adapters |

---

*← [Back to Architecture Patterns](../README.md)*
