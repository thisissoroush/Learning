# Chapter 1 — Arrays & Strings

> *"Arrays and strings are the foundation of almost every interview question. Master them first."*  
> — Gayle Laakmann McDowell

---

## 🎯 Core Concept

Arrays and strings are the most fundamental data structures in interviews. The techniques in this chapter — **hash tables, two pointers, sliding window, and StringBuilder** — appear in solutions to hundreds of problems. You will use them constantly.

---

## 🗂️ Hash Tables — The Most Powerful Interview Tool

A hash table maps keys to values in **O(1)** average time for insert, delete, and lookup. The most common optimization pattern in interviews is: *"Can I trade O(n) space for O(1) lookups?"*

```
HASH TABLE INTERNALS
──────────────────────────────────────────────────────────
  Key → hash function → bucket index → value

  Collision handling:
  ① Chaining: each bucket holds a linked list
  ② Open addressing: probe for next empty slot

  Average: O(1) for get/put/remove
  Worst:   O(n) if all keys hash to same bucket
──────────────────────────────────────────────────────────

Java implementation:
  HashMap<K,V>     → general key-value storage
  HashSet<K>       → fast existence checks
  LinkedHashMap    → preserves insertion order
  TreeMap          → sorted keys (O(log n) operations)
```

### Example: First Non-Repeating Character

```java
// Problem: Find first non-repeated character in a string.
// "abcadb" → 'c'  (appears once; a,b,d repeat)

char firstNonRepeating(String s) {
    // Pass 1: Count frequency of each character
    Map<Character, Integer> freq = new LinkedHashMap<>();
    for (char c : s.toCharArray())
        freq.merge(c, 1, Integer::sum);

    // Pass 2: Find first with count == 1
    for (Map.Entry<Character, Integer> e : freq.entrySet())
        if (e.getValue() == 1) return e.getKey();

    return '\0'; // no unique character
}
// Time: O(n), Space: O(1) — at most 26 distinct letters
```

---

## 🔡 StringBuilder — Why String Concatenation Kills You

```java
// ❌ WRONG: O(n²) time — creates new string each iteration
String joinWords(String[] words) {
    String result = "";
    for (String w : words) result += w; // copies entire string!
    return result;
}
// For n words of length n: total copies = n + 2n + 3n + ... = O(n²)

// ✅ CORRECT: O(n) time — amortized O(1) append
String joinWords(String[] words) {
    StringBuilder sb = new StringBuilder();
    for (String w : words) sb.append(w);
    return sb.toString();
}
```

---

## 👉 Two Pointers — The Classic Array Technique

Use two pointers (left/right) to avoid nested loops.

```java
// Problem: Two Sum (sorted array)
// Find indices of two numbers that add to target.
// [2, 7, 11, 15], target=9 → [0, 1]

int[] twoSum(int[] sorted, int target) {
    int left = 0, right = sorted.length - 1;
    while (left < right) {
        int sum = sorted[left] + sorted[right];
        if (sum == target) return new int[]{left, right};
        else if (sum < target) left++;   // need bigger sum
        else right--;                    // need smaller sum
    }
    return new int[]{};
}
// Time: O(n), Space: O(1) — vs O(n²) brute force
```

---

## 🪟 Sliding Window — For Substring/Subarray Problems

```java
// Problem: Longest substring without repeating characters.
// "abcabcbb" → 3 ("abc")

int lengthOfLongestSubstring(String s) {
    Set<Character> window = new HashSet<>();
    int left = 0, maxLen = 0;

    for (int right = 0; right < s.length(); right++) {
        // Shrink window from left until no duplicate
        while (window.contains(s.charAt(right)))
            window.remove(s.charAt(left++));

        window.add(s.charAt(right));
        maxLen = Math.max(maxLen, right - left + 1);
    }
    return maxLen;
}
// Time: O(n), Space: O(min(n, alphabet))
```

---

## 🔑 Key Interview Patterns

```
PATTERN 1: Is it a permutation? → Sort both, compare. Or
            count char frequencies, compare maps.

PATTERN 2: Are all chars unique? → Use boolean[256] or
            HashSet. If more chars than alphabet size → no.

PATTERN 3: Palindrome check → Two pointers from ends.
            Or reverse string and compare.

PATTERN 4: Anagram → Sort and compare, or frequency map.

PATTERN 5: String rotation → Check if s2 is substring
            of s1+s1. "rotation" in "rotationrotation"? YES.
```

### Example: Is Permutation?

```java
// Two strings are permutations of each other if they
// have the same characters in any order.
// "abc" and "bca" → true

boolean isPermutation(String a, String b) {
    if (a.length() != b.length()) return false;

    int[] counts = new int[128]; // ASCII
    for (char c : a.toCharArray()) counts[c]++;
    for (char c : b.toCharArray()) {
        if (--counts[c] < 0) return false;
    }
    return true;
}
// Time: O(n), Space: O(1) — fixed-size array
```

---

## 💡 Key Takeaways

| Pattern | When to Use | Complexity |
|---------|-------------|------------|
| Hash table / HashSet | Frequency counting, existence checks, O(1) lookup | O(n) time, O(n) space |
| Two pointers | Sorted array, finding pairs, palindromes | O(n) time, O(1) space |
| Sliding window | Longest/shortest subarray/substring with constraint | O(n) time, O(k) space |
| StringBuilder | String construction in a loop | O(n) vs O(n²) for concatenation |
| Char frequency array | When alphabet is bounded (ASCII/Unicode) | O(n) time, O(1) space |

---

*[← Chapter VII](07-technical-questions.md) | [Back to Index](../README.md) | [Chapter 2 — Linked Lists →](09-linked-lists.md)*
