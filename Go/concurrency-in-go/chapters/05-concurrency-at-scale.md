# Chapter 5: Concurrency at Scale

> *"With just a little forethought, and minimal overhead, you can make your error handling an asset to your system, and a delight to your users."*

---

## Core Concept

When your concurrent system grows beyond a single function into services, distributed systems, and long-running processes, new challenges emerge: how errors propagate, how to handle timeouts and cancellations gracefully, how to monitor goroutine health, and how to protect shared resources from overload.

---

## 5.1 Error Propagation — Well-Formed Errors

Errors in concurrent systems often lose context by the time they reach the user. A well-formed error contains four pieces of information:

```
1. WHAT HAPPENED:      "disk full", "connection refused"
2. WHEN & WHERE:       stack trace, machine, UTC timestamp
3. USER-FACING MSG:    concise, human-readable, one line
4. HOW TO LEARN MORE:  log ID to cross-reference full details
```

**Framework: Bugs vs. Known Edge Cases**

```
Every error falls into one of two categories:

  KNOWN EDGE CASE   → well-formed, carries full context
                      "cannot run job: binary not executable"

  BUG (raw error)   → unwrapped, unexpected, missing context
                      → show generic "unexpected error" to user
                      → always log full details + log ID
```

**Module boundary rule:** Wrap errors when they cross module/package boundaries:

```go
type MyError struct {
    Inner      error
    Message    string
    StackTrace string
    Misc       map[string]interface{}
}

func wrapError(err error, messagef string, args ...interface{}) MyError {
    return MyError{
        Inner:      err,
        Message:    fmt.Sprintf(messagef, args...),
        StackTrace: string(debug.Stack()),
        Misc:       make(map[string]interface{}),
    }
}

// At module boundary: wrap with context
func runJob(id string) error {
    isExecutable, err := isGloballyExec(jobBinPath)
    if err != nil {
        return IntermediateErr{wrapError(
            err,
            "cannot run job %q: requisite binaries not available", id,
        )}
    }
    // ...
}

// At the top: distinguish bug from known error
if _, ok := err.(IntermediateErr); ok {
    msg = err.Error()          // ← well-formed: show to user
} else {
    msg = "unexpected error"   // ← raw/bug: show generic message
}
handleError(logID, err, msg)
```

---

## 5.2 Timeouts and Cancellation

### When to Use Timeouts

| Reason | Description |
|--------|-------------|
| **System saturation** | Queue is full; request won't be retried or data goes stale |
| **Stale data** | The result will be useless by the time it's produced |
| **Deadlock prevention** | Timeout ensures the system always unblocks eventually |

### Why Cancellation Is Hard — Preemptability

```go
// Problem: reallyLongCalculation is not preemptable
select { case value = <-valueStream: }
result := reallyLongCalculation(value)  // ← blocks for a long time!
select { case resultStream <- result: }

// Solution: make every long operation check done
reallyLongCalculation := func(done <-chan interface{}, value interface{}) interface{} {
    intermediateResult := longCalculation(done, value)   // ← pass done down
    return longCalculation(done, intermediateResult)      // ← and down again
}
```

**Rule:** Every non-trivial operation in a goroutine must be preemptable. Break work into small atomic chunks, each checking `done`.

### Avoiding Duplicate Messages

When goroutines are restarted (e.g., after a crash), downstream may receive the same message twice:

```
Stage A sends result → Stage B receives it
Stage A is restarted → Stage A sends result AGAIN → Stage B receives it twice
```

Solutions:
1. **Accept first or last** — if your algorithm is idempotent
2. **Heartbeats** — bidirectional confirmation before sending (see section 5.3)
3. **Minimize shared state writes** — compute first, write once

```go
// WRONG: multiple writes, multiple rollback surfaces
result := add(1, 2, 3)
writeTallyToState(result)    // ← rollback needed if canceled here
result = add(result, 4, 5, 6)
writeTallyToState(result)    // ← and here

// RIGHT: compute all, write once
result := add(1, 2, 3, 4, 5, 6, 7, 8, 9)
writeTallyToState(result)    // ← single write, minimal rollback surface
```

---

## 5.3 Heartbeats — Monitor Goroutine Liveness

Heartbeats let goroutines signal "I'm alive and working" to their monitors.

### Interval-Based Heartbeats (for idle goroutines)

```go
doWork := func(done <-chan interface{}, pulseInterval time.Duration) (
    <-chan interface{}, <-chan time.Time,
) {
    heartbeat := make(chan interface{})
    results := make(chan time.Time)
    go func() {
        defer close(heartbeat)
        defer close(results)
        pulse := time.Tick(pulseInterval)
        workGen := time.Tick(2 * pulseInterval)

        sendPulse := func() {
            select {
            case heartbeat <- struct{}{}:
            default:  // no one listening? skip — heartbeat is best-effort
            }
        }
        for {
            select {
            case <-done:
                return
            case <-pulse:
                sendPulse()
            case r := <-workGen:
                // ... send result with pulse guard
                results <- r
            }
        }
    }()
    return heartbeat, results
}

// Consumer: monitor both heartbeats AND results
const timeout = 2 * time.Second
heartbeat, results := doWork(done, timeout/2)
for {
    select {
    case _, ok := <-heartbeat:
        if !ok { return }
        fmt.Println("pulse")
    case r, ok := <-results:
        if !ok { return }
        fmt.Printf("results %v\n", r.Second())
    case <-time.After(timeout):
        fmt.Println("worker goroutine is not healthy!")  // ← detected!
        return
    }
}
```

### Unit-of-Work Heartbeats (for testing)

```go
// Goroutine sends a heartbeat BEFORE each unit of work
doWork := func(done <-chan interface{}) (<-chan interface{}, <-chan int) {
    heartbeat := make(chan interface{}, 1)  // buffered: at least 1 pulse always sent
    intStream := make(chan int)
    go func() {
        time.Sleep(2 * time.Second)  // simulate startup delay
        for _, n := range nums {
            select {                  // non-blocking heartbeat
            case heartbeat <- struct{}{}:
            default:
            }
            select {
            case <-done:
                return
            case intStream <- n:
            }
        }
    }()
    return heartbeat, intStream
}

// GOOD TEST: waits for goroutine to actually start, not for an arbitrary timeout
func TestDoWork(t *testing.T) {
    heartbeat, results := DoWork(done, 0, 1, 2, 3)
    <-heartbeat  // ← wait until goroutine has started its first iteration
    for r := range results {
        // verify results...
    }
}
```

> 💡 **Testing benefit:** Heartbeats make tests deterministic. Instead of `time.After(1*time.Second)` (which fails on slow machines), wait for the heartbeat — exactly right timing, every time.

---

## 5.4 Replicated Requests — Fastest Wins

For latency-sensitive operations, send the same request to multiple goroutines and use the first result:

```go
doWork := func(done <-chan interface{}, id int, wg *sync.WaitGroup, result chan<- int) {
    started := time.Now()
    defer wg.Done()
    simulatedLoadTime := time.Duration(1+rand.Intn(5)) * time.Second
    select {
    case <-done:
    case <-time.After(simulatedLoadTime):
    }
    select {
    case <-done:
    case result <- id:
    }
    fmt.Printf("%v took %v\n", id, time.Since(started))
}

done := make(chan interface{})
result := make(chan int)
var wg sync.WaitGroup
wg.Add(10)
for i := 0; i < 10; i++ {
    go doWork(done, i, &wg, result)
}
firstReturned := <-result  // ← take first result
close(done)                // ← cancel all remaining handlers
wg.Wait()
fmt.Printf("Received answer from #%v\n", firstReturned)
```

```
10 handlers, random load 1-5 seconds:
  Handler #8 returned in 1.000s → we use this result
  Handlers #1,3 returned ~1s later (unnecessary, but canceled)
  Handlers #5,6 would have taken 4-5s (never ran to completion)
  
  Net saving: up to 4 seconds vs. using a single handler
```

**Caveat:** All handlers need equal opportunity and resources (different paths to the same data store, or entirely different data stores for true fault tolerance).

---

## 5.5 Rate Limiting — Protect Your System

**Why rate limit?**
- Prevent DoS (intentional and accidental)
- Protect other users from one noisy user
- Prevent "self-DDoS" under burst load
- Charge correctly for API access

**Token Bucket Algorithm:**
```
d = bucket depth (max burst)
r = refill rate (tokens/second)

How it works:
  1. User needs a token to make a request
  2. Token is removed from bucket on each request
  3. Tokens refill at rate r (up to max d)
  4. If bucket is empty → block until token available

Example: d=5, r=1 token/second
  T=0: bucket=[5], make 5 requests instantly (burst)
  T=1: bucket=[1], make 1 more
  T=2: bucket=[1], make 1 more
  → Rate limited to 1/second after burst
```

**Go implementation using `golang.org/x/time/rate`:**

```go
func Open() *APIConnection {
    return &APIConnection{
        // Per-second limit: 2 req/s, burst of 2
        // Per-minute limit: 10 req/min, burst of 10
        rateLimiter: MultiLimiter(
            rate.NewLimiter(Per(2, time.Second), 2),
            rate.NewLimiter(Per(10, time.Minute), 10),
        ),
    }
}

func (a *APIConnection) ReadFile(ctx context.Context) error {
    if err := a.rateLimiter.Wait(ctx); err != nil {  // ← blocks until token available
        return err
    }
    // do work
    return nil
}
```

**Composable multi-tier limiter:**
```go
// Combine API limit + resource-specific limit
func (a *APIConnection) ReadFile(ctx context.Context) error {
    err := MultiLimiter(a.apiLimit, a.diskLimit).Wait(ctx)
    // ...
}
func (a *APIConnection) ResolveAddress(ctx context.Context) error {
    err := MultiLimiter(a.apiLimit, a.networkLimit).Wait(ctx)
    // ...
}
```

```
Without rate limiting: all 20 requests fire at T=0
With rate limiting (2/s + 10/min):
  T=0:  requests 1-2  (burst)
  T=1:  request 3
  T=2:  request 4
  ...
  T=10: request 11  ← minute limit kicks in
  T=16: request 12
  T=22: request 13  ← now every 6 seconds (minute bucket refill)
  ...
```

---

## 5.6 Healing Unhealthy Goroutines

In long-running processes, goroutines can get stuck. A **steward** monitors a **ward** goroutine and restarts it if the heartbeat stops:

```go
type startGoroutineFn func(done <-chan interface{}, pulseInterval time.Duration) <-chan interface{}

newSteward := func(timeout time.Duration, startGoroutine startGoroutineFn) startGoroutineFn {
    return func(done <-chan interface{}, pulseInterval time.Duration) <-chan interface{} {
        heartbeat := make(chan interface{})
        go func() {
            defer close(heartbeat)
            var wardDone chan interface{}
            var wardHeartbeat <-chan interface{}

            startWard := func() {
                wardDone = make(chan interface{})
                wardHeartbeat = startGoroutine(or(wardDone, done), timeout/2)
            }
            startWard()
            pulse := time.Tick(pulseInterval)

        monitorLoop:
            for {
                timeoutSignal := time.After(timeout)
                for {
                    select {
                    case <-pulse:
                        select { case heartbeat <- struct{}{}: default: }
                    case <-wardHeartbeat:
                        continue monitorLoop  // ← ward is healthy, reset timeout
                    case <-timeoutSignal:
                        log.Println("steward: ward unhealthy; restarting")
                        close(wardDone)
                        startWard()          // ← restart the ward
                        continue monitorLoop
                    case <-done:
                        return
                    }
                }
            }
        }()
        return heartbeat
    }
}
```

```
Demo output (misbehaving ward that stops after 2 iterations):
  18:28:07 ward: Hello, I'm irresponsible!
  18:28:11 steward: ward unhealthy; restarting
  18:28:11 ward: Hello, I'm irresponsible!
  18:28:15 steward: ward unhealthy; restarting
  18:28:15 ward: Hello, I'm irresponsible!
  18:28:16 main: halting steward and ward.
```

> 📌 **Note:** Restarted wards start from scratch. If your ward is stateful (e.g., iterating a list), use closures to preserve state across restarts.

---

## Visual Summary

```
CONCURRENCY AT SCALE — KEY TECHNIQUES
═══════════════════════════════════════════════════════════

ERROR PROPAGATION:
  Two types: bugs (raw errors) vs. known edge cases (wrapped errors)
  Wrap errors at module boundaries with context + stack trace
  Show generic "unexpected error" for bugs; specific message for known errors

TIMEOUTS & CANCELLATION:
  Use context.WithTimeout / WithDeadline / WithCancel
  Make all long operations preemptable — pass done/ctx down
  Minimize shared-state writes (compute first, write once)

HEARTBEATS:
  Interval-based → detect stuck/frozen goroutines
  Per-work-unit  → make tests deterministic (no time.Sleep!)
  Always use default clause — heartbeats are best-effort

REPLICATED REQUESTS:
  Send to N handlers, use first result, cancel the rest
  Trade resource cost for latency reduction
  Requires handlers with independent resources

RATE LIMITING:
  Token bucket: depth (burst) + rate (refill)
  Compose limiters (per-second + per-minute + per-resource)
  Use golang.org/x/time/rate package
  Rate limits protect you, your users, and your system

HEALING GOROUTINES:
  Steward monitors ward via heartbeat
  Restarts ward if heartbeat stops (steward is also monitorable)
  Use closures to make wards carry complex, stateful behavior
```

---

*[← Chapter 4 — Concurrency Patterns](04-concurrency-patterns.md) | [Back to Index](../README.md) | [Chapter 6 — Goroutines and the Go Runtime →](06-goroutines-and-the-go-runtime.md)*
