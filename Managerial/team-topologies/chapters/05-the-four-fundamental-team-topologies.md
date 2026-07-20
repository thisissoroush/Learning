# Chapter 5: The Four Fundamental Team Topologies
## *The only four team types you need — and exactly what each one does*

---

## 🎯 Core Concept

After surveying all the different team patterns in industry, the authors identify that **every effective software team can be mapped to one of four fundamental types**. There are no others needed. These four types, used together, cover all the responsibilities needed to build, run, and evolve complex software systems — while keeping cognitive load manageable and flow fast.

```
THE FOUR FUNDAMENTAL TEAM TOPOLOGIES

  ┌─────────────────────────────────────────────────────────┐
  │                                                         │
  │  1. STREAM-ALIGNED TEAM    ████████████████████████     │
  │     Primary delivery team.                              │
  │     Aligned to a flow of business or user value.        │
  │                                                         │
  │  2. ENABLING TEAM          ░░░░░░░░░░░░░                │
  │     Helps other teams grow new capabilities.            │
  │     Temporary, coaching-focused.                        │
  │                                                         │
  │  3. COMPLICATED-SUBSYSTEM  ▓▓▓▓▓▓▓▓▓                   │
  │     TEAM                                                │
  │     Owns a specialized, complex technical area.         │
  │     Rare — only when specialist knowledge is essential. │
  │                                                         │
  │  4. PLATFORM TEAM          ▒▒▒▒▒▒▒▒▒▒▒▒▒               │
  │     Provides self-service internal platform.            │
  │     Reduces cognitive load for stream-aligned teams.    │
  │                                                         │
  └─────────────────────────────────────────────────────────┘
  
  KEY RATIO:
  Stream-aligned teams should be the MAJORITY (typically 6:1 or higher)
  All other types exist to SUPPORT stream-aligned teams
```

---

## 1️⃣ Stream-Aligned Teams

### What Is a Stream?

A "stream" is a continuous flow of work aligned to a **business domain, product feature, user journey, or specific outcome**.

Examples of streams:
- Customer checkout experience
- Mobile app (iOS)
- Fraud detection pipeline
- Order management
- Internal developer experience

### What Stream-Aligned Teams Do

```
STREAM-ALIGNED TEAM — FULL OWNERSHIP MODEL:

  User Need / Business Goal
         │
         ▼
  ┌─────────────────────────────────────────────────────┐
  │              STREAM-ALIGNED TEAM                    │
  │                                                     │
  │  Design → Build → Test → Deploy → Operate → Learn  │
  │                                                     │
  │  Owns the ENTIRE lifecycle of their software area   │
  └─────────────────────────────────────────────────────┘
         │
         ▼
  Running software delivering business value
```

### Capabilities a Stream-Aligned Team Should Have

| Capability | Description |
|---|---|
| Application security | Security practices baked in |
| Commercial/business analysis | Understanding of the domain |
| Design (UX, product) | User experience ownership |
| Development | Writing and maintaining code |
| Infrastructure/operations | Deployment and reliability |
| Metrics & monitoring | Observability and alerting |
| Product management | Prioritization and roadmap |
| Testing/QA | Quality built in, not bolted on |

> ⚠️ **Not every team needs all of these full-time.** Some capabilities can be shared via platform services or enabling teams. The goal is **the team doesn't need to wait for other teams** to do the work.

### Key Behaviors of Stream-Aligned Teams

- Aims to produce a **steady flow of feature delivery**
- Corrects course based on **fast feedback** from production
- **Experiments** to find solutions, using feature flags, A/B tests
- Minimal hand-offs — "you build it, you run it"
- Continuously learns from system behavior and user feedback

### Real Example: Amazon

Amazon uses **strictly independent service teams**:
- Each team owns its service end-to-end (design → deployment → operations)
- Teams do NOT share services with other teams
- If Team B needs something from Team A's service, they talk to Team A — not to the service's database
- Jeff Bezos's "API Mandate" (2002): all teams must communicate only via service interfaces, no direct database access, no backdoors

```
AMAZON'S OWNERSHIP MODEL:

  Team A              Team B              Team C
  ┌──────────┐        ┌──────────┐        ┌──────────┐
  │          │ ←API→  │          │ ←API→  │          │
  │ Service  │        │ Service  │        │ Service  │
  │ A        │        │ B        │        │ C        │
  └──────────┘        └──────────┘        └──────────┘
  
  No direct DB access. No shared libraries that couple teams.
  Every interaction is an explicit API contract.
```

---

## 2️⃣ Enabling Teams

### The Problem They Solve

Stream-aligned teams need to focus on delivering value. They can't stop to research new technologies, investigate new practices, or deeply learn new tools — that would destroy their flow.

> **Enabling teams exist to help stream-aligned teams build new capabilities without becoming dependent on the enabling team forever.**

### What Enabling Teams Do

```
ENABLING TEAM — TEMPORARY CAPABILITY UPLIFT:

  Stream-Aligned     Enabling        Result
  Team               Team
  
  "We don't know  → Embeds with  →  Stream team has
  how to do this"    stream team     the new capability
                     for 2-4 weeks   and owns it
  
  ⚠️ The enabling team then STEPS BACK.
     If the stream team keeps depending on them,
     the enabling team has failed.
```

### What Enabling Teams Are NOT

```
❌ NOT a shared services team (they don't do work FOR you)
❌ NOT a permanent support function (they don't get embedded forever)
❌ NOT a gatekeeper or approval body
❌ NOT the "experts who do the hard parts for you"

✅ They are: coaches, consultants, and educators who transfer capability
```

### Enabling Team Examples

| Domain | What They Enable |
|---|---|
| Security | Help teams build security practices into CI/CD pipelines |
| Observability | Help teams instrument their services with monitoring |
| DevOps/CI-CD | Help teams build their own deployment pipelines |
| Architecture | Help teams understand domain-driven design, bounded contexts |
| Testing | Help teams build automated testing cultures |

### Real Example: BCG Digital Ventures — Engineering Enablement Team

Within a large legal organization, BCG Digital Ventures set up an Engineering Enablement team:
- Embedded with product teams for short periods
- Focused on raising the standard of software engineering practices
- Helped teams adopt CI/CD, test-first development, and microservices
- Did NOT take over the work — coached teams to own it themselves

> **Lesson:** An enabling team's success is measured by whether the teams they help no longer need them.

---

## 3️⃣ Complicated-Subsystem Teams

### When They Are Needed (Rarely!)

Some parts of a system require **deep specialist knowledge** that would be too expensive to embed in every stream-aligned team. Examples:
- Video codec / streaming algorithms
- Mathematical modeling / actuarial calculations
- Real-time signal processing
- Complex physics engines
- ML/AI model training infrastructure

### What Makes This Type Different

```
COMPLICATED-SUBSYSTEM TEAM vs. STREAM-ALIGNED:

  Stream-Aligned Team:       Complicated-Subsystem Team:
  ─────────────────────      ──────────────────────────
  Owns a business feature    Owns a specialist component
  Cross-functional           Deep specialists
  Frequent releases          Releases based on subsystem needs
  Close to customer          Often abstracted from customer
  High feature flow          High complexity, lower feature frequency
```

### How They Interact with Stream-Aligned Teams

```
INTERACTION MODEL:

  Stream-Aligned     uses API from     Complicated-
  Team A             ──────────────→   Subsystem Team
  
  Stream-Aligned     uses API from     
  Team B             ──────────────→   (X-as-a-Service)
  
  The subsystem team provides a clean interface.
  Stream teams don't need to understand the internals.
  
  ⚠️ If stream teams constantly need to talk to the subsystem team,
     the API is probably not good enough.
```

> ⚠️ **Use sparingly.** Only create a complicated-subsystem team when the specialist knowledge required is genuinely too complex to spread across stream teams AND the subsystem is used by multiple teams. If only one team uses it, it should probably be part of that team.

---

## 4️⃣ Platform Teams

### The Platform Team's Mission

> **"The platform team's goal is to make the stream-aligned teams as autonomous as possible."**

A platform is an **internal product** — a curated set of tools, services, and practices that reduce the cognitive load on stream-aligned teams. The platform team treats stream-aligned teams as its customers.

```
PLATFORM TEAM MODEL:

  ┌──────────────────────────────────────────────────────────┐
  │                    PLATFORM TEAM                         │
  │                                                          │
  │  Provides self-service capabilities:                     │
  │                                                          │
  │  • Deployment pipelines (CI/CD)                         │
  │  • Compute infrastructure (cloud provisioning)          │
  │  • Logging & monitoring tools                           │
  │  • Security scanning                                    │
  │  • Service mesh / networking                            │
  │  • Secrets management                                   │
  │  • Internal developer portal                            │
  └──────────────────────────────────────────────────────────┘
                          │
           ┌──────────────┼──────────────┐
           ▼              ▼              ▼
    Stream Team A   Stream Team B   Stream Team C
    (consumes the platform as a self-service)
```

### What Makes a Good Platform

**The "just big enough" principle:**

A good platform is the **thinnest viable platform** — no more, no less. It provides what teams need to be autonomous without becoming so large and complex that it imposes its own cognitive load.

```
PLATFORM SIZE SPECTRUM:

  Too small:         Just right:        Too large:
  ─────────          ──────────         ─────────
  Teams reinvent     Teams self-        Platform becomes
  everything         serve easily       a monolith, hard
  → wasted effort    → low cognitive    to use, teams
                     load               route around it
```

### The Platform as a Product

The platform team should treat their platform as a **product with customers** (the stream-aligned teams). This means:

| Product Thinking | Technical Thinking (avoid) |
|---|---|
| User research — talk to stream teams | Build what seems technically interesting |
| Roadmap aligned to stream team needs | Roadmap driven by technology trends |
| Easy onboarding and documentation | Assume teams will figure it out |
| Feedback loops and iteration | Release and move on |
| Support SLAs | "It's open source, read the docs" |

### Real Example: Sky Betting & Gaming — Platform Feature Teams

Michael Maibaum (Chief Architect) described their platform evolution:
- Started with a central ops team managing everything
- Evolved to "Platform Feature Teams" — small teams within the platform org, each responsible for a specific capability (deployments, monitoring, networking, etc.)
- Stream-aligned teams could self-serve 90%+ of their needs
- Platform feature teams had their own backlogs, OKRs, and roadmaps

```
SKY BET PLATFORM STRUCTURE:

  Platform Organization
  ┌────────────────────────────────────────────────────┐
  │                                                    │
  │  ┌──────────────┐  ┌──────────────┐               │
  │  │ Deployment   │  │ Monitoring   │               │
  │  │ Feature Team │  │ Feature Team │               │
  │  └──────────────┘  └──────────────┘               │
  │  ┌──────────────┐  ┌──────────────┐               │
  │  │ Networking   │  │ Security     │               │
  │  │ Feature Team │  │ Feature Team │               │
  │  └──────────────┘  └──────────────┘               │
  │                                                    │
  └────────────────────────────────────────────────────┘
  
  Each platform feature team = itself a stream-aligned team
  (aligned to the stream of platform capability improvements)
```

### Real Example: Auto Trader — Evolving IT Operations

Auto Trader evolved their operations function:
- Started: traditional ops team managing all infrastructure manually
- Evolved: ops team became a platform team providing self-service tooling
- Stream-aligned teams gained autonomy to deploy and manage their own services
- Ops team focused on the platform's reliability and usability

---

## 🔗 How the Four Types Work Together

```
TEAM TOPOLOGIES IN A TYPICAL ORG:

                    ┌──────────────┐
                    │  ENABLING    │ (coaches stream teams)
                    │  TEAM        │
                    └──────┬───────┘
                           │ facilitates
                           ▼
  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
  │  Stream-     │    │  Stream-     │    │  Stream-     │
  │  Aligned     │    │  Aligned     │    │  Aligned     │
  │  Team A      │    │  Team B      │    │  Team C      │
  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
         │                  │                   │
         └──────────────────┼───────────────────┘
                            │ consumes
                            ▼
                    ┌──────────────┐
                    │  PLATFORM    │ (provides self-service)
                    │  TEAM        │
                    └──────────────┘
                    
                    ┌──────────────┐
                    │ COMPLICATED  │ (provides specialist API)
                    │ SUBSYSTEM    │ ← used by some stream teams
                    │ TEAM         │
                    └──────────────┘
```

---

## 🔄 Converting Common Team Types

Many organizations have legacy team types that don't map cleanly to the four topologies. Here's how to convert them:

### Traditional Infrastructure Team → Platform Team

```
BEFORE:                              AFTER:
  
  Infrastructure Team               Platform Team
  ┌────────────────────┐            ┌────────────────────┐
  │ Manages ALL infra  │            │ Self-service tools  │
  │ for ALL teams      │  →         │ for stream teams    │
  │ (ticketing system, │            │ (developer portal,  │
  │  wait queue)       │            │  Terraform modules, │
  └────────────────────┘            │  CI/CD templates)   │
                                    └────────────────────┘
  Bottleneck                        Enabler
```

### Traditional QA/Testing Team → Embedded in Stream Teams

```
BEFORE:                              AFTER:
  
  QA Team                           QA capability embedded
  ┌────────────────────┐            in each stream team
  │ Tests features     │  →         ┌────────────────────┐
  │ at end of sprint   │            │ Dev + QA work       │
  │ for ALL dev teams  │            │ together, test-     │
  └────────────────────┘            │ first, automated    │
  Bottleneck                        └────────────────────┘
                                    Built-in quality
```

### Traditional Support Team → Aligned to Streams

```
BEFORE:                              AFTER:
  
  Central Support Team              Support embedded per stream
  ┌────────────────────┐            ┌────────────────────┐
  │ Handles ALL support │  →        │ Support engineers   │
  │ tickets from ALL   │            │ know THEIR system   │
  │ systems            │            │ deeply, resolve     │
  └────────────────────┘            │ faster             │
  Slow (no context)                 └────────────────────┘
                                    Fast (domain experts)
```

---

## ⚠️ Avoid Team Silos in the Flow of Change

The biggest mistake with team topology design is creating **silos within the flow of change**:

```
SILO ANTI-PATTERN:

  Feature Request
       │
       ▼
  Design Team → (ticket, wait) → Dev Team → (ticket, wait)
  → QA Team → (ticket, wait) → Security Team → (ticket, wait)
  → Ops Team → (ticket, wait) → Customer
  
  Each team is a silo. Every hand-off is a delay and a quality risk.
  
  CORRECT:
  Feature Request → Stream-Aligned Team (all capabilities inside) → Customer
```

---

## ✅ Key Takeaways

| # | Takeaway |
|---|---|
| 1 | **Four team types cover all needs** — stream-aligned, enabling, complicated-subsystem, platform |
| 2 | **Stream-aligned teams are primary** — all others exist to support them |
| 3 | **Enabling teams transfer capability** — they coach, then step back; dependency = failure |
| 4 | **Complicated-subsystem teams are rare** — only for genuinely specialist areas used by multiple teams |
| 5 | **Platform teams build internal products** — treat stream teams as customers, optimize for self-service |
| 6 | **Platforms should be "just big enough"** — thin, usable, low cognitive load |
| 7 | **Convert legacy team types** to the four fundamental types to remove gray areas |
| 8 | **Most teams should be stream-aligned** — a good ratio is ~6:1 stream-aligned to others |

---

*← [Chapter 4 - Static Team Topologies](04-static-team-topologies.md) | [Back to Index](../README.md) | Next: [Chapter 6 - Choose Team-First Boundaries](06-choose-team-first-boundaries.md) →*
