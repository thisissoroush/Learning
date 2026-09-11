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
