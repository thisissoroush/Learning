# Chapter 1: An Introduction to Concurrency

> *"Concurrent code is notoriously difficult to get right. It usually takes a few iterations to get it working as expected, and even then it's not uncommon for bugs to exist in code for years before some change in timing causes a previously undiscovered bug to rear its head."*

---

## Core Concept

Concurrency is hard — not because Go makes it hard, but because the *nature* of concurrent systems creates fundamental problems. Before writing concurrent code, you must understand exactly what can go wrong. This chapter maps the full danger zone.

---

## 1.1 Why Concurrency Matters Now

### The Moore's Law Problem

For decades, programs got faster for free — CPUs doubled in speed every 18 months (Moore's Law). Around **2012, that ended**. CPU clock speeds plateaued. Instead, hardware vendors added more *cores*.

```
Historical CPU Speed:
   1965: Moore predicts component doubling each year
   1975: Revised to doubling every 2 years
   ~2012: Physical limits hit — horizontal scaling begins
   Today: 4, 8, 16, 32, 64 core machines are common
```

The implication: **your program must use all those cores or fall behind competitors who do**.

### Amdahl's Law — The Ceiling of Parallelism

Not all work can be parallelized. Amdahl's Law says:

```
Speed-up is bounded by the sequential portion of the program.

If 50% of your code is sequential:
  → Maximum possible speed-up = 2x (even with infinite CPUs)

If 95% of your code is parallelizable:
  → With 20 CPUs: near 20x speed-up
  → With 1000 CPUs: ~20x speed-up (still bounded by the 5%)
```

The takeaway: identify whether your problem is *embarrassingly parallel* (like calculating pi digits) or inherently sequential (like waiting for user input).

---

## 1.2 Why Is Concurrency Hard?

### ⚠️ Race Conditions

A **race condition** occurs when two or more operations must execute in a specific order, but the program doesn't guarantee that order.

```go
var data int
go func() {
    data++         // goroutine writes
}()
if data == 0 {
    fmt.Printf("the value is %v.\n", data)  // main reads
}
```

Three possible outcomes — all valid from the program's perspective:
```
Outcome 1: "the value is 0."  (goroutine didn't run yet)
Outcome 2: nothing printed    (goroutine ran before if statement)
Outcome 3: "the value is 1."  (goroutine ran between if and Printf)
```

> ⚠️ **The sleep trap:** Adding `time.Sleep` doesn't fix race conditions — it just makes them *less likely* to surface. Your probability asymptotically approaches correctness, but never reaches it.

```go
// WRONG: This looks like it works but is still a data race
go func() { data++ }()
time.Sleep(1 * time.Second) // ← only increases probability, never guarantees
if data == 0 { ... }
```

### ⚠️ Atomicity

An operation is **atomic** if it is indivisible within a given context — nothing can interrupt it mid-execution.

```
i++   looks atomic, but it's actually THREE operations:
  1. Read value of i
  2. Increment by 1
  3. Store new value back

If two goroutines do this simultaneously:
  Goroutine A reads i=5
  Goroutine B reads i=5  (before A wrote back!)
  Goroutine A writes i=6
  Goroutine B writes i=6  ← should be 7, data lost!
```

**Context matters enormously:**
- Atomic within a process? Maybe not within the OS
- Atomic within the OS? Maybe not within the machine
- Atomic within the machine? Maybe not in a distributed system

```
Fun Fact: In 2006, the game "Glider" (a World of Warcraft bot) bypassed
Blizzard's anti-cheat "Warden" by exploiting atomicity context.
Warden scanned memory "atomically" within its process context, but Glider
used hardware interrupts (a lower context) to hide itself during the scan.
```

### ⚠️ Memory Access Synchronization

When you have critical sections — code that needs exclusive access to shared state — you must *synchronize* access:

```go
var memoryAccess sync.Mutex
var value int

go func() {
    memoryAccess.Lock()    // ← acquire exclusive access
    value++
    memoryAccess.Unlock()  // ← release
}()

memoryAccess.Lock()
if value == 0 {
    fmt.Printf("the value is %v.\n", value)
} else {
    fmt.Printf("the value is %v.\n", value)
}
memoryAccess.Unlock()
```

> ⚠️ **Important distinction:** This solves the *data race* (exclusive memory access) but NOT the *race condition* (order of operations is still nondeterministic).

**Two costs of synchronization:**
1. **Convention cost** — all developers must follow the lock/unlock convention forever
2. **Performance cost** — entering/exiting critical sections is expensive; every `Lock()` call pauses your program

---

### ⚠️ Deadlocks

A **deadlock** is when all goroutines are waiting on each other — the program freezes forever without outside intervention.

```go
type value struct {
    mu    sync.Mutex
    value int
}

printSum := func(v1, v2 *value) {
    v1.mu.Lock()
    defer v1.mu.Unlock()
    time.Sleep(2 * time.Second)  // ← simulate work
    v2.mu.Lock()
    defer v2.mu.Unlock()
    fmt.Printf("sum=%v\n", v1.value+v2.value)
}

var a, b value
go printSum(&a, &b)   // locks a, then tries to lock b
go printSum(&b, &a)   // locks b, then tries to lock a
// DEADLOCK: each goroutine holds what the other needs
```

```
Timeline:
  T=0:  Goroutine 1 locks a
  T=0:  Goroutine 2 locks b
  T=2s: Goroutine 1 tries to lock b → BLOCKED (G2 holds b)
  T=2s: Goroutine 2 tries to lock a → BLOCKED (G1 holds a)
  T=∞:  Both wait forever
```

**The Coffman Conditions** — ALL four must be true for a deadlock to occur:

| Condition | Description |
|-----------|-------------|
| **Mutual Exclusion** | A process holds a resource exclusively |
| **Wait For Condition** | A process holds one resource AND waits for another |
| **No Preemption** | Resources can't be forcibly taken — only voluntarily released |
| **Circular Wait** | P1 waits on P2, P2 waits on P1 (or a longer chain) |

> 💡 **To prevent deadlocks:** ensure at least ONE of these conditions is false. Eliminating circular wait (always acquire locks in the same order) is often the most practical approach.

---

### ⚠️ Livelocks

A **livelock** is when goroutines are actively running but making no progress — like two people in a hallway constantly stepping the same direction to get out of each other's way.

```
Alice → → → → ← ← ← Alice
Barbara ← ← ← → → → Barbara

Both keep moving, neither passes the other.
The program looks "alive" (CPU is being used!) but no work is done.
```

```go
// Simplified livelock: two goroutines each step left/right
// trying to avoid each other, forever synchronized in failure
for i := 0; i < 5; i++ {
    if tryLeft(&out) || tryRight(&out) {
        return  // success
    }
}
// If both always choose the same direction → livelock
```

**Output of a livelocked program:**
```
Alice is trying to scoot: left right left right left right...
Alice tosses her hands up in exasperation!
Barbara is trying to scoot: left right left right left right...
Barbara tosses her hands up in exasperation!
```

> ⚠️ Livelocks are **harder to detect than deadlocks** — the program appears to be doing work. CPU utilization may look normal. Only careful inspection reveals the lack of progress.

---

### ⚠️ Starvation

**Starvation** is when a concurrent process can't get the resources it needs to do work because other processes are consuming them unfairly.

```go
// Greedy worker: holds the lock the ENTIRE time it works
greedyWorker := func() {
    for begin := time.Now(); time.Since(begin) <= runtime; {
        sharedLock.Lock()
        time.Sleep(3 * time.Nanosecond)  // ← holds lock the whole time
        sharedLock.Unlock()
        count++
    }
}

// Polite worker: releases and re-acquires the lock for each sub-task
politeWorker := func() {
    for begin := time.Now(); time.Since(begin) <= runtime; {
        sharedLock.Lock()
        time.Sleep(1 * time.Nanosecond)
        sharedLock.Unlock()
        sharedLock.Lock()
        time.Sleep(1 * time.Nanosecond)
        sharedLock.Unlock()
        sharedLock.Lock()
        time.Sleep(1 * time.Nanosecond)
        sharedLock.Unlock()
        count++
    }
}
```

**Result:**
```
Polite worker:  289,777 loops in 1 second
Greedy worker:  471,287 loops in 1 second  ← almost 2x more, starving the polite worker
```

The greedy worker *unnecessarily* holds the lock beyond its critical section, preventing the polite worker from getting its fair share.

> 💡 **Detection tip:** Record metrics on work completion rates. If a goroutine's rate is suspiciously low compared to theoretical maximum, starvation may be occurring.

---

## 1.3 Determining Concurrency Safety

One of the hardest problems: looking at code and knowing if it's concurrent-safe.

```go
// What does this tell you about concurrency?
func CalculatePi(begin, end int64, pi *Pi)
```

This raises unanswered questions:
- Does this function spawn goroutines internally?
- Am I responsible for synchronizing access to `*Pi`?
- Can I call this multiple times concurrently?

**Better — comment-documented version:**
```go
// CalculatePi calculates digits of Pi between begin and end.
//
// Internally, CalculatePi creates FLOOR((end-begin)/2) concurrent
// processes which recursively call CalculatePi. Synchronization of
// writes to pi are handled internally by the Pi struct.
func CalculatePi(begin, end int64, pi *Pi)
```

**Even better — use the type system:**
```go
// A channel return type signals concurrency is happening internally
func CalculatePi(begin, end int64) <-chan uint
```

> 📌 **Rule:** When writing concurrent functions, always clarify in comments or API design:
> 1. Who is responsible for the concurrency?
> 2. How does the problem map to concurrent primitives?
> 3. Who is responsible for synchronization?

---

## 1.4 Simplicity in the Face of Complexity

Go doesn't eliminate concurrency's inherent difficulty, but it significantly reduces the *incidental* complexity:

```
Traditional approach (threads + mutexes):
  ┌─────────────────────────────────────────────────────┐
  │ 1. Create thread pool                               │
  │ 2. Manage thread count manually                     │
  │ 3. Map work to threads                              │
  │ 4. Synchronize with mutexes                         │
  │ 5. Handle thread lifecycle                          │
  └─────────────────────────────────────────────────────┘

Go approach (goroutines + channels):
  ┌─────────────────────────────────────────────────────┐
  │ go handleConnection(conn)  ← that's it              │
  │                                                     │
  │ Runtime handles: scheduling, multiplexing,          │
  │ OS threads, memory management, GC                   │
  └─────────────────────────────────────────────────────┘
```

**Go's three key advantages:**
1. **Concurrent, low-latency GC** — garbage collection pauses < 100 microseconds as of Go 1.8; you don't need to manage memory across goroutines
2. **Automatic OS thread multiplexing** — Go's M:N scheduler maps goroutines to OS threads transparently; you think in goroutines, not threads
3. **Composable channels** — channels combine naturally; coordinating multiple concurrent operations is about composing channel operations, not carefully locking shared state

---

## Visual Summary

```
THE FIVE DANGERS OF CONCURRENT CODE
═══════════════════════════════════════════════════════════

① RACE CONDITION
   Two goroutines access shared state without ordering guarantee
   → Result: nondeterministic output, impossible to reproduce

② ATOMICITY
   i++ is NOT atomic (it's 3 operations: read, modify, write)
   → Result: lost updates when goroutines interleave

③ MEMORY SYNC
   Critical sections need exclusive access (mutex/lock)
   → But: synchronization is expensive and easy to forget

④ DEADLOCK  (all 4 Coffman conditions must hold)
   Mutual Exclusion + Wait For + No Preemption + Circular Wait
   → Result: program freezes forever

⑤ LIVELOCK / STARVATION
   Livelock: all goroutines active, none progressing
   Starvation: one goroutine monopolizes shared resources
   → Result: system appears alive but produces nothing

GO'S ANSWER:
   → goroutines (cheap threads, Go-managed)
   → channels (typed communication pipes)
   → select (multi-channel coordination)
   → context (structured cancellation)
```

---

*[Back to Index](../README.md) | [Chapter 2 — Communicating Sequential Processes →](02-communicating-sequential-processes.md)*
