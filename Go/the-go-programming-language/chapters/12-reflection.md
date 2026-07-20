# Chapter 12: Reflection

> *"Reflection is the ability of a program to examine its own structure, particularly through types — it's a form of metaprogramming."*

---

## Core Concept

Reflection lets you inspect and manipulate values and types at **runtime**, without knowing them at compile time. It's powerful but should be used sparingly. Most Go code never needs it.

---

## 12.1 Why Reflection?

Without reflection, you can't write generic code that works on unknown types:

```go
// Problem: how do you write fmt.Println for ANY type?
// Answer: reflect package

fmt.Println(42)            // int
fmt.Println("hello")       // string
fmt.Println([]int{1,2,3})  // slice
// fmt must handle ALL of these — using reflection
```

---

## 12.2 `reflect.Type` and `reflect.Value`

```go
import "reflect"

// reflect.TypeOf → returns the Type of a value
t := reflect.TypeOf(3.14)
fmt.Println(t)        // "float64"
fmt.Println(t.Kind()) // "float64" (Kind is more specific category)

// reflect.ValueOf → returns a Value wrapping the actual data
v := reflect.ValueOf(3.14)
fmt.Println(v)        // "3.14"
fmt.Println(v.Type()) // "float64"
fmt.Println(v.Kind()) // "float64"
fmt.Println(v.Float()) // 3.14  (extract actual value)
```

**Kind vs Type:**
```go
// Kind is one of: Bool, Int, Float64, String, Ptr, Struct, Slice, Map, etc.
// Type is the exact named type

type Celsius float64
c := Celsius(100)

reflect.TypeOf(c).Name()  // "Celsius"    (Type name)
reflect.TypeOf(c).Kind()  // "float64"    (underlying Kind)
```

---

## 12.3 Inspecting Struct Fields

```go
type Person struct {
    Name string `json:"name"`
    Age  int    `json:"age,omitempty"`
}

p := Person{"Alice", 30}
t := reflect.TypeOf(p)
v := reflect.ValueOf(p)

for i := 0; i < t.NumField(); i++ {
    field := t.Field(i)          // reflect.StructField
    value := v.Field(i)          // reflect.Value

    fmt.Printf("Name: %-10s  Kind: %-10s  Value: %v  Tag: %s\n",
        field.Name,
        field.Type.Kind(),
        value,
        field.Tag.Get("json"),
    )
}
// Name: Name        Kind: string      Value: Alice  Tag: name
// Name: Age         Kind: int         Value: 30     Tag: age,omitempty
```

---

## 12.4 Setting Values via Reflection

```go
// To set a value, you need a POINTER (addressable)
x := 42
v := reflect.ValueOf(&x).Elem()  // .Elem() dereferences the pointer

fmt.Println(v.CanSet())  // true
v.SetInt(100)
fmt.Println(x)           // 100

// Non-addressable values cannot be set
v2 := reflect.ValueOf(42)
fmt.Println(v2.CanSet()) // false
// v2.SetInt(100) → panic!
```

---

## 12.5 Calling Methods via Reflection

```go
type Dog struct{ Name string }
func (d Dog) Speak() string { return d.Name + " says: Woof!" }

d := Dog{"Rex"}
v := reflect.ValueOf(d)

method := v.MethodByName("Speak")
result := method.Call(nil)  // nil = no arguments
fmt.Println(result[0].String()) // "Rex says: Woof!"
```

---

## 12.6 Practical Example: Display Any Value

```go
// A simplified version of what fmt.Println does internally
func display(name string, v reflect.Value) {
    switch v.Kind() {
    case reflect.Invalid:
        fmt.Printf("%s = invalid\n", name)
    case reflect.Slice, reflect.Array:
        for i := 0; i < v.Len(); i++ {
            display(fmt.Sprintf("%s[%d]", name, i), v.Index(i))
        }
    case reflect.Struct:
        for i := 0; i < v.NumField(); i++ {
            fieldPath := fmt.Sprintf("%s.%s", name, v.Type().Field(i).Name)
            display(fieldPath, v.Field(i))
        }
    case reflect.Map:
        for _, key := range v.MapKeys() {
            display(fmt.Sprintf("%s[%q]", name, key), v.MapIndex(key))
        }
    case reflect.Ptr:
        if v.IsNil() {
            fmt.Printf("%s = nil\n", name)
        } else {
            display("(*"+name+")", v.Elem())
        }
    default:
        fmt.Printf("%s = %v\n", name, v)
    }
}
```

---

## 12.7 Struct Tags

```go
type User struct {
    Name  string `json:"name" validate:"required"`
    Email string `json:"email" validate:"email"`
    Age   int    `json:"age,omitempty"`
}

t := reflect.TypeOf(User{})
for i := 0; i < t.NumField(); i++ {
    f := t.Field(i)
    fmt.Printf("%-10s json=%-20s validate=%s\n",
        f.Name,
        f.Tag.Get("json"),
        f.Tag.Get("validate"),
    )
}
// Name       json=name                 validate=required
// Email      json=email                validate=email
// Age        json=age,omitempty        validate=
```

---

## When to Use Reflection

```
USE reflection when:
  ✅ Writing serialization (JSON, XML, YAML encoders)
  ✅ Building generic utilities (fmt, testing)
  ✅ Implementing dependency injection frameworks
  ✅ Reading struct tags at runtime

AVOID reflection when:
  ❌ A simple interface would do
  ❌ You know the types at compile time
  ❌ Performance is critical (reflection is ~10x slower)
  ❌ You want clear, readable code
```

---

## Visual Summary

```
REFLECTION
═══════════════════════════════════════════════

reflect.TypeOf(x)  → Type  (name, kind, methods, fields)
reflect.ValueOf(x) → Value (the actual data)

Kind hierarchy:
  Bool
  Int, Int8, Int16, Int32, Int64
  Uint, ...
  Float32, Float64
  Complex64, Complex128
  Array, Chan, Func, Interface, Map, Ptr, Slice, String, Struct

To READ:   reflect.ValueOf(x).Field(i).String()
To WRITE:  reflect.ValueOf(&x).Elem().Field(i).SetString("new")
           ↑ must use pointer!

Struct Tags:
  field.Tag.Get("json")      → "name,omitempty"
  field.Tag.Get("validate")  → "required"

⚠️  Reflection bypasses type safety — use carefully!
```

---

*← [Chapter 11 — Testing](11-testing.md) | [Back to Index](../README.md) | [Chapter 13 — Low-Level Programming](13-low-level-programming.md) →*
