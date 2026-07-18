# Chapter 1: Tutorial

> A hands-on tour of Go through real programs — from "Hello, World" to concurrent web servers.

---

## Core Concepts

1. **Packages & imports** — all Go code lives in packages
2. **`go run` vs `go build`** — run or compile
3. **`for` is the only loop** — three forms
4. **Maps** — built-in hash tables
5. **Goroutines & channels** — first taste of concurrency
6. **Interfaces** — `io.Writer` lets anything be a destination

---

## 1.1 Hello, World

```go
package main        // ← this is an executable program (not a library)

import "fmt"        // ← import the formatting package

func main() {
    fmt.Println("Hello, World")
}
```

**Run it:**
```bash
$ go run helloworld.go    # compile + run immediately
$ go build helloworld.go  # compile to binary
$ ./helloworld            # run the binary
```

**Key rules:**
- Every Go file starts with `package name`
- Unused imports = **compile error** (Go enforces cleanliness)
- Opening brace `{` must be on the **same line** as the declaration

---

## 1.2 Command-Line Arguments

`os.Args` is a **slice of strings**. `os.Args[0]` is the program name.

```go
package main

import (
    "fmt"
    "os"
)

func main() {
    // Version 1: traditional for loop
    var s, sep string
    for i := 1; i < len(os.Args); i++ {
        s += sep + os.Args[i]
        sep = " "
    }
    fmt.Println(s)
}
```

**Better with `range`:**
```go
func main() {
    s, sep := "", ""
    for _, arg := range os.Args[1:] {  // _ discards the index
        s += sep + arg
        sep = " "
    }
    fmt.Println(s)
}
```

**Even better:**
```go
func main() {
    fmt.Println(strings.Join(os.Args[1:], " "))
}
```

### The `for` Loop — Three Forms

```
┌─────────────────────────────────────────────────────────┐
│  Form 1: C-style                                        │
│  for init; condition; post { }                          │
│                                                         │
│  Form 2: while-style (no init/post)                     │
│  for condition { }                                      │
│                                                         │
│  Form 3: infinite loop                                  │
│  for { }                                                │
│                                                         │
│  Form 4: range over collection                          │
│  for i, v := range slice { }                            │
└─────────────────────────────────────────────────────────┘
```

---

## 1.3 Finding Duplicate Lines

Introduces **maps** and **`bufio.Scanner`**:

```go
func main() {
    counts := make(map[string]int)  // map: key=string, value=int
    input := bufio.NewScanner(os.Stdin)
    
    for input.Scan() {              // reads one line at a time
        counts[input.Text()]++      // increment count for that line
    }
    
    for line, n := range counts {
        if n > 1 {
            fmt.Printf("%d\t%s\n", n, line)
        }
    }
}
```

**Map rules:**
- Zero value of a missing key = `0` (for int maps) → `counts[line]++` works even on first sight
- `make(map[K]V)` creates an empty map
- Iteration order is **random by design** (forces robust programs)

### Printf Format Verbs
```
%d   decimal integer
%f   floating-point
%s   string
%q   quoted string "like this"
%v   any value (default format)
%T   type of value
%t   boolean
%%   literal percent sign
```

---

## 1.4 Animated GIFs (Lissajous Figures)

Introduces **constants**, **struct types**, and **composite literals**:

```go
const (
    cycles  = 5     // number of complete oscillator revolutions
    nframes = 64    // number of animation frames
    delay   = 8     // delay between frames (10ms units)
)

// Composite literal — creates a gif.GIF struct
anim := gif.GIF{LoopCount: nframes}

// Slice composite literal  
palette := []color.Color{color.White, color.Black}
```

**Visual output:**
```
    ╭──────╮
   ╱        ╲      Lissajous figure:
  │   ~~~~   │     parametric curve of two
  │  ~~~~~~  │     sine waves at different
   ╲        ╱     frequencies
    ╰──────╯
```

---

## 1.5 Fetching a URL

```go
func main() {
    for _, url := range os.Args[1:] {
        resp, err := http.Get(url)    // makes HTTP GET request
        if err != nil {
            fmt.Fprintf(os.Stderr, "fetch: %v\n", err)
            os.Exit(1)
        }
        b, err := ioutil.ReadAll(resp.Body)
        resp.Body.Close()             // always close the body!
        if err != nil {
            fmt.Fprintf(os.Stderr, "fetch: reading %s: %v\n", url, err)
            os.Exit(1)
        }
        fmt.Printf("%s", b)
    }
}
```

**Error handling pattern:**
```
call function
    ↓
check error first
    ↓ (if error)
handle error, return/exit
    ↓ (if no error)
continue happy path
```

---

## 1.6 Fetching URLs Concurrently ⚡

This is where Go shines — concurrency is built in:

```go
func main() {
    start := time.Now()
    ch := make(chan string)           // create a channel

    for _, url := range os.Args[1:] {
        go fetch(url, ch)             // start goroutine (go keyword!)
    }

    for range os.Args[1:] {
        fmt.Println(<-ch)             // receive from channel
    }
    fmt.Printf("%.2fs elapsed\n", time.Since(start).Seconds())
}

func fetch(url string, ch chan<- string) {
    start := time.Now()
    resp, err := http.Get(url)
    if err != nil {
        ch <- fmt.Sprint(err)         // send error to channel
        return
    }
    nbytes, err := io.Copy(ioutil.Discard, resp.Body)
    resp.Body.Close()
    secs := time.Since(start).Seconds()
    ch <- fmt.Sprintf("%.2fs %7d  %s", secs, nbytes, url)  // send result
}
```

**How goroutines + channels work:**
```
main goroutine
     │
     ├──► go fetch(url1, ch) ──────────────────╮
     │                                          │
     ├──► go fetch(url2, ch) ─────────────╮    │ all running
     │                                    │    │ simultaneously!
     ├──► go fetch(url3, ch) ─────────╮   │    │
     │                                │   │    │
     │    <-ch  <-ch  <-ch  ◄─────────┴───┴────╯
     │      ↑     ↑     ↑
     │    receives results as they arrive
```

**Result:** Total time = slowest fetch (not sum of all!)

---

## 1.7 A Web Server

```go
func main() {
    http.HandleFunc("/", handler)                          // route
    log.Fatal(http.ListenAndServe("localhost:8000", nil)) // start server
}

func handler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "URL.Path = %q\n", r.URL.Path)
}
```

**With a counter (introduces mutex for safety):**
```go
var mu sync.Mutex  // protects count from concurrent access
var count int

func handler(w http.ResponseWriter, r *http.Request) {
    mu.Lock()
    count++
    mu.Unlock()
    fmt.Fprintf(w, "URL.Path = %q\n", r.URL.Path)
}
```

---

## 1.8 Loose Ends

### Switch Statement
```go
switch coinflip() {
case "heads":
    heads++
case "tails":
    tails++
default:
    fmt.Println("landed on edge!")
}
// No fallthrough by default (unlike C)!
```

### Tagless switch (like if-else chain)
```go
func Signum(x int) int {
    switch {
    case x > 0:  return +1
    default:     return 0
    case x < 0:  return -1
    }
}
```

---

## Summary

```
Go Program = packages + declarations + statements
                │
                ├── package main → executable
                ├── func main() → entry point
                ├── import → declare dependencies (unused = error)
                └── formatting with gofmt (always!)
```

**The five programs you built in this chapter:**
1. `echo` — process command-line args
2. `dup` — find duplicate lines (maps!)
3. `lissajous` — generate animated GIFs
4. `fetch` — HTTP client
5. `fetchall` — concurrent HTTP (goroutines + channels)
6. `server` — HTTP server
