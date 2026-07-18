# Chapter 5: Functions

> *"A function lets us wrap up a sequence of statements as a unit that can be called from elsewhere in a program, perhaps multiple times."*

---

## Core Concept

Functions are **first-class values** in Go — they can be stored in variables, passed as arguments, and returned from other functions. This chapter also introduces Go's unique error handling pattern and the `defer`, `panic`, and `recover` mechanism.

---

## 5.1 Function Declarations

```
func name(parameter-list) (result-list) {
    body
}
```

```go
func hypot(x, y float64) float64 {
    return math.Sqrt(x*x + y*y)
}

// Multiple parameters of same type can be grouped
func add(x, y int) int { return x + y }

// Named results — declares local variables initialized to zero
func divide(a, b float64) (result float64, err error) {
    if b == 0 {
        err = errors.New("division by zero")
        return  // bare return — returns named variables
    }
    result = a / b
    return
}
```

**Key rule:** Arguments are **passed by value** — functions receive a copy. To modify the caller's variable, pass a pointer.

---

## 5.2 Recursion

Go uses **variable-size stacks** that grow as needed (up to ~1GB). No stack overflow worries like in C.

```go
// Classic recursive tree traversal
func visit(links []string, n *html.Node) []string {
    if n.Type == html.ElementNode && n.Data == "a" {
        for _, a := range n.Attr {
            if a.Key == "href" {
                links = append(links, a.Val)
            }
        }
    }
    for c := n.FirstChild; c != nil; c = c.NextSibling {
        links = visit(links, c)  // recurse into children
    }
    return links
}
```

---

## 5.3 Multiple Return Values

Go functions can return multiple values — the idiomatic way to handle errors:

```go
func findLinks(url string) ([]string, error) {
    resp, err := http.Get(url)
    if err != nil {
        return nil, err  // propagate error
    }
    defer resp.Body.Close()
    // ...
    return links, nil
}

// Caller must handle both values
links, err := findLinks("https://golang.org")
if err != nil {
    log.Fatal(err)
}
```

**Bare returns** — when results are named, `return` without values returns them all:

```go
func minMax(s []int) (min, max int) {
    min, max = s[0], s[0]
    for _, v := range s[1:] {
        if v < min { min = v }
        if v > max { max = v }
    }
    return  // returns min and max
}
```

> 💡 Use bare returns sparingly — they reduce clarity in long functions.

---

## 5.4 Errors

Go's approach: **errors are values**, not exceptions.

```go
// The error interface
type error interface {
    Error() string
}
```

### 5 Strategies for Error Handling

```
1. PROPAGATE      → return nil, err
2. RETRY          → retry with backoff
3. PRINT AND STOP → log.Fatalf(...)
4. LOG AND CONTINUE → log.Printf(...)
5. IGNORE         → _ = riskyOperation()
```

```go
// Strategy 1: Propagate with context
doc, err := html.Parse(resp.Body)
if err != nil {
    return nil, fmt.Errorf("parsing %s as HTML: %v", url, err)
}

// Strategy 2: Retry with backoff
func WaitForServer(url string) error {
    const timeout = 1 * time.Minute
    deadline := time.Now().Add(timeout)
    for tries := 0; time.Now().Before(deadline); tries++ {
        _, err := http.Head(url)
        if err == nil {
            return nil // success
        }
        time.Sleep(time.Second << uint(tries)) // exponential back-off
    }
    return fmt.Errorf("server %s failed to respond", url)
}

// End of File — a special sentinel error
for {
    r, _, err := in.ReadRune()
    if err == io.EOF {
        break
    }
    if err != nil {
        return fmt.Errorf("read failed: %v", err)
    }
}
```

**Error message style:**
- Lowercase, no punctuation at end
- Chain context: `"genesis: crashed: no parachute: G-switch failed"`

---

## 5.5 Function Values

Functions are first-class — assignable to variables, passable as arguments:

```go
func square(n int) int { return n * n }
func negative(n int) int { return -n }

f := square
fmt.Println(f(3))  // "9"
f = negative
fmt.Println(f(3))  // "-3"

// Zero value of function type is nil
var f func(int) int
f(3)  // panic: call of nil function
```

```go
// Higher-order functions
strings.Map(func(r rune) rune { return r + 1 }, "HAL-9000")
// Returns "IBM.:111"
```

---

## 5.6 Anonymous Functions & Closures

```go
// Anonymous function defined at point of use
add1 := func(r rune) rune { return r + 1 }

// Closure: inner function captures outer variable
func squares() func() int {
    var x int
    return func() int {
        x++
        return x * x
    }
}

f := squares()
fmt.Println(f()) // 1
fmt.Println(f()) // 4
fmt.Println(f()) // 9
fmt.Println(f()) // 16
// x persists between calls — it's captured by reference
```

```
┌─────────────────────────────────────┐
│  squares()                          │
│   ┌──────────┐                      │
│   │  var x   │ ← captured by        │
│   └──────────┘   the anonymous func │
│   return func() int {               │
│       x++                           │
│       return x * x                  │
│   }                                 │
└─────────────────────────────────────┘
```

### ⚠️ Caveat: Capturing Iteration Variables

```go
// WRONG: all rmdirs will remove the same directory!
var rmdirs []func()
for _, dir := range tempDirs() {
    os.MkdirAll(dir, 0755)
    rmdirs = append(rmdirs, func() {
        os.RemoveAll(dir) // captures the variable, not the value
    })
}

// CORRECT: create new variable per iteration
for _, dir := range tempDirs() {
    dir := dir  // new local variable
    os.MkdirAll(dir, 0755)
    rmdirs = append(rmdirs, func() {
        os.RemoveAll(dir) // captures the new local
    })
}
```

**Why?** The loop variable `dir` is shared across all iterations. All closures capture the same `dir`, which ends up being the last value after the loop finishes.

---

## 5.7 Variadic Functions

```go
func sum(vals ...int) int {
    total := 0
    for _, val := range vals {
        total += val
    }
    return total
}

fmt.Println(sum())          // "0"
fmt.Println(sum(3))         // "3"
fmt.Println(sum(1, 2, 3, 4)) // "10"

// Spread a slice into a variadic function
values := []int{1, 2, 3, 4}
fmt.Println(sum(values...)) // "10"
```

---

## 5.8 Deferred Function Calls

`defer` schedules a function call to run **when the surrounding function returns**, in **reverse order** of their declaration.

```go
// Without defer — easy to forget closing
func title(url string) error {
    resp, err := http.Get(url)
    if err != nil { return err }
    
    // Must close in every return path — error-prone!
    ct := resp.Header.Get("Content-Type")
    if ct != "text/html" {
        resp.Body.Close()  // must remember here
        return fmt.Errorf(...)
    }
    doc, err := html.Parse(resp.Body)
    resp.Body.Close()      // and here
    // ...
}

// With defer — clean and correct
func title(url string) error {
    resp, err := http.Get(url)
    if err != nil { return err }
    defer resp.Body.Close()  // always runs, no matter what
    // ...
}
```

### Defer for Tracing

```go
func bigSlowOperation() {
    defer trace("bigSlowOperation")() // note the extra ()
    time.Sleep(10 * time.Second)
}

func trace(msg string) func() {
    start := time.Now()
    log.Printf("enter %s", msg)
    return func() { log.Printf("exit %s (%s)", msg, time.Since(start)) }
}
// Output:
// enter bigSlowOperation
// exit bigSlowOperation (10.000589217s)
```

### Defer with Named Return Values

```go
func double(x int) (result int) {
    defer func() {
        fmt.Printf("double(%d) = %d\n", x, result)
    }()
    return x + x
}
// The deferred func can READ the named result
```

---

## 5.9 Panic

`panic` stops normal execution, runs deferred functions, and crashes the program with a stack trace.

```go
// Runtime panic
var s []int
_ = s[10] // panic: index out of range

// Manual panic — for impossible situations / bugs
switch s := suit(drawCard()); s {
case "Spades", "Hearts", "Diamonds", "Clubs":
    // ...
default:
    panic(fmt.Sprintf("invalid suit %q", s)) // should never happen
}

// MustCompile pattern — panics if regex is bad (used in init)
var httpRE = regexp.MustCompile(`^https?:`)
```

```
Panic execution flow:
─────────────────────
panic() called
    │
    ▼
Normal execution STOPS
    │
    ▼
All deferred functions run (in reverse order)
    │
    ▼
Program crashes with stack trace
```

---

## 5.10 Recover

`recover` catches a panic and returns its value — only useful inside `defer`.

```go
func Parse(input string) (s *Syntax, err error) {
    defer func() {
        if p := recover(); p != nil {
            err = fmt.Errorf("internal error: %v", p)
        }
    }()
    // parser code that might panic...
}
```

**Rule:** Only recover from panics **you intended** to be recoverable:

```go
func soleTitle(doc *html.Node) (title string, err error) {
    type bailout struct{} // unexported sentinel type
    
    defer func() {
        switch p := recover(); p {
        case nil:
            // no panic — ok
        case bailout{}:
            err = fmt.Errorf("multiple title elements")
        default:
            panic(p) // unexpected panic — re-panic!
        }
    }()
    
    // Search for title, panic(bailout{}) if multiple found
    forEachNode(doc, func(n *html.Node) {
        if n.Type == html.ElementNode && n.Data == "title" {
            if title != "" {
                panic(bailout{})
            }
            title = n.FirstChild.Data
        }
    }, nil)
    return title, nil
}
```

---

## Visual Summary

```
FUNCTIONS IN GO
════════════════════════════════════════════════

Declaration:      func name(params) (results) { body }
Multiple returns: func f() (int, error)
Variadic:         func f(vals ...int)
Anonymous:        func(x int) int { return x }
First-class:      f := someFunc; f(42)

DEFER: runs when function returns (reverse order)
├── cleanup: defer file.Close()
├── unlock:  defer mu.Unlock()
└── trace:   defer trace("fn")()

PANIC → crashes program (use for bugs)
RECOVER → catches panic (use with care)

ERROR HANDLING IDIOM:
if err != nil {
    return nil, fmt.Errorf("context: %v", err)
}
```
