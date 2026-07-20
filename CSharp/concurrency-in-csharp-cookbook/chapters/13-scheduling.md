# Chapter 13: Scheduling

> *"Don't specify a scheduler unless you have to — the defaults are usually correct."*

---

## Core Concept

A **scheduler** decides *where* (which thread/context) a piece of code executes.

```
SCHEDULER HIERARCHY
══════════════════════════════════════════════════════
  TaskScheduler.Default          → threadpool (most common)
  TaskScheduler.FromCurrent      → captures UI/request context
       SynchronizationContext()
  ConcurrentExclusiveScheduler   → concurrent OR exclusive execution
       Pair
```

---

## Recipe 13.1 — Scheduling Work to the Thread Pool

`Task.Run` is the modern way to push CPU-bound work to a threadpool thread.

```csharp
// Push blocking work to threadpool (frees UI thread)
Task task = Task.Run(() =>
{
    Thread.Sleep(2000);  // simulate CPU-bound work
});

// Task.Run understands async lambdas
Task<int> asyncTask = Task.Run(async () =>
{
    await Task.Delay(2000);
    return 42;
});

// Await the result
int result = await asyncTask;
```

**Replaces these legacy patterns (do NOT use in new code):**
- `BackgroundWorker`
- `ThreadPool.QueueUserWorkItem`
- `Delegate.BeginInvoke`
- `new Thread()`

> ⚠️ Don't use `Task.Run` on ASP.NET — request threads are already threadpool threads; pushing to another thread is wasteful.

---

## Recipe 13.2 — Executing Code with a TaskScheduler

```csharp
// 1. Default scheduler (thread pool)
TaskScheduler pool = TaskScheduler.Default;

// 2. Capture current context (e.g., UI thread) for later use
TaskScheduler uiScheduler = TaskScheduler.FromCurrentSynchronizationContext();
// Captured on UI thread → later code scheduled back to UI thread

// 3. ConcurrentExclusiveSchedulerPair
var pair = new ConcurrentExclusiveSchedulerPair();
TaskScheduler concurrent  = pair.ConcurrentScheduler;   // multiple at a time
TaskScheduler exclusive   = pair.ExclusiveScheduler;    // one at a time

// 4. Throttled concurrent scheduler (max 8 parallel)
var throttledPair = new ConcurrentExclusiveSchedulerPair(
    TaskScheduler.Default, maxConcurrencyLevel: 8);
TaskScheduler throttled = throttledPair.ConcurrentScheduler;
```

```
ConcurrentExclusiveSchedulerPair Rules:
  ┌────────────────────────────────────────────────┐
  │  ConcurrentScheduler: many tasks run at once   │
  │     BUT NOT while ExclusiveScheduler is active │
  │  ExclusiveScheduler: one task at a time        │
  │     AND blocks ConcurrentScheduler             │
  └────────────────────────────────────────────────┘
  Use case: readers (concurrent) + writers (exclusive) pattern
```

---

## Recipe 13.3 — Scheduling Parallel Code

Pass a `TaskScheduler` through `ParallelOptions`.

```csharp
// Limit all nested parallel loops to 8 total concurrent threads
void ProcessNested(IEnumerable<IEnumerable<Matrix>> collections, float degrees)
{
    var pair = new ConcurrentExclusiveSchedulerPair(
        TaskScheduler.Default, maxConcurrencyLevel: 8);
    var options = new ParallelOptions { TaskScheduler = pair.ConcurrentScheduler };

    Parallel.ForEach(collections, options,
        matrices => Parallel.ForEach(matrices, options,
            matrix => matrix.Rotate(degrees)));
}
```

> ⚠️ PLINQ does not support custom `TaskScheduler` — use `Parallel` if you need scheduling control.

---

## Recipe 13.4 — Dataflow Synchronization Using Schedulers

Schedule specific dataflow blocks to specific contexts.

```csharp
// Display results on UI thread by giving the block a UI scheduler
private void SetupDataflowPipeline()
{
    var uiOptions = new ExecutionDataflowBlockOptions
    {
        TaskScheduler = TaskScheduler.FromCurrentSynchronizationContext()
    };

    // This block processes on threadpool (default)
    var computeBlock = new TransformBlock<int, int>(x => x * 2);

    // This block updates UI — runs on UI thread
    var displayBlock = new ActionBlock<int>(
        result => ListBox.Items.Add(result),
        uiOptions);   // ← UI scheduler

    computeBlock.LinkTo(displayBlock,
        new DataflowLinkOptions { PropagateCompletion = true });
}
```

```
COMMON PATTERNS
════════════════════════════════════════════════════
  UI update block        → FromCurrentSynchronizationContext()
  CPU-bound block        → TaskScheduler.Default
  Reader/writer blocks   → ConcurrentExclusiveSchedulerPair
  Throttled pipeline     → ConcurrentExclusiveSchedulerPair(max: N)
```

---

*[← Chapter 12](12-synchronization.md) | [Back to Index](../README.md) | [Chapter 14 — Scenarios →](14-scenarios.md)*
