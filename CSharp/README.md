# C# — Learning Resources

This section contains notes and chapter summaries for C#-related books, focused on modern, idiomatic C# patterns with an emphasis on concurrency and asynchronous programming.

---

## Books

| Book | Author | Focus |
|------|--------|-------|
| [Concurrency in C# Cookbook, 2nd Ed.](concurrency-in-csharp-cookbook/README.md) | Stephen Cleary | async/await, Parallel, Rx, Dataflow, Channels |

---

## Key Themes Across C# Books

- **async/await first** — I/O-bound work should never block threads
- **Parallel for CPU** — `Parallel.ForEach`, PLINQ for data-parallel CPU work
- **Channels for pipelines** — `System.Threading.Channels` as the modern producer/consumer primitive
- **Cancellation everywhere** — `CancellationToken` should flow through every layer
- **Immutability reduces synchronization** — shared data that can't change needs no locks

---

## Related Sections

- [Go/concurrency-in-go](../Go/concurrency-in-go/README.md) — Same concurrency concepts in Go's goroutine/channel model
