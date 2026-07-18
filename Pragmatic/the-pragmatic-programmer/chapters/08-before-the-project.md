# Chapter 8: Before the Project
## *Getting requirements right before writing a single line of code*

---

## 🎯 Core Concept

The biggest source of project failure isn't bad code — it's misunderstood requirements, impossible puzzles that were never questioned, and working in isolation. This chapter covers the critical work that happens **before and during** the early project phases.

> *"The hardest single part of building a software system is deciding precisely what to build."* — Fred Brooks

---

## 📌 Topics in This Chapter

| Topic | Title | Core Idea |
|---|---|---|
| 45 | The Requirements Pit | Requirements are never given; they're discovered |
| 46 | Solving Impossible Puzzles | Reframe the problem; challenge constraints |
| 47 | Working Together | Pair/mob programming and code ownership |
| 48 | The Essence of Agility | Agility is a way of thinking, not a ceremony |

---

## 🔑 Topic 45 — The Requirements Pit

### 💡 Tip 76: No One Knows Exactly What They Want
### 💡 Tip 77: Programmers Help People Understand What They Want
### 💡 Tip 78: Requirements Are Learned in a Feedback Loop

Users don't know what they want until they see something. Requirements are not given — they're discovered through conversation and iteration.

```
THE REQUIREMENTS MYTH:                THE REALITY:
┌────────────────────────┐           ┌──────────────────────────────┐
│ User has a clear idea  │           │ User has a vague goal        │
│ → Writes requirements  │    →      │ → Developer helps clarify    │
│ → Developer builds it  │           │ → User sees it and refines   │
│ → User is happy        │           │ → Repeat until it's right    │
└────────────────────────┘           └──────────────────────────────┘
         ❌ Never happens                        ✅ How it works
```

### The Requirements Distinction

> **Policy** vs **Requirement**: "Only an employee's supervisor can approve timesheets" is **policy** — it might change. "The system must not allow a timesheet to be processed without approval" is the **requirement**. Implement the requirement; configure the policy.

### Strategies for Good Requirements

```
✅ Become a user — shadow actual users doing actual work
✅ Document requirements as user stories, not specs
✅ Create a project glossary — define terms once, use everywhere
✅ Don't over-specify — the more precise the spec, the more wrong it can be
✅ Build prototypes, get feedback, iterate quickly
```

### The Dangers of Over-Specification

A 200-page requirements document is a statement of intent for a system that doesn't exist yet. By the time you've built it, the world has changed. Build a little, get feedback, adjust. The best requirements document is working software.

---

## 🔑 Topic 46 — Solving Impossible Puzzles

### 💡 Tip 82: Don't Think Outside the Box — Find the Box

When a problem seems impossible, the issue is often **a false constraint**. You've assumed a boundary that doesn't actually exist.

### The Classic Example: 9 Dots

```
Connect all 9 dots using 4 straight lines, without lifting your pen:

•  •  •
•  •  •
•  •  •

Most people assume the lines must stay inside the square.
They don't. The constraint doesn't exist.
```

### How to Find the Box

1. **Enumerate all constraints** — write them all down
2. **Question each one** — "Does this constraint actually exist? Says who?"
3. **Look for the real requirement** — what is the actual goal behind this "constraint"?
4. **Try solving the simpler version** — what if this restriction didn't exist?

```
WHEN STUCK ON AN "IMPOSSIBLE" PROBLEM:

  Ask: Is there an easier way to do this?
  Ask: Am I solving the right problem?
  Ask: Why must it be done this way?
  Ask: What if we did the opposite?
  Ask: Who decided this was a constraint?
```

---

## 🔑 Topic 47 — Working Together

### 💡 Tip 83: Don't Go It Alone

Programming is a social activity. Isolation produces worse code and slower learning.

```
PAIR PROGRAMMING:
  Two developers, one keyboard.
  One writes code (driver), one thinks about strategy (navigator).
  Roles switch frequently.
  
  Benefits:
  ✅ Immediate code review
  ✅ Shared understanding of the code
  ✅ Two brains find more problems than one
  ✅ Junior devs learn from seniors in real-time
```

```
MOB PROGRAMMING:
  Whole team works on one thing, one screen.
  One driver, everyone else navigates.
  Extreme but effective for complex problems.
```

### Code Ownership

The best code is **owned by the team**, not by individuals. When any team member can modify any part of the codebase:
- No knowledge silos
- No "hero developers" who become bottlenecks
- Shared accountability for quality

---

## 🔑 Topic 48 — The Essence of Agility

### 💡 Tip 84: Agile Is Not a Noun; Agile Is How You Do Things
### 💡 Tip 85: Good Design Makes Things Easy to Change

"Agile" has been turned into a product, a process, a religion. The authors helped launch it and want to clarify what it actually means.

```
THE AGILE MANIFESTO (SIMPLIFIED):

  Individuals and interactions   > processes and tools
  Working software               > comprehensive documentation
  Customer collaboration         > contract negotiation
  Responding to change           > following a plan
```

The manifesto isn't anti-process or anti-documentation — it's about **priorities**. When the two sides conflict, favor the left side.

### The Real Essence of Agility

```
REAL AGILITY = THE ABILITY TO RESPOND TO CHANGE

  1. Work out where you are now
  2. Make the smallest meaningful change toward your goal
  3. Evaluate the result
  4. Repeat
  
  This works for code, for processes, for teams, for organizations.
```

### Why "Doing Agile" Often Fails

```
CARGO CULT AGILE:                    REAL AGILITY:
┌───────────────────────────┐       ┌──────────────────────────────┐
│ Two-week sprints ✓        │       │ We deliver working software  │
│ Daily standups ✓          │       │ We listen to users           │
│ Retrospectives ✓          │       │ We change when we learn      │
│ Story points ✓            │       │ We keep design flexible      │
│                           │       │                              │
│ But: no user feedback     │       │ Ceremonies are secondary     │
│ But: design is rigid      │       │ Feedback is primary          │
│ But: code is hard to change│      │                              │
└───────────────────────────┘       └──────────────────────────────┘
        ❌ "Doing" Agile                     ✅ Being Agile
```

Good design (DRY, decoupled, orthogonal) is what makes agility possible. Agility without good design is just moving faster toward chaos.

---

## 📊 Chapter Summary

```
┌──────────────────────────────────────────────────────────────────┐
│                    CHAPTER 8 MENTAL MODEL                        │
│                                                                  │
│  REQUIREMENTS     → Discovered, not received. Iterate with       │
│                     users. No one knows exactly what they want.  │
│                                                                  │
│  CONSTRAINTS      → Challenge every assumption. The "impossible" │
│                     problem may have a false boundary.           │
│                                                                  │
│  COLLABORATION    → Work together; pair and mob programming      │
│                     produce better code than isolation           │
│                                                                  │
│  AGILITY          → Respond to change. Work in small steps.      │
│                     Ceremonies don't make you agile; feedback    │
│                     loops and good design do.                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## 💡 Key Takeaways

| # | Takeaway |
|---|---|
| 1 | **Requirements are a journey** — users discover what they want by seeing your work |
| 2 | **Separate policy from requirement** — implement requirements, configure policy |
| 3 | **Question all constraints** — many "impossible" problems have false assumptions |
| 4 | **Don't code alone** — pairing and collaboration produce better outcomes |
| 5 | **Agility is a mindset** — respond to feedback, not a ceremony checklist |
| 6 | **Good design enables agility** — you can't be agile with brittle code |

---

*← [Chapter 7 — While You Are Coding](07-while-you-are-coding.md) | [Back to Index](../README.md) | Next: [Chapter 9 — Pragmatic Projects](09-pragmatic-projects.md) →*
