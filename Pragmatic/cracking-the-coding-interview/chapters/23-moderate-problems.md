# Chapter 16 — Moderate Problems

> *"Moderate problems test whether you can combine multiple techniques. The solution is rarely just one trick — it's two or three layered together."*  
> — Gayle Laakmann McDowell

---

## 🎯 Core Concept

Chapter 16 contains 26 "moderate" difficulty problems. Rather than summarizing all 26, this chapter covers the **core techniques and representative problems** that teach the thinking patterns behind this difficulty tier.

---

## 🧩 Pattern 1: Number Swapping Without Temp

```java
// Swap a and b without a temporary variable

// XOR method:
a = a ^ b;
b = a ^ b;  // b = (a^b)^b = a
a = a ^ b;  // a = (a^b)^a = b

// Arithmetic method (can overflow!):
a = a + b;
b = a - b;  // b = (a+b) - b = a
a = a - b;  // a = (a+b) - a = b

// ⚠️ These are clever but impractical — always ask WHY before using.
// In real code: use a temp variable. Clarity beats cleverness.
```

---

## 🎯 Pattern 2: English Integer (Number to Words)

Convert 1,234,567 → "One Million Two Hundred Thirty Four Thousand Five Hundred Sixty Seven"

```java
// Key insight: decompose into groups of 3 digits (thousands groups)
// 1,234,567 → [1][234][567]
// Apply hundreds/tens/ones logic to each group, append suffix.

String[] BELOW_20 = {"", "One", "Two", ..., "Nineteen"};
String[] TENS = {"", "", "Twenty", "Thirty", ..., "Ninety"};
String[] THOUSANDS = {"", "Thousand", "Million", "Billion"};

String numberToWords(int n) {
    if (n == 0) return "Zero";
    String result = "";
    int i = 0;
    while (n > 0) {
        if (n % 1000 != 0)
            result = helper(n % 1000) + THOUSANDS[i] + " " + result;
        n /= 1000;
        i++;
    }
    return result.trim();
}
// Time: O(log n) — one pass per group of 3 digits
```

---

## ⭕ Pattern 3: Smallest Difference Between Two Arrays

```java
// Find pair (a from array1, b from array2) with minimum |a - b|
// Brute force: O(n²) — check all pairs

// Optimal: sort both arrays, use two pointers
int smallestDifference(int[] arr1, int[] arr2) {
    Arrays.sort(arr1);
    Arrays.sort(arr2);
    int i = 0, j = 0, minDiff = Integer.MAX_VALUE;
    while (i < arr1.length && j < arr2.length) {
        minDiff = Math.min(minDiff, Math.abs(arr1[i] - arr2[j]));
        // Advance the pointer with smaller value
        if (arr1[i] < arr2[j]) i++;
        else j++;
    }
    return minDiff;
}
// Time: O(n log n + m log m) for sorting, O(n + m) for scan
```

---

## 🎲 Pattern 4: The Shuffle (Fisher-Yates)

```java
// Generate a uniformly random shuffle of an array
// (Each permutation must be equally likely)
void shuffle(int[] arr) {
    Random rand = new Random();
    for (int i = arr.length - 1; i > 0; i--) {
        // Pick random index from [0..i] and swap with i
        int j = rand.nextInt(i + 1);
        swap(arr, i, j);
    }
}
// Time: O(n)
// KEY: rand.nextInt(i+1) includes i itself
// Every permutation has equal probability 1/n!
```

---

## 📐 Pattern 5: Line Intersection

```java
// Do two line segments intersect?
// Key: handle parallel lines and endpoint cases separately.

// A line: y = mx + b (slope-intercept form)
// Special case: vertical lines (infinite slope) → x = c

// Two lines intersect at:
//   m1*x + b1 = m2*x + b2
//   x = (b2 - b1) / (m1 - m2)
// If m1 == m2 (parallel): no intersection (or infinite if same line)

// Then check: is x within both segments' x-ranges?
// (and handle vertical segments by checking y-ranges)
```

---

## 🗄️ Pattern 6: Contiguous Sequence (Max Sum Subarray)

```java
// Kadane's algorithm — classic moderate problem
// Find contiguous subarray with maximum sum.
// [-2, 1, -3, 4, -1, 2, 1, -5, 4] → 6  ([4,-1,2,1])

int maxSubarraySum(int[] arr) {
    int maxSum = arr[0];
    int currentSum = arr[0];

    for (int i = 1; i < arr.length; i++) {
        // Either extend current subarray, or start new one here
        currentSum = Math.max(arr[i], currentSum + arr[i]);
        maxSum = Math.max(maxSum, currentSum);
    }
    return maxSum;
}
// Time: O(n), Space: O(1)
// KEY INSIGHT: If currentSum goes negative, start fresh.
```

---

## 🔑 Common Moderate Problem Patterns

```
PATTERN                          TECHNIQUE
────────────────────────────────────────────────────────
Two arrays, find closest pair    Sort both + two pointers
Find duplicates in array         HashMap frequency count OR
                                 sort + adjacent comparison
Max/min subarray                 Kadane's algorithm
Circular array                   Treat as length 2n array
Geometric (lines, points)        Careful edge case analysis
Random selection                 Fisher-Yates shuffle
Number formatting                Groups of 3 + suffix tables
Palindrome partitioning          DP: precompute isPalin[i][j]
Pattern matching                 KMP or rabin-karp
Histogram problems               Stack-based approach
```

---

## 💡 Key Takeaways

| Problem Type | Key Insight |
|-------------|------------|
| Closest pair across two arrays | Sort + two pointers: O(n log n) |
| Max subarray | Kadane's: extend or restart; O(n) |
| Fair shuffle | Fisher-Yates: swap backwards, O(n) |
| Number to words | Decompose into groups of 3, apply suffix |
| Moderate tier generally | Combine 2–3 techniques; always ask "what if I sort first?" |

---

*[← Chapter 15](22-threads-and-locks.md) | [Back to Index](../README.md) | [Chapter 17 — Hard Problems →](24-hard-problems.md)*
