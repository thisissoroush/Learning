# Chapter 2: Modeling Your Code — Communicating Sequential Processes

> *"Concurrency is a property of the code; parallelism is a property of the running program."*

---

## Core Concept

The distinction between concurrency and parallelism isn't just semantic — it's the foundation of Go's design. This chapter explains *why* Go chose the CSP model over traditional thread-based concurrency, and gives you the mental model to reason about it correctly.

---

## 2.1 Concurrency vs. Parallelism — The Critical Difference

These words are often used interchangeably but mean fundamentally different things:

```
CONCURRENCY  = a property of the CODE
PARALLELISM  = a property of the RUNNING PROGRAM

You write concurrent code.
Whether it runs in parallel depends on the hardware and runtime.
```

**Example:** You write code with two goroutines. Does it run in parallel?

```
On a 1-core machine:
  Goroutine A: ─────────────────────────────────────
  Goroutine B:          ─────────────────────────────
  
  Both exist. They share 1 CPU via time-slicing.
  They are CONCURRENT but NOT PARALLEL.

On a 2-core machine:
  Core 1: Goroutine A ─────────────────────────────
  Core 2: Goroutine B ─────────────────────────────

  They are CONCURRENT AND PARALLEL.
```

> 💡 **The insight:** We do not write *parallel* code — we write *concurrent* code that we *hope* will run in parallel. The runtime decides how to execute it.

This means you can be **productively ignorant** of parallelism. Write the concurrent logic; let Go's runtime, the OS, and the hardware figure out actual execution.

---

## 2.2 The Chain of Abstraction

As computing has evolved, the level at which we model concurrency has shifted:

```
LEVEL          CONTEXT        PROBLEM COMPLEXITY
──────────────────────────────────────────────────
Distributed    Machines       Very Hard
  (cloud, VMs)
Process        OS boundary    Hard
Thread         OS thread      Very Hard (deadlocks, races)
──────────────────────────────────── ← most langs stop here
Goroutine      Go runtime     Easier
Channel        Communication  Elegant
```

Before Go, most languages stopped at OS threads. Concurrency primitives were mapped directly to `pthread_create`, mutexes, and semaphores. Go added a new link: **goroutines and channels** — built on OS threads, but presenting a dramatically simpler abstraction.

---

## 2.3 What Is CSP?

**CSP** = **Communicating Sequential Processes**, a paper by Tony Hoare published in 1978.

Hoare's insight: **input and output are first-class primitives** in concurrent programming — not an afterthought.

```
Traditional view (before CSP):
  Concurrent programs = threads sharing memory
  Coordination = locks and mutexes

Hoare's view (CSP):
  Concurrent programs = independent processes
  Coordination = message passing via channels
```

**CSP's original notation:**

| Operation | Meaning |
|-----------|---------|
| `cardreader?cardimage` | From cardreader, read a card into cardimage |
| `lineprinter!lineimage` | To lineprinter, send lineimage |
| `X?(x, y)` | From process X, receive a pair into (x, y) |
| `*[c: char; west?c → east!c]` | Read all from west, send one-by-one to east |

The similarities to Go's channel syntax (`<-ch`, `ch <- value`) are unmistakable. Go is one of the first mainstream languages to bring CSP ideas into its core.

---

## 2.4 How This Helps You (Web Server Example)

**Without goroutines** (thread-based thinking):
```
Questions you must answer before writing any code:
  ❓ Does my language support threads natively?
  ❓ Where should thread confinement boundaries be?
  ❓ How heavy are threads on this OS?
  ❓ How do different OSes handle threads differently?
  ❓ What's the optimal thread pool size?
  ❓ How do I map work evenly across threads?
```

**With goroutines** (natural mapping):
```go
// The natural model: each user connection is independent
// Map it directly to code — one goroutine per connection
http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
    // This handler runs in its own goroutine automatically
    handleRequest(w, r)
})

// Go's promise: goroutines are lightweight enough that you
// don't need to think about pools or thread counts upfront
```

The natural structure of the problem (each connection is independent) maps *directly* to the code structure. No translation needed.

**Benefits of this mapping:**
1. **Dynamic scaling** — goroutines scale automatically to available cores (Amdahl's Law in action)
2. **Runtime optimization** — improvements to Go's scheduler make all your programs faster for free
3. **I/O intelligence** — Go's runtime detects goroutines blocked on I/O and reallocates threads to goroutines that can do work

---

## 2.5 Go's Philosophy on Concurrency

Go supports both approaches to concurrency, but provides guidance on when to use each.

### The Decision Tree

```
Should I use CHANNELS or MUTEXES?
═══════════════════════════════════════════════════════════

Are you transferring OWNERSHIP of data?
  Yes → Use a CHANNEL
        (channels encode the transfer semantics; also makes
         code composable with other concurrent code)

Are you guarding INTERNAL STATE of a struct?
  Yes → Use a MUTEX
        (hide the lock inside the type; callers don't need to know)
        Example:
          type Counter struct {
              mu    sync.Mutex
              value int
          }
          func (c *Counter) Increment() {
              c.mu.Lock()
              defer c.mu.Unlock()
              c.value++
          }

Are you COORDINATING multiple pieces of logic?
  Yes → Use CHANNELS
        (channels compose; scattered mutexes don't)
        select makes channel coordination elegant

Is this a PERFORMANCE-CRITICAL section (profiler-proven)?
  Yes → Consider MUTEXES
        (channels use memory access sync internally → slower)
        But first ask: can you restructure the program instead?
```

### The Official Go Stance

> *"Do not communicate by sharing memory. Instead, share memory by communicating."*

But Go's authors also acknowledge this isn't absolute:

> *"Most locking issues can be solved using either channels or traditional locks. Use whichever is most expressive and/or most simple."*

---

## 2.6 Why Goroutines Beat Threads

**Thread model (Java, C++, Rust before async):**
```
OS Thread:
  - Stack: 1–8 MB fixed (or large default)
  - Managed by: OS kernel
  - Scheduling: preemptive (kernel decides)
  - Context switch: ~1.5 μs (save/restore registers, memory maps, etc.)
  - Max practical count: ~thousands
```

**Goroutine model (Go):**
```
Goroutine:
  - Stack: ~2–8 KB (grows/shrinks dynamically as needed)
  - Managed by: Go runtime (M:N scheduler)
  - Scheduling: cooperative + preemptive hybrid
  - Context switch: ~225 ns (92% faster than OS threads!)
  - Max practical count: hundreds of thousands to millions
```

**Memory comparison:**

| RAM Available | Max Goroutines (approx.) |
|--------------|--------------------------|
| 1 GB | ~370,000 |
| 4 GB | ~1,480,000 |
| 8 GB | ~2,960,000 |
| 64 GB | ~23,680,000 |

> The rule: *"Goroutines are free. Start one anytime the problem warrants it."*

---

## 2.7 Channels and select

CSP's other major contribution to Go is **channels** — and the **select statement** that lets you coordinate multiple channels.

```
CHANNELS: typed communication pipes
  - Encode the intent to transfer data between goroutines
  - Inherently composable with each other
  - Can be ranged over, closed, used in select

SELECT: the multi-channel coordination primitive
  - Allows waiting on multiple channel operations simultaneously
  - Enables cancellation, timeouts, and default fallback
  - Is what makes channel composition practical at scale
```

```go
// Channels compose naturally — this would be a nightmare with mutexes
select {
case msg := <-messageChannel:
    process(msg)
case <-timeoutChannel:
    return errors.New("timed out")
case <-cancelChannel:
    return errors.New("canceled")
}
```

Trying to build the same logic with mutexes would require complex condition variables and careful lock management. With channels, it reads almost like English.

---

## Visual Summary

```
CSP MODEL IN GO
═══════════════════════════════════════════════════════════

HISTORY:
  1978: Tony Hoare publishes "Communicating Sequential Processes"
  2009: Go releases — first mainstream language built around CSP

CORE INSIGHT:
  Communication IS the synchronization primitive
  You don't lock memory — you send ownership through a channel

CONCURRENCY vs PARALLELISM:
  Concurrency = code structure (multiple things in progress)
  Parallelism  = execution (multiple things literally at once)
  
  Write for CONCURRENCY → let the runtime achieve PARALLELISM

GOROUTINE vs THREAD:
  Thread:    ~1MB, OS-managed, ~1.5μs context switch
  Goroutine: ~2KB, Go-managed, ~225ns context switch
  
  → Goroutines are ~92% cheaper to context-switch
  → You can have millions vs thousands of threads

WHEN TO USE WHAT:
  Channel  → transferring data ownership, coordinating goroutines
  Mutex    → protecting internal state inside a struct
  Context  → structured cancellation propagating down call stacks
  
  Rule of thumb: "Start with channels; reach for mutexes only
                  when hiding implementation details of a type"
```

---

*[← Chapter 1 — Introduction to Concurrency](01-introduction-to-concurrency.md) | [Back to Index](../README.md) | [Chapter 3 — Go's Concurrency Building Blocks →](03-concurrency-building-blocks.md)*
