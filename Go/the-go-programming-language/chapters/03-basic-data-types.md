# Chapter 3: Basic Data Types

> Numbers, strings, booleans, and constants — the atoms of Go programs.

---

## Core Concepts

1. **Integers** — signed/unsigned, multiple sizes, bit operators
2. **Floating-point** — `float32`/`float64`, IEEE 754
3. **Complex numbers** — built into the language
4. **Booleans** — `true`/`false`, no implicit conversion
5. **Strings** — immutable byte sequences, UTF-8
6. **Constants & `iota`** — compile-time values, enum pattern

---

## 3.1 Integers

```
Signed:   int8  int16  int32  int64
Unsigned: uint8 uint16 uint32 uint64
Platform: int   uint   uintptr   (32 or 64 bit depending on platform)
Aliases:  byte = uint8,  rune = int32
```

**Binary operators (decreasing precedence):**
```
*  /  %  <<  >>  &  &^
+  -  |  ^
== != <  <= >  >=
&&
||
```

**Bitwise operations example:**
```go
var x uint8 = 1<<1 | 1<<5   // bits 1 and 5 set
var y uint8 = 1<<1 | 1<<2   // bits 1 and 2 set

fmt.Printf("%08b\n", x)     // 00100010  {1,5}
fmt.Printf("%08b\n", x&y)   // 00000010  intersection {1}
fmt.Printf("%08b\n", x|y)   // 00100110  union {1,2,5}
fmt.Printf("%08b\n", x^y)   // 00100100  symmetric diff {2,5}
fmt.Printf("%08b\n", x&^y)  // 00100000  difference {5}
```

**⚠️ Use signed int for lengths/indices:**
```go
medals := []string{"gold", "silver", "bronze"}
for i := len(medals) - 1; i >= 0; i-- {  // works!
    fmt.Println(medals[i])
}
// If len() returned uint, i >= 0 would ALWAYS be true → infinite loop!
```

---

## 3.2 Floating-Point Numbers

```go
var f float32 = 16777216  // 1<<24
fmt.Println(f == f+1)     // "true"! float32 loses precision

const e = 2.71828          // float64 by default
const Avogadro = 6.02e23   // scientific notation

// Special values:
var z float64
fmt.Println(z, -z, 1/z, -1/z, z/z)  // 0 -0 +Inf -Inf NaN

nan := math.NaN()
fmt.Println(nan == nan)  // false! NaN ≠ NaN always
```

**Prefer `float64`** — `float32` accumulates errors rapidly.

**Format verbs:**
```
%f    3.141593       (no exponent)
%e    3.141593e+00   (scientific)
%g    3.141593       (shortest)
```

---

## 3.3 Complex Numbers

```go
var x complex128 = complex(1, 2)  // 1+2i
var y complex128 = complex(3, 4)  // 3+4i

fmt.Println(x*y)        // (-5+10i)
fmt.Println(real(x*y))  // -5
fmt.Println(imag(x*y))  // 10

// Shorthand:
x := 1 + 2i
y := 3 + 4i

fmt.Println(cmplx.Sqrt(-1))  // (0+1i)
```

---

## 3.4 Booleans

```go
var b bool = true
fmt.Println(!b)          // false
fmt.Println(b && false)  // false (short-circuit: right side not evaluated if left is false)
fmt.Println(b || false)  // true  (short-circuit: right side not evaluated if left is true)

// No implicit conversion to/from numbers:
// if 1 { }    ← COMPILE ERROR

// Safe pattern:
s != "" && s[0] == 'x'  // s[0] only checked if s is non-empty
```

---

## 3.5 Strings

**Strings are immutable byte sequences (usually UTF-8):**

```go
s := "hello, world"
fmt.Println(len(s))    // 12 (bytes, not characters!)
fmt.Println(s[0])      // 104 (byte value of 'h')
fmt.Println(s[0:5])    // "hello"
fmt.Println(s[7:])     // "world"
fmt.Println(s[:5])     // "hello"

// Immutable:
// s[0] = 'H'  ← COMPILE ERROR

// But you can create new strings:
s += ", right foot"  // new string, old one unchanged
```

**String diagram:**
```
s = "hello, world"

 index: 0  1  2  3  4  5  6  7  8  9  10 11
 byte:  h  e  l  l  o  ,     w  o  r  l  d

 s[0:5]  → "hello"   (new string header, same underlying bytes)
 s[7:]   → "world"   (cheap! just pointer + length)
```

### String Literals

```go
"Hello\nWorld"   // interpreted: \n is newline
`Hello\nWorld`   // raw: \n is literal backslash-n (backtick)
```

### Unicode and UTF-8

```go
s := "Hello, 世界"
fmt.Println(len(s))                    // 13 bytes (not 9 chars!)
fmt.Println(utf8.RuneCountInString(s)) // 9 runes

// Range loop decodes UTF-8 automatically:
for i, r := range s {
    fmt.Printf("%d\t%q\t%d\n", i, r, r)
}
// 0    'H'   72
// 1    'e'   101
// ...
// 7    '世'  19990   ← 3 bytes, index jumps by 3
// 10   '界'  30028   ← 3 bytes
```

**UTF-8 encoding:**
```
0xxxxxxx                → 1 byte  (0-127, ASCII)
110xxxxx 10xxxxxx       → 2 bytes (128-2047)
1110xxxx 10xxxxxx 10xxxxxx  → 3 bytes (2048-65535)
```

### Key String Packages
```
strings    → Contains, HasPrefix, Join, Split, Replace, ToUpper...
bytes      → same functions but for []byte
strconv    → Atoi, Itoa, ParseFloat, FormatInt...
unicode    → IsLetter, IsDigit, ToUpper...
```

**Converting between string and []byte:**
```go
s := "abc"
b := []byte(s)   // copy of bytes (s is immutable, b is mutable)
s2 := string(b)  // copy back to string

// bytes.Buffer for building strings efficiently:
var buf bytes.Buffer
buf.WriteString("hello")
buf.WriteString(", world")
fmt.Println(buf.String())  // "hello, world"
```

---

## 3.6 Constants

```go
const pi = 3.14159
const (
    e  = 2.71828
    pi = 3.14159
)

// Type-specific constant:
const noDelay time.Duration = 0
const timeout = 5 * time.Minute
```

### `iota` — The Constant Generator

```go
type Weekday int

const (
    Sunday Weekday = iota  // 0
    Monday                  // 1
    Tuesday                 // 2
    Wednesday               // 3
    Thursday                // 4
    Friday                  // 5
    Saturday                // 6
)
```

**Powers of 2 with `iota`:**
```go
type Flags uint
const (
    FlagUp        Flags = 1 << iota  // 1
    FlagBroadcast                    // 2
    FlagLoopback                     // 4
    FlagPointToPoint                 // 8
    FlagMulticast                    // 16
)
```

**Storage sizes:**
```go
const (
    _   = 1 << (10 * iota)  // ignore first value
    KiB                      // 1024
    MiB                      // 1048576
    GiB                      // 1073741824
    TiB                      // 1099511627776
    PiB                      // 1125899906842624
    EiB                      // 1152921504606846976
)
```

### Untyped Constants

```go
// math.Pi can be used as float32, float64, or complex128:
var x float32  = math.Pi
var y float64  = math.Pi
var z complex128 = math.Pi
// No conversion needed — untyped constants adapt!

// Watch out with division:
fmt.Println(5 / 9 * (212.0 - 32))    // 0   (integer division)
fmt.Println(5.0 / 9.0 * (212.0 - 32)) // 100 (float division)
```

---

## Summary

```
Type        Size         Range / Notes
─────────── ──────────── ─────────────────────────────────────
int8        8 bits       -128 to 127
uint8/byte  8 bits       0 to 255
int16       16 bits      -32768 to 32767
int32/rune  32 bits      Unicode code point
int64       64 bits      ±9.2 × 10^18
float32     32 bits      ~6 decimal digits precision
float64     64 bits      ~15 decimal digits precision (prefer!)
complex128  128 bits     two float64s
bool        1 bit        true / false
string      immutable    UTF-8 bytes, len() = bytes not chars
```
