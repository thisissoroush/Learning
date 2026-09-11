# 🔴 C# — Senior Interview Questions

---

## 1. How does the .NET garbage collector work?

**A:** .NET's GC is a **generational, mark-and-compact** collector:

**Generations:**
- **Gen 0** — new, short-lived objects; collected most frequently (sub-millisecond)
- **Gen 1** — buffer between Gen 0 and Gen 2; medium-lived objects
- **Gen 2** — long-lived objects; collected least frequently (can cause longer pauses)
- **LOH (Large Object Heap)** — objects ≥ 85KB; collected with Gen 2; fragmentation-prone

**GC modes:**
- **Workstation GC** — optimized for low latency (UI apps)
- **Server GC** — one GC heap per CPU core, higher throughput (ASP.NET)
- **Background GC** — concurrent Gen 2 collection to minimize pauses (default)

**Tuning:**
```csharp
GC.Collect(2, GCCollectionMode.Forced); // force full GC
GC.GetTotalMemory(forceFullCollection: false);
// Set via runtimeconfig.json:
// "System.GC.HeapHardLimit": 1073741824 // 1GB
```

Key: avoid LOH fragmentation — reuse large arrays via `ArrayPool<T>`.

---

## 2. What is `ArrayPool<T>` and when should you use it?

**A:** `ArrayPool<T>` provides a pool of reusable arrays to reduce GC pressure:

```csharp
var pool = ArrayPool<byte>.Shared;

byte[] buffer = pool.Rent(4096); // get array of at least 4096 bytes
try
{
    int read = await stream.ReadAsync(buffer.AsMemory(0, buffer.Length), ct);
    Process(buffer.AsSpan(0, read));
}
finally
{
    pool.Return(buffer, clearArray: false); // return to pool
}
```

**Use when:** Frequently allocating and discarding buffers (HTTP request/response, serialization, compression). Especially important for LOH avoidance with large buffers.

**Caveats:**
- Rented array may be larger than requested — always use the returned length, not the array length
- Always return in `finally` — leaked arrays are not returned to pool (just GC'd, not pooled)

---

## 3. Explain `Memory<T>` and `Span<T>` and their relationship.

**A:**

| | `Span<T>` | `Memory<T>` |
|--|-----------|-------------|
| Storage | Stack only (ref struct) | Heap or stack |
| Async | Cannot cross `await` | Can cross `await` |
| From | array, stack, unmanaged | array, ArrayPool |
| Zero-copy slicing | ✅ | ✅ |

```csharp
// Span — synchronous, stack-confined
void ProcessSync(ReadOnlySpan<byte> data) { ... }

// Memory — can be stored and passed to async methods
async Task ProcessAsync(ReadOnlyMemory<byte> data, CancellationToken ct)
{
    await socket.SendAsync(data, ct); // Span can't cross await
}

// Conversion
byte[] arr = new byte[1024];
Memory<byte> mem = arr.AsMemory(0, 512);
Span<byte> span = mem.Span; // or arr.AsSpan(0, 512)
```

---

## 4. What is `System.IO.Pipelines` and when do you use it?

**A:** `System.IO.Pipelines` provides a high-performance I/O abstraction that eliminates buffer copying and manages backpressure:

```csharp
var pipe = new Pipe();

// Producer — writes data to the pipe
async Task WriteAsync(PipeWriter writer)
{
    Memory<byte> buffer = writer.GetMemory(1024);
    int bytes = await stream.ReadAsync(buffer);
    writer.Advance(bytes);
    await writer.FlushAsync();
}

// Consumer — reads from the pipe without copying
async Task ReadAsync(PipeReader reader)
{
    ReadResult result = await reader.ReadAsync();
    ReadOnlySequence<byte> buffer = result.Buffer;
    // parse buffer...
    reader.AdvanceTo(buffer.End);
}
```

Used in: Kestrel (ASP.NET Core's web server), SignalR, gRPC. Use when processing network streams, line-based protocols, or binary framing.

---

## 5. How does `IAsyncEnumerable<T>` work?

**A:** `IAsyncEnumerable<T>` enables async iteration — consuming items one at a time from an async source (database cursor, gRPC stream, Kafka consumer):

```csharp
// Producer
async IAsyncEnumerable<Order> GetOrdersAsync(
    [EnumeratorCancellation] CancellationToken ct = default)
{
    await foreach (var row in db.QueryAsync<Order>("SELECT...", ct))
        yield return row;
}

// Consumer
await foreach (var order in GetOrdersAsync(ct))
{
    await ProcessOrderAsync(order);
}

// With LINQ (System.Linq.Async)
var total = await GetOrdersAsync()
    .Where(o => o.Total > 100)
    .SumAsync(o => o.Total);
```

Key difference from `IEnumerable<Task<T>>`: items are produced and consumed concurrently without buffering all in memory.

---

## 6. Explain the TPL Dataflow library.

**A:** TPL Dataflow provides composable, actor-like message-passing blocks for concurrent pipelines:

```csharp
// Transform block: reads int, produces string
var transform = new TransformBlock<int, string>(
    async n => {
        await Task.Delay(10);
        return n.ToString();
    },
    new ExecutionDataflowBlockOptions { MaxDegreeOfParallelism = 4 });

// Action block: terminal consumer
var print = new ActionBlock<string>(
    s => Console.WriteLine(s));

// Link blocks
transform.LinkTo(print, new DataflowLinkOptions { PropagateCompletion = true });

// Feed data
for (int i = 0; i < 100; i++)
    await transform.SendAsync(i);

transform.Complete();
await print.Completion;
```

Blocks handle: bounded capacity (backpressure), parallelism, error propagation, cancellation. Good for ETL, event processing, image processing pipelines.

---

## 7. What is `Interlocked` and when do you use it over `lock`?

**A:** `System.Threading.Interlocked` provides atomic operations on primitive types without the overhead of a lock:

```csharp
int counter = 0;

// Atomic increment — no lock needed
Interlocked.Increment(ref counter);
Interlocked.Add(ref counter, 5);

// Compare-and-swap (CAS) — foundation of lock-free algorithms
int original = Interlocked.CompareExchange(ref counter, newValue, expected);
// Sets counter = newValue only if counter == expected

// Atomic read of long on 32-bit platforms
long value = Interlocked.Read(ref _longField);
```

Use for: simple counters, flags, CAS-based lock-free structures. For anything more complex, use `lock` or `Channel<T>`.

---

## 8. What are `ValueTask`, `Task.WhenAll`, and `Task.WhenAny` use cases?

**A:**

```csharp
// WhenAll — await multiple tasks concurrently
var results = await Task.WhenAll(
    FetchUserAsync(id),
    FetchOrdersAsync(id),
    FetchPrefsAsync(id)
); // all run concurrently; returns when ALL complete

// WhenAny — first-completed wins (timeout pattern)
var cts = new CancellationTokenSource();
var task = FetchAsync(cts.Token);
var timeout = Task.Delay(5000);

if (await Task.WhenAny(task, timeout) == timeout)
{
    cts.Cancel();
    throw new TimeoutException();
}
var result = await task;

// ValueTask — avoid allocation when result is synchronous
public ValueTask<int> GetCountAsync()
{
    if (_cache.TryGet("count", out int v))
        return ValueTask.FromResult(v); // no allocation
    return new ValueTask<int>(FetchCountAsync());
}
```

---

## 9. How does `EF Core` handle change tracking and what are the performance implications?

**A:** EF Core tracks entity state (Added, Modified, Deleted, Unchanged) to generate SQL on `SaveChanges`:

```csharp
// Tracking query (default) — entities are watched by change tracker
var user = await db.Users.FirstAsync(u => u.Id == id);
user.Name = "New Name";
await db.SaveChangesAsync(); // generates UPDATE

// No-tracking query — read-only, much faster
var users = await db.Users
    .AsNoTracking()
    .Where(u => u.IsActive)
    .ToListAsync();

// AsNoTrackingWithIdentityResolution — no tracking but deduplicates
var posts = await db.Posts
    .AsNoTrackingWithIdentityResolution()
    .Include(p => p.Author)
    .ToListAsync();
```

**Performance tips:**
- Use `AsNoTracking()` for read-only queries (20-40% faster)
- `SaveChanges` in bulk — batch inserts with `ExecuteUpdateAsync`/`ExecuteDeleteAsync` (EF 7+)
- Avoid loading the full entity for updates: `db.Users.Where(u => u.Id == id).ExecuteUpdateAsync(s => s.SetProperty(u => u.Name, "New"))`

---

## 10. What is the difference between `Task.Run` and `Task.Factory.StartNew`?

**A:**
- `Task.Run` — simplified API, always uses thread pool, propagates exceptions properly, preferred
- `Task.Factory.StartNew` — fine-grained control (scheduler, creation options, parent task)

```csharp
// Task.Run — for CPU-bound work on thread pool
await Task.Run(() => HeavyComputation());

// StartNew — when you need specific options
await Task.Factory.StartNew(
    () => HeavyWork(),
    ct,
    TaskCreationOptions.LongRunning, // dedicated thread (not pool)
    TaskScheduler.Default);
```

Use `TaskCreationOptions.LongRunning` for work that blocks for a long time — avoids starving the thread pool.

---

## 11. How do you implement the Outbox pattern in C#?

**A:** Outbox ensures atomicity between DB write and message publish — critical for microservices:

```csharp
// Within a transaction: save the domain object + the outbox record
await using var tx = await db.Database.BeginTransactionAsync();
db.Orders.Add(order);
db.OutboxMessages.Add(new OutboxMessage {
    Id = Guid.NewGuid(),
    Type = nameof(OrderCreated),
    Payload = JsonSerializer.Serialize(new OrderCreated(order.Id)),
    CreatedAt = DateTime.UtcNow
});
await db.SaveChangesAsync();
await tx.CommitAsync();

// Background relay (hosted service) — polls and publishes
// Uses SELECT ... FOR UPDATE SKIP LOCKED (Postgres) to avoid duplicates
```

Combine with idempotency keys on the consumer side to handle duplicate deliveries safely.

---

## 12. How do you implement rate limiting in ASP.NET Core?

**A:** ASP.NET Core 7+ has built-in rate limiting middleware:

```csharp
builder.Services.AddRateLimiter(options =>
{
    options.AddFixedWindowLimiter("api", o =>
    {
        o.PermitLimit = 100;
        o.Window = TimeSpan.FromMinutes(1);
        o.QueueProcessingOrder = QueueProcessingOrder.OldestFirst;
        o.QueueLimit = 10;
    });

    options.AddSlidingWindowLimiter("perUser", o =>
    {
        o.PermitLimit = 20;
        o.Window = TimeSpan.FromSeconds(10);
        o.SegmentsPerWindow = 5;
    });

    options.RejectionStatusCode = 429;
});

app.UseRateLimiter();

// Apply to endpoint
app.MapGet("/api/data", Handler).RequireRateLimiting("api");
```

---

## 13. What is `IHostedService` and `BackgroundService`?

**A:** `IHostedService` lets you run background work tied to the application lifetime:

```csharp
public class OutboxRelay : BackgroundService  // extends IHostedService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            await ProcessOutboxBatchAsync(stoppingToken);
            await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken);
        }
    }
}

// Register
builder.Services.AddHostedService<OutboxRelay>();
```

The host starts all `IHostedService` implementations on startup and stops them gracefully on shutdown.

---

## 14. What are source generators in C#?

**A:** Source generators (Roslyn) run at compile time and generate additional C# source code:

**Common uses:**
- `System.Text.Json` source generation — AOT-friendly serialization without reflection
- `LoggerMessage.Define` — structured logging without boxing
- `Microsoft.Extensions.Options` validation

```csharp
// JsonSerializerContext — source generated serializer
[JsonSerializable(typeof(Order))]
[JsonSerializable(typeof(List<Order>))]
public partial class AppJsonContext : JsonSerializerContext {}

var order = JsonSerializer.Deserialize<Order>(json, AppJsonContext.Default.Order);
// No reflection at runtime — faster, AOT-compatible
```

---

## 15. How do you handle cross-cutting concerns in .NET (logging, validation, error handling)?

**A:**

**Middleware pipeline (ASP.NET Core):**
```csharp
app.UseExceptionHandler("/error");
app.UseSerilogRequestLogging();
app.UseRateLimiter();
app.UseAuthentication();
app.UseAuthorization();
```

**MediatR pipeline behaviors (CQRS):**
```csharp
public class ValidationBehavior<TReq, TRes> : IPipelineBehavior<TReq, TRes>
{
    public async Task<TRes> Handle(TReq request, RequestHandlerDelegate<TRes> next, ...)
    {
        // validate before handler
        var errors = _validators.Select(v => v.Validate(request))
                                .SelectMany(r => r.Errors).ToList();
        if (errors.Any()) throw new ValidationException(errors);
        return await next();
    }
}
```

**Global exception handling (Problem Details, RFC 7807):**
```csharp
builder.Services.AddProblemDetails();
app.UseExceptionHandler(); // returns ProblemDetails JSON automatically
```
