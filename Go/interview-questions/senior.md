# 🔴 Go — Senior Interview Questions

---

## 1. How does Go's garbage collector work?

**A:** Go uses a **tri-color concurrent mark-and-sweep** GC:

1. **Mark phase:** Starting from GC roots (globals, stacks), the GC marks all reachable objects white → grey → black
2. **Sweep phase:** Unmarked (white) objects are reclaimed

Key properties:
- **Concurrent:** Runs alongside application goroutines (stop-the-world pauses are very short)
- **Generational? No** — Go's GC is not generational; it scans the entire heap
- **Write barrier:** Ensures mutations during concurrent marking are tracked

**Tuning:**
```go
// GOGC=100 (default) — GC triggers when heap doubles
// GOGC=off — disable GC (for benchmarks)
// GOMEMLIMIT — cap total memory usage (Go 1.19+)
runtime.GC() // force a GC cycle
```

Understanding GC pressure: allocations → more frequent GC → latency spikes. Reduce by reusing objects with `sync.Pool`.

---

## 2. Explain `sync.Pool` and when to use it.

**A:** `sync.Pool` is a thread-safe cache of temporary objects to reduce GC pressure from repeated allocation/deallocation:

```go
var pool = sync.Pool{
    New: func() interface{} {
        return &bytes.Buffer{}
    },
}

buf := pool.Get().(*bytes.Buffer)
buf.Reset()
// ... use buf
pool.Put(buf) // return to pool
```

**Important caveats:**
- Objects in the pool **may be collected** at any GC cycle — it's not a persistent cache
- Not for storing state — only temporary, reusable scratch objects
- Best for: HTTP request buffers, JSON encode/decode buffers, scratch byte slices

---

## 3. What is the difference between `sync.Mutex` and `sync.RWMutex`?

**A:**
- `sync.Mutex` — exclusive lock; only one goroutine can hold it (read or write)
- `sync.RWMutex` — shared/exclusive lock:
  - Multiple goroutines can hold **RLock** (read lock) simultaneously
  - Only one goroutine can hold **Lock** (write lock), blocking all readers

```go
var mu sync.RWMutex

// Read (concurrent)
mu.RLock()
val := cache[key]
mu.RUnlock()

// Write (exclusive)
mu.Lock()
cache[key] = val
mu.Unlock()
```

Use `RWMutex` when reads vastly outnumber writes (e.g., read-heavy caches).

---

## 4. How do you profile a Go application?

**A:** Go has built-in profiling via `pprof`:

```go
import _ "net/http/pprof"

go func() {
    log.Println(http.ListenAndServe(":6060", nil))
}()
```

```bash
# CPU profile
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30

# Heap/memory profile
go tool pprof http://localhost:6060/debug/pprof/heap

# Goroutine dump
go tool pprof http://localhost:6060/debug/pprof/goroutine

# Trace (scheduler, GC, goroutine events)
curl http://localhost:6060/debug/pprof/trace?seconds=5 > trace.out
go tool trace trace.out
```

For benchmarks: `go test -bench . -memprofile mem.out -cpuprofile cpu.out`

---

## 5. Explain Go's memory model. What are the happens-before guarantees?

**A:** Go's memory model defines when a write to a variable in one goroutine is **guaranteed to be visible** to a read in another goroutine.

**Happens-before rules (selected):**
- A `go` statement that starts a goroutine happens-before the goroutine's execution begins
- A send on a channel happens-before the corresponding receive completes
- Closing a channel happens-before a receive of the zero value
- An `sync.Mutex.Unlock` happens-before a subsequent `Lock`
- `sync/atomic` operations provide sequentially consistent ordering

**Implication:** Without synchronization, the compiler and CPU are free to reorder operations. Never assume shared variable writes are visible across goroutines without a synchronization primitive.

---

## 6. What are generics in Go (1.18+)?

**A:** Go 1.18 introduced generics via type parameters:

```go
// Generic function
func Map[T, U any](s []T, f func(T) U) []U {
    result := make([]U, len(s))
    for i, v := range s {
        result[i] = f(v)
    }
    return result
}

nums := Map([]int{1, 2, 3}, func(n int) string {
    return fmt.Sprintf("%d", n)
})
```

**Type constraints:**
```go
type Number interface {
    ~int | ~float64
}

func Sum[T Number](s []T) T {
    var total T
    for _, v := range s {
        total += v
    }
    return total
}
```

Use generics to eliminate repetitive code for collections and algorithms — but don't over-generalize; interface-based polymorphism is still often cleaner.

---

## 7. How do you handle panics in production code?

**A:** Panics represent programmer errors (nil dereference, out-of-bounds). Recover from them at service boundaries to avoid crashing the whole process:

```go
func safeHandler(h http.HandlerFunc) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        defer func() {
            if rec := recover(); rec != nil {
                // log the stack trace
                buf := make([]byte, 4096)
                n := runtime.Stack(buf, false)
                log.Printf("panic: %v\n%s", rec, buf[:n])
                http.Error(w, "Internal Server Error", 500)
            }
        }()
        h(w, r)
    }
}
```

**Rule:** Recover only at boundaries (HTTP handlers, goroutine entry points). Don't use panic/recover as normal control flow.

---

## 8. What is `unsafe` package and when is it appropriate?

**A:** `unsafe` provides operations that bypass Go's type safety:

```go
// Get the size of a type
size := unsafe.Sizeof(int64(0)) // 8

// Convert between types without copy (risky)
var f float64 = 3.14
bits := *(*uint64)(unsafe.Pointer(&f))
```

**Legitimate uses:**
- Interfacing with C via `cgo`
- High-performance serialization/deserialization (e.g., `encoding/binary`)
- `reflect` package internals

**Risks:** Memory safety violations, undefined behavior on GC runs, non-portability. Only use when performance profiling proves it necessary and the scope is minimal and well-tested.

---

## 9. How do you design for testability in Go?

**A:** Key techniques:

1. **Accept interfaces, return structs** — makes dependencies injectable:
```go
type Store interface { Get(id string) (User, error) }
type Handler struct { store Store }
// Test can inject a mock Store
```

2. **Use `httptest` for HTTP:**
```go
rec := httptest.NewRecorder()
req := httptest.NewRequest("GET", "/", nil)
handler.ServeHTTP(rec, req)
```

3. **Table-driven tests** for exhaustive case coverage

4. **`testing/fstest`** for fake filesystems

5. **Build tags** to separate integration tests: `//go:build integration`

---

## 10. Explain the internals of a Go slice.

**A:** A slice is a three-word struct: `(pointer, length, capacity)`:

```
┌──────────┬────────┬──────────┐
│  ptr     │  len   │   cap    │
└──────────┴────────┴──────────┘
     │
     └──▶ [underlying array]
```

```go
s := make([]int, 3, 5) // len=3, cap=5
s2 := s[1:3]           // shares same array, len=2, cap=4

// Append past cap — allocates a NEW backing array
s3 := append(s, 1, 2, 3)
```

This explains why:
- Slices passed to functions can mutate the original's elements (shared pointer)
- But `append` beyond capacity breaks the sharing (new array)
- Always return the slice if appending: `s = append(s, ...)`

---

## 11. What is `GOMAXPROCS` and how does it affect performance?

**A:** `GOMAXPROCS` sets the number of OS threads that can execute Go code simultaneously. Default is `runtime.NumCPU()`.

- CPU-bound work: set to number of cores (default is usually optimal)
- I/O-bound work: higher values may help since blocked goroutines release their thread
- Network servers: default is almost always fine

```go
runtime.GOMAXPROCS(4) // or set via GOMAXPROCS env var
```

Changing `GOMAXPROCS` at runtime is rarely needed; profile first.

---

## 12. How do you implement a worker pool in Go?

**A:**

```go
func workerPool(jobs <-chan Job, results chan<- Result, workers int) {
    var wg sync.WaitGroup
    for i := 0; i < workers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for job := range jobs {
                results <- process(job)
            }
        }()
    }
    go func() {
        wg.Wait()
        close(results)
    }()
}
```

Closing the `jobs` channel signals workers to exit the range loop. This is the canonical bounded concurrency pattern in Go.

---

## 13. What are functional options and why are they used?

**A:** Functional options are a pattern for flexible, extensible constructors:

```go
type Server struct {
    host    string
    port    int
    timeout time.Duration
}

type Option func(*Server)

func WithPort(p int) Option    { return func(s *Server) { s.port = p } }
func WithTimeout(d time.Duration) Option { return func(s *Server) { s.timeout = d } }

func NewServer(opts ...Option) *Server {
    s := &Server{host: "localhost", port: 8080, timeout: 30 * time.Second}
    for _, opt := range opts {
        opt(s)
    }
    return s
}

// Usage
srv := NewServer(WithPort(9090), WithTimeout(10*time.Second))
```

Benefits: backward compatible (adding new options doesn't break callers), self-documenting, avoids large config structs.

---

## 14. What is `cgo` and what are its trade-offs?

**A:** `cgo` allows Go code to call C functions and vice versa:

```go
// #include <stdio.h>
import "C"

func main() {
    C.puts(C.CString("hello from C"))
}
```

**Trade-offs:**
- ✅ Reuse existing C libraries (SQLite, OpenSSL, etc.)
- ❌ Crossing the Go/C boundary is **slow** (~100ns overhead per call)
- ❌ Complicates cross-compilation
- ❌ GC doesn't manage C memory — manual `C.free` required
- ❌ Disables some Go tooling and optimizations

Minimize cgo surface area; batch calls across the boundary.

---

## 15. How do you implement graceful shutdown in a Go HTTP server?

**A:**

```go
srv := &http.Server{Addr: ":8080"}

go func() {
    if err := srv.ListenAndServe(); err != http.ErrServerClosed {
        log.Fatal(err)
    }
}()

// Wait for interrupt signal
quit := make(chan os.Signal, 1)
signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
<-quit

ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
defer cancel()

if err := srv.Shutdown(ctx); err != nil {
    log.Fatal("forced shutdown:", err)
}
log.Println("server stopped")
```

`Shutdown` stops accepting new connections, waits for active requests to finish (up to the context deadline), then returns.

---

## 16. How does `sync.Map` differ from a regular map with a mutex?

**A:** `sync.Map` is optimized for two specific access patterns:
- Write-once, read-many (entry written once, then only read)
- Disjoint sets of keys per goroutine

```go
var m sync.Map

// Store, Load, LoadOrStore, Delete, Range
m.Store("key", 42)
val, ok := m.Load("key")

m.Range(func(k, v interface{}) bool {
    fmt.Println(k, v)
    return true // continue; return false to stop
})
```

For general-purpose concurrent maps (frequent writes, shared keys), a sharded `map` + `sync.RWMutex` is often faster due to lower overhead. Always benchmark before choosing `sync.Map`.

---

## 17. What is escape analysis in Go?

**A:** The Go compiler's escape analysis determines whether a variable should be stack-allocated (fast, no GC) or heap-allocated (slower, GC pressure):

```go
// Does NOT escape — stays on stack
func sum(a, b int) int {
    result := a + b
    return result
}

// Escapes to heap — pointer outlives the function
func newInt() *int {
    x := 42
    return &x // x escapes: must be on heap
}
```

```bash
go build -gcflags="-m" ./...  # see escape analysis decisions
```

**Reduce allocations:** Avoid returning pointers to local variables when unnecessary; use value receivers on small structs.

---

## 18. How do you implement a lock-free ring buffer in Go?

**A:** Using `sync/atomic` for head/tail indices:

```go
type RingBuffer struct {
    data  []interface{}
    head  uint64
    tail  uint64
    cap   uint64
}

func NewRingBuffer(size uint64) *RingBuffer {
    return &RingBuffer{data: make([]interface{}, size), cap: size}
}

func (r *RingBuffer) Push(item interface{}) bool {
    tail := atomic.LoadUint64(&r.tail)
    head := atomic.LoadUint64(&r.head)
    if tail-head == r.cap { return false } // full
    r.data[tail%r.cap] = item
    atomic.AddUint64(&r.tail, 1)
    return true
}

func (r *RingBuffer) Pop() (interface{}, bool) {
    head := atomic.LoadUint64(&r.head)
    tail := atomic.LoadUint64(&r.tail)
    if head == tail { return nil, false } // empty
    item := r.data[head%r.cap]
    atomic.AddUint64(&r.head, 1)
    return item, true
}
```

---

## 19. What are `//go:noescape`, `//go:nosplit`, and other compiler directives?

**A:** Compiler directives (pragmas) that control low-level behavior — only for runtime/stdlib-level code:

- `//go:noescape` — tells the compiler that a function's arguments don't escape to the heap (used with `asm` implementations)
- `//go:nosplit` — prevents stack splitting; function must not overflow a small stack (used in runtime, goroutine creation path)
- `//go:inline` — hint to inline the function
- `//go:noinline` — prevent inlining (useful in benchmarks to avoid optimization skewing results)
- `//go:linkname` — access unexported symbols from another package (unsafe, rarely appropriate)

These are only for situations where you're writing very low-level code. In application code, they're almost never needed.

---

## 20. How do you implement graceful cancellation propagation across a goroutine tree?

**A:**

```go
func orchestrate(ctx context.Context) error {
    g, ctx := errgroup.WithContext(ctx)

    results := make(chan Result, 10)

    // Workers — all share the same ctx; ctx cancellation stops all
    for i := 0; i < 5; i++ {
        i := i
        g.Go(func() error {
            return worker(ctx, i, results)
        })
    }

    // Collector — also in errgroup
    g.Go(func() error {
        return collect(ctx, results)
    })

    return g.Wait() // cancels ctx on first error; waits for all to stop
}

func worker(ctx context.Context, id int, out chan<- Result) error {
    for {
        select {
        case <-ctx.Done():
            return ctx.Err() // clean exit
        default:
        }
        result, err := doWork(ctx, id)
        if err != nil { return err }
        out <- result
    }
}
```

---

## 21. What is `pprof` trace vs CPU profile — when do you use each?

**A:**

| | CPU Profile | Execution Trace |
|--|------------|-----------------|
| What it shows | Where CPU time is spent (function call graph) | Goroutine scheduling, GC events, syscalls, channel ops — timeline |
| Sampling | Statistical (100Hz by default) | Every event recorded |
| Overhead | ~5-10% | Higher — use short durations |
| Use for | Hot functions, algorithmic bottlenecks | Goroutine stalls, scheduler latency, GC pauses, lock contention |

```bash
# CPU profile
curl -s "http://localhost:6060/debug/pprof/profile?seconds=30" > cpu.pprof
go tool pprof -http :8080 cpu.pprof

# Execution trace
curl -s "http://localhost:6060/debug/pprof/trace?seconds=5" > trace.out
go tool trace trace.out
```

---

## 22. How does Go's HTTP client handle connection pooling?

**A:** `http.DefaultClient` uses a `Transport` that maintains a connection pool (`http.Transport`):

```go
transport := &http.Transport{
    MaxIdleConns:        100,              // global idle connections
    MaxIdleConnsPerHost: 10,              // per-host idle connections
    MaxConnsPerHost:     50,              // total per-host (idle + active)
    IdleConnTimeout:     90 * time.Second,
    TLSHandshakeTimeout: 10 * time.Second,
    DisableCompression:  false,
}

client := &http.Client{
    Transport: transport,
    Timeout:   30 * time.Second,
}
```

**Critical:** Always read and close `resp.Body` — connections are only returned to the pool after the body is fully consumed and closed:

```go
resp, err := client.Do(req)
if err != nil { return err }
defer resp.Body.Close()
io.Copy(io.Discard, resp.Body) // drain before close
```

---

## 23. How do you implement singleflight to prevent thundering herd?

**A:**

```go
import "golang.org/x/sync/singleflight"

var g singleflight.Group

func getUser(id string) (*User, error) {
    result, err, shared := g.Do(id, func() (interface{}, error) {
        return db.GetUser(id) // only one call per key at a time
    })
    if err != nil { return nil, err }
    _ = shared // true if result was shared with other callers
    return result.(*User), nil
}
```

All concurrent calls for the same key block and receive the same result. Prevents N simultaneous DB calls on a cache miss for a hot key.

---

## 24. How does the `nethttp` muxer compare to third-party routers like `chi` or `gorilla/mux`?

**A:**

**`net/http` ServeMux (Go 1.22+):**
- Now supports path parameters: `{id}` and method matching: `GET /users/{id}`
- Good enough for most APIs since Go 1.22
- Zero dependency

**chi:**
- Lightweight, idiomatic, composable middleware
- Nested routers, named parameters, regexp constraints
- Used by many production Go APIs

**gorilla/mux:**
- Mature, feature-rich (regex routes, host matching, subrouters)
- Now in maintenance mode — chi or stdlib preferred for new projects

**Decision:** Use `net/http` 1.22+ for simple APIs; `chi` for complex routing with middleware chains.

---

## 25. What is `iter` package (Go 1.23) and range-over functions?

**A:** Go 1.23 introduced first-class iterators — functions can now be the target of `range`:

```go
// An iterator is a function that accepts a yield function
func Fibonacci() iter.Seq[int] {
    return func(yield func(int) bool) {
        a, b := 0, 1
        for {
            if !yield(a) { return } // stop if consumer breaks
            a, b = b, a+b
        }
    }
}

for n := range Fibonacci() {
    if n > 100 { break }
    fmt.Println(n)
}
```

Enables lazy, composable, memory-efficient sequence processing without channels or goroutines.

---

## 26. What is the difference between a concurrent and parallel program in Go?

**A:**
- **Concurrent** — multiple tasks are in progress at the same time (interleaved), but not necessarily running simultaneously
- **Parallel** — multiple tasks run simultaneously on multiple CPU cores

```
Concurrent (GOMAXPROCS=1):
Goroutine A: ---run---pause---run---
Goroutine B: --------run---pause---run

Parallel (GOMAXPROCS=4):
Goroutine A: ---run---run---
Goroutine B: ---run---run--- (literally at the same time)
```

Go's goroutines are concurrent by design; they become parallel when `GOMAXPROCS > 1` and there are idle OS threads.

Rob Pike: "Concurrency is about dealing with lots of things at once. Parallelism is about doing lots of things at once."

---

## 27. How do you detect and fix data races in Go?

**A:**

**Detection:**
```bash
go test -race ./...
go run -race main.go
```

The race detector instruments every memory access and reports races at runtime with full goroutine stacks.

**Common causes and fixes:**

| Cause | Fix |
|-------|-----|
| Concurrent map read/write | `sync.RWMutex` or `sync.Map` |
| Shared slice append | Channel or mutex |
| Closure capturing loop variable | Pass as function argument |
| Double-checked locking | `sync.Once` |
| Global variable | Protect with `sync/atomic` or mutex |

Always run the race detector in CI, even if it slows tests down — it catches bugs that are nearly impossible to find manually.
