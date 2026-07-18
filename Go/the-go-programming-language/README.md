# The Go Programming Language
### by Alan A. A. Donovan & Brian W. Kernighan

> *"Go is an open source programming language that makes it easy to build simple, reliable, and efficient software."*

---

## Why Go?

Go was conceived in 2007 at Google by Robert Griesemer, Rob Pike, and Ken Thompson — the same people behind Unix and UTF-8. It was built out of frustration with complexity in large software systems.

**Go's philosophy:** *Simplicity is the key to good software.* Complexity is multiplicative — fixing one part by making it more complex slowly adds complexity everywhere else.

---

## What Makes Go Different?

| Feature | Go's Approach |
|---|---|
| Object-Oriented | No classes or inheritance — uses **composition** |
| Concurrency | Built-in **goroutines** and **channels** (CSP model) |
| Memory | **Garbage collected** — no malloc/free |
| Typing | **Statically typed** but feels lightweight |
| Interfaces | **Implicit** satisfaction — no `implements` keyword |
| Error Handling | **Explicit** return values — no exceptions |

---

## Chapters

| # | Chapter | Core Topic |
|---|---|---|
| 1 | [Tutorial](./chapters/01-tutorial.md) | First programs, CLI args, HTTP, concurrency taste |
| 2 | [Program Structure](./chapters/02-program-structure.md) | Names, declarations, variables, scope |
| 3 | [Basic Data Types](./chapters/03-basic-data-types.md) | Integers, floats, strings, constants |
| 4 | [Composite Types](./chapters/04-composite-types.md) | Arrays, slices, maps, structs, JSON |
| 5 | [Functions](./chapters/05-functions.md) | Closures, recursion, defer, panic, recover |
| 6 | [Methods](./chapters/06-methods.md) | Pointer receivers, embedding, encapsulation |
| 7 | [Interfaces](./chapters/07-interfaces.md) | Contracts, type assertions, type switches |
| 8 | [Goroutines & Channels](./chapters/08-goroutines-and-channels.md) | CSP, select, pipelines, cancellation |
| 9 | [Concurrency with Shared Variables](./chapters/09-concurrency-with-shared-variables.md) | Mutex, race conditions, sync |
| 10 | [Packages & the Go Tool](./chapters/10-packages-and-the-go-tool.md) | Modules, imports, go build/test |
| 11 | [Testing](./chapters/11-testing.md) | go test, benchmarks, coverage |
| 12 | [Reflection](./chapters/12-reflection.md) | reflect package, dynamic inspection |
| 13 | [Low-Level Programming](./chapters/13-low-level-programming.md) | unsafe, cgo |

---

## Go's Family Tree

```
Algol/Pascal family          C family
       │                        │
    Modula-2                    C
       │                        │
    Oberon ──────────────────► Go ◄─── CSP (Hoare 1978)
       │                        │         │
    Object Oberon           concurrency   Squeak → Newsqueak → Alef
                             features
```

Go inherits:
- **From C**: expression syntax, control flow, basic data types, pointers, efficiency
- **From Oberon/Pascal**: package system, imports, declarations  
- **From CSP**: goroutines, channels (communicate by sharing, don't share memory to communicate)
