# Concurrency in Go

**Author:** Katherine Cox-Buday  
**Publisher:** O'Reilly Media, 2017  
**Topic:** Concurrent programming in Go — patterns, primitives, and production techniques

---

## Why This Book?

Go was designed with concurrency as a first-class concern. This book is the definitive guide to writing correct, composable, and scalable concurrent programs in Go — from the `go` keyword to production-grade patterns like pipelines, rate limiting, and goroutine healing.

---

## Chapter Index

| # | Chapter | Core Topics |
|---|---------|-------------|
| 1 | [An Introduction to Concurrency](chapters/01-introduction-to-concurrency.md) | Race conditions, atomicity, deadlock, livelock, starvation |
| 2 | [Communicating Sequential Processes](chapters/02-communicating-sequential-processes.md) | Concurrency vs. parallelism, CSP, Go's philosophy |
| 3 | [Go's Concurrency Building Blocks](chapters/03-concurrency-building-blocks.md) | Goroutines, channels, select, WaitGroup, Mutex, Pool |
| 4 | [Concurrency Patterns in Go](chapters/04-concurrency-patterns.md) | Pipelines, fan-out/in, or-channel, context package |
| 5 | [Concurrency at Scale](chapters/05-concurrency-at-scale.md) | Error propagation, timeouts, heartbeats, rate limiting, healing |
| 6 | [Goroutines and the Go Runtime](chapters/06-goroutines-and-the-go-runtime.md) | Work stealing, M:N scheduler, continuations |

📌 [Key Takeaways](key-takeaways.md) — The distilled essentials of the entire book

---

## The Core Mental Model

```
CONCURRENCY IN GO — THE THREE LAYERS

┌─────────────────────────────────────────────────────────┐
│  LAYER 3: SCALE                                         │
│  Error propagation · Timeouts · Heartbeats              │
│  Rate limiting · Replicated requests · Healing          │
├─────────────────────────────────────────────────────────┤
│  LAYER 2: PATTERNS                                      │
│  Pipelines · Fan-out/in · Confinement                   │
│  or-channel · tee-channel · context                     │
├─────────────────────────────────────────────────────────┤
│  LAYER 1: PRIMITIVES                                    │
│  goroutine · channel · select                           │
│  WaitGroup · Mutex · Once · Pool                        │
└─────────────────────────────────────────────────────────┘
        Built on: Go Runtime (Work Stealing Scheduler)
```

---

## The One Decision That Matters Most

```
CHANNELS  →  when transferring data ownership between goroutines
MUTEXES   →  when protecting internal state within a type

"Do not communicate by sharing memory.
 Instead, share memory by communicating."
                              — Go Philosophy
```

---

## Key Numbers to Remember

| Metric | Value |
|--------|-------|
| Goroutine size | ~2.8 KB |
| OS thread size | ~1 MB |
| Goroutine context switch | ~225 ns |
| OS thread context switch | ~1,467 ns |
| GC pause (Go 1.8+) | 10–100 μs |
| Goroutines on 8 GB RAM | millions |

---

## Quick Pattern Reference

```go
// 1. Start a goroutine with a join point
var wg sync.WaitGroup
wg.Add(1)
go func() { defer wg.Done(); doWork() }()
wg.Wait()

// 2. The for-select loop (goroutine lifecycle)
for {
    select {
    case <-done: return
    case v := <-stream: process(v)
    }
}

// 3. Pipeline stage
func multiply(done <-chan interface{}, in <-chan int, factor int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for v := range in {
            select {
            case <-done: return
            case out <- v * factor:
            }
        }
    }()
    return out
}

// 4. Context for cancellation + timeout
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()
// pass ctx as first arg to all downstream functions

// 5. Rate limiting
limiter := rate.NewLimiter(rate.Limit(10), 10) // 10/s, burst of 10
if err := limiter.Wait(ctx); err != nil { return err }
```

---

## Reading Guide

| Your Goal | Start Here |
|-----------|-----------|
| New to concurrency | Chapter 1 → 2 → 3 |
| Know basics, want patterns | Chapter 4 |
| Building production systems | Chapter 5 |
| Understanding the internals | Chapter 6 |
| Quick reference | [Key Takeaways](key-takeaways.md) |
