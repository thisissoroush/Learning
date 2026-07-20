# Chapter 7 — Implementing Queries in a Microservice Architecture

> *"Because each service has its own database, you must use one of the querying patterns to retrieve data scattered across multiple services."*

---

## 🎯 Core Concept

In a monolith, you JOIN tables. In microservices, data is split across services — you can't JOIN across databases. This chapter covers two patterns for querying across services: **API Composition** (simple aggregation) and **CQRS** (dedicated read models).

---

## 🔍 Pattern 1: API Composition

**Invoke multiple services and merge the results in memory.**

```
Client → API Gateway (or dedicated service)
           │
           ├──GET /orders/{id}──▶ Order Service
           ├──GET /tickets?orderId={id}──▶ Kitchen Service
           └──GET /deliveries?orderId={id}──▶ Delivery Service
           
           Aggregate results → return to client
```

### When to Use API Composition
- Simple joins — few services, small datasets
- Data volume is manageable in memory
- No complex filtering/sorting needed

### When It Falls Short
- **In-memory joins** of large datasets are expensive
- Services must be available (synchronous coupling)
- Complex aggregations are hard to implement efficiently

---

## 🏗️ Pattern 2: CQRS (Command Query Responsibility Segregation)

**Maintain separate read-optimized views, updated by consuming events.**

```
Write Side (Commands):                Read Side (Queries):
                                      
Order Service ──OrderCreated──▶ Event Handler
Kitchen Service ──TicketCreated──▶        │
Delivery Service ──DeliveryAssigned──▶    ▼
                               ┌─────────────────────┐
                               │ Order History View  │
                               │ (DynamoDB, Redis,   │
                               │  Elasticsearch...)  │
                               └─────────┬───────────┘
                                         │
                               Client ←──┘ GET /orders/{id}
```

### CQRS Architecture

```
┌───────────────────────────────────────────────────────────┐
│  Services emit events when data changes                   │
│                                                           │
│  Order Service ──┐                                        │
│  Kitchen Service ─┤── Message Broker ──▶ View Updater    │
│  Delivery Service ┘                           │          │
│                                               ▼          │
│                                     Read-Optimized Store  │
│                                     (query-friendly)      │
│                                               │          │
│                              Query Service ◀──┘          │
└───────────────────────────────────────────────────────────┘
```

### CQRS View Design Choices

**View datastore options:**

| Type | Best For | Examples |
|------|---------|---------|
| RDBMS table | Standard queries with filters | PostgreSQL, MySQL |
| DynamoDB | High-scale key-value + simple queries | AWS DynamoDB |
| Elasticsearch | Full-text search, complex filtering | Elasticsearch |
| Redis | Cache-like, low-latency lookups | Redis |

**Update strategies:**
- **Idempotent handlers** — safe to replay events
- **Version tracking** — ignore duplicate/out-of-order events
- **Full refresh** — occasionally rebuild from all events

---

## 📊 CQRS with DynamoDB — Example

```
OrderHistoryEventHandlers:
  handles → OrderCreated, TicketCreated, CreditCardAuthorized, ...
  updates → DynamoDB OrderHistory table

DynamoDB table design:
  PK: consumerId
  SK: orderId
  GSI: status, creationDate

Query patterns:
  - All orders for consumer: query by PK
  - Recent orders: query PK + sort by SK
  - Filter by status: use GSI
```

---

## ⚖️ API Composition vs. CQRS

| Factor | API Composition | CQRS |
|--------|----------------|------|
| Complexity | Low | High |
| Consistency | Strong (live data) | Eventual |
| Query flexibility | Limited | High |
| Performance | Medium (N service calls) | High (optimized store) |
| Data freshness | Real-time | Slightly delayed |
| Use case | Simple fetches | Complex views, high volume |

---

## 💡 Key Takeaways

| Insight | Implication |
|---------|-------------|
| No JOINs across service databases | Use API Composition for simple, CQRS for complex queries |
| CQRS views are eventually consistent | Design clients to handle slight staleness |
| Each query pattern can use a different datastore | Pick the right DB for the query, not the write model |
| View updaters must be idempotent | Events can be replayed — handlers must handle duplicates |
| CQRS eliminates the need for services to expose query endpoints | Query service owns the read model, not the write service |

---

*← [Back to Microservices Patterns](../README.md)*
