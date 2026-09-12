# Chapter 1: Concurrency — An Overview

> *"Concurrency is now a requirement. Users expect fully responsive interfaces, and server applications must scale to unprecedented levels."*

---

## Core Concept

Before writing a single line of concurrent code, you need to master the vocabulary. The biggest source of confusion in concurrency is that people use the same words to mean different things. This chapter is your dictionary — and your map of the entire landscape.

---

## 1.1 The Vocabulary of Concurrency

These four terms are frequently confused. Learn the precise distinctions:

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONCURRENCY VOCABULARY                       │
├─────────────────┬───────────────────────────────────────────────┤
│ CONCURRENCY     │ Doing more than one thing at a time           │
│                 │ (the umbrella term for all the others)        │
├─────────────────┼───────────────────────────────────────────────┤
│ MULTITHREADING  │ Using multiple threads of execution           │
│                 │ (one form of concurrency, not the only one)   │
├─────────────────┼───────────────────────────────────────────────┤
│ PARALLEL        │ Dividing work across multiple threads that run │
│ PROCESSING      │ simultaneously on multiple CPU cores          │
├─────────────────┼───────────────────────────────────────────────┤
│ ASYNC           │ Using futures/callbacks to avoid unnecessary  │
│ PROGRAMMING     │ threads (I/O doesn't need a thread to wait!)  │
├─────────────────┼───────────────────────────────────────────────┤
│ REACTIVE        │ Declarative programming where your app reacts │
│ PROGRAMMING     │ to events (push model, event streams)         │
└─────────────────┴───────────────────────────────────────────────┘
```

> 💡 Most developers hear "concurrency" and immediately think "multithreading." This is only one of four distinct approaches — and often not the best choice.

---

## 1.2 The Four Kinds of Concurrency

### Kind 1: Asynchronous Programming

The most important form for modern .NET. The core idea: **I/O doesn't need a thread to sit and wait**.

```
WITHOUT async (blocking):
  Thread → starts HTTP request → BLOCKED, waiting for response → continues
  (thread is idle the whole time the network is in flight!)

WITH async (non-blocking):
  Thread → starts HTTP request → returns to do other work
  [network in flight — no thread consumed]
  Thread pool thread → response arrives → continues where we left off
```

```csharp
// SYNCHRONOUS — wastes a thread while waiting
string data = httpClient.GetString(url);  // thread blocked here

// ASYNCHRONOUS — releases the thread while waiting
string data = await httpClient.GetStringAsync(url);  // thread free!
```

**Two benefits:**
- **GUI apps**: UI thread stays responsive while work happens in background
- **Server apps**: can handle 10x more requests with the same threads

---

### Kind 2: Parallel Programming

Use all your CPU cores. Split independent CPU-bound work across multiple threads.

```
Sequential (1 core):
  [Task A ──────────] [Task B ──────────] [Task C ──────────]
  Time: 3 units

Parallel (3 cores):
  Core 1: [Task A ──────────]
  Core 2: [Task B ──────────]
  Core 3: [Task C ──────────]
  Time: 1 unit  ← 3× faster!
```

```csharp
// Rotate 1000 matrices in parallel
Parallel.ForEach(matrices, matrix => matrix.Rotate(degrees));

// PLINQ version
var results = values.AsParallel().Select(v => ComputeExpensive(v));
```

> ⚠️ **Only use parallel on CPU-bound work.** Parallelizing I/O-bound work is an async job. Parallelizing things that aren't independent creates race conditions.

---

### Kind 3: Reactive Programming (System.Reactive / Rx)

Treat **streams of events** like streams of data. Think of it as LINQ-to-Events.

```
Traditional event handling:
  button.Click += (s, e) => { ... }  ← imperative, hard to compose

Reactive:
  buttonClicks                        ← an observable stream
    .Throttle(500ms)                  ← debounce
    .Select(e => e.Position)          ← transform
    .Subscribe(pos => Update(pos))    ← react
```

```csharp
// Observable stream of mouse moves, throttled to fire only
// when mouse stops moving for 1 second
Observable.FromEventPattern<MouseEventArgs>(this, "MouseMove")
    .Select(e => e.EventArgs.GetPosition(this))
    .Throttle(TimeSpan.FromSeconds(1))
    .Subscribe(pos => Trace.WriteLine(pos));
```

**Key characteristics:**
- **Push model** — events arrive and travel through the query by themselves
- **LINQ operators** available: `Where`, `Select`, `GroupBy`, etc.
- **Time operators** unique to Rx: `Throttle`, `Sample`, `Buffer`, `Window`, `Timeout`

---

### Kind 4: Dataflow (TPL Dataflow)

Build a **mesh of processing blocks** and pipe data through it.

```
Input → [Download Block] → [Parse Block] → [Process Block] → Output
              ↓parallel          ↓parallel
```

```csharp
var downloadBlock = new TransformBlock<string, string>(
    url => httpClient.GetStringAsync(url));

var parseBlock = new TransformBlock<string, MyData>(
    raw => Parse(raw));

downloadBlock.LinkTo(parseBlock,
    new DataflowLinkOptions { PropagateCompletion = true });
```

**Use dataflow when:**
- You have a sequence of processes to apply to data
- You want built-in buffering and backpressure
- You want some stages to run in parallel automatically

---

## 1.3 The Decision Map

```
You need to do something concurrently. Which kind?
                           │
           ┌───────────────┴───────────────┐
           ▼                               ▼
    Is it CPU-bound?               Is it I/O-bound?
    (computation)                  (network, disk, DB)
           │                               │
           ▼                               ▼
    PARALLEL PROCESSING             ASYNC PROGRAMMING
    Parallel.ForEach / PLINQ        async / await
           │
           ▼
    Is the structure a pipeline
    or mesh with multiple stages?
           │
           ▼
    TPL DATAFLOW
           │
           ▼
    Are you reacting to a
    stream of events over time?
           │
           ▼
    SYSTEM.REACTIVE (Rx)
```

---

## 1.4 Multithreading — The Low-Level Reality

All the above are built on top of threads and the thread pool. Understanding the basics helps you debug problems.

```
.NET Process
├── Thread Pool (maintained by .NET runtime)
│   ├── Worker Thread 1  → processes tasks
│   ├── Worker Thread 2  → processes tasks
│   └── Worker Thread N  → auto-scales as needed
│
└── Special Threads
    ├── UI Thread (WPF/WinForms/MAUI) ← only 1, must not block
    └── Main Thread (Console apps)
```

> ⚠️ **Never use `new Thread()` in modern code.** The moment you write `new Thread()`, you have legacy code. Use `Task.Run()` instead — it uses the thread pool efficiently.

> ⚠️ **Never use `BackgroundWorker`.** It's been superseded by `async`/`await`. Ignore it exists.

---

## 1.5 Collections for Concurrent Code

Two categories of collections are designed for concurrent use:

```
IMMUTABLE COLLECTIONS (System.Collections.Immutable NuGet)
  → Cannot be modified — inherently threadsafe
  → ImmutableList<T>, ImmutableDictionary<K,V>, ImmutableStack<T>, etc.
  → Write operations return a NEW collection (original unchanged)
  → Share memory between instances for efficiency

CONCURRENT COLLECTIONS (System.Collections.Concurrent, built-in)
  → Mutable, threadsafe via fine-grained locking / lock-free techniques
  → ConcurrentDictionary<K,V>, ConcurrentQueue<T>, ConcurrentStack<T>
  → Thread-safe reads and writes without external locks
```

---

## 1.6 Modern Design Philosophy

The best concurrent code is **functional** in nature:

```
FUNCTIONAL PRINCIPLES FOR CONCURRENT CODE
══════════════════════════════════════════

① PURITY — avoid side effects
  Each piece takes inputs and produces outputs.
  No shared state. No global variables.
  Pure functions are trivially concurrent.

② IMMUTABILITY — data that can't change
  Immutable data never needs synchronization.
  No deadlocks. No race conditions. No corruption.
  Modern C# records and init-only properties help here.

③ COMPOSABILITY — small pieces that combine
  async methods compose with await
  Rx operators compose with LINQ
  Dataflow blocks compose with LinkTo
```

---

## 1.7 Technology Reference Card

| Technology | NuGet Package | Best For |
|------------|---------------|----------|
| `async`/`await` | Built into .NET | I/O-bound operations |
| `Task Parallel Library` | Built into .NET | CPU-bound parallel work |
| `System.Reactive` | `System.Reactive` | Event streams, time-based operations |
| `TPL Dataflow` | `System.Threading.Tasks.Dataflow` | Processing pipelines/meshes |
| Immutable Collections | `System.Collections.Immutable` | Shared, rarely-changing data |
| Concurrent Collections | Built into .NET | Threadsafe mutable collections |
| Channels | `System.Threading.Channels` | High-perf async producer/consumer |

---

## Visual Summary

```
THE CONCURRENCY LANDSCAPE IN .NET
══════════════════════════════════════════════════════════════════

  ASYNC/AWAIT  ─────── I/O-bound ──── "Release thread while waiting"
       │
       ├── Task<T>          → single future value
       ├── IAsyncEnumerable → stream of async values
       └── ValueTask<T>     → performance-optimized single value

  PARALLEL  ────────── CPU-bound ──── "Use all cores"
       │
       ├── Parallel.ForEach → data parallelism
       ├── Parallel.Invoke  → task parallelism
       └── PLINQ            → LINQ parallel queries

  REACTIVE (Rx) ─────── Event streams ── "React as events arrive"
       │
       └── IObservable<T>  → push-based event stream

  DATAFLOW ─────────── Pipelines ──── "Mesh of processing blocks"
       │
       ├── TransformBlock   → one-in, one-out
       ├── ActionBlock      → consumer (no output)
       └── BufferBlock      → queue

  ALL BUILT ON: Thread Pool + Tasks + CancellationToken
```

---

*[Back to Index](../README.md) | [Chapter 2 — Async Basics →](02-async-basics.md)*
