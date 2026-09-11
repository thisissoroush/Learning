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
