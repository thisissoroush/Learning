# Chapter 3 — Paradigm Overview

> *"Each of the paradigms removes capabilities from the programmer. None of them adds new capabilities."*

---

## 🎯 Core Concept

Since the 1940s, three programming paradigms have emerged. Each one **restricts** what programmers can do — removing a dangerous feature to impose discipline. No new paradigms have appeared in over 50 years, and none are likely to.

---

## 🧱 The Three Paradigms

```
┌──────────────────────────────────────────────────────────────┐
│  PARADIGM               DISCOVERED   DISCIPLINE IMPOSED       │
├──────────────────────────────────────────────────────────────┤
│  Structured Programming   1968        No unrestrained GOTO    │
│  Object-Oriented          1966        No direct function ptrs │
│  Functional               1958        No mutable assignment   │
└──────────────────────────────────────────────────────────────┘
```

### 1. Structured Programming (Dijkstra, 1968)
- Replaced `goto` with `if/then/else`, `do/while`, `until`
- **Imposes discipline on direct transfer of control**
- Enables functional decomposition and testability

### 2. Object-Oriented Programming (Dahl & Nygaard, 1966)
- Function call stack frames moved to the heap → classes, instances, methods
- Polymorphism through disciplined use of function pointers
- **Imposes discipline on indirect transfer of control**

### 3. Functional Programming (Church, 1936 / McCarthy, 1958)
- Based on λ-calculus — values do not change (immutability)
- Variables in functional languages *do not vary*
- **Imposes discipline on assignment**

---

## 🔍 The Pattern: Paradigms Take Things Away

```
Structured:  Took away ──────→ goto statements
OO:          Took away ──────→ function pointers (made safe)
Functional:  Took away ──────→ assignment / mutable state

The question: Is there anything left to take away?
The answer:   Probably not. These three are likely all we'll ever have.
```

All three were discovered between **1958 and 1968** — a single decade. In the 50+ years since, no new paradigm has emerged.

---

## 🏛️ Connection to Architecture

| Paradigm | Architectural Role |
|----------|--------------------|
| Structured | Foundation of algorithms — functional decomposition of modules |
| OO | Crossing architectural boundaries via polymorphism |
| Functional | Managing data location and access (immutability) |

These three paradigms align perfectly with the three concerns of architecture:
- **Function** (structured)
- **Separation of components** (OO)
- **Data management** (functional)

---

## 💡 Key Takeaways

- Paradigms constrain; they don't empower. That's the point.
- The discipline they impose is what makes software manageable.
- All three together remove: `goto`, unsafe function pointers, and mutable state.
- Architecture uses all three paradigms — not just OO.

---

*← [Back to Clean Architecture](../README.md)*
