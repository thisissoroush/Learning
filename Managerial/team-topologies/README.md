# 📚 Team Topologies
### *Organizing Business and Technology Teams for Fast Flow*
**By Matthew Skelton & Manuel Pais**

---

## 🎯 What This Book Is About

Modern software delivery is broken — not because of bad engineers, but because of how teams are **structured and forced to interact**. This book gives you a practical, adaptive model for organizing technology teams so that software can flow to customers **fast and safely**.

The central insight: **your team structure IS your architecture.** You cannot design software in isolation from the humans who build it.

---

## 🗺️ The Big Map: Core Ideas at a Glance

```
┌─────────────────────────────────────────────────────────────────────┐
│                     TEAM TOPOLOGIES FRAMEWORK                        │
│                                                                      │
│   CONWAY'S LAW          TEAM-FIRST           COGNITIVE LOAD         │
│   ─────────────         ──────────           ──────────────         │
│   Software mirrors  →   Teams are the    →   Protect the team's    │
│   team structure        unit of delivery      mental capacity       │
│                                                                      │
│        ↓                    ↓                      ↓                │
│                                                                      │
│          4 TEAM TYPES  +  3 INTERACTION MODES                       │
│                                                                      │
│   Stream-Aligned  │  Enabling  │  Complicated-  │  Platform         │
│   Team            │  Team      │  Subsystem     │  Team             │
│                   │            │  Team          │                   │
│   ────────────────────────────────────────────────────────          │
│   Collaboration   │   X-as-a-Service   │   Facilitating            │
│                                                                      │
│        ↓                                                            │
│   EVOLVE the structure over time as context changes                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📖 Book Structure

The book is split into **3 parts** + a conclusion:

### Part I — Teams As the Means of Delivery
> Establishes *why* current org structures fail and the foundational principles

| Chapter | Title | Key Question |
|---|---|---|
| [Chapter 1](chapters/01-the-problem-with-org-charts.md) | The Problem with Org Charts | Why do org charts lie, and what should we use instead? |
| [Chapter 2](chapters/02-conways-law-and-why-it-matters.md) | Conway's Law and Why It Matters | How does team structure shape software architecture? |
| [Chapter 3](chapters/03-team-first-thinking.md) | Team-First Thinking | How do we build and protect effective teams? |

### Part II — Team Topologies That Work for Flow
> Defines the *patterns* — the four team types and how to apply them

| Chapter | Title | Key Question |
|---|---|---|
| [Chapter 4](chapters/04-static-team-topologies.md) | Static Team Topologies | What are the common patterns and anti-patterns? |
| [Chapter 5](chapters/05-the-four-fundamental-team-topologies.md) | The Four Fundamental Team Topologies | What are the only 4 team types you need? |
| [Chapter 6](chapters/06-choose-team-first-boundaries.md) | Choose Team-First Boundaries | How do you split software to match team capacity? |

### Part III — Evolving Team Interactions for Innovation
> Explains *how teams interact* and how to evolve the structure over time

| Chapter | Title | Key Question |
|---|---|---|
| [Chapter 7](chapters/07-team-interaction-modes.md) | Team Interaction Modes | How should teams talk to each other? |
| [Chapter 8](chapters/08-evolve-team-structures.md) | Evolve Team Structures with Organizational Sensing | How does the structure change as the org grows? |
| [Conclusion](chapters/09-conclusion.md) | The Next-Generation Digital Operating Model | How does it all fit together? |

---

## 🧠 The 5 Core Mental Models

### 1. Conway's Law
> *"Organizations which design systems are constrained to produce designs which are copies of the communication structures of those organizations."*
> — Mel Conway, 1968

Your team org chart **becomes** your software architecture. Fight it and you'll lose.

### 2. The Reverse Conway Maneuver
Design the **team structure first** to match the software architecture you *want*, rather than letting the software architecture emerge from whatever teams happen to exist.

### 3. Cognitive Load Limit
Every team has a **maximum cognitive capacity**. Exceeding it causes slow delivery, bugs, burnout, and disengagement. Software system sizes must be matched to team cognitive load — not the other way around.

### 4. Team-First Software Boundaries
Slice software not by technical layers (UI/backend/DB) but by **what a single team can comfortably own and evolve**.

### 5. Dynamic Topologies
Team structures must **evolve** over time. A topology that works during discovery (high collaboration) is wrong for execution (low bandwidth, X-as-a-service). Sense the context and adapt.

---

## 🏢 Real Companies Featured

| Company | Lesson |
|---|---|
| **Adidas** | Shifted from vendor-dependent to in-house cross-functional teams → 60x faster releases |
| **Amazon** | "Two-pizza teams" + each service owned by exactly one team |
| **Spotify** | Squads, tribes, chapters, guilds — physically co-located to match interaction needs |
| **IKEA** | Split one large team into two when cognitive load from two products caused bottlenecks |
| **Netflix** | SRE teams that temporarily embed with app teams, then step back |
| **TransUnion** | Evolved team topologies iteratively as platform maturity grew |
| **uSwitch** | Used Kubernetes adoption to reorganize entire team topology |
| **OutSystems** | Split one overloaded 8-person team into microteams per domain → motivation soared |

---

## 🔑 Key Terms Glossary

| Term | Definition |
|---|---|
| **Stream-Aligned Team** | End-to-end team aligned to a flow of business value (the primary team type) |
| **Enabling Team** | Helps other teams learn new practices without long-term dependency |
| **Complicated-Subsystem Team** | Owns a highly complex technical area requiring specialist knowledge |
| **Platform Team** | Provides self-service internal platform to reduce cognitive load on stream teams |
| **Collaboration Mode** | Two teams work closely together temporarily to discover something new |
| **X-as-a-Service Mode** | One team consumes another's output with minimal interaction |
| **Facilitating Mode** | One team coaches/unblocks another team |
| **Cognitive Load** | The total mental effort required to understand and work with a system |
| **Conway's Law** | Org communication structure shapes software architecture |
| **Reverse Conway Maneuver** | Design teams to match desired software architecture |
| **Fracture Plane** | Natural seam in a software system where it can be cleanly split |
| **Team API** | Everything other teams need to interact with your team (code, docs, practices, comms) |
| **Dunbar's Number** | Cognitive limits on group size: ~5 close, ~15 trust, ~50 mutual, ~150 remember |

---

*← [Back to Managerial Index](../README.md)*
