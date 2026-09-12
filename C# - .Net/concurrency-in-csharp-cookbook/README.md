# Concurrency in C# Cookbook, 2nd Edition

**Author:** Stephen Cleary  
**Publisher:** O'Reilly Media (2019)  
**Language:** C#  
**Focus:** Asynchronous, Parallel, and Multithreaded Programming

---

## What This Book Is About

A practical cookbook for modern C# concurrency. Stephen Cleary skips the low-level threading primitives that every other book starts with, and instead leads with the *highest-level abstractions* — `async`/`await`, Parallel LINQ, TPL Dataflow, and System.Reactive — explaining when and why to reach for each tool.

The core insight: concurrency is now a *requirement* for modern applications (responsive UIs, scalable servers), and the modern .NET toolchain makes it achievable without expert-level knowledge of threading internals.

---

## Who Should Read This

- C# developers who need to write responsive UI applications
- Backend developers building scalable server-side code
- Anyone who has been "burned" by old-school multithreading and wants a better path
- Developers migrating synchronous codebases to async

**Assumed knowledge:** C# generics, LINQ, IEnumerable. No concurrency experience required.

---

## Concurrency Landscape (Quick Mental Map)

```
CONCURRENCY IN C#
════════════════════════════════════════════════════════════════════
  async / await          I/O-bound work, natural sequential style
  Parallel / PLINQ       CPU-bound data parallelism
  TPL Dataflow           Pipelines with async + parallel mix
  System.Reactive (Rx)   Event streams over time
  Channels               High-perf producer/consumer queues
  Immutable Collections  Shared data that never needs synchronization
════════════════════════════════════════════════════════════════════
```

---

## Chapters

| # | Title | Core Theme |
|---|-------|-----------|
| [01](chapters/01-concurrency-an-overview.md) | Concurrency: An Overview | The four forms of concurrency and when to use each |
| [02](chapters/02-async-basics.md) | Async Basics | `async`/`await` patterns, Task, error handling |
| [03](chapters/03-asynchronous-streams.md) | Asynchronous Streams | `IAsyncEnumerable<T>`, `await foreach` |
| [04](chapters/04-parallel-basics.md) | Parallel Basics | `Parallel.ForEach`, PLINQ, dynamic parallelism |
| [05](chapters/05-dataflow-basics.md) | Dataflow Basics | TPL Dataflow pipeline blocks |
| [06](chapters/06-system-reactive-basics.md) | System.Reactive Basics | Rx observables, events as streams |
| [07](chapters/07-testing.md) | Testing | Unit testing async, dataflow, and Rx code |
| [08](chapters/08-interop.md) | Interop | Bridging async, parallel, Rx, and dataflow |
| [09](chapters/09-collections.md) | Collections | Immutable, threadsafe, and producer/consumer collections |
| [10](chapters/10-cancellation.md) | Cancellation | `CancellationToken` everywhere |
| [11](chapters/11-functional-friendly-oop.md) | Functional-Friendly OOP | Async constructors, properties, events, disposal |
| [12](chapters/12-synchronization.md) | Synchronization | Locks, signals, and throttling |
| [13](chapters/13-scheduling.md) | Scheduling | `TaskScheduler`, `Task.Run`, context management |
| [14](chapters/14-scenarios.md) | Scenarios | Lazy init, MVVM data binding, implicit state |

---

## Key Takeaways

→ See [key-takeaways.md](key-takeaways.md) for the essential principles distilled from the entire book.

---

## NuGet Packages Referenced

| Package | Purpose |
|---------|---------|
| `System.Reactive` | Rx / System.Reactive observables |
| `System.Threading.Tasks.Dataflow` | TPL Dataflow blocks |
| `System.Threading.Channels` | High-performance producer/consumer |
| `System.Collections.Immutable` | Immutable collections |
| `System.Linq.Async` | LINQ operators for `IAsyncEnumerable<T>` |
| `Nito.AsyncEx` | `AsyncLock`, `AsyncManualResetEvent`, `AsyncContext` |
| `Nito.Mvvm.Async` | `NotifyTask<T>` for MVVM data binding |
| `Microsoft.Reactive.Testing` | `TestScheduler` for Rx unit tests |

---

## Related Books in This Repo

- [Concurrency in Go](../../Go/concurrency-in-go/README.md) — Same concepts, Go's goroutine/channel model
