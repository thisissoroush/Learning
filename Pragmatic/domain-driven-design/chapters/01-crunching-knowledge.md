# Chapter 1 — Crunching Knowledge

> *"It is the creativity of brainstorming and massive experimentation, leveraged through a model-based language and disciplined by the feedback loop through implementation, that makes it possible to find a knowledge-rich model and distill it."*

---

## 🎯 Core Concept

Building good software is fundamentally about **understanding the domain** well enough to model it. The process of extracting this understanding from domain experts and collaborating to shape it into a model is called **knowledge crunching**.

The key insight: domain knowledge doesn't arrive pre-packaged. It requires **active collaboration**, constant refinement, and willingness to throw away early assumptions.

---

## 🔬 What Is Knowledge Crunching?

Imagine financial analysts: they don't just look at raw numbers. They sift through data, combine and recombine it, looking for the underlying meaning — a simple presentation of what really matters.

Domain modelers do the same thing with **business knowledge**:

```
Raw Information (Domain Experts' Heads)
           │
           ▼
    ┌─────────────────┐
    │  KNOWLEDGE      │
    │  CRUNCHING      │  ← Active collaboration, brainstorming,
    │                 │    trying many models, rejecting most
    └─────────────────┘
           │
           ▼
    Abstract Concepts that capture the essential truth
    of the domain and support a practical design
```

Knowledge crunching is **not a solitary activity**. It requires:
- Developers
- Domain experts
- Users of existing systems
- Prior experience with related systems

---

## 🖥️ The PCB Design Story (A Real Example)

Evans tells the story of building software for printed circuit board (PCB) design — a domain he knew nothing about.

**Initial challenge:** PCB engineers spoke in terminology he didn't understand. He couldn't just ask them "what should the software do?" — their answers were always too low-level (read a file, sort it, write it back).

**The breakthrough approach:** Start drawing interaction diagrams together. Let the engineers correct you constantly.

```
Early discovery session:

Developer: "I'll call these components 'components'"
Expert 1:  "We call them 'component instances' — there can be
            many of the same component"

Developer: "A net connects pins?"  
Expert 1:  "Yes — a pin belongs to only one component instance
            and connects to only one net"
Expert 2:  "Also every net has a topology..."
```

Each correction builds the **shared vocabulary** and the **model** simultaneously.

**What emerged:** A model centered on `Net`, `Pin`, `Component Instance`, and `Component Type` — concepts that made the probe simulation feature understandable and implementable.

```
              ┌──────────────────┐
              │  Component Type  │ ← defines push behavior
              │  (pushes map)    │
              └────────┬─────────┘
                       │ 1
                       │
              ┌────────▼─────────┐       ┌─────────┐
              │  Component       │──────▶│   Net   │
              │  Instance        │       │         │
              └──────────────────┘       └────┬────┘
                                              │
                                         ┌────▼────┐
                                         │   Pin   │
                                         └─────────┘
```

---

## 5️⃣ Ingredients of Effective Modeling

The PCB project succeeded because of five specific practices:

| # | Ingredient | What It Means |
|---|-----------|---------------|
| 1 | **Binding model and implementation** | The prototype forged an early link between model and code — and maintained it |
| 2 | **Cultivating a language based on the model** | Everyone used the same terms — no translation needed |
| 3 | **Developing a knowledge-rich model** | Objects had behavior and enforced rules — not just data containers |
| 4 | **Distilling the model** | Concepts were added when needed and **dropped** when they weren't |
| 5 | **Brainstorming and experimenting** | Hundreds of experimental variations were tried quickly in discussion |

---

## 🔄 The Knowledge Crunching Feedback Loop

The old **waterfall** approach fails because knowledge flows in one direction:

```
WATERFALL (broken):
Business Experts → Analysts → Programmers → Code
         (knowledge doesn't come back up)
```

Iterative but shallow also fails:

```
SHALLOW ITERATION (broken):
Expert describes feature → Developer builds it → Repeat
         (no abstraction, no principles, just features)
```

The DDD approach:

```
DDD KNOWLEDGE CRUNCHING (working):

    Domain Expert ──────────────────────────┐
         ▲                                  │
         │ model                            │ understanding
         │ questions                        ▼
    Developer ◄────────────────── Running Software
         │                                  ▲
         │ implementation                   │ feedback
         └──────────────────────────────────┘
```

---

## 🌊 Continuous Learning

When a team starts a project, they **never know enough**. Domain knowledge is:
- Fragmented across many people
- Mixed with irrelevant information
- Lost when people leave or reorganize

The solution is **continuous learning** — team members who deliberately study the domain, not just the technology.

> The accumulated knowledge in the minds of a stable core team makes them more effective knowledge crunchers.

---

## 💎 Deep Models

Initial models are almost always **naive and superficial**. They're based on what's visible — the nouns in a requirements document, the obvious entities.

Evans's shipping example: he initially modeled ships and containers. After months of crunching, the model evolved to focus on:
- **Transfers of legal responsibility** (not physical movement)
- **Bill of lading** (not loading operations)
- **Itinerary** (not ship locations)

```
SHALLOW MODEL:           →       DEEP MODEL:
Ships move cargo         →       Responsibility transfers between parties
Containers loaded        →       Legal documents govern hand-offs
Physical locations       →       Chain of custody from shipper to consignee
```

> *"Useful models seldom lie on the surface."*

Deep models emerge through iteration. You can't plan for them — you discover them.

---

## 💡 Key Takeaways

| Insight | Implication |
|---------|-------------|
| Knowledge crunching is collaborative | Developers must talk to domain experts constantly, not just at the start |
| Initial models are naive | Expect to throw away your first model — that's normal |
| Bind model to implementation early | A prototype that runs forces the model to be concrete |
| Cultivate shared language | When you can discuss requirements using model terms, the model is working |
| Drop concepts ruthlessly | A concept not needed in the solution should not be in the model |
| Continuous learning is required | Domain understanding compounds — protect your knowledgeable team members |

---

*← [Back to Domain-Driven Design](../README.md)*
