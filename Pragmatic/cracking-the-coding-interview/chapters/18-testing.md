# Chapter 11 — Testing

> *"Testing questions reveal how a candidate thinks about edge cases, user behavior, and system correctness — before the code is written."*  
> — Gayle Laakmann McDowell

---

## 🎯 Core Concept

Testing questions in interviews are not about writing unit test syntax. They test whether you think **systematically** about correctness, edge cases, and the difference between what the spec says and what users actually do.

---

## 🔢 The 4 Types of Testing Questions

```
TYPE 1: Test a REAL-WORLD OBJECT
  "How would you test a pen?"
  → Think like a QA engineer. What could go wrong?

TYPE 2: Test a PIECE OF SOFTWARE
  "How would you test Google Maps?"
  → Think in categories: functional, performance,
    security, usability, compatibility

TYPE 3: Write TEST CASES for a function
  "Write test cases for: int divide(int a, int b)"
  → Think: normal cases, edge cases, error cases

TYPE 4: DEBUG existing code
  "This function has a bug. Find it."
  → Trace through with examples. Binary search on inputs.
```

---

## 🧪 Testing a Real-World Object: "Test a Stapler"

```
STEP 1: Who uses it?
  → Office workers, students, teachers

STEP 2: How is it used?
  → Staple 2 pages, 10 pages, 50 pages
  → Left-handed and right-handed users

STEP 3: What can go wrong?
  → Jam: staple gets stuck
  → Misfire: staple doesn't penetrate all pages
  → Open mode: stapling into a board
  → Running out of staples

STEP 4: Define test categories:
  ① Functional: Does it staple correctly?
  ② Capacity:   Max pages it can staple
  ③ Durability: Works after 10,000 uses?
  ④ Safety:     No sharp edges exposed to users
  ⑤ Ergonomics: Comfortable to squeeze?
  ⑥ Edge cases: Paper thicknesses, card stock, plastic
```

---

## 💻 Testing Software: "Test ATM Software"

```
WHO ARE THE USERS?
  → Regular bank customers
  → Bank staff (maintenance)
  → Malicious users (hackers)

WHAT ACTIONS CAN THEY TAKE?
  → Insert card, enter PIN, withdraw, deposit,
    check balance, transfer, change PIN

NORMAL TEST CASES:
  → Valid card, correct PIN, sufficient balance → success
  → Withdraw $100, account has $500 → balance becomes $400

EDGE CASES:
  → Wrong PIN: 3 attempts → card locked
  → Withdraw more than balance → decline
  → Network timeout mid-transaction
  → Withdraw exactly $0.00 → error
  → Multiple concurrent sessions for same account

STRESS / LOAD TESTING:
  → 100 users withdrawing simultaneously
  → ATM runs 24/7 for 30 days continuously

SECURITY TESTING:
  → Card skimming simulation
  → SQL injection on PIN entry field
  → Session not closed when user walks away
```

---

## 🔑 Writing Test Cases for Code

```java
// Function: int divide(int dividend, int divisor)

// NORMAL CASES:
divide(10, 2)   → 5   (positive / positive, exact)
divide(10, 3)   → 3   (truncate toward zero: 3.33 → 3)
divide(-10, 2)  → -5  (negative / positive)
divide(10, -2)  → -5  (positive / negative)
divide(-10, -2) → 5   (negative / negative = positive)

// EDGE CASES:
divide(0, 5)    → 0   (zero dividend)
divide(5, 1)    → 5   (divisor is 1)
divide(5, 5)    → 1   (dividend == divisor)

// ERROR / BOUNDARY CASES:
divide(5, 0)    → ArithmeticException (divide by zero!)
divide(Integer.MIN_VALUE, -1) → overflow! MIN_VALUE = -2^31,
                                 result would be 2^31 (too big)
divide(Integer.MAX_VALUE, 1)  → MAX_VALUE (no issue)
```

---

## 🔍 Test Categories to Always Consider

```
FUNCTIONAL:    Does it do what the spec says?
BOUNDARY:      What happens at the min/max values?
NULL/EMPTY:    Null input, empty string, empty list
PERFORMANCE:   Does it stay fast with 1M items?
SECURITY:      Injection attacks? Auth bypass?
CONCURRENT:    Race conditions with multiple threads?
COMPATIBILITY: Works on Windows, Mac, Linux? Mobile?
RECOVERY:      What happens after a crash or network drop?
```

---

## 🐛 Debugging Mindset

When asked to find a bug:

```
STEP 1: Understand what the function SHOULD do
STEP 2: Pick a specific input and manually trace through
STEP 3: Find where expected and actual diverge
STEP 4: Form a hypothesis about the cause
STEP 5: Verify by checking edge cases

Binary search debugging:
  → If output wrong for n=10, test n=5
  → If n=5 is correct, bug is in [5..10] range
  → Narrow down systematically
```

---

## 💡 Key Takeaways

| Testing Dimension | What to Check |
|-------------------|--------------|
| Functional | Does it meet the spec? |
| Boundary | Min/max values, exact boundary conditions |
| Null/Empty | Null pointers, empty collections, zero-length strings |
| Error cases | Invalid input, divide by zero, network failure |
| Load/Performance | Does it scale? Time/memory under heavy load? |
| Security | Injection, auth bypass, data exposure |
| Concurrency | Race conditions, deadlocks, stale data |
| Real-world objects | Functional → Capacity → Durability → Safety → Ergonomics |

---

*[← Chapter 10](17-sorting-and-searching.md) | [Back to Index](../README.md) | [Chapter 12 — C & C++ →](19-c-and-cpp.md)*
