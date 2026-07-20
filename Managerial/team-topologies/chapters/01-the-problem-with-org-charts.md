# Chapter 1: The Problem with Org Charts
## *Why traditional org structures fail modern software delivery — and what to do instead*

---

## 🎯 Core Concept

The org chart is a **lie**. It shows you the official reporting hierarchy, but it tells you nothing about how work actually gets done. Real communication in organizations is messy, lateral, and constantly breaking through the "accepted lines." Designing software delivery around an org chart is like navigating a city using a map of train routes — it's related, but dangerously incomplete.

> **The org chart gives you the formal structure. What you actually need is a model that captures the *informal* and *value-creation* structures — where real work happens.**

---

## 📊 The Three Org Structures (Not Just One)

Most leaders think there's one org structure — the chart. But author Niels Pflaeging identifies **three** that coexist in every organization:

```
┌────────────────────────────────────────────────────────────────┐
│              THREE STRUCTURES IN EVERY ORGANIZATION            │
│                                                                │
│  1. FORMAL STRUCTURE     The official org chart               │
│     (the chart)          Useful for: legal, compliance        │
│                          Risk: people mistake it for reality  │
│                                                               │
│  2. INFORMAL STRUCTURE   The "realm of influence"             │
│     (the shadow)         Who trusts who, who talks to who     │
│                          Where: hallways, Slack DMs           │
│                                                               │
│  3. VALUE CREATION       How work ACTUALLY gets done          │
│     STRUCTURE            Inter-personal and inter-team rep    │
│     (the real one)       reputation drives decisions          │
└────────────────────────────────────────────────────────────────┘
```

> 💡 **Key insight:** The key to successful knowledge work is the **interaction between the informal structure and the value creation structure** — not the org chart.

---

## 📉 What the Org Chart Gets Wrong

### The Communication Gap

```
ORG CHART (what leadership thinks)          ACTUAL COMMS (what really happens)

      CEO                                         CEO
       │                                          ─┼─────────────
    ┌──┴──┐                                    ┌──┘┬──────────┐
   VP    VP                                   VP  ─┤─  VP     │
    │     │                                    │   ╲   │      │
 Team   Team                                Team ──╱ Team ────┤
   A     B                                    A       B       │
                                              └───────────────┘
                                          (dotted lines everywhere)
```

People reach out to **whoever they depend on** to get work done. They bend the rules. They communicate laterally. They form informal networks. The org chart captures none of this.

### The Local Optimization Trap

Decisions based on org-chart structure tend to **optimize for part of the organization** while ignoring upstream and downstream effects.

**Real example:**
```
Teams adopt cloud + infrastructure-as-code
→ Time to provision infrastructure: weeks → minutes ✅

But...

Every change still requires deployment approval
from a board that meets once a week
→ Delivery speed: still weekly ❌

The local optimization was real. The bottleneck moved — not removed.
```

> ⚠️ **Systems thinking** says: find the **largest bottleneck** in the whole system and eliminate it. Then repeat. Don't optimize parts while the whole is broken.

---

## 🔄 The Org Chart Is Always Out of Date

Just like a software architecture document becomes outdated the moment development starts, an org chart is **always out of sync with reality**.

```
Month 0:    Org chart created after reorg
Month 1:    Teams start communicating outside the lines
Month 3:    Shadow teams and informal channels form
Month 6:    New project needs a team that "doesn't exist"
Month 9:    Next reorg announced because "the structure isn't working"
Month 12:   Repeat.
```

This cycle is exhausting for workers and counterproductive for the business.

---

## 🧠 Conway's Law (First Mention — Expanded in Chapter 2)

In 1968, Mel Conway discovered that:

> **"Organizations which design systems are constrained to produce designs which are copies of the communication structures of these organizations."**

This is the most important single idea in this book. If your teams communicate in silos, your software will be siloed. If your teams communicate in cross-functional streams, your software will reflect that.

**Example (Eric Raymond's humorous version):**
> *"If you have four groups working on a compiler, you'll get a 4-pass compiler."*

---

## 💡 Cognitive Load: The Hidden Bottleneck

When teams are spread too thin across too many responsibilities, they hit their **cognitive load limit**.

```
COGNITIVE LOAD OVERLOAD MODEL:

Team gets new responsibility ──►  Team adapts, adds work ──►
Team gets more responsibility ──► Context switching begins ──►
Team gets even more ──────────► Motivation drops ─────────►
                                 Quality drops ────────────►
                                 Delivery slows ───────────►
                                 Team becomes a BOTTLENECK
```

**Real example — OutSystems Engineering Productivity Team:**
- 8-person team responsible for: CI, CD, infrastructure automation, test execution
- Sprint planning was chaotic — requests from multiple product areas simultaneously
- Constant context switching killed motivation
- Dan Pink's three elements of intrinsic motivation were all broken:
  - **Autonomy** → crushed by constant juggling of priorities
  - **Mastery** → "jack of all trades, master of none"
  - **Purpose** → too many domains = no clear mission

---

## 🚧 Obstacles to Fast Flow

The book identifies the main obstacles that hurt software delivery speed:

```
                    OBSTACLES TO FAST FLOW
                    
  ┌──────────────────────────────────────────────────────┐
  │                                                      │
  │  • Disengaged teams                                  │
  │  • Pushing against Conway's Law                      │
  │  • Painful reorgs every few years                    │
  │  • Flow slowed by software too big for teams         │
  │  • Too many surprises (lack of visibility)           │
  │  • Confusing org design options                      │
  │  • Teams pulled in many directions                   │
  │                                                      │
  └──────────────────────────────────────────────────────┘
```

---

## 🆕 Team Topologies: A New Way of Thinking

Team Topologies provides:

| Element | Description |
|---|---|
| **4 fundamental team types** | Stream-aligned, Platform, Enabling, Complicated-Subsystem |
| **3 core interaction modes** | Collaboration, X-as-a-Service, Facilitating |
| **Conway's Law awareness** | Use team structure to drive desired architecture |
| **Cognitive load management** | Match team size and responsibilities to cognitive capacity |
| **Sensing organization** | Structure evolves as context changes |

The goal: **teams that produce software aligned to customer needs, easier to build, run, and own.**

```
          TEAM TOPOLOGIES CORE DIAGRAM

  Stream-aligned    Complicated-
      team          subsystem       Enabling    Platform
  ┌──────────┐       team            team        team
  │          │    ┌──────────┐    ┌────────┐  ┌────────┐
  │  PRIMARY │    │ EXPERT   │    │ COACH  │  │ INFRA  │
  │  DELIVERY│    │ SUPPORT  │    │ TEACH  │  │ TOOLS  │
  └──────────┘    └──────────┘    └────────┘  └────────┘

  ─────────────────────────────────────────────────────
  
  Collaboration       X-as-a-Service      Facilitating
  (close teamwork)    (API boundary)      (coaching)
```

---

## 🏢 Industry Example: OutSystems (Part 1)

The Engineering Productivity team at OutSystems:
- Was 5 years old, grew to 8 people
- Took on: CI, CD, test execution, infrastructure automation
- Sprint planning became chaotic
- Constant context switching throughout sprints → motivation dip
- This is the **cognitive overload anti-pattern** in action

**Result:** Team functioned as a bottleneck rather than an enabler.

**Fix (covered in Chapter 3):** Split into domain-specific microteams.

---

## 📋 Naomi Stanford's 5 Rules for Org Design

The book references these heuristics for when and how to redesign your organization:

| # | Rule |
|---|---|
| 1 | Design when there is a **compelling reason** |
| 2 | Develop **options** for deciding on a design |
| 3 | Choose the **right time** to design |
| 4 | **Look for clues** that things are out of alignment |
| 5 | **Stay alert to the future** |

> Team Topologies adds the **dynamic and sensing aspects** required for technology organizations that traditional org design approaches are missing.

---

## ✅ Key Takeaways

| # | Takeaway |
|---|---|
| 1 | **Org charts don't show real communication** — they show formal hierarchy |
| 2 | **Three structures coexist** — formal, informal, and value-creation |
| 3 | **Conway's Law is real** — software mirrors team communication structures |
| 4 | **Cognitive load is a hard limit** — teams spread too thin become bottlenecks |
| 5 | **Optimize the whole system**, not just local parts |
| 6 | **Team Topologies** provides 4 team types + 3 interaction modes for fast flow |

---

*← [Back to Index](../README.md) | Next: [Chapter 2 - Conway's Law and Why It Matters](02-conways-law-and-why-it-matters.md) →*
