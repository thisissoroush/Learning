# Chapter 9: Collections

> *"Using the proper collections is essential in concurrent applications."*

---

## Core Concept

Three families of collections for concurrent code:

```
COLLECTION FAMILIES
═══════════════════════════════════════════════════════════

1. IMMUTABLE COLLECTIONS           (System.Collections.Immutable NuGet)
   Never change → naturally thread-safe → share memory between versions
   ImmutableStack, ImmutableQueue, ImmutableList, ImmutableHashSet,
   ImmutableSortedSet, ImmutableDictionary, ImmutableSortedDictionary

2. THREADSAFE (CONCURRENT) COLLECTIONS  (built into .NET)
   Multiple threads read/write simultaneously → fine-grained locks
   ConcurrentDictionary, ConcurrentStack, ConcurrentQueue, ConcurrentBag

3. PRODUCER/CONSUMER COLLECTIONS
   Bridge between producer code and consumer code
   Channel<T>                  (System.Threading.Channels NuGet)
   BlockingCollection<T>       (built-in, synchronous)
   BufferBlock<T>              (TPL Dataflow NuGet)
   AsyncProducerConsumerQueue  (Nito.AsyncEx NuGet)
```

---

## Immutable Collections

### Recipe 9.1 — Immutable Stacks and Queues

```csharp
// Stack: last-in, first-out — each operation returns NEW stack
ImmutableStack<int> stack = ImmutableStack<int>.Empty;
stack = stack.Push(13);
stack = stack.Push(7);
// foreach prints: 7, 13 (top first)

stack = stack.Pop(out int top);  // top == 7, original stack unchanged

// Snapshots share memory — efficient!
ImmutableStack<int> a = ImmutableStack<int>.Empty.Push(1);
ImmutableStack<int> b = a.Push(2);  // b shares "1" node with a
```

```csharp
// Queue: first-in, first-out
ImmutableQueue<int> queue = ImmutableQueue<int>.Empty;
queue = queue.Enqueue(13).Enqueue(7);
queue = queue.Dequeue(out int first);  // first == 13
```

> 💡 Immutable collections are great for snapshots and functional code. Don't use them as communication conduits between threads — use producer/consumer queues for that.

### Recipe 9.2 — Immutable Lists

```csharp
ImmutableList<int> list = ImmutableList<int>.Empty;
list = list.Insert(0, 7).Insert(1, 13);  // [7, 13]
list = list.RemoveAt(1);                  // [7]

// ⚠️ Performance difference vs List<T>:
//   list[i]   → O(log N) — NOT O(1)!  (internally a binary tree)
//   foreach   → O(N)    — OK
//   for (i++) → O(N log N) — SLOW, avoid!

foreach (var item in list)  // Always prefer foreach over indexed for loop
    Console.WriteLine(item);
```

### Recipe 9.3 — Immutable Sets

```csharp
// Unordered (prefer unless sorting needed)
ImmutableHashSet<int> set = ImmutableHashSet<int>.Empty;
set = set.Add(7).Add(13).Add(7);  // {7, 13} — no duplicates
set = set.Remove(7);

// Sorted (supports indexing like ImmutableList)
ImmutableSortedSet<int> sorted = ImmutableSortedSet<int>.Empty;
sorted = sorted.Add(13).Add(7);    // internally sorted: [7, 13]
int smallest = sorted[0];          // 7 — but O(log N)!
```

### Recipe 9.4 — Immutable Dictionaries

```csharp
ImmutableDictionary<int, string> dict = ImmutableDictionary<int, string>.Empty;
dict = dict.Add(1, "One").Add(2, "Two");
dict = dict.SetItem(1, "Uno");       // update — returns new dict
string val = dict[1];                // "Uno"
dict = dict.Remove(2);

// Use Builder for bulk population (efficient)
var builder = ImmutableDictionary.CreateBuilder<int, string>();
builder.Add(1, "One");
builder.Add(2, "Two");
ImmutableDictionary<int, string> builtDict = builder.ToImmutable();
```

---

## Threadsafe Collections

### Recipe 9.5 — Threadsafe Dictionaries (ConcurrentDictionary)

```csharp
var cache = new ConcurrentDictionary<string, string>();

// AddOrUpdate — handles both add and update atomically
string result = cache.AddOrUpdate(
    key:         "greeting",
    addValue:    "Hello",           // used if key doesn't exist
    updateValueFactory: (k, old) => old + "!");  // used if key exists

// TryGetValue — safe read
if (cache.TryGetValue("greeting", out string value))
    Console.WriteLine(value);

// TryRemove
cache.TryRemove("greeting", out string removed);

// Index syntax (simple add/update without conditional logic)
cache["greeting"] = "Hi";

// GetOrAdd — add only if missing
string existing = cache.GetOrAdd("greeting", key => "Hello " + key);
```

> ⚠️ `AddOrUpdate` delegates may be called multiple times — keep them pure (no side effects).

---

## Producer/Consumer Collections

### Recipe 9.6 — Blocking Queues (BlockingCollection)

```csharp
// Shared between producer and consumer threads
var queue = new BlockingCollection<int>();  // unbounded FIFO by default

// Producer thread
Task.Run(() =>
{
    queue.Add(1);
    queue.Add(2);
    queue.CompleteAdding();  // signal "no more items"
});

// Consumer thread — blocks waiting for items
foreach (int item in queue.GetConsumingEnumerable())
    Console.WriteLine(item);   // 1, 2

// With throttling (bounded capacity)
var bounded = new BlockingCollection<int>(boundedCapacity: 10);
```

### Recipe 9.7 — Blocking Stacks and Bags

```csharp
// Stack (LIFO) semantics
var stack = new BlockingCollection<int>(new ConcurrentStack<int>());

// Bag (unordered) semantics
var bag = new BlockingCollection<int>(new ConcurrentBag<int>());

// Usage same as blocking queue
stack.Add(1); stack.Add(2); stack.CompleteAdding();
foreach (int item in stack.GetConsumingEnumerable())
    Console.WriteLine(item);  // 2, 1 (LIFO order if single-threaded)
```

### Recipe 9.8 — Asynchronous Queues (Channels)

```csharp
// Unbounded channel (no backpressure)
Channel<int> ch = Channel.CreateUnbounded<int>();

// Producer
ChannelWriter<int> writer = ch.Writer;
await writer.WriteAsync(7);
await writer.WriteAsync(13);
writer.Complete();

// Consumer — modern async stream
await foreach (int item in ch.Reader.ReadAllAsync())
    Console.WriteLine(item);   // 7, 13

// Consumer — older platform pattern
ChannelReader<int> reader = ch.Reader;
while (await reader.WaitToReadAsync())
    while (reader.TryRead(out int val))
        Console.WriteLine(val);
```

### Recipe 9.9 — Throttling Queues

```csharp
// Bounded channel — producer is throttled (async backpressure)
Channel<int> ch = Channel.CreateBounded<int>(capacity: 10);
await writer.WriteAsync(item);   // waits if channel is full

// Bounded BlockingCollection — producer is throttled (sync backpressure)
var queue = new BlockingCollection<int>(boundedCapacity: 10);
queue.Add(item);  // blocks if full

// Bounded BufferBlock — async backpressure
var block = new BufferBlock<int>(new DataflowBlockOptions { BoundedCapacity = 10 });
await block.SendAsync(item);  // waits if full
```

### Recipe 9.10 — Sampling Queues (Drop When Full)

```csharp
// Drop OLDEST items when full (keep latest)
Channel<int> ch = Channel.CreateBounded<int>(new BoundedChannelOptions(10)
{
    FullMode = BoundedChannelFullMode.DropOldest
});

// Drop NEW (incoming) items when full (keep existing)
Channel<int> ch2 = Channel.CreateBounded<int>(new BoundedChannelOptions(10)
{
    FullMode = BoundedChannelFullMode.DropWrite
});

// Both WriteAsync calls complete immediately (no backpressure)
await writer.WriteAsync(7);   // stored
await writer.WriteAsync(13);  // 7 dropped if channel was full (DropOldest)
```

```
Throttle vs Sample:
  Throttle (Bounded + backpressure): producer SLOWS DOWN when full
  Sample   (Bounded + DropOldest):   producer keeps speed, old data DISCARDED
```

### Recipe 9.11 — Async Stacks and Bags (AsyncCollection)

```csharp
// From Nito.AsyncEx — async equivalent of BlockingCollection
var asyncStack = new AsyncCollection<int>(new ConcurrentStack<int>());
var asyncBag   = new AsyncCollection<int>(new ConcurrentBag<int>());

// Producer
await asyncStack.AddAsync(7);
await asyncStack.AddAsync(13);
asyncStack.CompleteAdding();

// Consumer
while (await asyncStack.OutputAvailableAsync())
    Console.WriteLine(await asyncStack.TakeAsync());  // 13, 7 (LIFO)
```

### Recipe 9.12 — Blocking/Async Queues (Best of Both)

```csharp
// BufferBlock<T> — supports both sync and async APIs
var queue = new BufferBlock<int>();

// Async producer
await queue.SendAsync(7);

// Sync producer
queue.Post(13);
queue.Complete();

// Async consumer
while (await queue.OutputAvailableAsync())
    Console.WriteLine(await queue.ReceiveAsync());

// OR — ActionBlock (defines consumer inline, most "dataflow" way)
var actionBlock = new ActionBlock<int>(item => Console.WriteLine(item));
await actionBlock.SendAsync(7);
actionBlock.Complete();
await actionBlock.Completion;
```

---

## Quick Reference: Which Collection to Use?

```
NEED                                USE
────────────────────────────────────────────────────────
Thread-safe, shared-state dict       ConcurrentDictionary<K,V>
Immutable, rarely-changing data      Immutable* collections
Async producer/consumer (modern)     Channel<T>
Sync producer/consumer               BlockingCollection<T>
Dataflow pipeline                    BufferBlock<T> / ActionBlock<T>
Drop items when too many             Channel<T> with BoundedChannelOptions
Both sync + async producer/consumer  BufferBlock<T>
Async stack/bag                      AsyncCollection<T> (Nito.AsyncEx)
```

---

*[← Chapter 8](08-interop.md) | [Back to Index](../README.md) | [Chapter 10 — Cancellation →](10-cancellation.md)*
