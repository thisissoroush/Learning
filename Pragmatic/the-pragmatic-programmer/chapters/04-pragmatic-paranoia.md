# Chapter 4: Pragmatic Paranoia
## *You can't write perfect software — so defend against your own mistakes*

---

## 🎯 Core Concept

> **Tip 36: You Can't Write Perfect Software**

Perfect software doesn't exist. Pragmatic Programmers know this — and they code defensively against their *own* mistakes, not just other people's. This chapter is about building safeguards into your code that catch errors early, loudly, and cleanly.

> *"When everybody actually is out to get you, paranoia is just good thinking."* — Woody Allen

---

## 📌 Topics in This Chapter

| Topic | Title | Core Idea |
|---|---|---|
| 23 | Design by Contract | Define rights and responsibilities explicitly |
| 24 | Dead Programs Tell No Lies | Crash early rather than limp along corrupted |
| 25 | Assertive Programming | Use assertions to catch the "impossible" |
| 26 | How to Balance Resources | Whoever allocates a resource must free it |
| 27 | Don't Outrun Your Headlights | Take small steps; don't predict too far ahead |

---

## 🔑 Topic 23 — Design by Contract (DBC)

### 💡 Tip 37: Design with Contracts

A contract defines **rights and responsibilities** between parties. Bertrand Meyer's Design by Contract applies this to software:

```
┌─────────────────────────────────────────────────────────────────┐
│                     CONTRACT COMPONENTS                         │
│                                                                 │
│  PRECONDITIONS   → What must be true BEFORE calling a function  │
│                    (caller's responsibility to ensure this)     │
│                                                                 │
│  POSTCONDITIONS  → What the function GUARANTEES when it returns │
│                    (function's responsibility)                  │
│                                                                 │
│  INVARIANTS      → What must ALWAYS be true about the class     │
│                    (from every caller's perspective)            │
└─────────────────────────────────────────────────────────────────┘
```

### Example in Clojure

```clojure
(defn accept-deposit [account-id amount]
  { :pre  [ (> amount 0.00)          ;; precondition: positive amount
            (account-open? account-id) ]  ;; precondition: valid account
    :post [ (contains? (account-transactions account-id) %) ] }
  ;; postcondition: transaction appears in account
  (create-transaction account-id :deposit amount))
```

If the precondition fails:
```
AssertionError: Assert failed: (> amount 0.0)
```

### DBC vs Testing

| | DBC | Unit Tests |
|---|---|---|
| When active | Always (design, dev, deploy, maintenance) | Only at test time |
| Focus | Internal invariants + API contracts | Public interface (black-box) |
| Mocking needed | No | Yes |
| Scope | Every call, every time | One specific case at a time |

**Use both.** They complement, not replace, each other.

---

## 🔑 Topic 24 — Dead Programs Tell No Lies

### 💡 Tip 38: Crash Early

A program that detects an impossible state and **crashes immediately** does far less damage than one that continues running with corrupted data.

```
SCENARIO: A variable that should never be null IS null

OPTION A: Continue running
  → Write corrupted data to the database
  → Corrupt downstream systems
  → Bug surfaces 10 minutes later in production
  → Root cause is buried under new failures
  → Very hard to debug

OPTION B: Crash immediately (Tip 38)
  → Stack trace points directly to the problem
  → No corrupted data was written
  → Easy to fix
  → A dead program does far less damage than a crippled one
```

### Erlang's Philosophy

Erlang/Elixir embrace this: *"Let it crash!"* Programs are designed to fail, but failures are managed by **supervisor trees**:

```
Supervisor (restarts crashed children)
    ├── Worker Process A
    ├── Worker Process B  ← crashes? supervisor restarts it
    └── Sub-supervisor
            ├── Worker C
            └── Worker D
```

This is how telecom systems achieve "nine nines" (99.9999999%) uptime.

### Catch and Release Is for Fish

```ruby
# BAD: Catch every exception and re-raise — noisy and fragile
begin
  add_score_to_board(score)
rescue InvalidScore
  Logger.error("Can't add invalid score. Exiting"); raise
rescue BoardServerDown
  Logger.error("Can't add score: board is down. Exiting"); raise
end

# GOOD: Let it propagate. Don't mask errors.
add_score_to_board(score)
```

---

## 🔑 Topic 25 — Assertive Programming

### 💡 Tip 39: Use Assertions to Prevent the Impossible

Whenever you think *"this can never happen"* — write code that checks it.

```java
// "result can't be null" → prove it
assert result != null && result.size() > 0 : "Empty result from XYZ";

// "my sort algorithm works" → verify it
books = my_sort(find("scifi"));
assert is_sorted?(books);
```

### Important Rules

| Rule | Explanation |
|---|---|
| **Don't use for user input** | Assertions are for impossible states, not expected errors |
| **Watch for side effects** | Don't call `iter.nextElement()` inside an assert — it advances the iterator |
| **Leave assertions ON in production** | Testing doesn't find all bugs; real users do |

```
MISCONCEPTION: "Turn off assertions in production for performance"
                                ↓
REALITY: This is like crossing a high wire without a net
         because you made it across once in practice.
```

---

## 🔑 Topic 26 — How to Balance Resources

### 💡 Tip 40: Finish What You Start
### 💡 Tip 41: Act Locally

The function or object that **allocates** a resource should be **responsible for deallocating** it.

```ruby
# BAD: read_customer opens a file, write_customer closes it
# These are tightly coupled through @customer_file
def update_customer(transaction_amount)
  read_customer           # opens @customer_file
  @balance += amount
  write_customer          # closes @customer_file (maybe!)
end

# GOOD: update_customer owns the file lifecycle
def update_customer(transaction_amount)
  File.open(@name + ".rec", "r+") do |file|   # opens here
    read_customer(file)
    @balance += amount
    write_customer(file)
  end                                           # closes here (guaranteed)
end
```

### Nesting Rules

```
WHEN USING MULTIPLE RESOURCES:

  1. Deallocate in REVERSE order of allocation
     → If you open A then B, close B then A
     → Prevents orphaned references
     
  2. Always allocate in the SAME ORDER throughout the code
     → Prevents deadlocks
     → Process A: claims resource1 then resource2
     → Process B: claims resource1 then resource2  (same order = no deadlock)
```

---

## 🔑 Topic 27 — Don't Outrun Your Headlights

### 💡 Tip 42: Take Small Steps — Always
### 💡 Tip 43: Avoid Fortune-Telling

Headlights on a car illuminate 160 feet ahead. At 70mph, stopping distance is 464 feet. You can literally outrun your headlights — and crash.

The same is true in software. We can only see a step or two ahead reliably. Beyond that, we're speculating.

```
WHAT'S IN YOUR HEADLIGHTS:        WHAT'S TOO FAR AHEAD:
┌───────────────────────┐         ┌─────────────────────────┐
│ ✅ Next few hours     │         │ ❌ Estimating 6 months  │
│ ✅ Current iteration  │         │    of exact work        │
│ ✅ Known requirements │         │ ❌ Predicting user       │
│ ✅ Tests for what     │         │    needs in 2 years     │
│    you just wrote     │         │ ❌ Designing for tech    │
│                       │         │    that doesn't exist   │
└───────────────────────┘         └─────────────────────────┘
```

**Feedback is your speed limit.** Take a step, get feedback, take another step. Never commit to a task that requires "fortune telling."

```
SMALL STEPS CHECKLIST:
  ✅ REPL results → feedback on APIs and algorithms
  ✅ Unit tests   → feedback on your last code change
  ✅ User demos   → feedback on features and usability
```

---

## 📊 Chapter Summary

```
┌──────────────────────────────────────────────────────────────────┐
│                    CHAPTER 4 MENTAL MODEL                        │
│                                                                  │
│  PERFECT SOFTWARE   → Doesn't exist; plan for this reality       │
│                                                                  │
│  CONTRACTS          → Define what you need, what you promise     │
│                       — make it explicit, not assumed            │
│                                                                  │
│  CRASH EARLY        → A program that stops immediately does      │
│                       less damage than one that limps along      │
│                                                                  │
│  ASSERTIONS         → Code your "this can never happen"          │
│                       checks; leave them on in production        │
│                                                                  │
│  RESOURCE BALANCE   → You open it, you close it. Period.         │
│                                                                  │
│  SMALL STEPS        → Feedback is your speed limit; don't        │
│                       outrun your headlights                     │
└──────────────────────────────────────────────────────────────────┘
```

---

## 💡 Key Takeaways

| # | Takeaway |
|---|---|
| 1 | **Perfect software is impossible** — design your code knowing this |
| 2 | **Contracts make expectations explicit** — preconditions, postconditions, invariants |
| 3 | **Crash early, crash loudly** — a dead program does less damage than a corrupted one |
| 4 | **Assert the "impossible"** — and leave assertions on in production |
| 5 | **The allocator is the deallocator** — resource balance prevents leaks |
| 6 | **Take small steps** — feedback is your headlights; don't outrun them |

---

*← [Chapter 3 — The Basic Tools](03-the-basic-tools.md) | [Back to Index](../README.md) | Next: [Chapter 5 — Bend, or Break](05-bend-or-break.md) →*
