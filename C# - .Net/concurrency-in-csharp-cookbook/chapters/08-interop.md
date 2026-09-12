# Chapter 8: Interop

> *"Async, parallel, reactive — they complement each other rather than compete. There's very little friction at the boundaries."*

---

## Core Concept

Real-world apps mix async, parallel, reactive, and dataflow code. This chapter shows the **bridge patterns** to cross those boundaries cleanly.

```
INTEROP MAP
═══════════════════════════════════════════════════════
EAP  (OperationAsync / OperationCompleted)
APM  (BeginXxx / EndXxx)
                          ↓ wrap with TaskCompletionSource
              TAP  (async/await + Task<T>)
                ↕                        ↕
         IObservable<T>          IAsyncEnumerable<T>
                ↕                        ↕
        Dataflow blocks ←────────────────┘
```

---

## Recipe 8.1 — Wrapping Old EAP Events (OperationAsync + OperationCompleted)

**Problem:** Old API uses the Event-based Asynchronous Pattern — you want to `await` it.

**Solution:** Use `TaskCompletionSource<T>` to bridge the event to a Task.

```csharp
// Wrapping WebClient's EAP pattern into TAP
public static Task<string> DownloadStringTaskAsync(this WebClient client, Uri address)
{
    var tcs = new TaskCompletionSource<string>();

    DownloadStringCompletedEventHandler handler = null;
    handler = (_, e) =>
    {
        client.DownloadStringCompleted -= handler;   // unsubscribe
        if (e.Cancelled)        tcs.TrySetCanceled();
        else if (e.Error != null) tcs.TrySetException(e.Error);
        else                    tcs.TrySetResult(e.Result);
    };

    client.DownloadStringCompleted += handler;
    client.DownloadStringAsync(address);
    return tcs.Task;
}

// Usage
string html = await client.DownloadStringTaskAsync(new Uri("http://example.com"));
```

---

## Recipe 8.2 — Wrapping APM (BeginXxx / EndXxx)

**Problem:** Old API uses the Asynchronous Programming Model — you want to `await` it.

**Solution:** Use `Task.Factory.FromAsync` — pass the Begin/End methods directly.

```csharp
// Cleanest form: pass Begin/End methods without calling them
public static Task<WebResponse> GetResponseAsync(this WebRequest request)
{
    return Task<WebResponse>.Factory.FromAsync(
        request.BeginGetResponse,
        request.EndGetResponse,
        null);   // state object (always null in modern code)
}
```

> 💡 Don't call `BeginXxx` before passing to `FromAsync` — it forces a less efficient code path.

---

## Recipe 8.3 — Wrapping Anything with TaskCompletionSource

**Problem:** Non-standard async pattern (e.g., callback-based).

**Solution:** `TaskCompletionSource<T>` is the universal adapter.

```csharp
// Callback-based API: void Method(args, Action<result, Exception> callback)
public static Task<string> DownloadAsync(this IMyHttpService service, Uri uri)
{
    var tcs = new TaskCompletionSource<string>();
    service.Download(uri, (result, ex) =>
    {
        if (ex != null) tcs.TrySetException(ex);
        else            tcs.TrySetResult(result);
    });
    return tcs.Task;
}
```

> ⚠️ Always ensure `TrySetResult/TrySetException/TrySetCanceled` is called in every code path — an uncompleted TCS silently leaks forever.

---

## Recipe 8.4 — Async Wrapper for Parallel Code

**Problem:** `Parallel.ForEach` on the UI thread blocks it.

**Solution:** Push parallel work to threadpool via `Task.Run`, then await the result.

```csharp
// UI thread stays responsive
await Task.Run(() => Parallel.ForEach(matrices, m => m.Rotate(45f)));
await Task.Run(() => values.AsParallel().Select(HeavyCompute).ToList());
```

> 💡 On ASP.NET server code, don't do this — the server already parallelizes across requests.

---

## Recipe 8.5 — Consuming Rx Observables with await

**Problem:** You have an `IObservable<T>` and need to use `await` to get values from it.

```csharp
IObservable<int> stream = ...;

// Await the last element (waits for OnCompleted)
int last = await stream.LastAsync();
int last2 = await stream;                 // same as LastAsync

// Await the first element (unsubscribes after first OnNext)
int first = await stream.FirstAsync();

// Collect all elements (waits for OnCompleted)
IList<int> all = await stream.ToList();

// Convert to Task<T> for use with WhenAll/WhenAny
Task<int> task = stream.ToTask();
```

---

## Recipe 8.6 — Wrapping async Code as Rx Observables

**Problem:** You have async code and want to incorporate it into an Rx pipeline.

```csharp
HttpClient client = ...;

// Already-started task → hot observable
IObservable<HttpResponseMessage> hot =
    client.GetAsync("http://example.com").ToObservable();

// Start task on subscription → warm observable (supports cancellation)
IObservable<HttpResponseMessage> warm =
    Observable.StartAsync(token => client.GetAsync("http://example.com", token));

// Start a new task per subscription → cold observable (supports cancellation)
IObservable<HttpResponseMessage> cold =
    Observable.FromAsync(token => client.GetAsync("http://example.com", token));

// Start async operation per event in a stream (SelectMany)
IObservable<HttpResponseMessage> perEvent =
    urlStream.SelectMany((url, token) => client.GetAsync(url, token));
```

---

## Recipe 8.7 — Async Streams ↔ Dataflow Meshes

**Problem:** Bridge between `IAsyncEnumerable<T>` and dataflow blocks.

```csharp
// Consume a dataflow block as an async stream
public static async IAsyncEnumerable<T> ReceiveAllAsync<T>(
    this ISourceBlock<T> block,
    [EnumeratorCancellation] CancellationToken token = default)
{
    while (await block.OutputAvailableAsync(token).ConfigureAwait(false))
        while (block.TryReceiveItem(out var value))
            yield return value;
}

// Usage
var multiplyBlock = new TransformBlock<int, int>(x => x * 2);
multiplyBlock.Post(5);
multiplyBlock.Complete();

await foreach (int item in multiplyBlock.ReceiveAllAsync())
    Console.WriteLine(item);   // 10

// Feed an async stream into a dataflow block
await asyncStream.WriteToBlockAsync(targetBlock);
```

---

## Recipe 8.8 — Rx ↔ Dataflow Meshes

**Problem:** Bridge between `IObservable<T>` and dataflow blocks.

```csharp
// Dataflow block → Observable (use block as event source)
var buffer = new BufferBlock<int>();
IObservable<int> observable = buffer.AsObservable();
observable.Subscribe(x => Console.WriteLine(x));
buffer.Post(42);   // triggers Subscribe handler

// Observable → Dataflow block (use block as observer/sink)
IObservable<DateTimeOffset> ticks = Observable.Interval(TimeSpan.FromSeconds(1))
    .Timestamp().Select(x => x.Timestamp).Take(5);

var display = new ActionBlock<DateTimeOffset>(t => Console.WriteLine(t));
ticks.Subscribe(display.AsObserver());
await display.Completion;
```

---

## Recipe 8.9 — Rx Observables → Async Streams

**Problem:** Convert a push-based `IObservable<T>` to a pull-based `IAsyncEnumerable<T>`.

```csharp
// Simple: uses unbounded buffer (producer must eventually slow down)
IObservable<long> obs = Observable.Interval(TimeSpan.FromSeconds(1));
IAsyncEnumerable<long> stream = obs.ToAsyncEnumerable();   // System.Linq.Async

// With bounded buffer (drops oldest when full)
public static async IAsyncEnumerable<T> ToAsyncEnumerable<T>(
    this IObservable<T> obs, int bufferSize)
{
    var opts = new BoundedChannelOptions(bufferSize)
        { FullMode = BoundedChannelFullMode.DropOldest };
    var ch = Channel.CreateBounded<T>(opts);
    using (obs.Subscribe(
        v  => ch.Writer.TryWrite(v),
        ex => ch.Writer.Complete(ex),
        ()  => ch.Writer.Complete()))
    {
        await foreach (T item in ch.Reader.ReadAllAsync())
            yield return item;
    }
}
```

```
Push vs Pull:
  IObservable<T>       →  data is pushed at you (you react)
  IAsyncEnumerable<T>  →  you pull data when ready (you control pace)

  Bridge with a buffer/channel:
    Observable pushes into channel →→→ async stream pulls from channel
```

---

*[← Chapter 7](07-testing.md) | [Back to Index](../README.md) | [Chapter 9 — Collections →](09-collections.md)*
