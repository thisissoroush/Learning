# Key Takeaways — Cracking the Coding Interview, 6th Edition

> Gayle Laakmann McDowell · CareerCup · 2015

---

## 🏆 The One Sentence

> **An interview is a test of how you think, not what you've memorized. Demonstrate your reasoning — out loud — at every step.**

---

## 🎯 The Universal 5-Step Process

```
1. LISTEN      → Every constraint is a hint.
2. EXAMPLE     → Specific, non-trivial, non-edge-case.
3. BRUTE FORCE → State the naive solution first.
4. OPTIMIZE    → Apply BUD. Know the BCR.
5. WALK THROUGH → Trace before you code.
```

## 🔧 BUD Optimization Framework

```
B — Bottlenecks:      slowest part — can it be faster?
U — Unnecessary work: work you could skip?
D — Duplicated work:  computing the same thing twice?
```

---

## 📊 Big O Rules Cold

| Rule | Example |
|------|---------|
| Drop constants | O(2n) = O(n) |
| Drop non-dominants | O(n² + n) = O(n²) |
| Multi-variable | Two arrays a, b → O(a × b), NOT O(n²) |
| Recursion | Draw call tree; nodes ≈ branches^depth |
| Amortized | ArrayList.add() = O(1) amortized |

---

## 🗂️ Data Structures — Right Tool

```
O(1) lookup / uniqueness    → HashSet / HashMap
Sorted, range queries       → TreeMap / BST
Priority (min or max)       → PriorityQueue (Heap)
Prefix string match         → Trie
LIFO / DFS / undo           → Stack (ArrayDeque)
FIFO / BFS / scheduling     → Queue (ArrayDeque)
Window max                  → Monotonic Deque
```

---

## ⚡ Top Optimization Patterns

| Problem Shape | O(n²) → O(n) Trick |
|---------------|---------------------|
| Pair sum/difference | HashSet: `seen.contains(target - x)` |
| Substring with constraint | Sliding window |
| Sorted array pair | Two pointers (L + R ends) |
| Repeated subproblem | Memoize → DP table |
| K smallest/largest | Heap of size K |
| String build in loop | `StringBuilder` not `+` |

---

## 🌳 Trees & Graphs Must-Know

```
In-order BST traversal   → sorted output
BFS (queue)              → shortest path, level-order
DFS (stack/recursion)    → cycles, topo sort, paths
Runner technique (LL)    → middle, kth-to-last, cycles
Floyd's cycle detect     → slow + fast pointers
Trie insert/search       → O(m) per word
```

---

## 💾 Recursion & DP Framework

```
Overlapping subproblems + optimal substructure → DP
Need ALL solutions → backtracking (prune early)

Top-down:  recursion + @cache → natural, easy to write
Bottom-up: iteration + table  → no call stack risk
Space opt: keep only last k rows of table
```

---

## 🏢 Company Strategies

| Company | Key Differentiator |
|---------|--------------------|
| Google | All rounds consistent — HC needs consensus |
| Amazon | Leadership Principles = equal weight to coding |
| Microsoft | Work independently, minimal hints |
| Apple | Passion for Apple products matters |
| Facebook | Show you ship; move fast |

---

## ⭐ Behavioral STAR Framework

```
S — Situation:  Brief context
T — Task:       Your specific responsibility
A — Action:     What YOU did (use "I", not "we")
R — Result:     Quantified outcome

Story library (5–7 stories):
  Most challenging technical problem
  Leadership without authority
  Conflict with teammate / manager
  A failure + what changed afterward
  Project you're most proud of
```

---

## 💀 Deadlock — 4 Conditions (break any one to prevent)

```
1. Mutual Exclusion   (one thread holds the resource)
2. Hold and Wait      (holds one lock, waits for another)
3. No Preemption      (can't force-take a resource)
4. Circular Wait      (A waits B, B waits A)

Prevention: enforce consistent lock ordering → breaks #4
```

---

## 🚫 Anti-Patterns

| Anti-Pattern | Fix |
|-------------|-----|
| Jump to code immediately | 5-step process first |
| Code silently | Think out loud always |
| Memorize solutions | Learn patterns, not answers |
| Skip edge cases | Always test null, empty, boundary |
| Give up on hard problems | Verbalize reasoning; partial credit exists |
| String `+` in loop | Use `StringBuilder` |
| `new Stack<>()` | Use `ArrayDeque` |

---

## 💡 Top 10 Principles

1. **Talk out loud** — silence is wasted signal
2. **Example first** — concrete before code
3. **Brute force is a start** — say it, then optimize
4. **Hash tables solve O(n²)** — "what if I cache this?"
5. **Sort first** — unlocks two-pointer and binary search
6. **Draw the call tree** — understand recursion complexity
7. **DP = recursion + cache** — repeated subproblems → memoize
8. **Lock ordering** — prevents deadlock
9. **Always test edge cases** — null, empty, max, min
10. **STAR for behavioral** — every story: S → T → A → R

---

*"Listen. Draw an example. State a brute force. Optimize. Walk through. Code. Test."*
