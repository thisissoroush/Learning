# Chapter 11: Functional-Friendly OOP

> *"Async is an implementation detail. The interface returns Task; whether it uses async/await is up to the implementation."*

---

## Core Concept

Async programming is **functional** in nature — it clashes with traditional OOP patterns like constructors, properties, and events. This chapter provides solutions for each friction point.

```
FRICTION POINTS & SOLUTIONS
════════════════════════════════════════════════════════
  async interface methods   → Return Task (no async keyword needed)
  async constructors        → Async factory method pattern
  async properties          → Method (if recalculated) or AsyncLazy<T>
  async events              → Deferral pattern
  async disposal            → IAsyncDisposable + await using
```

---

## Recipe 11.1 — Async Interfaces and Inheritance

`async` is an implementation detail — interfaces return `Task`, implementations use `async`.

```csharp
// Interface: return Task, no async keyword
interface IMyService
{
    Task<int> GetValueAsync();
    Task ProcessAsync();
}

// Async implementation
class AsyncImpl : IMyService
{
    public async Task<int> GetValueAsync()
    {
        await Task.Delay(100);
        return 42;
    }
    public async Task ProcessAsync() { await Task.Delay(50); }
}

// Synchronous implementation (still valid — returns completed task)
class SyncImpl : IMyService
{
    public Task<int> GetValueAsync() => Task.FromResult(42);
    public Task ProcessAsync() => Task.CompletedTask;
}

// Consumer: awaits the Task, doesn't care if impl is sync or async
async Task Use(IMyService svc)
{
    int value = await svc.GetValueAsync();
}
```

---

## Recipe 11.2 — Async Construction: Factories

Constructors can't be `async`. Use the **async factory method** pattern.

```csharp
class MyResource
{
    // Constructor is private — cannot be misused
    private MyResource() { }

    private async Task<MyResource> InitializeAsync()
    {
        await Task.Delay(500);  // async initialization
        return this;
    }

    // Only way to create an instance — fully initialized
    public static Task<MyResource> CreateAsync()
    {
        var instance = new MyResource();
        return instance.InitializeAsync();
    }

    public void DoWork() { /* safe to call — fully initialized */ }
}

// Usage — you can never get an uninitialized instance
MyResource res = await MyResource.CreateAsync();
res.DoWork();
```

> 💡 This is the **preferred** pattern because there's no way to get an uninitialized instance.

---

## Recipe 11.3 — Async Construction: Initialization Pattern (for DI)

When reflection-based DI/IoC must create the instance, use the **Asynchronous Initialization Pattern**.

```csharp
// Marker interface
public interface IAsyncInitialization
{
    Task Initialization { get; }
}

// Implementation
class MyService : IMyService, IAsyncInitialization
{
    public MyService()
    {
        Initialization = InitializeAsync();
    }

    public Task Initialization { get; }

    private async Task InitializeAsync()
    {
        await Task.Delay(500);  // async setup
    }
}

// DI consumer: check and await initialization
var svc = container.Resolve<IMyService>();
if (svc is IAsyncInitialization asyncSvc)
    await asyncSvc.Initialization;
svc.DoWork();   // safe — fully initialized
```

---

## Recipe 11.4 — Async Properties

Properties cannot be `async`. Choose based on semantics:

```csharp
// ❌ Wrong: "async property" — doesn't compile
// public async Task<int> Value { async get { ... } }

// ✅ Option A: If value is recalculated each time → make it a METHOD
public async Task<int> GetValueAsync()
{
    await Task.Delay(100);
    return 42;
}

// ✅ Option B: If value is computed once and cached → use AsyncLazy<T>
public AsyncLazy<int> Value { get; } = new AsyncLazy<int>(async () =>
{
    await Task.Delay(100);
    return 42;
});

// Consume:
int v = await instance.Value;   // computed once, cached forever
```

---

## Recipe 11.5 — Async Events

Two kinds of events need different treatment:

```
Notification events (button click, etc.)
  → Handlers can be async void — sender doesn't care when they finish
  → No special code needed

Command events (lifecycle hooks, etc.)
  → Sender needs to WAIT for handlers to complete
  → Use the Deferral pattern
```

```csharp
// Event args supporting deferrals (from Nito.AsyncEx)
public class MyEventArgs : EventArgs, IDeferralSource
{
    private readonly DeferralManager _deferrals = new DeferralManager();
    public IDisposable GetDeferral() => _deferrals.DeferralSource.GetDeferral();
    internal Task WaitForDeferralsAsync() => _deferrals.WaitForDeferralsAsync();
}

// Raising the event — awaits all async handlers
public event EventHandler<MyEventArgs> MyCommandEvent;
private async Task RaiseMyCommandEventAsync()
{
    var handler = MyCommandEvent;
    if (handler == null) return;
    var args = new MyEventArgs();
    handler(this, args);
    await args.WaitForDeferralsAsync();   // wait for all async handlers
}

// Async event handler uses a deferral
async void Handler(object sender, MyEventArgs args)
{
    using IDisposable deferral = args.GetDeferral();  // signals "I'm async"
    await Task.Delay(1000);
    // deferral disposed here → signals completion
}
```

---

## Recipe 11.6 — Async Disposal

Two approaches for types that need cleanup when disposed:

```csharp
// Approach A: Dispose = cancellation (cancel ongoing operations, don't wait)
class MyService : IDisposable
{
    private readonly CancellationTokenSource _cts = new CancellationTokenSource();

    public async Task<int> ComputeAsync()
    {
        await Task.Delay(2000, _cts.Token);
        return 42;
    }

    public void Dispose() => _cts.Cancel();  // cancels in-flight ops
}

// Approach B: IAsyncDisposable (wait for cleanup to complete)
class MyAsyncService : IAsyncDisposable
{
    public async ValueTask DisposeAsync()
    {
        await Task.Delay(500);  // async cleanup (flush buffers, close connections)
    }
}

// Consuming IAsyncDisposable:
await using var svc = new MyAsyncService();
// ... use svc ...
// DisposeAsync called and awaited automatically

// With ConfigureAwait(false):
var svc2 = new MyAsyncService();
await using (svc2.ConfigureAwait(false))
{
    // ...
}
```

---

*[← Chapter 10](10-cancellation.md) | [Back to Index](../README.md) | [Chapter 12 — Synchronization →](12-synchronization.md)*
