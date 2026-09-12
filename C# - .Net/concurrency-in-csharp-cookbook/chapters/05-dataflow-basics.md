# Chapter 5: Dataflow Basics

> *"Dataflow is a very declarative style of coding: normally, you completely define the mesh first and then start processing data."*

---

## Core Concept

TPL Dataflow models computation as a **mesh (graph) of blocks** — each block independently processes data and passes results to linked blocks. Think of it as an actor framework or pipeline where you wire up the topology once, then push data through.

```
Simple Pipeline:
  [Input] → [TransformBlock A] → [TransformBlock B] → [ActionBlock]
               multiply×2          subtract 2          print result

Branching (Fork):
  [Source] → [Target A]
           ↘ [Target B]

Joining:
  [Source A] ↘
              [JoinBlock] → [Target]
  [Source B] ↗

NuGet: System.Threading.Tasks.Dataflow
```

---

## Recipe 5.1 — Linking Blocks

**Problem:** Connect dataflow blocks into a pipeline.

**Solution:** `LinkTo` extension method, with `PropagateCompletion = true` for pipelines.

```csharp
var multiplyBlock = new TransformBlock<int, int>(item => item * 2);
var subtractBlock = new TransformBlock<int, int>(item => item - 2);
var printBlock    = new ActionBlock<int>(item => Console.WriteLine(item));

// Link with completion propagation
var options = new DataflowLinkOptions { PropagateCompletion = true };
multiplyBlock.LinkTo(subtractBlock, options);
subtractBlock.LinkTo(printBlock, options);

// Feed data
multiplyBlock.Post(5);    // → multiply: 10 → subtract: 8 → print: 8
multiplyBlock.Post(3);    // → multiply:  6 → subtract: 4 → print: 4

// Signal end of input — completion propagates through the chain
multiplyBlock.Complete();
await printBlock.Completion;   // wait for everything to finish
```

```
Completion flow with PropagateCompletion = true:
  multiplyBlock.Complete() called
       │
       ▼ (after processing all buffered items)
  subtractBlock faults/completes
       │
       ▼
  printBlock faults/completes
       │
       ▼
  printBlock.Completion task completes — we can await this
```

> 💡 Use `LinkTo` with a **filter predicate** to route different data to different blocks:
> ```csharp
> sourceBlock.LinkTo(evenBlock, item => item % 2 == 0);
> sourceBlock.LinkTo(oddBlock,  item => item % 2 != 0);
> ```
> Items that don't match any filter stay in the source block and stall it!

---

## Recipe 5.2 — Propagating Errors

**Problem:** Handle exceptions thrown inside dataflow block delegates.

**Solution:** Await `block.Completion` and catch exceptions there.

```csharp
var block = new TransformBlock<int, int>(item =>
{
    if (item == 0)
        throw new DivideByZeroException();
    return 100 / item;
});

block.Post(0);   // this will fault the block

try
{
    await block.Completion;
}
catch (DivideByZeroException ex)
{
    Console.WriteLine($"Block faulted: {ex.Message}");
}

// In a pipeline — exceptions wrapped in AggregateException per link
try
{
    var multiplyBlock = new TransformBlock<int, int>(item =>
    {
        if (item == 1) throw new InvalidOperationException("Bad item");
        return item * 2;
    });
    var printBlock = new ActionBlock<int>(item => Console.WriteLine(item));
    multiplyBlock.LinkTo(printBlock, new DataflowLinkOptions { PropagateCompletion = true });

    multiplyBlock.Post(1);
    await printBlock.Completion;
}
catch (AggregateException ex)
{
    // Flatten nested AggregateExceptions from multi-hop pipelines
    var flat = ex.Flatten();
    Console.WriteLine(flat.InnerException);
}
```

```
Error propagation through pipeline:
  Block A throws InvalidOperationException
       │ wrapped in AggregateException
       ▼
  Block B faults with AggregateException(InvalidOperationException)
       │ wrapped again
       ▼
  Block C faults with AggregateException(AggregateException(InvalidOpEx))

  Use ex.Flatten() to unwrap nesting → InnerException is the original
```

> ⚠️ When a block faults, it **drops all buffered data** and stops accepting new items.

---

## Recipe 5.3 — Unlinking Blocks

**Problem:** Dynamically change the dataflow structure at runtime.

**Solution:** Store the `IDisposable` returned by `LinkTo` and dispose it to unlink.

```csharp
var source = new TransformBlock<int, int>(item => item * 2);
var target = new BufferBlock<int>();

IDisposable link = source.LinkTo(target);

source.Post(1);
source.Post(2);

// Dynamically remove the link
link.Dispose();   // items posted after this may or may not have crossed the link
```

> ⚠️ Race conditions around unlinking are generally safe — no data duplication or loss, but items may or may not cross the link depending on timing.

---

## Recipe 5.4 — Throttling Blocks (BoundedCapacity)

**Problem:** In a fork scenario, the first target block greedily buffers everything, starving the second block.

**Solution:** Set `BoundedCapacity` to limit buffer size, forcing load balancing.

```csharp
var source = new BufferBlock<int>();

// Without BoundedCapacity: target A gets all items, target B gets none
// With BoundedCapacity = 1: source offers to A, if A is full → tries B
var opts = new DataflowBlockOptions { BoundedCapacity = 1 };
var targetA = new BufferBlock<int>(opts);
var targetB = new BufferBlock<int>(opts);

source.LinkTo(targetA);
source.LinkTo(targetB);

// Now data distributes between A and B
for (int i = 0; i < 10; i++)
    await source.SendAsync(i);   // SendAsync respects backpressure
```

```
Without BoundedCapacity (greedy):          With BoundedCapacity = 1:
  source → [A: 1,2,3,4,5,6,7,8,9,10]       source → [A: 1,3,5,7,9] 
           [B: (empty)]                              [B: 2,4,6,8,10]
```

> 💡 `Post()` is fire-and-forget. `await SendAsync()` respects backpressure — it waits until there's room in the block's buffer.

---

## Recipe 5.5 — Parallel Processing in Dataflow

**Problem:** A specific block is a bottleneck and needs to process items in parallel.

**Solution:** Set `MaxDegreeOfParallelism` on the block's options.

```csharp
var multiplyBlock = new TransformBlock<int, int>(
    item => item * 2,
    new ExecutionDataflowBlockOptions
    {
        MaxDegreeOfParallelism = 4   // process up to 4 items simultaneously
    });

// Default is 1 — sequential within the block
// DataflowBlockOptions.Unbounded = no limit
```

> 💡 Even without `MaxDegreeOfParallelism`, multiple blocks in a pipeline run concurrently — block A processes item N+1 while block B processes item N.

---

## Recipe 5.6 — Custom Blocks

**Problem:** You want to encapsulate a reusable sub-mesh as a single block.

**Solution:** Use `DataflowBlock.Encapsulate` to wrap a sub-mesh with one input and one output.

```csharp
IPropagatorBlock<int, int> CreateMyCustomBlock()
{
    var multiplyBlock = new TransformBlock<int, int>(item => item * 2);
    var addBlock      = new TransformBlock<int, int>(item => item + 2);
    var divideBlock   = new TransformBlock<int, int>(item => item / 2);

    var flowCompletion = new DataflowLinkOptions { PropagateCompletion = true };
    multiplyBlock.LinkTo(addBlock, flowCompletion);
    addBlock.LinkTo(divideBlock, flowCompletion);

    // First block = input, Last block = output
    return DataflowBlock.Encapsulate(multiplyBlock, divideBlock);
}

// Usage is identical to a built-in block
var myBlock = CreateMyCustomBlock();
myBlock.Post(4);    // internally: 4×2=8, 8+2=10, 10/2=5
myBlock.Complete();
int result = await myBlock.ReceiveAsync();   // 5
```

---

## Visual Summary

```
DATAFLOW BLOCK TYPES
══════════════════════════════════════════════════════════════

TransformBlock<TIn, TOut>      Input + transform + output
                                (like LINQ Select)

TransformManyBlock<TIn, TOut>  Input + transform → many outputs
                                (like LINQ SelectMany)

ActionBlock<T>                 Input + terminal action, no output
                                (sink / final step)

BufferBlock<T>                 Simple queue / passthrough

BatchBlock<T>                  Collects N items → outputs T[]

JoinBlock<T1, T2>              Waits for one from each input,
                                outputs Tuple<T1,T2>

KEY OPTIONS:
  BoundedCapacity         = max buffer size (throttling)
  MaxDegreeOfParallelism  = concurrent items per block
  CancellationToken       = cancel the block
  PropagateCompletion     = auto-complete downstream blocks
```

---

*[← Chapter 4](04-parallel-basics.md) | [Back to Index](../README.md) | [Chapter 6 — System.Reactive Basics →](06-system-reactive-basics.md)*
