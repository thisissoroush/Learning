# 🟡 C# — Mid-Level Interview Questions

---

## 1. How does `async`/`await` work in C#?

**A:** `async`/`await` is syntactic sugar over the Task Parallel Library (TPL). The compiler rewrites `async` methods into a state machine:

```csharp
public async Task<string> FetchDataAsync(string url)
{
    using var client = new HttpClient();
    string content = await client.GetStringAsync(url); // suspends here
    return content.ToUpper();
}
```

- `await` **suspends** the method without blocking the thread — the thread is returned to the pool
- When the awaited task completes, execution resumes (on the captured `SynchronizationContext` or thread pool)
- `async void` — fire-and-forget; avoid except for event handlers (exceptions are unobservable)
- Always prefer `async Task` over `async void`

---

## 2. What is `Task` vs `ValueTask`?

**A:**
- `Task<T>` — heap-allocated, reference type; always valid to use
- `ValueTask<T>` — struct that avoids heap allocation when the result is **already available** (common in hot paths)

```csharp
// ValueTask — efficient when result is cached
public ValueTask<int> GetCachedAsync(int key)
{
    if (_cache.TryGetValue(key, out int val))
        return ValueTask.FromResult(val); // no allocation

    return new ValueTask<int>(FetchAsync(key)); // wraps Task
}
```

**Rule:** Default to `Task<T>`. Use `ValueTask<T>` only when profiling shows allocation pressure on a hot async path.

---

## 3. What is `ConfigureAwait(false)` and when should you use it?

**A:** By default, `await` captures the `SynchronizationContext` and resumes on the original context (e.g., UI thread or ASP.NET request context). `ConfigureAwait(false)` tells the runtime not to restore the original context:

```csharp
// Library code — no need for original context
var data = await httpClient.GetStringAsync(url).ConfigureAwait(false);
```

**Use in:** Library/infrastructure code where you don't need to marshal back to the original context — avoids deadlocks in older ASP.NET (full framework) and improves performance.

**Don't use in:** UI code where you need to update controls from the continuation.

---

## 4. What are generics and what are generic constraints?

**A:** Generics allow type-safe code reuse:

```csharp
public T Max<T>(T a, T b) where T : IComparable<T>
{
    return a.CompareTo(b) >= 0 ? a : b;
}
```

**Common constraints:**

| Constraint | Meaning |
|------------|---------|
| `where T : class` | Reference type |
| `where T : struct` | Value type |
| `where T : new()` | Has parameterless constructor |
| `where T : IFoo` | Implements interface |
| `where T : Base` | Inherits from Base |

---

## 5. What is `IDisposable` and the Dispose pattern?

**A:** `IDisposable` provides deterministic cleanup of unmanaged resources (file handles, DB connections, sockets):

```csharp
public class FileProcessor : IDisposable
{
    private FileStream _stream;
    private bool _disposed;

    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }

    protected virtual void Dispose(bool disposing)
    {
        if (_disposed) return;
        if (disposing)
            _stream?.Dispose(); // managed resources
        // unmanaged cleanup here
        _disposed = true;
    }

    ~FileProcessor() => Dispose(false); // finalizer fallback
}
```

Always use `using` or `await using` to ensure `Dispose` is called.

---

## 6. What is LINQ deferred execution?

**A:** Most LINQ operators (e.g., `Where`, `Select`, `OrderBy`) are **lazy** — they return an `IEnumerable<T>` that is not evaluated until iterated:

```csharp
var query = numbers.Where(n => {
    Console.WriteLine($"Checking {n}");
    return n > 3;
}); // nothing printed yet

foreach (var n in query) // execution happens HERE
    Console.WriteLine(n);
```

**Immediate execution** operators force evaluation: `ToList()`, `ToArray()`, `Count()`, `First()`, `Sum()`.

**Gotcha:** Enumerating the same LINQ query twice executes it twice — `ToList()` to materialize if you need to reuse.

---

## 7. What is the difference between `IEnumerable<T>` and `IQueryable<T>`?

**A:**
- `IEnumerable<T>` — in-memory, LINQ operates in C# (all data loaded first)
- `IQueryable<T>` — out-of-process, LINQ expression tree translated to SQL (or other query language)

```csharp
// IQueryable — SQL: SELECT * FROM Users WHERE Age > 18
dbContext.Users.Where(u => u.Age > 18).ToList();

// IEnumerable — loads ALL users, filters in memory
dbContext.Users.AsEnumerable().Where(u => u.Age > 18).ToList();
```

Always use `IQueryable` with EF Core to push predicates to the database.

---

## 8. What is dependency injection (DI) in .NET?

**A:** DI is a technique where dependencies are provided to a class rather than created by it. .NET has a built-in DI container:

```csharp
// Register
services.AddScoped<IUserService, UserService>();
services.AddSingleton<ICache, RedisCache>();
services.AddTransient<IEmailSender, SmtpEmailSender>();

// Inject via constructor
public class UserController
{
    private readonly IUserService _users;
    public UserController(IUserService users) => _users = users;
}
```

**Lifetimes:**
- `Singleton` — one instance for app lifetime
- `Scoped` — one per request (or scope)
- `Transient` — new instance every time

---

## 9. What are delegates and events?

**A:**
```csharp
// Delegate — a type-safe function pointer
delegate int MathOp(int a, int b);

MathOp add = (a, b) => a + b;
Console.WriteLine(add(2, 3)); // 5

// Built-in delegates
Func<int, int, int> multiply = (a, b) => a * b;
Action<string> log = Console.WriteLine;
Predicate<int> isEven = n => n % 2 == 0;

// Event — delegate with publisher/subscriber pattern
public event EventHandler<DataEventArgs> DataReceived;
DataReceived += (sender, e) => Console.WriteLine(e.Data);
DataReceived?.Invoke(this, new DataEventArgs { Data = "hello" });
```

---

## 10. What is the difference between `Dictionary<K,V>` and `ConcurrentDictionary<K,V>`?

**A:**
- `Dictionary<K,V>` — not thread-safe; only one thread should access at a time
- `ConcurrentDictionary<K,V>` — fully thread-safe, lock-free reads, fine-grained locking on writes

```csharp
var cd = new ConcurrentDictionary<string, int>();
cd.TryAdd("a", 1);
cd.AddOrUpdate("a", 1, (key, old) => old + 1);
int val = cd.GetOrAdd("b", key => ComputeValue(key));
```

Use `ConcurrentDictionary` when multiple threads read/write. Prefer immutable snapshots or channels for complex workflows.

---

## 11. What is `record` in C#?

**A:** `record` (C# 9+) is a reference type with **value-based equality**, immutability by default, and built-in `ToString`/`GetHashCode`:

```csharp
record Person(string Name, int Age);

var p1 = new Person("Alice", 30);
var p2 = new Person("Alice", 30);
Console.WriteLine(p1 == p2);  // true — value equality
Console.WriteLine(p1);        // Person { Name = Alice, Age = 30 }

// Non-destructive mutation
var p3 = p1 with { Age = 31 };
```

Great for DTOs, value objects, immutable data pipelines.

---

## 12. What is `Span<T>` and why is it useful?

**A:** `Span<T>` is a stack-allocated view over contiguous memory (arrays, stack memory, native memory) — zero allocation slicing:

```csharp
byte[] data = new byte[1024];
Span<byte> header = data.AsSpan(0, 64);   // no copy
Span<byte> body   = data.AsSpan(64, 960); // no copy

// Parse without allocation
string input = "2024-01-15";
ReadOnlySpan<char> year = input.AsSpan(0, 4); // no string allocation
```

Used extensively in `System.Text`, `System.IO.Pipelines`, `HttpClient` to reduce allocations on hot paths.

---

## 13. How does exception filtering work in C#?

**A:** `when` clause filters exceptions without catching and rethrowing (preserves stack trace):

```csharp
try {
    await CallServiceAsync();
}
catch (HttpRequestException ex) when (ex.StatusCode == HttpStatusCode.ServiceUnavailable)
{
    // only catches 503, not other HttpRequestException
    await RetryAsync();
}
catch (HttpRequestException ex) when (LogAndReturn(ex))
{
    // never catches — LogAndReturn returns false; useful for logging side effects
}
```

---

## 14. What is `CancellationToken` and how do you use it?

**A:** `CancellationToken` propagates cancellation requests across async operations:

```csharp
public async Task<Data> FetchAsync(CancellationToken ct)
{
    using var response = await _client.GetAsync(url, ct);
    ct.ThrowIfCancellationRequested(); // manual check
    return await response.Content.ReadAsAsync<Data>(ct);
}

// Caller
var cts = new CancellationTokenSource(timeout: TimeSpan.FromSeconds(30));
await FetchAsync(cts.Token);

// Cancel externally
cts.Cancel();
```

Always thread `CancellationToken` through all async calls. Catch `OperationCanceledException` at boundaries.

---

## 15. What are extension methods?

**A:** Extension methods add methods to existing types without modifying them:

```csharp
public static class StringExtensions
{
    public static bool IsNullOrEmpty(this string? s) =>
        string.IsNullOrEmpty(s);

    public static string Truncate(this string s, int maxLength) =>
        s.Length <= maxLength ? s : s[..maxLength] + "...";
}

// Usage
string? name = null;
bool empty = name.IsNullOrEmpty(); // true

"Hello, World!".Truncate(5); // "Hello..."
```

LINQ is implemented entirely as extension methods on `IEnumerable<T>`.

---

## 16. What is `Task.ConfigureAwait` at the library level and how does it affect deadlocks?

**A:** In older ASP.NET (full framework) or desktop apps with a `SynchronizationContext`, awaiting without `ConfigureAwait(false)` can deadlock:

```csharp
// Deadlock scenario (old ASP.NET / WinForms)
public ActionResult Index()
{
    // Blocks the sync context thread waiting for the task
    var result = GetDataAsync().Result; // DEADLOCK
    return View(result);
}

async Task<string> GetDataAsync()
{
    await Task.Delay(1000); // tries to resume on the captured sync context
    return "data";          // but the thread is blocked above — deadlock!
}

// Fix in library code
async Task<string> GetDataAsync()
{
    await Task.Delay(1000).ConfigureAwait(false); // don't restore sync context
    return "data";
}
```

In ASP.NET Core there is no `SynchronizationContext`, so this is less of an issue — but still good practice in library code.

---

## 17. How does `Channel<T>` differ from classic producer-consumer with `BlockingCollection<T>`?

**A:**

| | `BlockingCollection<T>` | `Channel<T>` |
|--|------------------------|-------------|
| API | Synchronous blocking | Async-native |
| Threading model | Thread-blocking | Task-based |
| Backpressure | Bounded + blocks | Bounded + async wait |
| Cancellation | Via token | Via token |

```csharp
// Channel<T> — modern async producer/consumer
var channel = Channel.CreateBounded<int>(capacity: 100);

// Producer
await channel.Writer.WriteAsync(item, ct);
channel.Writer.Complete(); // signals end

// Consumer
await foreach (var item in channel.Reader.ReadAllAsync(ct))
    await ProcessAsync(item);
```

Use `Channel<T>` for async pipelines. `BlockingCollection<T>` for legacy sync code.

---

## 18. What is `IAsyncDisposable` and `await using`?

**A:** For resources that require async cleanup (e.g., flushing a buffer, closing a network connection gracefully):

```csharp
public class AsyncResource : IAsyncDisposable
{
    private readonly Stream _stream;

    public async ValueTask DisposeAsync()
    {
        await _stream.FlushAsync();
        await _stream.DisposeAsync();
    }
}

// Usage
await using var resource = new AsyncResource();
// DisposeAsync() called on exit, even on exception
```

---

## 19. What is `Lazy<T>` and when is it thread-safe?

**A:**
```csharp
// Thread-safe lazy initialization
Lazy<ExpensiveService> lazy = new Lazy<ExpensiveService>(
    () => new ExpensiveService(),
    LazyThreadSafetyMode.ExecutionAndPublication); // default

var svc = lazy.Value; // initialized once, thread-safe

// Common DI pattern
services.AddSingleton<IExpensiveService>(
    sp => new Lazy<IExpensiveService>(() => sp.GetRequiredService<ExpensiveService>()).Value);
```

**Modes:**
- `None` — no thread safety (single-threaded only)
- `PublicationOnly` — multiple threads may call factory; first to finish wins
- `ExecutionAndPublication` (default) — only one thread calls factory; others wait

---

## 20. What is `ReadOnlySpan<T>` and how does it improve string parsing?

**A:** String operations like `Substring` allocate new strings. `ReadOnlySpan<char>` slices without allocation:

```csharp
string input = "2024-01-15";

// Substring — allocates 3 new strings
int year  = int.Parse(input.Substring(0, 4));
int month = int.Parse(input.Substring(5, 2));
int day   = int.Parse(input.Substring(8, 2));

// ReadOnlySpan — zero allocation
ReadOnlySpan<char> span = input.AsSpan();
int year2  = int.Parse(span.Slice(0, 4));
int month2 = int.Parse(span.Slice(5, 2));
int day2   = int.Parse(span.Slice(8, 2));
```

This matters at scale — high-throughput parsers (HTTP headers, CSV, binary protocols) use `Span<T>` to eliminate GC pressure.

---

## 21. Explain `IOptions<T>`, `IOptionsSnapshot<T>`, and `IOptionsMonitor<T>`.

**A:**

| | `IOptions<T>` | `IOptionsSnapshot<T>` | `IOptionsMonitor<T>` |
|--|--------------|----------------------|---------------------|
| Lifetime | Singleton | Scoped | Singleton |
| Hot reload | No | Per request | Yes (OnChange callback) |
| Use in | Singletons | Controllers/services | Background services |

```csharp
// Register
builder.Services.Configure<SmtpOptions>(config.GetSection("Smtp"));

// Inject and use
public class EmailService
{
    private readonly SmtpOptions _opts;
    public EmailService(IOptionsMonitor<SmtpOptions> opts)
    {
        _opts = opts.CurrentValue;
        opts.OnChange(newOpts => _opts = newOpts); // reacts to config changes
    }
}
```

---

## 22. What is the Outbox pattern and how do you implement it in EF Core?

**A:** Ensures that a DB write and a message publish are atomic — prevents lost events on crash:

```csharp
// Same transaction: business record + outbox entry
await using var tx = await db.Database.BeginTransactionAsync(ct);

db.Orders.Add(order);
db.OutboxMessages.Add(new OutboxMessage
{
    Id = Guid.NewGuid(),
    Type = nameof(OrderCreated),
    Payload = JsonSerializer.Serialize(new OrderCreated(order.Id)),
    CreatedAt = DateTime.UtcNow,
    Processed = false
});

await db.SaveChangesAsync(ct);
await tx.CommitAsync(ct);

// Separate BackgroundService polls OutboxMessages and publishes to bus
// Uses SELECT ... FOR UPDATE SKIP LOCKED to avoid duplicate processing
```

---

## 23. How does `HybridCache` work in .NET 9?

**A:** `HybridCache` (introduced in .NET 9 Preview) combines L1 (in-process memory) and L2 (Redis) caching with stampede protection built in:

```csharp
services.AddHybridCache();
services.AddStackExchangeRedisCache(o => o.Configuration = "redis:6379");

// Usage
public async Task<UserDto> GetUserAsync(int id, CancellationToken ct)
{
    return await _cache.GetOrCreateAsync(
        $"user:{id}",
        async cancel => await _db.Users.FindAsync(new object[] { id }, cancel),
        new HybridCacheEntryOptions
        {
            Expiration = TimeSpan.FromMinutes(5),
            LocalCacheExpiration = TimeSpan.FromMinutes(1)
        },
        cancellationToken: ct);
}
```

Stampede protection (single-flight) is built in — concurrent misses trigger only one DB call.

---

## 24. How do you write integration tests for ASP.NET Core with `WebApplicationFactory`?

**A:**
```csharp
public class OrdersApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public OrdersApiTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.WithWebHostBuilder(builder =>
        {
            builder.ConfigureServices(services =>
            {
                // Replace real DB with in-memory
                services.RemoveAll<DbContextOptions<AppDbContext>>();
                services.AddDbContext<AppDbContext>(o => o.UseInMemoryDatabase("test"));
            });
        }).CreateClient();
    }

    [Fact]
    public async Task CreateOrder_Returns201()
    {
        var response = await _client.PostAsJsonAsync("/orders",
            new { CustomerId = "cust-1", Items = new[] { new { ProductId = "p1", Qty = 2 } } });

        Assert.Equal(HttpStatusCode.Created, response.StatusCode);
    }
}
```

---

## 25. What are primary constructors in C# 12?

**A:** C# 12 allows constructors directly in the class declaration:

```csharp
// Before C# 12
public class OrderService
{
    private readonly IOrderRepository _repo;
    private readonly ILogger<OrderService> _logger;

    public OrderService(IOrderRepository repo, ILogger<OrderService> logger)
    {
        _repo = repo;
        _logger = logger;
    }
}

// C# 12 primary constructor
public class OrderService(IOrderRepository repo, ILogger<OrderService> logger)
{
    public async Task<Order> GetAsync(Guid id) =>
        await repo.FindAsync(id) ?? throw new NotFoundException(id);
}
```

Parameters are in scope throughout the class body. Reduces boilerplate for DI-heavy services.

---

## 26. What is `FrozenDictionary<K,V>` and when should you use it?

**A:** `FrozenDictionary<T,K>` (introduced in .NET 8) is an immutable dictionary optimized for read performance — lookup is faster than `Dictionary<K,V>` because it can use perfect hashing:

```csharp
// Build once at startup
FrozenDictionary<string, CountryInfo> countries =
    LoadCountries().ToFrozenDictionary(c => c.Code);

// Then use throughout app lifetime — faster lookups, no lock needed
if (countries.TryGetValue("US", out var info))
    Console.WriteLine(info.Name);
```

Use for large, read-only lookup tables initialized at startup (country codes, product catalogs, feature flags snapshot).

---

## 27. How does `BenchmarkDotNet` work?

**A:**
```csharp
[MemoryDiagnoser]
[SimpleJob(RuntimeMoniker.Net80)]
public class StringBenchmarks
{
    private string _input = "Hello, World!";

    [Benchmark(Baseline = true)]
    public string Substring() => _input.Substring(0, 5);

    [Benchmark]
    public ReadOnlySpan<char> AsSpan() => _input.AsSpan(0, 5);
}
```

```bash
dotnet run -c Release -- --filter '*StringBenchmarks*'
```

BenchmarkDotNet handles warmup, multiple iterations, statistical analysis, and memory allocation reporting. Never benchmark in `Debug` mode.

---

## 28. What is `record struct` vs `record class`?

**A:**
```csharp
// record class (default) — reference type, value equality, heap-allocated
record class Point(int X, int Y);

// record struct — value type, value equality, stack-allocated
record struct Point3D(int X, int Y, int Z);

var p1 = new Point3D(1, 2, 3);
var p2 = p1; // full copy — value type

// readonly record struct — immutable value type (preferred for small data)
readonly record struct Color(byte R, byte G, byte B);
```

Use `readonly record struct` for small, immutable value objects (coordinates, money, color) — zero heap allocation.
