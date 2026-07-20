# Chapter 3: Asynchronous Streams

> *"IAsyncEnumerable<T> is the natural fit for sequences of data that arrive over time."*

---

## Core Concept

Asynchronous streams combine the best of two worlds: `async/await` (for non-blocking I/O) and `yield return` (for producing multiple values lazily). The result is `IAsyncEnumerable<T>` — a **pull-based, lazy, asynchronous sequence**.

```
Type Comparison Table:
─────────────────────────────────────────────────────────────────
Type                    | Single/Multi | Async | Push/Pull
──────────────────────────────────────────────────────────────────
T                        | Single       | No    | N/A
IEnumerable<T>           | Multiple     | No    | Pull (sync blocks)
Task<T>                  | Single       | Yes   | Pull
Task<IEnumerable<T>>     | Multiple     | Yes*  | Pull (all at once)
IAsyncEnumerable<T>      | Multiple     | Yes   | Pull (per item)
IObservable<T>           | Single/Multi | Yes   | PUSH
─────────────────────────────────────────────────────────────────
* Task<IEnumerable<T>> is async to start, but items are enumerated synchronously
```

**The key insight:** `IAsyncEnumerable<T>` is pull-based — the consumer controls when to ask for the next item, and each "ask" can be asynchronous.

---

## Why Not the Others?

**Why not `Task<T>`?** Only returns one value.

**Why not `IEnumerable<T>`?** Synchronous — blocks while fetching each item.

**Why not `Task<List<T>>`?** Must load *all* items before returning. No streaming.

**Why not `IObservable<T>`?** Push-based. Events flood the consumer at the source's pace — backpressure is complex. Observable is great for UI events; async streams are great for paged APIs, file reading, database cursors.

---

## Recipe 3.1 — Creating Asynchronous Streams

**Problem:** You need to return multiple values where each may require async work.

**Solution:** Return `IAsyncEnumerable<T>` and use `yield return` with `await`.

```csharp
// Basic async stream — mix of await and yield return
async IAsyncEnumerable<int> GetValuesAsync()
{
    await Task.Delay(1000);   // async work before first item
    yield return 10;

    await Task.Delay(1000);   // async work before second item
    yield return 13;
}

// Real-world: paged API that returns all items across multiple pages
async IAsyncEnumerable<string> GetAllResultsAsync(HttpClient client)
{
    int offset = 0;
    const int limit = 10;

    while (true)
    {
        // Async fetch of one page
        string json = await client.GetStringAsync(
            $"https://api.example.com/items?offset={offset}&limit={limit}");

        string[] items = ParseJson(json);

        // Yield each item from this page — synchronous between await calls
        foreach (string item in items)
            yield return item;   // no await here; items come out fast

        if (items.Length < limit)
            break;   // last page

        offset += limit;
    }
}
```

```
Paged API streaming visualization:
  Consumer asks for item 1
       ↓
  Method: fetch page 1 (await HTTP) → yield items 1-10 one by one
  Consumer asks for item 11
       ↓
  Method: fetch page 2 (await HTTP) → yield items 11-20 one by one
  ...
```

> 💡 Most items in an async stream come from the same page (synchronously). `IAsyncEnumerable<T>` is built on `ValueTask<T>` under the hood specifically to handle this efficiently — synchronous yields have zero allocation overhead.

---

## Recipe 3.2 — Consuming Asynchronous Streams

**Problem:** You need to process an `IAsyncEnumerable<T>`.

**Solution:** `await foreach`

```csharp
// Basic consumption
await foreach (string item in GetAllResultsAsync(client))
{
    Console.WriteLine(item);
}

// With async work in the loop body
await foreach (string item in GetAllResultsAsync(client))
{
    await SaveToDbAsync(item);   // async processing per item — totally fine!
}

// With ConfigureAwait(false) for library code
await foreach (string item in GetAllResultsAsync(client).ConfigureAwait(false))
{
    Console.WriteLine(item);
}
```

```
await foreach execution model:
  [await foreach starts]
       │
       ├── [await] get next item from IAsyncEnumerator
       │       (may be synchronous if already cached, or async if needs I/O)
       │
       ├── [execute loop body]
       │
       └── [repeat until enumeration complete]
            │
            └── [await] DisposeAsync() the enumerator
```

> 💡 The loop body can contain `await` calls — this is a major advantage over `IObservable<T>` subscriptions (which must be synchronous). `await foreach` will patiently wait for your async loop body before asking for the next item.

---

## Recipe 3.3 — Using LINQ with Async Streams

**Problem:** You want to filter, project, or aggregate an async stream using familiar LINQ operators.

**Solution:** `System.Linq.Async` NuGet package provides LINQ operators for `IAsyncEnumerable<T>`.

```
Naming conventions for async LINQ operators:
  Where        → filter with synchronous predicate
  WhereAwait   → filter with asynchronous predicate
  CountAsync   → terminal operator returning awaitable scalar
  CountAwaitAsync → terminal with async delegate, returns awaitable scalar
```

```csharp
// Synchronous Where still works on async streams
IAsyncEnumerable<int> evenValues =
    SlowRange().Where(value => value % 2 == 0);

// WhereAwait — predicate itself is async
IAsyncEnumerable<int> filtered = SlowRange().WhereAwait(async value =>
{
    bool shouldInclude = await CheckDatabaseAsync(value);
    return shouldInclude;
});

// SelectAwait — transform with async operation
IAsyncEnumerable<string> labels = GetIdsAsync().SelectAwait(async id =>
    await FetchLabelAsync(id));

// CountAsync — terminal operator
int count = await SlowRange().CountAsync(value => value % 2 == 0);

// CountAwaitAsync — terminal with async predicate
int count = await SlowRange().CountAwaitAsync(async value =>
{
    await Task.Delay(10);
    return value % 2 == 0;
});

// Convert any IEnumerable<T> to async stream to use WhereAwait, SelectAwait, etc.
IAsyncEnumerable<int> asyncStream = Enumerable.Range(1, 100).ToAsyncEnumerable();
```

> 💡 **NuGet:** `System.Linq.Async` for the operators above. `System.Interactive.Async` for additional operators.

---

## Recipe 3.4 — Cancellation with Async Streams

**Problem:** You need to cancel an async stream from outside the `await foreach`.

**Solution 1 — Break early** (no token needed):
```csharp
await foreach (int result in SlowRange())
{
    Console.WriteLine(result);
    if (result >= 8)
        break;   // simply stop consuming — the stream producer stops too
}
```

**Solution 2 — CancellationToken via parameter** (most common):
```csharp
// Producer: mark the token parameter with [EnumeratorCancellation]
async IAsyncEnumerable<int> SlowRange(
    [EnumeratorCancellation] CancellationToken token = default)
{
    for (int i = 0; i != 10; ++i)
    {
        await Task.Delay(i * 100, token);   // token respected here
        yield return i;
    }
}

// Consumer: pass token directly
using var cts = new CancellationTokenSource(TimeSpan.FromMilliseconds(500));
await foreach (int result in SlowRange(cts.Token))
    Console.WriteLine(result);
```

**Solution 3 — WithCancellation extension** (when you don't own the source):
```csharp
async Task ConsumeAsync(IAsyncEnumerable<int> items)
{
    using var cts = new CancellationTokenSource(500);
    await foreach (int result in items.WithCancellation(cts.Token))
        Console.WriteLine(result);
}
```

```
How [EnumeratorCancellation] works:
  IAsyncEnumerable<T> is defined (not yet running)
       │
  Consumer calls items.WithCancellation(token)
       │
  Compiler passes token to the [EnumeratorCancellation] parameter
       │
  Producer uses token internally → cooperative cancellation
       │
  OperationCanceledException thrown when token fires
```

> 💡 You can chain both `WithCancellation` and `ConfigureAwait(false)`:
> ```csharp
> await foreach (var item in items.WithCancellation(token).ConfigureAwait(false))
> ```

---

## Visual Summary

```
ASYNC STREAMS — WHEN TO USE WHAT
══════════════════════════════════════════════════════════════

Scenario                              Best Type
──────────────────────────────────────────────────────────────
One async result                      Task<T>
Many sync results                     IEnumerable<T>
Many async results, loaded at once    Task<List<T>>
Many async results, streamed          IAsyncEnumerable<T>  ←
Push events, time-based operators     IObservable<T>

PRODUCING: async IAsyncEnumerable<T> + yield return + await
CONSUMING: await foreach
COMPOSING: WhereAwait, SelectAwait (System.Linq.Async NuGet)
CANCELING: [EnumeratorCancellation] param or .WithCancellation()
```

---

*[← Chapter 2](02-async-basics.md) | [Back to Index](../README.md) | [Chapter 4 — Parallel Basics →](04-parallel-basics.md)*
