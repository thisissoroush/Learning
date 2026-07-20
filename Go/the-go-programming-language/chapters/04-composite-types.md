# Chapter 4: Composite Types

> Arrays, slices, maps, and structs — building complex data from simple types.

---

## Core Concepts

1. **Arrays** — fixed-size, value type, rarely used directly
2. **Slices** — dynamic, reference to array, Go's workhorse collection
3. **Maps** — hash tables, unordered key/value pairs
4. **Structs** — grouped fields, composition via embedding
5. **JSON** — marshaling/unmarshaling Go structs
6. **Templates** — text/html generation

---

## 4.1 Arrays

Fixed-length sequence. **Rarely used directly** — prefer slices.

```go
var a [3]int                      // [0, 0, 0]
a[0] = 1
fmt.Println(a[len(a)-1])          // last element

var q [3]int = [3]int{1, 2, 3}   // literal
q := [...]int{1, 2, 3}           // ... = compiler counts

// Arrays are VALUES (copied on assignment):
b := a                            // b is a copy of a
b[0] = 99                         // doesn't affect a
```

**Array size is part of its type:**
```go
// [3]int and [4]int are DIFFERENT types
q := [3]int{1, 2, 3}
// q = [4]int{...}  ← COMPILE ERROR
```

---

## 4.2 Slices

A slice is a **view into an underlying array** with three fields:
```
┌─────────┐
│ pointer │ → points to first element in array
│ length  │ → number of elements accessible
│ capacity│ → elements until end of underlying array
└─────────┘
```

```go
months := [...]string{1:"Jan", 2:"Feb", ..., 12:"Dec"}
Q2     := months[4:7]   // ["Apr","May","Jun"]  len=3, cap=9
summer := months[6:9]   // ["Jun","Jul","Aug"]  len=3, cap=7

// Both share same underlying array!
summer[0] = "changed"   // also changes months[6]
```

**Slice diagram:**
```
months:  [_ Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec]
              1   2   3   4   5   6   7   8   9  10  11  12

Q2:          [        4   5   6  ]        ptr→months[4], len=3, cap=9
summer:                  [6   7   8  ]    ptr→months[6], len=3, cap=7
```

**Creating slices:**
```go
s := []int{1, 2, 3}         // slice literal (creates array too)
s := make([]int, 3)          // [0,0,0] len=3 cap=3
s := make([]int, 3, 5)       // [0,0,0] len=3 cap=5
```

**nil vs empty:**
```go
var s []int      // nil slice: s==nil, len(s)==0
s = []int{}      // non-nil empty: s!=nil, len(s)==0
s = make([]int, 0)  // non-nil empty
// Use len(s)==0, not s==nil, to check emptiness!
```

### `append` — The Key Operation

```go
var s []int
s = append(s, 1)          // [1]
s = append(s, 2, 3)       // [1,2,3]
s = append(s, s...)        // [1,2,3,1,2,3] (spread operator)
```

**How append works (doubling strategy):**
```
i=0: cap=1  [0]
i=1: cap=2  [0 1]           ← reallocated
i=2: cap=4  [0 1 2]         ← reallocated
i=3: cap=4  [0 1 2 3]       (no realloc, had slack)
i=4: cap=8  [0 1 2 3 4]     ← reallocated (doubled to 8)
...
```

**Always reassign after append:**
```go
// WRONG: s might be a stale reference after reallocation
append(s, x)

// CORRECT:
s = append(s, x)
```

### In-Place Slice Techniques

```go
// Reverse in place:
func reverse(s []int) {
    for i, j := 0, len(s)-1; i < j; i, j = i+1, j-1 {
        s[i], s[j] = s[j], s[i]
    }
}

// Filter non-empty strings (reuse same backing array):
func nonempty(strings []string) []string {
    i := 0
    for _, s := range strings {
        if s != "" {
            strings[i] = s
            i++
        }
    }
    return strings[:i]
}

// Stack operations:
stack = append(stack, v)           // push
top := stack[len(stack)-1]         // peek
stack = stack[:len(stack)-1]       // pop

// Remove element at index i (order preserved):
copy(slice[i:], slice[i+1:])
slice = slice[:len(slice)-1]
```

---

## 4.3 Maps

Hash table: `map[K]V` — unordered key/value pairs.

```go
ages := make(map[string]int)
ages := map[string]int{          // map literal
    "alice":   31,
    "charlie": 34,
}

ages["alice"] = 32               // set
fmt.Println(ages["alice"])       // 32
delete(ages, "alice")            // remove
ages["bob"]++                    // safe even if "bob" doesn't exist (zero value = 0)

// Check existence:
age, ok := ages["bob"]
if !ok { /* "bob" not in map */ }

// Combined form:
if age, ok := ages["bob"]; !ok { ... }

// Range (order is RANDOM):
for name, age := range ages {
    fmt.Printf("%s: %d\n", name, age)
}
```

**Map as Set:**
```go
seen := make(map[string]bool)
seen["hello"] = true
if !seen["world"] { ... }   // false = not seen
```

**Nil map panics on write:**
```go
var m map[string]int
m["key"] = 1   // PANIC: assignment to entry in nil map
// Must: m = make(map[string]int)
```

---

## 4.4 Structs

```go
type Employee struct {
    ID       int
    Name     string
    Position string
    Salary   int
}

var e Employee
e.Name = "Alice"
e.Salary = 50000

// Struct literal:
e := Employee{ID: 1, Name: "Alice", Salary: 50000}

// Pointer to struct:
p := &Employee{ID: 1, Name: "Bob"}
p.Salary = 60000   // shorthand for (*p).Salary
```

### Struct Embedding (Composition)

```go
type Point struct{ X, Y int }

type Circle struct {
    Point           // anonymous field — embedded!
    Radius int
}

type Wheel struct {
    Circle          // embedded
    Spokes int
}

var w Wheel
w.X = 8            // shorthand for w.Circle.Point.X = 8
w.Radius = 5       // shorthand for w.Circle.Radius = 5
w.Spokes = 20
```

**Embedding promotes fields AND methods:**
```
Wheel
 └── Circle (promoted: Radius, all Circle methods)
      └── Point (promoted: X, Y, all Point methods)
```

---

## 4.5 JSON

```go
type Movie struct {
    Title  string
    Year   int    `json:"released"`           // custom JSON key
    Color  bool   `json:"color,omitempty"`    // omit if false
    Actors []string
}

movies := []Movie{
    {Title: "Casablanca", Year: 1942, Actors: []string{"Bogart"}},
}

// Marshal (Go → JSON):
data, err := json.Marshal(movies)
data, err := json.MarshalIndent(movies, "", "  ")  // pretty print

// Unmarshal (JSON → Go):
var titles []struct{ Title string }
json.Unmarshal(data, &titles)
// Only "Title" field populated, rest ignored

// Streaming decoder (for large data or HTTP responses):
json.NewDecoder(resp.Body).Decode(&result)
```

**JSON → Go field matching is case-insensitive:**
```
JSON "html_url" → Go field with `json:"html_url"` tag
JSON "Title"    → Go field "Title" (exact or case-insensitive)
```

---

## 4.6 Text and HTML Templates

```go
const templ = `{{.TotalCount}} issues:
{{range .Items}}
Number: {{.Number}}
User:   {{.User.Login}}
Title:  {{.Title | printf "%.64s"}}
{{end}}`

// Parse once, execute many times:
t := template.Must(template.New("report").Parse(templ))
t.Execute(os.Stdout, data)

// HTML template auto-escapes for XSS safety:
import "html/template"
// <script> in data → &lt;script&gt; in output
```

---

## Summary

```
┌──────────┬─────────────┬──────────────────────────────────────┐
│ Type     │ Mutable?    │ Notes                                │
├──────────┼─────────────┼──────────────────────────────────────┤
│ Array    │ Yes (values)│ Fixed size, value semantics           │
│ Slice    │ Yes (shared)│ Dynamic, reference to array           │
│ Map      │ Yes (shared)│ Hash table, random iteration order    │
│ Struct   │ Yes         │ Value type, use pointer for mutation  │
│ String   │ No          │ Immutable bytes                       │
└──────────┴─────────────┴──────────────────────────────────────┘

Key Rule: Slices, maps, and channels are reference types.
          Assigning them copies the reference, not the data.
```

---

*← [Chapter 3 — Basic Data Types](03-basic-data-types.md) | [Back to Index](../README.md) | [Chapter 5 — Functions](05-functions.md) →*
