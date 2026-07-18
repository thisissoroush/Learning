# Chapter 7: While You Are Coding
## *Active thinking, not mechanical transcription*

---

## 🎯 Core Concept

Coding is not mechanical. Every line requires decisions — decisions that, if made carelessly, can doom a system to years of pain. This chapter is about **how to code thoughtfully**: trusting your instincts, avoiding coincidence, testing intelligently, and naming things well.

> *"The single biggest reason that software projects fail is the attitude that coding is mostly mechanical, transcribing the design into executable statements."*

---

## 📌 Topics in This Chapter

| Topic | Title | Core Idea |
|---|---|---|
| 37 | Listen to Your Lizard Brain | Trust your instincts — they're data |
| 38 | Programming by Coincidence | Code what you understand, not what seems to work |
| 39 | Algorithm Speed | Know your Big-O before it matters |
| 40 | Refactoring | Continuously improve the code you've written |
| 41 | Test to Code | Testing drives better design, not just fewer bugs |
| 42 | Property-Based Testing | Let the computer find edge cases for you |
| 43 | Stay Safe Out There | Security basics every developer needs |
| 44 | Naming Things | Names reveal intent and shape understanding |

---

## 🔑 Topic 37 — Listen to Your Lizard Brain

### 💡 Tip 61: Listen to Your Inner Lizard

Your brain processes far more than your conscious mind shows you. When something feels wrong — you're uneasy about a design, reluctant to start coding, nagged by a vague feeling — **pay attention**. That feeling is your subconscious recognizing a pattern.

```
WHEN YOUR LIZARD BRAIN SPEAKS:

  "I don't want to write this code"    →  Maybe the design is wrong
  "This feels too complicated"         →  It probably is
  "Something's off about this API"     →  Investigate before continuing
  "I'm not sure this is right"         →  Stop and prototype first
```

### How to Listen

If you're stuck or uneasy, don't force it:
1. **Stop coding.** Do something else for a while — your subconscious keeps working.
2. **Externalize the problem** — write it down, draw it, explain it to a rubber duck.
3. **Prototype** — write throwaway code to explore the thing you're unsure about.
4. **Tell your brain it's OK to fail** — prototypes aren't real; explore freely.

---

## 🔑 Topic 38 — Programming by Coincidence

### 💡 Tip 62: Don't Program by Coincidence

**Programming by coincidence** = writing code that seems to work without understanding *why*. When it breaks (and it will), you won't know where to start.

```
COINCIDENCE:                          INTENTIONAL:
┌─────────────────────────────┐      ┌────────────────────────────────┐
│ I called function A         │      │ I called function A because    │
│ before function B and it    │  →   │ the docs say A must initialize │
│ works, so I guess that's    │      │ the context before B can use   │
│ the right order             │      │ it. I verified this with tests.│
└─────────────────────────────┘      └────────────────────────────────┘
         ❌ Fragile                             ✅ Solid
```

### Signs You're Programming by Coincidence

- You don't know why the code works; you just know it does
- You're afraid to change code because "it might break something"
- You copy-pasted from Stack Overflow and tweaked until it compiled
- You have commented-out code "just in case"

### How to Code Deliberately

1. **Know your preconditions** — don't rely on undocumented behavior
2. **Document your assumptions** — as assertions or comments
3. **Don't guess — experiment** — write a test that proves it
4. **Understand every line you write** — if you can't explain it, you don't own it

---

## 🔑 Topic 39 — Algorithm Speed

### 💡 Tip 63: Estimate the Order of Your Algorithms

Big-O notation describes how an algorithm's time or space scales with input size.

```
BIG-O CHEAT SHEET:

  O(1)       → Constant    — Hash lookup, array index
  O(log n)   → Logarithmic — Binary search
  O(n)       → Linear      — Simple loop through array
  O(n log n) → Linearithmic— Merge sort, heap sort
  O(n²)      → Quadratic   — Nested loops
  O(2ⁿ)      → Exponential → Brute-force combinatorics
  O(n!)      → Factorial   → Traveling salesman (brute)
```

```
VISUAL GROWTH (n = 1000):
  O(1)      →           1 operations
  O(log n)  →          10 operations
  O(n)      →       1,000 operations
  O(n log n)→      10,000 operations
  O(n²)     →   1,000,000 operations ← 1000× more!
  O(2ⁿ)     → 10^300 operations     ← impossible
```

**Estimate before you code.** If your algorithm is O(n²) on 1 million items, that's a trillion operations. Find a better algorithm first.

**Measure after you code.** Your intuitions about what's slow are often wrong. Profile first, optimize second.

---

## 🔑 Topic 40 — Refactoring

### 💡 Tip 64: Refactor Early, Refactor Often

**Refactoring** = improving the internal structure of code without changing external behavior. It's not rewriting — it's gardening. Continuous, small, disciplined improvement.

```
WHEN TO REFACTOR:
  ✅ You learned something new about the domain
  ✅ You fixed a bug (the code showed a structural problem)
  ✅ You notice duplication
  ✅ You see code that violates DRY, orthogonality, or naming clarity
  ✅ When adding a feature is harder than it should be
```

### How to Refactor Safely

```
1. Don't refactor and add features at the same time
2. Have good tests before you start
3. Take small, deliberate steps
4. Run tests after every step
5. If it breaks, revert immediately — don't debug refactoring
```

### Technical Debt

Software naturally tends toward disorder (entropy). Postponed refactoring is technical debt — it compounds. Paying it off gets harder the longer you wait.

---

## 🔑 Topic 41 — Test to Code

### 💡 Tip 65: Test to Code, Not Code to Test (TDD)
### 💡 Tip 66: Testing Is Not About Finding Bugs

The biggest value of testing isn't finding bugs — it's **the feedback it gives you about your design**.

If your code is hard to test, your design is wrong. Tests expose:
- Tight coupling (you need to set up the whole world to test one function)
- Missing abstractions (the interface is awkward to use)
- Unclear responsibilities (you don't know what to assert)

```
TEST-DRIVEN DEVELOPMENT CYCLE:

  1. Write a failing test for the next small piece of behavior
              ↓
  2. Write just enough code to make the test pass
              ↓
  3. Refactor the code (tests keep you safe)
              ↓
  4. Repeat
```

### Test Types

| Type | Scope | Purpose |
|---|---|---|
| **Unit tests** | Single function/class | Fast feedback on logic |
| **Integration tests** | Multiple components | Verify they work together |
| **Property-based** | Many random inputs | Find edge cases automatically |
| **End-to-end** | Full system | Verify the user journey |

---

## 🔑 Topic 42 — Property-Based Testing

### 💡 Tip 67: Use Property-Based Tests to Validate Your Assumptions

Instead of writing specific test cases, describe **properties that must always be true**, then let the computer generate hundreds of random inputs to try to violate them.

```python
# Example-based test (limited):
assert sort([3,1,2]) == [1,2,3]

# Property-based test (powerful):
# "A sorted list always has each element ≤ the next"
# "A sorted list has the same elements as the input"
# → Framework generates 100s of random lists and checks these properties
```

**Tools:** Hypothesis (Python), QuickCheck (Haskell), PropEr (Erlang), fast-check (JavaScript)

When a property test fails, the framework **shrinks** the input to the minimal failing case — a huge debugging aid.

---

## 🔑 Topic 43 — Stay Safe Out There

### 💡 Tip 68: Keep It Simple and Minimize Attack Surface
### 💡 Tip 69: Apply Security Patches Quickly

Security is not an add-on. Build it in from the start.

```
BASIC SECURITY PRINCIPLES:

  1. MINIMIZE ATTACK SURFACE
     → Less code = fewer vulnerabilities
     → Fewer open ports, interfaces, and services exposed
     → Don't give users more access than they need
     
  2. PRINCIPLE OF LEAST PRIVILEGE
     → Run with minimal permissions
     → Request permissions only when needed, relinquish immediately
     
  3. VALIDATE ALL INPUT
     → Never trust data from outside your system
     → Sanitize before using in SQL, HTML, shell commands
     
  4. ENCRYPT SENSITIVE DATA
     → Data at rest and in transit
     → Don't roll your own crypto
     
  5. APPLY UPDATES QUICKLY
     → Most breaches exploit known vulnerabilities
     → Old, unpatched software is a liability
```

---

## 🔑 Topic 44 — Naming Things

### 💡 Tip 74: Name Well; Rename When Needed

Names are the first documentation anyone reads. They reveal (or hide) intent.

```
BAD NAMES:                        GOOD NAMES:
  d  (days? data?)           →    elapsed_time_in_days
  fn (function name?)        →    calculate_interest
  the_list                   →    accounts_payable
  info                       →    user_profile
  data                       →    sensor_readings
  temp                       →    temporary_file_handle
```

### Naming Reveals Your Understanding

If you can't name something clearly, you may not fully understand it. The struggle to find a good name is often a signal to rethink the design.

**Culture matters:** Name things in the language of the domain. If business says "invoice," don't call it `bill` or `document`. Consistent vocabulary reduces cognitive load and prevents misunderstandings.

> *"Name things as if you were explaining them to a reader — because you are."*

---

## 📊 Chapter Summary

```
┌──────────────────────────────────────────────────────────────────┐
│                    CHAPTER 7 MENTAL MODEL                        │
│                                                                  │
│  LIZARD BRAIN     → Unease is data. Stop and investigate.        │
│                                                                  │
│  DELIBERATE CODE  → Understand every line. No coincidence.       │
│                                                                  │
│  ALGORITHM SPEED  → Know Big-O before you write; measure after   │
│                                                                  │
│  REFACTORING      → Continuous small improvements; pay debt now  │
│                                                                  │
│  TESTING          → Drives design quality; hard-to-test = bad    │
│                     design; TDD is a design tool                 │
│                                                                  │
│  PROPERTY TESTS   → Let computers find edge cases you missed     │
│                                                                  │
│  SECURITY         → Minimize attack surface; least privilege;    │
│                     validate all input; patch quickly            │
│                                                                  │
│  NAMING           → Names reveal intent; rename without fear     │
└──────────────────────────────────────────────────────────────────┘
```

---

## 💡 Key Takeaways

| # | Takeaway |
|---|---|
| 1 | **Trust your instincts** — unease is a signal worth investigating |
| 2 | **Code deliberately** — understand every line you write |
| 3 | **Know Big-O** — estimate algorithm cost before writing, measure after |
| 4 | **Refactor continuously** — small, safe, tested improvements |
| 5 | **Tests drive design** — if it's hard to test, the design is wrong |
| 6 | **Property tests find edge cases** — humans miss; computers don't |
| 7 | **Security is built-in, not bolted-on** — minimize surface, validate input |
| 8 | **Good names reveal intent** — naming is design |

---

*← [Chapter 6 — Concurrency](06-concurrency.md) | [Back to Index](../README.md) | Next: [Chapter 8 — Before the Project](08-before-the-project.md) →*
