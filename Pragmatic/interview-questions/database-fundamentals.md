# 🗄️ Database Fundamentals — Interview Questions

---

### 1. What is ACID and why does it matter?

**A:** ACID is a set of properties that guarantee database transactions are processed reliably:

```
A — Atomicity:    All operations in a transaction succeed, or none do.
                  No partial writes.
    "Transfer $100: debit A AND credit B. If credit fails, debit is rolled back."

C — Consistency:  Transaction brings the database from one valid state to another.
                  All rules, constraints, and cascades are respected.
    "Balance cannot go negative (check constraint). Transaction must not violate it."

I — Isolation:    Concurrent transactions execute as if they were sequential.
                  Transactions don't see each other's intermediate state.
    "Two simultaneous transfers don't interfere with each other."

D — Durability:   Once committed, data survives system failure.
                  Written to disk, replicated, WAL logged.
    "Committed transaction survives power outage."
```

---

### 2. What are transaction isolation levels?

**A:** Isolation is a spectrum. Higher isolation = fewer anomalies + lower concurrency + lower performance.

**Read anomalies:**
```
Dirty Read:      Reading uncommitted data from another transaction
                 "I see $500 that may be rolled back"

Non-Repeatable: Same query returns different results within a transaction
Read:           "First read: $500. Another transaction commits. Second read: $400."

Phantom Read:   Same query returns different rows (not values) within a transaction
                "First: 5 rows. Another transaction inserts. Second: 6 rows."
```

**Isolation levels:**
| Level | Dirty Read | Non-Repeatable Read | Phantom Read |
|-------|-----------|---------------------|--------------|
| Read Uncommitted | ✅ Possible | ✅ Possible | ✅ Possible |
| Read Committed | ❌ Prevented | ✅ Possible | ✅ Possible |
| Repeatable Read | ❌ Prevented | ❌ Prevented | ✅ Possible* |
| Serializable | ❌ Prevented | ❌ Prevented | ❌ Prevented |

*PostgreSQL's Repeatable Read also prevents phantoms via MVCC.

```sql
-- Set isolation level
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN;
  SELECT balance FROM accounts WHERE id = 42;
  -- Other transactions can't change this row until we COMMIT
COMMIT;
```

---

### 3. What are indexes and how do they work?

**A:** An index is a separate data structure that stores a subset of table data (the indexed columns) in a way that speeds up lookups.

```
Without index:
  SELECT * FROM orders WHERE customer_id = 42
  → Full table scan: read every row, check condition
  → O(n) — 1M rows = 1M reads

With index on customer_id:
  → B-tree lookup: O(log n)
  → For customer_id = 42: follow B-tree to leaf → get row pointers → fetch rows
  → 1M rows ≈ 20 comparisons + fetch matching rows

Index types:
  B-tree: default, equality + range queries, sorted
  Hash:   equality only, faster for equality
  GIN:    arrays, JSONB, full-text search
  GiST:   geometry, text search, flexible
  BRIN:   very large tables with physical ordering (time-series)
  Partial: indexes a subset of rows (WHERE is_active = true)
  Composite: multiple columns — order matters!
```

```sql
-- Composite index: (a, b, c)
-- Can use for: (a), (a, b), (a, b, c)
-- Cannot use for: (b), (c), (b, c)

CREATE INDEX CONCURRENTLY idx_orders_customer_status
    ON orders(customer_id, status)  -- covers queries on customer_id alone too
    WHERE deleted_at IS NULL;       -- partial index

EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 42 AND status = 'pending';
-- Look for: "Index Scan" (good), not "Seq Scan" (bad for selective queries)
```

---

### 4. What is the N+1 query problem?

**A:** Occurs when fetching a list of N items, then fetching related data for each individually — N+1 round trips to the database.

```python
# N+1 PROBLEM
orders = db.query("SELECT * FROM orders LIMIT 100")  # 1 query
for order in orders:
    customer = db.query("SELECT * FROM customers WHERE id = %s", order.customer_id)
    # 1 query per order → 100 queries for 100 orders = 101 total!

# SOLUTION 1: JOIN
orders = db.query("""
    SELECT o.*, c.name as customer_name, c.email
    FROM orders o
    JOIN customers c ON c.id = o.customer_id
    LIMIT 100
""")  # 1 query total

# SOLUTION 2: IN clause
orders = db.query("SELECT * FROM orders LIMIT 100")
customer_ids = [o.customer_id for o in orders]
customers = {c.id: c for c in db.query("SELECT * FROM customers WHERE id = ANY(%s)", customer_ids)}
for order in orders:
    order.customer = customers[order.customer_id]
# 2 queries total
```

---

### 5. What is the difference between SQL and NoSQL?

**A:**

| | SQL (Relational) | NoSQL |
|--|-----------------|-------|
| Schema | Fixed, predefined | Flexible, schema-less |
| Relationships | Joins (FK, normalization) | Denormalized, embedded |
| ACID | Full ACID | Varies (eventual → strong) |
| Scale | Vertical (+ read replicas) | Horizontal (sharding built-in) |
| Query | Powerful SQL (joins, aggregations) | Limited (no joins) |
| Use for | Complex relationships, financial | Documents, time-series, wide tables |

**NoSQL types:**
```
Document:    MongoDB, CouchDB — store JSON documents
             Use: catalogs, content, user profiles

Key-Value:   Redis, DynamoDB — simple key → value
             Use: caching, sessions, leaderboards

Wide-Column: Cassandra, HBase — rows with dynamic columns
             Use: time-series, IOT, write-heavy

Graph:       Neo4j — nodes and edges
             Use: social networks, recommendation engines

Search:      Elasticsearch — inverted index for text
             Use: full-text search, log analytics
```

---

### 6. What is normalization?

**A:** Organizing data to reduce redundancy and ensure data integrity. Higher normal forms = less redundancy.

```sql
-- UNNORMALIZED (multiple values in one cell)
CREATE TABLE orders (
    order_id INT,
    customer_name VARCHAR(100),
    customer_email VARCHAR(100),  -- repeated for every order of same customer
    items VARCHAR(1000)           -- "iPhone|2|999.99, iPad|1|799.99" (multi-valued)
);

-- 1NF: Atomic values, no repeating groups
-- 2NF: No partial dependencies on composite PK
-- 3NF: No transitive dependencies (non-key depends only on PK)

-- 3NF NORMALIZED
CREATE TABLE customers (id INT PRIMARY KEY, name VARCHAR, email VARCHAR);
CREATE TABLE orders (id INT PRIMARY KEY, customer_id INT REFERENCES customers);
CREATE TABLE products (id INT PRIMARY KEY, name VARCHAR, price DECIMAL);
CREATE TABLE order_items (order_id INT, product_id INT, quantity INT, unit_price DECIMAL);

-- Benefits: no anomalies (update/insert/delete), no redundancy
-- Cost: more JOINs required for reads
```

---

### 7. What is denormalization and when is it appropriate?

**A:** Intentionally introducing redundancy to improve read performance.

```sql
-- Normalized: requires JOIN to get customer name with order
SELECT o.id, o.total, c.name, c.email
FROM orders o JOIN customers c ON c.id = o.customer_id;

-- Denormalized: customer name stored directly in orders (redundant)
ALTER TABLE orders ADD COLUMN customer_name VARCHAR(100);
ALTER TABLE orders ADD COLUMN customer_email VARCHAR(100);

-- Query is now: SELECT id, total, customer_name FROM orders;
-- No join, faster read
```

**When to denormalize:**
- Read performance is the bottleneck
- Data is rarely updated (snapshot at write time is acceptable)
- Reporting/analytics (OLAP) — denormalized star schemas
- Document databases (embed related data to avoid lookups)

**Cost:** Update anomalies — changing customer email requires updating all orders.

---

### 8. What is Optimistic vs Pessimistic Locking?

**A:**

**Pessimistic:** Lock first, then work. Assume conflicts are likely.
```sql
-- Lock row — others cannot read or write (FOR UPDATE)
BEGIN;
SELECT balance FROM accounts WHERE id = 42 FOR UPDATE;
-- Other sessions block here until this transaction commits
UPDATE accounts SET balance = balance - 100 WHERE id = 42;
COMMIT;

-- Use: high contention, short transactions, financial systems
```

**Optimistic:** Work first, check for conflict at write. Assume conflicts are rare.
```sql
-- Read with version
SELECT balance, version FROM accounts WHERE id = 42;
-- version = 5

-- Write only if version unchanged
UPDATE accounts SET balance = 400, version = 6
WHERE id = 42 AND version = 5;
-- If 0 rows affected → conflict → retry or return error

-- Use: low contention, long-running operations, web applications
```

---

### 9. What is database replication?

**A:**

```
Master-Replica (Primary-Secondary) replication:
  All writes → Primary
  Primary → async replication → Replicas
  Reads → can go to Replicas (eventual consistency)

  Use: read scaling, geographic distribution, disaster recovery

Synchronous replication:
  Primary waits for replica confirmation before acking write
  → Strong consistency, no data loss on primary failure
  → Higher write latency

Asynchronous replication:
  Primary acks write, replicates to replica later
  → Low write latency
  → Possible data loss on primary failure (replication lag)

Replication lag:
  Time for a write on primary to appear on replica
  Critical for read-after-write consistency:
    Write to primary → immediately read from replica → might not see the write!
  Solution: read from primary for important reads after writes
```

---

### 10. What is database sharding?

**A:** Horizontal partitioning — splitting data across multiple databases (shards) based on a shard key.

```
Shard key: user_id
  User IDs 1-1M    → Shard 1 (DB server 1)
  User IDs 1M-2M   → Shard 2 (DB server 2)
  User IDs 2M-3M   → Shard 3 (DB server 3)

Query for user_id=500000:
  Router → Shard 1 (only queries that shard)

Cross-shard query (bad):
  Get all orders across all users?
  → Must query ALL shards → aggregate → expensive

Shard key selection (critical):
  ✅ High cardinality (many distinct values)
  ✅ Even distribution (no hot shards)
  ✅ Queries mostly within one shard
  ❌ Time as shard key → all recent writes go to latest shard (hot)
  ❌ Sequential IDs → uneven distribution as recent data grows
```

---

### 11. What is the difference between OLTP and OLAP?

**A:**

| | OLTP (Online Transaction Processing) | OLAP (Online Analytical Processing) |
|--|--------------------------------------|-------------------------------------|
| Purpose | Day-to-day transactions | Analysis, reporting, BI |
| Operations | INSERT, UPDATE, DELETE | SELECT (complex aggregations) |
| Data | Current, normalized | Historical, denormalized (star schema) |
| Query type | Simple, by PK | Complex, aggregations over many rows |
| Latency | Milliseconds | Seconds to minutes |
| Concurrency | High (many users) | Low (few analysts) |
| Examples | PostgreSQL, MySQL | Redshift, BigQuery, Snowflake |
| Index strategy | Many indexes (any column queried) | Columnar storage, bitmap indexes |

```
ETL/ELT pipeline:
  OLTP (operational DB) → ETL → Data Warehouse (OLAP)
  → Business Intelligence tools (Tableau, Looker) → Reports

Column-oriented storage (OLAP):
  Stores values column-by-column:
    all name values, then all age values, then all city values...
  → Compression: same-type values compress well
  → Analytics: only read needed columns (not entire rows)
  → Much faster for: SELECT city, COUNT(*), AVG(age) FROM users GROUP BY city
```

---

### 12. What are the most important database performance tips?

**A:**

```sql
-- 1. EXPLAIN ANALYZE — understand query plan
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 42 AND status = 'pending';
-- Look for: Seq Scan on large tables = missing index
-- Look for: Nested Loop with large rows = N+1 in ORM

-- 2. Index the right columns
-- Index WHERE clause columns, JOIN columns, ORDER BY columns
-- Don't index low-cardinality (boolean, status with 2 values)
-- Composite index: most selective column first

-- 3. Avoid SELECT *
SELECT id, status, total FROM orders  -- not SELECT *

-- 4. Use LIMIT for pagination
SELECT * FROM orders ORDER BY created_at DESC LIMIT 20 OFFSET 0;

-- 5. Avoid functions on indexed columns (index unusable)
-- BAD:  WHERE LOWER(email) = 'alice@x.com'  -- index on email not used
-- GOOD: CREATE INDEX ON users(LOWER(email)); WHERE LOWER(email) = 'alice@x.com'

-- 6. Batch operations
INSERT INTO orders (customer_id, total) VALUES
  (1, 99.99), (2, 149.99), (3, 49.99);  -- one statement
-- not 3 separate INSERTs

-- 7. Connection pooling — never create new connection per request
-- PgBouncer (PostgreSQL), HikariCP (Java), SQLAlchemy pooling (Python)

-- 8. Vacuum and analyze (PostgreSQL)
-- Autovacuum runs automatically but may need tuning for write-heavy tables

-- 9. Partitioning for large tables
-- Range partition orders by created_at (monthly partitions)
-- Queries with WHERE created_at > '2024-01-01' only scan recent partitions
```
