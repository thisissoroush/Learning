# Chapter 10 — Distributed Data Access

> *"A service must never reach into another service's database. But it still needs the data."*

---

## 🎯 Core Concept

In distributed architectures, bounded contexts forbid direct cross-service database access. But services constantly need data owned by other services. This chapter provides four patterns for accessing data across service boundaries — each suited to different situations.

---

## 🚫 The Problem

```
Service A owns:  customers table
Service B needs: customer_name to process an order

Forbidden:
  Service B → direct SQL → customers table ✗
  (violates bounded context, creates tight coupling)

Allowed (four patterns):
  1. Call Service A's API (Interservice Communication)
  2. Replicate the column into Service B's DB
  3. Use a replicated cache
  4. Share the data domain
```

---

## 🔗 Pattern 1: Interservice Communication

**Idea:** Service B calls Service A's API to get the data it needs.

```
Service B needs customer name:
  
  Service B ──GET /customers/{id}──▶ Service A
  Service B ◀──{ name: "Alice" }──── Service A
```

**Benefits:**
- Data is always current (no staleness)
- Clean bounded contexts
- No data duplication

**Shortcomings:**
- Added network latency per request
- Service B fails if Service A is down (runtime coupling)
- Cascading failures if many services chain API calls

**When to use:**
- Data changes frequently and must be current
- Low request volume
- Acceptable latency tolerance

---

## 📋 Pattern 2: Column Schema Replication

**Idea:** Copy specific columns from the owner's table into the consumer's table.

```
Service A owns: customers (id, name, email, address, credit_score, ...)
Service B needs: only customer_name for display purposes

Service B's DB:
  orders (order_id, customer_id, customer_name, ...)
                                  ↑
                         replicated column from Service A
```

**Synchronization:**
```
When customer name changes in Service A:
  Option 1: Service A publishes CustomerNameChanged event
  Option 2: Background sync process
  
Service B updates its replicated column.
```

**Benefits:**
- No runtime dependency on Service A
- Fast local reads (no network call)

**Shortcomings:**
- Data duplication
- Eventual consistency (brief staleness possible)
- Schema changes in Service A require coordinating Service B

**When to use:**
- Read-only, rarely-changing reference data
- Data needed for performance-critical queries

---

## 🗃️ Pattern 3: Replicated Caching

**Idea:** Maintain an in-memory cache populated from the data owner, accessible by the consumer service.

```
Service A writes: ──▶ Cache (shared, in-memory)
Service B reads:  ◀── Cache (local read, sub-millisecond)

                  ┌─────────────────┐
Service A ──────▶ │  Distributed    │ ◀────── Service B
                  │  Cache (Redis)  │
                  └─────────────────┘
```

**Benefits:**
- Extremely fast reads (in-memory)
- No runtime coupling to Service A (reads from cache)
- Cache updated on every change (near real-time)

**Shortcomings:**
- Cache consistency management complexity
- Memory constraints limit data volume
- Cache invalidation is notoriously hard

**When to use:**
- Reference/lookup data (product codes, country codes, exchange rates)
- High read volume, low write volume
- Data fits in memory

---

## 🏛️ Pattern 4: Data Domain

**Idea:** Two or more services share the same database schema (data domain), with agreed ownership rules per table.

```
Customer Domain Schema:
  ┌──────────────┬──────────────┬──────────────┐
  │ customers    │ addresses    │ preferences  │
  │ (owned by    │ (owned by    │ (owned by    │
  │  Profile Svc)│  Profile Svc)│  Pref Svc)   │
  └──────────────┴──────────────┴──────────────┘
         ▲                              ▲
   Profile Service              Preferences Service

Both services connect to the same schema.
Ownership rules define who writes to what.
```

**Benefits:**
- No network calls needed (direct DB access)
- ACID transactions possible within the domain
- Best performance of all patterns

**Shortcomings:**
- Services share a deployment dependency (DB)
- Schema changes require coordination between services
- Reduces service independence

**When to use:**
- Tightly related services that genuinely share data
- When ACID is required and other patterns can't provide it
- When performance requirements rule out network calls

---

## ⚖️ Pattern Comparison

| Pattern | Coupling | Performance | Consistency | Best For |
|---------|----------|-------------|-------------|----------|
| Interservice Call | Runtime | Lowest | Strong | Dynamic, current data |
| Column Replication | Schema | High | Eventual | Stable reference columns |
| Replicated Cache | None | Highest | Near-real-time | High-volume lookups |
| Data Domain | DB Schema | Very High | Strong (ACID) | Tightly coupled data |

---

## 🏢 Sysops Squad Saga: Ticket Assignment Data Access

**Problem:** Ticket Assignment Service needs customer location and expert skills — both owned by other services.

```
Expert Skills: owned by Admin Service (experts table)
Customer Location: owned by Customer Service

Ticket Assignment needs both to make assignments.

Solution chosen:
  Expert Skills → Replicated Caching
    (changes rarely, read-heavy, needs speed for assignment algorithm)
    
  Customer Location → Interservice Communication  
    (must be current — wrong location = wrong expert dispatched)
```

---

## 💡 Key Takeaways

| Insight | Implication |
|---------|-------------|
| Never cross service DB boundaries directly | Always go through the owning service or one of the four patterns |
| Choose pattern based on data characteristics | Frequency of change, consistency needs, volume, and latency tolerance |
| Replicated caching is powerful for reference data | Sub-millisecond reads with no runtime coupling |
| Data domains are a pragmatic compromise | Sometimes you need to accept shared DB for complex tightly-coupled data |
| Each pattern trades a different value | There's no universally best pattern — choose for your specific context |

---

*← [Back to Software Architecture: The Hard Parts](../README.md)*
