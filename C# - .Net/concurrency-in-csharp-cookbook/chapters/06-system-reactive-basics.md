# Chapter 6: System.Reactive Basics

> *"Rx is LINQ to Events — a push model where events travel through your query by themselves."*

---

## Core Concept

System.Reactive (Rx) treats **events as data streams** (`IObservable<T>`). Unlike LINQ-to-Objects (pull), Rx is **push**: events arrive and flow through your operators automatically. Every observable can produce zero or more items (`OnNext`), then either complete (`OnCompleted`) or fail (`OnError`) — exactly once.

```
Observable stream lifecycle:
  OnNext(value1) → OnNext(value2) → OnNext(value3) → OnCompleted
  or
  OnNext(value1) → OnNext(value2) → OnError(exception)

Rx vs LINQ-to-Objects:
  LINQ-to-Objects: you pull data when you iterate (foreach)
  Rx:             data pushes itself through your operators when events fire

NuGet: System.Reactive
```

---

## Recipe 6.1 — Converting .NET Events to Observables

**Problem:** You want to treat a .NET event as an observable stream.

**Solution:** `Observable.FromEventPattern`

```csharp
// Modern events using EventHandler<T> — cleanest form
var progress = new Progress<int>();
IObservable<EventPattern<int>> reports =
    Observable.FromEventPattern<int>(
        handler => progress.ProgressChanged += handler,
        handler => progress.ProgressChanged -= handler);

reports.Subscribe(data => Console.WriteLine($"Progress: {data.EventArgs}"));

// Old-style events with custom delegate types (e.g., ElapsedEventHandler)
var timer = new System.Timers.Timer(1000) { Enabled = true };
IObservable<EventPattern<ElapsedEventArgs>> ticks =
    Observable.FromEventPattern<ElapsedEventHandler, ElapsedEventArgs>(
        handler => (s, a) => handler(s, a),   // convert to EventHandler<T>
        handler => timer.Elapsed += handler,
        handler => timer.Elapsed -= handler);

ticks.Subscribe(x => Console.WriteLine(x.EventArgs.SignalTime));

// Reflection-based (simpler syntax, but loses strong typing)
IObservable<EventPattern<object>> ticksLoose =
    Observable.FromEventPattern(timer, nameof(timer.Elapsed));
ticksLoose.Subscribe(x =>
    Console.WriteLine(((ElapsedEventArgs)x.EventArgs).SignalTime));
```

> 💡 `SubscribeOn` controls which thread subscribes/unsubscribes to the event. `ObserveOn` controls which thread receives notifications. Don't confuse them.

---

## Recipe 6.2 — Sending Notifications to a Specific Context

**Problem:** Observable notifications arrive on threadpool threads but you need to update UI.

**Solution:** `ObserveOn` with a `SynchronizationContext`.

```csharp
// In a UI button click handler
SynchronizationContext uiContext = SynchronizationContext.Current;

Observable.Interval(TimeSpan.FromSeconds(1))  // fires on threadpool
    .ObserveOn(uiContext)                      // marshal to UI thread
    .Subscribe(x => label.Content = x.ToString());

// Move heavy work OFF the UI thread, then results back ON
Observable.FromEventPattern<MouseEventHandler, MouseEventArgs>(...)
    .Select(e => e.EventArgs.GetPosition(this))
    .ObserveOn(Scheduler.Default)              // move to threadpool
    .Select(pos =>
    {
        // CPU-heavy work runs on threadpool
        return HeavyComputation(pos);
    })
    .ObserveOn(uiContext)                      // move results back to UI
    .Subscribe(result => label.Content = result.ToString());
```

---

## Recipe 6.3 — Grouping Events with Windows and Buffers

**Problem:** You need to process groups of events (by count or time window).

**Solution:** `Buffer` (collect then emit list) or `Window` (emit sub-stream as events arrive).

```csharp
// Buffer — collect 2 events, emit as IList<T>
Observable.Interval(TimeSpan.FromSeconds(1))
    .Buffer(2)   // [0,1], [2,3], [4,5], ...
    .Subscribe(batch => Console.WriteLine($"Got {batch[0]} and {batch[1]}"));

// Buffer by time — all events in 1-second window
mouseMoves
    .Buffer(TimeSpan.FromSeconds(1))
    .Subscribe(batch => Console.WriteLine($"{batch.Count} moves this second"));

// Window — emit IObservable<T> for each window (items arrive in real-time)
Observable.Interval(TimeSpan.FromSeconds(1))
    .Window(2)
    .Subscribe(window =>
    {
        window.Subscribe(
            x  => Console.WriteLine($"  item: {x}"),
            () => Console.WriteLine("  window done"));
    });
```

```
Buffer(2) output:      Window(2) output:
  ──────────────────    ──────────────────
  [collect 0,1]         window 1 opens
  emit [0,1]             emit 0
  [collect 2,3]          emit 1
  emit [2,3]            window 1 closes, window 2 opens
                         emit 2  ...
```

---

## Recipe 6.4 — Throttling and Sampling Event Streams

**Problem:** Events arrive too fast (e.g., mouse moves, keystrokes) and flood your processing.

**Solution:** `Throttle` (sliding window — emit after quiet period) or `Sample` (regular snapshot).

```csharp
// Throttle — emit last value after no new events for 1 second
// Great for: search-as-you-type, autocomplete
mouseMoves
    .Select(e => e.GetPosition(this))
    .Throttle(TimeSpan.FromSeconds(1))   // resets timer on each new event
    .Subscribe(pos => DoSearch(pos));

// Sample — emit most recent value every 1 second regardless
// Great for: live dashboards, progress bars
sensorReadings
    .Sample(TimeSpan.FromSeconds(1))
    .Subscribe(reading => UpdateDisplay(reading));
```

```
Throttle vs Sample:
  Events: ●●●●●●  (burst)   ...quiet...  ●●●
  
  Throttle: waits for silence → emits last  → only 1 value after quiet period
  Sample:   emits every T seconds regardless → steady output rate
```

---

## Recipe 6.5 — Timeouts

**Problem:** You're waiting for an event that may never arrive, and need a fallback.

**Solution:** `Timeout` operator terminates the stream with `TimeoutException` if no event arrives.

```csharp
// Timeout — stream ends with TimeoutException if idle for 1 second
httpCall.ToObservable()
    .Timeout(TimeSpan.FromSeconds(1))
    .Subscribe(
        result => Console.WriteLine(result),
        ex     => Console.WriteLine($"Error: {ex}"));   // catches TimeoutException

// Timeout with fallback stream — switch to a different observable on timeout
mouseMoves
    .Timeout(TimeSpan.FromSeconds(1), clickStream)   // after timeout, switch to clicks
    .Subscribe(
        pos => Console.WriteLine($"Position: {pos}"),
        ex  => Console.WriteLine($"Error: {ex}"));
```

---

## Visual Summary

```
Rx OPERATOR CHEAT SHEET
══════════════════════════════════════════════════════════════

FROM:
  FromEventPattern()    Convert .NET events → observable
  Observable.Return()   Single value observable
  Observable.Interval() Periodic timer observable
  task.ToObservable()   Task<T> → observable

TRANSFORM:
  Select()       project each element
  Where()        filter elements
  SelectMany()   flatten/expand each element

TIME-BASED:
  Throttle()     emit after silence period (debounce)
  Sample()       emit on fixed schedule
  Timeout()      error if no event in timespan
  Delay()        delay all notifications
  Buffer(n/t)    batch into lists
  Window(n/t)    batch into sub-streams

CONTEXT:
  ObserveOn()    control which thread receives notifications
  SubscribeOn()  control which thread subscribes/unsubscribes

TERMINATE:
  Subscribe()    start listening
  FirstAsync()   await next element
  LastAsync()    await final element  
  ToList()       collect all → await list
```

---

*[← Chapter 5](05-dataflow-basics.md) | [Back to Index](../README.md) | [Chapter 7 — Testing →](07-testing.md)*
