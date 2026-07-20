# Chapter 9: Concurrency with Shared Variables

> *"Do not communicate by sharing memory; instead, share memory by communicating."*

---

## Core Concept

When goroutines share variables, you must prevent **data races**. Go provides mutexes and atomic operations for safe shared-state concurrency, while also recommending channels where possible.

---

## 9.1 Race Conditions

A **data race** occurs when two goroutines access the same variable concurrently and at least one is writing:

```go
// DANGER: data race!
var balance int

func Deposit(amount int) { balance += amount }  // read + write
func Balance() int       { return balance }      // read

// Two goroutines running simultaneously:
go Deposit(200)
go fmt.Println(Balance())  // may see 0, 200, or garbage!
```

**Three ways to avoid data races:**
1. Don't write the shared variable (read-only after init)
2. Confine the variable to a single goroutine
3. Allow many readers OR one writer (mutual exclusion)

---

## 9.2 Mutex: sync.Mutex

```go
var (
    mu      sync.Mutex
    balance int
)

func Deposit(amount int) {
    mu.Lock()
    balance += amount
    mu.Unlock()
}

func Balance() int {
    mu.Lock()
    defer mu.Unlock()  // always use defer for safety
    return balance
}
```

```
Mutex states:
  UNLOCKED ─── Lock() ─── LOCKED
  LOCKED   ─── Unlock() ─ UNLOCKED

  Only one goroutine holds the lock at a time.
  Others BLOCK at Lock() until it's released.
```

**Critical section** = code between Lock() and Unlock()

---

## 9.3 Read/Write Mutex: sync.RWMutex

When reads are frequent, use RWMutex to allow multiple concurrent readers:

```go
var mu sync.RWMutex
var cache map[string]int

// Multiple goroutines can read simultaneously
func Lookup(key string) int {
    mu.RLock()
    defer mu.RUnlock()
    return cache[key]
}

// Only one goroutine can write
func Update(key string, val int) {
    mu.Lock()
    defer mu.Unlock()
    cache[key] = val
}
```

```
RWMutex:
  RLock/RUnlock: multiple readers OK simultaneously
  Lock/Unlock:   exclusive — no readers or other writers

  Use when reads >> writes
```

---

## 9.4 Memory Synchronization

The mutex does two jobs: mutual exclusion AND memory synchronization. Modern CPUs and compilers reorder operations. Lock/Unlock create **synchronization points** — ensuring all writes before Unlock() are visible after the next Lock().

```go
// WITHOUT synchronization: goroutine B may never see x=1
var x, y int
go func() { x = 1; fmt.Println("y:", y) }()
go func() { y = 1; fmt.Println("x:", x) }()

// Output could be: x:0, y:0 (both!)
```

---

## 9.5 Lazy Initialization: sync.Once

```go
var (
    once sync.Once
    db   *sql.DB
)

func loadDB() *sql.DB {
    once.Do(func() {
        db = connectToDatabase()  // called exactly once
    })
    return db
}
// Thread-safe, efficient — no mutex overhead after init
```

---

## 9.6 The Race Detector

Go has a built-in race detector — use it during testing:

```bash
go test -race ./...
go run -race main.go
go build -race
```

```
==================
WARNING: DATA RACE
Write at 0x00c420090f88 by goroutine 7:
  main.Deposit(...)
Read at 0x00c420090f88 by goroutine 8:
  main.Balance(...)
==================
```

**Always run with `-race` during development and testing.**

---

## 9.7 Non-Blocking Cache (Concurrent-Safe Memoization)

```go
type Func func(key string) (interface{}, error)

type result struct {
    value interface{}
    err   error
}

type entry struct {
    res   result
    ready chan struct{}  // closed when res is ready
}

type Memo struct {
    f     Func
    mu    sync.Mutex
    cache map[string]*entry
}

func (memo *Memo) Get(key string) (interface{}, error) {
    memo.mu.Lock()
    e := memo.cache[key]
    if e == nil {
        e = &entry{ready: make(chan struct{})}
        memo.cache[key] = e
        memo.mu.Unlock()
        e.res.value, e.res.err = memo.f(key)
        close(e.ready)  // broadcast: result is ready
    } else {
        memo.mu.Unlock()
        <-e.ready  // wait for result
    }
    return e.res.value, e.res.err
}
```

---

## 9.8 Goroutines vs Threads

| Feature | OS Thread | Goroutine |
|---------|-----------|-----------|
| Stack size | Fixed ~1-8 MB | Dynamic 2KB–1GB |
| Scheduling | OS (preemptive) | Go runtime (cooperative) |
| Creation cost | High | Very low |
| Count | Thousands | Millions |
| Identity | Thread ID | None (intentional!) |

---

## Visual Summary

```
CONCURRENCY WITH SHARED STATE
═══════════════════════════════════════════════

DATA RACE: two goroutines access same var, ≥1 writes
  → undefined behavior, crashes, corruption

FIXES:
  sync.Mutex:    mu.Lock() / mu.Unlock()  [exclusive]
  sync.RWMutex:  mu.RLock() / mu.RUnlock() [shared reads]
  sync.Once:     once.Do(f) [run once safely]
  sync/atomic:   atomic.AddInt64(&n, 1) [low-level]

ALWAYS:
  defer mu.Unlock() after mu.Lock()
  go test -race during development

MANTRA: "Share memory by communicating" → prefer channels
         but sync.Mutex is fine for protecting shared state
```

---

*← [Chapter 8 — Goroutines and Channels](08-goroutines-and-channels.md) | [Back to Index](../README.md) | [Chapter 10 — Packages and the Go Tool](10-packages-and-the-go-tool.md) →*
