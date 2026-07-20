# Chapter 7: Interfaces

> *"Interface types express generalizations or abstractions about the behaviors of other types."*

---

## Core Concept

Go interfaces are **implicit** — a type satisfies an interface simply by having the required methods. No `implements` keyword needed. This makes Go interfaces uniquely flexible: you can define new interfaces for existing types you don't control.

---

## 7.1 Interfaces as Contracts

```go
// io.Writer is a contract: "I can write bytes"
package io
type Writer interface {
    Write(p []byte) (n int, err error)
}

// fmt.Fprintf only depends on the Write method — not the concrete type
func Fprintf(w io.Writer, format string, args ...interface{}) (int, error)

// Works with ANY type that has Write:
fmt.Fprintf(os.Stdout, "hello")          // *os.File
fmt.Fprintf(&buf, "hello")              // *bytes.Buffer
fmt.Fprintf(myCustomWriter, "hello")    // your own type
```

```
Interface as envelope:

┌─────────────────────────┐
│  io.Writer              │
│  ┌───────────────────┐  │
│  │ dynamic type:     │  │
│  │   *os.File        │  │
│  │ dynamic value:    │  │
│  │   os.Stdout ptr   │  │
│  └───────────────────┘  │
│  (only Write is visible)│
└─────────────────────────┘
```

---

## 7.2 Interface Types

```go
// Single method
type Writer interface { Write(p []byte) (n int, err error) }
type Reader interface { Read(p []byte) (n int, err error) }
type Closer interface { Close() error }

// Combining interfaces via embedding
type ReadWriter interface {
    Reader
    Writer
}
type ReadWriteCloser interface {
    Reader
    Writer
    Closer
}

// The empty interface — satisfied by ALL types
var any interface{}
any = 42
any = "hello"
any = []int{1, 2, 3}
```

---

## 7.3 Interface Satisfaction

A type satisfies an interface if it has **all the required methods**:

```go
// *os.File satisfies: Reader, Writer, Closer, ReadWriter, ReadWriteCloser
// *bytes.Buffer satisfies: Reader, Writer, ReadWriter (but NOT Closer)

var w io.Writer
w = os.Stdout             // OK: *os.File has Write
w = new(bytes.Buffer)     // OK: *bytes.Buffer has Write
w = time.Second           // COMPILE ERROR: time.Duration lacks Write

// Pointer vs value receivers matter!
type IntSet struct{ words []uint64 }
func (*IntSet) String() string { ... }  // pointer receiver

var s IntSet
var _ fmt.Stringer = &s  // OK: *IntSet has String
var _ fmt.Stringer = s   // COMPILE ERROR: IntSet lacks String
```

---

## 7.4 Interface Values

An interface value has **two components**: dynamic type + dynamic value.

```go
var w io.Writer          // nil interface: type=nil, value=nil

w = os.Stdout            // type=*os.File,      value=&os.Stdout
w = new(bytes.Buffer)    // type=*bytes.Buffer, value=&buffer
w = nil                  // back to nil
```

```
nil interface:           Non-nil interface:
┌──────────┐             ┌──────────────────┐
│ type=nil │             │ type=*os.File     │
│value=nil │             │ value=0x4b3f20... │ → (os.Stdout)
└──────────┘             └──────────────────┘
```

**Two interface values are equal if:**
- Both are nil, OR
- Both have identical dynamic type AND equal dynamic values

### ⚠️ Critical Trap: Non-nil Interface Containing Nil Pointer

```go
var buf *bytes.Buffer  // nil pointer
var out io.Writer = buf  // NON-nil interface! (type=*bytes.Buffer, value=nil)

if out != nil {
    out.Write(...)  // PANICS! Method called on nil *bytes.Buffer
}

// FIX: use the interface type directly
var out io.Writer
if debug {
    out = new(bytes.Buffer)
}
```

---

## 7.5 Sorting with sort.Interface

```go
package sort

type Interface interface {
    Len() int
    Less(i, j int) bool  // i < j means element i should come before j
    Swap(i, j int)
}

// Make any slice sortable:
type StringSlice []string
func (s StringSlice) Len() int           { return len(s) }
func (s StringSlice) Less(i, j int) bool { return s[i] < s[j] }
func (s StringSlice) Swap(i, j int)      { s[i], s[j] = s[j], s[i] }

sort.Sort(StringSlice(names))
// or simply:
sort.Strings(names)

// Custom sort by multiple fields using sort.Slice:
sort.Slice(tracks, func(i, j int) bool {
    if tracks[i].Title != tracks[j].Title {
        return tracks[i].Title < tracks[j].Title
    }
    return tracks[i].Year < tracks[j].Year
})
```

---

## 7.6 The http.Handler Interface

```go
package http
type Handler interface {
    ServeHTTP(w ResponseWriter, r *Request)
}

// Any type with ServeHTTP can be a web handler
type database map[string]dollars
func (db database) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    switch r.URL.Path {
    case "/list":
        for item, price := range db {
            fmt.Fprintf(w, "%s: %s\n", item, price)
        }
    case "/price":
        // ...
    }
}

// http.HandlerFunc adapts a plain function to be a Handler
http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "URL.Path = %q\n", r.URL.Path)
})
```

---

## 7.7 The error Interface

```go
// Built into Go — the error interface:
type error interface {
    Error() string
}

// Creating errors:
errors.New("EOF")
fmt.Errorf("parsing %s: %v", url, err)

// Custom error types carry more information:
type PathError struct {
    Op   string
    Path string
    Err  error
}
func (e *PathError) Error() string {
    return e.Op + " " + e.Path + ": " + e.Err.Error()
}
```

---

## 7.8 Type Assertions

Extract the concrete value from an interface:

```go
var w io.Writer = os.Stdout

// Assertion to concrete type — panics if wrong
f := w.(*os.File)     // success: f is *os.File
b := w.(*bytes.Buffer) // PANIC: holds *os.File, not *bytes.Buffer

// Safe assertion — returns (value, bool)
f, ok := w.(*os.File)      // ok=true
b, ok := w.(*bytes.Buffer) // ok=false, b=nil

// Assertion to interface type
rw, ok := w.(io.ReadWriter) // ok=true if w has Read+Write
```

---

## 7.9 Type Switches

Distinguish between multiple possible types:

```go
func describe(i interface{}) {
    switch v := i.(type) {
    case int:
        fmt.Printf("int: %d\n", v)
    case string:
        fmt.Printf("string: %q\n", v)
    case bool:
        fmt.Printf("bool: %t\n", v)
    default:
        fmt.Printf("other: %T\n", v)
    }
}

// Discriminating errors:
if pe, ok := err.(*os.PathError); ok {
    fmt.Println(pe.Path)
}
```

---

## Visual Summary

```
GO INTERFACES
═══════════════════════════════════════════════

IMPLICIT: No "implements" keyword — just have the methods

Interface value = dynamic type + dynamic value
  nil interface  → type=nil, value=nil
  non-nil        → type=*ConcreteType, value=pointer/value

SATISFACTION:
  *os.File → io.Reader, io.Writer, io.Closer
  *bytes.Buffer → io.Reader, io.Writer (not Closer)

KEY INTERFACES:
  io.Writer    → Write([]byte) (int, error)
  io.Reader    → Read([]byte) (int, error)
  fmt.Stringer → String() string
  error        → Error() string
  sort.Interface → Len, Less, Swap

TYPE ASSERTION:  v, ok := x.(T)
TYPE SWITCH:     switch v := x.(type) { case T: ... }

⚠️ TRAP: nil *T stored in interface ≠ nil interface
```

---

*← [Chapter 6 — Methods](06-methods.md) | [Back to Index](../README.md) | [Chapter 8 — Goroutines and Channels](08-goroutines-and-channels.md) →*
