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
