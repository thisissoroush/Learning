# Chapter 5: Bend, or Break
## *Writing flexible code that survives the future*

---

## 🎯 Core Concept

Life doesn't stand still, and neither can your code. This chapter teaches you to write code that **bends rather than breaks** — flexible, loosely coupled, and easy to change as the world evolves.

> *"We need to make every effort to write code that's as loose — as flexible — as possible. Otherwise we may find our code quickly becoming outdated, or too brittle to fix."*

---

## 📌 Topics in This Chapter

| Topic | Title | Core Idea |
|---|---|---|
| 28 | Decoupling | Reduce connections between components |
| 29 | Juggling the Real World | Respond to events with FSMs, observers, pub/sub, streams |
| 30 | Transforming Programming | Think in data pipelines, not objects |
| 31 | Inheritance Tax | Inheritance causes coupling — use better alternatives |
| 32 | Configuration | Move decisions that change outside your code |

---

## 🔑 Topic 28 — Decoupling

### 💡 Tip 44: Decoupled Code Is Easier to Change
### 💡 Tip 45: Tell, Don't Ask
### 💡 Tip 46: Don't Chain Method Calls
### 💡 Tip 47: Avoid Global Data
### 💡 Tip 48: If It's Important Enough to Be Global, Wrap It in an API

**Coupling** = dependencies between components. Coupling makes change hard: change one thing, something else breaks unexpectedly.

```
COUPLED (like a rigid bridge):       DECOUPLED (like a chain):
┌─┐─┐─┐─┐─┐─┐─┐─┐                  ┌─┐ ┌─┐ ┌─┐ ┌─┐
│A│B│C│D│E│F│G│H│                  │A│ │B│ │C│ │D│
└─┘─┘─┘─┘─┘─┘─┘─┘                  └─┘ └─┘ └─┘ └─┘
   All links rigid                      Each link independent
   Change A → affects H                 Change A → only affects A
```

### Train Wrecks (Method Chaining Gone Wrong)

```java
// BAD: traverses 5 levels of abstraction — brittle!
totals = customer.orders.find(order_id).getTotals();
totals.grandTotal = totals.grandTotal - discount;

// BETTER: Tell, Don't Ask — delegate to the object
customer.findOrder(order_id).applyDiscount(discount);
```

The "Tell, Don't Ask" principle: **don't make decisions based on an object's internal state and then update it**. Tell the object to do it itself.

**One-dot rule:** Try not to chain more than one "." when accessing something. Exception: stable library APIs like `array.sort_by{}.first(10).map{}` are fine.

### The Evils of Globals

Every global variable is an implicit parameter to every function. It:
- Makes testing hard (must set up global state)
- Creates hidden coupling between unrelated code
- Makes reuse nearly impossible

> Even singletons are globals. Even "config objects" are globals. Wrap them in APIs.

---

## 🔑 Topic 29 — Juggling the Real World

The real world is event-driven. Here are 4 strategies for handling events:

```
┌─────────────────────────────────────────────────────────────────┐
│                  4 EVENT HANDLING STRATEGIES                    │
│                                                                 │
│  1. FINITE STATE MACHINES  → Explicit states + transitions      │
│  2. OBSERVER PATTERN       → Register callbacks with a source   │
│  3. PUBLISH / SUBSCRIBE    → Decouple via named channels        │
│  4. REACTIVE STREAMS       → Treat events as collections        │
└─────────────────────────────────────────────────────────────────┘
```

### Finite State Machines (FSM)

```
States: Initial → Reading → Done | Error

TRANSITIONS TABLE:
┌──────────┬────────┬──────┬─────────┬───────┐
│ State    │ Header │ Data │ Trailer │ Other │
├──────────┼────────┼──────┼─────────┼───────┤
│ Initial  │Reading │Error │ Error   │ Error │
│ Reading  │ Error  │Read. │  Done   │ Error │
└──────────┴────────┴──────┴─────────┴───────┘
```

```ruby
TRANSITIONS = {
  initial: { header: :reading },
  reading: { data: :reading, trailer: :done },
}
state = :initial
while state != :done && state != :error
  msg = get_next_message()
  state = TRANSITIONS[state][msg.msg_type] || :error
end
```

### Observer Pattern

An observable maintains a list of observers. When an event fires, it calls each observer's registered callback. Simple, but introduces coupling (observers must register with the observable).

### Publish/Subscribe

Solves observer coupling: publishers and subscribers communicate through **named channels**. Neither knows about the other. Channels can be async. Works across processes and machines.

### Reactive Streams

Treat events like collections. Filter, map, zip, combine event streams just like arrays. Enables elegant async code without callback hell.

---

## 🔑 Topic 30 — Transforming Programming

### 💡 Tip 49: Programming Is About Code, But Programs Are About Data
### 💡 Tip 50: Don't Hoard State; Pass It Around

Think of your program as a **series of transformations** — data flows in one end, is transformed step by step, and the result comes out the other end.

```
find . -type f | xargs wc -l | sort -n | tail -5

  directory name
  → list of files         (find)
  → list with line counts (wc -l)
  → sorted list           (sort -n)
  → top 5                 (tail -5)
```

### Pipeline Style (Elixir)

```elixir
def anagrams_in(word) do
  word
  |> all_subsets_longer_than_three_characters()
  |> as_unique_signatures()
  |> find_in_dictionary()
  |> group_by_length()
end
```

Each `|>` is a transformation. Data flows through code; code doesn't hide data.

### Why This Matters

```
OBJECT-ORIENTED:                  TRANSFORMATIONAL:
┌─────────────────────┐          ┌──────────────────────────┐
│ Objects hide data   │          │ Data flows through code  │
│ Objects talk to     │    →     │ Functions transform data  │
│ each other          │          │ Less coupling            │
│ More coupling       │          │ Easier to reuse          │
└─────────────────────┘          └──────────────────────────┘
```

### Error Handling in Pipelines

Wrap values in a result type: `{:ok, value}` or `{:error, reason}`. Each transformation passes errors through unchanged — the pipeline short-circuits naturally.

```elixir
File.read(file_name)
|> find_matching_lines(pattern)   # skipped if :error
|> truncate_lines()               # skipped if :error
```

---

## 🔑 Topic 31 — Inheritance Tax

### 💡 Tip 51: Don't Pay Inheritance Tax
### 💡 Tip 52: Prefer Interfaces to Express Polymorphism
### 💡 Tip 53: Delegate to Services: Has-A Trumps Is-A
### 💡 Tip 54: Use Mixins to Share Functionality

Inheritance causes **coupling**: the child is coupled to the parent, the parent's parent, and all code using the child is coupled to all ancestors.

```
INHERITANCE PROBLEM:

class Vehicle { def move_at(speed); ... }
class Car < Vehicle { ... }

top_level_code.my_car.move_at(30)
                       ↑ calls Vehicle's method

Developer renames move_at → set_velocity in Vehicle
→ Car breaks silently
→ Top-level code breaks
→ All because of inheritance coupling!
```

### Better Alternatives

| Alternative | Use when |
|---|---|
| **Interfaces/Protocols** | You want polymorphism — multiple types share a behavior contract |
| **Delegation** | You want to use functionality without inheriting the full API |
| **Mixins/Traits** | You want to share behavior across unrelated classes |

```java
// PREFER INTERFACES: Car and Phone are both Locatable
interface Locatable { Coordinate getLocation(); boolean locationIsValid(); }
class Car implements Locatable { ... }
class Phone implements Locatable { ... }

List<Locatable> items = new ArrayList<>();
items.add(new Car()); items.add(new Phone());
// Works polymorphically — no inheritance needed
```

---

## 🔑 Topic 32 — Configuration

### 💡 Tip 55: Parameterize Your App Using External Configuration

When values might change after deployment, keep them **outside the app**:

```
WHAT BELONGS IN CONFIGURATION:
  ✅ Credentials (DB, APIs)
  ✅ Logging levels and destinations
  ✅ Feature flags
  ✅ Environment-specific validation rules
  ✅ Tax rates, formatting rules
  ✅ Port numbers, cluster names
```

```
STATIC CONFIG (files):           CONFIG-AS-A-SERVICE:
┌──────────────────────┐        ┌──────────────────────────────┐
│ YAML / JSON file     │   →    │ Config API service           │
│ Read at startup      │        │ Multiple apps share config   │
│ Restart to change    │        │ Changes apply live, no restart│
└──────────────────────┘        └──────────────────────────────┘
```

Wrap configuration behind an API — don't access it as raw globals.

---

## 📊 Chapter Summary

```
┌──────────────────────────────────────────────────────────────────┐
│                    CHAPTER 5 MENTAL MODEL                        │
│                                                                  │
│  DECOUPLING       → Reduce connections; tell, don't ask         │
│                     One-dot rule; no global data                │
│                                                                  │
│  EVENTS           → FSMs for flow control, pub/sub for          │
│                     decoupled messaging, streams for async      │
│                                                                  │
│  TRANSFORMATIONS  → Programs are pipelines; data flows          │
│                     through functions; don't hoard state        │
│                                                                  │
│  INHERITANCE      → Causes coupling; prefer interfaces,         │
│                     delegation, and mixins instead              │
│                                                                  │
│  CONFIGURATION    → Move changeable values outside the app;     │
│                     parameterize everything that might vary     │
└──────────────────────────────────────────────────────────────────┘
```

---

## 💡 Key Takeaways

| # | Takeaway |
|---|---|
| 1 | **Coupling is the enemy of change** — minimize it everywhere |
| 2 | **Tell, don't ask** — let objects act on themselves |
| 3 | **Events are ubiquitous** — design systems to respond to them |
| 4 | **Think in transformations** — data flows through your program |
| 5 | **Inheritance tax is real** — use interfaces, delegation, mixins |
| 6 | **Externalize configuration** — code shouldn't know what might change |

---

*← [Chapter 4 — Pragmatic Paranoia](04-pragmatic-paranoia.md) | [Back to Index](../README.md) | Next: [Chapter 6 — Concurrency](06-concurrency.md) →*
