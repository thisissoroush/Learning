# Chapter 5 — Bit Manipulation

> *"Bit manipulation is a powerful tool. Used correctly, it can be the most elegant solution to an otherwise complex problem."*  
> — Gayle Laakmann McDowell

---

## 🎯 Core Concept

Bit manipulation operates directly on binary representations of numbers. It unlocks O(1) tricks for problems that seem to require O(n) work. While not asked as often as trees or graphs, when bit manipulation IS the answer, nothing else comes close.

---

## 🔢 Binary Number Fundamentals

```
BINARY BASICS
──────────────────────────────────────────────────────────
  Decimal:   0   1   2   3   4   5   6   7   8
  Binary:    0   1  10  11 100 101 110 111 1000

  Bit positions (0-indexed from right):
  Number 13 = 0b1101
  Position:     3210
                │││└─ bit 0 = 1  (2⁰ = 1)
                ││└── bit 1 = 0  (2¹ = 2)
                │└─── bit 2 = 1  (2² = 4)
                └──── bit 3 = 1  (2³ = 8)
  Total: 8+4+0+1 = 13 ✓

  NEGATIVE NUMBERS: Two's complement
  -1  = all 1s  = 1111...1111
  -n  = ~n + 1  (flip all bits, add 1)
──────────────────────────────────────────────────────────
```

---

## 🛠️ Bitwise Operators

```java
// AND  (&): 1 only if BOTH bits are 1
0b1100 & 0b1010 = 0b1000   // 12 & 10 = 8

// OR   (|): 1 if EITHER bit is 1
0b1100 | 0b1010 = 0b1110   // 12 | 10 = 14

// XOR  (^): 1 if bits are DIFFERENT
0b1100 ^ 0b1010 = 0b0110   // 12 ^ 10 = 6

// NOT  (~): flip all bits
~0b0001 = 0b1110...1110     // ~1 = -2 (two's complement)

// LEFT SHIFT  (<<): multiply by 2
1 << 3 = 8      // 001 → 1000

// RIGHT SHIFT (>>): divide by 2 (signed, preserves sign bit)
16 >> 2 = 4     // 10000 → 100

// UNSIGNED RIGHT SHIFT (>>>): always fills 0 from left
-1 >>> 1 = Integer.MAX_VALUE  // fills 0s, ignores sign
```

---

## 🎯 The Essential Bit Tricks

```java
// 1. CHECK if bit i is set
boolean isBitSet(int n, int i) {
    return (n & (1 << i)) != 0;
}
// n=13 (1101), i=1: (1101 & 0010) = 0 → bit 1 is NOT set

// 2. SET bit i (turn on)
int setBit(int n, int i) {
    return n | (1 << i);
}
// n=13 (1101), i=1: 1101 | 0010 = 1111 = 15

// 3. CLEAR bit i (turn off)
int clearBit(int n, int i) {
    return n & ~(1 << i);
}
// n=13 (1101), i=2: 1101 & ~(0100) = 1101 & 1011 = 1001 = 9

// 4. UPDATE bit i to value v
int updateBit(int n, int i, int v) {
    return (n & ~(1 << i)) | (v << i);
}

// 5. CHECK if power of 2
boolean isPowerOfTwo(int n) {
    return n > 0 && (n & (n - 1)) == 0;
}
// Powers of 2: 1000, 10000 etc — n-1 flips all lower bits
// 8 & 7 = 1000 & 0111 = 0 ✓
// 6 & 5 = 0110 & 0101 = 0100 ≠ 0 → not power of 2 ✓

// 6. COUNT number of set bits (Brian Kernighan's algorithm)
int countBits(int n) {
    int count = 0;
    while (n != 0) {
        n &= (n - 1);  // clears the LOWEST set bit
        count++;
    }
    return count;
}
// 12 (1100): 1100&1011=1000 → 1000&0111=0000 → count=2 ✓
```

---

## 🧩 XOR — The Magic Operator

XOR has a special property: `a ^ a = 0` and `a ^ 0 = a`

```java
// CLASSIC PROBLEM: Find the single number in an array
// where every other number appears exactly twice.
// [4, 1, 2, 1, 2] → 4

int singleNumber(int[] nums) {
    int result = 0;
    for (int n : nums) result ^= n;
    return result;
}
// Pairs cancel: 1^1=0, 2^2=0, leaving only 4.
// Time: O(n), Space: O(1) — no HashMap needed!

// SWAP two integers without a temporary variable
void swap(int[] arr, int i, int j) {
    arr[i] ^= arr[j];
    arr[j] ^= arr[i];
    arr[i] ^= arr[j];
}
```

---

## 🔑 Two's Complement — Negative Numbers

```
 4-bit two's complement:
  0111 =  7
  0110 =  6
  0001 =  1
  0000 =  0
  1111 = -1   ← flip all bits of 0001, add 1: 1110+1=1111
  1110 = -2
  1000 = -8   ← most negative value for 4 bits

  To negate n: ~n + 1
  To negate -4 (1100): ~1100 = 0011, +1 = 0100 = 4 ✓
```

---

## 💡 Key Takeaways

| Operation | Code | Notes |
|-----------|------|-------|
| Check bit i | `(n >> i) & 1` | Returns 0 or 1 |
| Set bit i | `n \| (1 << i)` | Turns bit on |
| Clear bit i | `n & ~(1 << i)` | Turns bit off |
| Toggle bit i | `n ^ (1 << i)` | Flips bit |
| Power of two? | `n > 0 && (n & n-1) == 0` | Classic trick |
| Count set bits | Brian Kernighan: `n &= n-1` in loop | O(# set bits) |
| Find unique element | XOR all elements; pairs cancel | O(n), O(1) |
| Negative numbers | Two's complement: `~n + 1` | How CPUs store negatives |

---

*[← Chapter 4](11-trees-and-graphs.md) | [Back to Index](../README.md) | [Chapter 6 — Math & Logic Puzzles →](13-math-and-logic-puzzles.md)*
