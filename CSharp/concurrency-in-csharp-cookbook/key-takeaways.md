# Key Takeaways — Concurrency in C# Cookbook, 2nd Edition

> Stephen Cleary · O'Reilly Media · 2019

---

## 🏆 The Big Ideas

### 1. Start at the Top, Not the Bottom
Most concurrency books teach threads first. This book deliberately starts with the highest-level abstractions (`async`/`await`, `Parallel`, `Channels`) and works down only when needed. You will write safer, cleaner code by defaulting to high-level APIs.

### 2. Concurrency Is Now a Requirement
Responsive UIs and scalable servers both need concurrency. With modern C# tooling, there's no excuse to avoid it. `async`/`await` makes asynchronous code *read like synchronous code*.

### 3. The Four Types of Concurrency
```
Asynchronous     → awaiting I/O without blocking threads
Parallel         → CPU-bound work on multiple cores simultaneously
Reactive (Rx)    → declaratively reacting to event streams over time
Dataflow         → pipelines where blocks process data asynchronously/in parallel
```
Most real apps combine all four. Use whichever fits the shape of the problem.

---

## ⚡ async / await Rules

| Rule | Why |
|------|-----|
| `async` all the way up the call stack | Mixing sync-over-async causes deadlocks |
| Never `.Wait()` or `.Result` on the UI thread | Deadlock guaranteed in one-thread contexts |
| Use `ConfigureAwait(false)` in library code | Avoids unnecessary context capture |
| Prefer `Task` return over `async void` | `async void` swallows exceptions; can't be awaited |
| `async void` is ONLY for event handlers | It's the sole legitimate use case |

```csharp
// ✅ Correct
public async Task DoWorkAsync()
{
    await SomeIoAsync().ConfigureAwait(false);
}

// ❌ Deadlock waiting to happen
public void DoWork()
{
    SomeIoAsync().Wait();   // blocks UI thread → awaiter can never resume
}
```

---

## 📊 Choose the Right Tool

```
PROBLEM                              SOLUTION
──────────────────────────────────────────────────────────────────
Make HTTP request / DB query         async/await + HttpClient/EF
Loop over data in parallel           Parallel.ForEach / PLINQ
React to events / mouse moves        System.Reactive (Rx)
Pipeline: download → parse → store   TPL Dataflow
Pass messages between threads        Channels (System.Threading.Channels)
Share reference data (read-mostly)   ImmutableDictionary / ImmutableList
Share mutable data across threads    ConcurrentDictionary
Synchronize async code               SemaphoreSlim (NOT lock)
Synchronize sync code                lock statement
```

---

## 🔄 Task Lifecycle Cheat Sheet

```
Task.FromResult(value)      → completed successfully (sync stub)
Task.FromException(ex)      → completed faulted (sync error stub)
Task.FromCanceled(token)    → completed canceled
Task.CompletedTask          → completed void (no result)
Task.Run(() => ...)         → runs on thread pool
Task.WhenAll(tasks)         → wait for ALL tasks; collect results
Task.WhenAny(tasks)         → wait for FIRST task to complete
TaskCompletionSource<T>     → manually control when a task completes
```

---

## 🌊 Asynchronous Streams Key Points

- `IAsyncEnumerable<T>` = pull-based, asynchronous sequence
- Consume with `await foreach`
- Produce with `async` + `yield return` (combine both!)
- Apply `ConfigureAwait(false)` on the `await foreach` itself
- Pass cancellation via `[EnumeratorCancellation] CancellationToken` + `WithCancellation()`
- Use `System.Linq.Async` NuGet for `WhereAwait`, `SelectAwait`, `CountAwaitAsync`, etc.

```csharp
// Perfect fit: paged API → IAsyncEnumerable
async IAsyncEnumerable<Item> GetAllItemsAsync(
    [EnumeratorCancellation] CancellationToken ct = default)
{
    int offset = 0;
    while (true)
    {
        var page = await FetchPageAsync(offset, ct);
        foreach (var item in page) yield return item;
        if (page.Count < PageSize) break;
        offset += page.Count;
    }
}
```

---

## ⛓️ Cancellation Pattern

```csharp
// 1. Source creates the token
using var cts = new CancellationTokenSource();
cts.CancelAfter(TimeSpan.FromSeconds(5));   // optional timeout

// 2. Token flows down through every layer
await DoWorkAsync(cts.Token);

// 3. Implementations accept and pass the token on
async Task DoWorkAsync(CancellationToken ct)
{
    await SomeApiAsync(ct);           // pass to all API calls
    ct.ThrowIfCancellationRequested(); // poll in CPU loops
}

// 4. Callers handle cancellation as a normal outcome
try { await DoWorkAsync(cts.Token); }
catch (OperationCanceledException) { /* expected */ }
```

**Linked tokens:** combine user-cancellation + timeout + your own trigger:
```csharp
using var linked = CancellationTokenSource.CreateLinkedTokenSource(userToken);
linked.CancelAfter(TimeSpan.FromSeconds(2));
await DoWorkAsync(linked.Token);
```

---

## 🏗️ Collections Decision Tree

```
Do items ever change?
├── NO  → Immutable collections (ImmutableList, ImmutableDictionary, …)
│          • Naturally thread-safe, share memory between versions
└── YES → Is it a key-value store?
          ├── YES → ConcurrentDictionary<K,V>
          └── NO  → Is it a producer/consumer pipe?
                    ├── Blocking threads OK → BlockingCollection<T>
                    ├── Async only          → Channel<T>  ← prefer this
                    └── Pipeline/mesh       → TPL Dataflow BufferBlock<T>
```

---

## 🔒 Synchronization Rules

**Three conditions that require synchronization — ALL must be true:**
1. Multiple things run concurrently
2. They access the same data
3. At least one writes

```
sync code   → lock (blocking)
async code  → SemaphoreSlim.WaitAsync() / AsyncLock (Nito.AsyncEx)
signal once → TaskCompletionSource<T>.TrySetResult()
signal many → AsyncManualResetEvent (Nito.AsyncEx)
throttle    → SemaphoreSlim(N) — limit concurrent operations to N
```

**Never hold a lock across an `await`!** Use `SemaphoreSlim` instead of `lock` for async code.

---

## 🧪 Testing Concurrency

```csharp
// ✅ async unit tests — supported by MSTest, xUnit, NUnit
[Fact]
public async Task MyMethod_ReturnsExpected()
{
    var result = await MyMethodAsync();
    Assert.Equal(expected, result);
}

// Test all three mock behaviors:
Task.FromResult(value)          // synchronous success
Task.FromException<T>(ex)       // synchronous failure  
Task.Yield() + return value     // forced asynchronous success

// System.Reactive: use TestScheduler to control virtual time
var scheduler = new TestScheduler();
// ... set up with scheduler ...
scheduler.Start();  // advance virtual time instantly — no real waiting!
```

---

## 🔁 Interop Quick Lookup

| From | To | How |
|------|----|-----|
| Task | Observable | `task.ToObservable()` |
| Observable | Task | `observable.FirstAsync()` / `LastAsync()` / `ToTask()` |
| Observable | `IAsyncEnumerable` | `observable.ToAsyncEnumerable()` |
| Dataflow block | Observable | `block.AsObservable()` |
| Observable | Dataflow block | `observable.Subscribe(block.AsObserver())` |
| APM (Begin/End) | Task | `Task.Factory.FromAsync(...)` |
| EAP (event-based) | Task | `TaskCompletionSource<T>` |
| Anything | Task | `TaskCompletionSource<T>` |

---

## 🚫 Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| `async void` (not event handler) | Exceptions are unobservable | Return `Task` |
| `task.Wait()` / `.Result` on UI thread | Deadlock | `await task` |
| `new Thread(...)` | Obsolete, wasteful | `Task.Run(...)` |
| `lock` with `await` inside | `lock` isn't re-entrant across awaits | `SemaphoreSlim` |
| `Task.WhenAny` for timeout | Doesn't actually cancel the operation | `CancellationToken` with timeout |
| Sync-over-async wrapper methods | Hidden deadlocks, thread pool starvation | Async all the way |
| Catching all exceptions, swallowing cancellation | Hides bugs | Rethrow `OperationCanceledException` |

---

## 📐 Functional Design Principles

Cleary applies functional programming ideas to concurrency:

- **Purity**: Each unit of work takes input → produces output, no side effects on shared state
- **Immutability**: Data that can't change never needs synchronization
- **Composition**: Build complex pipelines from small, independent, tested blocks

The less shared mutable state you have, the less synchronization you need.

---

## 🎯 Decision Flowchart: What Concurrency Tool?

```
Is the work I/O-bound?
  YES → async/await
  NO  → Is it CPU-bound?
          YES → How much data?
                  Lots   → Parallel.ForEach / PLINQ
                  Some   → Task.Run (single operation)
          NO  → Is it event-driven?
                  YES → System.Reactive (Rx)
                  NO  → Is it a pipeline?
                          YES → TPL Dataflow
                          NO  → producer/consumer?
                                  YES → Channels
```
