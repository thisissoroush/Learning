# Chapter 6: Methods

> *"An object is simply a value or variable that has methods, and a method is a function associated with a particular type."*

---

## Core Concept

Go achieves object-oriented programming through **methods on named types** — not classes. Any named type can have methods. The relationship is **composition over inheritance**.

---

## 6.1 Method Declarations

A method is a function with an extra **receiver** parameter that appears before the function name:

```go
type Point struct{ X, Y float64 }

// Regular function
func Distance(p, q Point) float64 {
    return math.Hypot(q.X-p.X, q.Y-p.Y)
}

// Same logic as a METHOD of Point
func (p Point) Distance(q Point) float64 {
    return math.Hypot(q.X-p.X, q.Y-p.Y)
}

p := Point{1, 2}
q := Point{4, 6}
fmt.Println(Distance(p, q))  // function call
fmt.Println(p.Distance(q))   // method call — p is the receiver
```

```
Method call anatomy:
  p.Distance(q)
  │  └── method name
  └── receiver (the object)
```

**Methods can be on any named type** — not just structs:

```go
type Path []Point  // a named slice type

func (path Path) Distance() float64 {
    sum := 0.0
    for i := range path {
        if i > 0 {
            sum += path[i-1].Distance(path[i])
        }
    }
    return sum
}

perim := Path{{1,1}, {5,1}, {5,4}, {1,1}}
fmt.Println(perim.Distance()) // "12"
```

---

## 6.2 Methods with a Pointer Receiver

Use `*T` receiver when:
1. The method **mutates** the receiver
2. The receiver is **large** (avoids copying)

```go
func (p *Point) ScaleBy(factor float64) {
    p.X *= factor
    p.Y *= factor
}

// Three equivalent ways to call a pointer-receiver method:
r := &Point{1, 2}
r.ScaleBy(2)        // explicit pointer

p := Point{1, 2}
(&p).ScaleBy(2)     // explicit address

p.ScaleBy(2)        // compiler adds & automatically (if p is addressable)
```

```
Receiver type      Compiler action
──────────────────────────────────
*Point needed, have Point  →  &p  (if p is a variable)
 Point needed, have *Point  →  *p  (always ok)
```

> ⚠️ Convention: if **any** method has a pointer receiver, **all** methods should use pointer receivers.

### Nil Is a Valid Receiver

```go
type IntList struct {
    Value int
    Tail  *IntList
}

func (list *IntList) Sum() int {
    if list == nil {
        return 0  // nil is the empty list
    }
    return list.Value + list.Tail.Sum()
}
```

---

## 6.3 Composing Types by Struct Embedding

Embedding **promotes** fields and methods from the embedded type:

```go
type Point struct{ X, Y float64 }
type Circle struct {
    Point        // anonymous field — embeds Point
    Radius float64
}
type Wheel struct {
    Circle       // anonymous field — embeds Circle
    Spokes int
}

var w Wheel
w.X = 8          // shorthand for w.Circle.Point.X = 8
w.Y = 8          // shorthand for w.Circle.Point.Y = 8
w.Radius = 5     // shorthand for w.Circle.Radius = 5
w.Spokes = 20
```

```
Embedding hierarchy:

Wheel
 ├── Circle (embedded)
 │    ├── Point (embedded)
 │    │    ├── X  ← accessible as w.X
 │    │    └── Y  ← accessible as w.Y
 │    └── Radius ← accessible as w.Radius
 └── Spokes ← accessible as w.Spokes
```

**Methods are promoted too:**

```go
// Even though ColoredPoint has no Distance method, it gets it from Point
type ColoredPoint struct {
    Point
    Color color.RGBA
}

p := ColoredPoint{Point{1, 1}, red}
q := ColoredPoint{Point{5, 4}, blue}
fmt.Println(p.Distance(q.Point)) // calls Point.Distance
p.ScaleBy(2)                     // calls (*Point).ScaleBy
```

> ⚠️ This is NOT inheritance. `ColoredPoint` **has a** `Point` — it is NOT a `Point`.

**Struct literal syntax still requires explicit embedding:**

```go
w = Wheel{Circle{Point{8, 8}, 5}, 20}
// or
w = Wheel{
    Circle: Circle{
        Point:  Point{X: 8, Y: 8},
        Radius: 5,
    },
    Spokes: 20,
}
```

---

## 6.4 Method Values and Expressions

```go
p := Point{1, 2}
q := Point{4, 6}

// Method VALUE — binds method to specific receiver
distanceFromP := p.Distance  // p is bound
fmt.Println(distanceFromP(q)) // "5"

// Method EXPRESSION — first param becomes the receiver
distance := Point.Distance
fmt.Println(distance(p, q))   // "5"
fmt.Printf("%T\n", distance)  // "func(Point, Point) float64"
```

---

## 6.5 Encapsulation

Go's encapsulation is **package-level**: exported names start with uppercase, unexported don't.

```go
// IntSet is opaque — internal representation is hidden
type IntSet struct {
    words []uint64  // unexported — clients can't access directly
}

func (s *IntSet) Has(x int) bool { ... }
func (s *IntSet) Add(x int)      { ... }
func (s *IntSet) String() string { ... }
```

**Benefits of encapsulation:**
1. Fewer statements to inspect (internal state is controlled)
2. Freedom to change implementation without breaking API
3. Prevents clients from setting invalid state

```go
// Example: Counter only allows increment and reset — not arbitrary set
type Counter struct { n int }
func (c *Counter) N() int       { return c.n }
func (c *Counter) Increment()   { c.n++ }
func (c *Counter) Reset()       { c.n = 0 }
```

---

## Visual Summary

```
GO METHODS
═══════════════════════════════════════════════

Named type T  →  methods with receiver (p T)
Pointer *T    →  methods with receiver (p *T) — for mutation

EMBEDDING (not inheritance):
  Outer struct gets inner type's fields AND methods promoted

  type Wheel struct {
      Circle          ← embedded
      Spokes int
  }
  w.X = 8            ← w.Circle.Point.X shorthand

ENCAPSULATION:
  Uppercase = exported (public)
  lowercase = unexported (package-private)
  Unit of encapsulation = PACKAGE (not type)

METHOD VALUE:   p.Distance      (p is bound)
METHOD EXPR:    Point.Distance  (p is first param)
```
