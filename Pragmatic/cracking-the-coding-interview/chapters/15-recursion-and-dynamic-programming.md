# Chapter 8 — Recursion & Dynamic Programming

> *"Dynamic programming is just recursion with memoization. Once you see that, everything clicks."*  
> — Gayle Laakmann McDowell

---

## 🎯 Core Concept

Recursion breaks a problem into smaller versions of itself. Dynamic programming (DP) is recursion **plus caching** — so you never solve the same subproblem twice. Mastering these two techniques unlocks an enormous class of interview problems.

---

## 🔁 Recursion Fundamentals

Every recursive solution needs:
1. **Base case** — the stopping condition (no more recursion)
2. **Recursive case** — the problem expressed in terms of a smaller version of itself

```java
// Classic: Fibonacci
// Bad — O(2^n): recomputes fib(3) many times
int fib(int n) {
    if (n <= 1) return n;          // base case
    return fib(n-1) + fib(n-2);   // recursive case
}
```

```
fib(5) call tree (shows repeated work):
         fib(5)
        /      \
     fib(4)   fib(3)
     /    \   /    \
  fib(3) fib(2) fib(2) fib(1)
  ...
  fib(3) is computed TWICE. fib(2) THREE times. O(2^n) total.
```

---

## ⚡ Memoization — Top-Down DP

Cache the result of every subproblem so it's only computed once.

```java
// Fibonacci with memoization: O(n) time, O(n) space
int fib(int n, int[] memo) {
    if (n <= 1) return n;
    if (memo[n] != 0) return memo[n];   // cache hit!
    memo[n] = fib(n-1, memo) + fib(n-2, memo);
    return memo[n];
}
// Now fib(3) is computed ONCE and cached. O(n) calls total.
```

---

## 📋 Tabulation — Bottom-Up DP

Build the solution iteratively from the smallest subproblems up.

```java
// Fibonacci with tabulation: O(n) time, O(n) space
int fib(int n) {
    if (n <= 1) return n;
    int[] dp = new int[n + 1];
    dp[0] = 0; dp[1] = 1;
    for (int i = 2; i <= n; i++)
        dp[i] = dp[i-1] + dp[i-2];
    return dp[n];
}

// Space-optimized: O(1) space (only need last 2 values)
int fib(int n) {
    if (n <= 1) return n;
    int prev2 = 0, prev1 = 1;
    for (int i = 2; i <= n; i++) {
        int curr = prev1 + prev2;
        prev2 = prev1;
        prev1 = curr;
    }
    return prev1;
}
```

---

## 🪜 Classic DP Problem: Staircase

> How many ways to climb n stairs, taking 1 or 2 steps at a time?

```java
// Key insight: to reach step n, you came from n-1 or n-2.
// ways(n) = ways(n-1) + ways(n-2)  ← THIS IS FIBONACCI!

int climbStairs(int n) {
    if (n <= 2) return n;
    int[] dp = new int[n + 1];
    dp[1] = 1; dp[2] = 2;
    for (int i = 3; i <= n; i++)
        dp[i] = dp[i-1] + dp[i-2];
    return dp[n];
}
// Time: O(n), Space: O(n)  [or O(1) with prev/prev2 trick]
```

---

## 🎒 Classic DP Problem: 0/1 Knapsack

> n items with weights and values. Knapsack capacity W. Maximize value.

```java
// dp[i][w] = max value using first i items with capacity w
int knapsack(int[] weights, int[] values, int W) {
    int n = weights.length;
    int[][] dp = new int[n+1][W+1];

    for (int i = 1; i <= n; i++) {
        for (int w = 0; w <= W; w++) {
            // Skip item i (don't take it):
            dp[i][w] = dp[i-1][w];
            // Take item i (if it fits):
            if (weights[i-1] <= w)
                dp[i][w] = Math.max(dp[i][w],
                    dp[i-1][w - weights[i-1]] + values[i-1]);
        }
    }
    return dp[n][W];
}
// Time: O(n×W), Space: O(n×W)
```

---

## 🧩 Classic DP Problem: Longest Common Subsequence

```java
// LCS of "ABCBDAB" and "BDCAB" = "BCAB" (length 4)
int lcs(String s, String t) {
    int m = s.length(), n = t.length();
    int[][] dp = new int[m+1][n+1];

    for (int i = 1; i <= m; i++)
        for (int j = 1; j <= n; j++)
            if (s.charAt(i-1) == t.charAt(j-1))
                dp[i][j] = dp[i-1][j-1] + 1;     // chars match
            else
                dp[i][j] = Math.max(dp[i-1][j], dp[i][j-1]); // skip one
    return dp[m][n];
}
// Time: O(m×n), Space: O(m×n)
```

---

## 🗺️ When to Use DP — Recognition Pattern

```
A problem is likely DP when:
────────────────────────────────────────────────────────
  ✅ "How many ways to..."     (counting problems)
  ✅ "What is the maximum/minimum..."   (optimization)
  ✅ "Is it possible to..."    (feasibility)
  ✅ Subproblems OVERLAP       (same subproblem appears twice)
  ✅ Optimal substructure      (optimal solution uses optimal
                                solutions of subproblems)

NOT DP (just recursion / divide & conquer):
  ❌ Merge sort — subproblems DON'T overlap
  ❌ Binary search — single subproblem at each step
────────────────────────────────────────────────────────
```

---

## 🔑 Backtracking — Generate All Solutions

When you need all solutions (not just the optimal one):

```java
// Generate all permutations of an array
void permute(int[] nums, int start, List<List<Integer>> result) {
    if (start == nums.length) {
        // Base case: add current permutation to results
        List<Integer> perm = new ArrayList<>();
        for (int n : nums) perm.add(n);
        result.add(perm);
        return;
    }
    for (int i = start; i < nums.length; i++) {
        swap(nums, start, i);             // choose
        permute(nums, start + 1, result); // explore
        swap(nums, start, i);             // un-choose (backtrack)
    }
}
// Time: O(n!), Space: O(n) call stack
```

---

## 💡 Key Takeaways

| Technique | When to Use | Complexity Gain |
|-----------|-------------|-----------------|
| Memoization (top-down) | Natural recursive structure with overlapping subproblems | O(2^n) → O(n) |
| Tabulation (bottom-up) | When you need all subproblem values anyway | Same as memo, less stack |
| Space optimization | When only last k rows of dp table needed | O(n²) space → O(n) |
| Backtracking | When you need ALL solutions, not just optimal | Prune bad branches early |
| DP recognition | Overlapping subproblems + optimal substructure | — |

---

*[← Chapter 7](14-object-oriented-design.md) | [Back to Index](../README.md) | [Chapter 9 — System Design →](16-system-design-and-scalability.md)*
