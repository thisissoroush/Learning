# Chapter 7: Team Interaction Modes
## *How teams should communicate — and when each mode creates flow vs. friction*

---

## 🎯 Core Concept

Having the right team types (Chapter 5) and the right boundaries (Chapter 6) is not enough. Teams also need to **interact with each other** — and the *way* they interact determines whether they accelerate or block each other.

This chapter defines **three interaction modes** that cover every legitimate way teams need to work together. Using the wrong mode for the context creates waste, confusion, and hidden coupling. Using the right mode produces clarity, speed, and clean interfaces.

> **"Well-defined interactions are key to effective teams."**

---

## 🔀 The Three Essential Team Interaction Modes

```
THE THREE INTERACTION MODES

  Mode 1: COLLABORATION         Mode 2: X-AS-A-SERVICE    Mode 3: FACILITATING
  ─────────────────────         ──────────────────────    ────────────────────
  
  Team A ◄────────► Team B      Team A ──API──► Team B    Team A (enables)
  (close, joint work)           (consumer/provider)             │
                                                                 ▼
  When: discovery,              When: clear interface     Team B (learns)
  innovation, high              exists, stable service,
  uncertainty                   execution mode            When: one team needs
                                                          to uplift another
  Cost: HIGH bandwidth          Cost: LOW bandwidth       Cost: MEDIUM bandwidth
  (overhead, needs              (clear expectations,      (temporary, then
   coordination)                 less coordination)        ends)
```

---

## 1️⃣ Collaboration Mode

### What It Looks Like

Two (or more) teams work **closely together** for a period of time, with **overlapping responsibilities and shared work**. This is intentional blurring of team boundaries.

```
COLLABORATION MODE:

  ┌──────────────────────────────────────────┐
  │                                          │
  │   Team A  ◄────── Daily work ──────►  Team B  │
  │            ◄── Shared codebase  ───►           │
  │            ◄── Joint planning   ───►           │
  │            ◄── Mob programming  ───►           │
  │                                          │
  └──────────────────────────────────────────┘
  
  Boundary between teams: deliberately blurred
  Communication: high bandwidth, daily, rich
```

### When to Use Collaboration

✅ **Good for:**
- When there is **high uncertainty** — no one knows the answer yet
- **Discovering** new architectures, new technologies, new approaches
- When two teams need to **quickly learn from each other**
- Short-term **innovation sprints** where exploration is the goal

❌ **Bad for:**
- Steady-state feature delivery (too much overhead)
- When clear interfaces already exist (don't fix what works)
- Long-term operation (collaboration fatigue sets in)

### The Hidden Cost of Collaboration

```
COLLABORATION OVERHEAD CALCULATION:

  2 teams of 7 people each collaborating closely:
  
  → Joint planning sessions: 14 people × 2 hours/week = 28 person-hours
  → Context switching between team norms: ongoing overhead
  → Shared backlog management: additional coordination
  → Merge conflict resolution: shared codebase friction
  
  Collaboration is EXPENSIVE. Use it with purpose and time limits.
  
  Rule: Collaboration should have a CLEAR END STATE
  → "We will collaborate until we've defined the API boundary"
  → NOT: "We'll just work together forever"
```

### Advantages and Disadvantages

| Advantages | Disadvantages |
|---|---|
| Rapid knowledge transfer | High cognitive overhead |
| Faster innovation and discovery | Can create long-term dependency |
| Team members develop new skills | Blurs ownership responsibility |
| Reveals missing platform capabilities | Expensive (communication bandwidth) |

---

## 2️⃣ X-as-a-Service Mode

### What It Looks Like

One team **provides** a service, API, or tool. Another team **consumes** it. The interaction is **low bandwidth** — the consuming team doesn't need to know how it works internally, just how to use the interface.

```
X-AS-A-SERVICE MODE:

  ┌─────────────┐          ┌─────────────────────────┐
  │  Consumer   │          │      Provider           │
  │  Team       │ ──API──► │      Team               │
  │             │          │                         │
  │  Uses the   │          │  Owns the service,      │
  │  service    │          │  maintains it, evolves  │
  │  (black box)│          │  it as a product        │
  └─────────────┘          └─────────────────────────┘
  
  Communication: low bandwidth
  Documentation: self-service
  Support: SLA-driven (not ad-hoc)
```

### Examples of X-as-a-Service

| Provider | Service | Consumer |
|---|---|---|
| Platform team | Kubernetes cluster provisioning | Stream-aligned teams |
| Complicated-subsystem team | Recommendation engine API | Multiple stream teams |
| Security team | Authentication SDK | All service teams |
| Data team | Analytics pipeline | Product teams |
| Internal tools team | CI/CD templates | All engineering teams |

### When to Use X-as-a-Service

✅ **Good for:**
- When the **interface is stable and well-understood**
- When the service is **used by many teams** (scale justifies the investment)
- When teams are in **execution mode** (not discovery)
- When you want **maximum team autonomy** for consuming teams

❌ **Bad for:**
- When the service is brand new and evolving rapidly (use collaboration first)
- When the consuming team needs to influence the service deeply
- When the "service" is actually too coupled to be a clean API

### What Makes a Good X-as-a-Service Experience

```
CHARACTERISTICS OF A GOOD X-AS-A-SERVICE:

  ✅ Self-service documentation (teams don't need to call you)
  ✅ Clear API versioning (teams know when to upgrade)
  ✅ Stable interface (changes don't break consumers)
  ✅ Support SLA (known response times for issues)
  ✅ Easy onboarding (new consumers get started in hours)
  ✅ Feedback mechanism (consumers can suggest improvements)
  
  ❌ Anti-patterns:
  ❌ "Ask Bob" — informal tribal knowledge required
  ❌ Constant breaking changes
  ❌ No documentation ("read the source code")
  ❌ Shared Slack channel as the only support mechanism
```

### Advantages and Disadvantages

| Advantages | Disadvantages |
|---|---|
| Clear ownership boundaries | Provider may be slow to respond to consumer needs |
| Low communication overhead | Risk of provider becoming disconnected from consumer reality |
| Maximum autonomy for consumer | Innovation can be slower (interface negotiation required) |
| Scalable (one provider serves many) | Interface may not perfectly fit all consumers |

---

## 3️⃣ Facilitating Mode

### What It Looks Like

One team **helps, coaches, or unblocks** another team. The facilitating team doesn't do the work — they help the other team become capable of doing it themselves.

```
FACILITATING MODE:

  ┌──────────────────┐              ┌──────────────────┐
  │  Facilitating    │ ─── helps ──► │  Facilitated     │
  │  Team            │              │  Team            │
  │                  │              │                  │
  │  (Enabling team  │              │  (grows in       │
  │   or expert)     │              │   capability)    │
  └──────────────────┘              └──────────────────┘
  
  Direction: one-way (facilitator → facilitated)
  Duration: temporary (until capability is transferred)
  Success: when the facilitated team no longer needs help
```

### When to Use Facilitating

✅ **Good for:**
- When a team needs to learn a **new practice** (CI/CD, TDD, observability)
- When a team is **blocked** and needs temporary expert help
- When **enabling teams** are coaching stream-aligned teams

❌ **Bad for:**
- Long-term technical ownership (enabling teams don't own the result)
- When the capability gap is too large (team needs fundamental restructuring, not coaching)

### Advantages and Disadvantages

| Advantages | Disadvantages |
|---|---|
| Builds team capability permanently | Requires skilled facilitators |
| Doesn't create permanent dependency | Slow if facilitated team isn't motivated |
| Enables teams to become more autonomous | Hard to measure progress |
| Temporarily adds expertise without headcount | Risk of facilitator doing the work for them |

---

## 🗺️ Which Mode for Which Team Type?

```
PRIMARY INTERACTION MODES PER TEAM TYPE:

  STREAM-ALIGNED TEAM:
  → Primary: X-as-a-Service (from platform, subsystem teams)
  → Secondary: Collaboration (during discovery phases)
  → Occasional: Facilitating (when receiving coaching)

  ENABLING TEAM:
  → Primary: Facilitating (their whole purpose)
  → Secondary: Collaboration (to understand stream team context)

  COMPLICATED-SUBSYSTEM TEAM:
  → Primary: X-as-a-Service (serves stream teams via API)
  → Secondary: Collaboration (when API design is new/uncertain)

  PLATFORM TEAM:
  → Primary: X-as-a-Service (serves stream teams)
  → Secondary: Collaboration (when building new platform capabilities)
  → Occasional: Facilitating (onboarding new stream teams)
```

---

## 📊 Team Interaction Mode Decision Guide

```
WHICH INTERACTION MODE TO USE?

  Start: What is the current situation?
  
  ┌────────────────────────────────────────────────────┐
  │  Is the solution well-understood AND the interface │
  │  between teams is stable?                          │
  │                                                    │
  │  YES → X-AS-A-SERVICE                              │
  │  NO → Continue...                                  │
  └────────────────────────────────────────────────────┘
                      │ NO
                      ▼
  ┌────────────────────────────────────────────────────┐
  │  Does one team need to LEARN something from        │
  │  or be COACHED by another team?                    │
  │                                                    │
  │  YES → FACILITATING                                │
  │  NO → Continue...                                  │
  └────────────────────────────────────────────────────┘
                      │ NO
                      ▼
  ┌────────────────────────────────────────────────────┐
  │  Are both teams discovering something new together,│
  │  with high uncertainty about the outcome?          │
  │                                                    │
  │  YES → COLLABORATION (time-limited!)               │
  └────────────────────────────────────────────────────┘
```

---

## 🏢 Real Example: IBM around 2014

Eric Minick (Program Director for Continuous Delivery, IBM) described how IBM used multiple interaction modes simultaneously across different teams:

```
IBM INTERACTION MODE DIVERSITY (2014):

  Large product (middleware/DevOps tooling)

  Scenario A: New team learning CI/CD
  → Enabling team FACILITATES stream team
  → Embedded for 4-6 weeks
  → Then steps back
  
  Scenario B: Platform providing deployment infrastructure
  → Platform team provides X-AS-A-SERVICE
  → Stream teams self-serve via API
  → SLA-driven support
  
  Scenario C: Two teams discovering new architecture
  → COLLABORATION mode for 2-3 month spike
  → Output: agreed interface design
  → Transition to X-as-a-Service after
  
  Key insight: DIFFERENT MODES running SIMULTANEOUSLY
               across different team pairs
```

---

## ⚠️ Mode Mismatches — Common Mistakes

### Mistake 1: Treating Everything as Collaboration

```
❌ WRONG:
  "We're all one team here" → everyone collaborates with everyone
  → No clear boundaries → monolithic thinking
  → Slow decisions, unclear ownership
  → Conway's Law warning: this will produce a monolith
  
  ✅ RIGHT:
  Most inter-team interaction should be X-as-a-Service
  Collaboration is reserved for discovery phases
```

### Mistake 2: Premature X-as-a-Service

```
❌ WRONG:
  "We'll expose an API" → service is new, interface changes weekly
  → Consumer teams constantly broken
  → "API contract" becomes a source of friction
  
  ✅ RIGHT:
  Collaborate first to discover the right interface
  Then graduate to X-as-a-Service when stable
```

### Mistake 3: Enabling Teams That Never Leave

```
❌ WRONG:
  Enabling team gets comfortable embedded in stream team
  → Stream team becomes dependent
  → Enabling team becomes a shared service team in disguise
  
  ✅ RIGHT:
  Set explicit timebox for facilitating engagement
  Define "done" criteria: "when stream team can do X independently"
  Enabling team moves on to next team
```

---

## 🔄 Mode Evolution Over Time

The interaction mode between two teams should **change over time** as the relationship matures:

```
TYPICAL MODE EVOLUTION:

  New technology / new area:
  COLLABORATION (2-6 months) → discover interface
         │
         ▼
  Interface discovered:
  FACILITATING (1-3 months) → transfer knowledge
         │
         ▼
  Knowledge transferred, interface stable:
  X-AS-A-SERVICE (ongoing) → consumer self-serves
  
  
  Trigger for reverting:
  If stream team needs to influence platform significantly
  → Temporary COLLABORATION period → update interface → back to XaaS
```

---

## 🧭 Choosing Basic Team Organization

The right interaction modes also help you decide basic team organization:

```
INTERACTION MODE → PROXIMITY IMPLICATION:

  COLLABORATION:     Teams should be in the same location
                     (or very close in virtual space)
                     → Shared Slack workspace, shared standups
  
  X-AS-A-SERVICE:    Teams can be anywhere
                     → All communication via API and docs
  
  FACILITATING:      Facilitating team should be near the facilitated team
                     → Temporary physical/virtual proximity
```

---

## ✅ Key Takeaways

| # | Takeaway |
|---|---|
| 1 | **Three interaction modes cover all inter-team communication needs** — collaboration, X-as-a-Service, facilitating |
| 2 | **Collaboration = discovery mode** — high bandwidth, time-limited, for uncertainty |
| 3 | **X-as-a-Service = execution mode** — low bandwidth, stable, for known interfaces |
| 4 | **Facilitating = capability building mode** — one-directional, temporary, coaching |
| 5 | **Most daily inter-team interaction should be X-as-a-Service** — not collaboration |
| 6 | **Match mode to context** — wrong mode for the situation creates waste or dependency |
| 7 | **Modes should evolve** — discovery → facilitating → X-as-a-service as maturity grows |
| 8 | **Multiple modes run simultaneously** across different team pairs in the same org |

---

*← [Chapter 6 - Choose Team-First Boundaries](06-choose-team-first-boundaries.md) | [Back to Index](../README.md) | Next: [Chapter 8 - Evolve Team Structures](08-evolve-team-structures.md) →*
