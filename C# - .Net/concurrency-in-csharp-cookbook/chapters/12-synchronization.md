# Chapter 12: Synchronization

> *"You need synchronization when: multiple pieces of code run concurrently, access the same data, AND at least one writes."*

---

## Core Concept

Three conditions must ALL be true to require synchronization:
1. Multiple pieces of code run **concurrently**
2. They access the **same data**
3. At least one piece **writes** to that data

```
SYNCHRONIZATION TYPES
════════════════════════════════════════════
  COMMUNICATION    Signal from one piece of code to another
  DATA PROTECTION  Prevent corrupted reads/writes to shared state
```

---

## When Is Synchronization Needed?

```csharp
// ✅ NO sync needed — sequential async (even if resumes on different threads)
async Task Sequential()
{
    int x = 0;
    await Task.Delay(100);
    x++;           // only one thing runs at a time
    await Task.Delay(100);
    x--;
}

// ⚠️ DEPENDS ON CONTEXT — concurrent modifications
private int _value;
async Task Concurrent()
{
    Task t1 = ModifyAsync();
    Task t2 = ModifyAsync();  // running concurrently!
    await Task.WhenAll(t1, t2);
    // No sync needed IF context is UI/ASP.NET (one-at-a-time context)
    // Sync REQUIRED if running on threadpool (Task.Run)
}

// ❌ ALWAYS needs sync — threadpool parallelism with shared state
async Task BadCode()
{
    int value = 0;
    Task t1 = Task.Run(() => { value++; });  // concurrent on threadpool!
    Task t2 = Task.Run(() => { value++; });
    await Task.WhenAll(t1, t2);
    // value may be 1, not 2 — race condition!
}
```

---

## Recipe 12.1 — Blocking Locks

Use `lock` for synchronous code that shares data between threads.

```csharp
class Counter
{
    private readonly object _mutex = new object();  // private lock object
    private int _value;

    public void Increment()
    {
        lock (_mutex)
        {
            _value++;
        }
    }

    public int Value
    {
        get { lock (_mutex) { return _value; } }
    }
}
```

**Four rules for correct locking:**
1. 🔒 **Restrict visibility** — lock object must be `private`, never exposed outside class
2. 📝 **Document what it protects** — comment which fields/operations the lock covers
3. ✂️ **Minimize code under lock** — no blocking calls, no I/O while holding lock
4. 🚫 **Never call arbitrary code while locked** — no events, virtual methods, or delegates under lock

> ❌ Never `lock(this)`, `lock(typeof(T))`, or `lock("string")` — these are accessible externally and can deadlock.

---

## Recipe 12.2 — Async Locks

`lock` blocks the thread — incompatible with `await`. Use `SemaphoreSlim` instead.

```csharp
class AsyncCounter
{
    private readonly SemaphoreSlim _mutex = new SemaphoreSlim(1);  // max 1 at a time
    private int _value;

    public async Task IncrementAsync()
    {
        await _mutex.WaitAsync();    // async wait — doesn't block thread
        try
        {
            int old = _value;
            await Task.Delay(100);  // can await inside the lock safely
            _value = old + 1;
        }
        finally
        {
            _mutex.Release();        // always release in finally
        }
    }
}

// Nito.AsyncEx provides cleaner API:
class AsyncCounterEx
{
    private readonly AsyncLock _mutex = new AsyncLock();
    private int _value;

    public async Task IncrementAsync()
    {
        using (await _mutex.LockAsync())  // auto-releases on dispose
        {
            int old = _value;
            await Task.Delay(100);
            _value = old + 1;
        }
    }
}
```

---

## Recipe 12.3 — Blocking Signals

One thread waits for a notification from another thread.

```csharp
class Initializer
{
    private readonly ManualResetEventSlim _ready = new ManualResetEventSlim();
    private int _value;

    // Called from thread A
    public void Initialize()
    {
        _value = 42;
        _ready.Set();   // signal: "I'm done initializing"
    }

    // Called from thread B — blocks until initialized
    public int WaitForValue()
    {
        _ready.Wait();   // blocks calling thread
        return _value;
    }
}
```

> 💡 Use `ManualResetEventSlim` for one-time or resettable signals. If passing data between threads, prefer producer/consumer queues (Chapter 9).

---

## Recipe 12.4 — Async Signals

Like blocking signals, but the waiter doesn't block a thread.

```csharp
// One-time signal using TaskCompletionSource
class AsyncInitializer
{
    private readonly TaskCompletionSource<object> _ready =
        new TaskCompletionSource<object>();
    private int _value;

    public void Initialize()
    {
        _value = 42;
        _ready.TrySetResult(null);  // signal completion
    }

    public async Task<int> WaitForValueAsync()
    {
        await _ready.Task;   // async wait — no thread blocked
        return _value;
    }
}

// Resettable async signal — AsyncManualResetEvent (Nito.AsyncEx)
class Connection
{
    private readonly AsyncManualResetEvent _connected = new AsyncManualResetEvent();

    public async Task WaitUntilConnectedAsync()
    {
        await _connected.WaitAsync();
    }

    public void SetConnected(bool connected)
    {
        if (connected) _connected.Set();
        else           _connected.Reset();
    }
}
```

---

## Recipe 12.5 — Throttling

Limit how many concurrent operations run simultaneously.

```csharp
// Async throttling with SemaphoreSlim — e.g. max 10 concurrent HTTP calls
async Task<string[]> DownloadAllAsync(HttpClient client, IEnumerable<string> urls)
{
    using var semaphore = new SemaphoreSlim(10);  // max 10 concurrent

    Task<string>[] tasks = urls.Select(async url =>
    {
        await semaphore.WaitAsync();
        try
        {
            return await client.GetStringAsync(url);
        }
        finally
        {
            semaphore.Release();
        }
    }).ToArray();

    return await Task.WhenAll(tasks);
}

// Dataflow throttling
var block = new TransformBlock<int, int>(x => x * 2,
    new ExecutionDataflowBlockOptions { MaxDegreeOfParallelism = 10 });

// Parallel throttling
Parallel.ForEach(items, new ParallelOptions { MaxDegreeOfParallelism = 10 },
    item => Process(item));

// PLINQ throttling
items.AsParallel().WithDegreeOfParallelism(10).Select(x => x * 2);
```

---

## Quick Reference

```
NEED                          USE
────────────────────────────────────────────────────
Sync data protection          lock (blocking)
Async data protection         SemaphoreSlim / AsyncLock
Blocking cross-thread signal  ManualResetEventSlim
One-time async signal         TaskCompletionSource
Resettable async signal       AsyncManualResetEvent
Limit concurrency             SemaphoreSlim / MaxDegreeOfParallelism
```

---

*[← Chapter 11](11-functional-friendly-oop.md) | [Back to Index](../README.md) | [Chapter 13 — Scheduling →](13-scheduling.md)*
