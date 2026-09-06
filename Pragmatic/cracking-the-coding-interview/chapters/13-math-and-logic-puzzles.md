# Chapter 6 — Math & Logic Puzzles

> *"Math and logic puzzles test whether you can reason from first principles rather than recall a formula."*  
> — Gayle Laakmann McDowell

---

## 🎯 Core Concept

This chapter covers the mathematical reasoning skills that underpin algorithmic problem solving: **prime numbers, combinatorics, probability, and classic brain teasers**. These appear less frequently than trees or graphs but demonstrate analytical depth.

---

## 🔢 Prime Numbers

### Primality Test

```java
// Naive: O(√n) — only need to check up to √n
boolean isPrime(int n) {
    if (n < 2) return false;
    for (int i = 2; i * i <= n; i++) {  // note: i*i ≤ n not i ≤ n
        if (n % i == 0) return false;
    }
    return true;
}
// WHY √n? If n = a × b and a ≤ b, then a ≤ √n.
// So if no factor ≤ √n, n is prime.
```

### Sieve of Eratosthenes — All Primes Up to N

```java
// Find all primes ≤ n. Time: O(n log log n), Space: O(n)
boolean[] sieve(int n) {
    boolean[] isComposite = new boolean[n + 1];
    // isComposite[i] = false means i is PRIME
    for (int i = 2; i * i <= n; i++) {
        if (!isComposite[i]) {
            // Mark all multiples of i as composite
            for (int j = i * i; j <= n; j += i)
                isComposite[j] = true;
        }
    }
    return isComposite;
}
// Key insight: start marking at i*i because smaller multiples
// were already marked by smaller primes.
```

---

## 🎲 Probability

### Basic Rules

```
P(A and B) = P(A) × P(B)     [if A, B are INDEPENDENT]
P(A and B) = P(A|B) × P(B)   [if NOT independent]
P(A or B)  = P(A) + P(B) - P(A and B)
P(A or B)  = P(A) + P(B)     [if MUTUALLY EXCLUSIVE]
```

### Classic Problem: Birthday Paradox

> How many people do you need in a room for a 50%+ chance two share a birthday?

```
Probability that NO TWO share a birthday with n people:
  P(no match) = (365/365) × (364/365) × (363/365) × ... × ((365-n+1)/365)

P(at least one match) = 1 - P(no match)

n=23: P(match) ≈ 50.7%  ← surprisingly low!
n=50: P(match) ≈ 97%
n=70: P(match) ≈ 99.9%

Counterintuitive because we compare ALL pairs, not just one.
With 23 people, there are C(23,2) = 253 pairs to compare.
```

---

## 🧮 Combinatorics Basics

```
PERMUTATIONS (order matters):
  P(n, k) = n! / (n-k)! = n × (n-1) × ... × (n-k+1)
  Example: Choose 3 people from 5, ordered seating:
  P(5,3) = 5 × 4 × 3 = 60

COMBINATIONS (order doesn't matter):
  C(n, k) = n! / (k! × (n-k)!)
  Example: Choose 3 people from 5 (any order):
  C(5,3) = 60 / 6 = 10

Pascal's Triangle gives C(n,k) values:
  C(n,k) = C(n-1,k-1) + C(n-1,k)
```

---

## 🧩 Classic Brain Teasers (Interview Examples)

### The 9 Balls Problem

> 9 balls, one heavier. Find it using a balance scale in 2 weighings.

```
Strategy (divide into thirds — not halves!):
  Weighing 1: Put 3 balls on each side.
    → If balanced: heavy ball is in the 3 not weighed.
    → If one side tips: heavy ball is in those 3.

  Weighing 2: From the identified 3, weigh 1 vs 1.
    → If balanced: remaining ball is heavy.
    → If one tips: that's the heavy ball.

KEY INSIGHT: Binary decisions (left/right/balanced) are
ternary, not binary. Each weighing gives 3 outcomes.
n balls identified in k weighings: n ≤ 3^k.
```

### The Jug Water Problem

> Two jugs: 3L and 5L. Measure exactly 4L.

```
Fill 5L. Pour into 3L. 5L has 2L left.
Empty 3L. Pour 2L from 5L into 3L.
Fill 5L again. Pour into 3L (needs 1L to fill).
5L now has exactly 4L. ✓
```

---

## 📐 Useful Math Facts for Interviews

```
SUM OF 1..n = n(n+1)/2
SUM OF SQUARES 1²+2²+...+n² = n(n+1)(2n+1)/6
POWERS OF 2: 2^10 ≈ 1,000 (1KB), 2^20 ≈ 1M, 2^30 ≈ 1B
LOG BASE CHANGE: log_a(b) = log(b) / log(a)
GEOMETRIC SERIES: 1+2+4+...+2^n = 2^(n+1) - 1

MODULAR ARITHMETIC:
  (a + b) % m = ((a % m) + (b % m)) % m
  (a × b) % m = ((a % m) × (b % m)) % m
```

---

## 💡 Key Takeaways

| Concept | Key Formula / Trick |
|---------|---------------------|
| Primality test | Check divisors up to √n only |
| Sieve of Eratosthenes | Mark composites from i² upward; O(n log log n) |
| Independent probability | P(A and B) = P(A) × P(B) |
| Birthday paradox | 23 people → 50% chance of shared birthday |
| Permutations | n!/(n-k)! — order matters |
| Combinations | n!/(k!(n-k)!) — order doesn't matter |
| Balance puzzle | Think in thirds (ternary), not halves (binary) |
| Sum of 1..n | n(n+1)/2 — memorize this |

---

*[← Chapter 5](12-bit-manipulation.md) | [Back to Index](../README.md) | [Chapter 7 — Object-Oriented Design →](14-object-oriented-design.md)*
