# Chapter 4 — Structured Programming

> *"Testing shows the presence, not the absence, of bugs." — Dijkstra*

---

## 🎯 Core Concept

Dijkstra proved that `goto` prevents programs from being decomposed into provable units. Replacing `goto` with `if/then/else` and `do/while` makes programs testable. Software is like science — we prove correctness by failing to prove incorrectness.

---

## 🧪 The Proof Approach

Dijkstra wanted to apply mathematical proofs to programs. He discovered:
- Programs using only **sequence**, **selection**, **iteration** can be recursively decomposed
- These decomposed units can be individually proven correct
- `goto` breaks this decomposability

```
Three control structures (Böhm & Jacopini, proven 1966):
  1. Sequence   — one statement after another
  2. Selection  — if/then/else
  3. Iteration  — do/while, for

All programs can be built from JUST these three.
```

---

## 🔬 Science, Not Math

Math proves things **true**. Science proves things **false**.

```
Mathematical proof:  You can prove a theorem is correct
Scientific method:   You fail to prove something is incorrect,
                     then deem it "true enough"

Software testing:    We CANNOT prove a program correct.
                     We can only fail to prove it incorrect.
```

> "A program can be proven incorrect by a test, but it cannot be proven correct."

This means: tests that **fail to find bugs** give us confidence — but never certainty.

---

## 🗂️ Functional Decomposition

Structured programming enables:
- Breaking large problems into high-level functions
- Breaking those into lower-level functions (recursively)
- Each function is small enough to be tested individually

```
System
  └── Module A
        ├── Function A1
        │     ├── Function A1a  ← individually testable
        │     └── Function A1b  ← individually testable
        └── Function A2
```

This is why **functional decomposition** remains a best practice — it creates testable, falsifiable units.

---

## 💡 Key Takeaways

- `goto` is harmful because it prevents provable decomposition
- All programs = sequence + selection + iteration
- Software correctness is proven by failing to prove incorrectness (scientific method)
- Structured programming's legacy: testable units at every level of architecture

---

*← [Back to Clean Architecture](../README.md)*
