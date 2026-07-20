# Chapter 6: Goroutines and the Go Runtime

> *"Go has done a wonderful job of wielding some powerful ideas that make your program more performant, but abstracting away these details."*

---

## Core Concept

Go's runtime automatically manages goroutine scheduling through **work stealing** — a sophisticated algorithm that keeps all CPU cores busy without requiring the developer to think about thread management.

---

## 6.1 The Problem with Naive Scheduling

**Fair scheduling** (divide work equally upfront) fails in fork-join models:

```
Fair scheduling with 2 processors (P1, P2):
  Tasks assigned: P1 → [T1, T3], P2 → [T2, T4]

  If T1 depends on T4 (which is on P2):
  Time  P1          P2
  T     T1 BLOCKED  T2
  T+a   T1 BLOCKED  T4
  T+b   T1 RUNS     idle   ← P2 idle! wasted resources

Problems:
  1. Underutilization when tasks have dependencies
  2. Poor cache locality (related data scattered across processors)
  3. A central queue creates a bottleneck under contention
```

---

## 6.2 Work Stealing — Go's Solution

Each OS thread (processor) gets its own **double-ended queue (deque)** of goroutines. The rules:

```
Work Stealing Rules:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. FORK POINT:
   Add new goroutines to the TAIL of my own deque

2. IDLE THREAD:
   Steal goroutines from the HEAD of a random other thread's deque

3. JOIN POINT (not ready):
   Pop work from the TAIL of my own deque (keep working!)

4. MY DEQUE IS EMPTY:
   a. Stall at join point, OR
   b. Steal from HEAD of a random thread's deque
```

```
Visual: Two threads, each with a deque
  
  Thread 1 deque:        Thread 2 deque:
  HEAD [A][B][C] TAIL    HEAD [D][E][F] TAIL
  
  Thread 1 forks G → adds to TAIL:
  HEAD [A][B][C][G] TAIL
  
  Thread 2 is idle → steals from Thread 1's HEAD:
  Thread 1: HEAD [B][C][G] TAIL   (A was stolen)
  Thread 2: HEAD [D][E][F][A] TAIL
```

---

## 6.3 Stealing Tasks vs. Continuations

When goroutine P forks child C, there's a choice of **what to schedule next**:

```
Option A — Steal Tasks (schedule child C immediately):
  P creates C, C runs immediately, P is put on queue
  → More goroutines in the system (higher memory overhead)
  → Less cache-friendly (P's state must be saved and reloaded)

Option B — Steal Continuations (P continues, C queued):
  P creates C, P keeps running, C waits in queue
  → Fewer goroutines alive at once (lower memory overhead)
  → Better cache locality (P keeps its data hot)
  → Go uses this approach!
```

**Why continuations win:**
- The calling goroutine (P) has already loaded its context into cache
- Immediately context-switching to child (C) wastes that warm cache
- Queuing C and letting P continue is more efficient in practice

---

## 6.4 The M:N Scheduler

Go uses an M:N threading model:
- **M** green threads (goroutines)
- **N** OS threads  
- GOMAXPROCS controls N (defaults to number of CPU cores)

```
┌─────────────────────────────────────────┐
│              Go Program                 │
│                                         │
│  G G G G G G G G G G G G G G G G G G   │  ← Goroutines (M)
│  │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │   │
│  └─┴─┴─┴─┘ └─┴─┴─┴─┘ └─┴─┴─┴─┴─┘     │
│      │           │           │          │
│      P           P           P          │  ← Processors (logical)
│      │           │           │          │
│      T           T           T          │  ← OS Threads (N)
└──────┼───────────┼───────────┼──────────┘
       │           │           │
   CPU Core    CPU Core    CPU Core        ← Hardware
```

**What happens when a goroutine blocks?**
- The OS thread parks
- The Go scheduler moves the logical processor to another OS thread
- Other runnable goroutines continue executing
- This is why goroutines can block on I/O without wasting CPU

---

## 6.5 Fibonacci Example — Work Stealing in Action

```go
var fib func(n int) <-chan int
fib = func(n int) <-chan int {
    result := make(chan int)
    go func() {
        defer close(result)
        if n <= 2 {
            result <- 1
            return
        }
        result <- <-fib(n-1) + <-fib(n-2)
    }()
    return result
}
fmt.Printf("fib(4) = %d", <-fib(4))
```

```
Execution trace with 2 threads (T1, T2):

  T1 deque        T2 deque
  [fib(4)]        []

  T1 runs fib(4):
    forks fib(3) → T1 tail: [fib(4-cont), fib(3)]
    forks fib(2) → T1 tail: [fib(4-cont), fib(3), fib(2)]
    T1 blocks at join (waiting for fib(3) and fib(2))

  T1 steals from own tail: runs fib(2) → returns 1
  T2 steals fib(3) from T1's head
  T2 runs fib(3): forks fib(2), fib(1), computes...
  
  → Work distributes naturally across threads
  → No manual thread management required
```

---

## 6.6 What This Means for You

```
PRACTICAL TAKEAWAYS FROM THE RUNTIME:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ START GOROUTINES FREELY
   The scheduler handles distribution across CPUs automatically.
   A goroutine costs ~2.8 KB — start thousands without worry.

✅ DON'T MANAGE OS THREADS
   GOMAXPROCS defaults to NumCPU(). Rarely need to change it.
   The runtime optimizes thread allocation for you.

✅ BLOCKING IS FREE
   When a goroutine blocks (I/O, channel), the thread is reassigned.
   No CPU is wasted waiting.

✅ RUNTIME IMPROVEMENTS ARE FREE UPGRADES
   When Go improves its scheduler (as in Go 1.5+), your program
   gets faster without any code changes.

⚠️  GOMAXPROCS TUNING
   Only useful for specific scenarios (e.g., triggering race
   conditions in tests by exceeding CPU count).
   Always benchmark before and after any change.
```

---

## Visual Summary

```
GO RUNTIME SCHEDULER — HOW IT WORKS
═══════════════════════════════════════════════════════════

ARCHITECTURE:
  M goroutines scheduled onto N OS threads
  Each thread has its own local deque (double-ended queue)
  GOMAXPROCS = number of simultaneously executing threads

WORK STEALING:
  New goroutines → added to TAIL of creator's deque
  Idle threads   → steal from HEAD of random other deque
  At join points → pop from own TAIL (keep working)
  FIFO for stolen work, LIFO for local work (cache-friendly)

KEY INSIGHT — CONTINUATIONS, NOT TASKS:
  When goroutine forks, the PARENT continues (not the child)
  Child is queued for potential stealing
  Parent's cache stays warm → better performance

BLOCKING:
  I/O or channel block → logical processor detaches from thread
  Thread may pick up other goroutines
  Original goroutine resumes when unblocked (possibly on new thread)

RESULT:
  Developers write simple sequential-looking goroutines
  Runtime provides parallel execution automatically
  Near-zero overhead per goroutine (vs. ~1 MB per OS thread)
```

---

*[← Chapter 5 — Concurrency at Scale](05-concurrency-at-scale.md) | [Back to Index](../README.md)*
