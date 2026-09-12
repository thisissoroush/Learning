# Chapter 7: Testing

> *"Unit testing concurrent code isn't as difficult as developers think — modern tools have put a lot of thought into testing."*

---

## Core Concept

Testing concurrent code feels hard but modern frameworks and libraries make it approachable. The key principles:
- **async Task** test methods are natively supported by MSTest, NUnit, xUnit
- Deadlocks surface as hangs → set a per-test timeout
- Rx has a `TestScheduler` that lets you control time without real waiting

---

## Recipe 7.1 — Unit Testing async Methods

**Problem:** Test an async method.

**Solution:** Make the test method `async Task` — the test runner will await it.

```csharp
// xUnit
[Fact]
public async Task GetValue_ReturnsExpectedResult()
{
    var sut = new MyService();
    int result = await sut.GetValueAsync();
    Assert.Equal(42, result);
}

// MSTest
[TestMethod]
public async Task GetValue_ReturnsExpectedResult()
{
    var sut = new MyService();
    int result = await sut.GetValueAsync();
    Assert.AreEqual(42, result);
}
```

**Mocking async dependencies — test these 3 scenarios:**

```csharp
// 1. Synchronous success (most common mock)
class SyncSuccessStub : IMyService
{
    public Task<int> GetValueAsync() => Task.FromResult(42);
}

// 2. Synchronous failure
class SyncErrorStub : IMyService
{
    public Task<int> GetValueAsync() =>
        Task.FromException<int>(new InvalidOperationException("fail"));
}

// 3. Asynchronous success (forces real async behavior in tests)
class AsyncSuccessStub : IMyService
{
    public async Task<int> GetValueAsync()
    {
        await Task.Yield();   // forces the method to be truly async
        return 42;
    }
}
```

> ⚠️ Always set per-test timeouts (e.g., 2 seconds in Visual Studio test settings). Deadlocks in async code will otherwise hang your test runner silently.

---

## Recipe 7.2 — Unit Testing async Methods Expected to Fail

**Problem:** Assert that an async method throws a specific exception.

**Solution:** Use `Assert.ThrowsAsync<T>` (xUnit), or write your own.

```csharp
// xUnit — CORRECT
[Fact]
public async Task Divide_ByZero_ThrowsDivideByZeroException()
{
    await Assert.ThrowsAsync<DivideByZeroException>(async () =>
    {
        await MyClass.DivideAsync(4, 0);
    });
}

// ⚠️ DON'T FORGET the await — without it the test always passes silently!
// [Fact]
// public async Task Bad_Test()
// {
//     Assert.ThrowsAsync<...>(...)  ← missing await! always green, always wrong
// }
```

> ❌ Avoid `[ExpectedException]` attribute — it passes if the exception occurs anywhere in the test, not specifically at the line you're testing.

---

## Recipe 7.3 — Unit Testing async void Methods

**Problem:** You must test an `async void` method.

**Solution:** Refactor first — wrap logic in `async Task`, use `async void` only as the thin interface implementation.

```csharp
// Pattern: expose testable async Task, thin void wrapper for interface
sealed class MyCommand : ICommand
{
    async void ICommand.Execute(object p) => await Execute(p);  // not directly testable

    public async Task Execute(object p)    // testable!
    {
        await DoWorkAsync();
    }
}

// Test the Task-returning version
[Fact]
public async Task Execute_DoesWork()
{
    var cmd = new MyCommand();
    await cmd.Execute(null);
    // assert...
}
```

> 💡 If you absolutely must test `async void`, use `AsyncContext.Run` from `Nito.AsyncEx` — it captures exceptions from `async void` and re-throws them.

---

## Recipe 7.4 — Unit Testing Dataflow Meshes

**Problem:** Test a dataflow block or mesh.

**Solution:** Post items, complete, await Completion, then assert results.

```csharp
[TestMethod]
public async Task CustomBlock_DoublesValues()
{
    var block = CreateMyCustomBlock();

    block.Post(3);
    block.Post(7);
    block.Complete();

    Assert.AreEqual(4,  block.Receive());   // 3 → processed → 4
    Assert.AreEqual(8,  block.Receive());   // 7 → processed → 8
    await block.Completion;                 // ensure clean completion
}

// Testing fault behavior
[TestMethod]
public async Task CustomBlock_OnFault_Propagates()
{
    var block = CreateMyCustomBlock();
    ((IDataflowBlock)block).Fault(new InvalidOperationException());

    try
    {
        await block.Completion;
    }
    catch (AggregateException ex)
    {
        Assert.IsInstanceOfType(
            ex.Flatten().InnerException,
            typeof(InvalidOperationException));
    }
}
```

---

## Recipe 7.5 — Unit Testing System.Reactive Observables

**Problem:** Test code that produces or consumes `IObservable<T>`.

**Solution:** Use `Observable.Return` / `Observable.Throw` for stubs; `SingleAsync` / `ToList` to consume results.

```csharp
public class MyTimeoutClass
{
    private readonly IHttpService _http;
    public MyTimeoutClass(IHttpService http) => _http = http;

    public IObservable<string> GetWithTimeout(string url) =>
        _http.GetString(url).Timeout(TimeSpan.FromSeconds(1));
}

// Stub for success
class SuccessStub : IHttpService
{
    public IObservable<string> GetString(string url) =>
        Observable.Return("result");
}

[TestMethod]
public async Task GetWithTimeout_Success_ReturnsResult()
{
    var sut = new MyTimeoutClass(new SuccessStub());
    string result = await sut.GetWithTimeout("http://example.com").SingleAsync();
    Assert.AreEqual("result", result);
}

// Stub for failure
class ErrorStub : IHttpService
{
    public IObservable<string> GetString(string url) =>
        Observable.Throw<string>(new HttpRequestException());
}

[TestMethod]
public async Task GetWithTimeout_Failure_PropagatesException()
{
    var sut = new MyTimeoutClass(new ErrorStub());
    await Assert.ThrowsExceptionAsync<HttpRequestException>(async () =>
        await sut.GetWithTimeout("http://example.com").SingleAsync());
}
```

---

## Recipe 7.6 — Unit Testing Rx with Faked Time (TestScheduler)

**Problem:** Testing Rx code with real timeouts makes tests slow and flaky.

**Solution:** Inject `IScheduler` and use `TestScheduler` to control virtual time.

```csharp
// Production code: inject scheduler (default to Scheduler.Default)
public IObservable<string> GetWithTimeout(string url, IScheduler scheduler = null) =>
    _http.GetString(url)
         .Timeout(TimeSpan.FromSeconds(1), scheduler ?? Scheduler.Default);

// NuGet: Microsoft.Reactive.Testing
[TestMethod]
public void GetWithTimeout_ShortDelay_ReturnsResult()
{
    var scheduler = new TestScheduler();
    var stub = new SuccessStub { Scheduler = scheduler, Delay = TimeSpan.FromSeconds(0.5) };
    var sut = new MyTimeoutClass(stub);

    string result = null;
    sut.GetWithTimeout("http://example.com", scheduler)
       .Subscribe(r => result = r);

    scheduler.Start();   // advance virtual time until done — runs in ~70ms real time

    Assert.AreEqual("result", result);
}

[TestMethod]
public void GetWithTimeout_LongDelay_TimesOut()
{
    var scheduler = new TestScheduler();
    var stub = new SuccessStub { Scheduler = scheduler, Delay = TimeSpan.FromSeconds(1.5) };
    var sut = new MyTimeoutClass(stub);

    Exception error = null;
    sut.GetWithTimeout("http://example.com", scheduler)
       .Subscribe(_ => Assert.Fail(), ex => error = ex);

    scheduler.Start();   // virtual 1.5 seconds, real ~70ms

    Assert.IsInstanceOfType(error, typeof(TimeoutException));
}
```

```
Real time vs virtual time:
  Without TestScheduler: test waits 1 second of real clock
  With TestScheduler:    "1 second" runs in milliseconds
  → TestScheduler makes time-dependent Rx tests fast and deterministic
```

---

*[← Chapter 6](06-system-reactive-basics.md) | [Back to Index](../README.md) | [Chapter 8 — Interop →](08-interop.md)*
