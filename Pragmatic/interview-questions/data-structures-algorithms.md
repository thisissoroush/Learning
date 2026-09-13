# 📊 Data Structures & Algorithms — Interview Questions

Focus on reasoning about complexity and trade-offs, not LeetCode tricks.

---

### 1. What is Big-O notation and why does it matter?

**A:** Big-O describes how an algorithm's time or space requirements grow as input size (n) increases, in the worst case.

```
O(1)       — constant:    array access by index, hash map lookup
O(log n)   — logarithmic: binary search, balanced BST operations
O(n)       — linear:      linear scan, linked list traversal
O(n log n) — linearithmic: efficient sorting (merge sort, quick sort avg)
O(n²)      — quadratic:   nested loops, bubble sort
O(2ⁿ)      — exponential: recursive fibonacci, power set
O(n!)      — factorial:   permutations
```

**Why it matters:** An O(n²) algorithm with n=1,000,000 performs 10¹² operations — it will never finish. An O(n log n) performs ~20,000,000 — completes in seconds.

**Common misconception:** Big-O ignores constants. O(2n) = O(n). At small n, a "worse" algorithm may be faster in practice due to cache effects and constants.

---

### 2. What are arrays and when do you use them?

**A:**

```
Array: contiguous block of memory, fixed size, O(1) random access by index

Memory layout: [42][17][99][5][88]
                 0   1   2  3   4   ← index

Operations:
  Access by index: O(1)  ← best-in-class
  Search (unsorted): O(n)
  Search (sorted binary): O(log n)
  Insert at end: O(1) amortized (dynamic array)
  Insert at middle: O(n) — must shift elements
  Delete at middle: O(n) — must shift elements
```

**Use arrays when:** Random access by index is frequent, memory locality matters (cache-friendly), size is known or doesn't change often.

**Avoid arrays when:** Frequent insertions/deletions in the middle, size varies wildly.

---

### 3. What is a Linked List and when do you use it?

**A:**

```
Singly linked: [42|→] → [17|→] → [99|→] → [5|→] → null
                head                          tail

Doubly linked: null ← [42|↔] ↔ [17|↔] ↔ [99|↔] ↔ [5|→] → null

Operations:
  Insert at head/tail: O(1)
  Insert at middle (with pointer): O(1)
  Search: O(n) — no random access
  Access by index: O(n)
  Delete (with pointer): O(1)
```

**Use when:** Frequent insertions/deletions at head or tail (queue, stack), unknown or variable size, don't need random access.

**Avoid when:** Need random access, memory overhead of pointers matters, cache performance is critical (arrays have better locality).

---

### 4. What is a Hash Table and how does it work?

**A:**

```
Key → hash function → index → bucket

"alice" → hash → 3 → buckets[3] → [(alice, User{...})]

Collision resolution:
  Chaining: each bucket holds a linked list of collisions
  Open addressing: probe for next empty slot (linear, quadratic, double hashing)

Average case: O(1) for get, put, delete
Worst case: O(n) — all keys hash to same bucket
Load factor: n_elements / capacity → resize when > 0.75 (Java HashMap)
```

**Use when:** Need O(1) average lookup by key, frequency counting, deduplication, caching.

**Pitfalls:**
- Keys must be hashable and implement equals consistently
- Order is not preserved (use LinkedHashMap for insertion order)
- Hash collisions can degrade to O(n) — avoid poor hash functions

---

### 5. What is a Stack and what is a Queue?

**A:**

```
Stack — LIFO (Last In, First Out)
  push(x) → [3][2][1]  ← top
  pop()   ← returns 3
  peek()  ← returns 3 (no remove)

  Use: function call stack, undo/redo, expression parsing,
       DFS iteratively, balanced parentheses check

Queue — FIFO (First In, First Out)
  enqueue(x) → [1][2][3] → dequeue() returns 1
  Front                    Rear

  Use: BFS, task scheduling, rate limiting, producer/consumer,
       print spooler, message queues
```

```python
from collections import deque

# Stack
stack = []
stack.append(1)       # push
stack.append(2)
top = stack.pop()     # pop → 2

# Queue (deque is O(1) for both ends; list is O(n) for popleft)
queue = deque()
queue.append(1)       # enqueue
queue.append(2)
first = queue.popleft()  # dequeue → 1
```

---

### 6. What are Trees and what are their key variants?

**A:**

```
Binary Tree:
        8
       / \
      3   10
     / \    \
    1   6    14
       / \   /
      4   7 13

Binary Search Tree (BST): left < node < right
  Search: O(log n) average, O(n) worst (degenerate/unbalanced)

Balanced BST (AVL, Red-Black):
  Maintains balance → O(log n) guaranteed

Heap:
  Max-heap: parent ≥ children (root = maximum)
  Min-heap: parent ≤ children (root = minimum)
  get-min/max: O(1)
  insert: O(log n)
  extract-min/max: O(log n)
  Use: priority queue, heap sort, k-th largest element, Dijkstra

Trie:
  Tree of characters for string prefix lookup
  Search: O(m) where m = string length
  Use: autocomplete, spell checker, IP routing
```

---

### 7. What are Graphs and how do you represent them?

**A:**

```
Graph G = (V, E)
V = vertices (nodes)
E = edges (connections)

Types:
  Directed vs Undirected
  Weighted vs Unweighted
  Cyclic vs Acyclic (DAG = Directed Acyclic Graph)
  Dense vs Sparse

Representations:
  Adjacency Matrix: O(V²) space, O(1) edge lookup
    [0,1,1,0]
    [1,0,0,1]
    [1,0,0,1]
    [0,1,1,0]

  Adjacency List: O(V+E) space, O(degree) edge lookup — better for sparse
    0: [1, 2]
    1: [0, 3]
    2: [0, 3]
    3: [1, 2]
```

**Use adjacency list** for most problems (social networks, routing) — they're sparse.
**Use adjacency matrix** when density is high and O(1) edge lookup is needed.

---

### 8. What is BFS vs DFS?

**A:**

```
BFS (Breadth-First Search) — explores level by level using a Queue
  Start → neighbors → neighbors' neighbors → ...
  Finds SHORTEST PATH (unweighted graphs)
  Memory: O(width) — can be large for wide graphs

DFS (Depth-First Search) — goes deep first using a Stack (or recursion)
  Start → go as deep as possible → backtrack
  Finds IF path exists (not necessarily shortest)
  Memory: O(depth) — better for very wide graphs

          1
        /   \
       2     3
      / \   / \
     4   5 6   7

BFS order: 1, 2, 3, 4, 5, 6, 7  ← level by level
DFS order: 1, 2, 4, 5, 3, 6, 7  ← pre-order
```

```python
from collections import deque

def bfs(graph, start):
    visited, queue = {start}, deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

def dfs(graph, node, visited=None):
    if visited is None: visited = set()
    visited.add(node)
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited)
```

---

### 9. What are the most important sorting algorithms and their trade-offs?

**A:**

| Algorithm | Best | Average | Worst | Space | Stable? | Use when |
|-----------|------|---------|-------|-------|---------|----------|
| Bubble Sort | O(n) | O(n²) | O(n²) | O(1) | Yes | Never (educational only) |
| Selection Sort | O(n²) | O(n²) | O(n²) | O(1) | No | Minimizing writes |
| Insertion Sort | O(n) | O(n²) | O(n²) | O(1) | Yes | Small or nearly-sorted |
| Merge Sort | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes | Need stable, guaranteed O(n log n) |
| Quick Sort | O(n log n) | O(n log n) | O(n²) | O(log n) | No | General purpose, in-place |
| Heap Sort | O(n log n) | O(n log n) | O(n log n) | O(1) | No | In-place, guaranteed |
| Counting Sort | O(n+k) | O(n+k) | O(n+k) | O(k) | Yes | Small integer range |
| Radix Sort | O(nk) | O(nk) | O(nk) | O(n+k) | Yes | Large sets of integers/strings |

**Practical reality:** Most languages use Timsort (hybrid merge+insertion) for stability and O(n log n) guaranteed performance.

---

### 10. What is binary search and when can you use it?

**A:** Binary search finds a target in a **sorted** array in O(log n) by halving the search space each iteration.

```python
def binary_search(arr: list, target: int) -> int:
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2  # avoid integer overflow

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1   # target is in right half
        else:
            right = mid - 1  # target is in left half

    return -1  # not found

# PRECONDITION: array must be sorted
# Also applies to: search space with a monotonic property (not just sorted arrays)
# E.g., "find minimum X such that f(X) is true" — binary search on answer
```

**Generalized binary search:** Any problem where you can define a monotonic predicate (once true, always true as X increases) can use binary search.

---

### 11. What is recursion and what is the call stack limit?

**A:**

```python
def factorial(n: int) -> int:
    if n <= 1: return 1          # base case — stops recursion
    return n * factorial(n - 1)  # recursive case

# Call stack:
# factorial(5)
#   factorial(4)
#     factorial(3)
#       factorial(2)
#         factorial(1) → returns 1
#       returns 2
#     returns 6
#   returns 24
# returns 120
```

**Stack overflow:** Each recursive call uses stack frame memory. Default limit: ~1000 (Python), ~10000 (Java), ~500000 (Go). Deeply recursive code needs iteration or tail-call optimization.

**Tail recursion:** Some languages (Scala, Haskell, Kotlin) optimize tail calls (recursive call is last operation) into iteration.

```python
# Non-tail recursive: n * factorial(n-1) — must keep frame for multiplication
# Tail recursive: accumulator carries the result
def factorial_tail(n: int, acc: int = 1) -> int:
    if n <= 1: return acc
    return factorial_tail(n - 1, n * acc)  # Python doesn't optimize this, but conceptually TCO
```

---

### 12. What is dynamic programming?

**A:** Solve complex problems by breaking them into overlapping subproblems, solving each once, and storing results (memoization or tabulation).

```python
# Fibonacci — naive: O(2ⁿ), DP: O(n)

# Memoization (top-down) — recursive + cache
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n: int) -> int:
    if n <= 1: return n
    return fib(n-1) + fib(n-2)

# Tabulation (bottom-up) — iterative
def fib(n: int) -> int:
    if n <= 1: return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]

# Space-optimized — only need last two
def fib(n: int) -> int:
    a, b = 0, 1
    for _ in range(n): a, b = b, a + b
    return a
```

**When to use DP:** Problem has optimal substructure (optimal solution built from optimal sub-solutions) + overlapping subproblems (same subproblem solved multiple times).

---

### 13. What is a Heap and how do you implement a priority queue?

**A:**

```python
import heapq

# Python heapq is a min-heap
pq = []
heapq.heappush(pq, (3, "low priority task"))
heapq.heappush(pq, (1, "urgent task"))
heapq.heappush(pq, (2, "medium task"))

priority, task = heapq.heappop(pq)  # (1, "urgent task") — minimum first

# Max-heap — negate priorities
heapq.heappush(pq, (-priority, task))

# K largest elements in O(n log k)
import heapq
def k_largest(nums: list, k: int) -> list:
    return heapq.nlargest(k, nums)

# Heap sort
def heap_sort(arr):
    heapq.heapify(arr)      # O(n) — build heap
    return [heapq.heappop(arr) for _ in range(len(arr))]  # O(n log n)
```

**Heap internal structure:**
```
Min-heap:          1
                 /   \
                3     5
               / \   / \
              8   9 10  11
Stored as array: [1, 3, 5, 8, 9, 10, 11]
Parent of i: (i-1)//2
Left child:  2*i+1
Right child: 2*i+2
```

---

### 14. How do you reason about algorithm trade-offs in a real system?

**A:** This is the most important skill for senior engineers — algorithmic correctness is table stakes.

**Questions to ask:**
1. **What's n?** Algorithm complexity only matters at scale. For n=100, O(n²) is fine.
2. **What's the access pattern?** Lots of reads → hash map. Lots of range queries → sorted array or tree.
3. **Memory vs speed trade-off?** Can you cache? Is memory constrained?
4. **Is it in a hot path?** Premature optimization. Profile first.
5. **Data characteristics?** Nearly sorted → insertion sort wins. Random → quicksort wins.

```
Example: "How would you find duplicate files on disk?"

Naive: compare every pair — O(n²)
Better: hash each file content → group by hash → O(n)
Even better: first compare sizes (cheap I/O) → then hash only same-size files → fewer reads

The "best" algorithm depends on:
  - Disk I/O cost vs CPU cost
  - Expected number of duplicates
  - Whether files fit in memory
  - Network vs local storage
```
