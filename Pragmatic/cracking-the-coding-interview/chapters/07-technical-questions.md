# Chapter VII — Technical Questions

> *"The worst thing you can do in a technical interview is jump straight to coding. The best thing you can do is think before you type."*  
> — Gayle Laakmann McDowell

---

## 🎯 Core Concept

This chapter is the **operating manual for every coding question** in the book. Before covering a single data structure, Gayle teaches you the universal 5-step process for approaching technical problems — a process that applies to every question from Easy to Hard.

---

## 🔢 The 5-Step Problem-Solving Process

```
STEP 1: LISTEN carefully
   → Every word in the problem is there for a reason.
   → "sorted array" means binary search is probably useful.
   → "unique elements" means a hash set probably helps.
   → Ask about edge cases: empty input? negatives? duplicates?

STEP 2: DRAW AN EXAMPLE
   → Use a SPECIFIC, reasonably-sized, non-special-case example.
   → Bad example:  arr = [1, 2]  (too small, hides patterns)
   → Good example: arr = [1, 5, 3, 8, 2, 9, 4, 7] (8 elements)

STEP 3: STATE A BRUTE FORCE SOLUTION
   → Say it out loud. Don't code it.
   → "The naive approach is O(n²) — for each element,
      scan the rest of the array for a match."
   → This proves you can solve it. Now optimize.

STEP 4: OPTIMIZE
   → Walk through the BUD framework (see below).
   → Think through time/space trade-offs.
   → Pick the approach you're most confident implementing.

STEP 5: WALK THROUGH the algorithm BEFORE CODING
   → Re-read your example. Mentally run the algorithm.
   → Catch bugs BEFORE they're in code (much easier!).
   → THEN open your editor / pick up the marker.
```

---

## 🔧 The BUD Framework for Optimization

```
BUD = Bottlenecks · Unnecessary Work · Duplicated Work

BOTTLENECKS:
  Find the slowest part and ask: can this be faster?
  "My sort is O(n log n) but I'm searching O(n) — can I
   preprocess to make search O(1)?"

UNNECESSARY WORK:
  Are you doing work you don't need to do?
  "I'm scanning the full array, but I could stop early
   once I find a match."

DUPLICATED WORK:
  Are you computing the same thing twice?
  "I'm recomputing the sum of subarrays — I should use
   a prefix sum array instead."
```

---

## 🗺️ Best Conceivable Runtime (BCR)

Before optimizing, ask: **what's the best possible runtime for this problem?**

```
EXAMPLES OF BCR REASONING:
─────────────────────────────────────────────────────────
  Problem: Find all pairs that sum to a target.
  BCR: O(n) — you must at least read every element once.

  Problem: Sort an array.
  BCR: O(n log n) — proven lower bound for comparison sorts.

  Problem: Find element in sorted array.
  BCR: O(log n) — binary search is optimal.

  WHY BCR MATTERS:
  If your current solution is O(n log n) and BCR is O(n log n),
  stop optimizing and start coding. You're already optimal.

  If BCR is O(n) and you have O(n²), there's room to improve.
```

---

## 🛠️ Space/Time Trade-offs — The Hash Table Pattern

The single most powerful optimization technique in interviews:

```java
// PROBLEM: Find if any two elements sum to target.

// Brute Force: O(n²) time, O(1) space
for (int i = 0; i < arr.length; i++)
    for (int j = i+1; j < arr.length; j++)
        if (arr[i] + arr[j] == target) return true;

// OPTIMIZED: O(n) time, O(n) space — trade space for time
Set<Integer> seen = new HashSet<>();
for (int x : arr) {
    if (seen.contains(target - x)) return true;
    seen.add(x);
}
// Key insight: "Have I seen the complement?" → O(1) lookup
```

---

## ✍️ Writing the Actual Code

```
CODE QUALITY RULES (what interviewers look for):
──────────────────────────────────────────────────────────
  ✅ Modular: Break into helper functions
  ✅ Error checking: Handle null, empty, edge cases
  ✅ Good variable names: "leftIndex" not "i2"
  ✅ Avoid magic numbers: constants or named variables
  ✅ DRY: Don't repeat the same logic twice

  Write the HAPPY PATH first, then add edge cases.
  Say out loud: "I'll handle the null case in a moment."
──────────────────────────────────────────────────────────
```

---

## 🐛 Testing Your Code — In the Interview

After writing your solution, **always test it before saying "I'm done"**:

```
TEST SEQUENCE:
  1. Trace through your specific example from Step 2
  2. Test edge cases:
     → Empty input (arr = [])
     → Single element (arr = [5])
     → All same elements (arr = [3, 3, 3])
     → Already sorted / reverse sorted
     → Negative numbers (if applicable)
  3. Look for off-by-one errors in loops
  4. Check for null pointer dereferences
```

---

## 🧠 Optimize & Solve Techniques

```
TECHNIQUE 1: Look for BUD (described above)
TECHNIQUE 2: DIY — solve it manually, then generalize
  "How would a human do this without code?"
  Humans often naturally use the optimal algorithm.

TECHNIQUE 3: Simplify and Generalize
  Solve a simpler version first.
  "What if I only needed to find ONE pair instead of all?"

TECHNIQUE 4: Base Case and Build
  Solve for n=1. Then n=2. Then n=3. Pattern emerges.
  Often leads to recursive + DP solutions naturally.

TECHNIQUE 5: Data Structure Brainstorm
  Run through your toolkit: hash table? tree? stack? heap?
  "What if I used a heap here?"
```

---

## 💡 Key Takeaways

| Step | What to Do |
|------|-----------|
| Listen | Every constraint in the problem is a hint |
| Example | Specific, non-trivial, non-edge-case |
| Brute force | State it before optimizing — proves you can solve it |
| Optimize | Use BUD: Bottlenecks, Unnecessary work, Duplicated work |
| BCR | Know the theoretical best — stop when you reach it |
| Space/time | Hash tables trade O(n) space for O(1) lookup repeatedly |
| Write code | Modular, named variables, edge cases explicitly noted |
| Test | Always trace your example + edge cases before saying "done" |

---

*[← Chapter VI](06-big-o.md) | [Back to Index](../README.md) | [Chapter 1 — Arrays & Strings →](08-arrays-and-strings.md)*
