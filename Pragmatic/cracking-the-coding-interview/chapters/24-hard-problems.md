# Chapter 17 — Hard Problems

> *"Hard problems require you to combine insights from multiple areas. Don't panic — break it down and trust the process."*  
> — Gayle Laakmann McDowell

---

## 🎯 Core Concept

Hard problems rarely have an obvious approach — they require creative insight, clever data structure choice, or a non-obvious reduction. This chapter covers the **thinking frameworks** and representative techniques behind the hardest difficulty tier.

---

## 🏆 Pattern 1: Add Without Plus (Bit Manipulation)

```java
// Add two integers without + operator.
// XOR = sum without carry | AND << 1 = carry bits
int add(int a, int b) {
    while (b != 0) {
        int carry = (a & b) << 1;  // carry: common 1-bits shifted left
        a = a ^ b;                 // sum: different bits only
        b = carry;                 // loop until no more carry
    }
    return a;
}
// Each iteration: one more carry bit resolves → terminates in O(bits)
```

---

## 🌊 Pattern 2: Trapping Rain Water

```java
// [0,1,0,2,1,0,1,3,2,1,2,1] → 6 units of water
// Water at i = min(maxLeft[i], maxRight[i]) - height[i]

int trap(int[] h) {
    int n = h.length;
    int[] L = new int[n], R = new int[n];
    L[0] = h[0];
    for (int i = 1; i < n; i++) L[i] = Math.max(L[i-1], h[i]);
    R[n-1] = h[n-1];
    for (int i = n-2; i >= 0; i--) R[i] = Math.max(R[i+1], h[i]);
    int water = 0;
    for (int i = 0; i < n; i++) water += Math.min(L[i], R[i]) - h[i];
    return water;
}
// Time: O(n), Space: O(n)  [can reduce to O(1) with two pointers]
```

---

## 📐 Pattern 3: Sliding Window Maximum

```java
// Max value in every window of size k. Naive: O(nk). Optimal: O(n).
// KEY: Monotonic deque of indices — always decreasing values.

int[] maxSlidingWindow(int[] nums, int k) {
    Deque<Integer> dq = new ArrayDeque<>();
    int[] res = new int[nums.length - k + 1];
    for (int i = 0; i < nums.length; i++) {
        // Remove out-of-window indices
        while (!dq.isEmpty() && dq.peekFirst() < i - k + 1)
            dq.pollFirst();
        // Remove smaller elements (they'll never be the max)
        while (!dq.isEmpty() && nums[dq.peekLast()] < nums[i])
            dq.pollLast();
        dq.offerLast(i);
        if (i >= k - 1) res[i - k + 1] = nums[dq.peekFirst()];
    }
    return res;
}
// Each element enters and leaves deque once → O(n) total
```

---

## 🎯 Pattern 4: Shortest Supersequence

```java
// Shortest subarray of big[] containing ALL elements of small[].
// Sliding window + "have" counter (same as minimum window substring).

// Template:
int left = 0, have = 0;
int[] best = {0, Integer.MAX_VALUE};
for (int right = 0; right < big.length; right++) {
    // expand window: add big[right], update have if needed
    while (have == needed.size()) {
        // record best, shrink from left
    }
}
// Time: O(b + s)  where b = big.length, s = small.length
```

---

## 🔑 Hard Problem Thinking Framework

```
WHEN STUCK — ask yourself in order:
───────────────────────────────────────────────────────
  1. SIMPLIFY:     Solve n=1, n=2, n=3. Pattern emerges.

  2. DATA STRUCTURE:
     "What if I use a heap / deque / trie / segment tree?"
     Right structure often drops O(n²) → O(n log n).

  3. PRECOMPUTE:
     "Can I build prefix/suffix arrays for O(1) queries?"
     Precompute once, answer queries cheaply.

  4. DIVIDE & CONQUER:
     "Solve left half + right half + merge cleverly?"
     Merge step is often where the insight lives.

  5. BIT MANIPULATION:
     "Can I encode state as bits?"
     XOR for unique/paired, AND/OR for masks.

  6. MATH INSIGHT:
     "Is there a formula I'm missing?"
     Pigeonhole, modular arithmetic, sum of 1..n.
───────────────────────────────────────────────────────
```

---

## 💡 Key Takeaways

| Problem | Technique | Complexity |
|---------|-----------|------------|
| Add without + | XOR (sum bits) + AND<<1 (carry bits), iterate | O(bits) |
| Trapping rain water | Precompute maxLeft + maxRight arrays | O(n) |
| Sliding window max | Monotonic deque — decreasing value order | O(n) |
| Shortest supersequence | Sliding window + "have" counter | O(n + m) |
| Count smaller after self | Modified merge sort OR Fenwick tree | O(n log n) |
| Hard problems generally | Simplify → right structure → precompute → divide | — |

---

*[← Chapter 16](23-moderate-problems.md) | [Back to Index](../README.md)*
