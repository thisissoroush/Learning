# Chapter 6: Choose Team-First Boundaries
## *How to split software systems along natural seams that match team cognitive load*

---

## 🎯 Core Concept

You can't just split a system however you like and expect teams to thrive. Software boundaries need to be chosen based on **what a single team can comfortably own, understand, and evolve** — not based on technical layers, not based on management convenience, and not based on what the legacy system happened to look like. This chapter gives you practical tools to find the right boundaries.

> **"Choose software boundaries to match team cognitive load."**

---

## 🏚️ The Hidden Monolith Problem

### Monoliths Aren't Just in Your Application Code

When people think "monolith," they think of a single large codebase. But monolithic coupling appears in many forms — some hidden:

```
TYPES OF HIDDEN MONOLITHS:

  1. MONOLITHIC APPLICATION
     Single large codebase, deployed as one unit
     → Everyone's changes block everyone else's

  2. MONOLITHIC DATABASE
     Multiple services sharing one database
     → Schema changes ripple everywhere
     → No team has clear data ownership

  3. MONOLITHIC PIPELINE
     Single CI/CD pipeline for all teams
     → One team's broken build blocks everyone
     → No team autonomy over release rhythm

  4. MONOLITHIC RELEASE
     All teams must release together
     → Coordination overhead grows exponentially
     → Blame game when anything goes wrong

  5. MONOLITHIC THINKING
     Leaders who think "we need everyone aligned on this"
     before any team can make a decision
     → Decision bottleneck at the top
```

### Coupling Is the Enemy of Flow

Any coupling between teams creates coordination overhead and slows delivery:

```
COUPLING COSTS:

  Two teams tightly coupled:
  
  Team A wants to change X
       → Must coordinate with Team B
       → Must wait for Team B's sprint cycle
       → Must run integrated tests together
       → Must release together
       → Multiple weeks of delay for a small change
  
  Two teams loosely coupled (via clean API):
  
  Team A wants to change X
       → Makes change independently
       → API contract unchanged
       → Deploys independently
       → Done in hours
```

---

## 🔍 Finding Fracture Planes

A **fracture plane** is a natural seam in a software system where it can be cleanly split. Good fracture planes make it easy for two pieces to evolve independently. Bad splits create more coupling than the original monolith.

```
FRACTURE PLANE CONCEPT:

  MONOLITH                    AFTER SPLIT
  ┌────────────────┐          ┌─────────┐   ┌─────────┐
  │                │          │         │   │         │
  │  ┌──────────┐  │    →     │Part A   │   │Part B   │
  │  │ fracture │  │          │         │   │         │
  │  │  plane   │  │          └────┬────┘   └────┬────┘
  │  └──────────┘  │               │              │
  │                │               └──── API ─────┘
  └────────────────┘          (clean interface between parts)
```

### The 6 Types of Fracture Planes

#### 1. Business Domain Bounded Context

The most natural and most recommended fracture plane. Split along the natural language and concepts of the business domain.

```
E-COMMERCE SYSTEM — BUSINESS DOMAIN SPLIT:

  Instead of splitting by technology layer:
  ┌────────────────────────────────────────────┐
  │ Frontend Layer  │  Backend Layer  │  DB     │
  └────────────────────────────────────────────┘
  
  Split by business domain (bounded context):
  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │  CATALOGUE   │  │   CHECKOUT   │  │   ORDERS     │
  │  (products,  │  │  (cart,      │  │  (orders,    │
  │   search,    │  │   payments,  │  │   shipping,  │
  │   pricing)   │  │   promo      │  │   returns)   │
  │              │  │   codes)     │  │              │
  └──────────────┘  └──────────────┘  └──────────────┘
  
  Each owns its own: frontend + backend + database
  Each is owned by: one stream-aligned team
```

> 💡 This aligns with **Domain-Driven Design (DDD)** concepts — bounded contexts map almost perfectly to team boundaries.

#### 2. Regulatory Compliance

Some parts of a system are subject to heavy regulatory scrutiny (PCI-DSS for payments, HIPAA for health data, GDPR for personal data). Splitting along these lines reduces the compliance surface area.

```
REGULATORY SPLIT:

  ┌─────────────────────────────────────────────┐
  │           Main Application                  │
  │                                             │
  │  ┌────────────────────────┐                 │
  │  │   PAYMENT PROCESSING   │ ← PCI scope     │
  │  │   (isolated, high      │                 │
  │  │    security controls)  │                 │
  │  └────────────────────────┘                 │
  │                                             │
  └─────────────────────────────────────────────┘
  
  After split:
  ┌──────────────────┐        ┌──────────────────┐
  │  Main App        │ ←API→  │  Payment Service │
  │  (out of PCI     │        │  (strict PCI     │
  │   scope)         │        │   compliance)    │
  └──────────────────┘        └──────────────────┘
```

#### 3. Change Cadence

Parts of the system that change at **very different rates** should be separated. Mixing fast-changing and slow-changing code creates friction.

```
CHANGE CADENCE SPLIT:

  HIGH CHANGE:                    LOW CHANGE:
  User interface features         Core business rules engine
  Marketing landing pages         Payment gateway integration
  A/B test variations             Regulatory reporting module
  
  → Separate these into different services
  → Fast-changing parts can deploy frequently
  → Slow-changing parts deploy rarely (but reliably)
  
  Mixing them means:
  - Fast changes are blocked by slow-moving parts
  - Risk of touching stable code when changing fast code
```

#### 4. Team Location

When teams are in different time zones or locations, split the system along **team location boundaries** so each team works on a system where they have full context and autonomy.

```
LOCATION SPLIT:

  Team in Berlin                Team in Singapore
  ┌──────────────────┐          ┌──────────────────┐
  │ European         │  ←API→  │ Asian             │
  │ User Management  │          │ User Management   │
  │ + EU features    │          │ + APAC features   │
  └──────────────────┘          └──────────────────┘
  
  Each team owns their region's system end-to-end.
  Time-zone friction → minimized.
```

#### 5. Risk Profile

High-risk parts of the system (financial transactions, sensitive data, critical paths) should be separated from low-risk parts to contain blast radius.

```
RISK PROFILE SPLIT:

  LOW RISK:              MEDIUM RISK:           HIGH RISK:
  Static content         User profiles          Payment processing
  Public API docs        Search results         Authentication
  Blog / marketing       Notifications          Fraud detection
  
  → Separate deployment, separate team, separate risk controls
  → A bug in the blog doesn't take down payments
```

#### 6. Technology

Sometimes different technologies create natural seams — embedded systems, IoT, mobile, cloud, legacy COBOL systems.

```
TECHNOLOGY FRACTURE PLANE:

  ┌────────────┐    ┌────────────┐    ┌────────────┐
  │  Mobile    │    │   Cloud    │    │    IoT     │
  │  Team      │    │  Backend   │    │  Firmware  │
  │  (Swift/   │    │  Team      │    │  Team      │
  │   Kotlin)  │    │  (Go/K8s)  │    │  (C/RTOS)  │
  └────────────┘    └────────────┘    └────────────┘
  
  Each team speaks its own language, owns its own stack.
  Clean API contracts at the boundaries.
```

---

## 🏭 Real Example: Manufacturing Analogy

The book uses a manufacturing analogy to explain fracture planes:

In a factory, you don't organize workers by tool (all saw operators in one room, all welders in another). You organize by **product stream**: all the people needed to build Product A work together in one area.

```
WRONG (by tool/skill):         RIGHT (by product stream):

  Saw Room → Weld Room           Product A Line:
  → Paint Room → Assemble          Saw + Weld + Paint + Assemble
  → Quality Room                   (dedicated to Product A)
  → Ship Room
                                 Product B Line:
  Problem: hand-offs,              Saw + Weld + Paint + Assemble
  wait times, no ownership         (dedicated to Product B)
  of the final product
                                 Result: faster, clearer ownership
```

---

## 🔍 Real Example: Poppulo — Finding Good Software Boundaries

Stephanie Sheehan (VP of Operations) and Damien Daly (Director of Engineering) at Poppulo, a communications software company, describe their process:

**Starting state:**
- Single large codebase
- Multiple teams all working in the same repo
- Constant merge conflicts, broken builds, deployment coordination hell

**Process:**
1. Mapped out where in the codebase changes clustered
2. Identified which parts changed together vs. independently
3. Found natural bounded contexts matching business domains
4. Split along those lines, giving each domain to one team

**Result:**
- Teams could deploy independently
- Fewer merge conflicts
- Clearer ownership
- Faster feature delivery

> **Lesson:** Don't guess at your fracture planes. Map where changes actually happen and let the data guide the split.

---

## 📋 The "Team Cognitive Load" Test for Boundaries

Before finalizing a software boundary, test it against team cognitive load:

```
BOUNDARY QUALITY TEST:

  Ask the team that will own this area:
  
  1. "Can you understand this entire area deeply enough to own it?"
     → YES: boundary is right-sized
     → NO: area is too large; find a sub-boundary
  
  2. "Does this area feel too small to be worth a team?"
     → YES: merge with adjacent area
     → NO: good
  
  3. "Do you constantly need to coordinate with Team X to make changes?"
     → YES: boundary is wrong; the coupling shows the two areas belong together
     → NO: boundary is correct
  
  4. "Could a new team member understand this area in 2-3 months?"
     → YES: cognitive load is manageable
     → NO: simplify or split further
```

---

## 🧩 Domain-Driven Design Alignment

Team Topologies aligns closely with **Domain-Driven Design (DDD)** concepts:

| DDD Concept | Team Topologies Equivalent |
|---|---|
| Bounded Context | Stream-aligned team boundary |
| Ubiquitous Language | Team's domain vocabulary |
| Context Map | Inter-team interaction diagram |
| Anti-Corruption Layer | API between teams (prevents coupling) |
| Shared Kernel | Complicated-subsystem team's output |

```
DDD BOUNDED CONTEXTS → TEAM BOUNDARIES:

  Customer Context          Order Context
  ┌──────────────────┐     ┌──────────────────┐
  │  "Customer"      │     │  "Order"         │
  │  means:          │     │  means:          │
  │  - Profile       │     │  - LineItems      │
  │  - Preferences   │     │  - ShippingAddr   │
  │  - Payment Info  │     │  - Status         │
  │                  │     │                  │
  │  Team: Customer  │     │  Team: Orders    │
  │  Profile Team    │     │  Team            │
  └──────────────────┘     └──────────────────┘
         │                        │
         └─── customer ID API ────┘
         (teams speak to each other
          via minimal, explicit interfaces)
```

---

## ⚠️ Bad Fracture Plane Anti-Patterns

### Anti-Pattern 1: Split by Technical Layer

```
❌ WRONG — Technical layer split:

  Frontend Team      Backend Team      Database Team
  ┌───────────┐     ┌───────────┐     ┌───────────┐
  │ All UIs   │←────│ All APIs  │←────│ All DBs   │
  └───────────┘     └───────────┘     └───────────┘
  
  Every feature requires all three teams → hand-off hell
  Nobody owns a feature end-to-end
```

### Anti-Pattern 2: Split by Team Preference

```
❌ WRONG — Split based on what teams "like" doing:

  "We're good at payments"  →  Team A takes payments + reporting + notifications
  "We like frontend work"   →  Team B takes all frontend regardless of domain
  
  Result: Teams that don't understand their domain
          and cross-cut business boundaries
```

### Anti-Pattern 3: Splitting Before Coupling Is Understood

```
❌ WRONG — Split too early:

  Assume microservices are better → split monolith into 50 services
  → Teams now own multiple micro-services each
  → Services are tightly coupled (shared database, synchronous calls)
  → More complexity, not less
  
  ✅ RIGHT:
  Understand the actual coupling first
  Find natural seams
  Split along THOSE seams
  Let each team own one piece completely
```

---

## 📐 Practical Steps to Find Your Fracture Planes

```
STEP-BY-STEP PROCESS:

  Step 1: MAP the current system
          → Draw all components, services, databases
          → Mark which teams touch which parts
  
  Step 2: ANALYZE change patterns
          → Which parts change together? (they belong together)
          → Which parts change independently? (fracture plane here)
  
  Step 3: IDENTIFY business domains
          → Use DDD techniques: event storming, domain mapping
          → Find bounded contexts
  
  Step 4: CHECK cognitive load
          → Would one team be able to own this domain?
          → Is it too big? Too small?
  
  Step 5: DRAW proposed boundaries
          → Map one team per boundary
          → Define API contracts between them
  
  Step 6: VALIDATE with teams
          → Ask each team: "Can you own this?"
          → Look for discomfort (signals poor boundary choice)
  
  Step 7: MIGRATE incrementally
          → Don't big-bang rewrite
          → Move one bounded context at a time
          → Validate after each step
```

---

## ✅ Key Takeaways

| # | Takeaway |
|---|---|
| 1 | **Hidden monoliths are everywhere** — not just application code (DB, pipeline, release, thinking) |
| 2 | **Fracture planes are natural seams** — where systems can be split cleanly |
| 3 | **Best fracture plane: business domain bounded context** — aligns with DDD |
| 4 | **Six types of fracture planes:** business domain, regulatory, change cadence, team location, risk, technology |
| 5 | **Test boundaries against cognitive load** — can one team own this comfortably? |
| 6 | **Avoid technical layer splits** — they create hand-off chains, not flow |
| 7 | **Analyze actual change patterns** before deciding where to split |
| 8 | **Migrate incrementally** — one bounded context at a time, validate as you go |

---

*← [Chapter 5 - The Four Fundamental Team Topologies](05-the-four-fundamental-team-topologies.md) | [Back to Index](../README.md) | Next: [Chapter 7 - Team Interaction Modes](07-team-interaction-modes.md) →*
