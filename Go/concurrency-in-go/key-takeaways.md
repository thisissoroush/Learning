# Key Takeaways — Concurrency in Go

*Katherine Cox-Buday | O'Reilly, 2017*

---

## 🧠 The Big Ideas

### 1. Concurrency ≠ Parallelism
- **Concurrency** is a property of *your code* — the structure you write
- **Parallelism** is a property of the *running program* — whether it actually runs simultaneously
- You write concurrent code; the runtime decides if/how it runs in parallel
- Go lets you be productively ignorant of this distinction most of the time

### 2. Go's Philosophy: Share Memory by Communicating
> *"Do not communicate by sharing memory. Instead, share memory by communicating."*
- Channels transfer ownership of data — only one goroutine "owns" data at a time
- This eliminates most race conditions by design
- Mutexes are for protecting internal struct state; channels are for everything else

### 3. Goroutines Are Cheap — Use Them
- ~2.8 KB per goroutine (vs ~1 MB per OS thread)
- Context switch: ~225 ns (vs ~1,467 ns for OS threads — 6× faster)
- On 8 GB RAM: potentially millions of goroutines
- Rule: model problems with one goroutine per concurrent unit of work

---

## ⚠️ Concurrency Is Hard — Know the Pitfalls

### Race Conditions
```go
// WRONG: no guarantee which runs first
var data int
go func() { data++ }()
if data == 0 { fmt.Println(data) }  // could print 0 or 1 or nothing

// Sleeps are NOT a fix — only logical correctness is
time.Sleep(1 * time.Second)  // still a race condition, just less likely
```

### Atomicity Is Context-Dependent
- `i++` is *not* atomic — it's three operations: read, increment, store
- Combining atomic operations doesn't produce a larger atomic operation
- Define your scope first, then determine what atomicity means within it

### The Four Deadlock Conditions (Coffman)
Any deadlock requires ALL four:
1. **Mutual Exclusion** — exclusive resource access
2. **Wait For Condition** — holding resource while waiting for another
3. **No Preemption** — resources can't be taken away
4. **Circular Wait** — circular chain of waiting

*Eliminate any one of these to prevent deadlock.*

### Livelock vs. Starvation
- **Livelock**: everyone is active but no progress (two people in a hallway)
- **Starvation**: greedy goroutine prevents others from getting CPU time
- Both are correctness problems, not just performance issues

---

## 🔧 Building Blocks

### Goroutines
```go
go func() { /* concurrent */ }()              // fork
var wg sync.WaitGroup; wg.Wait()              // join
```
- Always create a join point — `time.Sleep` is NOT a join point
- Closures capture *references* not values — shadow loop variables!

### Channels
```go
ch := make(chan int)       // unbuffered: synchronizes
ch := make(chan int, n)    // buffered: n items before blocking
close(ch)                  // signal no more values
for v := range ch { }      // receive until closed
```
- **Channel ownership rule**: creator writes and closes; consumers read only
- Use `chan<- T` / `<-chan T` types to enforce this at compile time
- Closing a channel unblocks *all* waiting receivers simultaneously

### sync Package Decision Matrix
| Situation | Use |
|-----------|-----|
| Waiting for goroutines to finish | `sync.WaitGroup` |
| Protecting shared struct fields | `sync.Mutex` or `sync.RWMutex` |
| Waiting for a condition to change | `sync.Cond` |
| Initialize something exactly once | `sync.Once` |
| Pool of reusable expensive objects | `sync.Pool` |
| Transfer data between goroutines | `channel` |

### select Statement
- Waits on multiple channels simultaneously
- If multiple ready: **random uniform selection** (not sequential)
- `default` clause: non-blocking check
- `time.After(d)`: timeout pattern inside select

---

## 🏗️ Patterns to Know

### 1. The for-select Loop (universal goroutine body)
```go
for {
    select {
    case <-done: return
    default: doWork()
    }
}
```

### 2. Goroutine Leak Prevention
- **Rule**: if a goroutine creates a goroutine, it must be able to stop it
- Always pass a `done <-chan interface{}` channel as first parameter
- Goroutines block on nil channels — always check before passing

### 3. Pipelines
- Generator → Stage → Stage → Stage → Consumer
- Each stage is a goroutine; channel connects them
- All stages become preemptable via `done` channel
- Fan-out: run N copies of expensive stage; fan-in: merge results

### 4. Error Handling
```go
// WRONG: goroutine swallows or prints errors
// RIGHT: return errors paired with results
type Result struct {
    Error    error
    Response *http.Response
}
// Caller has full context to decide what to do
```

### 5. context Package
```go
ctx, cancel := context.WithCancel(context.Background())
defer cancel()
ctx, cancel = context.WithTimeout(ctx, 5*time.Second)
// Pass ctx as first arg to all functions; never store it in a struct
```
- `Done()`: channel closed on cancellation
- `Err()`: why it was canceled
- `Deadline()`: check if deadline is achievable before doing work
- `Value()`: request-scoped metadata (not optional parameters!)

---

## 📈 Scaling Patterns

### Error Propagation Framework
```
Every error is one of two types:
  BUG          → raw error → show "unexpected error" to user, log details
  KNOWN CASE   → wrapped error → show specific message to user
```
- Wrap errors at module boundaries with context + stack trace
- Include: what happened, when/where, user message, log ID

### Heartbeats (for liveness detection)
- **Interval-based**: goroutine signals it's alive even when idle
- **Per-work-unit**: goroutine signals before each item (great for tests!)
- Makes tests deterministic — wait for heartbeat, not `time.Sleep`

### Rate Limiting (Token Bucket)
- `d` = bucket depth (burst capacity)
- `r` = refill rate (sustained throughput)
- Use `golang.org/x/time/rate`; compose `MultiLimiter` for tiers
- Apply per-second AND per-minute limits; per-resource limits

### Healing Goroutines (Steward/Ward Pattern)
- **Steward**: monitors ward via heartbeat; restarts if unhealthy
- **Ward**: does the actual work; exposes heartbeat channel
- Steward itself returns `startGoroutineFn` — it's also monitorable

---

## 🚀 The Go Runtime

### Work Stealing Scheduler
- Each thread has its own deque; idle threads steal from others
- New goroutines go to **tail** of creator's deque (LIFO — cache friendly)
- Stolen goroutines taken from **head** (FIFO — fair)
- When goroutine blocks: thread released, other goroutines continue

### Key Numbers
```
Goroutine memory:    ~2.8 KB
OS thread memory:    ~1 MB
Goroutine ctx switch: ~225 ns
OS thread ctx switch: ~1,467 ns
GC pause (Go 1.8+):  10–100 μs
```

---

## 💬 Memorable Quotes

> *"Concurrency is a property of the code; parallelism is a property of the running program."*

> *"The free lunch is over: a fundamental turn toward concurrency in software."* — Herb Sutter, 2005

> *"Do not communicate by sharing memory. Instead, share memory by communicating."* — Go Philosophy

> *"Go's philosophy on concurrency can be summed up like this: aim for simplicity, use channels when possible, and treat goroutines like a free resource."*

---

## 🎯 Decision Guide

```
When to use CHANNELS vs MUTEXES:
  → Transferring ownership of data?        → CHANNEL
  → Protecting internal struct state?      → MUTEX
  → Coordinating multiple pieces of logic? → CHANNEL
  → Performance-critical tight loop?       → MUTEX (channels use mutexes internally)

When to use GOROUTINES:
  → Any task that can run independently    → goroutine
  → Each web request, each user session    → goroutine
  → Fan-out of expensive computation       → goroutine
  → Don't pre-optimize goroutine count!

When to RATE LIMIT:
  → Accepting external API connections     → always
  → Accessing shared resources             → always
  → Protecting your system from yourself   → yes, even then
```
