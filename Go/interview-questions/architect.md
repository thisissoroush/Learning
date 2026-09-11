# 🏛️ Go — Architect-Level Interview Questions

---

## 1. How would you design a high-throughput event processing system in Go?

**A:** Key design decisions:

**Ingestion Layer:**
- Kafka or NATS for durable message ingestion
- Go's HTTP/gRPC server with bounded goroutine pools (avoid goroutine-per-request anti-pattern at scale)

**Processing:**
```
Kafka → Consumer Group → Channel → Worker Pool → Output Sink
```
- Use Go channels as in-process queues; keep them small (backpressure)
- Fan-out with multiple worker pools for parallel processing stages

**Backpressure:** Critical at every stage. If a downstream sink is slow:
```go
select {
case ch <- event:
default:
    metrics.Increment("dropped_events")
    // or: block with timeout
}
```

**State Management:**
- Stateless workers + external state (Redis, Postgres) for scalability
- Or use `sync.Map` / sharded maps for hot in-memory state

**Observability:** `prometheus/client_golang` for metrics, structured logging (`slog`/`zap`), distributed tracing (OpenTelemetry)

---

## 2. How do you approach microservices communication in a Go ecosystem?

**A:**

**Synchronous:** gRPC (protobuf, strongly typed, bidirectional streaming, generated clients)
```proto
service OrderService {
  rpc CreateOrder(CreateOrderRequest) returns (Order);
  rpc WatchOrders(WatchRequest) returns (stream Order);
}
```

**Asynchronous:** Kafka / NATS / RabbitMQ for event-driven patterns

**Service Mesh vs. Library:**
- Service mesh (Istio, Linkerd) — infrastructure-level mTLS, retries, circuit breaking
- Library (gRPC interceptors) — application-level, full control

**Resilience patterns in Go:**
- Circuit breaker: `sony/gobreaker`
- Retry with backoff: `cenkalti/backoff`
- Timeout: always propagate `context.Context` with deadline

**Service discovery:** Consul, Kubernetes DNS, or etcd with `go.etcd.io/etcd/client/v3`

---

## 3. What is your strategy for managing configuration in a large Go service fleet?

**A:**

**Layered configuration:**
1. Hardcoded defaults (in code)
2. Config files (YAML/TOML) — `viper` or `koanf`
3. Environment variables (12-factor app compliance)
4. Remote config (Consul, etcd, Kubernetes ConfigMap)

**Secrets:** Never in config files. Use Vault, AWS Secrets Manager, or Kubernetes Secrets, loaded at startup via the secrets SDK.

**Strongly typed config struct:**
```go
type Config struct {
    DB struct {
        DSN             string        `env:"DB_DSN"`
        MaxOpenConns    int           `env:"DB_MAX_OPEN" default:"25"`
    }
    HTTP struct {
        Port            int           `env:"HTTP_PORT" default:"8080"`
        ReadTimeout     time.Duration `env:"HTTP_READ_TIMEOUT" default:"30s"`
    }
}
```

**Hot reload:** Watch config sources and emit to a channel; consumers re-read atomically:
```go
atomic.StorePointer(&globalCfg, unsafe.Pointer(newCfg))
```

---

## 4. How do you design a caching layer in Go? What trade-offs do you consider?

**A:**

**Local (in-process) cache:**
- `sync.Map` or sharded `map` + `sync.RWMutex` for low-overhead reads
- LRU eviction: `hashicorp/golang-lru`
- TTL: `patrickmn/go-cache` or custom with a background ticker

**Distributed cache:** Redis via `go-redis/redis/v9`

**Design decisions:**
| Trade-off | Consideration |
|-----------|--------------|
| Cache-aside vs write-through | Write-through = consistency; cache-aside = simpler |
| TTL vs explicit invalidation | TTL = simpler; invalidation = fresher data |
| Thundering herd | Single-flight (`golang.org/x/sync/singleflight`) |
| Memory bound | Eviction policy (LRU vs LFU vs ARC) |

**Singleflight (critical for hot keys):**
```go
var g singleflight.Group

result, _, _ := g.Do(key, func() (interface{}, error) {
    return db.Get(key)
})
```
Collapses concurrent duplicate requests into one backend call.

---

## 5. How would you architect a Go service for zero-downtime deployments?

**A:**

**Application level:**
- Graceful shutdown (drain in-flight requests, finish async workers)
- Health endpoints: `/healthz` (liveness), `/readyz` (readiness)
- Readiness must return 503 during startup and drain — Kubernetes uses this to route traffic

**Deployment level:**
- Rolling deploys or blue/green in Kubernetes
- `PodDisruptionBudget` — ensure minimum replicas always running
- `preStop` hook — add artificial sleep before SIGTERM to let load balancer drain

**Database migrations:**
- Forward-compatible migrations only (never drop a column in the same deploy that removes its code)
- Migrate in a separate Job before rolling out the new binary

**Long-running connections (WebSocket, gRPC streams):**
- On SIGTERM: stop accepting new streams, drain existing streams within a timeout
- Expose a metric for active streams to make the drain observable

---

## 6. Discuss your approach to observability in Go services.

**A:** Three pillars:

**Metrics (Prometheus):**
```go
var requestDuration = prometheus.NewHistogramVec(
    prometheus.HistogramOpts{Name: "http_request_duration_seconds", Buckets: prometheus.DefBuckets},
    []string{"method", "path", "status"},
)
```
Instrument: latency (p50/p95/p99), error rate, saturation (goroutine count, queue depth), throughput.

**Logging (structured):**
```go
slog.Info("request completed",
    "method", r.Method,
    "path", r.URL.Path,
    "status", status,
    "duration_ms", elapsed.Milliseconds(),
    "trace_id", traceID,
)
```
Always include a trace ID for correlation.

**Tracing (OpenTelemetry):**
```go
ctx, span := tracer.Start(ctx, "db.query")
defer span.End()
span.SetAttributes(attribute.String("db.statement", query))
```
Propagate context across service boundaries; export to Jaeger or Tempo.

**Alerting:** Alert on symptoms (latency, error rate), not causes. Use SLOs as the anchor.

---

## 7. How do you handle distributed transactions in a Go microservices architecture?

**A:** Distributed transactions are hard — avoid 2PC (slow, fragile). Preferred patterns:

**Saga pattern:**
- Choreography: services emit events and react to others' events (loose coupling, harder to debug)
- Orchestration: a central saga orchestrator directs steps (easier to trace, single point)

**Go implementation:**
```go
type Saga struct {
    steps []SagaStep
}
type SagaStep struct {
    Execute     func(ctx context.Context) error
    Compensate  func(ctx context.Context) error
}

func (s *Saga) Run(ctx context.Context) error {
    executed := []int{}
    for i, step := range s.steps {
        if err := step.Execute(ctx); err != nil {
            // compensate in reverse
            for j := len(executed) - 1; j >= 0; j-- {
                s.steps[executed[j]].Compensate(ctx)
            }
            return err
        }
        executed = append(executed, i)
    }
    return nil
}
```

**Idempotency keys:** Every operation must be idempotent — retries on failures won't create duplicates.

**Outbox pattern:** Atomically write event + business record in the same DB transaction; a separate relay polls and publishes.

---

## 8. How do you scale Go services and what are the bottlenecks you watch for?

**A:**

**Horizontal scaling:**
- Go services are generally stateless → easy to scale horizontally
- Pin session state to Redis, not in-process
- Use consistent hashing if sharding by key

**Common bottlenecks:**

| Bottleneck | Signal | Fix |
|------------|--------|-----|
| GC pressure | High GC pause in pprof | Reduce allocations; use `sync.Pool`; tune `GOMEMLIMIT` |
| Lock contention | High `sync.Mutex` wait in pprof | Shard locks; use `RWMutex`; go lock-free |
| DB connection pool exhaustion | High wait time in DB metrics | Tune `SetMaxOpenConns`; add read replicas |
| Goroutine leak | Growing `runtime.NumGoroutine()` | Audit channel patterns; use context cancellation |
| Network saturation | High bytes/s, retries | Batching; compression; connection pooling |

---

## 9. How do you design Go packages and project layout at scale?

**A:**

**Package design principles:**
- Packages should have a single, clear purpose
- Accept interfaces, return concrete types (or interfaces when polymorphism is needed)
- Avoid cyclic imports — indicates design smell
- `internal/` package — restricts use to the parent module

**Project layout (large service):**
```
myservice/
├── cmd/
│   └── server/main.go       # entry point
├── internal/
│   ├── domain/              # business logic, no external deps
│   ├── repository/          # DB access
│   ├── handler/             # HTTP/gRPC handlers
│   └── service/             # application services
├── pkg/                     # reusable, importable packages
├── proto/                   # protobuf definitions
└── migrations/              # DB migrations
```

**Dependency rule:** `domain` knows nothing of `repository` or `handler`. Handlers depend on service interfaces. This enables testing and replaceability.

---

## 10. How do you approach API versioning in a Go service?

**A:**

**REST:**
- URL versioning: `/v1/users`, `/v2/users` — most explicit, easiest to route
- Header versioning: `Accept: application/vnd.myapi.v2+json` — cleaner URLs, harder to test in browser

**gRPC:**
- Package versioning in protobuf: `package myservice.v2`
- Additive-only changes to v1 (backward compatible); new major version for breaking changes

**Deprecation strategy:**
1. Add new endpoint/method alongside old
2. Announce deprecation (response header: `Deprecation: true`, `Sunset: Sat, 01 Jan 2026`)
3. Monitor usage metrics for the old endpoint
4. Remove only after usage drops to zero or deadline passes

**In Go — routing versioned handlers:**
```go
v1 := r.PathPrefix("/v1").Subrouter()
v1.HandleFunc("/users", v1Handler.ListUsers)

v2 := r.PathPrefix("/v2").Subrouter()
v2.HandleFunc("/users", v2Handler.ListUsers)
```
