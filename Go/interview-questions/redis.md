# 🔴 Redis in Go — Interview Questions (Junior → Architect)

---

## 🟢 Junior Level

---

### 1. How do you connect to Redis with `go-redis`?

**A:**

```go
import "github.com/redis/go-redis/v9"

// Single node
rdb := redis.NewClient(&redis.Options{
    Addr:         "localhost:6379",
    Password:     "",
    DB:           0,
    PoolSize:     10,
    MinIdleConns: 5,
    MaxRetries:   3,
})

// Verify connection
ctx := context.Background()
if err := rdb.Ping(ctx).Err(); err != nil {
    log.Fatal("redis connect failed:", err)
}

// Cluster
rdb := redis.NewClusterClient(&redis.ClusterOptions{
    Addrs: []string{":7000", ":7001", ":7002"},
})

// Sentinel (HA)
rdb := redis.NewFailoverClient(&redis.FailoverOptions{
    MasterName:    "mymaster",
    SentinelAddrs: []string{":26379", ":26380", ":26381"},
})
```

---

### 2. What are the basic Redis data types and how do you use them in Go?

**A:**

```go
ctx := context.Background()

// String — cache, counters, flags
rdb.Set(ctx, "user:42:name", "Alice", 5*time.Minute)
val, _ := rdb.Get(ctx, "user:42:name").Result()
rdb.Incr(ctx, "page:views")
rdb.IncrBy(ctx, "score", 10)

// Hash — object fields
rdb.HSet(ctx, "user:42", "name", "Alice", "email", "alice@example.com")
rdb.HGet(ctx, "user:42", "name")
rdb.HGetAll(ctx, "user:42") // map[string]string
rdb.HIncrBy(ctx, "user:42", "points", 5)

// List — queues, feeds
rdb.LPush(ctx, "tasks", "task1", "task2") // push to front
rdb.RPush(ctx, "tasks", "task3")          // push to back
rdb.LPop(ctx, "tasks")                    // pop from front
rdb.BLPop(ctx, 10*time.Second, "tasks")  // blocking pop

// Set — unique items, membership
rdb.SAdd(ctx, "online:users", "42", "43", "44")
rdb.SIsMember(ctx, "online:users", "42")  // true/false
rdb.SMembers(ctx, "online:users")
rdb.SRem(ctx, "online:users", "42")

// Sorted Set — leaderboards, priority queues
rdb.ZAdd(ctx, "leaderboard", redis.Z{Score: 100, Member: "alice"})
rdb.ZAdd(ctx, "leaderboard", redis.Z{Score: 200, Member: "bob"})
rdb.ZRangeWithScores(ctx, "leaderboard", 0, -1) // ascending
rdb.ZRevRangeWithScores(ctx, "leaderboard", 0, 9) // top 10
rdb.ZScore(ctx, "leaderboard", "alice")           // 100
```

---

### 3. How do you implement caching with Redis in Go?

**A:**

```go
type Cache struct {
    rdb *redis.Client
}

func (c *Cache) GetUser(ctx context.Context, id string) (*User, error) {
    // Try cache first
    data, err := c.rdb.Get(ctx, "user:"+id).Bytes()
    if err == nil {
        var user User
        json.Unmarshal(data, &user)
        return &user, nil
    }
    if !errors.Is(err, redis.Nil) {
        return nil, err // real error
    }

    // Cache miss — fetch from DB
    user, err := db.GetUser(ctx, id)
    if err != nil {
        return nil, err
    }

    // Store in cache
    data, _ = json.Marshal(user)
    c.rdb.Set(ctx, "user:"+id, data, 5*time.Minute)

    return user, nil
}

func (c *Cache) InvalidateUser(ctx context.Context, id string) error {
    return c.rdb.Del(ctx, "user:"+id).Err()
}
```

---

### 4. How do you handle Redis errors and nil values?

**A:**

```go
val, err := rdb.Get(ctx, "key").Result()
if errors.Is(err, redis.Nil) {
    // Key doesn't exist — not an error, just a cache miss
    return nil, ErrNotFound
}
if err != nil {
    // Real error: connection refused, timeout, etc.
    return nil, fmt.Errorf("redis get: %w", err)
}
// val is the string value

// For typed commands
n, err := rdb.Incr(ctx, "counter").Result()

exists, err := rdb.Exists(ctx, "key1", "key2").Result() // returns count of existing keys

ttl, err := rdb.TTL(ctx, "key").Result()
if ttl == -1 { /* key exists but no TTL */ }
if ttl == -2 { /* key doesn't exist */ }
```

---

### 5. How do you use pipelines for batch operations?

**A:**

```go
// Without pipeline: 3 round trips
rdb.Set(ctx, "a", 1, 0)
rdb.Set(ctx, "b", 2, 0)
rdb.Set(ctx, "c", 3, 0)

// With pipeline: 1 round trip
pipe := rdb.Pipeline()
pipe.Set(ctx, "a", 1, 0)
pipe.Set(ctx, "b", 2, 0)
pipe.Set(ctx, "c", 3, 0)
_, err := pipe.Exec(ctx)

// Read results from pipeline
pipe = rdb.Pipeline()
getA := pipe.Get(ctx, "a")
getB := pipe.Get(ctx, "b")
pipe.Exec(ctx)

valA, _ := getA.Result()
valB, _ := getB.Result()

// TxPipeline — pipeline wrapped in MULTI/EXEC (atomic)
_, err = rdb.TxPipelined(ctx, func(pipe redis.Pipeliner) error {
    pipe.Incr(ctx, "counter")
    pipe.Expire(ctx, "counter", time.Hour)
    return nil
})
```

---

## 🟡 Mid Level

---

### 6. How do you implement a distributed lock with Redis?

**A:** Using the SET NX PX pattern (Redlock for multi-node):

```go
type RedisLock struct {
    rdb   *redis.Client
    key   string
    token string
    ttl   time.Duration
}

func NewLock(rdb *redis.Client, key string, ttl time.Duration) *RedisLock {
    return &RedisLock{rdb: rdb, key: "lock:" + key, token: uuid.New().String(), ttl: ttl}
}

func (l *RedisLock) Acquire(ctx context.Context) (bool, error) {
    // SET key token NX PX ttl_ms — atomic set-if-not-exists
    ok, err := l.rdb.SetNX(ctx, l.key, l.token, l.ttl).Result()
    return ok, err
}

// Release with Lua script — atomic check-and-delete
var releaseLua = redis.NewScript(`
    if redis.call("GET", KEYS[1]) == ARGV[1] then
        return redis.call("DEL", KEYS[1])
    else
        return 0
    end
`)

func (l *RedisLock) Release(ctx context.Context) error {
    _, err := releaseLua.Run(ctx, l.rdb, []string{l.key}, l.token).Result()
    return err
}

// Usage
lock := NewLock(rdb, "order:42", 30*time.Second)
acquired, err := lock.Acquire(ctx)
if err != nil || !acquired {
    return ErrLockNotAcquired
}
defer lock.Release(ctx)

// Critical section
processOrder(ctx, 42)
```

For production multi-node Redlock: use `go-redsync/redsync`.

---

### 7. How do you use Lua scripts in go-redis?

**A:** Lua scripts execute atomically on the Redis server — no race conditions between commands:

```go
// Define script once — EVALSHA reuses cached script
var incrementIfLessThan = redis.NewScript(`
    local current = redis.call("GET", KEYS[1])
    if current == false then
        current = 0
    else
        current = tonumber(current)
    end
    local limit = tonumber(ARGV[1])
    if current < limit then
        return redis.call("INCR", KEYS[1])
    else
        return -1
    end
`)

// Rate limiting: increment counter if below limit
result, err := incrementIfLessThan.Run(
    ctx, rdb,
    []string{"rate:user:42"},  // KEYS
    100,                        // ARGV[1] — limit
).Int()

if result == -1 {
    return ErrRateLimitExceeded
}

// Conditional get-or-set
var getOrSet = redis.NewScript(`
    local val = redis.call("GET", KEYS[1])
    if val == false then
        redis.call("SET", KEYS[1], ARGV[1], "PX", ARGV[2])
        return ARGV[1]
    end
    return val
`)
```

---

### 8. How do you implement pub/sub with go-redis?

**A:**

```go
// Publisher
func publishEvent(ctx context.Context, rdb *redis.Client, channel string, event any) error {
    data, err := json.Marshal(event)
    if err != nil {
        return err
    }
    return rdb.Publish(ctx, channel, data).Err()
}

// Subscriber
func subscribeToEvents(ctx context.Context, rdb *redis.Client) {
    pubsub := rdb.Subscribe(ctx, "orders", "payments")
    defer pubsub.Close()

    ch := pubsub.Channel()
    for {
        select {
        case msg := <-ch:
            fmt.Printf("channel=%s payload=%s\n", msg.Channel, msg.Payload)
            handleMessage(msg)
        case <-ctx.Done():
            return
        }
    }
}

// Pattern subscribe
pubsub := rdb.PSubscribe(ctx, "orders.*")
// Receives from orders.created, orders.cancelled, orders.shipped, etc.
```

**Redis pub/sub is fire-and-forget** — messages are not persisted. If a subscriber disconnects, it misses messages. For persistence, use Redis Streams.

---

### 9. How do you use Redis Streams?

**A:** Redis Streams provide a persistent, consumer-group-based message log:

```go
// Produce
msgID, err := rdb.XAdd(ctx, &redis.XAddArgs{
    Stream: "orders",
    MaxLen: 10000,     // trim to 10k messages
    Approx: true,      // approximate trim (faster)
    Values: map[string]any{
        "order_id":    "order-123",
        "customer_id": "cust-456",
        "total":       "99.99",
    },
}).Result()

// Create consumer group
rdb.XGroupCreateMkStream(ctx, "orders", "order-processors", "$") // $ = only new messages

// Consume
results, err := rdb.XReadGroup(ctx, &redis.XReadGroupArgs{
    Group:    "order-processors",
    Consumer: "worker-1",
    Streams:  []string{"orders", ">"},  // > = only undelivered messages
    Count:    10,
    Block:    5 * time.Second,
}).Result()

for _, stream := range results {
    for _, msg := range stream.Messages {
        if err := processMessage(ctx, msg); err != nil {
            // Don't ack — will be redelivered after visibility timeout
            continue
        }
        // Acknowledge processed message
        rdb.XAck(ctx, "orders", "order-processors", msg.ID)
    }
}

// Claim stale messages (from crashed workers)
stale, _ := rdb.XAutoClaim(ctx, &redis.XAutoClaimArgs{
    Stream:   "orders",
    Group:    "order-processors",
    Consumer: "worker-1",
    MinIdle:  5 * time.Minute,
    Start:    "0",
    Count:    10,
}).Result()
```

---

### 10. How do you implement rate limiting with Redis?

**A:**

```go
// Sliding window rate limiter using Lua script
var slidingWindowLua = redis.NewScript(`
    local key = KEYS[1]
    local limit = tonumber(ARGV[1])
    local window = tonumber(ARGV[2]) -- milliseconds
    local now = tonumber(ARGV[3])

    -- Remove old entries outside the window
    redis.call("ZREMRANGEBYSCORE", key, 0, now - window)

    -- Count current requests
    local count = redis.call("ZCARD", key)

    if count < limit then
        -- Add current request
        redis.call("ZADD", key, now, now)
        redis.call("PEXPIRE", key, window)
        return 1  -- allowed
    end
    return 0  -- denied
`)

func Allow(ctx context.Context, rdb *redis.Client, key string, limit int, window time.Duration) (bool, error) {
    now := time.Now().UnixMilli()
    result, err := slidingWindowLua.Run(ctx, rdb,
        []string{"rl:" + key},
        limit,
        window.Milliseconds(),
        now,
    ).Int()
    return result == 1, err
}

// Simple fixed window (simpler, less accurate)
func AllowFixed(ctx context.Context, rdb *redis.Client, key string, limit int64) (bool, error) {
    count, err := rdb.Incr(ctx, "rl:"+key).Result()
    if err != nil { return false, err }
    if count == 1 {
        rdb.Expire(ctx, "rl:"+key, time.Minute)
    }
    return count <= limit, nil
}
```

---

### 11. How do you implement a cache-aside with singleflight to prevent thundering herd?

**A:**

```go
import "golang.org/x/sync/singleflight"

type Cache struct {
    rdb   *redis.Client
    group singleflight.Group
}

func (c *Cache) GetProduct(ctx context.Context, id string) (*Product, error) {
    cacheKey := "product:" + id

    // Check cache
    data, err := c.rdb.Get(ctx, cacheKey).Bytes()
    if err == nil {
        var p Product
        json.Unmarshal(data, &p)
        return &p, nil
    }

    // Cache miss — use singleflight to collapse concurrent misses
    result, err, _ := c.group.Do(cacheKey, func() (any, error) {
        // Only ONE goroutine executes this, others wait and share the result
        product, err := db.GetProduct(ctx, id)
        if err != nil { return nil, err }

        data, _ := json.Marshal(product)
        c.rdb.Set(ctx, cacheKey, data, 5*time.Minute)
        return product, nil
    })
    if err != nil { return nil, err }
    return result.(*Product), nil
}
```

---

## 🔴 Senior Level

---

### 12. How do you handle Redis connection failures gracefully?

**A:**

```go
rdb := redis.NewClient(&redis.Options{
    Addr:            "redis:6379",
    MaxRetries:      3,
    MinRetryBackoff: 8 * time.Millisecond,
    MaxRetryBackoff: 512 * time.Millisecond,
    DialTimeout:     5 * time.Second,
    ReadTimeout:     3 * time.Second,
    WriteTimeout:    3 * time.Second,
    PoolTimeout:     4 * time.Second,
    PoolSize:        20,
})

// Circuit breaker pattern — degrade gracefully when Redis is down
type CacheWithFallback struct {
    rdb     *redis.Client
    healthy atomic.Bool
}

func (c *CacheWithFallback) Get(ctx context.Context, key string) ([]byte, error) {
    if !c.healthy.Load() {
        return nil, ErrCacheUnavailable // bypass Redis entirely
    }

    data, err := c.rdb.Get(ctx, key).Bytes()
    if err != nil && !errors.Is(err, redis.Nil) {
        c.healthy.Store(false)
        go c.healthCheck() // background reconnect probe
        return nil, ErrCacheUnavailable
    }
    return data, err
}

func (c *CacheWithFallback) healthCheck() {
    ticker := time.NewTicker(5 * time.Second)
    defer ticker.Stop()
    for range ticker.C {
        if err := c.rdb.Ping(context.Background()).Err(); err == nil {
            c.healthy.Store(true)
            return
        }
    }
}
```

---

### 13. How do you implement session storage with Redis?

**A:**

```go
type SessionStore struct {
    rdb *redis.Client
    ttl time.Duration
}

type Session struct {
    UserID    string    `json:"user_id"`
    Email     string    `json:"email"`
    Role      string    `json:"role"`
    CreatedAt time.Time `json:"created_at"`
    ExpiresAt time.Time `json:"expires_at"`
}

func (s *SessionStore) Create(ctx context.Context, session *Session) (string, error) {
    token := uuid.New().String()
    key := "session:" + token

    data, err := json.Marshal(session)
    if err != nil { return "", err }

    return token, s.rdb.Set(ctx, key, data, s.ttl).Err()
}

func (s *SessionStore) Get(ctx context.Context, token string) (*Session, error) {
    data, err := s.rdb.Get(ctx, "session:"+token).Bytes()
    if errors.Is(err, redis.Nil) {
        return nil, ErrSessionNotFound
    }
    if err != nil { return nil, err }

    var session Session
    return &session, json.Unmarshal(data, &session)
}

func (s *SessionStore) Refresh(ctx context.Context, token string) error {
    return s.rdb.Expire(ctx, "session:"+token, s.ttl).Err()
}

func (s *SessionStore) Delete(ctx context.Context, token string) error {
    return s.rdb.Del(ctx, "session:"+token).Err()
}

// Invalidate all sessions for a user (store reverse mapping)
func (s *SessionStore) InvalidateAll(ctx context.Context, userID string) error {
    tokens, _ := s.rdb.SMembers(ctx, "user:sessions:"+userID).Result()
    keys := make([]string, len(tokens))
    for i, t := range tokens {
        keys[i] = "session:" + t
    }
    keys = append(keys, "user:sessions:"+userID)
    return s.rdb.Del(ctx, keys...).Err()
}
```

---

## 🏛️ Architect Level

---

### 14. How do you design a Redis topology for high availability?

**A:**

**Redis Sentinel (HA for single master):**
```
Master → Replica 1
       → Replica 2

3 Sentinels monitor master; promote replica on failure
```

```go
rdb := redis.NewFailoverClient(&redis.FailoverOptions{
    MasterName:       "mymaster",
    SentinelAddrs:    []string{":26379", ":26380", ":26381"},
    SentinelPassword: sentinelPass,
    Password:         redisPass,
})
```

**Redis Cluster (sharding + HA):**
```
3 master shards × 1 replica each = 6 nodes
Each master owns a range of hash slots (16384 total)
```

```go
rdb := redis.NewClusterClient(&redis.ClusterOptions{
    Addrs:    []string{":7000", ":7001", ":7002", ":7003", ":7004", ":7005"},
    Password: redisPass,
    // Cross-slot operations (MGET, pipelines) must use hash tags
    // MGET "user:{42}:name" "user:{42}:email" — same slot guaranteed
})
```

**Design rules for Cluster:**
- Keys that must be in the same slot: use hash tags `{userId}:name`, `{userId}:email`
- MULTI/EXEC only works if all keys are in the same slot
- Lua scripts: all KEYS must be in the same slot

---

### 15. How do you monitor Redis in production?

**A:**

```go
// go-redis built-in hook for metrics
type MetricsHook struct {
    hits   prometheus.Counter
    misses prometheus.Counter
}

func (h *MetricsHook) ProcessHook(next redis.ProcessHook) redis.ProcessHook {
    return func(ctx context.Context, cmd redis.Cmder) error {
        start := time.Now()
        err := next(ctx, cmd)
        duration := time.Since(start)

        labels := prometheus.Labels{"cmd": cmd.Name()}
        redisCommandDuration.With(labels).Observe(duration.Seconds())

        if cmd.Name() == "get" {
            if errors.Is(cmd.Err(), redis.Nil) {
                h.misses.Inc()
            } else {
                h.hits.Inc()
            }
        }
        return err
    }
}

rdb.AddHook(&MetricsHook{})
```

**Key Redis metrics:**
```
redis_memory_used_bytes          — memory usage (alert near maxmemory)
redis_connected_clients          — client connections (alert near maxclients)
redis_keyspace_hits_total        — cache hits
redis_keyspace_misses_total      — cache misses (hit rate = hits/(hits+misses))
redis_commands_duration_seconds  — command latency p99
redis_evicted_keys_total         — evictions (bad: means memory pressure)
redis_rejected_connections_total — connection refused (maxclients reached)
```

**Alerting:**
- Hit rate < 80% → cache design issue
- Memory > 80% of maxmemory → scale up or tune eviction
- Evicted keys > 0 with volatile-lru → acceptable; with noeviction → critical
- Command latency p99 > 10ms → investigate slow commands (`SLOWLOG GET 10`)
