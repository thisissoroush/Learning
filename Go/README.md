# 🐹 Go — Learning Resources

This section contains book summaries, chapter notes, and interview preparation materials for Go — covering language fundamentals, concurrency, web frameworks, ORMs, messaging, and production patterns.

---

## 📚 Books

| Book | Author | Focus |
|------|--------|-------|
| [The Go Programming Language](the-go-programming-language/README.md) | Donovan & Kernighan | Language fundamentals, data structures, interfaces, concurrency |
| [Concurrency in Go](concurrency-in-go/README.md) | Katherine Cox-Buday | Goroutines, channels, sync primitives, patterns, scheduler |

---

## 🎯 Interview Questions

### Core Language

| Level | File | Focus |
|-------|------|-------|
| 🟢 Junior | [interview-questions/junior.md](interview-questions/junior.md) | Syntax, types, goroutines, channels, interfaces |
| 🟡 Mid | [interview-questions/mid.md](interview-questions/mid.md) | Goroutine leaks, select, sync, context, testing, modules |
| 🔴 Senior | [interview-questions/senior.md](interview-questions/senior.md) | GC, pprof, memory model, generics, worker pools, escape analysis |
| 🏛️ Architect | [interview-questions/architect.md](interview-questions/architect.md) | Event systems, gRPC, config, caching, scaling, multi-region |

### Web Frameworks

| Topic | File | Focus |
|-------|------|-------|
| 🌐 Gin | [interview-questions/gin.md](interview-questions/gin.md) | Routing, middleware, binding, auth, graceful shutdown, performance |
| 🌿 Echo & Chi | [interview-questions/echo-chi.md](interview-questions/echo-chi.md) | Echo context/validation, Chi stdlib-compatible handlers, framework choice |

### Data Access

| Topic | File | Focus |
|-------|------|-------|
| 🐘 GORM | [interview-questions/gorm.md](interview-questions/gorm.md) | Models, CRUD, associations, hooks, scopes, migrations |
| 🔧 SQLC | [interview-questions/sqlc.md](interview-questions/sqlc.md) | Code generation, type-safe queries, transactions, batch inserts |
| 🔴 Redis | [interview-questions/redis.md](interview-questions/redis.md) | Caching, pub/sub, Streams, distributed locks, Lua scripts, Sentinel/Cluster |

### Communication & Messaging

| Topic | File | Focus |
|-------|------|-------|
| 📡 gRPC | [interview-questions/grpc.md](interview-questions/grpc.md) | Proto definitions, streaming, interceptors, deadlines, mTLS, buf |
| 📬 Messaging | [interview-questions/messaging.md](interview-questions/messaging.md) | Kafka (franz-go), NATS/JetStream, Asynq, outbox pattern, DLQ |

### Tooling & Infrastructure

| Topic | File | Focus |
|-------|------|-------|
| 💉 Wire & Fx | [interview-questions/wire-fx.md](interview-questions/wire-fx.md) | Compile-time DI (Wire), runtime DI (Fx), lifecycle management |
| 🌿 Viper | [interview-questions/viper.md](interview-questions/viper.md) | Config from files/env/remote, hot reload, secrets, multi-env |
| 🧪 Testing | [interview-questions/testing.md](interview-questions/testing.md) | testify, mockery, testcontainers, fuzzing, benchmarks, build tags |

---

## 🔑 Key Themes Across Go Books

- **Concurrency via goroutines and channels** — communicate by sharing memory, not share memory to communicate
- **Interfaces for composition** — small, focused interfaces over inheritance
- **Error as values** — explicit error handling, wrapping with `%w`
- **Context for cancellation** — propagate `context.Context` across all I/O
- **Simplicity over cleverness** — readable code is maintainable code

---

## 🔗 Related Sections

- [C# - .Net/interview-questions](../C%23%20-%20.Net/interview-questions/README.md) — Parallel interview prep for .NET
