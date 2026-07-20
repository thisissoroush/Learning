# Chapter 3: Go's Concurrency Building Blocks

> *"Every Go program has at least one goroutine: the main goroutine, which is automatically created and started when the process begins."*

---

## Core Concept

Go provides two categories of concurrency primitives: **goroutines** (lightweight concurrent functions) and a set of **synchronization tools** in the `sync` package. Knowing when to use each, and exactly how they behave, is the foundation of correct concurrent Go code.

---

## 3.1 Goroutines

### Starting a Goroutine

```go
// Any function can become a goroutine with the `go` keyword
go sayHello()

// Anonymous functions too
go func() {
    fmt.Println("hello")
}()

// Or assign and call
sayHello := func() { fmt.Println("hello") }
go sayHello()
```

### The Fork-Join Model

Go's concurrency follows the **fork-join** model:
- **Fork** = `go` statement — spawns a child goroutine
- **Join** = synchronization point where parent and child reunite

```
main goroutine
     │
     ├──── go f()  ← FORK: child goroutine starts here
     │         │
     │         │   (child runs concurrently)
     │         │
     │◄────────┘   ← JOIN: parent waits for child
     │
   continues
```

```go
// Without a join point — WRONG: child may never run
go sayHello()
// program may exit before goroutine starts

// With a join point — CORRECT
var wg sync.WaitGroup
wg.Add(1)
go func() {
    defer wg.Done()
    fmt.Println("hello")
}()
wg.Wait()  // ← JOIN POINT
```

### The Closure Capture Bug (Classic Mistake)

```go
// BUG: all goroutines see the same final value of salutation
for _, salutation := range []string{"hello", "greetings", "good day"} {
    go func() {
        fmt.Println(salutation)  // ← captures the variable, not the value
    }()
}
// Likely output: "good day", "good day", "good day"
// The loop ends before goroutines start; salutation = last value

// FIX: pass as parameter to get a copy
for _, salutation := range []string{"hello", "greetings", "good day"} {
    go func(salutation string) {  // ← receives a COPY
        fmt.Println(salutation)
    }(salutation)  // ← passed at loop-time
}
// Correct output: "hello", "greetings", "good day" (in any order)
```

### Goroutine Size

```
Benchmark results (book measurements):
  Memory per goroutine: ~2.817 KB (empty goroutine)
  Context switch cost:  ~225 ns (vs ~1,467 ns for OS threads)
  
  On an 8 GB machine: ~2.9 million goroutines possible
  In practice: limited by your logic, not by goroutine overhead
```

---

## 3.2 The `sync` Package

### WaitGroup — Waiting for Multiple Goroutines

```go
var wg sync.WaitGroup

wg.Add(1)             // ← register goroutine BEFORE starting it
go func() {
    defer wg.Done()   // ← decrement when done (use defer to ensure it runs)
    fmt.Println("goroutine 1")
}()

wg.Add(1)
go func() {
    defer wg.Done()
    fmt.Println("goroutine 2")
}()

wg.Wait()             // ← blocks until count reaches 0
fmt.Println("all done")
```

> ⚠️ **Critical:** Call `Add` *before* starting the goroutine, not inside it. If `Add` is inside the goroutine, `Wait` might return before `Add` is called — a race condition.

```go
// WRONG: Add inside goroutine creates a race with Wait
go func() {
    wg.Add(1)  // ← might not execute before wg.Wait()!
    defer wg.Done()
}()
wg.Wait()

// RIGHT: Add before the goroutine starts
wg.Add(1)
go func() {
    defer wg.Done()
}()
wg.Wait()
```

---

### Mutex — Exclusive Access to Shared State

`Mutex` = **mutual exclusion**: only one goroutine can hold the lock at a time.

```go
var count int
var lock sync.Mutex

increment := func() {
    lock.Lock()          // ← acquire
    defer lock.Unlock()  // ← always release (defer protects against panics)
    count++
}

decrement := func() {
    lock.Lock()
    defer lock.Unlock()
    count--
}

// Safe to call concurrently
var wg sync.WaitGroup
for i := 0; i < 5; i++ {
    wg.Add(1)
    go func() { defer wg.Done(); increment() }()
}
wg.Wait()
```

### RWMutex — Multiple Readers OR One Writer

When reads vastly outnumber writes, `RWMutex` allows concurrent reads:

```go
var m sync.RWMutex
var data []int

// Multiple goroutines can read simultaneously
reader := func() {
    m.RLock()         // ← shared read lock (multiple allowed)
    defer m.RUnlock()
    _ = data[0]
}

// Only ONE goroutine can write at a time (blocks all readers too)
writer := func(v int) {
    m.Lock()          // ← exclusive write lock
    defer m.Unlock()
    data = append(data, v)
}
```

```
Performance benchmark (book data):
  At 2^10 (1024) readers:
    RWMutex: ~459 μs
    Mutex:   ~850 μs   ← ~85% slower than RWMutex
  
  The benefit grows with reader count.
  Use RWMutex whenever readers >> writers.
```

---

### Cond — Signal-Based Coordination

`Cond` is a *rendezvous point* — goroutines wait for some condition to become true.

```go
// Naive approach (burns CPU):
for conditionTrue() == false {}  // ← busy-wait, wastes 100% of a core

// Better but wasteful:
for conditionTrue() == false {
    time.Sleep(1 * time.Millisecond)  // ← still arbitrary and wasteful
}

// CORRECT approach with Cond:
c := sync.NewCond(&sync.Mutex{})

c.L.Lock()
for conditionTrue() == false {
    c.Wait()  // ← suspends goroutine (releases lock, re-acquires on wake)
}
c.L.Unlock()
```

**Practical example — queue of fixed size:**

```go
c := sync.NewCond(&sync.Mutex{})
queue := make([]interface{}, 0, 10)

removeFromQueue := func(delay time.Duration) {
    time.Sleep(delay)
    c.L.Lock()
    queue = queue[1:]
    fmt.Println("Removed from queue")
    c.L.Unlock()
    c.Signal()  // ← notify ONE waiting goroutine
}

for i := 0; i < 10; i++ {
    c.L.Lock()
    for len(queue) == 2 {   // ← check in a loop (spurious wakeups!)
        c.Wait()
    }
    fmt.Println("Adding to queue")
    queue = append(queue, struct{}{})
    go removeFromQueue(1 * time.Second)
    c.L.Unlock()
}
```

**Signal vs Broadcast:**

| Method | Effect |
|--------|--------|
| `c.Signal()` | Wakes ONE waiting goroutine (the longest-waiting) |
| `c.Broadcast()` | Wakes ALL waiting goroutines simultaneously |

```go
// Broadcast use case: a button with multiple handlers
type Button struct {
    Clicked *sync.Cond
}
button := Button{Clicked: sync.NewCond(&sync.Mutex{})}

// Register handlers that wait for click
subscribe := func(c *sync.Cond, fn func()) {
    go func() {
        c.L.Lock()
        defer c.L.Unlock()
        c.Wait()  // wait for click
        fn()
    }()
}

subscribe(button.Clicked, func() { fmt.Println("Maximizing window.") })
subscribe(button.Clicked, func() { fmt.Println("Displaying dialog.") })
subscribe(button.Clicked, func() { fmt.Println("Mouse clicked.") })

button.Clicked.Broadcast()  // ← all three handlers run simultaneously
// Output (in any order):
//   Mouse clicked.
//   Maximizing window.
//   Displaying dialog.
```

> 💡 `Broadcast` is the one behavior channels can't easily replicate. Use `sync.Cond` when you need to notify many goroutines simultaneously and repeatedly.

---

### Once — Run Exactly Once

```go
var count int
increment := func() { count++ }

var once sync.Once

for i := 0; i < 100; i++ {
    go func() {
        once.Do(increment)  // ← only the FIRST call executes increment
    }()
}
// count == 1, not 100
```

> ⚠️ **Key subtlety:** `sync.Once` counts *calls to Do*, not unique functions. Calling `once.Do(funcA)` then `once.Do(funcB)` — only `funcA` runs, `funcB` is silently skipped.

```go
// TRAP: Circular Once causes deadlock
var onceA, onceB sync.Once
var initB func()
initA := func() { onceB.Do(initB) }
initB = func() { onceA.Do(initA) }  // ← circular!
onceA.Do(initA)                     // → DEADLOCK
```

---

### Pool — Object Reuse

`Pool` is a concurrent-safe **object pool** — reuse expensive objects rather than create/GC them repeatedly.

```go
myPool := &sync.Pool{
    New: func() interface{} {
        fmt.Println("Creating new instance.")
        return struct{}{}
    },
}

// First Get: creates a new instance
myPool.Get()

// Put it back
instance := myPool.Get()
myPool.Put(instance)

// This Get reuses the returned instance — no new creation
myPool.Get()
// Output:
//   Creating new instance.
//   Creating new instance.  (not 3 times!)
```

**Real-world impact — pre-warming connections:**

```go
// WITHOUT Pool: ~1,000,000 ns per operation
func startNetworkDaemon() {
    for conn := server.Accept(); ; conn = server.Accept() {
        connectToService()  // ← 1 second per request!
        conn.Close()
    }
}

// WITH Pool: ~2,904 ns per operation (3 orders of magnitude faster!)
connPool := &sync.Pool{New: connectToService}
for conn := server.Accept(); ; conn = server.Accept() {
    svcConn := connPool.Get()
    connPool.Put(svcConn)
    conn.Close()
}
```

**Rules for Pool:**
1. Give it a thread-safe `New` function
2. Make no assumptions about the state of objects you `Get` back
3. Always `Put` back when done (usually via `defer`)
4. Objects in the pool should be **uniform** — pools of variable-sized things lose efficiency

---

## 3.3 Channels

### Creating Channels

```go
// Bidirectional (most common)
ch := make(chan int)       // unbuffered
ch := make(chan int, 5)    // buffered, capacity 5

// Unidirectional (for type safety at function boundaries)
var sendOnly chan<- int    // send-only
var recvOnly <-chan int    // receive-only

// Go converts automatically at function boundaries
func producer(out chan<- int) { out <- 42 }   // caller passes chan int
func consumer(in <-chan int) { v := <-in }    // caller passes chan int
```

### Sending, Receiving, Closing

```go
ch <- value    // send (blocks if full/no receiver)
v := <-ch      // receive (blocks if empty/no sender)
v, ok := <-ch  // ok=false means channel is closed and drained

close(ch)      // signal no more values; readers get zero values after draining
```

**Ranging over a channel:**
```go
go func() {
    defer close(ch)  // ← close when done sending
    for i := 0; i < 5; i++ {
        ch <- i
    }
}()

for v := range ch {  // ← automatically stops when channel is closed
    fmt.Println(v)
}
```

### Channel Operations Reference

| Operation | nil channel | Open, not empty | Open, empty | Closed |
|-----------|------------|-----------------|-------------|--------|
| **Read** | Block forever | Return value | Block | Return zero value + false |
| **Write** | Block forever | Write value | Write value | **panic** |
| **Close** | **panic** | Close (reads succeed until drained) | Close (reads get zero) | **panic** |

> 📌 **Rule of thumb:** The goroutine that **creates** a channel should **own** it — it's responsible for writing to it and closing it. Consumer goroutines only receive.

### Unidirectional Channels for Safety

```go
// Owner function: creates, writes, closes — exposes READ-ONLY to consumer
chanOwner := func() <-chan int {
    resultStream := make(chan int, 5)  // internal — owner's full access
    go func() {
        defer close(resultStream)
        for i := 0; i <= 5; i++ {
            resultStream <- i
        }
    }()
    return resultStream  // ← returns read-only view
}

// Consumer: can only read — cannot write or close
for result := range chanOwner() {
    fmt.Printf("Received: %d\n", result)
}
```

### Buffered Channels

```go
c := make(chan rune, 4)  // capacity 4

// Sends without blocking (until full)
c <- 'A'
c <- 'B'
c <- 'C'
c <- 'D'

// 5th send BLOCKS — channel full
// c <- 'E'   ← would block here

// A read frees space
<-c  // reads 'A'; now 'E' can be sent
```

```
Buffered channel state visualization:
  make(chan rune, 4)   →  [ _ ][ _ ][ _ ][ _ ]
  c <- 'A'            →  [A][ _ ][ _ ][ _ ]
  c <- 'B'            →  [A][B][ _ ][ _ ]
  c <- 'C'            →  [A][B][C][ _ ]
  c <- 'D'            →  [A][B][C][D]  ← full
  <-c  (reads 'A')    →  [B][C][D][ _ ]  ← room for one more
```

**Unblocking multiple goroutines at once:**
```go
begin := make(chan interface{})
for i := 0; i < 5; i++ {
    go func(i int) {
        <-begin  // ← all goroutines block here
        fmt.Printf("%v has begun\n", i)
    }(i)
}

fmt.Println("Unblocking goroutines...")
close(begin)  // ← closing broadcasts to ALL waiting goroutines simultaneously
```

---

## 3.4 The `select` Statement

`select` is the coordination primitive for channels — it waits on multiple channel operations and picks one that's ready:

```go
var c1, c2 <-chan interface{}
select {
case v := <-c1:
    fmt.Println("from c1:", v)
case v := <-c2:
    fmt.Println("from c2:", v)
}
// If multiple are ready simultaneously → one is chosen at RANDOM (uniform)
// If none are ready → blocks until one becomes ready
```

**Timeout pattern:**
```go
select {
case result := <-workCh:
    fmt.Println("got result:", result)
case <-time.After(5 * time.Second):
    fmt.Println("timed out!")
}
```

**Non-blocking check (default clause):**
```go
select {
case v := <-ch:
    fmt.Println("received:", v)
default:
    fmt.Println("no value ready, moving on")  // executes immediately
}
```

**for-select loop — most common pattern:**
```go
done := make(chan interface{})
for {
    select {
    case <-done:
        return  // ← exit when told to stop
    default:
        // do work
    }
}
```

**Empty select blocks forever:**
```go
select {}  // ← blocks the goroutine indefinitely
```

---

## 3.5 GOMAXPROCS

`runtime.GOMAXPROCS(n)` controls how many OS threads host Go's work queues.

```go
// Before Go 1.5: default was 1 (single-threaded scheduling)
// After Go 1.5:  default = number of logical CPUs on the machine
runtime.GOMAXPROCS(runtime.NumCPU())  // now the default behavior

// When would you change it?
// → During testing to trigger race conditions more aggressively
// → Very rare performance tuning (measure first!)
runtime.GOMAXPROCS(8)  // force 8 OS threads even on a 4-core machine
```

---

## Visual Summary

```
GO'S CONCURRENCY TOOLKIT
═══════════════════════════════════════════════════════════

GOROUTINES
  go f()           → fork a new goroutine
  sync.WaitGroup   → wait for a set of goroutines to finish
  ~2.8 KB each     → start millions if needed

SYNC PACKAGE (for protecting shared state)
  sync.Mutex       → exclusive access to ONE goroutine at a time
  sync.RWMutex     → multiple concurrent readers OR one writer
  sync.Cond        → wait for a condition; Signal/Broadcast to wake
  sync.Once        → run a function exactly once, ever
  sync.Pool        → reuse expensive objects; avoid GC pressure

CHANNELS (for communication between goroutines)
  make(chan T)     → unbuffered: synchronizes sender and receiver
  make(chan T, n)  → buffered: sender can put n items without blocking
  close(ch)        → signal no more values coming
  range ch         → receive until closed
  chan<- T         → send-only (function parameter safety)
  <-chan T         → receive-only (function parameter safety)

SELECT
  select { case <-ch: ... }          → wait for first ready channel
  select { case ...; default: ... }  → non-blocking check
  for { select { ... } }             → the for-select loop (very common)
  time.After(d)                      → timeout inside select
```

---

*[← Chapter 2 — CSP](02-communicating-sequential-processes.md) | [Back to Index](../README.md) | [Chapter 4 — Concurrency Patterns →](04-concurrency-patterns.md)*
