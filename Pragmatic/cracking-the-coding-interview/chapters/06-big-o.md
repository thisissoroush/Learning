# Chapter VI — Big O

> *"Big O time is the metric we use to describe the efficiency of an algorithm. Not knowing it is like not knowing how fast your car goes."*  
> — Gayle Laakmann McDowell

---

## 🎯 Core Concept

Big O notation describes how an algorithm's runtime or memory usage **scales as the input grows**. It's the single most important theoretical tool in an interview. You can't analyze your solutions without it.

---

## 📐 The Complexity Classes — Visual

```
RUNTIME GROWTH COMPARISON (n = input size)
══════════════════════════════════════════════════════════════
  Class       n=10      n=100    n=1,000    n=10,000
  ──────────────────────────────────────────────────────────
  O(1)        1         1        1          1
  O(log n)    3         7        10         13
  O(n)        10        100      1,000      10,000
  O(n log n)  33        664      9,966      132,877
  O(n²)       100       10,000   1,000,000  100,000,000
  O(2ⁿ)       1,024     HUGE     ✗          ✗
  O(n!)       3,628,800 ✗        ✗          ✗
══════════════════════════════════════════════════════════════
  Goal: Stay at or below O(n log n) for large inputs.
```

---

## 📏 Big O Rules

### Rule 1: Drop Constants

```java
// O(2n) → we say O(n). Constants vanish at infinity.
for (int i = 0; i < n; i++) { doWork(); }
for (int i = 0; i < n; i++) { doMoreWork(); }
```

### Rule 2: Drop Non-Dominant Terms

```java
// O(n² + n) → O(n²)   |   O(n + log n) → O(n)
// Keep only the FASTEST-GROWING term.
```

### Rule 3: Multi-Variable Complexity

```java
// Two DIFFERENT inputs → two DIFFERENT variables!
void printPairs(int[] a, int[] b) {
    for (int x : a)          // O(a)
        for (int y : b)      // O(b)
            print(x, y);
}
// This is O(a × b) — NOT O(n²) unless a == b
```

---

## 🔑 Space Complexity

```java
// Time O(n), Space O(1) — no extra structures
int sum = 0;
for (int x : arr) sum += x;

// Time O(n), Space O(n) — new array allocated
int[] doubled = Arrays.copyOf(arr, arr.length);

// Recursion uses STACK SPACE:
// Time O(n), Space O(n) — n frames on the call stack
int factorial(int n) {
    return n == 0 ? 1 : n * factorial(n - 1);
}
```

---

## 🌳 Recursive Complexity — The Call Tree Method

```
fibonacci(4) call tree — branching factor 2, depth n:
                   fib(4)
                 /        \
            fib(3)        fib(2)
           /      \       /    \
       fib(2)  fib(1) fib(1) fib(0)
       /    \
   fib(1) fib(0)

Total nodes ≈ 2^n  →  Time: O(2^n)

With memoization: each unique value computed ONCE
→ Time: O(n), Space: O(n)

General Rule: b branches per level × depth d → O(b^d)
```

---

## 📊 Common Complexities Cheat Sheet

```
SORTING
  Bubble / Selection / Insertion:  O(n²) time, O(1) space
  Merge Sort:                      O(n log n) time, O(n) space
  Quick Sort:                      O(n log n) avg, O(n²) worst
  Heap Sort:                       O(n log n) time, O(1) space

DATA STRUCTURES (average case)
  Array unsorted:  Access O(1), Search O(n), Insert O(n)
  Array sorted:    Binary Search O(log n)
  Hash Table:      All operations O(1)  [worst: O(n)]
  Balanced BST:    All operations O(log n)
  Heap:            Insert O(log n), Peek-min O(1)
```

---

## ⚡ Amortized Analysis — ArrayList Example

```
ArrayList doubles when full. Copy counts per n inserts:
  1 + 2 + 4 + 8 + ... + n/2 + n = 2n total copies

Amortized cost = 2n / n = O(1) per insert.
This is why ArrayList.add() is O(1) amortized, not O(n).
```

---

## 🎯 When Does O(log n) Appear?

O(log n) appears whenever the **problem is halved** at each step:

```java
// Binary search — halve search space each iteration
int binarySearch(int[] arr, int target) {
    int lo = 0, hi = arr.length - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;  // avoid int overflow!
        if (arr[mid] == target) return mid;
        else if (arr[mid] < target) lo = mid + 1;
        else hi = mid - 1;
    }
    return -1;
}
// n=1,000,000 → at most 20 iterations (log₂(1,000,000) ≈ 20)
```

---

## 💡 Key Takeaways

| Concept | Rule |
|---------|------|
| Drop constants | O(2n) = O(n) |
| Drop non-dominants | O(n² + n) = O(n²) |
| Multi-variable | Different inputs = different variables (a × b ≠ n²) |
| Space complexity | Count recursion stack frames too |
| Recursive complexity | Draw call tree; nodes ≈ branches^depth |
| Amortized | Average cost over many ops (ArrayList.add = O(1)) |
| O(log n) | Appears when problem halves each step |
| Goal | O(n log n) or better for large n |

---

*[← Chapter V](05-behavioral-questions.md) | [Back to Index](../README.md) | [Chapter VII →](07-technical-questions.md)*
