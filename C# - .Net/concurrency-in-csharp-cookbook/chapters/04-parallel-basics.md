# Chapter 4: Parallel Basics

> *"The chunks of work should be as independent from one another as possible."*

---

## Core Concept

Parallel programming uses **multiple CPU cores simultaneously** to complete CPU-bound work faster. The key: divide independent work among threads. If your work isn't independent (threads share state), you get bugs. If your work is I/O-bound, use `async` instead.

```
When to use Parallel:
  ✅ CPU-intensive computation (image processing, math, encryption)
  ✅ Large collections of independent items to process
  ✅ Work that can be split and doesn't share mutable state
  ❌ I/O-bound work (use async/await instead)
  ❌ Server-side code (server already has built-in parallelism)
  ❌ Work items with shared mutable state (use locks → reduces benefit)
```

---

## Recipe 4.1 — Parallel Processing of Data

**Problem:** Process a large collection, doing the same operation on each element.

**Solution:** `Parallel.ForEach`

```csharp
// Basic parallel foreach
Parallel.ForEach(matrices, matrix => matrix.Rotate(degrees));

// With early stopping (from inside the loop)
Parallel.ForEach(matrices, (matrix, state) =>
{
    if (!matrix.IsInvertible)
        state.Stop();   // signal other iterations to stop starting
    else
        matrix.Invert();
});

// With cancellation (from outside the loop)
Parallel.ForEach(
    matrices,
    new ParallelOptions { CancellationToken = token },
    matrix => matrix.Rotate(degrees));

// With shared state (use a lock to protect it)
int failCount = 0;
object mutex = new object();
Parallel.ForEach(matrices, matrix =>
{
    if (!matrix.IsInvertible)
    {
        lock (mutex)
            failCount++;   // only lock when writing shared state
    }
    else
        matrix.Invert();
});
```

```
Parallel.ForEach threading model:
  Collection: [A, B, C, D, E, F, G, H]
                ↓ divided automatically
  Thread 1: [A, B]   Thread 2: [C, D]   Thread 3: [E, F]   Thread 4: [G, H]
                ↓ run concurrently on multiple cores
  Results collected / side effects applied
```

> 💡 **Parallel.ForEach vs PLINQ:** `Parallel` plays nicer with other processes (dynamic work stealing). PLINQ tries to saturate all cores by default but has cleaner LINQ syntax. Use whichever feels more natural.

> ⚠️ `state.Stop()` doesn't cancel already-running iterations — it prevents new ones from starting. Other threads may still process items after Stop() is called.

---

## Recipe 4.2 — Parallel Aggregation

**Problem:** Sum, average, or aggregate results from parallel processing.

**Solution:** Use local values in `Parallel.ForEach`, or PLINQ aggregation operators.

```csharp
// Parallel.ForEach with local aggregation (thread-local partial results)
int ParallelSum(IEnumerable<int> values)
{
    object mutex = new object();
    int result = 0;
    Parallel.ForEach(
        source: values,
        localInit: () => 0,                            // each thread starts at 0
        body: (item, state, localValue) =>
            localValue + item,                         // add to local (no lock!)
        localFinally: localValue =>
        {
            lock (mutex) result += localValue;         // merge locals (lock once per thread)
        });
    return result;
}

// PLINQ — much simpler for standard aggregations
int sum = values.AsParallel().Sum();
double avg = values.AsParallel().Average();

// PLINQ custom aggregation
int product = values.AsParallel().Aggregate(
    seed: 1,
    func: (acc, item) => acc * item);
```

```
Local value pattern eliminates lock contention:
  Thread 1: 1+2+3+4 = 10  (local, no lock)
  Thread 2: 5+6+7+8 = 26  (local, no lock)
  Thread 3: 9+10    = 19  (local, no lock)
        ↓ each thread locks once to merge
  result = 10 + 26 + 19 = 55
```

---

## Recipe 4.3 — Parallel Invocation

**Problem:** Call several independent methods in parallel.

**Solution:** `Parallel.Invoke`

```csharp
// Two halves of an array processed simultaneously
Parallel.Invoke(
    () => ProcessPartialArray(array, 0, array.Length / 2),
    () => ProcessPartialArray(array, array.Length / 2, array.Length));

// Dynamic number of actions
Action[] actions = Enumerable.Repeat(expensiveAction, 20).ToArray();
Parallel.Invoke(actions);

// With cancellation
Parallel.Invoke(
    new ParallelOptions { CancellationToken = token },
    () => DoWork1(),
    () => DoWork2());
```

> 💡 Use `Parallel.Invoke` when you have a fixed, known set of independent operations. Use `Parallel.ForEach` when you're iterating over a data collection.

---

## Recipe 4.4 — Dynamic Parallelism

**Problem:** The number and structure of parallel tasks isn't known until runtime (e.g., a tree traversal).

**Solution:** Use `Task` directly with `TaskCreationOptions.AttachedToParent`.

```csharp
// Parallel tree traversal — structure determined at runtime
void Traverse(Node current)
{
    DoExpensiveWork(current);

    if (current.Left != null)
        Task.Factory.StartNew(
            () => Traverse(current.Left),
            CancellationToken.None,
            TaskCreationOptions.AttachedToParent,   // ← links to parent task
            TaskScheduler.Default);

    if (current.Right != null)
        Task.Factory.StartNew(
            () => Traverse(current.Right),
            CancellationToken.None,
            TaskCreationOptions.AttachedToParent,
            TaskScheduler.Default);
}

void ProcessTree(Node root)
{
    Task task = Task.Factory.StartNew(
        () => Traverse(root),
        CancellationToken.None,
        TaskCreationOptions.None,
        TaskScheduler.Default);

    task.Wait();   // waits for root AND all attached children
}
```

```
AttachedToParent — parent waits for all children:
  Root Task
  ├── Child Task (left subtree)
  │   ├── Child Task (left-left)
  │   └── Child Task (left-right)
  └── Child Task (right subtree)

  root.Wait() blocks until every node in the whole tree is done.
  Exceptions from children propagate to parent → to root.
```

> ⚠️ **Parallel tasks vs Async tasks:** Don't mix them up.
> - Parallel task: `Task.Run` or `Task.Factory.StartNew`, uses `.Wait()`, `.Result`
> - Async task: uses `await`, never `.Wait()`

---

## Recipe 4.5 — Parallel LINQ (PLINQ)

**Problem:** You have LINQ queries over large data sets and want to parallelize them.

**Solution:** Add `.AsParallel()` to your LINQ query.

```csharp
// Simple multiplication — unordered (fastest)
IEnumerable<int> doubled = values.AsParallel()
    .Select(v => v * 2);

// Preserve original order (slightly slower, uses extra memory)
IEnumerable<int> orderedDoubled = values.AsParallel()
    .AsOrdered()
    .Select(v => v * 2);

// Parallel sum
int total = values.AsParallel().Sum();

// Primality filter
IEnumerable<int> primes = values.AsParallel()
    .Where(v => IsPrime(v));

// With cancellation
IEnumerable<int> results = values.AsParallel()
    .WithCancellation(token)
    .Select(v => ExpensiveCompute(v));
```

```
PLINQ vs Parallel class comparison:
  ┌──────────────────────┬──────────────────────────────┐
  │ Parallel class       │ PLINQ                        │
  ├──────────────────────┼──────────────────────────────┤
  │ More resource-friendly│ Tries to use all cores      │
  │ Imperative style     │ Declarative/LINQ style       │
  │ Good for side effects│ Good for transformations     │
  │ ForEach, Invoke, For │ AsParallel(), AsOrdered()    │
  └──────────────────────┴──────────────────────────────┘
```

> ⚠️ By default, PLINQ doesn't preserve order. Add `.AsOrdered()` if order matters — but this has a performance cost.

> 💡 **Task granularity:** Tasks that are too short (microseconds) waste overhead on scheduling. Tasks that are too long prevent dynamic load balancing. Aim for tasks that run for at least a millisecond.

---

## Visual Summary

```
PARALLEL DECISION TREE
══════════════════════════════════════════════════════════════

Is the work CPU-bound?  ──NO──→ Use async/await instead
       │YES
       ▼
Is the number of tasks known upfront?
  YES → Fixed tasks → Parallel.Invoke()
  YES → Data collection → Parallel.ForEach() or PLINQ
  NO  → Dynamic/tree → Task with AttachedToParent

Need aggregation? → Use localInit/localFinally or PLINQ .Sum()/.Aggregate()
Need ordering?    → PLINQ .AsOrdered()
Need cancellation?→ ParallelOptions { CancellationToken = token }
```

---

*[← Chapter 3](03-asynchronous-streams.md) | [Back to Index](../README.md) | [Chapter 5 — Dataflow Basics →](05-dataflow-basics.md)*
