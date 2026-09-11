# 🟢 Go — Junior Interview Questions

---

## 1. What is Go and what are its main features?

**Q:** What is Go? What makes it different from other languages?

**A:** Go (Golang) is a statically typed, compiled language created at Google. Key features:
- **Fast compilation** — builds in seconds
- **Garbage collected** — no manual memory management
- **Built-in concurrency** — goroutines and channels as first-class citizens
- **Simple syntax** — minimal keywords, no inheritance, no generics (until 1.18)
- **Strong standard library** — HTTP, JSON, testing, crypto all built in
- **Single binary output** — no runtime dependency

---

## 2. What is the difference between `var` and `:=`?

**Q:** When do you use `var x int` vs `x := 5`?

**A:**
- `var` is a full declaration — can be used at package or function scope, and you can declare without initializing
- `:=` is short variable declaration — only inside functions, infers type from the right-hand side

```go
var x int       // zero value (0)
var y = 10      // type inferred, initialized
z := "hello"    // shorthand, function scope only
```

---

## 3. What are Go's basic data types?

**A:**
- **Integers:** `int`, `int8`, `int16`, `int32`, `int64`, `uint`, `uint8`...
- **Floats:** `float32`, `float64`
- **Complex:** `complex64`, `complex128`
- **Boolean:** `bool`
- **String:** `string` (immutable, UTF-8)
- **Byte:** `byte` (alias for `uint8`)
- **Rune:** `rune` (alias for `int32`, represents a Unicode code point)

---

## 4. What is the zero value in Go?

**Q:** What happens when you declare a variable without initializing it?

**A:** Go assigns a **zero value** based on the type:
- `int`, `float64` → `0`
- `bool` → `false`
- `string` → `""`
- pointers, slices, maps, channels, functions → `nil`
- structs → zero value of each field

```go
var i int     // 0
var s string  // ""
var b bool    // false
var p *int    // nil
```

---

## 5. What is the difference between an array and a slice?

**A:**

| | Array | Slice |
|--|-------|-------|
| Size | Fixed at compile time | Dynamic |
| Type | `[3]int` | `[]int` |
| Value type | Yes — copied on assignment | No — reference to underlying array |
| Common use | Rarely used directly | Used almost everywhere |

```go
arr := [3]int{1, 2, 3}   // array
sl := []int{1, 2, 3}      // slice
sl = append(sl, 4)         // can grow
```

---

## 6. How do maps work in Go?

**Q:** How do you create and use maps? How do you check if a key exists?

**A:**
```go
// Create
m := map[string]int{"a": 1, "b": 2}
m := make(map[string]int)

// Set / Get
m["key"] = 42
val := m["key"]

// Check existence — always use the two-value form
val, ok := m["key"]
if !ok {
    // key doesn't exist
}

// Delete
delete(m, "key")
```

Maps are **not safe for concurrent use** — use `sync.Map` or a mutex for concurrent access.

---

## 7. What is a struct?

**A:** A struct is a composite type grouping named fields:

```go
type Person struct {
    Name string
    Age  int
}

p := Person{Name: "Alice", Age: 30}
fmt.Println(p.Name) // Alice
```

Structs are **value types** — assignment copies all fields.

---

## 8. How does error handling work in Go?

**Q:** Go doesn't have exceptions. How are errors handled?

**A:** Functions return an `error` as the last return value. Callers check it explicitly:

```go
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

result, err := divide(10, 0)
if err != nil {
    log.Fatal(err)
}
```

This makes error paths explicit and visible in code.

---

## 9. What is `defer`?

**Q:** What does `defer` do and when is it executed?

**A:** `defer` schedules a function call to run when the surrounding function returns — regardless of how it returns (normal, panic, return with value). Deferred calls are executed in **LIFO order**.

```go
func readFile(path string) error {
    f, err := os.Open(path)
    if err != nil {
        return err
    }
    defer f.Close() // runs when readFile returns

    // ... read from f
    return nil
}
```

Common uses: closing resources, unlocking mutexes, logging.

---

## 10. What is an interface in Go?

**A:** An interface defines a set of method signatures. Any type that implements those methods **implicitly** satisfies the interface — no `implements` keyword needed.

```go
type Animal interface {
    Sound() string
}

type Dog struct{}
func (d Dog) Sound() string { return "Woof" }

type Cat struct{}
func (c Cat) Sound() string { return "Meow" }

func makeSound(a Animal) {
    fmt.Println(a.Sound())
}

makeSound(Dog{}) // Woof
makeSound(Cat{}) // Meow
```

---

## 11. What is a goroutine?

**Q:** What is a goroutine and how do you start one?

**A:** A goroutine is a lightweight thread managed by the Go runtime. Start one with the `go` keyword:

```go
go func() {
    fmt.Println("running concurrently")
}()
```

Goroutines are much cheaper than OS threads — you can have millions of them. The Go scheduler multiplexes them onto OS threads.

---

## 12. What is a channel?

**Q:** What are channels used for?

**A:** Channels are typed conduits for communication between goroutines:

```go
ch := make(chan int)

go func() {
    ch <- 42 // send
}()

val := <-ch // receive
fmt.Println(val) // 42
```

Channels enable goroutines to synchronize without shared memory — **"Don't communicate by sharing memory; share memory by communicating."**

---

## 13. What is `fmt.Println` vs `fmt.Printf`?

**A:**
- `fmt.Println` — prints values with spaces between them and a newline at the end
- `fmt.Printf` — formatted output using verbs (`%s`, `%d`, `%v`, `%+v`, `%T`, etc.)
- `fmt.Sprintf` — same as Printf but returns a string instead of printing

```go
fmt.Println("Hello", 42)       // Hello 42
fmt.Printf("Name: %s\n", "Al") // Name: Al
s := fmt.Sprintf("%d + %d", 1, 2) // "1 + 2"
```

---

## 14. How do you loop in Go?

**A:** Go has only one loop keyword — `for` — but it covers all cases:

```go
// Classic
for i := 0; i < 5; i++ { }

// While-style
for x < 10 { x++ }

// Infinite
for { }

// Range over slice
for i, v := range slice { }

// Range over map
for k, v := range m { }
```

---

## 15. What is a pointer in Go?

**A:** A pointer holds the memory address of a value. Use `&` to get the address, `*` to dereference:

```go
x := 42
p := &x    // p is *int, holds address of x
*p = 100   // modifies x through the pointer
fmt.Println(x) // 100
```

Pointers are used to avoid copying large structs and to allow mutation through function parameters.

---

## 16. What are multiple return values and how are they used?

**A:** Go functions can return multiple values — this is idiomatic, especially for returning a result + error:

```go
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

result, err := divide(10, 2)
```

You can also ignore a return value with the blank identifier `_`:
```go
result, _ := divide(10, 2) // ignore error (only when truly safe)
```

---

## 17. What are named return values?

**A:** You can name return values in the function signature — they act as pre-declared variables and enable a "naked return":

```go
func minMax(arr []int) (min, max int) {
    min, max = arr[0], arr[0]
    for _, v := range arr[1:] {
        if v < min { min = v }
        if v > max { max = v }
    }
    return // naked return — returns min and max
}
```

**Use sparingly:** Named returns help document what values mean; naked returns in long functions hurt readability.

---

## 18. What is `iota` and how do you use it in const blocks?

**A:** `iota` is a predeclared identifier that resets to 0 at each `const` block and increments by 1 for each spec:

```go
type Direction int

const (
    North Direction = iota // 0
    East                   // 1
    South                  // 2
    West                   // 3
)

// Bit flags
const (
    Read    = 1 << iota // 1
    Write               // 2
    Execute             // 4
)
```

---

## 19. What is a type assertion and a type switch?

**A:**

**Type assertion** — extract the concrete type from an interface:
```go
var i interface{} = "hello"

s, ok := i.(string) // safe assertion
if !ok {
    fmt.Println("not a string")
}
```

**Type switch** — branch on the concrete type:
```go
func describe(i interface{}) {
    switch v := i.(type) {
    case int:
        fmt.Printf("int: %d
", v)
    case string:
        fmt.Printf("string: %s
", v)
    default:
        fmt.Printf("unknown: %T
", v)
    }
}
```

---

## 20. What is the `init()` function?

**A:** `init` is a special function that runs automatically before `main`, after all variable initializations:

```go
var config Config

func init() {
    config = loadConfig("config.yaml")
}
```

- Multiple `init` functions can exist in a package (even in the same file)
- They run in the order they appear, files alphabetically
- Cannot be called explicitly
- Common uses: register drivers (`database/sql`), initialize package-level state

---

## 21. What is the blank identifier `_`?

**A:** `_` discards a value you don't need:

```go
// Ignore second return value
val, _ := strconv.Atoi("42")

// Ignore loop index
for _, v := range slice { fmt.Println(v) }

// Compile-time interface check (no runtime cost)
var _ Animal = (*Dog)(nil) // fails to compile if Dog doesn't implement Animal

// Import for side effects only
import _ "github.com/lib/pq" // registers postgres driver
```

---

## 22. How do you convert between strings, `[]byte`, and `[]rune`?

**A:**
```go
s := "hello, 世界"

// string → []byte (raw UTF-8 bytes)
b := []byte(s)

// []byte → string
s2 := string(b)

// string → []rune (Unicode code points)
r := []rune(s)
fmt.Println(len(s))  // 13 (bytes)
fmt.Println(len(r))  // 9 (runes/characters)

// Iterate characters correctly
for i, ch := range s {
    fmt.Printf("%d: %c
", i, ch) // ch is a rune
}
```

---

## 23. What is `fmt.Stringer` and why implement it?

**A:** `fmt.Stringer` is an interface with a single method `String() string`. Implement it to control how your type prints:

```go
type Point struct{ X, Y int }

func (p Point) String() string {
    return fmt.Sprintf("(%d, %d)", p.X, p.Y)
}

p := Point{3, 4}
fmt.Println(p)        // (3, 4)
fmt.Printf("%v
", p) // (3, 4)
```

---

## 24. How does error wrapping work with `fmt.Errorf` and `%w`?

**A:** `%w` wraps an error, preserving the original for inspection with `errors.Is` and `errors.As`:

```go
func openConfig(path string) error {
    _, err := os.Open(path)
    if err != nil {
        return fmt.Errorf("openConfig: %w", err) // wrap with context
    }
    return nil
}

err := openConfig("missing.yaml")
errors.Is(err, os.ErrNotExist) // true — unwraps chain
```

---

## 25. What is the `any` type?

**A:** `any` is an alias for `interface{}` introduced in Go 1.18 — use it for values of unknown type:

```go
var v any = 42
v = "now a string"
v = []int{1, 2, 3}

// You need a type assertion to use the underlying value
if s, ok := v.(string); ok {
    fmt.Println(s)
}
```

Avoid overusing `any` — it bypasses type safety. Prefer generics or concrete types where possible.

---

## 26. What is the difference between `make` for slices with length vs capacity?

**A:**
```go
s1 := make([]int, 5)     // len=5, cap=5 — 5 zero elements
s2 := make([]int, 0, 5)  // len=0, cap=5 — empty, preallocated

// s1 already has 5 elements
fmt.Println(s1) // [0 0 0 0 0]

// s2 is empty but won't reallocate until 6th append
s2 = append(s2, 1, 2, 3) // len=3, cap=5 — no reallocation
```

Preallocate with known capacity to avoid repeated backing-array copies during appending.

---

## 27. What happens when you pass a slice to a function?

**A:** The slice header (pointer, len, cap) is copied, but the underlying array is shared:

```go
func double(s []int) {
    for i := range s {
        s[i] *= 2 // modifies original array
    }
}

nums := []int{1, 2, 3}
double(nums)
fmt.Println(nums) // [2 4 6] — mutated!
```

But `append` inside a function doesn't affect the caller's slice if it causes reallocation:
```go
func addItem(s []int) []int {
    return append(s, 99) // may or may not affect original — always return
}
```

---

## 28. What is a variadic function and how do you pass a slice to one?

**A:**
```go
func sum(nums ...int) int {
    total := 0
    for _, n := range nums { total += n }
    return total
}

sum(1, 2, 3)           // pass individual values
s := []int{1, 2, 3}
sum(s...)              // unpack slice with ...
```

---

## 29. What is short-circuit evaluation in Go?

**A:** `&&` and `||` short-circuit — the right operand is only evaluated if necessary:

```go
if user != nil && user.IsActive() { // IsActive only called if user != nil
    // safe
}

if cached || expensiveLookup() { // expensiveLookup skipped if cached is true
    // ...
}
```

---

## 30. How do you format and lint Go code?

**A:**
```bash
gofmt -w .           # format code (built-in)
goimports -w .       # format + organize imports
go vet ./...         # report suspicious constructs
staticcheck ./...    # advanced static analysis
golangci-lint run    # meta-linter (runs many linters at once)
```

`gofmt` is non-negotiable — the entire Go community uses it. CI pipelines typically reject unformatted code.
