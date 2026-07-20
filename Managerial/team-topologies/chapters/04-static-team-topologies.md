# Chapter 4: Static Team Topologies
## *Common patterns, dangerous anti-patterns, and how to choose the right topology for your context*

---

## 🎯 Core Concept

Before defining the "perfect" team structure, we need to understand two things: (1) there is **no single correct topology** that works for all organizations, and (2) there are **clearly wrong topologies** that consistently fail. This chapter surveys the landscape of team patterns that exist in real organizations — which ones work, which don't, and what factors should guide your choice.

> **Ad hoc or constantly changing team designs slow software delivery. But copying a "successful" org structure from another company without understanding the context can be equally harmful.**

---

## ❌ Team Anti-Patterns

Before looking at what works, recognize what doesn't. Two persistent anti-patterns that hurt almost every organization:

### Anti-Pattern 1: Ad Hoc Team Design

```
AD HOC DESIGN CYCLE:

  New project starts → Random people assigned → "Team" is just a label
        ↓
  Project ends → Team dissolves → Knowledge disappears
        ↓
  Next project → Different random people → Start from zero
        ↓
  Organization wonders why delivery is slow and quality is poor
```

Teams need **time to form**. Constantly reshuffling people prevents teams from ever reaching the "performing" stage.

### Anti-Pattern 2: Constant Reorganization

```
REORG CYCLE:

  Org is slow → Leadership decides structure is wrong
       ↓
  Reorg: new teams, new managers, new reporting lines
       ↓
  Teams spend 3–6 months adapting, trust rebuilding, norms re-establishing
       ↓
  Org is still slow (because it wasn't the structure that was the problem)
       ↓
  Leadership decides structure is wrong again...
```

> ⚠️ Reorgs destroy the informal and value-creation structures (from Chapter 1) that took years to build. The cost is almost never measured.

---

## 🌊 Design for Flow of Change

The key insight for topology design: **optimize for the flow of change**, not for technical specialization or management convenience.

```
NOT OPTIMIZED FOR FLOW:                 OPTIMIZED FOR FLOW:

  Business                               Business
  Request                                Request
     │                                      │
     ▼                                      ▼
  BA Team → (wait) →                    Stream-Aligned Team
  Dev Team → (wait) →                   (has all skills needed)
  QA Team → (wait) →                          │
  Ops Team → (wait) →                         ▼
  Security Review → (wait) →             Live Feature ✅
  Release Board
     │
     ▼
  Live Feature (weeks/months later)
```

A team optimized for flow has:
- All the skills needed to take a feature from idea to production
- Minimal dependency on other teams for day-to-day work
- Clear ownership of its area of the system
- Autonomy to make decisions within its domain

---

## 🎵 The Spotify Model (and Its Limitations)

Spotify popularized a model of **Squads, Tribes, Chapters, and Guilds** around 2012. Henrik Kniberg and Anders Ivarsson described it as:

```
SPOTIFY MODEL:

  GUILD (cross-tribe community of interest)
  ┌──────────────────────────────────────────────────────────┐
  │                    TRIBE (~50 people)                    │
  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
  │  │  Squad   │  │  Squad   │  │  Squad   │  │  Squad   │ │
  │  │(~8 ppl)  │  │(~8 ppl)  │  │(~8 ppl)  │  │(~8 ppl)  │ │
  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
  │                                                          │
  │  Chapter: engineers of same specialty across squads     │
  └──────────────────────────────────────────────────────────┘
```

**What Spotify got right:**
- Small, autonomous squads with full-stack ownership
- Tribes limited to Dunbar's ~50 number
- Guilds for cross-organizational learning
- Physical co-location of squads within a tribe

**What people miss when copying it:**
- Spotify evolved this model iteratively — it wasn't designed up front
- The model was **context-specific** to Spotify's size, culture, and maturity
- Copying the *form* without understanding the *forces* that shaped it rarely works
- Spotify themselves acknowledged the model had significant problems by 2020

> 💡 **Lesson:** Don't copy Spotify (or Netflix, or Amazon). Understand the *principles* behind their structures and apply those to your context.

---

## ✅ Successful Team Patterns

### Pattern 1: Feature Teams (Stream-Aligned Teams)

A cross-functional team that owns a complete vertical slice of functionality, from user interface to database to deployment.

```
FEATURE TEAM STRUCTURE:

  ┌────────────────────────────────────────────────┐
  │              Feature Team (7 people)            │
  │                                                │
  │  Product   Frontend  Backend   DB     DevOps   │
  │  Owner       Dev       Dev     Dev    Engineer  │
  │                                                │
  │  Owns: everything from user story → production │
  └────────────────────────────────────────────────┘
```

**When it works best:**
- When the team has sufficient technical depth in each area
- When subsystems are well-defined and loosely coupled
- When the platform is stable and reduces operational overhead

**Failure condition:** Feature teams struggle when they need to constantly negotiate with platform teams, DBA teams, security teams, etc. for every change.

---

### Pattern 2: Product Teams with Shared Support Functions

```
PRODUCT + SHARED SUPPORT:

  Product Team A ←─── SRE / Platform team ───→ Product Team B
                       (supporting both,
                        X-as-a-Service)
```

Product teams own their services. A shared SRE or platform team reduces overhead by providing shared infrastructure as a service.

**The relationship between SRE and App Teams:**

```
SRE TEAM RELATIONSHIP MODEL:

  Phase 1: New service
    App Team ←── close collaboration ──→ SRE Team
    (SRE embeds to help build operational practices)
    
  Phase 2: Mature service
    App Team ──── SRE consults ──── SRE Team
    (SRE provides consultation + on-call if needed)
    
  Phase 3: Service that doesn't meet SRE standards
    App Team ← SRE hands back ownership
    (App team must fix before SRE re-engages)
    
  (Based on Google's SRE model)
```

---

### Pattern 3: Ericsson's Cross-Subsystem Feature Teams

Ericsson (a telecom equipment company) used feature teams supported by cross-subsystem functions:

```
ERICSSON MODEL:

  Cross-subsystem Feature Teams
  (own end-to-end features across the product)
  
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │Feature   │  │Feature   │  │Feature   │
  │Team A    │  │Team B    │  │Team C    │
  └──────────┘  └──────────┘  └──────────┘
        │              │             │
        └──────────────┴─────────────┘
                       │
           ┌───────────┴───────────┐
           │  Subsystem Functions  │
           │  (not teams — roles   │
           │   embedded in teams)  │
           └───────────────────────┘
```

---

## 🔧 Considerations When Choosing a Topology

Four factors heavily influence which team topology is right for your organization:

### Factor 1: Technical and Cultural Maturity

```
MATURITY SPECTRUM:

  LOW MATURITY                         HIGH MATURITY
  ──────────────────────────────────────────────────
  • Manual deployments                 • Full CI/CD
  • No monitoring                      • Observability
  • No testing culture                 • Test-first
  • Waterfall mindset                  • DevOps mindset
  
  Needs:                               Can use:
  • Enabling teams                     • Stream-aligned teams
  • Coaching first                       with high autonomy
  • Platform investment                • X-as-a-Service patterns
```

### Factor 2: Organizational Scale

```
SCALE vs. TEAM TOPOLOGY:

  Small org (< 50 engineers):
  → Simple flat structure, everyone works closely
  → 1–3 stream-aligned teams + lightweight platform

  Medium org (50–500 engineers):
  → Clear stream-aligned teams
  → Dedicated platform team
  → Possibly enabling team(s)

  Large org (500+ engineers):
  → Multiple streams with full team topologies per stream
  → Platform as a product team
  → Enabling teams per capability area
  → Complicated-subsystem teams for specialist areas
```

### Factor 3: Engineering Discipline

```
ENGINEERING DISCIPLINE vs. TEAM INDEPENDENCE:

  Low discipline        Medium discipline      High discipline
  (no standards)        (some standards)       (strong practices)
        │                     │                       │
        ▼                     ▼                       ▼
  Teams can't be       Teams can work         Teams can work
  truly autonomous     semi-independently     fully independently
  (need enabling       (need occasional       (X-as-a-service
  teams)               collaboration)          interactions)
```

### Factor 4: Interaction Patterns Needed

```
  If teams need to:               Use this interaction mode:
  ─────────────────               ──────────────────────────
  Discover something new          Collaboration (close contact)
  Use a stable service/API        X-as-a-Service (low bandwidth)
  Learn a new practice            Facilitating (coaching)
```

---

## 🏥 Real Example: Healthcare Organization (DevOps Transformation)

A healthcare organization (via Accenture) had this starting state:
- Development and operations in complete silos
- All deployments manual, requiring ops approval
- No shared tooling between dev and ops

**Topology evolution:**

```
Phase 1 (months 1-6):
  Dev Team A ←── close collaboration ──→ Ops Team
  (DevOps team temporarily embedded to help)
  
Phase 2 (months 6-12):
  Dev Team A ──── new: DevOps practices embedded ────
  (Dev teams now own their own deployments)
  Ops team transitions to platform/SRE model
  
Phase 3 (months 12+):
  Stream-Aligned Teams (own CI/CD)
  Platform Team (provides infrastructure as service)
```

---

## 🔄 TransUnion — Evolution of Team Topologies (Part 1)

Ian Watson (Head of DevOps at TransUnion) described how they evolved their structure:

**Starting point:** Traditional dev + ops silos. Long release cycles, high friction.

**Evolution:**
1. Created a dedicated "System Build" team to own CI/CD pipeline
2. Created a "Platform Build" team to own infrastructure
3. Over time, these teams converged and then split again as capabilities matured

> **Lesson:** Team topologies should evolve as the organization's capabilities and product maturity evolve. There's no "final state."

---

## 🚧 Splitting Responsibilities to Break Silos

One powerful pattern: **deliberately split a team's responsibilities** to force empowerment of other teams.

```
SILO BREAKING PATTERN:

  Before:
  ┌─────────────────────────┐
  │      Operations Team    │
  │  (owns ALL infra,       │
  │   all deployments,      │
  │   all monitoring)       │
  └─────────────────────────┘
  ↑ every team depends on them → bottleneck

  After (split responsibilities):
  ┌─────────────────────────┐   ┌──────────────────────┐
  │  Platform Team          │   │  Stream-Aligned Teams │
  │  (owns shared infra     │   │  (own their own       │
  │   as self-service)      │   │   deployments +       │
  └─────────────────────────┘   │   monitoring)         │
                                └──────────────────────┘
  Platform = X-as-a-Service → stream teams are empowered
```

---

## 📋 Use DevOps Topologies to Evolve the Organization

The "DevOps Topologies" (Matthew Skelton's original work, pre-book) identified two types of patterns:

| Type | Description |
|---|---|
| **Good Topologies** | Anti-silos, cross-functional ownership, platform as product |
| **Anti-Patterns** | Dev-throws-over-wall-to-ops, NoOps (no ops involvement), DevOps team as a silo |

```
KEY ANTI-PATTERN — "DevOps Team" as a silo:

  ❌ WRONG:
  Dev Team → throws code over wall → DevOps Team → deploys
  
  This just recreates the silo problem with a new name.
  The DevOps team becomes a bottleneck, not an enabler.
  
  ✅ RIGHT:
  Dev team owns CI/CD + deployments + monitoring
  Platform team provides the tools as self-service
```

---

## ✅ Key Takeaways

| # | Takeaway |
|---|---|
| 1 | **There is no universal topology** — choose based on context |
| 2 | **Ad hoc team design and constant reorgs are anti-patterns** — both destroy flow |
| 3 | **Optimize for flow of change**, not for technical specialization |
| 4 | **Spotify's model is context-specific** — don't copy the form, understand the principles |
| 5 | **Four factors guide topology choice:** maturity, scale, engineering discipline, interaction needs |
| 6 | **Splitting responsibilities can break silos** — empower stream teams to own their deployments |
| 7 | **Topologies must evolve** — there's no final state; sense and adapt |

---

*← [Chapter 3 - Team-First Thinking](03-team-first-thinking.md) | [Back to Index](../README.md) | Next: [Chapter 5 - The Four Fundamental Team Topologies](05-the-four-fundamental-team-topologies.md) →*
