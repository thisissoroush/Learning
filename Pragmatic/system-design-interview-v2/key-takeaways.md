# Key Takeaways — System Design Interview: An Insider's Guide, Volume 2

> *By Alex Xu & Sahn Lam — 13 real-world large-scale system designs taught through the lens of interview preparation*

---

## 🗺️ The Interview Framework (Applied Across All 13 Chapters)

Every chapter follows the same disciplined structure — and this is itself the most important lesson:

```
Step 1: Clarify requirements (functional + non-functional)
Step 2: Back-of-envelope estimation (QPS, storage, bandwidth)
Step 3: Propose high-level design (diagram + data flow)
Step 4: Deep dive into critical components
Step 5: Discuss trade-offs honestly
```

> **Never jump to implementation before you understand the constraints.**

---

## 🌍 Geospatial Systems

### 1. Discretize 2D Space for Efficient Indexing
Continuous coordinates can't be indexed. You must convert them to a discrete, queryable structure.

```
Geohash:  lat/lng → 1D string prefix → prefix search in Redis
QuadTree: recursive 4-way spatial subdivision → tree traversal
S2 Cells: Google's approach — spherical geometry, hierarchical

Choose Geohash for interviews — simpler, Redis-native, distributed
```

### 2. The 9-Cell Boundary Problem
Never query just the target cell. Always query **center + 8 surrounding cells**:

```
┌───┬───┬───┐
│NW │ N │NE │
├───┼───┼───┤
│ W │ ME│ E │  ← Query all 9 cells
├───┼───┼───┤
│SW │ S │SE │
└───┴───┴───┘
```

A user near a cell boundary will miss nearby businesses if you only query their cell.

### 3. Real-time Location = WebSocket + Redis Pub/Sub
For moving users (Nearby Friends), use:
- **WebSocket**: persistent bidirectional connection (not HTTP polling)
- **Redis Pub/Sub**: one channel per user for fan-out across WebSocket servers

---

## 🗺️ Maps & Routing

### 4. Pre-render Map Tiles, Serve from CDN
Never render map tiles on demand. Pre-render the pyramid of zoom levels, store on CDN:

```
URL: /tiles/{zoom}/{x}/{y}.png
Cache hit ratio: ~99%
CDN handles: ~99% of requests without hitting origin
```

### 5. A* Over Dijkstra for Routing
For large road networks, A* with a geographic heuristic (straight-line distance) explores far fewer nodes than Dijkstra while finding the same shortest path.

### 6. GPS Probes = Real-time Traffic
Every navigation app anonymously sends `{speed, location, heading}` every 30 seconds. Aggregated across millions of users, this provides real-time traffic data far better than any sensor network.

---

## 📨 Messaging Systems

### 7. Topics → Partitions → Offsets (Kafka Mental Model)

```
Topic = logical category (e.g., "orders")
Partition = unit of parallelism (ordered within, unordered across)
Offset = consumer's position (consumer controls this, not the broker)
```

**Rules**:
- More partitions = more throughput (more consumers can read in parallel)
- Same key = same partition = ordered delivery for that key
- Offset commit AFTER processing = at-least-once delivery (safest default)

### 8. Append-Only Log is the Right Data Structure for Queues

Sequential disk writes (300MB/s on HDD) vastly outperform random writes (~1MB/s). Message queues are fast precisely because they never do random I/O — only append.

### 9. Pull Model for Consumer Backpressure
Kafka consumers **pull** at their own pace. If a consumer is slow, it just pulls less frequently — it doesn't crash the broker. This is why Kafka handles slow consumers gracefully where RabbitMQ (push) struggles.

---

## 📊 Observability

### 10. Time-Series Data Needs a Specialized Database

```
Regular DB for metrics: INSERT INTO metrics → billions of rows → slow range queries
TSDB (InfluxDB/Prometheus): optimized for sequential writes + time-range queries
                            10-100x more efficient

TSDB data model: (metric_name, {labels}, timestamp, float_value)
```

### 11. Downsampling Saves 96% of Storage

```
Raw (15-second resolution):  Keep 7 days
5-minute averages:           Keep 30 days
1-hour averages:             Keep 1 year
1-day averages:              Keep forever

Cost: Can't see spike detail in 6-month-old data
Benefit: 96% storage reduction
```

### 12. Alert Fatigue Kills On-call Engineers

**Every alert must be:**
1. Actionable (can a human do something about it?)
2. Urgent (is this worth waking someone up?)
3. Deduplicated (don't send 100 alerts for the same root cause)

Use error budget burn rate (SLO-based alerting), not raw threshold alerts.

---

## ⚡ Event Aggregation

### 13. Lambda Architecture: Speed + Accuracy = Two Pipelines

```
Stream layer (Flink/Storm): Low latency, approximate → real-time dashboards
Batch layer (Spark):        High latency, exact → billing, finance
Serving layer:              Merge both → single API
```

**When to use Kappa instead**: If your stream processing can replay historical data efficiently, drop the batch layer (simpler codebase).

### 14. Watermarks Handle Late Arriving Events

Don't close time windows at the exact window end time. Wait for a watermark period (e.g., 2 minutes) to allow late events to arrive. Events older than watermark: drop or route to dead-letter topic.

---

## 🏨 Inventory & Reservation

### 15. The Atomic UPDATE Pattern Prevents Overbooking

```sql
-- Check AND decrement in ONE SQL statement (atomic):
UPDATE inventory
SET reserved = reserved + 1
WHERE item_id = X AND reserved < total;
-- rows_affected = 0 → sold out → fail gracefully
-- rows_affected = 1 → success
```

This eliminates the TOCTOU (Time-of-check-time-of-use) race condition that causes overbooking.

### 16. Idempotency Keys Make Retries Safe

```
Client generates UUID at checkout: "pay-uuid-1234"
Every retry sends same UUID
Server: "have I seen pay-uuid-1234?" 
  YES → return cached result (no double charge)
  NO  → process, store result, return

Works for: payments, reservations, any non-idempotent operation
```

---

## 💾 Storage Systems

### 17. Erasure Coding vs. Replication

| Strategy | Overhead | Tolerated Failures |
|---------|---------|-------------------|
| 3× Replication | 200% extra storage | 2 node failures |
| 6+3 Erasure Coding | 50% extra storage | 3 node failures |

**Use erasure coding for cold storage** (archive, backups) — same durability at 4× lower cost. Pay with CPU for encoding/decoding.

### 18. Multipart Upload for Large Files

Split large files into chunks (e.g., 100MB each), upload in parallel, have server reassemble. Benefits:
- Better network utilization (parallel connections)
- Retry only the failed chunk (not the whole file)
- Resume interrupted uploads

### 19. Pack Many Small Objects into Large Segment Files

Storing billions of small files in a filesystem is slow. Instead, pack multiple small objects into large segment files and maintain an index:

```
segment-0001.dat: [obj1][obj2][obj3]...[objN]
index.dat: obj_id → {file, offset, length}
```

---

## 💳 Financial Systems

### 20. Double-Entry Bookkeeping: The Foundation

```
RULE: Every transaction must debit ≥1 account AND credit ≥1 account
      Sum(debits) must ALWAYS equal Sum(credits)

Transfer $100: Alice → Bob
  DEBIT  Alice  $100  (money leaves)
  CREDIT Bob    $100  (money arrives)
  NET = 0 ← always

If books don't balance: there's a bug. Money appeared or disappeared.
```

### 21. Event Sourcing for Financial Audit Trails

Store events (what happened), not state (current balance). Derive state by replaying events.

```
Benefits:
  Complete audit trail (regulatory requirement)
  Point-in-time queries ("what was Alice's balance on Jan 1?")
  Debugging ("how did this balance get to $43.21?")
  Replay on bug fix

Cost:
  Complex to implement
  Eventual consistency for balance reads
```

### 22. Reconciliation is the Safety Net

Nightly reconciliation compares internal records to external bank/PSP statements. It catches the edge cases that all your safety mechanisms missed. **Never skip reconciliation** — it's the final guarantee that your books are correct.

---

## 🏎️ High-Performance Systems

### 23. Single-Threaded Matching Engine > Multi-threaded

For ultra-low-latency systems (stock exchange matching), a single-threaded design:
- Eliminates lock contention overhead
- Produces deterministic, replayable output
- Maximizes L1/L2 CPU cache efficiency
- Handles millions of operations/second

### 24. Redis Sorted Set is Perfect for Leaderboards

```redis
ZADD leaderboard 9820 "player:alice"    # O(log N)
ZINCRBY leaderboard 150 "player:alice"  # Atomic increment O(log N)
ZREVRANK leaderboard "player:alice"     # Player's rank O(log N)
ZREVRANGE leaderboard 0 9 WITHSCORES   # Top 10 O(log N + N)
```

O(log N) for all operations means 500 million players → ~29 operations for rank query.

### 25. Sequencer = Total Ordering in Distributed Systems

When multiple producers submit events concurrently, you need a **sequencer** to assign a monotonically increasing ID before processing. This converts a concurrent problem into a serial one, ensuring:
- Deterministic ordering (no ties, no ambiguity)
- Fair FIFO processing
- Exact replay capability

---

## 🧠 Meta-Patterns Across All Chapters

### The Back-of-Envelope Estimation Framework

```
Read/write ratio  → cache strategy, replica count
QPS at peak       → server count (assume 1000 QPS/server)
Storage per day   → DB choice, retention policy
Bandwidth         → CDN vs. direct, compression need
```

### Choose Database Based on Access Pattern

| Pattern | Best DB |
|---------|---------|
| Key-value with TTL | Redis |
| Time-series write-heavy | Cassandra / InfluxDB |
| Full-text search | Elasticsearch |
| Geospatial queries | Redis GEORADIUS |
| ACID transactions | PostgreSQL / MySQL |
| Blob/file storage | S3 / object store |
| Graph relationships | Neo4j / DynamoDB |

### The CAP Theorem in Practice

Every distributed system must choose between Consistency and Availability during a network Partition:

```
Banking/payments: Choose Consistency (CP)
  Better to be unavailable than wrong

Social feed/leaderboard: Choose Availability (AP)
  Stale data is fine; downtime is not

Most systems: Design for consistency, tolerate brief unavailability
```

---

## 🎯 Interview-Specific Advice

1. **State assumptions explicitly**: "I'll assume DAU of 100M and read/write ratio of 10:1"
2. **Draw before you talk**: Architecture diagram first, then explain components
3. **Name the trade-offs**: Every design decision has a cost — say it out loud
4. **Know your numbers**: 1ms network round trip, 100ms disk seek, 1GB/s memory bandwidth
5. **Start simple, then optimize**: Never lead with the complex solution; earn the complexity

---

*← [Back to System Design Interview Vol. 2](README.md)*
