# Chapter 6 — Pulling Apart Operational Data

> *"Data is a precious thing and will last longer than the systems themselves."* — Tim Berners-Lee

---

## 🎯 Core Concept

Breaking apart code is hard. Breaking apart data is **harder**. Data lives longer than systems, has more risk, and is more coupled than it appears. But shared databases in distributed architectures create serious problems — you must decide *when* to break data apart and *how* to do it safely.

Two opposing forces govern this decision:
- **Data Disintegrators** → reasons to break data apart
- **Data Integrators** → reasons to keep data together

---

## ⚡ Data Disintegrators (Reasons to Split)

### 1. Change Control

```
Monolith DB change impact:
  ALTER TABLE tickets DROP COLUMN status;
  
  All services that query tickets must:
    ① Be identified (easy to miss one!)
    ② Be updated
    ③ Be tested together
    ④ Be deployed simultaneously
    
  Miss one service → production failures ✗
```

**Bounded context solves this:**
```
Service A owns its DB          Service B owns its DB
  ↕                              ↕
Database A                    Database B

Change to DB A only impacts Service A.
Service B is abstracted via contract (JSON/API).
Column name changes in DB A don't break Service B's contract. ✓
```

### 2. Connection Management

```
Monolith: 200 connections to DB
Break into 50 services, 10 connections each:
  Minimum instances (2 each) → 1,000 connections
  Scaled instances (avg 5 each) → 1,700 connections
  
Original DB had 200 connections → now 8.5x overloaded!
```

**Connection quotas:**
```
Service A: quota=10, max used=5 → has spare capacity
Service B: quota=20, max used=20 → hitting quota, connection waits!

Solution: Reallocate quota from A to B
  Service A: quota=8
  Service B: quota=25 → no more waits ✓
```

### 3. Scalability

As services scale to multiple instances, DB connections multiply:
```
Service | Quota | Instances | Connections Used
───────────────────────────────────────────────
A       |  8    |    2      |    10
B       |  25   |    3      |    75
C       |  20   |    3      |    45
D       |  25   |    2      |    50
E       |  18   |    4      |    56

Total needed: 236  vs  Available: 100  → CRISIS
```

Breaking the DB reduces connections needed per database.

### 4. Fault Tolerance

```
Shared DB = Single Point of Failure
  DB goes down → ALL services fail simultaneously ✗

Separate DBs:
  DB-B goes down → only Service B fails
  Service A, C, D, E continue operating ✓
```

### 5. Architectural Quantum

A shared database forces all services into a **single architecture quantum** (Chapter 2). To achieve independent operational characteristics (different scalability, availability) per service, databases must be separated.

### 6. Database Type Optimization

Not all data is the same type. Breaking apart the DB lets you:
- Move key-value reference data → Key-Value DB
- Move survey data → Document DB  
- Move social graph → Graph DB
- Keep transactional data → Relational DB

---

## 🔒 Data Integrators (Reasons to Keep Together)

### 1. Data Relationships

```
Foreign keys, triggers, views tie tables together:

Table: ticket ──FK──▶ Table: ticket_status
                  ↑
         Can't separate these without removing the FK!
         
Removing FK means:
  - Application must enforce referential integrity
  - More code, more bugs, more complexity
```

### 2. Database Transactions (ACID)

```
Single DB: ACID transaction
─────────────────────────────
BEGIN;
  INSERT INTO customer VALUES (...)    ← succeeds
  INSERT INTO password VALUES (...)    ← if fails → ROLLBACK both ✓
COMMIT;

Multiple DBs: No ACID
─────────────────────
HTTP call → Insert customer → COMMITTED ✓
HTTP call → Insert password → FAILS ✗
Customer record now exists with NO password → data corruption!
```

---

## 🔨 The Five-Step Decomposition Process

```
Step 1: Analyze DB and Create Data Domains
  Group tables by domain: Customer, Payment, Survey, Profile, Ticketing, KB

Step 2: Assign Tables to Data Domains  
  Move tables into separate schemas within the same DB server
  Create synonyms for cross-domain access (temporary)

Step 3: Separate DB Connections to Data Domains
  Each service connects only to its own schema
  Remove all cross-schema queries (move to service-to-service calls)

Step 4: Move Schemas to Separate DB Servers
  Backup/restore OR replicate schemas to new servers
  Switch service connections to new servers

Step 5: Switch Over and Remove Old Schemas
  Final cutover — remove from original DB
  Each data domain now has its own independent DB ✓
```

### The Soccer Ball Metaphor

```
Think of the database like a soccer ball:

  ⚽ Each white hexagon = a data domain
  
  Inside each hexagon:
    - Tables
    - Foreign keys (self-contained)
    - Views (self-contained)
    
  Between hexagons (the black lines):
    - Cross-domain FKs → must be REMOVED
    - Cross-domain views → must be REMOVED
    - These become service-to-service calls
```

---

## 🗄️ Selecting a Database Type

### Relational Databases (PostgreSQL, MySQL, Oracle)
- ✅ ACID transactions, SQL, strong consistency
- ✅ Flexible querying (reads/writes balanced)
- ❌ Hard to scale horizontally, no native horizontal sharding

### Key-Value Databases (Redis, DynamoDB, Riak)
- ✅ Extremely fast key lookups, easy horizontal scaling
- ✅ Good for: session storage, user preferences, reference data
- ❌ Can only query by key — no ad-hoc queries

### Document Databases (MongoDB, Couchbase)
- ✅ Aggregate-oriented, flexible schema, secondary indexes
- ✅ Great for surveys, catalogs, user profiles (hierarchical data)
- ❌ Multi-document ACID limited, complex sharding

### Column Family (Cassandra, Scylla)
- ✅ Extremely high write throughput, horizontal scaling
- ✅ Tunable consistency
- ❌ Hard learning curve, complex data modeling

### Graph Databases (Neo4j)
- ✅ Relationship traversal is near-instant (pre-computed)
- ✅ Perfect for social graphs, recommendation engines, knowledge bases
- ❌ Cannot shard easily, steep learning curve

### NewSQL (CockroachDB, VoltDB)
- ✅ SQL + ACID + horizontal scaling — best of both worlds
- ✅ Auto-sharding, geo-distributed
- ❌ Newer, smaller communities

### Time-Series (InfluxDB, TimescaleDB)
- ✅ Optimized for append-only timestamp data
- ✅ Perfect for metrics, IoT, observability
- ❌ Not general-purpose, append-only model

---

## 🏢 Sysops Squad Saga: Polyglot Databases

The team justified migrating the Survey data domain from relational to document DB:

**Business justification (from the product owner):**
- Marketing department wants flexible, fast-changing surveys
- Currently takes *days* to add a question (schema change required)
- With document DB: add a new question in minutes

**Technical justification:**
- Survey data is hierarchical (survey → questions → answers)
- Document DB naturally represents this structure

**Decision — Single Aggregate vs. Split Aggregate:**
```json
// Single aggregate (chosen):
{
  "survey_id": "19999",
  "questions": [
    {"question_id": "50001", "question": "Rate the expert", "answer_type": "Option"},
    {"question_id": "50000", "question": "Did expert fix it?", "answer_type": "Boolean"}
  ]
}

// Split aggregate (rejected):
// Survey document + separate Question documents (harder to render)
```

The team chose **single aggregate** — accepting some duplication of question data in exchange for much simpler UI rendering and faster development.

---

## 💡 Key Takeaways

| Insight | Implication |
|---------|-------------|
| Breaking data is harder than breaking code | Plan data decomposition carefully — use the 5-step process |
| Shared DB = single quantum = single point of failure | To achieve true service independence, DB separation is often required |
| Bounded contexts abstract services from DB schema changes | Service B calling Service A's API is unaffected by A's DB schema changes |
| Connection multiplication surprises teams | Calculate connections before and after scaling — plan quota management |
| Not all data fits in relational databases | Polyglot persistence = use the right DB type for each domain's nature |

---

*← [Back to Software Architecture: The Hard Parts](../README.md)*
