# Chapter 9 — System Design & Scalability

> *"System design is the most open-ended type of interview question. There is no single right answer — only better and worse trade-offs."*  
> — Gayle Laakmann McDowell

---

## 🎯 Core Concept

System design questions test your ability to architect large-scale distributed systems. Unlike algorithm questions, there is no "correct" solution — only **justified trade-offs**. The interviewer evaluates your thought process.

---

## 🔢 The 4-Step Approach

```
STEP 1: CLARIFY (5–10 min)
  → Scale: users? reads/writes per second?
  → Features: what must the system do on day 1?
  → Constraints: latency? consistency? availability?

STEP 2: ESTIMATE (2–3 min)
  → "100M users × 2 requests/day = 2,300 QPS"
  → Storage: "1M new posts/day × 1KB = 1GB/day"

STEP 3: HIGH-LEVEL DESIGN
  → Draw boxes: client, LB, servers, cache, DB, queue, CDN
  → Start simple. Don't over-engineer.

STEP 4: DEEP DIVE
  → Pick 2–3 components. Go deep. Discuss trade-offs.
```

---

## 📈 The Scalability Ladder

```
< 1K users:  Single server (app + DB on one machine)
< 10K:       Separate DB server
< 1M:        Load balancer + multiple app servers + DB replica
< 10M:       Add Redis cache (80% reads from cache)
< 100M+:     CDN for static assets + DB sharding
```

---

## ⚡ Caching Strategies

```
Cache-aside (lazy):  App → check cache → miss → read DB → write cache
  + Only caches what's used.  – First request always slow.

Write-through:       Every write → cache AND DB simultaneously
  + Cache always fresh.  – Slower writes.

Write-back:          Write to cache only → async flush to DB
  + Fastest writes.  – Data loss risk if cache fails.

Eviction: LRU (most common), LFU, FIFO
```

```java
// LRU Cache — interview classic! O(1) get/put
class LRUCache {
    private final int capacity;
    private final LinkedHashMap<Integer, Integer> cache;

    public LRUCache(int capacity) {
        this.capacity = capacity;
        this.cache = new LinkedHashMap<>(capacity, 0.75f, true) {
            @Override
            protected boolean removeEldestEntry(Map.Entry<Integer,Integer> e) {
                return size() > capacity; // auto-evict least-recently-used
            }
        };
    }

    public int get(int key) { return cache.getOrDefault(key, -1); }
    public void put(int key, int value) { cache.put(key, value); }
}
// LinkedHashMap with accessOrder=true tracks LRU automatically
```

---

## 🗄️ Database Scaling

```
REPLICATION:
  Primary handles writes; replicas handle reads.
  + Read scalability + failover
  – Primary still a write bottleneck; replication lag

SHARDING (horizontal partition):
  Hash-based:   hash(user_id) % N → even distribution,
                bad for range queries
  Range-based:  A-M on shard 1, N-Z on shard 2 →
                risk of hot spots
  Directory:    lookup table maps key → shard; flexible
```

---

## 📬 Message Queues

```
Tight coupling (no queue):
  User → API → Video Transcoder  (slow synchronous call)

Decoupled (with queue):
  User → API → [Queue] → Workers
  API returns instantly; workers process async.

Benefits: burst absorption, independent scaling,
          retry on failure, multiple consumers.

Tools: Kafka (high-throughput, replay)
       RabbitMQ (flexible routing)
       Amazon SQS (managed, simple)
```

---

## ⚖️ CAP Theorem

```
Choose 2 of 3 in a distributed system:
  C — Consistency:   All nodes see the same data
  A — Availability:  Every request gets a response
  P — Partition Tol: Works despite network splits

Network partitions ARE inevitable → always choose C or A:
  CP: HBase, ZooKeeper, etcd  (consistent but may block)
  AP: Cassandra, DynamoDB      (always responds, may be stale)
```

---

## 💡 Key Takeaways

| Concept | Key Rule |
|---------|---------|
| Clarify first | Scale + features + constraints before boxes |
| Cache | 80% of reads from cache; reduces DB load dramatically |
| LRU Cache | LinkedHashMap(accessOrder=true) = O(1) implementation |
| Sharding | Hash-based for distribution; range-based for queries |
| Message queues | Decouple producers/consumers; absorb burst traffic |
| CAP theorem | Pick C or A when network partition occurs |
| Replication | Read scaling + failover; write bottleneck remains |

---

*[← Chapter 8](15-recursion-and-dynamic-programming.md) | [Back to Index](../README.md) | [Chapter 10 — Sorting & Searching →](17-sorting-and-searching.md)*
