# Chapter 10: Packages and the Go Tool

> *"A package is the unit of code reuse, compilation, and encapsulation in Go."*

---

## Core Concept

Packages are Go's modularity system. Every Go file belongs to a package. The `go` tool handles building, testing, formatting, and dependency management.

---

## 10.1 Package Basics

```go
// Every file declares its package
package geometry

// Package-level names starting with uppercase = exported (public)
// lowercase = unexported (private to the package)

func Distance(p, q Point) float64 { ... }  // exported
func helper() { ... }                       // unexported
```

---

## 10.2 Import Paths

```go
import (
    "fmt"                          // standard library
    "math/rand"                    // sub-package
    "golang.org/x/net/html"       // external package
    "github.com/user/repo/pkg"    // GitHub package
    "myapp/internal/config"       // internal package
)

// Import with alias
import (
    myfmt "fmt"
    . "math"   // dot import: use Sin() instead of math.Sin()
    _ "image/png"  // blank import: side-effects only (init())
)
```

---

## 10.3 Package Declaration Rules

```
Rule: package name = last segment of import path
  import "encoding/json"  →  package json

Exceptions:
  main    — standalone executable (not a library)
  _test   — external test package suffix (testing only)
```

---

## 10.4 Package Initialization

```go
// Variables initialized in dependency order
var a = b + c   // initialized 3rd
var b = f()     // initialized 2nd
var c = 1       // initialized 1st

// init() runs automatically after all variable initializations
func init() {
    // runs once per package, multiple init()s allowed
    // called in order of appearance
}
```

```
Initialization order:
  1. Package-level vars (in dependency order)
  2. init() functions (in source order)
  3. main() (only in main package)

  Imported packages are initialized FIRST.
```

---

## 10.5 The `go` Tool — Essential Commands

```bash
# Build & Run
go build ./...          # compile packages
go run main.go          # compile and run
go install              # build + install to $GOPATH/bin

# Dependencies
go get github.com/pkg   # download and install
go mod init myapp       # create go.mod
go mod tidy             # add missing, remove unused deps

# Testing
go test ./...           # run all tests
go test -v              # verbose output
go test -run TestFoo    # run specific test
go test -race           # race detector
go test -bench=.        # run benchmarks
go test -cover          # show coverage
go test -coverprofile=c.out && go tool cover -html=c.out

# Code Quality
go fmt ./...            # format code (run this always!)
go vet ./...            # find suspicious code
go doc fmt.Println      # show documentation
go doc -all fmt         # all docs for package

# Inspection
go list ./...           # list packages
go list -json .         # package metadata as JSON
go env                  # show Go environment
go version              # show Go version
```

---

## 10.6 Package Naming Conventions

```go
// Good package names: short, lowercase, no underscores
package strings   // not: string_utils
package http      // not: httpUtils
package io        // not: inputOutput

// Naming exported things: don't repeat the package name
// BAD:  strings.StringReader
// GOOD: strings.Reader       (used as strings.Reader)

// BAD:  http.HTTPServer
// GOOD: http.Server          (used as http.Server)
```

---

## 10.7 Module System (go.mod)

```
myapp/
  go.mod         ← module definition
  go.sum         ← dependency checksums
  main.go
  pkg/
    ...
```

```go
// go.mod example
module github.com/myuser/myapp

go 1.21

require (
    github.com/gorilla/mux v1.8.0
    golang.org/x/net v0.17.0
)
```

---

## Visual Summary

```
PACKAGE SYSTEM
═══════════════════════════════════════════════

Package = unit of modularity + encapsulation
  Exported:   Uppercase names → visible outside package
  Unexported: lowercase names → package-private

import path: "encoding/json"
package name: json
usage: json.Marshal(...)

WORKSPACE STRUCTURE:
  $GOPATH/
    src/   (legacy, pre-modules)
    bin/   (compiled binaries)
    pkg/   (compiled packages)

  go.mod based (modern, recommended):
    module myapp
    go 1.21
    require ( ... )

KEY COMMANDS:
  go build   compile
  go run     compile + run
  go test    run tests
  go fmt     format code ← ALWAYS DO THIS
  go vet     static analysis
  go get     fetch dependency
  go mod     module management
```
