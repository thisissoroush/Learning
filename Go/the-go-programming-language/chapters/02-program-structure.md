# Chapter 2: Program Structure

> How Go programs are organized — names, variables, types, packages, and scope.

---

## Core Concepts

1. **25 keywords** — Go is deliberately small
2. **Zero values** — every variable always has a value
3. **Short variable declaration `:=`** — the workhorse inside functions
4. **Pointers** — explicit addresses, no pointer arithmetic
5. **Packages** — the unit of modularity and encapsulation
6. **Scope** — lexical scoping with shadowing pitfalls

---

## 2.1 Names

Go names follow one rule: **case determines visibility**.

```
Uppercase first letter → Exported (visible outside package)  → fmt.Println
Lowercase first letter → Unexported (package-private)        → internal helper
```

**25 keywords (can't be used as names):**
```
break    default     func    interface  select
case     defer       go      map        struct
chan     else        goto    package    switch
const    fallthrough if      range      type
continue for        import  return     var
```

**Style:** Go uses `camelCase` not `snake_case`. Acronyms stay uppercase: `HTMLParser`, `parseURL`.

---

## 2.2 Declarations

Four kinds: `var`, `const`, `type`, `func`

```go
package main

import "fmt"

const boilingF = 212.0   // package-level constant

func main() {
    var f = boilingF      // local variable
    var c = (f - 32) * 5 / 9
    fmt.Printf("boiling = %g°F or %g°C\n", f, c)
}
```

**Scope:** Package-level names visible across all files. Local names visible only in their function.

---

## 2.3 Variables

### Four ways to declare a variable (all equivalent for strings):
```go
s := ""              // short declaration (only inside functions)
var s string         // zero value = ""
var s = ""           // with initializer
var s string = ""    // explicit type + initializer
```

**Zero values (never uninitialized in Go!):**
```
int, float     → 0
bool           → false
string         → ""
pointer        → nil
slice, map     → nil
interface      → nil
```

### Short Variable Declaration `:=`
```go
// Inside functions only:
x := 10             // declares AND initializes
a, b := 1, "hello"  // multiple at once

// := requires at least ONE new variable on the left:
in, err  := os.Open(infile)   // both new ✓
out, err := os.Create(outfile) // err already exists, but out is new ✓
f, err   := os.Open(infile)
f, err   := os.Create(outfile) // ERROR: no new variables!
```

### Pointers
```go
x := 1
p := &x         // p is *int — "address of x"
fmt.Println(*p) // "1" — dereference p
*p = 2          // set x to 2 via pointer
fmt.Println(x)  // "2"
```

**Pointer diagram:**
```
 x:  [  1  ]  ← memory address: 0xc000012050
 p:  [ 0xc000012050 ]   ← p holds address of x
      *p = contents at that address = 1
```

**Safe to return pointer to local variable:**
```go
func f() *int {
    v := 1      // v lives on heap (Go figures this out)
    return &v   // safe! v outlives f()
}
```

### The `new` Function
```go
p := new(int)   // allocates unnamed int, returns *int
*p = 42
// Equivalent to:
var x int
p := &x
```

---

## 2.4 Assignments

```go
x = 1           // simple
*p = true       // indirect (via pointer)
person.name = "bob"  // struct field
count[x] *= scale    // compound assignment

// Tuple assignment (right side evaluated first):
x, y = y, x    // swap!
a[i], a[j] = a[j], a[i]  // swap array elements

// GCD using tuple assignment:
func gcd(x, y int) int {
    for y != 0 {
        x, y = y, x%y
    }
    return x
}
```

---

## 2.5 Type Declarations

Create a **new named type** from an existing type:

```go
type Celsius    float64
type Fahrenheit float64

// Now they're DIFFERENT types — can't mix them!
var c Celsius   = 100
var f Fahrenheit = 212

// c + f  ← COMPILE ERROR: type mismatch

// Must convert explicitly:
Celsius(f)      // convert f to Celsius type (doesn't change value)
FToC(f)         // this DOES convert between scales
```

**Why?** Prevents accidentally adding meters to kilograms.

**Types can have methods:**
```go
func (c Celsius) String() string {
    return fmt.Sprintf("%g°C", c)
}
// Now: fmt.Println(c) prints "100°C" automatically
```

---

## 2.6 Packages and Files

```
Package = modularity + encapsulation + separate compilation
         ↑
         A package = one or more .go files in the same directory
```

**Import path vs package name:**
```go
import "gopl.io/ch2/tempconv"   // import PATH (directory path)
// package name is "tempconv"   // used as: tempconv.CToF(...)
```

**Package initialization order:**
```
1. Package-level variables initialized (dependencies first)
2. init() functions run (in declaration order)
3. main() starts
```

```go
var pc [256]byte

func init() {             // init() runs automatically at startup
    for i := range pc {
        pc[i] = pc[i/2] + byte(i&1)  // precompute lookup table
    }
}
```

---

## 2.7 Scope

**Lexical scope** — where a name is visible in source code.

```
Universe block  →  built-ins (int, true, len, make...)
Package block   →  package-level declarations
File block      →  imported packages
Function block  →  local variables
Inner blocks    →  if/for/switch bodies
```

**Shadowing (dangerous!):**
```go
x := "hello!"
for i := 0; i < len(x); i++ {
    x := x[i]         // NEW x shadows outer x
    if x != '!' {
        x := x + 'A' - 'a'    // another NEW x!
        fmt.Printf("%c", x)   // this x
    }
    // outer x is still "hello!" here
}
```

**Short declaration scope trap:**
```go
var cwd string          // package-level

func init() {
    cwd, err := os.Getwd()   // WRONG! := creates NEW local cwd
    // package-level cwd is never set!
    _ = err
}

// Fix:
func init() {
    var err error
    cwd, err = os.Getwd()   // = (not :=) assigns to existing cwd
    if err != nil { ... }
}
```

---

## Summary

```
┌─────────────────────────────────────────────────────┐
│              Variable Declaration                    │
│                                                      │
│  var x T = value    → explicit, full form            │
│  var x T            → zero value                     │
│  var x = value      → type inferred                  │
│  x := value         → short (functions only)         │
│                                                      │
│  Zero values → ALWAYS defined, NEVER garbage         │
│  Uppercase   → exported (public)                     │
│  Lowercase   → unexported (package-private)          │
└─────────────────────────────────────────────────────┘
```

---

*← [Chapter 1 — Tutorial](01-tutorial.md) | [Back to Index](../README.md) | [Chapter 3 — Basic Data Types](03-basic-data-types.md) →*
