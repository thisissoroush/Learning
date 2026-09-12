# 🔷 C# / .NET — Learning Resources

This section contains book summaries, chapter notes, and interview preparation materials for C# and the .NET ecosystem, with a strong emphasis on concurrency, async programming, and modern .NET patterns.

---

## 📚 Books

| Book | Author | Focus |
|------|--------|-------|
| [Concurrency in C# Cookbook, 2nd Ed.](concurrency-in-csharp-cookbook/README.md) | Stephen Cleary | async/await, Parallel, Rx, Dataflow, Channels |

---

## 🎯 Interview Questions

### Core Language

| Level | File | Focus |
|-------|------|-------|
| 🟢 Junior | [interview-questions/junior.md](interview-questions/junior.md) | OOP basics, value/ref types, collections, LINQ, syntax |
| 🟡 Mid | [interview-questions/mid.md](interview-questions/mid.md) | async/await, generics, DI, Span\<T\>, records, EF Core |
| 🔴 Senior | [interview-questions/senior.md](interview-questions/senior.md) | GC internals, ArrayPool, IO.Pipelines, source generators |
| 🏛️ Architect | [interview-questions/architect.md](interview-questions/architect.md) | CQRS/ES, multi-tenancy, resilience, zero-downtime, security |

### Framework & Library Specific

| Topic | File | Focus |
|-------|------|-------|
| 🌐 ASP.NET Core / Kestrel | [interview-questions/aspnetcore.md](interview-questions/aspnetcore.md) | Middleware, routing, auth, rate limiting, HTTP/2, Kestrel tuning |
| 🗄️ Entity Framework Core | [interview-questions/efcore.md](interview-questions/efcore.md) | DbContext, migrations, change tracking, compiled queries, multi-tenancy |
| 🔌 Dapper | [interview-questions/dapper.md](interview-questions/dapper.md) | Raw SQL mapping, TypeHandlers, dynamic queries, CQRS read side |
| 🚌 MassTransit | [interview-questions/masstransit.md](interview-questions/masstransit.md) | Consumers, sagas, outbox, retry, RabbitMQ, Azure Service Bus |

---

## 🔑 Key Themes Across C# / .NET

- **async/await first** — I/O-bound work should never block threads
- **Parallel for CPU** — `Parallel.ForEach`, PLINQ for data-parallel CPU work
- **Channels for pipelines** — `System.Threading.Channels` as the modern producer/consumer primitive
- **Cancellation everywhere** — `CancellationToken` should flow through every layer
- **Immutability reduces synchronization** — shared data that can't change needs no locks
- **Span\<T\> and Memory\<T\>** — zero-allocation slicing for high-performance code
- **Source generators** — compile-time code generation for AOT-friendly serialization and logging

---

## 🔗 Related Sections

- [Go/concurrency-in-go](../Go/concurrency-in-go/README.md) — Same concurrency concepts in Go's goroutine/channel model
- [Go/interview-questions](../Go/interview-questions/README.md) — Parallel interview prep for Go
