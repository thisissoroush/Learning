# Key Takeaways — System Design Interview: An Insider's Guide (2nd Edition)

> *By Alex Xu — 15 real-world system designs for large-scale distributed systems interview preparation*

---

## 🗺️ The Interview Framework (Applied Every Time)

```
Step 1: Clarify requirements (3-10 min)   → Functional + Non-functional
Step 2: Back-of-envelope estimation        → QPS, Storage, Bandwidth
Step 3: High-level design                  → Box diagram + APIs
Step 4: Deep dive                          → Bottlenecks, algorithms, trade-offs
Step 5: Wrap up                            → Summary + operational concerns
```

> **Golden Rule**: Never jump to a solution before understanding the constraints. The interview rewards the *process*, not just the answer.

---

## ⚖️ The Fundamental Scaling Toolkit

### 1. Stateless Web Tier = Horizontal Scalability

```
✗ Session on web server → locked to one machine (can't scale out)
✓ Session in Redis → any server handles any request → unlimited horizontal scale
```

### 2. Cache Before Everything

```
Read path without cache: User → Web Server → DB → User    (slow, expensive)
Read path with cache:    User → Web Server → Redis → User  (fast, cheap)

Cache hit rate of 80% means:
  80% of traffic never reaches your database
  → DB load reduced 5×
  → Response time reduced 10×
```

### 3. CDN for All Static Content

```
Without CDN: User in Tokyo → your servers in US East → 150ms
With CDN:    User in Tokyo → CDN edge in Tokyo → 5ms

CDN handles: images, CSS, JS, videos, fonts
Rule: If it doesn't change per-user, put it in a CDN
```

### 4. DB Read Replicas for Read-Heavy Systems

```
Typical read/write ratio: 10:1 or higher
Primary DB: handles all writes (1 node)
Read Replicas: handle all reads (N nodes)

Result: DB capacity scales linearly with read replicas
```

---

## 🔑 Core Algorithmic Patterns

### 5. Consistent Hashing → Elastic Distributed Storage

```
Problem with naive modulo hashing:
  Add 1 server to 4-server cluster → 80% of all keys must move!

With consistent hashing:
  Add 1 server to 4-server cluster → only 20% of keys move (1/N)

Key: Virtual nodes (100 per server) → even distribution across the ring
Used by: Cassandra, DynamoDB, Memcached clusters
```

### 6. Bloom Filter → Fast Negative Lookups

```
Question: "Have I seen this URL before?" (web crawler, cache)

Without Bloom Filter: DB query (slow) or large in-memory set (expensive)
With Bloom Filter:    1.25GB RAM for 1 billion URLs, O(1) lookup

Rules:
  - "NOT in filter" = 100% certain → skip DB entirely
  - "MIGHT be in filter" = needs DB check
  - False positive rate: configurable, typically 1%
```

### 7. LSM Tree → Write-Optimized Storage

```
B-Tree (read-optimized):  Random disk writes → 100 IOPS
LSM Tree (write-optimized): Sequential appends → 300MB/s

How it works:
  1. Write to WAL (disk) + MemTable (RAM)
  2. Flush MemTable to SSTable when full
  3. Compact SSTables in background

Used by: Cassandra, RocksDB, LevelDB
```

### 8. Snowflake ID → Distributed Unique IDs

```
64-bit structure:
  1 bit (sign) | 41 bits (timestamp ms) | 5 bits (DC) | 5 bits (machine) | 12 bits (sequence)

Properties:
  - Time-ordered (sort by ID = sort by creation time)
  - 4,096 IDs per machine per millisecond
  - No coordination needed between machines
  - Used by: Twitter, Discord, Instagram

Custom epoch matters: Use recent epoch (not 1970) to maximize 41-bit lifespan
```

### 9. Token Bucket → Rate Limiting

```
State: (tokens: int, last_refill: timestamp)

Algorithm:
  1. Refill tokens since last check: tokens += elapsed_time × refill_rate
  2. Cap at bucket size
  3. If tokens >= 1: allow request, tokens -= 1
  4. Else: reject with HTTP 429

Redis-backed for distributed systems:
  INCR rate:user:alice:window → check against limit
  All servers share the same counter via Redis
```

---

## 💾 Storage Selection Patterns

### 10. Choose Database by Access Pattern

| Access Pattern | Database | Why |
|---------------|---------|-----|
| Simple key-value, fast | Redis | In-memory, O(1) |
| Sorted set (leaderboard) | Redis ZSET | O(log N) rank queries |
| Write-heavy, wide-column | Cassandra | LSM tree, linear scale |
| Full-text search | Elasticsearch | Inverted index |
| ACID transactions | PostgreSQL/MySQL | Strong consistency |
| Large files/blobs | S3/Object Store | Cheap, scalable |
| Time-series metrics | InfluxDB | Optimized for time-range |
| Geospatial | Redis GEORADIUS | O(N+K) radius search |

### 11. The Right DB Schema for Cassandra

```
Primary key design = query design:

For chat messages:
  CREATE TABLE messages (
      chat_id    UUID,       ← partition key (all messages in one partition)
      message_id BIGINT,     ← clustering key (sorted by Snowflake ID)
      ...
      PRIMARY KEY ((chat_id), message_id)
  )

This schema directly encodes the query: "Give me all messages in chat X, sorted by time"
Without touching any secondary index → O(1) partition lookup + O(N) range scan
```

---

## ⚡ Real-time & Messaging Patterns

### 12. WebSocket for Bidirectional Real-time

```
HTTP: Request-response, client must initiate
WebSocket: Bidirectional, either side can send anytime

When to use WebSocket:
  ✓ Chat systems
  ✓ Gaming (real-time state updates)
  ✓ Collaboration tools (Google Docs)
  ✓ Financial market data feeds

When NOT to use WebSocket:
  ✗ Simple request-response APIs (use REST)
  ✗ Mobile apps in background (use push notifications instead)
```

### 13. Fan-out on Write vs. Fan-out on Read

```
Fan-out on Write (Push model):
  When user A posts → write to all N followers' caches immediately
  ✅ Read is O(1) (pre-built)
  ❌ Celebrity with 100M followers = 100M cache writes per post

Fan-out on Read (Pull model):
  When user B opens feed → fetch from all followees in real-time
  ✅ No celebrity problem
  ❌ Read requires N queries (slow)

Hybrid (what Twitter/Facebook do):
  Regular users: push model (fast reads)
  Celebrities: pull model (avoid write storms)
```

### 14. Kafka in the Middle for Reliability

```
Without Kafka: Service A → Service B (direct)
  If B is slow: A blocks
  If B is down: request lost

With Kafka: Service A → Kafka → Service B
  If B is slow: Kafka buffers messages (backpressure handled)
  If B is down: messages wait in Kafka until B recovers
  If A generates burst: Kafka absorbs, B processes at sustainable rate

The Rule: Any time you need async, decoupled, reliable messaging → Kafka
```

---

## 🌐 Scale & Distribution Patterns

### 15. Sharding Strategy

```
Horizontal sharding by key:
  shard = hash(key) % num_shards
  → Even distribution
  → All operations on same key → same shard

Problems to solve:
  1. Cross-shard joins → denormalize, accept data duplication
  2. Cross-shard transactions → saga pattern or avoid
  3. Hot shards → virtual sharding, rebalance

Modern alternative: Use consistent hashing → minimize key migration
```

### 16. CDN for Video at Scale

```
YouTube scale: 100M video views/day = 1,157 views/sec
Avg video size: 500MB (5 min, 720p)

Without CDN: 1,157 × 500MB = 579GB/sec from your servers (impossible)
With CDN:    95% cache hit rate → 29GB/sec from origin
             Origin serves: rare videos, new videos not yet cached

Video serving architecture:
  S3 (origin) → CDN edge nodes (cache) → User
  
  HLS/DASH: adaptive bitrate = player chooses quality based on bandwidth
  No buffering wheel of death
```

### 17. Delta Sync for File Storage

```
Problem: 100MB file, user changes 1KB → don't upload 100MB!

Block-level delta sync:
  1. Split file into 4MB blocks
  2. Hash each block (SHA-256)
  3. Compare hashes with server
  4. Upload only changed blocks

Result: 4MB upload instead of 100MB = 96% bandwidth reduction
Deduplication bonus: identical blocks across users stored once
```

---

## 🎯 Interview Execution Patterns

### 18. The "Numbers You Must Know"

```
Latency:
  Memory: 100 nanoseconds
  SSD random read: 150 microseconds (0.15ms)
  DB query: 1-10 milliseconds
  Network DC round-trip: 0.5ms
  Cross-continent: 150-200ms

Storage:
  2^10 = 1KB | 2^20 = 1MB | 2^30 = 1GB | 2^40 = 1TB | 2^50 = 1PB

Time:
  86,400 sec/day ≈ 10^5 sec/day (use for QPS calculations)
  30 days/month, 365 days/year

Servers:
  1 server handles ~1,000 QPS (for typical web APIs)
```

### 19. The Trade-off Framework

Every design decision has a trade-off. Always state it:

```
"I'm choosing to push feeds to followers when a user posts.
 This gives us O(1) feed reads at the cost of more writes.
 The trade-off is worth it because reads are 300× more frequent than writes.
 For celebrities, we'd use the pull model to avoid write storms."

Format: "I'm choosing X. This gives us [benefit]. The trade-off is [cost].
         This is acceptable because [reason]."
```

### 20. Requirements Clarification Questions

```
Always ask:
  □ How many DAU?
  □ What's the read/write ratio?
  □ What are the latency requirements? (< 100ms? 1s?)
  □ What's the availability requirement? (99.9%? 99.99%?)
  □ What's the data retention period?
  □ Mobile-only? Web? Both?
  □ Global or single region?
```

---

## 🔗 Cross-System Pattern Reference

| Pattern | Systems in This Book |
|---------|---------------------|
| Redis ZSET | Leaderboard (Ch.10 V2), News Feed cache |
| Snowflake ID | Chat (Ch.12), Notification, YouTube video IDs |
| Bloom Filter | Web Crawler (Ch.9), Key-Value Store (Ch.6) |
| Trie | Search Autocomplete (Ch.13) |
| LSM Tree | Key-Value Store (Ch.6) |
| Consistent Hashing | Key-Value Store (Ch.6) |
| WebSocket | Chat (Ch.12), Google Drive notifications |
| Kafka | Notification (Ch.10), YouTube (Ch.14), Drive (Ch.15) |
| CDN | URL Shortener cache, YouTube streaming |
| Fan-out | News Feed (Ch.11) |
| Delta Sync | Google Drive (Ch.15) |
| Block Storage | Google Drive (Ch.15), Object Storage (V2 Ch.9) |

---

*← [Back to System Design Interview](README.md)*
