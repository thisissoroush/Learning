# Chapter 1 — Scale From Zero to Millions of Users

> *"Every expert system started as a simple one. The journey from one user to one million users is a series of intentional trade-offs, not lucky accidents."*

---

## 🎯 Core Concept

This chapter is the foundation of all system design thinking. It walks through the evolution of a web application from a single server handling everything, to a globally distributed, fault-tolerant architecture that can serve millions of users.

The key insight: **you don't design for 100 million users on day one**. You design for today, with the ability to evolve toward tomorrow.

---

## 🏗️ The Evolution Journey

### Stage 1: Single Server — Everything on One Machine

```
User → DNS → Web Server (runs everything: web app + database + cache)

Simple. Zero operational overhead.
Works for: early prototypes, < 1,000 users
Problem: One point of failure. Can't scale. DB and app compete for resources.
```

### Stage 2: Separate Web and Database Tiers

```
Users → DNS → Web Server (app logic)
                    ↓
              Database Server (MySQL / PostgreSQL)
```

**Why split?** Different scaling needs:
- Web tier: CPU-bound (compute), scales horizontally
- Database tier: I/O-bound (disk), scales vertically then horizontally

### Stage 3: Load Balancer + Multiple Web Servers

```
Users → DNS → Load Balancer → Web Server 1
                            → Web Server 2
                            → Web Server 3
```

**Benefits:**
- No single point of failure in web tier
- Add/remove servers based on traffic
- Health checks: if Server 1 is down, traffic redirects to Server 2

**Load balancing algorithms:**
```
Round-robin:    Server 1 → Server 2 → Server 3 → Server 1...
Least-connections: route to whichever server has fewest active connections
IP-hash:        same client always routes to same server (sticky sessions)
```

### Stage 4: Database Replication

```
Primary DB  ←writes
     ↓ replicates
Replica DB1  ←reads
Replica DB2  ←reads
```

**Benefits:**
- Read QPS split across replicas (most traffic is reads)
- Replica can be promoted if primary fails
- Geographic replicas for lower read latency

**Writes always go to primary.** Reads can go to any replica. Accept slight staleness (eventually consistent reads).

### Stage 5: Cache Layer

```
App Server → Cache (Redis) → DB (only on cache miss)
```

**Cache-aside (lazy loading) pattern:**
```python
def get_user(user_id):
    # 1. Try cache
    user = cache.get(f"user:{user_id}")
    if user:
        return user  # Cache hit: O(1), ~1ms
    
    # 2. Cache miss: read from DB
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    
    # 3. Populate cache for next time
    cache.set(f"user:{user_id}", user, ttl=3600)
    return user
```

**What to cache:** Expensive queries, frequently read + rarely written data (user profiles, product details, popular articles).

**What NOT to cache:** Financial balances, real-time inventory counts, anything requiring strong consistency.

### Stage 6: CDN for Static Assets

```
User → CDN (edge server near user) → Origin Server (only on cache miss)
     ↑ 99% of static asset requests served here
```

CDN stores: images, CSS, JavaScript, videos, HTML

**Cache headers control CDN behavior:**
```
Cache-Control: public, max-age=31536000  ← cache for 1 year (immutable assets)
Cache-Control: no-cache                  ← always check origin (dynamic content)
```

**CDN invalidation:** When you deploy new CSS/JS, change filenames (hash-based):
```
app.abc123.css  → new version → app.xyz789.css
Old URL stays in CDN cache. New URL always gets fresh content.
```

### Stage 7: Multiple Data Centers (Global Scale)

```
US East → Load Balancer → App + DB cluster
                                ↕ replication
US West → Load Balancer → App + DB cluster
```

**GeoDNS** routes users to nearest datacenter:
- User in New York → US East (50ms latency)
- User in LA → US West (30ms latency)
- US East fails → GeoDNS switches all traffic to US West

**Challenge:** Data consistency across regions. Writes to US East must replicate to US West (eventual consistency).

### Stage 8: Stateless Architecture

```
❌ Stateful (session on server):
  User logs in → Session stored on Web Server 1
  If Load Balancer routes user to Web Server 2 → user logged out!

✅ Stateless (session in shared store):
  User logs in → Session stored in Redis
  Web Server 1 reads from Redis → authenticated
  Web Server 2 reads from Redis → also authenticated
  Any server can handle any request
```

**Rule:** Web servers must be stateless. Store state in external storage (Redis, DB).

### Stage 9: Sharding the Database

When a single primary DB can't handle write throughput:

```
Shard 1: users with user_id % 4 == 0
Shard 2: users with user_id % 4 == 1
Shard 3: users with user_id % 4 == 2
Shard 4: users with user_id % 4 == 3
```

**Challenge: Cross-shard joins**
```sql
-- This is now IMPOSSIBLE without scatter-gather:
SELECT u.name, o.total
FROM users u JOIN orders o ON u.id = o.user_id
-- users might be on shard 1, orders on shard 3!
```

**Solution:** Denormalize. Store user info alongside orders. Accept data duplication.

---

## 📊 Architecture Diagram

![Scale From Zero Architecture](../images/01-scale-from-zero.png)

---

## 📋 Back-of-Envelope: When to Add Each Tier

```
< 1,000 users:     Single server is fine
1K - 10K:          Separate DB from web server
10K - 100K:        Add load balancer + 2 web servers
100K - 1M:         Add cache + CDN + DB read replicas
1M - 10M:          Message queues for async work, vertical scaling of DB
10M+:              DB sharding, multiple data centers, microservices
```

---

## ⚖️ Design Decisions & Trade-offs

### SQL vs. NoSQL

| Factor | SQL (MySQL, PostgreSQL) | NoSQL (Cassandra, DynamoDB) |
|--------|------------------------|---------------------------|
| **Joins** | Powerful, native | Avoid (denormalize instead) |
| **Consistency** | ACID transactions | Eventual consistency |
| **Schema** | Fixed, migrations required | Flexible, schema-less |
| **Scale** | Vertical first, sharding complex | Horizontal natively |
| **Best for** | Relational data, transactions | Key-value, wide-column, large scale |

**Choose SQL if:** Your data has complex relationships, you need transactions, you're not sure yet.
**Choose NoSQL if:** You need massive write throughput, flexible schema, simple key-based access.

### Vertical vs. Horizontal Scaling

```
Vertical (scale up): Replace 16GB RAM server with 128GB RAM server
  + Simple, no code changes needed
  - Has a ceiling (biggest machine available)
  - Single point of failure
  - Very expensive

Horizontal (scale out): Add more servers
  + Unlimited scale in theory
  + Redundancy (fault tolerant)
  - Requires stateless architecture
  - Complexity increases
```

**Rule of thumb:** Scale vertically first (simpler), then horizontally when you hit limits.

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **Stateless web tier** | Store session in Redis/DB — any server handles any request |
| **Cache aggressively** | 80% of reads can be served from cache, not DB |
| **CDN for static assets** | Near-zero latency for images/CSS/JS for global users |
| **DB read replicas** | Split reads from writes — reads are 80% of traffic |
| **Horizontal scaling** | Add servers, not bigger servers — enables redundancy |
| **Message queues** | Decouple async work from synchronous request-response |

---

*← [Back to System Design Interview](../README.md)*
