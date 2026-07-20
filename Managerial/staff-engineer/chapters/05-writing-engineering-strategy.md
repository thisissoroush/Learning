# Chapter 5: Writing Engineering Strategy
## *From Design Docs to Strategy to Vision — Bottom-Up, Not Top-Down*

---

## 🎯 Core Concept

Engineering strategy sounds mystical, but it's actually mundane — and that's a feature, not a bug. Good strategy is boring. It's specific. It emerges from real decisions already being made, not from brilliant ideas in isolation.

> *"I kind of think writing about engineering strategy is hard because good strategy is pretty boring."* — Camille Fournier

**The recipe:** Write 5 design docs → extract 1 strategy. Write 5 strategies → extrapolate 1 vision.

---

## 🗺️ The Strategy Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    THE ENGINEERING STRATEGY PIPELINE                     │
│                                                                          │
│   DESIGN DOCS          STRATEGY              VISION                     │
│   ───────────          ────────              ──────                     │
│                                                                          │
│   5 design docs   →    Pull out the      →   Extrapolate 5             │
│                        common            →   strategies 2-3            │
│   Specific             decisions &           years forward             │
│   Real problems        tradeoffs                                        │
│   Grounded                               The implied future            │
│                        "When should      if all strategies             │
│   Examples:            we use Redis?"    hold                          │
│   - Service design     "SQL vs NoSQL"    "Robust belief                │
│   - API changes        "Monolith vs      in the future"                │
│   - Data models        services"                                        │
│                                                                          │
│   TIMEFRAME: Now    ──── 6-12 months ──── 2-3 years ────              │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📄 Step 1: Write Great Design Documents

Design documents (also called RFCs, tech specs, or DUCKs at Uber) describe decisions and tradeoffs for specific projects.

### When to Write One

Write a design doc when:
- Capabilities will be used by numerous future projects
- Project meaningfully impacts users
- Work takes more than a month of engineering time

### How to Write Well

| Principle | What It Means |
|---|---|
| **Start from the problem** | Clearer problem = more obvious solutions |
| **Keep templates simple** | Overloaded templates = fewer docs written |
| **Gather widely, write alone** | Collect input from all stakeholders, but one author writes it |
| **Prefer good over perfect** | Ship the document and iterate — don't wait for the perfect version |

```
BEST PRACTICE: Reread designs AFTER implementing them.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Where did implementation deviate from your plan?
  What caused those deviations?
  → This is how you improve future designs.
```

---

## 📋 Step 2: Synthesize Design Docs Into Strategy

After 5 design docs, read them all together. Look for:
- **Controversial decisions** that came up multiple times
- **Tradeoffs** that were hard to agree on
- **Patterns** in what you chose and why

### What Good Strategy Looks Like

```
BAD STRATEGY:                     GOOD STRATEGY:
──────────────────────────        ──────────────────────────────
"Use Redis for caching."          "Use Redis when:
                                   - Data fits in memory
No rationale.                      - You need sub-ms latency
Can't adapt it later.              - Durability is not required
                                  Use PostgreSQL when durability
                                  matters or queries are complex.
                                  Rationale: we learned this from
                                  the 3 outages in Q2 where Redis
                                  was used for durable storage."
```

### Strategy Writing Rules

1. **Start where you are** — don't wait for perfect information; just start
2. **Write the specifics** — stop when you start generalizing; generic = useless
3. **Be opinionated** — strategies that don't take a position don't help anyone
4. **Show your work** — explain WHY, not just WHAT, so others can evolve it

> ⚠️ Some of the best strategies you write will seem "too obvious." Write them anyway. "Which databases do we use for which use cases?" is a strategy worth writing.

---

## 🔭 Step 3: Extrapolate Strategies Into a Vision

Take 5 strategies, extrapolate their implications 2-3 years forward. Weave the threads together, resolve contradictions. That's your vision.

### Vision Writing Rules

| Rule | Why It Matters |
|---|---|
| **2-3 years out** | Far enough to be meaningful; close enough to be realistic |
| **Ground in business and users** | Visions disconnected from business get ignored by leadership |
| **Optimistic, not audacious** | Best possible outcome if things go well — not "infinite resources" fantasy |
| **Stay concrete and specific** | Generic statements are easy to agree with and useless to navigate by |
| **Keep it 1-2 pages** | Most people won't read long documents; force yourself to be compact |

### The Muted Response Problem

When you finish a vision, the urge is to share it widely and receive acclaim. You won't. The primary audience for a vision is people writing strategies — a small group. A great vision is so obvious that it bores rather than excites.

> **How to measure a vision:** Read a design doc from 2 years ago and one from last week. If there's marked improvement, your vision is working.

---

## ✅ Key Takeaways

| # | Takeaway |
|---|---|
| 1 | **Good strategy is boring** — specific, practical, and grounded in real decisions |
| 2 | **Build bottom-up**: design docs → strategy → vision (not the other way around) |
| 3 | **Design docs need a problem, not a solution** — clarity of problem drives quality of solution |
| 4 | **Bad strategy states a policy without rationale** — context-free rules become incomprehensible |
| 5 | **Show your work** — the rationale lets others evolve the strategy as context changes |
| 6 | **Visions fail if they're disconnected from users and the business** |
| 7 | **Measure vision impact by improvement over time**, not by initial excitement |

---

*← [Chapter 4 - Work on What Matters](04-work-on-what-matters.md) | [Back to Index](../README.md) | Next: [Chapter 6 - Managing Technical Quality](06-managing-technical-quality.md) →*
