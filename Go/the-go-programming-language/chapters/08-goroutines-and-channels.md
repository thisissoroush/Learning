# Chapter 8: Goroutines and Channels

> *"Go's concurrency is based on CSP (Communicating Sequential Processes): goroutines communicate by passing values, not by sharing memory."*

---

## Core Concept

Go has two primitives for concurrency:
- **Goroutines** — lightweight concurrent functions (like threads, but much cheaper)
- **Channels** — typed conduits for sending values between goroutines

---

## 8.1 Goroutines

```go
// Start a goroutine with the "go" keyword
go f()           // f runs concurrently
go f(x, y, z)   // arguments evaluated NOW, f called later

// Main goroutine — when main returns, all goroutines are killed
func main() {
    go spinner(100 * time.Millisecond)  // runs concurrently
    const n = 45
    fibN := fib(n)                      // runs in main goroutine
    fmt.Printf("\rFibonacci(%d) = %d\n", n, fibN)
}

func spinner(delay time.Duration) {
    for {
        for _, r := range `-\|/` {
            fmt.Printf("\r%c", r)
            time.Sleep(delay)
        }
    }
}
```

```
Goroutine vs Thread:
  Thread: ~1-8 MB stack, OS managed, thousands possible
  Goroutine: ~2-8 KB stack (grows as needed), Go managed, MILLIONS possible
```

---

## 8.2 Channels

A channel is a **typed pipe** for communication:

```go
// Create a channel
ch := make(chan int)          // unbuffered
ch := make(chan int, 100)     // buffered (capacity 100)

// Send and receive
ch <- value    // send value (blocks until receiver is ready)
value = <-ch   // receive value (blocks until sender is ready)
<-ch           // receive and discard

// Close (sender closes, not receiver)
close(ch)

// Range over channel until closed
for v := range ch {
    fmt.Println(v)
}
```

```
Unbuffered channel synchronizes sender and receiver:
  Goroutine A: ch <- 1  ─────wait─────┐
                                       │ handshake
  Goroutine B:          x := <-ch ────┘
```

---

## 8.3 Pipeline Pattern

Chain goroutines with channels:

```go
func counter(out chan<- int) {
    for x := 0; ; x++ {
        out <- x
    }
}

func squarer(out chan<- int, in <-chan int) {
    for v := range in {
        out <- v * v
    }
    close(out)
}

func printer(in <-chan int) {
    for v := range in {
        fmt.Println(v)
    }
}

func main() {
    naturals := make(chan int)
    squares  := make(chan int)

    go counter(naturals)
    go squarer(squares, naturals)
    printer(squares)
}
```

```
naturals channel       squares channel
counter ──────────► squarer ──────────► printer
  0,1,2,3...          0,1,4,9...
```

---

## 8.4 Unidirectional Channel Types

```go
chan<- int   // send-only
<-chan int   // receive-only
chan int     // bidirectional (can convert to either)

func producer(out chan<- int) { out <- 42 }   // can only send
func consumer(in <-chan int)  { v := <-in }   // can only receive
```

---

## 8.5 Buffered Channels

```go
ch := make(chan string, 3)  // capacity 3

// Non-blocking sends until full
ch <- "A"  // ok
ch <- "B"  // ok
ch <- "C"  // ok
ch <- "D"  // BLOCKS — channel full

fmt.Println(<-ch)  // "A" — now there's room
```

---

## 8.6 Looping in Parallel

```go
// Make n goroutines, collect results via channel
func makeThumbnails(filenames []string) int64 {
    sizes := make(chan int64)
    var wg sync.WaitGroup
    for _, f := range filenames {
        wg.Add(1)
        go func(f string) {
            defer wg.Done()
            thumb, err := thumbnail.ImageFile(f)
            if err != nil {
                log.Println(err)
                return
            }
            info, _ := os.Stat(thumb)
            sizes <- info.Size()
        }(f)  // NOTE: pass f as argument to avoid capture bug!
    }
    go func() {
        wg.Wait()
        close(sizes)
    }()

    var total int64
    for size := range sizes {
        total += size
    }
    return total
}
```

---

## 8.7 Select

`select` is like `switch` but for channels — picks a ready case at random:

```go
select {
case <-ch1:
    // ch1 received something
case x := <-ch2:
    // ch2 received x
case ch3 <- y:
    // sent y to ch3
default:
    // no channel is ready — non-blocking
}

// Timeout pattern:
select {
case result := <-ch:
    fmt.Println(result)
case <-time.After(5 * time.Second):
    fmt.Println("timeout!")
}

// Cancellation with a done channel:
done := make(chan struct{})
// send cancel signal:
close(done)    // broadcast to ALL receivers at once

// each goroutine checks:
select {
case <-done:
    return  // cancelled
default:
    // keep working
}
```

---

## 8.8 Concurrent Web Crawler

```go
var tokens = make(chan struct{}, 20)  // limit concurrency to 20

func crawl(url string) []string {
    tokens <- struct{}{}   // acquire token
    list, err := links.Extract(url)
    <-tokens               // release token
    if err != nil { log.Print(err) }
    return list
}

func main() {
    worklist := make(chan []string)
    var n int
    n++
    go func() { worklist <- os.Args[1:] }()

    seen := make(map[string]bool)
    for ; n > 0; n-- {
        list := <-worklist
        for _, link := range list {
            if !seen[link] {
                seen[link] = true
                n++
                go func(link string) {
                    worklist <- crawl(link)
                }(link)
            }
        }
    }
}
```

---

## Visual Summary

```
GO CONCURRENCY MODEL (CSP)
═══════════════════════════════════════════════

Goroutine: go f()  — lightweight, millions possible

Channel: ch := make(chan T)
  ch <- value   send (blocks if unbuffered and no receiver)
  <-ch          receive (blocks if nothing to receive)
  close(ch)     signal no more values (sender closes)
  range ch      receive until closed

PATTERNS:
  Pipeline:     A ─ch1─► B ─ch2─► C
  Fan-out:      A ─► [B1, B2, B3] (multiple goroutines, one input)
  Fan-in:       [A1, A2, A3] ─► B (merge multiple channels)
  Done channel: close(done) broadcasts cancel to ALL goroutines

SELECT: like switch for channels — picks ready case (random if multiple)
  select { case <-ch: ... case <-done: return }

SEMAPHORE (limit concurrency):
  tokens := make(chan struct{}, 20)
  tokens <- struct{}{} // acquire
  <-tokens             // release
```

---

*← [Chapter 7 — Interfaces](07-interfaces.md) | [Back to Index](../README.md) | [Chapter 9 — Concurrency with Shared Variables](09-concurrency-with-shared-variables.md) →*
