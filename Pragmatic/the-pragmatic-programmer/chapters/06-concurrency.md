# Chapter 6: Concurrency
## *Writing code that does many things at once — safely*

---

## 🎯 Core Concept

Concurrency is no longer exotic — it's a requirement. Users interact while data is being fetched and external services are being called, all at the same time. This chapter teaches you to reason about and write concurrent code without shooting yourself in the foot.

> **Concurrency** = code that *acts as if* running simultaneously (fibers, threads, processes)
> **Parallelism** = code that *actually runs* simultaneously (multiple cores/machines)

---

## 📌 Topics in This Chapter

| Topic | Title | Core Idea |
|---|---|---|
| 33 | Breaking Temporal Coupling | Don't impose sequence where none is needed |
| 34 | Shared State Is Incorrect State | Shared mutable state is the root of concurrency bugs |
| 35 | Actors and Processes | Concurrency without shared state |
| 36 | Blackboards | Decoupled, coordinated agents via a shared space |

---

## 🔑 Topic 33 — Breaking Temporal Coupling

### 💡 Tip 56: Analyze Workflow to Improve Concurrency

**Temporal coupling** = your code imposes an ordering that isn't actually required by the problem. Method A *must* be called before B, even when there's no reason for that.

### Activity Diagrams Reveal True Parallelism

Making a piña colada — naively done in strict sequence:
```
Open blender → Get mix → Put mix in → Add rum → Add ice → Blend → Get glasses → Serve
```

But many steps can happen in parallel:
```
┌──────────────────────────────────────────────────────┐
│ PARALLEL START:                                      │
│   Open mix        ─────────────────┐                │
│   Measure rum     ─────────────────┼──► Blend ──► Serve
│   Get glasses     ─────────────────┘                │
│   Get umbrellas   ─────────────────┘                │
└──────────────────────────────────────────────────────┘
```

Look for activities that take **clock time but not CPU time** — waiting for DB queries, external API calls, user input. These are opportunities for concurrency.

---

## 🔑 Topic 34 — Shared State Is Incorrect State

### 💡 Tip 57: Shared State Is Incorrect State
### 💡 Tip 58: Random Failures Are Often Concurrency Issues

**The Diner Problem:**
- Waiter 1 checks: "Is there pie?" → sees 1 slice → promises it to customer
- Waiter 2 checks: "Is there pie?" → sees 1 slice → promises it to customer
- Only one waiter can actually deliver. Someone gets disappointed.

```
PROBLEM: Non-atomic check-then-act

Waiter1:   check(pie_count > 0)  →  promise  →  take_pie
                                 ↑
                         Waiter2 runs here:
                                 check(pie_count > 0) → promise → error!
```

### Solutions

**1. Semaphores:** Lock before checking. Only one can hold the semaphore.
```ruby
case_semaphore.protect() {
  if @slices.size > 0
    update_sales_data(:pie)
    return @slices.shift
  else
    false
  end
}
```

**2. Make the resource transactional:** Move the check-and-take into the resource itself as an atomic operation.

```ruby
slice = display_case.get_pie_if_available()  # atomic: check AND take
if slice
  give_pie_to_customer()
end
```

**The lesson:** Managing shared state manually is hard and error-prone. The next topic offers a better way.

---

## 🔑 Topic 35 — Actors and Processes

### 💡 Tip 59: Use Actors For Concurrency Without Shared State

**An actor** is an independent processor with:
- Its own private state (no shared memory)
- A mailbox (message queue)
- Behavior: process one message at a time

```
ACTOR MODEL:

  Customer ──[hungry for pie]──► Waiter ──[get slice]──► PieCase
                                                             │
                                 Waiter ◄──[add to order]───┤
  Customer ◄──[put on table]──────────────────────────────┘
```

### Key Properties of Actors

```
✅ No shared state between actors
✅ Messages are one-way (fire and forget)
✅ Each actor processes messages sequentially
✅ Actors can create other actors
✅ Works identically on 1 CPU or 1000 CPUs
✅ No locks, no semaphores, no deadlocks
```

### Why This Is Better

| Shared State Approach | Actor Approach |
|---|---|
| Need semaphores/mutexes | No locking needed |
| Deadlock risk | No deadlocks (no shared state) |
| Hard to reason about | Each actor is simple and isolated |
| Debugging is a nightmare | Trace messages to find bugs |

---

## 🔑 Topic 36 — Blackboards

### 💡 Tip 60: Use Blackboards to Coordinate Workflow

A **blackboard** is a shared space where independent agents post facts and read others' facts — like a detective board where multiple detectives contribute clues.

```
┌────────────────────────────────────────────────────┐
│           BLACKBOARD                               │
│                                                    │
│  H. Dumpty: Accident or Murder?                    │
│  ─────────────────────────────────────────────     │
│  [Photo: cracked shell]    [Witness: saw wall]     │
│  [Phone logs: threatening] [Gambling debts: yes]   │
│  ──► Detective Holmes: "Note connection: debts+calls│
└────────────────────────────────────────────────────┘

Agents post facts. Other agents read and react.
No agent needs to know about any other agent.
```

### Blackboard Properties

- Agents are **independent** — they don't know about each other
- Data arrives in **any order** — agents react when relevant facts appear
- Agents have **different skills** — specialists focus on their domain
- The system **evolves** — new agents can be added without changing others

### Modern Implementations

Today's message brokers (Kafka, NATS) implement blackboard-like semantics: persistent event logs + pattern-based retrieval. Microservice architectures often operate as informal blackboards.

---

## 📊 Chapter Summary

```
┌──────────────────────────────────────────────────────────────────┐
│                    CHAPTER 6 MENTAL MODEL                        │
│                                                                  │
│  TEMPORAL COUPLING → Don't impose sequence where none required   │
│                      Use activity diagrams to find parallelism   │
│                                                                  │
│  SHARED STATE      → Is incorrect state. Concurrent access to    │
│                      mutable data causes race conditions         │
│                                                                  │
│  ACTORS            → Concurrency without shared state           │
│                      Private state + message passing = safe     │
│                                                                  │
│  BLACKBOARDS       → Agents post/read facts independently       │
│                      No orchestrator; data drives the process   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 💡 Key Takeaways

| # | Takeaway |
|---|---|
| 1 | **Concurrency is required** — the real world is asynchronous |
| 2 | **Remove temporal coupling** — don't serialize what can be parallel |
| 3 | **Shared mutable state is the root of concurrency bugs** |
| 4 | **Random failures in concurrent code often mean a race condition** |
| 5 | **Actors eliminate shared state** — the safest concurrency model |
| 6 | **Blackboards enable decoupled coordination** — agents work independently |

---

*← [Chapter 5 — Bend, or Break](05-bend-or-break.md) | [Back to Index](../README.md) | Next: [Chapter 7 — While You Are Coding](07-while-you-are-coding.md) →*
