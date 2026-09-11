# 🟡 Go — Mid-Level Interview Questions

---

## 1. Explain goroutine leaks. How do you prevent them?

**Q:** What is a goroutine leak and how do you detect/prevent it?

**A:** A goroutine leak occurs when a goroutine is started but never terminates — it blocks forever, consuming memory and scheduler resources.

**Common causes:**
- Sending to an unbuffered channel with no receiver
- Receiving from a channel that nobody ever sends to
- Waiting on a `sync.WaitGroup` that never reaches zero

**Prevention:**
```go
// Use context for cancellation
func worker(ctx context.Context) {
    for {
        select {
        case <-ctx.Done():
            return // clean exit
        default:
            // do work
        }
    }
}

ctx, cancel := context.WithCancel(context.Background())
go worker(ctx)
// ...
cancel() // signals goroutine to stop
```

**Detection:** Use `runtime.NumGoroutine()` in tests or the `pprof` goroutine profile.

---

## 2. What is the difference between buffered and unbuffered channels?

**A:**

| | Unbuffered | Buffered |
|--|-----------|----------|
| Created with | `make(chan int)` | `make(chan int, N)` |
| Send blocks when | No receiver ready | Buffer is full |
| Receive blocks when | No sender ready | Buffer is empty |
| Synchronization | Both sides must be ready simultaneously | Decoupled |

```go
// Unbuffered — sender blocks until receiver is ready
ch := make(chan int)

// Buffered — sender can proceed without a receiver (up to cap)
ch := make(chan int, 10)
```

Use buffered channels to decouple producer/consumer or avoid deadlocks in known-size scenarios.

---

## 3. What is `select` and how does it work?

**A:** `select` lets a goroutine wait on multiple channel operations simultaneously. It picks whichever case is ready; if multiple are ready, it picks one at random:

```go
select {
case msg := <-ch1:
    fmt.Println("from ch1:", msg)
case msg := <-ch2:
    fmt.Println("from ch2:", msg)
case <-time.After(1 * time.Second):
    fmt.Println("timeout")
default:
    fmt.Println("nothing ready") // non-blocking
}
```

`select` with a `default` case is non-blocking. Without `default`, it blocks until one case is ready.

---

## 4. What is `sync.Mutex` and when do you use it vs channels?

**A:** `sync.Mutex` is a mutual exclusion lock — only one goroutine can hold it at a time:

```go
var mu sync.Mutex
counter := 0

mu.Lock()
counter++
mu.Unlock()
```

**When to use each:**

| Use Mutex when | Use Channels when |
|----------------|------------------|
| Protecting shared state | Passing ownership of data |
| Simple critical sections | Signaling/coordination between goroutines |
| Cache, counters, maps | Pipelines, producer/consumer |

Rule of thumb: **share state → mutex; share data → channel**.

---

## 5. Explain `sync.WaitGroup`.

**A:** `WaitGroup` waits for a collection of goroutines to finish:

```go
var wg sync.WaitGroup

for i := 0; i < 5; i++ {
    wg.Add(1)
    go func(n int) {
        defer wg.Done()
        fmt.Println("worker", n)
    }(i)
}

wg.Wait() // blocks until all Done() calls balance the Add() calls
```

Always call `Add()` before launching the goroutine, and `Done()` via `defer`.

---

## 6. How does the Go scheduler work?

**A:** Go uses an **M:N scheduler** — it multiplexes M goroutines onto N OS threads (via logical processors, `GOMAXPROCS`).

Key components:
- **G** — goroutine
- **M** — OS thread
- **P** — logical processor (processor context, runs goroutines)

`GOMAXPROCS` controls how many OS threads run Go code simultaneously (defaults to number of CPU cores).

The scheduler is **cooperative + preemptive** (since Go 1.14): goroutines yield at function calls, channel ops, or system calls. Long-running goroutines can also be preempted.

---

## 7. What are closures in Go and what pitfall do they introduce in goroutines?

**A:** A closure captures variables from its surrounding scope:

```go
x := 10
f := func() { fmt.Println(x) } // captures x
x = 20
f() // prints 20
```

**Common goroutine pitfall** — capturing loop variables:

```go
// BUG: all goroutines print the same value
for i := 0; i < 3; i++ {
    go func() { fmt.Println(i) }() // captures i by reference
}

// FIX: pass as parameter
for i := 0; i < 3; i++ {
    go func(n int) { fmt.Println(n) }(i) // copy at call time
}
```

---

## 8. What is the difference between `new` and `make`?

**A:**
- `new(T)` — allocates memory for type T, zeroes it, returns a `*T` (pointer). Works for any type.
- `make(T, ...)` — initializes and returns an **initialized** value (not pointer) for slices, maps, and channels only.

```go
p := new(int)      // *int, points to zero int
s := make([]int, 5) // []int of length 5
m := make(map[string]int) // initialized map
```

You almost never use `new` directly; `make` is essential for slices, maps, and channels.

---

## 9. How does Go handle dependencies (Go Modules)?

**A:** Go Modules (since Go 1.11, default since 1.13) is the official dependency management system:

```bash
go mod init github.com/user/project  # create go.mod
go get github.com/some/dep@v1.2.3    # add dependency
go mod tidy                          # remove unused, add missing
go mod vendor                        # vendor dependencies
```

`go.mod` defines the module path and dependencies; `go.sum` pins cryptographic hashes for reproducibility.

---

## 10. What is the `context` package used for?

**A:** `context.Context` carries deadlines, cancellation signals, and request-scoped values across API boundaries:

```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
resp, err := http.DefaultClient.Do(req)
// If 5s elapses, the request is cancelled automatically
```

Always pass `ctx` as the **first parameter** to functions that do I/O, call other services, or can be cancelled.

---

## 11. How do you write tests in Go?

**A:** Go has a built-in testing framework:

```go
// math_test.go
func TestAdd(t *testing.T) {
    got := Add(2, 3)
    want := 5
    if got != want {
        t.Errorf("Add(2, 3) = %d; want %d", got, want)
    }
}
```

```bash
go test ./...           # run all tests
go test -run TestAdd    # run specific test
go test -cover          # show coverage
go test -bench .        # run benchmarks
```

Table-driven tests are idiomatic in Go:

```go
func TestAdd(t *testing.T) {
    cases := []struct{ a, b, want int }{
        {1, 2, 3}, {0, 0, 0}, {-1, 1, 0},
    }
    for _, tc := range cases {
        got := Add(tc.a, tc.b)
        if got != tc.want {
            t.Errorf("Add(%d, %d) = %d; want %d", tc.a, tc.b, got, tc.want)
        }
    }
}
```

---

## 12. What are embedding and composition in Go?

**A:** Go uses **composition over inheritance** via struct embedding:

```go
type Logger struct{}
func (l Logger) Log(msg string) { fmt.Println(msg) }

type Server struct {
    Logger // embedded — promotes Log() to Server
    Port int
}

s := Server{}
s.Log("started") // calls Logger.Log directly
```

The embedded type's methods are promoted to the outer type. This is Go's answer to inheritance.

---

## 13. What is a race condition and how do you detect it in Go?

**A:** A race condition occurs when two goroutines access shared memory concurrently and at least one is writing.

**Detection:** Go's built-in race detector:
```bash
go test -race ./...
go run -race main.go
```

**Fix:** Protect shared state with `sync.Mutex`, `sync.RWMutex`, `sync/atomic`, or redesign with channels.

---

## 14. What are variadic functions?

**A:** Functions that accept a variable number of arguments:

```go
func sum(nums ...int) int {
    total := 0
    for _, n := range nums {
        total += n
    }
    return total
}

sum(1, 2, 3)          // 6
nums := []int{1, 2, 3}
sum(nums...)          // spread slice into variadic
```

---

## 15. Explain `io.Reader` and `io.Writer` — why are they important?

**A:** These are the two most fundamental interfaces in the Go standard library:

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}
type Writer interface {
    Write(p []byte) (n int, err error)
}
```

They make code composable — any type satisfying `io.Reader` works with `io.Copy`, `bufio.Scanner`, `json.Decoder`, HTTP bodies, files, gzip, etc. This is Go's version of Unix pipes at the code level.

---

## 16. What is `context.WithValue` and what are its pitfalls?

**A:** `context.WithValue` stores a key-value pair in the context, accessible downstream:

```go
type ctxKey string
const TraceIDKey ctxKey = "trace_id"

ctx := context.WithValue(r.Context(), TraceIDKey, "abc-123")
traceID := ctx.Value(TraceIDKey).(string)
```

**Pitfalls:**
- Never use built-in types (string, int) as keys — causes collisions across packages. Always use a package-private type.
- Values in context are untyped — requires assertion; panics if wrong type
- Not a replacement for function parameters — only for request-scoped metadata (trace IDs, auth info)

---

## 17. How do you implement the pipeline pattern in Go?

**A:** A pipeline is a series of stages connected by channels:

```go
func generate(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for _, n := range nums { out <- n }
    }()
    return out
}

func square(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for n := range in { out <- n * n }
    }()
    return out
}

// Usage
for n := range square(generate(2, 3, 4)) {
    fmt.Println(n) // 4, 9, 16
}
```

---

## 18. What is `errgroup` and how does it improve on `WaitGroup`?

**A:** `golang.org/x/sync/errgroup` runs goroutines concurrently and returns the first error:

```go
g, ctx := errgroup.WithContext(context.Background())

g.Go(func() error {
    return fetchUser(ctx, userID)
})
g.Go(func() error {
    return fetchOrders(ctx, userID)
})

if err := g.Wait(); err != nil {
    log.Fatal(err) // first non-nil error from any goroutine
}
```

Cleaner than `sync.WaitGroup` when you need to propagate errors from goroutines.

---

## 19. What is the `once` pattern with `sync.Once`?

**A:** `sync.Once` ensures a function runs exactly once, regardless of how many goroutines call it — the canonical singleton/lazy init pattern:

```go
var (
    instance *DB
    once     sync.Once
)

func GetDB() *DB {
    once.Do(func() {
        instance = connectToDB()
    })
    return instance
}
```

Safe for concurrent use. The `Do` function blocks all callers until the first call completes.

---

## 20. Explain Go's interface nil gotcha.

**A:** An interface has two components: `(type, value)`. An interface is only `nil` when both are nil:

```go
var p *MyError = nil    // typed nil pointer
var err error = p       // err has (type=*MyError, value=nil)

fmt.Println(err == nil) // false! — type is set

// Fix: always return untyped nil for interfaces
func doSomething() error {
    var p *MyError = nil
    if somethingFailed {
        return p // BUG
    }
    return nil  // correct
}
```

---

## 21. What is `atomic` package and when do you use it?

**A:** `sync/atomic` provides lock-free atomic operations on integer and pointer types:

```go
var counter int64

// Safe concurrent increment
atomic.AddInt64(&counter, 1)

// Load/Store — atomic read/write of 64-bit values
val := atomic.LoadInt64(&counter)
atomic.StoreInt64(&counter, 0)

// Compare-and-swap
swapped := atomic.CompareAndSwapInt64(&counter, old, new)
```

Use for simple counters, flags, and lock-free state. For complex state transitions, use `sync.Mutex`.

---

## 22. How do you handle timeouts in Go?

**A:** Three approaches:

```go
// 1. context.WithTimeout (preferred — composes with cancellation)
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()
result, err := fetchData(ctx)

// 2. time.After in select
select {
case result := <-ch:
    process(result)
case <-time.After(5 * time.Second):
    return errors.New("timeout")
}

// 3. time.AfterFunc — callback after duration
timer := time.AfterFunc(5*time.Second, func() {
    cancel()
})
defer timer.Stop()
```

---

## 23. What is the `http.Handler` interface and how do you build middleware?

**A:**
```go
type Handler interface {
    ServeHTTP(ResponseWriter, *Request)
}

// Middleware wraps a handler
func Logger(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s %v", r.Method, r.URL.Path, time.Since(start))
    })
}

// Chain middleware
mux := http.NewServeMux()
mux.HandleFunc("/", homeHandler)
http.ListenAndServe(":8080", Logger(mux))
```

---

## 24. How do you decode JSON in Go safely?

**A:**
```go
type User struct {
    Name  string `json:"name"`
    Email string `json:"email"`
    Age   int    `json:"age,omitempty"`
}

// Decode from HTTP body (streaming, no full-load)
var u User
dec := json.NewDecoder(r.Body)
dec.DisallowUnknownFields() // strict mode
if err := dec.Decode(&u); err != nil {
    http.Error(w, "bad request", 400)
    return
}

// Marshal
data, err := json.Marshal(u)

// Pretty print
data, err = json.MarshalIndent(u, "", "  ")
```

---

## 25. What is `go generate` and when do you use it?

**A:** `go generate` runs arbitrary commands before building — typically for code generation:

```go
//go:generate mockgen -source=service.go -destination=mock_service.go
//go:generate stringer -type=Status
```

```bash
go generate ./...
```

Common uses: mock generation (`mockgen`), generating `String()` methods for enums (`stringer`), embedding static assets, protobuf compilation. The `//go:generate` directive is just a comment that `go generate` reads and executes.

---

## 26. What is the difference between `os.Exit` and `panic`?

**A:**
- `os.Exit(code)` — terminates immediately; deferred functions do NOT run; used for clean CLI exit codes
- `panic` — unwinds the stack, runs deferred functions, prints stack trace; can be recovered with `recover()`

```go
// Use panic for unrecoverable programmer errors
if len(os.Args) < 2 {
    panic("expected at least one argument") // developer error
}

// Use os.Exit for intentional program termination
if err := run(); err != nil {
    fmt.Fprintln(os.Stderr, err)
    os.Exit(1)
}
```

---

## 27. What are Go build tags?

**A:** Build tags control which files are included in a build:

```go
//go:build linux
// +build linux  (old syntax, still needed for Go < 1.17)

package mypackage
```

```bash
go build -tags integration ./...
go test -tags integration ./...
```

Common uses:
- Platform-specific code (`linux`, `darwin`, `windows`)
- Integration test files (`//go:build integration`)
- Feature flags during development

---

## 28. What is `os.ReadFile` vs `bufio.Scanner` for reading files?

**A:**
```go
// os.ReadFile — reads entire file into memory (fine for small files)
data, err := os.ReadFile("config.yaml")

// bufio.Scanner — line-by-line, memory-efficient for large files
f, err := os.Open("large.log")
defer f.Close()

scanner := bufio.NewScanner(f)
for scanner.Scan() {
    line := scanner.Text() // no newline
    process(line)
}
if err := scanner.Err(); err != nil {
    log.Fatal(err)
}
```

---

## 29. How do you implement a simple rate limiter in Go?

**A:** Using `time.Ticker` (fixed rate) or `golang.org/x/time/rate` (token bucket):

```go
// Simple token bucket
import "golang.org/x/time/rate"

limiter := rate.NewLimiter(rate.Limit(100), 10) // 100 req/s, burst of 10

func handleRequest(ctx context.Context) error {
    if err := limiter.Wait(ctx); err != nil {
        return err // context cancelled
    }
    return doWork()
}
```

---

## 30. What is `go vet` and what does it catch?

**A:** `go vet` is the built-in static analyzer — catches bugs that are syntactically valid but logically wrong:

- Incorrect `Printf` format strings: `fmt.Printf("%d", "string")`
- Unreachable code after `return`
- Passing non-pointer to `Unmarshal`
- Misuse of `sync.Mutex` (copying a mutex)
- Unused results from functions that must be checked (e.g., `exec.Command`)

```bash
go vet ./...
```

Run it in CI — it catches real bugs. Complement with `staticcheck` for even more analysis.
