# 🔑 Key Takeaways — Team Topologies
### Matthew Skelton & Manuel Pais

> The single most important idea in this book: **Your team structure IS your software architecture.** You cannot design one without designing the other.

---

## 🧠 The Foundational Mental Models

| # | Takeaway |
|---|----------|
| 1 | **Org charts lie** — they show formal hierarchy, not how work actually gets done. Three structures coexist: formal (the chart), informal (the shadow), and value-creation (the real one) |
| 2 | **Conway's Law is inevitable** — *"Organizations which design systems are constrained to produce designs which are copies of the communication structures of those organizations."* Fight it and you lose |
| 3 | **Use the Reverse Conway Maneuver** — instead of letting software emerge from whatever teams exist, design your team structure first to match the architecture you *want* to produce |
| 4 | **Cognitive load is a hard limit** — every team has a maximum mental capacity. Exceeding it causes slow delivery, bugs, burnout, and disengagement — not more output |
| 5 | **Optimize the whole system, not local parts** — a local improvement (e.g., faster CI) that doesn't remove the system's biggest bottleneck changes nothing for users |

---

## 👥 The Four Team Types

| # | Takeaway |
|---|----------|
| 6 | **Stream-Aligned Teams are the primary delivery unit** — end-to-end ownership of a flow of business value; they should be the most common team type in any organization |
| 7 | **Platform Teams reduce cognitive load** — they provide self-service capabilities so stream teams don't have to manage infrastructure; measure success by how rarely stream teams need to ask for help |
| 8 | **Enabling Teams coach, then step back** — they transfer capability to stream teams and explicitly work toward making themselves unnecessary. If stream teams become dependent, the enabling team has failed |
| 9 | **Complicated-Subsystem Teams own specialist areas** — rare; justified only when a specific technical area (e.g., a complex algorithm, a DSP) requires deep expertise that stream teams can't reasonably acquire |
| 10 | **Every piece of software has exactly one owning team** — unclear ownership is the root cause of most maintenance failures and cognitive overload |

---

## 🔀 The Three Interaction Modes

| # | Takeaway |
|---|----------|
| 11 | **Collaboration mode is for discovery, not execution** — two teams blur boundaries to explore new ground. High bandwidth, time-limited. Convert to X-as-a-service once the solution is known |
| 12 | **X-as-a-Service mode is for execution** — one team consumes another's output with a clear, stable API boundary. Low interaction overhead. The goal of most mature platform relationships |
| 13 | **Facilitating mode transfers capability** — one team coaches another to grow a skill. Ends when the target team can self-serve. Never a permanent arrangement |
| 14 | **Unexpected inter-team communication is a signal** — if teams that shouldn't need to talk are talking constantly, it reveals an architecture or boundary problem, not a communication problem |

---

## 🏗️ Team Design Principles

| # | Takeaway |
|---|----------|
| 15 | **Teams should be 5–9 people** — Dunbar's number sets cognitive limits; beyond ~9, trust and communication degrade. Split before you hit the limit |
| 16 | **Keep teams long-lived and stable** — flow work to teams, don't move people to work. Disbanding high-performing teams destroys trust, context, and morale |
| 17 | **Match software size to team cognitive load** — if a team struggles to understand the system they own, the system is too large, not the team too small |
| 18 | **Team API is real** — every team should explicitly define how others interact with them: code, docs, versioning, communication channels, practices |
| 19 | **Use fracture planes to split large systems** — natural seams (bounded contexts, regulatory boundaries, pace of change, risk) guide where software can be cleanly divided across team boundaries |

---

## 🔄 Evolution & Sensing

| # | Takeaway |
|---|----------|
| 20 | **There is no final topology** — the right structure depends on context, and context changes. Build the organizational muscle to evolve continuously |
| 21 | **Become a sensing organization** — watch for signals: slow delivery, team stress, unexpected communication, architecture drift. These are symptoms of topology problems |
| 22 | **Start with one change** — don't attempt a full reorg. Identify the single biggest topology problem, fix it, measure the impact, then repeat |
| 23 | **A topology that works during discovery is wrong for execution** — collaboration mode (high bandwidth) should transition to X-as-a-service (low bandwidth) as the product matures |

---

## ⚠️ What Team Topologies Doesn't Replace

| # | Takeaway |
|---|----------|
| 24 | **Team Topologies is the skeleton, not the whole body** — you still need technical practices (CI/CD, TDD, observability), culture (psychological safety, blameless post-mortems), and leadership (clear strategy, budget for platforms) |
| 25 | **Good org design creates conditions for success** — it removes structural obstacles but cannot substitute for engineering excellence or a learning culture |

---

## 🏢 Real-World Evidence

| Company | Lesson |
|---------|--------|
| **Adidas** | Shifted from vendor teams to in-house cross-functional teams → 60x faster releases |
| **Amazon** | "Two-pizza teams" + each service owned by exactly one team |
| **OutSystems** | Split one overloaded 8-person team into domain-specific microteams → motivation and quality soared |
| **IKEA** | Split one large team into two when cognitive load from two products became a bottleneck |

---

## 🗺️ The Complete Framework at a Glance

```
Conway's Law → Team-First Thinking → 4 Types + 3 Modes → Evolve Continuously
     ↓                  ↓                    ↓                    ↓
Software =         Team is unit       Stream-Aligned      Sense signals
team comms         of delivery        Platform            Adapt topology
structure          Protect cog        Enabling            Repeat
                   load               Complicated-Sub
```

---

*← [Back to Book Overview](README.md)*
