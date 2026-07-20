# Chapter 4: Concurrency Patterns in Go

> *"These patterns will both help us solve problems and avoid issues that can come up when combining concurrency primitives."*

---

## Core Concept

Individual primitives (goroutines, channels, mutexes) are just tools. This chapter shows you how to **compose** them into reusable, named patterns that solve recurring problems in concurrent systems.

---

## 4.1 Confinement — Make Sharing Unnecessary

The safest concurrent code doesn't share state at all. **Confinement** ensures data is only ever accessed by one goroutine — no synchronization needed.

**Ad hoc confinement** (convention-based, fragile):
```go
// By convention, only loopData reads 'data'
data := make([]int, 4)
go loopData(data)
// But nothing prevents another goroutine from touching data!
```

**Lexical confinement** (compiler-enforced, robust):
```go
// The channel is created inside chanOwner — its write access is confined
chanOwner := func() <-chan int {
    results := make(chan int, 5)     // ← write access confined here
    go func() {
        defer close(results)
        for i := 0; i <= 5; i++ {
            results <- i
        }
    }()
    return results  // ← consumer gets READ-ONLY view; can't write or close
}

consumer := func(results <-chan int) {
    for result := range results {
        fmt.Printf("Received: %d\n", result)
    }
}
consumer(chanOwner())
```

```go
// Confining slices by passing sub-slices
data := []byte("golang")
go printData(&wg, data[:3])  // goroutine 1 owns first 3 bytes
go printData(&wg, data[3:])  // goroutine 2 owns last 3 bytes
// No synchronization needed — each goroutine has exclusive access to its slice
```

> 💡 Prefer lexical confinement over ad hoc. The compiler enforces it — humans don't have to remember rules.

---

## 4.2 The for-select Loop

The most common pattern in concurrent Go code:

```go
// Pattern 1: iterate and send, stopping when done
for _, s := range []string{"a", "b", "c"} {
    select {
    case <-done:
        return
    case stringStream <- s:
    }
}

// Pattern 2: infinite loop until stopped (short select)
for {
    select {
    case <-done:
        return
    default:
    }
    doWork()  // non-preemptable work here
}

// Pattern 3: work inside select's default
for {
    select {
    case <-done:
        return
    default:
        doWork()  // preemptable at every loop iteration
    }
}
```

---

## 4.3 Preventing Goroutine Leaks

Goroutines are not garbage-collected. A goroutine that can never exit is a **leak** — memory and resources consumed forever.

**The leak:**
```go
// This goroutine leaks if nil is passed — it blocks on nil channel forever
doWork := func(strings <-chan string) <-chan interface{} {
    completed := make(chan interface{})
    go func() {
        defer close(completed)
        for s := range strings {  // ← blocks forever on nil channel
            fmt.Println(s)
        }
    }()
    return completed
}
doWork(nil)  // goroutine lives until process dies
```

**The fix — always pass a `done` channel:**
```go
doWork := func(done <-chan interface{}, strings <-chan string) <-chan interface{} {
    terminated := make(chan interface{})
    go func() {
        defer close(terminated)
        for {
            select {
            case s := <-strings:
                fmt.Println(s)
            case <-done:  // ← always exits when told to
                return
            }
        }
    }()
    return terminated
}

done := make(chan interface{})
terminated := doWork(done, nil)
go func() {
    time.Sleep(1 * time.Second)
    close(done)  // ← parent cancels after 1 second
}()
<-terminated
```

> 📌 **Convention:** If a goroutine creates a goroutine, it is responsible for ensuring it can be stopped. Always pass `done` as the first parameter.

---

## 4.4 The or-channel — Combine Multiple Done Channels

When you want to cancel if *any* of several channels closes:

```go
var or func(channels ...<-chan interface{}) <-chan interface{}
or = func(channels ...<-chan interface{}) <-chan interface{} {
    switch len(channels) {
    case 0:
        return nil
    case 1:
        return channels[0]
    }
    orDone := make(chan interface{})
    go func() {
        defer close(orDone)
        switch len(channels) {
        case 2:
            select {
            case <-channels[0]:
            case <-channels[1]:
            }
        default:
            select {
            case <-channels[0]:
            case <-channels[1]:
            case <-channels[2]:
            case <-or(append(channels[3:], orDone)...):  // ← recursive
            }
        }
    }()
    return orDone
}

// Usage: close if ANY of these channels closes first
<-or(
    sig(2*time.Hour),
    sig(5*time.Minute),
    sig(1*time.Second),    // ← this closes first
    sig(1*time.Hour),
)
// → done after ~1 second
```

---

## 4.5 Error Handling — Return Errors, Don't Print Them

Don't trap errors inside goroutines. Return them paired with results:

```go
// WRONG: goroutine prints the error and continues — caller has no control
go func() {
    resp, err := http.Get(url)
    if err != nil {
        fmt.Println(err)  // ← swallowed! caller can't react
        return
    }
}()

// RIGHT: pair error with result in a struct
type Result struct {
    Error    error
    Response *http.Response
}

checkStatus := func(done <-chan interface{}, urls ...string) <-chan Result {
    results := make(chan Result)
    go func() {
        defer close(results)
        for _, url := range urls {
            resp, err := http.Get(url)
            select {
            case <-done:
                return
            case results <- Result{Error: err, Response: resp}:
            }
        }
    }()
    return results
}

// Caller decides what to do with errors
for result := range checkStatus(done, urls...) {
    if result.Error != nil {
        fmt.Printf("error: %v\n", result.Error)
        errCount++
        if errCount >= 3 {
            fmt.Println("Too many errors, stopping!")
            break
        }
        continue
    }
    fmt.Printf("Response: %v\n", result.Response.Status)
}
```

---

## 4.6 Pipelines — Chain Stages of Data Transformation

A **pipeline** is a series of stages connected by channels. Each stage receives input, transforms it, and sends output.

```go
// Generator: converts discrete values to a channel stream
generator := func(done <-chan interface{}, integers ...int) <-chan int {
    intStream := make(chan int)
    go func() {
        defer close(intStream)
        for _, i := range integers {
            select {
            case <-done:
                return
            case intStream <- i:
            }
        }
    }()
    return intStream
}

// Stage: multiply each value
multiply := func(done <-chan interface{}, intStream <-chan int, multiplier int) <-chan int {
    multipliedStream := make(chan int)
    go func() {
        defer close(multipliedStream)
        for i := range intStream {
            select {
            case <-done:
                return
            case multipliedStream <- i * multiplier:
            }
        }
    }()
    return multipliedStream
}

// Compose into a pipeline
done := make(chan interface{})
defer close(done)

intStream := generator(done, 1, 2, 3, 4)
pipeline := multiply(done, multiply(done, intStream, 2), 3)

for v := range pipeline {
    fmt.Println(v)  // 6, 12, 18, 24
}
```

```
Pipeline visualization:
  generator → [1,2,3,4] → multiply(×2) → [2,4,6,8] → multiply(×3) → [6,12,18,24]
  
  Each stage runs in its own goroutine — concurrent processing throughout
```

**Handy generators:**
```go
// repeat: infinite stream of the given values, cycling
repeat := func(done <-chan interface{}, values ...interface{}) <-chan interface{} { ... }

// take: take only the first n items
take := func(done <-chan interface{}, in <-chan interface{}, n int) <-chan interface{} { ... }

// Usage: take 10 ones
for num := range take(done, repeat(done, 1), 10) {
    fmt.Printf("%v ", num)
}
// Output: 1 1 1 1 1 1 1 1 1 1
```

---

## 4.7 Fan-Out, Fan-In — Parallelize Expensive Stages

When one pipeline stage is slow, run it in parallel on multiple goroutines:

```
Before fan-out (sequential):
  input → [slow stage] → output
  Search took: 23 seconds

After fan-out (8 parallel workers):
  input → [slow stage #1] ─┐
  input → [slow stage #2] ─┤
  input → [slow stage #3] ─┤ fanIn → output
  input → [slow stage #4] ─┤
  ...                       │
  input → [slow stage #8] ─┘
  Search took: 5 seconds  (78% improvement!)
```

```go
// Fan-out: start numCPU copies of the expensive stage
numFinders := runtime.NumCPU()
finders := make([]<-chan int, numFinders)
for i := 0; i < numFinders; i++ {
    finders[i] = primeFinder(done, randIntStream)  // all read from same input
}

// Fan-in: merge all outputs into one channel
for prime := range take(done, fanIn(done, finders...), 10) {
    fmt.Printf("%d\n", prime)
}

// fanIn implementation
fanIn := func(done <-chan interface{}, channels ...<-chan interface{}) <-chan interface{} {
    var wg sync.WaitGroup
    multiplexedStream := make(chan interface{})
    multiplex := func(c <-chan interface{}) {
        defer wg.Done()
        for i := range c {
            select {
            case <-done:
                return
            case multiplexedStream <- i:
            }
        }
    }
    wg.Add(len(channels))
    for _, c := range channels {
        go multiplex(c)
    }
    go func() {
        wg.Wait()
        close(multiplexedStream)
    }()
    return multiplexedStream
}
```

> 📌 **When to fan-out:** Stage is order-independent AND takes a long time to run.

---

## 4.8 Other Useful Patterns

### or-done-channel — Clean Range Over External Channel
```go
// Without or-done: verbose and error-prone
loop:
for {
    select {
    case <-done:
        break loop
    case v, ok := <-myChan:
        if !ok { return }
        // process v
    }
}

// With or-done: clean and readable
orDone := func(done, c <-chan interface{}) <-chan interface{} {
    valStream := make(chan interface{})
    go func() {
        defer close(valStream)
        for {
            select {
            case <-done:
                return
            case v, ok := <-c:
                if !ok { return }
                select {
                case valStream <- v:
                case <-done:
                }
            }
        }
    }()
    return valStream
}

for val := range orDone(done, myChan) {  // ← clean again!
    // process val
}
```

### tee-channel — Split One Channel into Two
```go
// Like the Unix `tee` command — one input, two identical outputs
out1, out2 := tee(done, inputChannel)
// Both out1 and out2 receive every value from inputChannel
```

### bridge-channel — Flatten Channel of Channels
```go
// Consume a sequence of channels as if it's one continuous stream
for val := range bridge(done, channelOfChannels) {
    fmt.Printf("%v ", val)
}
// Output: 0 1 2 3 4 5 6 7 8 9
```

---

## 4.9 Queuing — Decouple Stages

**Key insight:** Queuing (buffered channels between stages) doesn't speed up your pipeline — it changes *behavior*.

```
WITHOUT queue:
  acceptConnection → processRequest
  If processRequest is slow → acceptConnection blocks → users get errors

WITH queue:
  acceptConnection → [buffer] → processRequest
  If processRequest is slow → connections queue → users wait, not fail
```

**Little's Law** — the math behind queue sizing:
```
L = λW

L = average number of requests in the system
λ = arrival rate (requests/second)
W = average time in system (seconds)

Example:
  W = 1ms, λ = 100,000 req/s
  L = 100,000 × 0.001 = 10 in-flight requests
  → Queue of 7 (minus 3 for pipeline stages) is sufficient

Insight: adding queue increases L, which either increases λ
(more arrivals) or increases W (more time in system).
QUEUING NEVER DECREASES TOTAL RUNTIME.
```

**When queuing helps:**
1. **Chunking** — batching writes to disk/network (like `bufio.Writer`)
2. **Preventing death-spirals** — queue absorbs burst traffic at the entrance to a pipeline

---

## 4.10 The context Package — Structured Cancellation

The `context` package replaces raw `done` channels with richer cancellation + metadata:

```go
// context.Context interface
type Context interface {
    Done() <-chan struct{}          // closed when work should stop
    Err() error                    // reason for cancellation
    Deadline() (time.Time, bool)   // when context expires
    Value(key interface{}) interface{}  // request-scoped data
}
```

**Creating contexts:**
```go
ctx, cancel := context.WithCancel(context.Background())
defer cancel()  // always call cancel to free resources

ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
ctx, cancel := context.WithDeadline(ctx, time.Now().Add(1*time.Minute))
ctx = context.WithValue(ctx, ctxUserID, "jane")
```

**Practical example — cascading cancellation:**
```go
func main() {
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()

    go func() {
        if err := printGreeting(ctx); err != nil {
            fmt.Printf("error: %v\n", err)
            cancel()  // ← if greeting fails, cancel farewell too
        }
    }()
    go func() {
        if err := printFarewell(ctx); err != nil {
            fmt.Printf("error: %v\n", err)
        }
    }()
}

func genGreeting(ctx context.Context) (string, error) {
    ctx, cancel := context.WithTimeout(ctx, 1*time.Second)  // ← local timeout
    defer cancel()
    // ... use ctx
}
```

```
Context tree visualization:
  Background()
      │
      ├── WithCancel(...)     ← main cancels all children
      │       │
      │       ├── printGreeting
      │       │       └── WithTimeout(1s)  ← greeting times out independently
      │       │
      │       └── printFarewell            ← canceled when main cancels
```

**Storing data in context — guidelines:**
```
✅ Use for:  request ID, user ID, auth token (read-only, crosses API boundaries)
❌ Avoid for: optional function parameters, mutable state, complex objects
```

---

## Visual Summary

```
CONCURRENCY PATTERNS CHEAT SHEET
═══════════════════════════════════════════════════════════

SAFETY PATTERNS:
  Confinement     → lexical scope limits data access; no sync needed
  Goroutine leak  → always pass done channel; creator is responsible

COORDINATION PATTERNS:
  or-channel      → combine N done channels; close if any closes
  for-select      → the universal goroutine loop pattern
  context         → rich cancellation with deadline + metadata

DATA FLOW PATTERNS:
  Pipeline        → chain stages via channels; each stage concurrent
  Generator       → convert discrete data to channel streams
  Fan-out/fan-in  → parallelize slow stages; merge results
  or-done         → clean channel ranging with cancellation
  tee-channel     → split one channel into two identical streams
  bridge-channel  → flatten channel-of-channels into one stream

PERFORMANCE PATTERNS:
  Queuing         → decouple stages; prevent death-spirals at entrances
  Pool (sync)     → reuse expensive objects across goroutines

ERROR HANDLING:
  Pair errors with results in structs
  Never trap errors inside goroutines
  Caller decides how many errors are too many
```

---

*[← Chapter 3 — Building Blocks](03-concurrency-building-blocks.md) | [Back to Index](../README.md) | [Chapter 5 — Concurrency at Scale →](05-concurrency-at-scale.md)*
