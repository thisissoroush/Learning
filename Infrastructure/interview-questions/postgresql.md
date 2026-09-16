# 🐘 PostgreSQL — Interview Questions

---

### 1. What makes PostgreSQL different from other relational databases?

**A:** PostgreSQL is a full-featured, ACID-compliant, extensible open-source RDBMS with some standout capabilities:

- **Advanced types:** Arrays, JSONB, hstore, UUID, network types, range types, geometric types
- **True MVCC:** Multi-Version Concurrency Control — readers never block writers
- **Extensibility:** Custom data types, operators, functions, index types, procedural languages (PL/pgSQL, PL/Python, PL/Go)
- **Full-text search:** Built-in `tsvector`/`tsquery` — no need for Elasticsearch for basic search
- **Table inheritance:** Physical table partitioning and inheritance hierarchies
- **Advanced indexing:** B-tree, Hash, GiST, GIN, SP-GiST, BRIN — each optimized for different access patterns
- **Write-Ahead Log (WAL):** Foundation for replication, point-in-time recovery, logical decoding (CDC)
- **Window functions, CTEs, lateral joins:** More expressive SQL than most databases

---

### 2. What is MVCC and how does PostgreSQL implement it?

**A:** Multi-Version Concurrency Control allows readers and writers to operate concurrently without locking each other.

```
Each row has hidden system columns:
  xmin — transaction ID that created this row version
  xmax — transaction ID that deleted/updated this row (0 if current)
  ctid  — physical location (page, tuple offset)

When a row is updated:
  Old row: xmin=100, xmax=200 (marked dead by transaction 200)
  New row: xmin=200, xmax=0   (current version)

Reader at transaction 150:
  Sees old row (xmin=100 ≤ 150, xmax=200 > 150) — it was alive at tx 150
  Does NOT see new row (xmin=200 > 150)

Reader at transaction 250:
  Old row is dead (xmax=200 ≤ 250)
  Sees new row (xmin=200 ≤ 250, xmax=0)
```

**Consequence:** Dead row versions accumulate → **VACUUM** needed to reclaim space.

```sql
-- Check dead tuples
SELECT relname, n_live_tup, n_dead_tup, last_autovacuum
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;
```

---

### 3. What is VACUUM and why is it critical?

**A:** VACUUM reclaims storage occupied by dead row versions (created by UPDATE and DELETE under MVCC).

```sql
-- Manual VACUUM
VACUUM orders;               -- reclaim dead tuples, update visibility map
VACUUM ANALYZE orders;       -- + update query planner statistics
VACUUM FULL orders;          -- rewrites table, reclaims OS-level disk space (locks table!)

-- Check autovacuum activity
SELECT schemaname, relname, last_autovacuum, last_autoanalyze,
       n_dead_tup, n_live_tup,
       round(n_dead_tup::numeric / NULLIF(n_live_tup, 0) * 100, 2) AS dead_ratio
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;

-- Autovacuum triggers when:
-- n_dead_tup > autovacuum_vacuum_threshold + autovacuum_vacuum_scale_factor * n_live_tup
-- defaults: 50 + 0.20 * n_live_tup
```

**Transaction ID Wraparound** (critical): PostgreSQL uses 32-bit transaction IDs — after ~2 billion transactions, XID wraps around. Autovacuum prevents this by freezing old tuples. Monitor `age(datfrozenxid)` — alert above 1.5 billion.

```sql
SELECT datname, age(datfrozenxid) AS xid_age
FROM pg_database
ORDER BY xid_age DESC;
-- Alert if > 1,500,000,000
```

---

### 4. What are PostgreSQL index types and when do you use each?

**A:**

| Index Type | Use for | Example |
|-----------|---------|---------|
| **B-tree** (default) | Equality, range, sorting | `WHERE id = 42`, `WHERE price BETWEEN 10 AND 100` |
| **Hash** | Equality only, faster than B-tree for equality | `WHERE email = 'alice@x.com'` |
| **GIN** | Arrays, JSONB, full-text, `@>` containment | `WHERE tags @> '{python}'` |
| **GiST** | Geometric, text search, exclusion constraints | `WHERE point <-> center < radius` |
| **SP-GiST** | Non-balanced structures, partitioned data | IP routing, quad trees |
| **BRIN** | Very large tables with physical ordering | `WHERE created_at BETWEEN ...` on append-only tables |

```sql
-- Partial index — index only a subset (smaller, faster)
CREATE INDEX idx_orders_pending ON orders(customer_id)
WHERE status = 'pending';

-- Expression index — index a computed value
CREATE INDEX idx_users_lower_email ON users(LOWER(email));
-- Enables: WHERE LOWER(email) = 'alice@x.com' to use the index

-- Covering index (INCLUDE) — avoid table lookup
CREATE INDEX idx_orders_cover ON orders(customer_id)
INCLUDE (status, total, created_at);
-- Query: SELECT status, total FROM orders WHERE customer_id = 42
-- → Index-only scan (no heap access)

-- Composite index — column order matters
CREATE INDEX idx_orders_composite ON orders(customer_id, status, created_at);
-- Useful for: (customer_id), (customer_id, status), (customer_id, status, created_at)
-- NOT useful for: (status) alone, (created_at) alone

-- Concurrent index creation — doesn't lock table
CREATE INDEX CONCURRENTLY idx_large_table ON large_table(column);
```

---

### 5. How do you use EXPLAIN ANALYZE?

**A:**

```sql
EXPLAIN ANALYZE
SELECT o.id, o.total, c.name
FROM orders o
JOIN customers c ON c.id = o.customer_id
WHERE o.status = 'pending'
  AND o.created_at > NOW() - INTERVAL '7 days'
ORDER BY o.created_at DESC
LIMIT 100;

-- Output (simplified):
-- Limit (cost=... rows=100) (actual time=12.3..12.5 rows=100 loops=1)
--   -> Sort (cost=... rows=523) (actual time=12.1..12.2 rows=100 loops=1)
--       -> Hash Join (cost=...) (actual time=4.1..11.8 rows=523 loops=1)
--           Hash Cond: (o.customer_id = c.id)
--           -> Index Scan on orders (cost=... rows=523)
--               Index Cond: (status = 'pending' AND created_at > ...)
--           -> Hash (cost=...) (actual rows=10000 loops=1)
--               -> Seq Scan on customers

-- Key things to look for:
-- Seq Scan on large table → missing index
-- Nested Loop with large outer → N+1 pattern in ORM
-- Actual rows >> estimated rows → stale statistics (run ANALYZE)
-- Hash Join vs Nested Loop vs Merge Join → planner chose correctly?
-- Buffers: hit=X read=Y → cache hit ratio (hit/(hit+read))

-- More detail with buffers
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT ...;
```

---

### 6. What are CTEs and when should you use them?

**A:**

```sql
-- CTE (Common Table Expression) — named subquery, runs once
WITH monthly_revenue AS (
    SELECT DATE_TRUNC('month', created_at) AS month,
           SUM(total) AS revenue
    FROM orders
    WHERE status = 'completed'
    GROUP BY 1
),
ranked AS (
    SELECT month, revenue,
           LAG(revenue) OVER (ORDER BY month) AS prev_month,
           revenue - LAG(revenue) OVER (ORDER BY month) AS growth
    FROM monthly_revenue
)
SELECT month, revenue, prev_month,
       ROUND(growth / NULLIF(prev_month, 0) * 100, 2) AS growth_pct
FROM ranked
ORDER BY month;

-- Recursive CTE — for hierarchical data (org charts, category trees)
WITH RECURSIVE category_tree AS (
    -- Base case: root categories
    SELECT id, name, parent_id, 0 AS depth, name::text AS path
    FROM categories WHERE parent_id IS NULL

    UNION ALL

    -- Recursive case: children
    SELECT c.id, c.name, c.parent_id, ct.depth + 1,
           ct.path || ' > ' || c.name
    FROM categories c
    JOIN category_tree ct ON ct.id = c.parent_id
)
SELECT * FROM category_tree ORDER BY path;

-- CTE vs subquery:
-- CTE: materialized by default in older PG, more readable, reusable
-- PG 12+: CTEs are NOT materialized unless referenced multiple times or WITH RECURSIVE
-- Subquery: can be inlined by planner, sometimes more efficient
```

---

### 7. What are window functions?

**A:**

```sql
-- Window function: operates over a "window" of rows related to the current row
-- Does NOT collapse rows (unlike GROUP BY)

SELECT
    order_id,
    customer_id,
    total,
    -- Ranking
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY created_at DESC) AS order_rank,
    RANK()       OVER (PARTITION BY customer_id ORDER BY total DESC) AS total_rank,
    DENSE_RANK() OVER (ORDER BY total DESC) AS global_rank,

    -- Aggregations over window
    SUM(total)   OVER (PARTITION BY customer_id) AS customer_total,
    AVG(total)   OVER (PARTITION BY customer_id) AS customer_avg,
    COUNT(*)     OVER (PARTITION BY customer_id) AS customer_order_count,

    -- Running totals
    SUM(total) OVER (PARTITION BY customer_id ORDER BY created_at
                     ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total,

    -- Access adjacent rows
    LAG(total, 1) OVER (PARTITION BY customer_id ORDER BY created_at) AS prev_order_total,
    LEAD(total, 1) OVER (PARTITION BY customer_id ORDER BY created_at) AS next_order_total,

    -- First/Last in partition
    FIRST_VALUE(total) OVER (PARTITION BY customer_id ORDER BY created_at) AS first_order,
    LAST_VALUE(total)  OVER (PARTITION BY customer_id ORDER BY created_at
                              ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) AS last_order

FROM orders;
```

---

### 8. How does PostgreSQL handle JSON and JSONB?

**A:**

```sql
-- JSON: stored as text, preserves whitespace and key order
-- JSONB: stored as binary, deduplicated keys, supports indexing
-- Always prefer JSONB for querying

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT,
    attributes JSONB  -- flexible schema
);

INSERT INTO products VALUES (1, 'iPhone 15', '{"color": "blue", "storage": 256, "features": ["5G", "USB-C"]}');

-- Query JSONB
SELECT attributes->>'color' FROM products WHERE id = 1;          -- "blue" (text)
SELECT attributes->'storage' FROM products WHERE id = 1;          -- 256 (jsonb)
SELECT attributes#>>'{features,0}' FROM products WHERE id = 1;   -- "5G"

-- Filter
SELECT * FROM products WHERE attributes->>'color' = 'blue';
SELECT * FROM products WHERE attributes @> '{"storage": 256}';   -- containment
SELECT * FROM products WHERE attributes ? 'color';               -- key exists
SELECT * FROM products WHERE attributes->'storage' > '128'::jsonb;

-- Update JSONB
UPDATE products SET attributes = attributes || '{"color": "red"}' WHERE id = 1;
UPDATE products SET attributes = jsonb_set(attributes, '{storage}', '512') WHERE id = 1;

-- GIN index on JSONB (enables fast @>, ?, ?| queries)
CREATE INDEX idx_products_attributes ON products USING GIN (attributes);
CREATE INDEX idx_products_color ON products USING BTREE ((attributes->>'color'));
```

---

### 9. What is table partitioning in PostgreSQL?

**A:**

```sql
-- Range partitioning — partition by value range (common for time-series)
CREATE TABLE orders (
    id BIGINT,
    customer_id INT,
    total DECIMAL(10,2),
    created_at TIMESTAMP NOT NULL
) PARTITION BY RANGE (created_at);

-- Create partitions
CREATE TABLE orders_2024_q1 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE orders_2024_q2 PARTITION OF orders
    FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');

-- Default partition for anything that doesn't match
CREATE TABLE orders_default PARTITION OF orders DEFAULT;

-- List partitioning — partition by discrete values
CREATE TABLE orders (region TEXT, ...) PARTITION BY LIST (region);
CREATE TABLE orders_us PARTITION OF orders FOR VALUES IN ('US', 'CA');
CREATE TABLE orders_eu PARTITION OF orders FOR VALUES IN ('DE', 'FR', 'UK');

-- Hash partitioning — distribute evenly
CREATE TABLE orders (...) PARTITION BY HASH (customer_id);
CREATE TABLE orders_0 PARTITION OF orders FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE orders_1 PARTITION OF orders FOR VALUES WITH (MODULUS 4, REMAINDER 1);

-- Benefits:
-- Partition pruning: query on created_at only scans relevant partitions
-- Faster bulk deletes: DROP TABLE orders_2022_q1 (instant vs slow DELETE)
-- Better vacuum: each partition vacuumed independently

-- Check partition pruning
EXPLAIN SELECT * FROM orders WHERE created_at > '2024-01-01';
-- Should show: "Partitions selected: orders_2024_q1, orders_2024_q2..."
-- NOT: scan of all partitions
```

---

### 10. How does PostgreSQL replication work?

**A:**

```bash
# Streaming replication — WAL records streamed in real-time
# Primary streams WAL → Replica applies WAL

# postgresql.conf (primary)
wal_level = replica          # or logical for logical replication
max_wal_senders = 10
wal_keep_size = 1GB          # keep WAL for replicas that fall behind

# pg_hba.conf (primary) — allow replica to connect
host replication replicator 192.168.1.2/32 scram-sha-256

# Replica: pg_basebackup to copy initial data
pg_basebackup -h primary -U replicator -D /var/lib/postgresql/data -Fp -Xs -P

# recovery.conf / postgresql.conf (replica)
primary_conninfo = 'host=primary port=5432 user=replicator'
hot_standby = on  # allow reads on replica

# Check replication lag
SELECT client_addr, state, sent_lsn, write_lsn, flush_lsn, replay_lsn,
       (sent_lsn - replay_lsn) AS replication_lag_bytes
FROM pg_stat_replication;
```

```sql
-- Logical replication — replicate specific tables, different PG versions
-- Primary
CREATE PUBLICATION my_pub FOR TABLE orders, customers;

-- Replica (can be different PG version)
CREATE SUBSCRIPTION my_sub
    CONNECTION 'host=primary dbname=mydb user=replicator'
    PUBLICATION my_pub;

-- Logical replication also powers: Debezium CDC, pglogical, cross-version migration
```

---

### 11. What are common PostgreSQL performance tuning settings?

**A:**

```ini
# postgresql.conf — production tuning

# Memory
shared_buffers = 25% of RAM            # page cache (e.g., 4GB for 16GB server)
effective_cache_size = 75% of RAM      # planner hint (not allocated)
work_mem = 64MB                         # per sort/hash operation (careful: per connection!)
maintenance_work_mem = 512MB           # for VACUUM, CREATE INDEX

# WAL
wal_buffers = 16MB                     # WAL write buffer
checkpoint_completion_target = 0.9    # spread checkpoints
min_wal_size = 1GB
max_wal_size = 4GB

# Connections
max_connections = 200                  # use PgBouncer instead of high value
# Each idle connection uses ~5MB RAM

# Planner
random_page_cost = 1.1                 # SSD (default 4.0 is for HDD)
effective_io_concurrency = 200         # SSD parallel I/O

# Logging (for slow query analysis)
log_min_duration_statement = 1000      # log queries > 1s
log_checkpoints = on
log_lock_waits = on
log_temp_files = 0                     # log all temp file usage

# Autovacuum (tune for write-heavy tables)
autovacuum_vacuum_scale_factor = 0.05  # 5% dead tuples (default 20%)
autovacuum_analyze_scale_factor = 0.02 # 2% changes (default 10%)
```

---

### 12. What is pg_stat_statements and how do you use it?

**A:**

```sql
-- Enable extension (requires restart or superuser)
CREATE EXTENSION pg_stat_statements;

-- Find the slowest queries
SELECT
    LEFT(query, 80) AS query,
    calls,
    round(total_exec_time::numeric, 2) AS total_ms,
    round(mean_exec_time::numeric, 2) AS avg_ms,
    round(stddev_exec_time::numeric, 2) AS stddev_ms,
    round((total_exec_time / SUM(total_exec_time) OVER ()) * 100, 2) AS pct_total,
    rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;

-- Find queries with high row estimates vs actuals (stale stats)
-- → Run ANALYZE on those tables

-- Find queries with high variance (stddev >> mean)
-- → Possible lock waits or cache misses

-- Reset stats
SELECT pg_stat_statements_reset();
```

---

### 13. What are common PostgreSQL gotchas?

**A:**

```sql
-- 1. NULL comparisons — NULL != NULL
SELECT * FROM users WHERE manager_id != 42;
-- Does NOT return rows where manager_id IS NULL!
-- Fix:
SELECT * FROM users WHERE manager_id != 42 OR manager_id IS NULL;

-- 2. Integer division
SELECT 7 / 2;  -- returns 3, not 3.5!
SELECT 7.0 / 2;  -- or CAST(7 AS float) / 2

-- 3. LIKE with leading wildcard disables index
SELECT * FROM users WHERE name LIKE '%alice%';  -- Seq Scan!
-- Fix: use full-text search, or pg_trgm extension for LIKE with GIN index
CREATE EXTENSION pg_trgm;
CREATE INDEX idx_name_trgm ON users USING GIN (name gin_trgm_ops);

-- 4. SERIAL is not a transaction-safe sequence gap-free counter
-- Gaps happen on rollback — this is expected behavior
-- Use GENERATED ALWAYS AS IDENTITY for standard SQL

-- 5. ORDER BY without LIMIT on subqueries is optimized away
SELECT * FROM (SELECT * FROM orders ORDER BY created_at) sub LIMIT 10;
-- ORDER BY in subquery has no effect without LIMIT — add LIMIT to subquery

-- 6. UPDATE with JOIN syntax
UPDATE orders o
SET status = 'archived'
FROM customers c
WHERE o.customer_id = c.id AND c.region = 'EU' AND o.created_at < NOW() - INTERVAL '1 year';

-- 7. Timestamp with time zone vs without
-- Always use TIMESTAMPTZ — stored as UTC, displayed in session timezone
-- TIMESTAMP (without tz) stores literally what you give it — timezone-unaware
```

---

### 14. What is logical decoding and how does Debezium use it?

**A:**

```sql
-- Logical decoding: stream data changes (CDC) from WAL in a structured format

-- Enable (postgresql.conf)
wal_level = logical

-- Create replication slot
SELECT pg_create_logical_replication_slot('my_slot', 'pgoutput');

-- Peek at changes
SELECT * FROM pg_logical_slot_peek_changes('my_slot', NULL, NULL,
    'proto_version', '1', 'publication_names', 'my_pub');

-- Debezium connector reads from replication slot
-- Produces Kafka events:
-- { "op": "c", "before": null,  "after": {"id":1, "status":"pending"} }  -- INSERT
-- { "op": "u", "before": {...}, "after": {"id":1, "status":"shipped"} }  -- UPDATE
-- { "op": "d", "before": {...}, "after": null }                           -- DELETE

-- Monitor replication slots (unconsumed slots block WAL cleanup → disk full!)
SELECT slot_name, active, pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) AS lag_bytes
FROM pg_replication_slots;
-- Alert if lag_bytes grows unbounded
```

---

### 15. How do you implement connection pooling with PgBouncer?

**A:**

```ini
# pgbouncer.ini
[databases]
mydb = host=postgres port=5432 dbname=mydb

[pgbouncer]
listen_port = 6432
listen_addr = *
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt

# Pooling modes:
# session:     connection released when client disconnects (transparent)
# transaction: connection released after each transaction (most efficient for web)
# statement:   connection released after each statement (no multi-statement tx!)
pool_mode = transaction

max_client_conn = 1000       # clients can connect to PgBouncer
default_pool_size = 20       # actual connections to PostgreSQL
reserve_pool_size = 5        # extra connections for peak load
server_idle_timeout = 600    # close idle server connections after 10 min

# Transaction mode limitations:
# - SET, LISTEN, advisory locks, prepared statements need special handling
# - Use session mode for these or configure ignore_startup_parameters
```

```bash
# Check PgBouncer stats
psql -p 6432 pgbouncer -c "SHOW POOLS;"
psql -p 6432 pgbouncer -c "SHOW STATS;"
psql -p 6432 pgbouncer -c "SHOW CLIENTS;"
```
