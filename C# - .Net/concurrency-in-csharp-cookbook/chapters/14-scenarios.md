# Chapter 14: Scenarios

> *"Mix and match concurrency techniques — use the best tool for each part of the problem."*

---

## Core Concept

Real-world applications combine multiple concurrency techniques. This chapter shows practical patterns that emerge when building complete concurrent systems.

---

## Recipe 14.1 — Initializing Shared Resources (Async Lazy)

Initialize a resource exactly once, even with concurrent callers.

```csharp
// Sync lazy (built-in)
static readonly Lazy<int> _sharedInt = new Lazy<int>(() => ComputeExpensive());
void Use() { int v = _sharedInt.Value; }  // computed once, cached forever

// Async lazy — Lazy<Task<T>>
static readonly Lazy<Task<int>> _sharedAsync = new Lazy<Task<int>>(
    () => Task.Run(async () =>
    {
        await Task.Delay(1000);   // async initialization
        return 42;
    }));

async Task UseAsync()
{
    int value = await _sharedAsync.Value;  // Task computed once, awaited many times
}

// Best option: AsyncLazy<T> from Nito.AsyncEx (retries on failure)
static readonly AsyncLazy<int> _bestOption = new AsyncLazy<int>(
    async () =>
    {
        await Task.Delay(1000);
        return 42;
    },
    AsyncLazyFlags.RetryOnFailure);   // re-runs factory if it throws

async Task UseBest()
{
    int value = await _bestOption;    // direct await supported
}
```

---

## Recipe 14.2 — System.Reactive Deferred Evaluation

Create a fresh observable for each subscriber (like a cold observable factory).

```csharp
// Without Defer: single observable shared by all subscribers
IObservable<int> shared = GetValueAsync().ToObservable();
// All subscribers get the same result

// With Defer: factory runs for each subscriber independently
IObservable<int> perSubscription = Observable.Defer(
    () => GetValueAsync().ToObservable());
// Each Subscribe() triggers a new call to GetValueAsync()

perSubscription.Subscribe(_ => { });   // calls GetValueAsync()
perSubscription.Subscribe(_ => { });   // calls GetValueAsync() again
```

---

## Recipe 14.3 — Asynchronous Data Binding

Expose async results via data binding in MVVM, without blocking the UI.

```csharp
// ViewModel using NotifyTask<T> (Nito.Mvvm.Async)
class MyViewModel
{
    public MyViewModel()
    {
        Data = NotifyTask.Create(LoadDataAsync());
    }

    public NotifyTask<string> Data { get; }

    private async Task<string> LoadDataAsync()
    {
        await Task.Delay(2000);
        return "Loaded!";
    }
}
```

```xml
<!-- XAML: bind to different states of the async operation -->
<StackPanel>
    <!-- Show while loading -->
    <TextBlock Text="Loading..."
               Visibility="{Binding Data.IsNotCompleted,
                   Converter={StaticResource BoolToVisibility}}"/>
    <!-- Show result when done -->
    <TextBlock Text="{Binding Data.Result}"
               Visibility="{Binding Data.IsSuccessfullyCompleted,
                   Converter={StaticResource BoolToVisibility}}"/>
    <!-- Show error message if faulted -->
    <TextBlock Text="Error occurred" Foreground="Red"
               Visibility="{Binding Data.IsFaulted,
                   Converter={StaticResource BoolToVisibility}}"/>
</StackPanel>
```

```
NotifyTask<T> Properties
  ├── IsNotCompleted      → true while running
  ├── IsSuccessfullyCompleted → true on success
  ├── IsFaulted           → true on exception
  ├── Result              → value (or default if not done)
  └── InnerException      → the exception (if faulted)
```

---

## Recipe 14.4 — Implicit State (AsyncLocal)

Pass context through call stacks without adding parameters everywhere.

```csharp
// Store operation-scoped context (like a correlation ID)
private static readonly AsyncLocal<Guid> _operationId = new AsyncLocal<Guid>();

async Task HandleRequestAsync()
{
    _operationId.Value = Guid.NewGuid();   // set at entry point
    await ProcessStepAsync();              // all downstream code can read it
}

async Task ProcessStepAsync()
{
    await Task.Delay(100);
    // Read anywhere in the async call chain:
    Trace.WriteLine($"Operation: {_operationId.Value}");
}
```

> ⚠️ Only store **immutable** data in `AsyncLocal<T>`. Mutable shared state leads to subtle bugs. For complex data, use `ImmutableStack<T>` wrapped in `AsyncLocal`.

> 💡 `AsyncLocal<T>` is the async-friendly replacement for `[ThreadStatic]`.

---

## Recipe 14.5 — Identical Sync and Async Code (Boolean Argument Hack)

When you must expose both synchronous and asynchronous APIs without duplicating logic.

```csharp
// Core method: single implementation, driven by 'sync' flag
private async Task<int> CoreAsync(bool sync)
{
    int value = 100;
    if (sync)
        Thread.Sleep(value);       // synchronous path
    else
        await Task.Delay(value);   // asynchronous path
    return value;
}

// Async API
public Task<int> GetValueAsync() => CoreAsync(sync: false);

// Sync API — safe ONLY because CoreAsync(true) always returns completed task
public int GetValue() => CoreAsync(sync: true).GetAwaiter().GetResult();
```

> ⚠️ Critical: when `sync: true`, the core method **must never** return an incomplete task. If it does, `GetResult()` will deadlock.

---

## Recipe 14.6 — Railway Programming with Dataflow

Use a discriminated union (success | failure) to flow errors alongside data instead of crashing blocks.

```csharp
// Instead of letting exceptions fault your block, carry them as data
record Result<T>(T Value = default, Exception Error = null)
{
    public bool IsSuccess => Error == null;
}

var safeBlock = new TransformBlock<Result<int>, Result<int>>(input =>
{
    if (!input.IsSuccess) return input;  // pass errors through unchanged
    try
    {
        return new Result<int>(Value: input.Value * 2);
    }
    catch (Exception ex)
    {
        return new Result<int>(Error: ex);   // convert exception to data
    }
});
```

---

## Recipe 14.7 — Throttling Progress Updates

Too many UI updates can hurt performance. Throttle progress notifications.

```csharp
// Approach 1: Use IProgress<T> — Progress<T> captures the context automatically
async Task DoWorkAsync(IProgress<int> progress = null)
{
    for (int i = 0; i <= 100; i++)
    {
        await Task.Delay(50);
        progress?.Report(i);
    }
}

// Approach 2: Use System.Reactive Throttle for rapid-fire updates
IObservable<int> progressStream = /* your observable */;
progressStream
    .Throttle(TimeSpan.FromMilliseconds(100))  // only report if stable for 100ms
    .ObserveOn(SynchronizationContext.Current)  // update UI thread
    .Subscribe(value => ProgressBar.Value = value);
```

---

## Putting It All Together — Typical Modern App Pattern

```
┌─────────────────────────────────────────────────────┐
│  UI Layer                                           │
│  • async/await for all I/O                         │
│  • Task.Run for CPU-bound work                     │
│  • NotifyTask for async data binding               │
│  • IProgress<T> for progress                       │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│  Business Logic Layer                               │
│  • Async methods with CancellationToken             │
│  • Channels/Dataflow for pipelines                 │
│  • Parallel.ForEach / PLINQ for CPU work           │
│  • AsyncLocal<T> for implicit context              │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│  Data / Infrastructure Layer                        │
│  • Async I/O APIs (HttpClient, EF Core, etc.)      │
│  • Immutable collections for shared reference data │
│  • ConcurrentDictionary for shared mutable cache   │
└─────────────────────────────────────────────────────┘
```

---

*[← Chapter 13](13-scheduling.md) | [Back to Index](../README.md)*
