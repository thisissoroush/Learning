# Chapter 2: A Pragmatic Approach
## *Universal principles that apply at every level of software development*

---

## 🎯 Core Concept

This chapter gives you the **design and thinking principles** that underlie everything else. Before diving into specific tools or techniques, you need a handful of mental models that apply universally — to code, to design, to documentation, to teams.

> *"There are certain tips and tricks that apply at all levels of software development, processes that are virtually universal, and ideas that are almost axiomatic."*

---

## 📌 Topics in This Chapter

| Topic | Title | Core Idea |
|---|---|---|
| 8 | The Essence of Good Design | ETC — Easier to Change |
| 9 | DRY — The Evils of Duplication | Every piece of knowledge has one home |
| 10 | Orthogonality | Changes in one place don't affect others |
| 11 | Reversibility | Avoid locking yourself into decisions |
| 12 | Tracer Bullets | Get early feedback on the whole system |
| 13 | Prototypes and Post-it Notes | Explore risk cheaply before committing |
| 14 | Domain Languages | Write code that speaks the problem's language |
| 15 | Estimating | How to give accurate, honest estimates |

---

## 🔑 Topic 8 — The Essence of Good Design

### 💡 Tip 14: Good Design Is Easier to Change Than Bad Design

Every design principle — DRY, SOLID, decoupling, naming — is ultimately a special case of one master principle:

> **ETC: Easier To Change**

```
ETC IS THE ROOT OF ALL DESIGN PRINCIPLES:

  Why is decoupling good?
    → Isolating concerns makes each part easier to change. ETC.

  Why is single responsibility principle useful?
    → A change in requirements changes only one module. ETC.

  Why does naming matter?
    → Good names make code readable, and you must read to change. ETC.
    
  Why is DRY important?
    → One place to change means you can't accidentally miss a spot. ETC.
```

**ETC is a value, not a rule.** It's a guiding question you ask yourself:

> *"Did the thing I just did make the overall system easier or harder to change?"*

Ask this when you save a file. Ask it when you write a test. Ask it when you fix a bug. After a week, it becomes instinct.

---

## 🔑 Topic 9 — DRY: The Evils of Duplication

### 💡 Tip 15: DRY — Don't Repeat Yourself

> *Every piece of knowledge must have a single, unambiguous, authoritative representation within a system.*

**DRY is NOT just about code duplication.** It's about knowledge duplication. If you have to change something in two places, you'll eventually forget one of them.

### Types of DRY Violations

```
┌──────────────────────────────────────────────────────────────────┐
│                     DRY VIOLATION TYPES                          │
├──────────────────┬───────────────────────────────────────────────┤
│ Code Duplication │ Copy-pasted logic in multiple functions        │
├──────────────────┼───────────────────────────────────────────────┤
│ Documentation    │ Comment describes what the code already shows  │
├──────────────────┼───────────────────────────────────────────────┤
│ Data Structures  │ length field that duplicates end - start       │
├──────────────────┼───────────────────────────────────────────────┤
│ Across APIs      │ Your code knows the schema of an external API  │
├──────────────────┼───────────────────────────────────────────────┤
│ Across Devs      │ Two teams implement the same utility function  │
└──────────────────┴───────────────────────────────────────────────┘
```

### Example: Code Duplication

```ruby
# BAD — fee formatting logic duplicated
def print_balance(account)
  printf "Fees:    %10.2f\n", account.fees      if account.fees >= 0
  printf "Fees:    %10.2f-\n", -account.fees    if account.fees < 0
  printf "Balance: %10.2f\n", account.balance   if account.balance >= 0
  printf "Balance: %10.2f-\n", -account.balance if account.balance < 0
end

# GOOD — extract the duplicated knowledge into one place
def format_amount(value)
  result = sprintf("%10.2f", value.abs)
  value < 0 ? result + "-" : result + " "
end

def print_balance(account)
  printf "Fees:    %s\n", format_amount(account.fees)
  printf "Balance: %s\n", format_amount(account.balance)
end
```

### Example: Data Structure Duplication

```java
// BAD — length duplicates information already in start and end
class Line {
  Point  start;
  Point  end;
  double length;   // ← WRONG: this is derivable!
}

// GOOD — compute it, don't store it
class Line {
  Point  start;
  Point  end;
  double length() { return start.distanceTo(end); }
}
```

### When Is "Duplicate" Code NOT a DRY violation?

```python
# These look the same — are they a DRY violation?
def validate_age(value):
    validate_type(value, :integer)
    validate_min_integer(value, 0)

def validate_quantity(value):
    validate_type(value, :integer)
    validate_min_integer(value, 0)
```

**Answer: No.** The code is the same, but the *knowledge* is different. Age and quantity both happen to require the same validation *today*, but for unrelated reasons. If age validation changes (e.g., must be 18+), you shouldn't change quantity validation. These represent different intent.

### 💡 Tip 16: Make It Easy to Reuse

The best DRY enforcement is making reuse easy. If people can find and reuse existing code faster than writing new code, they will. If they can't, they'll duplicate.

---

## 🔑 Topic 10 — Orthogonality

### 💡 Tip 17: Eliminate Effects Between Unrelated Things

**Orthogonality** (from geometry: two lines meeting at right angles) means: *changes in one thing do not affect another unrelated thing*.

```
ORTHOGONAL AXES (geometry):        ORTHOGONAL COMPONENTS (code):

        North ↑                       Database
              │                       ────────
              │                       Changes here...
      ─────── + ──────── East              ↓
              │                       DON'T affect...
              │                           ↓
                                      User Interface
                                      ─────────────
Moving North doesn't affect         And vice versa!
your East/West position.
```

### The Helicopter Analogy

Flying a helicopter is **not orthogonal**. When you adjust one control:
- Lower the collective pitch lever → nose drops → need backward stick
- Adjust the stick → affects the foot pedals
- Adjust foot pedals → affects everything else again

**Every input has secondary effects.** This is enormously complex and dangerous. Non-orthogonal code is the same.

### Benefits of Orthogonality

```
┌────────────────────────────────────────────────────────────────┐
│                  WHY ORTHOGONALITY MATTERS                     │
│                                                                │
│  PRODUCTIVITY GAINS:                                           │
│  ✅ Changes are localized → faster dev and test               │
│  ✅ Components can be combined in unexpected ways             │
│  ✅ M things × N things = M×N capabilities (not M+N)         │
│                                                                │
│  RISK REDUCTION:                                               │
│  ✅ Bugs are isolated → can't spread to the whole system      │
│  ✅ System is less fragile                                    │
│  ✅ Easier to test each component independently               │
│  ✅ Less vendor lock-in                                       │
└────────────────────────────────────────────────────────────────┘
```

### The Orthogonality Test

> *"If I dramatically change the requirements behind a particular function, how many modules are affected?"*

In an orthogonal system, the answer should be **one**.

- Moving a button on a GUI should NOT require a database schema change
- Adding context-sensitive help should NOT change the billing subsystem

### Layered Architecture

```
┌──────────────────────────┐
│      User Interface      │  ← Change UI without touching DB
├──────────────────────────┤
│  Authorization / Business│  ← Change rules without touching UI
├──────────────────────────┤
│      Data Model          │  ← Change schema without touching UI
├──────────────────────────┤
│   Database Access        │  ← Swap databases without changing UI
└──────────────────────────┘
```

### Coding for Orthogonality

| Practice | How it helps |
|---|---|
| **Write shy code** | Modules don't reveal internals or rely on others' internals |
| **Avoid global data** | Globals link every function to every other implicitly |
| **Avoid similar functions** | Duplicate code is a symptom of structural problems |
| **Use the Law of Demeter** | Only talk to your immediate friends |

---

## 🔑 Topic 11 — Reversibility

### 💡 Tip 18: There Are No Final Decisions
### 💡 Tip 19: Forgo Following Fads

> *"Nothing is more dangerous than an idea if it's the only one you have."*

Every time you make a critical, irreversible architectural decision, you narrow your target. Requirements change. Vendors get acquired. Better options emerge.

```
ARCHITECTURAL CHOICES OVER 20 YEARS:

  Big hunk of iron
      → Federations of big iron
          → Load-balanced commodity clusters
              → Cloud VMs running applications
                  → Cloud VMs running services
                      → Containers
                          → Serverless
                              → (back to big iron for some tasks?)
```

The lesson is not to pick the right architecture — **it's to make your architecture easy to swap**.

### How to Stay Reversible

```
┌───────────────────────────────────────────────────────┐
│               REVERSIBILITY TECHNIQUES                │
│                                                       │
│  ✅ Follow DRY → no duplicated decisions to unwind    │
│  ✅ Decouple → swap components independently          │
│  ✅ Use external config → change behavior without     │
│     recompiling                                       │
│  ✅ Hide third-party APIs behind your own abstraction │
│  ✅ Build in components → easier to split later       │
└───────────────────────────────────────────────────────┘
```

> *"Instead of carving decisions in stone, think of them as written in sand at the beach. A big wave can come along and wipe them out at any time."*

---

## 🔑 Topic 12 — Tracer Bullets

### 💡 Tip 20: Use Tracer Bullets to Find the Target

When shooting in the dark at a moving target, tracer bullets light up the path from gun to target in real time. You can adjust as you go.

**Tracer bullet development** applies the same principle: build a thin, end-to-end slice of your system quickly to get real feedback.

```
TRADITIONAL (Big-Bang):            TRACER BULLET:
┌────────────────────┐            ┌──────────────────────────┐
│ Design everything  │            │ Find a simple feature    │
│ → Build module 1   │     →      │ that crosses all layers  │
│ → Build module 2   │            │ → Build just that        │
│ → Build module N   │            │ → Show users             │
│ → Integrate        │            │ → Adjust and iterate     │
│ → Pray it works    │            │ → Keep building on top   │
└────────────────────┘            └──────────────────────────┘
        ❌                                    ✅
```

### Tracer Bullet in Action

```
                    FULL SYSTEM (end goal)
                    
  UI Layer      ████░░░░░░░░░░░░░░░░░░  (solid = done)
  Auth Layer    ████░░░░░░░░░░░░░░░░░░
  Business      ████░░░░░░░░░░░░░░░░░░
  Data Model    ████░░░░░░░░░░░░░░░░░░
  Database      ████░░░░░░░░░░░░░░░░░░
                 ↑
            Tracer bullet cuts through ALL layers
            for ONE feature — gets to the target.
            Rest of the app is not yet implemented.
```

### Benefits

| Benefit | Why it matters |
|---|---|
| Users see something working early | Real feedback, not paper specs |
| Developers have a structure to work in | No more blank page problem |
| Integration happens continuously | No big-bang integration surprises |
| Always have something to demo | Never caught without progress to show |

### Tracer Bullets vs Prototypes

```
PROTOTYPE                         TRACER BULLET
┌────────────────────────┐       ┌─────────────────────────────┐
│ Explores ONE aspect    │       │ Explores ONE path through   │
│ of the final system    │       │ the WHOLE system            │
│                        │       │                             │
│ Disposable code        │       │ Production-quality code     │
│ (throw it away)        │       │ (keep it and build on it)   │
│                        │       │                             │
│ Purpose: learn about   │       │ Purpose: get to the target  │
│ a specific risk        │       │ and keep adjusting aim      │
└────────────────────────┘       └─────────────────────────────┘
```

---

## 🔑 Topic 13 — Prototypes and Post-it Notes

### 💡 Tip 21: Prototype to Learn

A prototype answers specific questions at low cost. You prototype things that carry **risk** — things you're uncertain about, things that haven't been done before.

```
WHAT TO PROTOTYPE:
  ✅ Architecture decisions
  ✅ New functionality in an existing system
  ✅ Third-party tools or components
  ✅ Performance bottlenecks
  ✅ User interface designs
  ✅ External data formats
```

### How to Prototype

When building a prototype, you can ignore:

| Usually Required | In a Prototype... |
|---|---|
| Correctness | Dummy data is fine |
| Completeness | Only the one path you're exploring |
| Robustness | Error checking optional |
| Style | Comments and docs minimal |

> ⚠️ **Critical:** Make sure everyone knows it's a prototype. People will try to ship it. If that's a real risk, use tracer bullets instead.

---

## 🔑 Topic 14 — Domain Languages

### 💡 Tip 22: Program Close to the Problem Domain

The language you write code in shapes how you think about the problem. Pragmatic Programmers go a step further: they write code *using the vocabulary of the domain*.

### Internal vs External Domain Languages

```
INTERNAL DOMAIN LANGUAGE           EXTERNAL DOMAIN LANGUAGE
(runs as host language code)       (parsed as its own syntax)

Examples: RSpec, Phoenix Router    Examples: Cucumber, Ansible YAML

describe BowlingScore do           Feature: Scoring
  it "totals 12 if you            Background:
      score 3 four times" do        Given an empty scorecard
    score = BowlingScore.new       Scenario: bowling a lot of 3s
    4.times { score.add(3) }         Given I throw a 3
    expect(score.total).to eq(12)    And I throw a 3
  end                                Then the score should be 12
end
```

| Type | Pro | Con |
|---|---|---|
| Internal | Free power of host language | Bound by host language syntax |
| External | Complete freedom of syntax | Need a parser; adds complexity |

**Rule of thumb:** Use off-the-shelf external languages (YAML, JSON, CSV) when possible. Use internal languages when your users will write the code themselves.

---

## 🔑 Topic 15 — Estimating

### 💡 Tip 23: Estimate to Avoid Surprises
### 💡 Tip 24: Iterate the Schedule with the Code

Estimating is a skill. Bad estimates damage trust. Good estimates help everyone plan.

### Scale Your Units to Your Accuracy

| If the duration is... | Express it as... |
|---|---|
| 1–15 days | Days |
| 3–6 weeks | Weeks |
| 8–20 weeks | Months |
| Over 20 weeks | Think hard before answering |

*"130 days"* implies false precision. *"About 6 months"* honestly communicates the range. Same duration, very different expectations.

### The Estimation Process

```
1. UNDERSTAND what's being asked
        ↓
2. BUILD a mental model of the system
        ↓
3. BREAK the model into components
        ↓
4. GIVE each parameter a realistic value
        ↓
5. CALCULATE, then validate against intuition
        ↓
6. TRACK your estimates vs actuals
   (this is how you get better)
```

### The Elephant Approach

> *"How do you eat an elephant? One bite at a time."*

The only way to estimate a complex project accurately is to **start doing it**. After the first iteration, you have real data. After the second, you have a trend. Estimates get better as you go.

### The Best Answer When Asked for an Estimate

> **"I'll get back to you."**

Estimates made at the coffee machine haunt you. Slow down, go through the process, then respond.

---

## 📊 Chapter Summary: The Pragmatic Approach

```
┌──────────────────────────────────────────────────────────────────┐
│                    CHAPTER 2 MENTAL MODEL                        │
│                                                                  │
│  ETC              → All design decisions should make things      │
│                     easier to change                             │
│                                                                  │
│  DRY              → Every piece of knowledge has ONE home        │
│                     (not just code — docs, data, intent)         │
│                                                                  │
│  Orthogonality    → Changes in one place don't ripple           │
│                     unexpectedly to others                       │
│                                                                  │
│  Reversibility    → Avoid locking yourself in; write code        │
│                     that can be swapped out                      │
│                                                                  │
│  Tracer Bullets   → Get end-to-end feedback early               │
│                     on the real system                           │
│                                                                  │
│  Prototypes       → Explore risk cheaply; throw the code away    │
│                                                                  │
│  Domain Language  → Write code in the vocabulary of the problem  │
│                                                                  │
│  Estimating       → A learnable skill; track and improve         │
└──────────────────────────────────────────────────────────────────┘
```

---

## 💡 Key Takeaways

| # | Takeaway |
|---|---|
| 1 | **ETC is the meta-principle** — every design rule serves it |
| 2 | **DRY is about knowledge, not just code** — duplication of intent is the real evil |
| 3 | **Orthogonal systems are easier to change, test, and debug** |
| 4 | **No decisions are final** — design for replaceability |
| 5 | **Tracer bullets give real feedback** — don't build in the dark |
| 6 | **Prototypes are disposable** — tracer code is production-grade |
| 7 | **Speak the domain's language** — it reduces translation errors |
| 8 | **Slow down before estimating** — "I'll get back to you" is an answer |

---

*← [Chapter 1 — A Pragmatic Philosophy](01-a-pragmatic-philosophy.md) | [Back to Index](../README.md) | Next: [Chapter 3 — The Basic Tools](03-the-basic-tools.md) →*
