# 🔴 Redis — Interview Questions

---

### 1. What is Redis and what are its core use cases?

**A:** Redis (Remote Dictionary Server) is an in-memory data structure store — database, cache, message broker, and streaming engine.

**Core use cases:**
- **Caching** — application-level cache (session data, query results, API responses)
- **Session storage** — web session state across multiple app servers
- **Rate limiting** — sliding window counters
- **Pub/Sub** — real-time messaging (chat, notifications)
- **Queues** — list-based task queues, Streams for durable queues
- **Leaderboards** — sorted sets for rankings
- **Distributed locks** — SET NX PX for mutual exclusion
- **Geospatial** — location-based queries
- **Real-time analytics** — HyperLogLog for cardinality, bitmaps for user tracking

---

### 2. What are Redis data types and when do you use each?

**A:**

```bash
# String — cache, counters, flags, sessions
SET user:42:name "Alice" EX 3600
GET user:42:name
INCR page:views             # atomic counter
INCRBY score 10
SETNX lock:resource 1       # set if not exists (distributed lock)
GETSET key newvalue         # get old, set new atomically

# Hash — object with multiple fields (avoid JSON for frequently-updated objects)
HSET user:42 name "Alice" email "alice@x.com" age 30
HGET user:42 name
HMGET user:42 name email
HGETALL user:42
HINCRBY user:42 login_count 1   # increment field

# List — queues, feeds, recent items
LPUSH tasks "task1" "task2"    # push to front
RPUSH tasks "task3"             # push to back
LPOP tasks                      # pop from front
BRPOP tasks 10                  # blocking pop (10s timeout) — for workers
LRANGE tasks 0 -1               # all items
LLEN tasks

# Set — unique items, membership, tags, social graphs
SADD tags:post:42 "python" "redis" "backend"
SISMEMBER tags:post:42 "redis"  # O(1) membership
SMEMBERS tags:post:42
SUNION tags:post:42 tags:post:43     # union
SINTER tags:post:42 tags:post:43     # intersection (common tags)
SDIFF  tags:post:42 tags:post:43     # difference

# Sorted Set — leaderboards, priority queues, time-series
ZADD leaderboard 100 "alice" 200 "bob" 95 "carol"
ZRANGE leaderboard 0 -1 WITHSCORES REV    # top scores
ZRANK leaderboard "alice"                  # rank (0-based)
ZINCRBY leaderboard 50 "alice"             # add 50 to alice's score

# HyperLogLog — approximate cardinality (unique visitors)
PFADD visitors:2024-01-15 "user1" "user2" "user1"
PFCOUNT visitors:2024-01-15    # ~2 (approximate, ~1% error)

# Bitmap — per-user flags, compact boolean arrays
SETBIT user:42:logins 20240115 1    # user logged in on day 20240115
GETBIT user:42:logins 20240115
BITCOUNT user:42:logins 0 -1        # total days logged in
```

---

### 3. What is Redis persistence and what are the trade-offs?

**A:**

| | RDB | AOF | No Persistence |
|--|-----|-----|---------------|
| Data loss | Up to last snapshot (minutes) | Up to 1s (fsync=everysec) | All data on restart |
| File size | Compact binary | Larger (all commands) | N/A |
| Startup time | Fast (load snapshot) | Slower (replay log) | Instant |
| Performance | Minimal impact | ~1% impact (everysec) | Best |
| Use case | Backups, DR | Mission-critical | Pure cache |

```bash
# redis.conf

# RDB — point-in-time snapshots
save 900 1        # save if 1+ writes in 900s
save 300 10       # save if 10+ writes in 300s
save 60 10000     # save if 10000+ writes in 60s
dbfilename dump.rdb
dir /var/lib/redis

# AOF — Append Only File
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec    # fsync every second (recommended)
# appendfsync always    # fsync every write (slowest, safest)
# appendfsync no        # OS decides (fastest, riskiest)

# AOF rewrite — compacts the AOF file periodically
auto-aof-rewrite-percentage 100   # rewrite when AOF is 2x original size
auto-aof-rewrite-min-size 64mb

# Hybrid: RDB + AOF (recommended for production)
aof-use-rdb-preamble yes  # AOF file starts with RDB snapshot (fast load)
```

---

### 4. What is Redis replication?

**A:**

```bash
# Master-Replica setup
# On replica:
replicaof 192.168.1.1 6379

# Or at runtime
redis-cli REPLICAOF 192.168.1.1 6379

# Check replication status
redis-cli INFO replication
# role:master
# connected_slaves:2
# slave0:ip=192.168.1.2,port=6379,state=online,offset=12345,lag=0

# Replication is async by default — replica may lag
# For sync replication before acking client:
WAIT 1 1000  # wait for 1 replica to ack, timeout 1000ms

# Replica is read-only by default
# All writes go to master → async replicated to replicas
# Reads can go to replicas (eventual consistency)
```

---

### 5. What is Redis Sentinel?

**A:** Redis Sentinel provides high availability — monitors master, performs automatic failover:

```
Client → Sentinel (discovery) → Master (read/write)
                              → Replica1 (read)
                              → Replica2 (read)

On master failure:
1. Sentinels detect master is down (via PING timeout)
2. Majority of sentinels agree master is down (quorum)
3. Sentinel elects a new leader
4. Leader promotes a replica to master
5. Other replicas replicate from new master
6. Clients are notified (SUBSCRIBE __sentinel__:hello)
```

```bash
# sentinel.conf
sentinel monitor mymaster 192.168.1.1 6379 2   # quorum = 2
sentinel down-after-milliseconds mymaster 5000   # failover after 5s
sentinel failover-timeout mymaster 10000
sentinel parallel-syncs mymaster 1

# Start sentinel
redis-sentinel /etc/redis/sentinel.conf

# Client connection (Python)
from redis.sentinel import Sentinel

sentinel = Sentinel([
    ("sentinel1", 26379),
    ("sentinel2", 26379),
    ("sentinel3", 26379),
])

master = sentinel.master_for("mymaster", password="secret")
replica = sentinel.slave_for("mymaster", password="secret")

master.set("key", "value")
replica.get("key")   # reads from replica
```

---

### 6. What is Redis Cluster?

**A:** Redis Cluster provides horizontal scaling by sharding data across multiple nodes:

```
16384 hash slots divided across nodes:
  Node A (master): slots 0-5460
  Node B (master): slots 5461-10922
  Node C (master): slots 10923-16383
  + replicas for each master (HA)

Key → CRC16(key) % 16384 → which slot → which node

Hash tags — force keys to same slot:
  {user:42}:name, {user:42}:email → same slot (CRC16 of "user:42")
  Must use hash tags for MGET/MSET/transactions across keys
```

```bash
# Create cluster
redis-cli --cluster create \
  192.168.1.1:7000 192.168.1.2:7001 192.168.1.3:7002 \
  192.168.1.4:7003 192.168.1.5:7004 192.168.1.6:7005 \
  --cluster-replicas 1

# Check cluster
redis-cli cluster info
redis-cli cluster nodes
redis-cli cluster slots
```

```python
# Python cluster client
from redis.cluster import RedisCluster

rc = RedisCluster(
    host="redis-node1",
    port=7000,
    password="secret",
    decode_responses=True,
)

# Cross-slot operations require hash tags
rc.mset({"user:{42}:name": "Alice", "user:{42}:email": "alice@x.com"})
rc.mget("user:{42}:name", "user:{42}:email")

# SCAN in cluster — must scan each node
for node in rc.get_primaries():
    for key in node.scan_iter("user:*"):
        print(key)
```

---

### 7. How do you implement distributed locking with Redis?

**A:**

```python
# SET NX PX — atomic set if not exists with expiry
import uuid, time

def acquire_lock(redis_client, resource: str, ttl_ms: int = 10000) -> str | None:
    token = str(uuid.uuid4())
    acquired = redis_client.set(
        f"lock:{resource}",
        token,
        nx=True,       # set only if not exists
        px=ttl_ms,     # expire in ttl_ms milliseconds
    )
    return token if acquired else None

# Release — Lua script for atomic check-and-delete
RELEASE_SCRIPT = """
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
else
    return 0
end
"""

def release_lock(redis_client, resource: str, token: str) -> bool:
    result = redis_client.eval(RELEASE_SCRIPT, 1, f"lock:{resource}", token)
    return result == 1

# Usage
token = acquire_lock(redis, "order:42")
if not token:
    raise ConcurrentModificationError("Could not acquire lock")

try:
    process_order(42)
finally:
    release_lock(redis, "order:42", token)

# Production: use Redlock algorithm (multi-node)
from redis.lock import Lock
with redis.lock("my-lock", timeout=10, blocking_timeout=5):
    critical_section()

# Or: redlock-py for true Redlock
from redlock import Redlock
dlm = Redlock([{"host": "localhost", "port": 6379}])
lock = dlm.lock("my-resource", 10000)
if lock:
    try: do_work()
    finally: dlm.unlock(lock)
```

---

### 8. How do you implement caching patterns?

**A:**

```python
import json, hashlib
from functools import wraps

# Cache-Aside (Lazy Loading) — most common
def get_user(user_id: int) -> dict:
    cache_key = f"user:{user_id}"

    # 1. Check cache
    cached = redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # 2. Cache miss — query DB
    user = db.query("SELECT * FROM users WHERE id = %s", user_id)
    if not user:
        return None

    # 3. Store in cache (5 min TTL)
    redis.setex(cache_key, 300, json.dumps(user))
    return user

# Write-Through — update cache on every write
def update_user(user_id: int, data: dict) -> dict:
    user = db.update("UPDATE users SET ... WHERE id = %s", user_id, data)
    redis.setex(f"user:{user_id}", 300, json.dumps(user))  # update cache
    return user

# Write-Behind (Write-Back) — write to cache, async flush to DB
# Faster writes but risk of data loss

# Read-Through — cache fetches from DB automatically (Redis proxy)

# Singleflight — prevent cache stampede
import threading
_flights = {}
_lock = threading.Lock()

def get_with_singleflight(key: str, fetch_fn) -> any:
    # Check cache first
    cached = redis.get(key)
    if cached: return json.loads(cached)

    with _lock:
        if key not in _flights:
            _flights[key] = threading.Event()
            should_fetch = True
        else:
            event = _flights[key]
            should_fetch = False

    if should_fetch:
        try:
            result = fetch_fn()
            redis.setex(key, 300, json.dumps(result))
            return result
        finally:
            with _lock:
                event = _flights.pop(key)
                event.set()
    else:
        event.wait()
        return json.loads(redis.get(key))
```

---

### 9. What are Redis Streams and how do they compare to pub/sub?

**A:**

| | Pub/Sub | Streams |
|--|---------|---------|
| Persistence | No — lost if no subscriber | Yes — disk persistence |
| Consumer groups | No | Yes |
| Message replay | No | Yes |
| Acknowledgment | No | Yes (XACK) |
| Fan-out | Yes (all subscribers) | Yes (multiple groups) |
| Use case | Real-time notifications | Reliable event log |

```bash
# Streams
XADD orders * event OrderCreated order_id order-123 total 99.99
# Returns: 1704067200000-0 (timestamp-sequence)

# Read from stream
XREAD COUNT 10 STREAMS orders 0-0    # from beginning
XREAD COUNT 10 STREAMS orders $      # only new messages

# Consumer groups
XGROUP CREATE orders order-service $ MKSTREAM

# Consume (each consumer gets different messages)
XREADGROUP GROUP order-service worker1 COUNT 10 STREAMS orders >
# > means "give me undelivered messages"

# Acknowledge
XACK orders order-service 1704067200000-0

# Pending messages (unacked)
XPENDING orders order-service - + 10

# Claim stale messages (from crashed workers)
XAUTOCLAIM orders order-service worker2 300000 0-0

# Stream info
XINFO STREAM orders
XINFO GROUPS orders
XLEN orders
```

---

### 10. How do you implement rate limiting with Redis?

**A:**

```python
# Fixed window
def is_allowed_fixed(user_id: int, limit: int = 100) -> bool:
    key = f"rl:fixed:{user_id}:{int(time.time() // 60)}"  # per minute
    count = redis.incr(key)
    if count == 1:
        redis.expire(key, 60)
    return count <= limit

# Sliding window (Lua script for atomicity)
SLIDING_WINDOW = """
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
local count = redis.call('ZCARD', key)

if count < limit then
    redis.call('ZADD', key, now, now)
    redis.call('PEXPIRE', key, window)
    return 1
end
return 0
"""

def is_allowed_sliding(user_id: int, limit: int = 100, window_ms: int = 60000) -> bool:
    now = int(time.time() * 1000)
    result = redis.eval(SLIDING_WINDOW, 1, f"rl:{user_id}", limit, window_ms, now)
    return bool(result)

# Token bucket (Lua script)
TOKEN_BUCKET = """
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])  -- tokens per second
local now = tonumber(ARGV[3])

local data = redis.call('HMGET', key, 'tokens', 'last_refill')
local tokens = tonumber(data[1]) or capacity
local last_refill = tonumber(data[2]) or now

-- Refill tokens
local elapsed = (now - last_refill) / 1000
tokens = math.min(capacity, tokens + elapsed * refill_rate)

if tokens >= 1 then
    redis.call('HMSET', key, 'tokens', tokens - 1, 'last_refill', now)
    redis.call('PEXPIRE', key, 3600000)
    return 1
end
return 0
"""
```

---

### 11. What are common Redis performance patterns?

**A:**

```bash
# Pipelining — send multiple commands without waiting for each response
redis.pipeline()
  .set("a", 1)
  .set("b", 2)
  .incr("c")
  .execute()
# 1 round trip instead of 3

# Transactions (MULTI/EXEC) — atomic command block
redis.multi()
  .incr("counter")
  .expire("counter", 3600)
  .exec()

# WATCH — optimistic locking
WATCH counter
value = redis.get("counter")
if value < 100:
    redis.multi()
    redis.incr("counter")
    redis.exec()   # fails if counter changed since WATCH

# Lua scripts — atomic, no round trips between commands
script = redis.register_script("""
    local val = redis.call('GET', KEYS[1])
    if val then
        return redis.call('SET', KEYS[1], tonumber(val) + tonumber(ARGV[1]))
    end
    return redis.call('SET', KEYS[1], ARGV[1])
""")
script(keys=["counter"], args=[5])

# Scan instead of KEYS (non-blocking)
# NEVER: redis.keys("user:*")  — blocks entire server
for key in redis.scan_iter("user:*", count=100):
    process(key)
```

---

### 12. What is Redis eviction policy?

**A:**

```bash
# redis.conf — memory management
maxmemory 2gb
maxmemory-policy allkeys-lru   # evict least recently used from all keys

# Eviction policies:
# noeviction      — return error when memory full (default)
# allkeys-lru     — evict LRU from all keys (general purpose cache)
# volatile-lru    — evict LRU from keys with TTL
# allkeys-lfu     — evict least frequently used from all
# volatile-lfu    — evict LFU from keys with TTL
# allkeys-random  — evict random from all
# volatile-random — evict random from keys with TTL
# volatile-ttl    — evict key with nearest TTL

# Check eviction stats
redis-cli INFO stats | grep evicted_keys
redis-cli INFO memory | grep mem_allocator
```

---

### 13. What are Redis keyspace notifications?

**A:**

```bash
# Enable in redis.conf
notify-keyspace-events "KEA"
# K = Keyspace events (published per key)
# E = Keyevent events (published per event type)
# A = All commands
# x = Expired events
# g = Generic commands (DEL, EXPIRE, etc.)
# l = List commands
# s = Set commands
# z = Sorted Set commands

# Subscribe to expired events (session cleanup, TTL processing)
redis-cli SUBSCRIBE __keyevent@0__:expired
```

```python
# Listen for expired keys — cleanup side effects
pubsub = redis.pubsub()
pubsub.psubscribe("__keyevent@0__:expired")

for message in pubsub.listen():
    if message["type"] == "pmessage":
        expired_key = message["data"].decode()
        if expired_key.startswith("session:"):
            session_id = expired_key.removeprefix("session:")
            cleanup_session(session_id)
```

---

### 14. How do you monitor Redis in production?

**A:**

```bash
# Redis INFO command — comprehensive stats
redis-cli INFO all
redis-cli INFO memory   # memory usage
redis-cli INFO stats    # command stats, evictions
redis-cli INFO replication  # replication status
redis-cli INFO persistence  # RDB/AOF status
redis-cli INFO clients  # connected clients

# Key metrics:
# used_memory_rss        — actual OS memory usage
# mem_fragmentation_ratio — > 1.5 means high fragmentation
# connected_clients      — alert if approaches maxclients
# blocked_clients        — clients waiting on BRPOP etc.
# evicted_keys           — alert if > 0 (memory pressure)
# keyspace_hits/misses   — hit rate = hits/(hits+misses)
# instantaneous_ops_per_sec — throughput
# latency_stats          — slow commands

# Slow log
redis-cli SLOWLOG GET 10   # last 10 slow commands
redis-cli SLOWLOG RESET

# Monitor commands in real time (dev only — never in prod)
redis-cli MONITOR

# Latency monitoring
redis-cli --latency -h redis
redis-cli --latency-history -h redis

# Memory analysis
redis-cli DEBUG SLEEP 0
redis-cli MEMORY USAGE key:42
redis-cli MEMORY DOCTOR   # recommendations
redis-cli MEMORY STATS
```

---

### 15. What is the difference between Redis and Memcached?

**A:**

| | Redis | Memcached |
|--|-------|---------|
| Data types | String, Hash, List, Set, ZSet, Stream, etc. | String only |
| Persistence | RDB + AOF | No |
| Replication | Yes | No (third-party) |
| Cluster | Yes | Consistent hashing (client-side) |
| Pub/Sub | Yes | No |
| Lua scripting | Yes | No |
| Transactions | Yes (MULTI/EXEC) | No |
| Threads | Single-threaded (I/O), multi-threaded (I/O since 6.0) | Multi-threaded |
| Memory efficiency | Slightly higher overhead | Slightly more efficient |
| Choose when | Need data structures, persistence, replication | Simple string cache, max throughput |

---

### 16. How do you handle Redis connection pooling in Python?

**A:**

```python
from redis import ConnectionPool, Redis, Sentinel

# Connection pool — share connections across threads/requests
pool = ConnectionPool(
    host="redis",
    port=6379,
    db=0,
    password="secret",
    max_connections=20,          # max simultaneous connections
    decode_responses=True,       # auto-decode bytes to str
    socket_timeout=5,            # socket read timeout
    socket_connect_timeout=2,    # connection timeout
    retry_on_timeout=True,
    health_check_interval=30,    # ping connections every 30s
)

redis = Redis(connection_pool=pool)

# FastAPI/Django — create pool once at startup
# DON'T create a new Redis() per request

# Async pool
from redis.asyncio import ConnectionPool as AsyncConnectionPool, Redis as AsyncRedis

async_pool = AsyncConnectionPool(
    host="redis", port=6379, max_connections=20, decode_responses=True
)
async_redis = AsyncRedis(connection_pool=async_pool)

async def get_user(user_id: int):
    return await async_redis.get(f"user:{user_id}")

# Sentinel-aware pool
sentinel = Sentinel([("sentinel1", 26379), ("sentinel2", 26379)], socket_timeout=0.1)
master = sentinel.master_for("mymaster", socket_timeout=0.1, password="secret")
```
