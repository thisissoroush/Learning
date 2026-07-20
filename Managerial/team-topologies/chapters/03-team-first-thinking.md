# Chapter 3: Team-First Thinking
## *The team — not the individual — is the fundamental unit of software delivery*

---

## 🎯 Core Concept

We've been thinking about software delivery wrong. We optimize for individual productivity (better tools, better developers, bigger salaries) while neglecting the unit that actually delivers: **the team**. Research, military experience, and decades of software practice all confirm the same thing — **well-functioning teams outperform collections of brilliant individuals** for complex knowledge work.

The shift: **stop assigning work to individuals. Assign it to teams.** And then protect those teams.

> *"The best-performing teams accomplish remarkable feats not simply because of the individual qualifications of their members, but because those members coalesce into a single organism."*
> — General Stanley McChrystal, *Team of Teams*

---

## 👥 Use Small, Long-Lived Teams as the Standard

### Team Size: The 5-9 Rule

Research and practice converge on a maximum effective team size:

```
TEAM SIZE SWEET SPOT:

  Too small           Optimal             Too large
  (< 4 people)       (5 - 9 people)      (> 9 people)
      │                    │                   │
      ▼                    ▼                   ▼
   Limited            High trust           Trust breaks
  capacity         + fast decisions      down, politics
  & coverage         + full ownership      emerges, slow
```

**Why 5-9?** Robin Dunbar's anthropological research shows humans have hard limits on the number of trusted relationships they can maintain. These are called **Dunbar's numbers**.

---

## 🔵 Dunbar's Number: The Science of Group Size

```
         DUNBAR'S NUMBER — CONCENTRIC CIRCLES OF TRUST
         
                        ┌─────────────────────────────┐
                        │            ~150              │
                        │    (remember capabilities)  │
                        │    ┌─────────────────────┐  │
                        │    │        ~50           │  │
                        │    │  (mutual trust)      │  │
                        │    │  ┌───────────────┐   │  │
                        │    │  │     ~15        │   │  │
                        │    │  │ (deep trust)   │   │  │
                        │    │  │  ┌─────────┐  │   │  │
                        │    │  │  │   ~5    │  │   │  │
                        │    │  │  │(close   │  │   │  │
                        │    │  │  │ personal│  │   │  │
                        │    │  │  │ bonds)  │  │   │  │
                        │    │  │  └─────────┘  │   │  │
                        │    │  └───────────────┘   │  │
                        │    └─────────────────────┘  │
                        └─────────────────────────────┘
                        
                                    ~500
                        (acquaintances / weak ties)
                        
                                   ~1500
                              (faces we recognize)
```

### Applying Dunbar's Numbers to Org Design

| Group Size | Trust Level | Org Equivalent |
|---|---|---|
| ~5 people | Close personal bonds, working memory | Core inner-circle squad |
| ~15 people | Deep trust | Single software team (high-trust org) |
| ~50 people | Mutual trust | Family/"tribe" grouping |
| ~150 people | Remember capabilities | Division / Stream / P&L line |
| ~500 people | Acquaintances | Larger business unit |

> 🔑 **Key rule:** When a group exceeds one of these thresholds, the dynamics change. Plan your software architecture to match — otherwise the misalignment creates friction.

### Practical Team Groupings

```
Recommended groupings:

  Single team:           5–8 people (up to 15 in high-trust orgs)
  Tribe / families:      up to 50 people
  Divisions / streams:   up to 150 or 500 people
  
  When you exceed a limit → split off a semi-independent grouping
  AND realign the software architecture with the new groupings
```

---

## ⏳ Long-Lived Teams: Flow Work to the Team

### Why Team Stability Matters

Teams take **2 weeks to 3 months** to form into a cohesive unit. Once they reach high performance, they can be many times more effective than individuals alone.

```
TEAM FORMATION JOURNEY (Tuckman Model + Reality):

  Month 0    Month 1    Month 2    Month 3    Month 4+
     │          │          │          │          │
     ▼          ▼          ▼          ▼          ▼
  Forming    Storming   Norming   Performing  Sustaining
  (meeting   (friction  (finding  (high      (maintain +
   for the   & debate)  rhythms)  output)     evolve)
   first
   time)
   
  ⚠️ NOTE: Research shows "storming" never fully stops.
           It recurs throughout the team's lifetime.
           Continual nurturing is required.
```

### Brooks's Law: Why Adding People Hurts (Short Term)

> **"Adding manpower to a late software project makes it later."** — Fred Brooks, *The Mythical Man-Month*

```
ADDING MEMBER TO A TEAM:

  Before new member:   A ←→ B ←→ C  (3 communication lines)
  After new member:    A ←→ B ←→ C ←→ D  (6 communication lines)
                       A ←→ C ←→ D
                       A ←→ D
  
  Communication overhead grows faster than capacity added.
  Plus: ramp-up time, emotional adjustment, re-norming.
```

**The right approach:** Keep the team stable. **Flow work to the team.** Don't flow people to the work.

### How Often Should Teams Change?
- **Typical orgs:** People should stay 18 months to 2 years
- **High-trust orgs:** People may switch teams ~every 9–12 months (e.g., Pivotal)

---

## 🏠 The Team Owns the Software

**Every piece of software must be owned by exactly one team.** No shared ownership, no co-ownership, no "shared components with no owner."

```
OWNERSHIP MODEL:

  ✅ CORRECT:
  ┌──────────┐         ┌──────────┐
  │  Team A  │ owns →  │Service A │
  └──────────┘         └──────────┘
  ┌──────────┐         ┌──────────┐
  │  Team B  │ owns →  │Service B │
  └──────────┘         └──────────┘

  ❌ WRONG:
  ┌──────────┐
  │  Team A  │ ─┐
  └──────────┘  ├→ "Shared Component" ← no real owner
  ┌──────────┐  │     (breaks silently,
  │  Team B  │ ─┘      nobody cares)
  └──────────┘
```

**What ownership means:**
- Team cares for the code like a **steward or gardener** — not a private owner
- Other teams may submit pull requests or suggestions
- But only the owning team makes changes (or temporarily grants access)
- Team plans across time horizons: immediate fixes, near-term improvements, long-term evolution

---

## 🧠 Good Boundaries Minimize Cognitive Load

### The Three Types of Cognitive Load

Psychologist John Sweller (1988) defined three types:

```
┌──────────────────────────────────────────────────────────────────┐
│                    THREE TYPES OF COGNITIVE LOAD                  │
│                                                                   │
│  INTRINSIC      ← Fundamental to the problem domain              │
│  (necessary)       e.g., "What is a Java class?"                 │
│                    e.g., "How does this business domain work?"    │
│                                                                   │
│  EXTRANEOUS     ← The environment / tooling overhead             │
│  (eliminate!)      e.g., "How do I deploy this again?"           │
│                    e.g., "Which config flag was that?"            │
│                                                                   │
│  GERMANE        ← The "value-add" thinking — learning &          │
│  (maximize!)       optimization                                   │
│                    e.g., "How should this service interact        │
│                    with the payments service?"                    │
└──────────────────────────────────────────────────────────────────┘

STRATEGY:
  Minimize intrinsic  →  training, good tech choices, pair programming
  Eliminate extraneous → automation, good platforms, good docs
  Maximize germane    →  this is where competitive advantage lives
```

### How to Detect Cognitive Overload

A simple, non-judgmental check:

> *"Do you feel like you're effective and able to respond in a timely fashion to the work you are asked to do?"*

If the answer is clearly **no**, the team is likely overloaded. Look for these signals:

| Signal | What It Means |
|---|---|
| Constant context switching between unrelated work | Too many domains |
| Team members feel they lack domain knowledge | Load exceeded |
| Low morale, missed deadlines, quality issues | Overload in progress |
| "We're always firefighting" | Extraneous cognitive load dominating |
| Sprint planning feels chaotic | Too many competing priorities |

---

## 📏 Limit Domains Per Team

**Heuristics for domain assignment:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOMAIN ASSIGNMENT RULES                       │
│                                                                  │
│  Simple domain      → Team can handle 2–3 of these              │
│  (routine, clear)     (older system with minor changes, etc.)   │
│                                                                  │
│  Complicated domain → Team should handle 1 (maybe 2)            │
│  (needs analysis)     More than this → split the team           │
│                                                                  │
│  Complex domain     → Team should handle ONLY this one           │
│  (experimentation)    Don't add anything else — focus needed    │
└─────────────────────────────────────────────────────────────────┘
```

**Visual — Before and After Domain Assignment:**

```
BEFORE (overloaded):               AFTER (right-sized):

  Team A (8 people)                  Team 1 (5 people)
  ┌────────────────────┐             ┌───────────────┐
  │ Domain 1 (complex) │             │Domain 1       │
  │ Domain 2 (complex) │             │(complex)      │
  │ Domain 3 (compl.)  │             └───────────────┘
  │ Domain 4 (compl.)  │             
  └────────────────────┘             Team 2 (5 people)
                                     ┌───────────────┐
  Result: constant context           │Domain 2       │
  switching, disengagement,          │(complex)      │
  poor quality                       └───────────────┘
                                     
                                     Team 3 (5 people)
                                     ┌───────────────┐
                                     │Domain 3 + 4   │
                                     │(complicated)  │
                                     └───────────────┘
```

---

## 🏢 Real Examples

### OutSystems — Microteam Split (Part 2)

The Engineering Productivity team (8 people, 4 domains) split into 3 microteams:
- **IDE Productivity** (co-located with IDE product team)
- **Platform-Server Productivity** (co-located with platform team)
- **Infrastructure Automation**

Results after a few months:
- Motivation sharply increased ✅
- Clear mission per team ✅
- Less context switching ✅
- Flow and solution quality significantly improved ✅

### IKEA — Mobile Team Split

A high-performing mobile team kept adding projects. Eventually:
- Two products living in one codebase
- Work streams blocking each other's releases

Despite the team's high performance, **cognitive overload was slowing them down**. The solution: split into two teams following Conway's Law — one per product.

> **Lesson:** Even a great team has a cognitive load ceiling. It's not a weakness — it's physics.

---

## 📡 Design "Team APIs"

With stable teams owning defined areas, you can build a **Team API** — a consistent interface for how other teams interact with you.

```
TEAM API COMPONENTS:

  ┌─────────────────────────────────────────────────────────┐
  │                       TEAM API                          │
  │                                                         │
  │  📦 Code         Runtime endpoints, libraries, clients  │
  │                  UI components, SDKs                    │
  │                                                         │
  │  🔢 Versioning   SemVer promises ("we won't break you") │
  │                                                         │
  │  📖 Docs         How-to guides, runbooks, architecture  │
  │                  decision records (ADRs)                │
  │                                                         │
  │  ⚙️ Practices    Preferred ways of working              │
  │                  (review process, PR standards, etc.)   │
  │                                                         │
  │  💬 Comms        Chat channels, response SLAs,          │
  │                  video conferencing norms               │
  │                                                         │
  │  📋 Work info    Current priorities, roadmap,           │
  │                  what's next (visible externally)       │
  └─────────────────────────────────────────────────────────┘
```

**Key questions for your Team API:**
- Will other teams find it easy to interact with us?
- How easy is it for a new team to get on board?
- Is our backlog visible and understandable to other teams?
- How do we respond to pull requests from other teams?

**Extreme example — AWS:** Jeff Bezos required that every team treat every other team as a **potential denial-of-service attacker**, requiring service levels, quotas, and throttling. This forced crystal-clear API design at scale.

---

## 🏗️ Design the Physical and Virtual Environment

### Office Design for Teams

Teams need **three modes of work** supported by their environment:

```
THREE MODES → THREE SPACE TYPES:

  Focused individual work    →  Quiet zones, noise-cancelling options
  Collaborative intra-team   →  Team bay / open bench with whiteboards
  Collaborative inter-team   →  Shared commons, event spaces, lounges
```

**CDL Case Study — "Benched Bay" Design:**
- Long bench per team, flanked by whiteboard partitions
- Asymmetric arrangement (bench close to one partition) → more standing room on one side for standups
- Smart-surface walls for drawing
- Flexible: small teams spread out, growing teams squeeze up
- Split teams take culture with them → skip "storming" phase

**Auto Trader Case Study:**
- Reorganized from 15 offices to 3
- All senior managers sit with their teams (no private offices)
- Single monitors per desk → reduces hiding behind screens, promotes pairing
- Clear-desk policy → people move to wherever they need to be
- Floor/building per business stream → full tribe co-location

**Spotify Model:**
- Squads physically in the same office
- Lounge areas between squads promote inter-squad collaboration
- Office layout maps exactly to the squad/tribe structure

### Virtual Environment

For remote teams, naming conventions matter enormously:

```
CHAT CHANNEL NAMING (example):

  #deploy-pre-production        ← by function
  #practices-engineering        ← by practice type  
  #practices-testing
  #support-environments         ← by support category
  #support-logging
  #team-vesuvius                ← by team name
  #team-kilimanjaro

Username conventions:
  Instead of "Jai Kale"
  Use "[Platform] Jai Kale" → instantly visible which team they're on
```

---

## 🎯 Team-First Mindset

For teams to work, individual team members need to **put team needs above their own**:

| Team-First Behaviors | Anti-Patterns |
|---|---|
| Arrive to standups on time | Frequently missing or late |
| Help unblock others before starting new work | Always grabbing the "fun" tickets |
| Encourage focus on team goals | Pursuing personal side projects on team time |
| Mentor less experienced members | Hoarding knowledge for status |
| Agree to explore options rather than "win" arguments | "My way or the highway" |

> ⚠️ **"Team-toxic" individuals** — those unable or unwilling to put team needs above their own — can destroy a team's performance. This needs to be addressed proactively.

### Reward the Whole Team, Not Individuals

W. Edwards Deming identified individual performance bonuses as **actively harmful** to team performance. Nokia's approach during its most successful decade:
- Pay differences across the org were muted
- Bonuses were small and team-based, not individual
- Training budgets: allocated to the **whole team**, who decides how to use it

---

## ✅ Key Takeaways

| # | Takeaway |
|---|---|
| 1 | **The team is the unit of delivery** — stop assigning work to individuals |
| 2 | **5–9 people is the optimal team size** — based on Dunbar's trust limits |
| 3 | **Limit team size groupings** at ~50, ~150, ~500 as you scale |
| 4 | **Keep teams stable** — flow work to the team, not people to work |
| 5 | **Every piece of software has exactly one owner team** — no shared ownership |
| 6 | **Cognitive load has a hard limit** — match software scope to team capacity |
| 7 | **Eliminate extraneous cognitive load** via good platforms, automation, documentation |
| 8 | **Team APIs** create clean interfaces for inter-team interaction |
| 9 | **Design the physical/virtual environment** to support intra-team and inter-team work |
| 10 | **Reward the team** — individual performance optimization damages collective performance |

---

*← [Chapter 2 - Conway's Law](02-conways-law-and-why-it-matters.md) | [Back to Index](../README.md) | Next: [Chapter 4 - Static Team Topologies](04-static-team-topologies.md) →*
