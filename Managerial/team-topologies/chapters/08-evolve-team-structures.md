# Chapter 8: Evolve Team Structures with Organizational Sensing
## *How to build an organization that detects when its structure needs to change — and actually changes it*

---

## 🎯 Core Concept

Team topologies are not a destination — they're a **dynamic, living system** that must continuously adapt to changes in technology, business context, product maturity, and team capability. An organization that locks in a structure and never revisits it will eventually be fighting against its own topology.

The goal is to build an **organizational sensing capability**: the ability to detect when the current team structure is no longer serving you — and to evolve it deliberately, not reactively.

> **"Organizations should be viewed as complex and adaptive organisms rather than mechanistic and linear systems."**
> — Naomi Stanford

---

## 📡 How Much Collaboration Is Right?

The right amount of collaboration between any two teams depends on **where they are in the product/discovery cycle**:

```
COLLABORATION LEVEL vs. DISCOVERY PHASE:

  HIGH       ████████████████░░░░░░░░░░░░░░░░
  COLLABO-   ████████████████░░░░░░░░░░░░░░░░
  RATION     ████████████████░░░░░░░░░░░░░░░░
             │                │
  LOW        ░░░░░░░░░░░░░░░░████████████████
  COLLABO-   ░░░░░░░░░░░░░░░░████████████████
  RATION     ░░░░░░░░░░░░░░░░████████████████
             │                │
             DISCOVERY        EXECUTION
             (high            (clear
              uncertainty)     direction)
  
  When you're discovering:   → High collaboration, overlapping teams
  When you're executing:     → Low collaboration, X-as-a-Service boundaries
```

> ⚠️ **The trap:** Many organizations use high collaboration mode during execution phase — because it feels like teamwork. But it creates friction and slows delivery.

---

## 🌱 Accelerate Learning and Adoption of New Practices

When an organization needs to adopt a new technology or practice (Kubernetes, observability, domain-driven design), there's a deliberate pattern:

### The Adoption Lifecycle

```
NEW CAPABILITY ADOPTION PATTERN:

  Phase 1: SPIKE / EXPERIMENT (Collaboration)
  ┌──────────────────────────────────────────┐
  │  Small team explores new technology       │
  │  (cloud team + embedded team)            │
  │  → Learn what works, what doesn't        │
  └──────────────────────────────────────────┘
                      │
                      ▼
  Phase 2: ENABLING / FACILITATING
  ┌──────────────────────────────────────────┐
  │  Enabling team builds pattern library    │
  │  Embeds with stream teams to teach       │
  │  → Each team learns, owns their usage    │
  └──────────────────────────────────────────┘
                      │
                      ▼
  Phase 3: X-AS-A-SERVICE (Platform)
  ┌──────────────────────────────────────────┐
  │  Platform team provides self-service     │
  │  → Stream teams consume autonomously     │
  │  → Enabling team moves to next topic     │
  └──────────────────────────────────────────┘
```

### Real Example: uSwitch — Kubernetes Adoption

Paul Ingles (Head of Engineering, uSwitch) describes how adopting Kubernetes drove organizational change:

```
USWITCH KUBERNETES JOURNEY:

  Before:
  → Monolithic deployment pipeline
  → Ops team bottleneck
  → Slow releases (days to weeks)
  
  Phase 1: Cloud + embedded team (collaboration)
  → Small "Cloud" team experimented with Kubernetes
  → Embedded with stream teams to understand needs
  → Discovered what the right platform shape should be
  
  Phase 2: Platform team forms
  → Cloud team became the Platform team
  → Built self-service Kubernetes tooling
  → Enabled stream teams to deploy independently
  
  Phase 3: Stream team autonomy
  → Stream teams own their own deployments
  → Platform team focuses on platform reliability + new capabilities
  → Release frequency: days to multiple times per day
  
  KEY: The team topology CHANGED as the technology matured
```

---

## 🔄 Constant Evolution of Team Topologies

Team topologies should evolve through multiple mechanisms:

### 1. Teams Merging

When two teams are collaborating so closely that the separation creates more overhead than value, **merge them** into one team.

```
TEAM MERGE:

  Before:           After:
  Team A ←→ Team B  →  Team AB
  (constant         (single team,
   collaboration)    clear ownership)
  
  Signal to merge: teams can't make a decision
                   without involving each other
```

### 2. Teams Splitting

When a team has grown too large (approaching Dunbar's limit) or has taken on too many domains, **split** it.

```
TEAM SPLIT:

  Before:              After:
  Team A               Team A1 (stream A)
  (8 people,     →     Team A2 (stream B)
   2 products,
   cognitive        Each team: 4-5 people
   overload)         Each team: 1 product
```

### 3. Teams Creating a New Team Type

When a team has developed a capability that other teams repeatedly need, it may be time to **extract it into a platform or enabling team**.

```
CAPABILITY EXTRACTION:

  Stream Team A         Platform Team (new)
  ┌────────────────┐    ┌─────────────────────┐
  │ Product work   │    │ Self-service tool   │
  │ + CI/CD tool   │ →  │ (used by all teams) │
  │ maintenance    │    │                     │
  └────────────────┘    └─────────────────────┘
  
  Stream Team A now focuses on product only
  Platform team serves all stream teams
```

---

## 📊 Real Example: TransUnion — Evolution Over Time (Part 2)

Dave Hotchkiss (Platform Build Manager, TransUnion) describes the full evolution:

```
TRANSUNION TOPOLOGY EVOLUTION:

  PHASE 1: Starting state (silos)
  Dev Team ─────────────────────── Ops Team
  (build)                          (deploy/run)
  → Long release cycles
  → High friction between teams
  
  PHASE 2: System Build + Platform Build teams formed
  ┌──────────────────┐  ┌──────────────────┐
  │  System Build    │  │  Platform Build  │
  │  Team            │  │  Team            │
  │  (CI/CD focus)   │  │  (infra focus)   │
  └──────────────────┘  └──────────────────┘
  → Better, but still separate
  
  PHASE 3: Collaboration between the two teams
  ┌──────────────────────────────────────────┐
  │  System Build + Platform Build           │
  │  (working closely to align pipelines)   │
  └──────────────────────────────────────────┘
  
  PHASE 4: Merged into single team
  ┌──────────────────────────────────────────┐
  │  Combined Platform Team                  │
  │  (CI/CD + infrastructure together)      │
  └──────────────────────────────────────────┘
  
  PHASE 5: Split back into Dev and Ops streams
  Dev Teams (stream-aligned) → own their CI/CD
  Ops Team → pure platform/SRE model
  
  KEY: Each phase was right for that moment.
       There was no "final" correct structure.
```

---

## 🌟 Real Example: Sky Betting & Gaming (Part 2)

Michael Maibaum (Chief Architect) describes continued evolution:

```
SKY BET PLATFORM EVOLUTION:

  Stage 1: Central "Platform" team (monolith of a team)
  → All infrastructure managed by one team
  → Bottleneck: stream teams waiting for platform

  Stage 2: Platform split into "Platform Feature Teams"
  → Each feature team owns a slice (deployments, monitoring, etc.)
  → Stream teams can self-serve most needs
  → Platform feature teams have their own backlogs

  Stage 3: Some platform teams become stream-aligned
  → Platform capabilities that are stable → X-as-a-Service
  → Platform capabilities still evolving → collaboration mode
  → Platform teams treat their platform as a product
  
  RESULT: Stream teams deploy ~50x more frequently
          Platform team satisfaction increased significantly
```

---

## 🔭 Triggers for Evolution of Team Topologies

How do you know when to change your team structure? Look for these signals:

### Signal Category 1: Delivery Is Slowing

```
SLOW DELIVERY SIGNALS:

  ❶ Teams constantly waiting for approvals from other teams
  ❷ Release trains requiring synchronization across many teams
  ❸ "Integration hell" — changes work in isolation but not together
  ❹ Bugs found by customers that "should have been caught"
  ❺ Features that take 3x longer than estimated
  
  POSSIBLE CAUSES:
  → Too much collaboration (unclear boundaries)
  → Wrong team boundaries (need to split or merge)
  → Missing platform capability (stream teams doing platform work)
  → Enabling team needed but doesn't exist
```

### Signal Category 2: Team Health Is Degrading

```
TEAM HEALTH SIGNALS:

  ❶ Team members feel overwhelmed or burned out
  ❷ "We're always firefighting"
  ❸ Low morale, people leaving
  ❹ Team can't find time for improvements / technical debt
  ❺ Sprint planning is chaotic
  
  POSSIBLE CAUSES:
  → Cognitive load too high (split the team or reduce scope)
  → Too many domains (need domain specialization)
  → Missing platform capability (too much undifferentiated work)
```

### Signal Category 3: Architecture Is Drifting

```
ARCHITECTURE DRIFT SIGNALS:

  ❶ Services that should be independent are deeply coupled
  ❷ Database shared by teams that shouldn't share one
  ❸ "We can't change X without affecting Y"
  ❹ Different teams have different understanding of shared concepts
  
  POSSIBLE CAUSES:
  → Team boundaries don't match Conway's Law
  → Fracture planes chosen incorrectly
  → Teams that shouldn't collaborate are collaborating too much
```

### The Sensing Heatmap

```
ORGANIZATIONAL SENSING HEATMAP:

  Measure these regularly (quarterly):
  
  Metric                      Green    Yellow    Red
  ─────────────────────────   ─────    ──────    ───
  Deployment frequency        Daily    Weekly    Monthly+
  Lead time for changes       Hours    Days      Weeks+
  Team cognitive load (self)  Low      Medium    High
  Inter-team communication    Needed   Managed   Chaotic
  Platform adoption           >80%     50-80%    <50%
  Team stability              >18mo    12-18mo   <12mo
```

---

## 🏗️ Combining Topologies for Greater Effectiveness

### The "Platform Wrapper" Pattern

When a third-party or legacy system is too complex for stream teams to use directly, a small team can build a **wrapper platform** around it:

```
PLATFORM WRAPPER:

  ┌────────────────────────────────────────────────┐
  │             PLATFORM WRAPPER TEAM              │
  │  (simplifies complex 3rd party for other teams)│
  └────────────────────────────────────────────────┘
                          │
                          ▼
  ┌────────────────────────────────────────────────┐
  │         COMPLEX THIRD-PARTY SYSTEM             │
  │    (Salesforce, SAP, legacy mainframe, etc.)   │
  └────────────────────────────────────────────────┘
                          ↑
  Stream teams see only the wrapper's clean API
  They never interact with the complex underlying system
```

### New Service + "Business as Usual" (BAU) Split

When a team is responsible for both maintaining an old system AND building a new one, the competing priorities cause both to suffer. Solution: separate them.

```
NEW SERVICE + BAU SPLIT:

  Before:
  ┌──────────────────────────────────────────────┐
  │  Team A                                      │
  │  (maintains old system + builds new service) │
  │  → neither gets adequate attention           │
  └──────────────────────────────────────────────┘
  
  After:
  ┌────────────────────┐    ┌────────────────────┐
  │  BAU Team          │    │  New Service Team  │
  │  (maintains old    │    │  (builds new       │
  │   system)          │    │   product)         │
  └────────────────────┘    └────────────────────┘
  
  Old system gets proper care.
  New product gets proper focus.
  Eventually: BAU team absorbs new service when ready.
```

---

## 🧭 Self-Steer Design and Development

The most mature organizations build an **inherent sensing ability** — teams and leaders can detect when the topology needs to evolve without waiting for a top-down reorg.

### Signs of a Self-Steering Organization

| Indicator | Description |
|---|---|
| **Teams flag cognitive load themselves** | Teams speak up when they're overloaded before it becomes a crisis |
| **Inter-team communication problems are surfaced** | Teams flag when they can't work without excessive coordination |
| **Platform gaps are reported** | Stream teams identify where the platform is missing capabilities |
| **Team topology changes are proposed bottom-up** | Teams suggest their own splits, merges, or mode changes |
| **Leadership acts on signals** | Leaders treat topology evolution as normal, not as a sign of failure |

### Conway's Law as a Sensing Tool

```
USING UNEXPECTED COMMS AS A SIGNAL:

  Expected: Team A talks to Platform Team via API
  Unexpected: Team A talks to Platform Team daily via Slack
  
  Signal: The API isn't good enough. Something is missing.
  Action: Investigate, improve platform, or temporarily collaborate
  
  Expected: Team A and Team B interact rarely (different domains)
  Unexpected: Team A and Team B have daily joint standups
  
  Signal: The boundary is wrong. Either:
  → A belongs in B's domain (merge)
  → B's capabilities need to be in A's domain (move capability)
  → A's API to B is insufficient (improve interface)
```

---

## 📅 How to Run a Team Topology Review

A practical process for sensing and evolving your topologies:

```
QUARTERLY TOPOLOGY REVIEW PROCESS:

  Step 1: MEASURE (weeks 1-2)
  → Collect delivery metrics (deployment frequency, lead time)
  → Run team health surveys
  → Map actual communication patterns (who talks to whom)
  → Compare actual comms to expected comms (Conway's Law check)
  
  Step 2: ANALYZE (week 3)
  → Identify signals (delivery slowdowns, team stress, comms surprises)
  → Root-cause each signal to a topology issue
  → Propose topology changes (split, merge, new team type, mode change)
  
  Step 3: DECIDE (week 4)
  → Leadership + tech leads review proposals
  → Prioritize by impact vs. disruption
  → Approve changes for next quarter
  
  Step 4: EXECUTE (next quarter)
  → Implement topology changes iteratively
  → Communicate clearly to all affected teams
  → Set success criteria and timelines
```

---

## ✅ Key Takeaways

| # | Takeaway |
|---|---|
| 1 | **Team topologies are dynamic** — there is no final state; evolve continuously |
| 2 | **Collaboration level must match the discovery phase** — high during discovery, low during execution |
| 3 | **New capability adoption follows a pattern** — collaborate → facilitate → X-as-a-service |
| 4 | **Teams evolve by merging, splitting, and changing type** — all are normal and healthy |
| 5 | **Know your signals** — slow delivery, team stress, and architecture drift all signal topology problems |
| 6 | **Build organizational sensing** — detect when topology needs to change before it becomes a crisis |
| 7 | **Use unexpected communication patterns as diagnostic signals** — they reveal hidden architectural coupling |
| 8 | **Self-steering organizations** surface topology problems bottom-up, not just top-down |

---

*← [Chapter 7 - Team Interaction Modes](07-team-interaction-modes.md) | [Back to Index](../README.md) | Next: [Conclusion](09-conclusion.md) →*
