# Chapter 10: Cancellation

> *"Cancellation is cooperative — it can be requested but not enforced. Code must opt in."*

---

## Core Concept

The .NET cancellation system has two sides:
- **`CancellationTokenSource`** — the *sender* that issues cancellation
- **`CancellationToken`** — the *receiver* that observes and responds

Cancelled code throws `OperationCanceledException` — this is the contract.

```
CANCELLATION FLOW
══════════════════════════════════════════════════
  CancellationTokenSource.Cancel()
           ↓
  CancellationToken.IsCancellationRequested = true
           ↓
  Code observes via:
    • ThrowIfCancellationRequested()   ← polling
    • Register(callback)               ← callback
    • Pass token to API                ← delegation
           ↓
  OperationCanceledException thrown
```

---

## Recipe 10.1 — Issuing Cancellation Requests

```csharp
// Basic: create source, get token, pass to cancelable code, call Cancel()
async Task SimpleExample()
{
    using var cts = new CancellationTokenSource();
    Task work = DoWorkAsync(cts.Token);

    cts.Cancel();   // request cancellation

    try
    {
        await work;
    }
    catch (OperationCanceledException) { /* canceled */ }
    catch (Exception)                  { /* other error */ throw; }
}

// GUI pattern: start/cancel buttons
private CancellationTokenSource _cts;

private async void StartButton_Click(object sender, RoutedEventArgs e)
{
    _cts = new CancellationTokenSource();
    try
    {
        await DoWorkAsync(_cts.Token);
        MessageBox.Show("Done");
    }
    catch (OperationCanceledException) { MessageBox.Show("Cancelled"); }
}

private void CancelButton_Click(object sender, RoutedEventArgs e) => _cts?.Cancel();
```

> ⚠️ Once `Cancel()` is called, a `CancellationTokenSource` is permanently canceled — create a new instance for the next operation.

---

## Recipe 10.2 — Responding by Polling

Use when you have a processing loop with no lower-level API to pass the token to.

```csharp
public int ProcessData(IEnumerable<int> data, CancellationToken token)
{
    int total = 0;
    foreach (int item in data)
    {
        // Check every iteration for responsive cancellation
        token.ThrowIfCancellationRequested();
        total += HeavyCompute(item);
    }
    return total;
}

// For very tight loops: check less often
public int TightLoop(int iterations, CancellationToken token)
{
    int result = 0;
    for (int i = 0; i < iterations; i++)
    {
        if (i % 1000 == 0)           // check every 1000 iterations
            token.ThrowIfCancellationRequested();
        result += i;
    }
    return result;
}
```

---

## Recipe 10.3 — Canceling Due to Timeouts

Timeout = cancellation triggered by a timer, not a user action.

```csharp
// Pass timeout to constructor
async Task WithTimeoutConstructor(HttpClient client)
{
    using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(5));
    await client.GetStringAsync("http://example.com", cts.Token);
}

// Or: schedule cancel after creation
async Task WithCancelAfter(HttpClient client)
{
    using var cts = new CancellationTokenSource();
    cts.CancelAfter(TimeSpan.FromSeconds(5));
    await client.GetStringAsync("http://example.com", cts.Token);
}
```

---

## Recipe 10.4 — Canceling async Code

The most common pattern: just pass the token through.

```csharp
// Accept token, pass it to every API that supports it
public async Task<int> GetDataAsync(string url, CancellationToken token = default)
{
    string content = await _client.GetStringAsync(url, token);
    await Task.Delay(100, token);      // even delays respect cancellation
    return ParseData(content);
}
```

---

## Recipe 10.5 — Canceling Parallel Code

```csharp
// Pass via ParallelOptions (preferred)
void ProcessParallel(IEnumerable<Matrix> matrices, CancellationToken token)
{
    Parallel.ForEach(matrices,
        new ParallelOptions { CancellationToken = token },
        matrix => matrix.Rotate(45f));
}

// PLINQ: use WithCancellation operator
IEnumerable<int> ProcessPlinq(IEnumerable<int> values, CancellationToken token)
{
    return values.AsParallel()
                 .WithCancellation(token)
                 .Select(v => v * 2);
}
```

---

## Recipe 10.6 — Canceling System.Reactive Code

```csharp
// Option 1: dispose the subscription (simplest)
IDisposable subscription = observable.Subscribe(handler);
// ... later:
subscription.Dispose();   // stops receiving events

// Option 2: ToTask with cancellation (for async observable consumption)
int result = await observable.Take(1).ToTask(cancellationToken);

// Option 3: CancellationDisposable — cancel when disposed
using var cd = new CancellationDisposable();
// cd.Token is canceled when the using block exits
await DoWorkAsync(cd.Token);
```

---

## Recipe 10.7 — Canceling Dataflow Meshes

```csharp
IPropagatorBlock<int, int> BuildCancelableMesh(CancellationToken token)
{
    var opts = new ExecutionDataflowBlockOptions { CancellationToken = token };
    var multiply = new TransformBlock<int, int>(x => x * 2, opts);
    var subtract = new TransformBlock<int, int>(x => x - 1, opts);
    multiply.LinkTo(subtract, new DataflowLinkOptions { PropagateCompletion = true });
    return DataflowBlock.Encapsulate(multiply, subtract);
}
```

> ⚠️ Canceling a dataflow block drops all buffered items — cancellation is not a flush.

---

## Recipe 10.8 — Linked Cancellation (Combining Tokens)

Inject your own cancellation into received cancellation — e.g., add a timeout on top of a user-passed token.

```csharp
// User passes their token; we add a timeout on top
async Task<HttpResponseMessage> FetchWithTimeout(
    HttpClient client, string url, CancellationToken userToken)
{
    // Combined: cancel if EITHER user cancels OR timeout fires
    using var cts = CancellationTokenSource.CreateLinkedTokenSource(userToken);
    cts.CancelAfter(TimeSpan.FromSeconds(3));

    return await client.GetAsync(url, cts.Token);
}
```

```
LinkedTokenSource responds to ANY of its source tokens:
  userToken.Cancel()   → combined token canceled
  cts.CancelAfter()    → combined token canceled (timeout)
  Either one fires     → GetAsync throws OperationCanceledException
```

---

## Recipe 10.9 — Interop with Non-Standard Cancellation

When a third-party type has its own cancel method, bridge it with `CancellationToken.Register`.

```csharp
async Task<PingReply> PingWithCancellation(string host, CancellationToken token)
{
    using var ping = new Ping();
    Task<PingReply> task = ping.SendPingAsync(host);

    // Register callback: when token is canceled, call ping's own cancel method
    using CancellationTokenRegistration _ = token.Register(() => ping.SendAsyncCancel());

    return await task;
}
```

> 💡 Dispose the registration (via `using`) when the operation completes — otherwise callback keeps the object alive as long as the token lives.

---

## Summary: Cancellation Decision Tree

```
Do I write cancelable code?
  → Accept CancellationToken parameter (last param by convention)
  → Call ThrowIfCancellationRequested() in loops
  → Pass token to every API that accepts it

Do I issue cancellation?
  → Create CancellationTokenSource
  → Call cts.Cancel() when needed
  → Dispose the CTS when done (using statement)

Do I need a timeout?
  → new CancellationTokenSource(TimeSpan) OR cts.CancelAfter(TimeSpan)

Do I need to combine tokens?
  → CancellationTokenSource.CreateLinkedTokenSource(token1, token2, ...)

Do I interop with non-standard cancel?
  → token.Register(() => thirdPartyObj.Cancel())
```

---

*[← Chapter 9](09-collections.md) | [Back to Index](../README.md) | [Chapter 11 — Functional-Friendly OOP →](11-functional-friendly-oop.md)*
