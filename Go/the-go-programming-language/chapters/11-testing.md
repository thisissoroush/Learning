# Chapter 11: Testing

> *"Testing is the practice of creating small programs that check the behavior of other programs."*

---

## Core Concept

Go has a built-in lightweight testing framework. Tests are plain Go functions with specific naming conventions. No heavy frameworks needed — the standard library covers everything.

---

## 11.1 The `go test` Tool

```
File naming:   *_test.go  (only compiled during testing)
Function types:
  TestXxx(t *testing.T)       → unit test
  BenchmarkXxx(b *testing.B)  → performance benchmark
  ExampleXxx()                → documentation + test
```

```bash
go test                    # test current package
go test ./...              # test all packages
go test -v                 # verbose (print all test names)
go test -run TestFoo       # run specific test by regex
go test -run "Test(Add|Sub)" # run multiple
go test -count=1           # disable result caching
```

---

## 11.2 Test Functions

```go
// word_test.go
package word

import "testing"

func TestPalindrome(t *testing.T) {
    // Basic assertion
    if !IsPalindrome("racecar") {
        t.Error("expected 'racecar' to be a palindrome")
    }
}

// Table-driven test (idiomatic Go pattern)
func TestIsPalindrome(t *testing.T) {
    tests := []struct {
        input string
        want  bool
    }{
        {"", true},
        {"a", true},
        {"racecar", true},
        {"hello", false},
        {"A man a plan a canal Panama", false}, // spaces matter
    }
    for _, tt := range tests {
        got := IsPalindrome(tt.input)
        if got != tt.want {
            t.Errorf("IsPalindrome(%q) = %v, want %v",
                tt.input, got, tt.want)
        }
    }
}
```

**Key `*testing.T` methods:**
```go
t.Error("msg")      // log failure, continue test
t.Errorf("fmt", …)  // formatted failure, continue
t.Fatal("msg")      // log failure, STOP test immediately
t.Fatalf("fmt", …)  // formatted, STOP
t.Log("msg")        // log (only shown with -v)
t.Skip("reason")    // skip this test
t.Helper()          // mark as helper (better error location)
```

---

## 11.3 Test Coverage

```bash
go test -cover                    # show % coverage
go test -coverprofile=c.out       # save profile
go tool cover -html=c.out         # open HTML report in browser
go tool cover -func=c.out         # show per-function coverage
```

```
ok      mypackage   0.012s  coverage: 87.3% of statements
```

---

## 11.4 Benchmark Functions

```go
func BenchmarkIsPalindrome(b *testing.B) {
    for i := 0; i < b.N; i++ {  // b.N auto-tuned by framework
        IsPalindrome("A man, a plan, a canal: Panama")
    }
}
```

```bash
go test -bench=.              # run all benchmarks
go test -bench=BenchmarkFoo   # run specific
go test -bench=. -benchmem    # include memory allocations
go test -bench=. -count=5     # run 5 times for stability
```

```
BenchmarkIsPalindrome-8    1000000    1023 ns/op    128 B/op    3 allocs/op
        ↑ func name   ↑ CPUs  ↑ iterations  ↑ time/op   ↑ memory    ↑ allocs
```

---

## 11.5 Profiling

```bash
go test -cpuprofile=cpu.out   # CPU profile
go test -memprofile=mem.out   # memory profile
go tool pprof cpu.out         # interactive profiler
```

---

## 11.6 Example Functions

```go
// Self-documenting AND tested: output must match comment
func ExampleIsPalindrome() {
    fmt.Println(IsPalindrome("racecar"))
    fmt.Println(IsPalindrome("hello"))
    // Output:
    // true
    // false
}
```

---

## External Test Packages

```go
// package word        → testing internals
// package word_test   → testing the public API (black-box)

package word_test  // note: _test suffix

import (
    "testing"
    "word"  // import your own package
)
```

---

## Visual Summary

```
TESTING IN GO
═══════════════════════════════════════════════

FILE:     foo_test.go  (excluded from normal builds)
PACKAGE:  package foo       (white-box, internal access)
          package foo_test  (black-box, public API only)

TEST TYPES:
  func TestXxx(t *testing.T)      → unit test
  func BenchmarkXxx(b *testing.B) → performance
  func ExampleXxx()               → docs + test

PATTERN: Table-Driven Tests (MOST IDIOMATIC)
  tests := []struct{ in string; want bool }{ ... }
  for _, tt := range tests {
      if got := f(tt.in); got != tt.want {
          t.Errorf(...)
      }
  }

COMMANDS:
  go test -v          verbose
  go test -run Foo    filter by name
  go test -bench=.    benchmarks
  go test -cover      coverage
  go test -race       data races
```
