# Chapter 13: Low-Level Programming

> *"The unsafe package lets you step outside Go's type system when you need to — but with great power comes great responsibility."*

---

## Core Concept

Go is a safe language — the type system prevents most memory errors. But sometimes you need to go low-level: talking to C libraries, working with OS internals, or squeezing maximum performance. The `unsafe` package is the escape hatch.

**Use this only when absolutely necessary. Normal Go code never needs it.**

---

## 13.1 `unsafe.Sizeof`, `Alignof`, `Offsetof`

These functions operate at compile time and return memory layout information:

```go
import "unsafe"

var x struct {
    a bool    // 1 byte
    b int16   // 2 bytes
    c []int   // 24 bytes (ptr + len + cap)
}

// Sizeof: total bytes in memory representation
fmt.Println(unsafe.Sizeof(x.a))  // 1
fmt.Println(unsafe.Sizeof(x.b))  // 2
fmt.Println(unsafe.Sizeof(x.c))  // 24
fmt.Println(unsafe.Sizeof(x))    // 32 (with padding/alignment)

// Alignof: required memory alignment in bytes
fmt.Println(unsafe.Alignof(x.a)) // 1
fmt.Println(unsafe.Alignof(x.b)) // 2

// Offsetof: byte offset of field within struct
fmt.Println(unsafe.Offsetof(x.a)) // 0
fmt.Println(unsafe.Offsetof(x.b)) // 2  (padded from 1 to align on 2)
fmt.Println(unsafe.Offsetof(x.c)) // 8  (padded to align on 8)
```

```
Memory layout visualization:

Byte: 0    1    2    3    4    5    6    7    8   ...  31
      [  a ][pad][    b    ][         pad         ][     c (slice)    ]
       bool        int16                             ptr+len+cap
```

---

## 13.2 `unsafe.Pointer`

`unsafe.Pointer` is a special pointer type that can hold the address of any value and be converted to any other pointer type:

```go
// Legal conversions involving unsafe.Pointer:
// 1. *T → unsafe.Pointer
// 2. unsafe.Pointer → *T
// 3. unsafe.Pointer → uintptr (for arithmetic)
// 4. uintptr → unsafe.Pointer (DANGEROUS)

// Example: reinterpret float64 bits as uint64
func Float64bits(f float64) uint64 {
    return *(*uint64)(unsafe.Pointer(&f))
}

fmt.Printf("%016x\n", Float64bits(1.0))
// Output: 3ff0000000000000  (IEEE 754 representation)
```

**Common pattern — accessing struct fields by offset:**
```go
// Accessing unexported field (fragile, not recommended)
type MyStruct struct {
    // ... exported fields ...
    secret int  // unexported
}

s := MyStruct{}
// Get pointer to 'secret' field using its offset
p := (*int)(unsafe.Pointer(
    uintptr(unsafe.Pointer(&s)) + unsafe.Offsetof(s.secret),
))
*p = 42
```

---

## 13.3 Deep Equivalence

The `reflect.DeepEqual` function uses reflection (not `unsafe`) to compare any two values recursively:

```go
import "reflect"

// Works for slices, maps, structs — things == can't handle
a := []int{1, 2, 3}
b := []int{1, 2, 3}

fmt.Println(a == b)                    // compile error: slice not comparable
fmt.Println(reflect.DeepEqual(a, b))   // true

// For maps
m1 := map[string]int{"a": 1}
m2 := map[string]int{"a": 1}
fmt.Println(reflect.DeepEqual(m1, m2)) // true
```

---

## 13.4 Calling C Code with `cgo`

`cgo` allows Go programs to call C functions directly:

```go
package main

/*
#include <stdio.h>
#include <stdlib.h>

void sayHello(const char* name) {
    printf("Hello from C, %s!\n", name);
}
*/
import "C"
import "unsafe"

func main() {
    name := C.CString("Go")        // Go string → C string (malloc)
    defer C.free(unsafe.Pointer(name))  // must free!
    C.sayHello(name)
}
```

```bash
go build    # automatically invokes C compiler via cgo
```

**cgo rules:**
```
Go → C:  Use C.CString() for strings, manual memory management required
C → Go:  Use //export annotation, but exported functions can't use cgo themselves
```

---

## Safety Rules for `unsafe.Pointer`

```
⚠️  RULES — violating these causes subtle memory corruption bugs:

✅ SAFE:
   p := unsafe.Pointer(&x)         // take address
   q := (*int)(p)                  // convert to concrete pointer type
   *q = 42                         // use it

❌ DANGEROUS:
   // Converting uintptr back to unsafe.Pointer is only safe
   // in a SINGLE expression — never store uintptr in a variable!
   
   // BAD: GC can move x between these two lines
   addr := uintptr(unsafe.Pointer(&x))  // store address
   p := unsafe.Pointer(addr)             // convert back — x may have moved!
   
   // GOOD: single expression
   p := unsafe.Pointer(uintptr(unsafe.Pointer(&x)) + offset)
```

---

## When to Use `unsafe`

```
✅ USE unsafe for:
   - Calling C libraries (via cgo)
   - OS/syscall interfaces requiring raw memory
   - Performance-critical code after profiling proves it necessary
   - Implementing low-level data structures

❌ NEVER use unsafe for:
   - Accessing unexported fields of external packages
   - Bypassing type checks "for convenience"
   - Code that will be maintained long-term without deep Go expertise
```

---

## Visual Summary

```
LOW-LEVEL PROGRAMMING
═══════════════════════════════════════════════

unsafe package functions (compile-time):
  unsafe.Sizeof(x)        → bytes x occupies in memory
  unsafe.Alignof(x)       → alignment requirement
  unsafe.Offsetof(x.f)    → byte offset of field f in struct x

unsafe.Pointer:
  The universal pointer — can convert TO/FROM any *T
  
  *T ──────────────→ unsafe.Pointer ──────────────→ *U
                             │
                             ↓ (arithmetic only)
                          uintptr

cgo (C interop):
  /* #include <foo.h> */
  import "C"
  C.foo()          → call C function
  C.CString(s)     → Go string to C *char
  C.free(ptr)      → free C memory

MEMORY LAYOUT:
  Struct fields have padding for alignment
  Offsetof tells you where each field starts
  
  [field a][padding][field b][padding][field c...]
   ^                ^
   Offsetof(a)=0    Offsetof(b)=depends on alignment
```
