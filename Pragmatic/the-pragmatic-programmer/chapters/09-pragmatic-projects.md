# Chapter 9: Pragmatic Projects
## *Applying pragmatic principles to the whole team and the whole project*

---

## 🎯 Core Concept

Individual programmers can be pragmatic, but the real payoff comes when the **entire team** adopts pragmatic habits. This final chapter scales everything from previous chapters up to team and project level — how teams behave, what practices they automate, and ultimately what it means to delight users and take pride in your craft.

> *"Pragmatic techniques that work for an individual programmer also work for a team, with some adjustment."*

---

## 📌 Topics in This Chapter

| Topic | Title | Core Idea |
|---|---|---|
| 49 | Pragmatic Teams | Apply pragmatic principles at team scale |
| 50 | Coconuts Don't Cut It | Don't copy practices without understanding them |
| 51 | Pragmatic Starter Kit | Version control, testing, automation — the non-negotiables |
| 52 | Delight Your Users | The goal isn't shipping features — it's solving problems |
| 53 | Pride and Prejudice | Own your work; sign it with pride |

---

## 🔑 Topic 49 — Pragmatic Teams

### 💡 Tip 86: Maintain Small, Stable Teams

A pragmatic team applies all the individual practices — DRY, good design, automation — at the team level.

```
PRAGMATIC TEAM CHARACTERISTICS:

  ✅ No broken windows — the team fixes problems, doesn't accept them
  ✅ No broken windows policy — anyone can and should fix a problem
  ✅ Boiled frog awareness — someone watches the big picture
  ✅ DRY at team level — no two people own the "same knowledge"
  ✅ Orthogonal teams — responsibilities are clear and non-overlapping
  ✅ Automation everywhere — don't do manually what can be automated
```

### Team Size and Structure

Small, stable teams outperform large, chaotic ones. A team that changes composition constantly loses shared context and trust — its most valuable assets.

```
THE COMMUNICATION TAX:
  2 people:   1 communication channel
  4 people:   6 communication channels
  10 people: 45 communication channels
  50 people: 1,225 channels ← impossible to manage

  Keep teams small enough to communicate effectively.
  Amazon's "two-pizza rule": if you need more than two pizzas to feed
  the team, it's too big.
```

### Team Branding

Great teams have an identity. Give the team a name, a shared mission, a way of working that the whole team owns. Pride in the team translates to pride in the work.

---

## 🔑 Topic 50 — Coconuts Don't Cut It

### 💡 Tip 87: Do What Works, Not What's Fashionable

**Cargo cult programming**: adopting the superficial practices of successful teams without understanding what makes those practices valuable.

```
THE CARGO CULT STORY:

  After WWII, some Pacific islanders saw military planes bring
  goods. They built fake airstrips, fake control towers, and fake
  headsets from coconuts — hoping to summon the cargo planes back.
  
  The ritual looked right but missed the point entirely.
  
  Same thing happens with software practices:
  → "Spotify uses squads and tribes, so we should too"
  → "Netflix does chaos engineering, let's do that"
  → "Google has OKRs, we need OKRs"
  
  Without understanding WHY these work, you get the coconuts.
```

### How to Choose Practices

```
DON'T ask: "What does Google/Netflix/Spotify do?"
DO ask:    "What problem am I trying to solve?"
           "Does this practice address that problem?"
           "Can I measure whether it's working?"
           "Can I abandon it if it doesn't?"

Context matters. What works in one organization won't necessarily
work in yours.
```

---

## 🔑 Topic 51 — Pragmatic Starter Kit

### 💡 Tip 89: Use Version Control to Drive Builds, Tests, and Releases

Three practices every project must have, non-negotiably:

```
THE PRAGMATIC STARTER KIT:

  ┌─────────────────────────────────────────────────────────────┐
  │  1. VERSION CONTROL                                         │
  │     Everything in version control. Everything.              │
  │     Code, config, docs, scripts, infrastructure.            │
  │     VCS is the single source of truth.                     │
  │                                                             │
  │  2. RUTHLESS AND CONTINUOUS TESTING                         │
  │     Tests run automatically on every commit.                │
  │     Unit → Integration → E2E → Performance → Security.     │
  │     A failing test stops everything until fixed.            │
  │                                                             │
  │  3. FULL AUTOMATION                                         │
  │     Build, test, deploy — all automated.                   │
  │     No manual steps. If it can't be automated, understand   │
  │     why not. Humans introduce errors; machines don't.       │
  └─────────────────────────────────────────────────────────────┘
```

### Continuous Integration / Continuous Delivery

```
IDEAL CI/CD PIPELINE:

  Developer pushes code
        ↓
  Automated build runs
        ↓
  Unit tests run (fast, <5 min)
        ↓
  Integration tests run
        ↓
  Code quality checks (linting, security scan)
        ↓
  Deploy to staging automatically
        ↓
  E2E tests run against staging
        ↓
  Deploy to production (automatically or with one click)
        ↓
  Monitor and alert

  If anything fails → stop, notify, fix before proceeding.
```

### Testing Strategy

| Test Type | Speed | When to Run | What It Catches |
|---|---|---|---|
| Unit tests | Seconds | Every save | Logic errors in isolation |
| Integration | Minutes | Every commit | Component interaction bugs |
| System/E2E | Minutes-hours | Every merge | Full workflow failures |
| Performance | Hours | Nightly | Regressions in speed |
| Security | Hours | Nightly | Vulnerabilities |

> **Rule:** A test that isn't run automatically isn't really a test — it's wishful thinking.

---

## 🔑 Topic 52 — Delight Your Users

### 💡 Tip 91: Delight Users, Don't Just Deliver Code

Users don't want features. They want their **problems solved**. There's a difference:

```
FEATURE DELIVERY:                    USER DELIGHT:
┌────────────────────────────┐      ┌────────────────────────────────┐
│ "We shipped the reporting  │      │ "The sales team can now get    │
│ module on time."           │      │ the insights they need in      │
│                            │  →   │ 30 seconds instead of 3 days.  │
│ → Did the user's life      │      │ Their pipeline review meetings │
│   get better? Unknown.     │      │ went from 2 hours to 20 mins." │
└────────────────────────────┘      └────────────────────────────────┘
        ❌ Feature shipped                   ✅ Problem solved
```

### The Expectation Gap

Users have expectations that go beyond explicit requirements. A pragmatic programmer:
- Understands the user's **real underlying goal**, not just the stated request
- Asks "What would make this truly useful?" not just "What was specified?"
- Delivers surprises that solve problems users didn't know to ask about

> *"Your job is not to build software. Your job is to make your users' lives better."*

---

## 🔑 Topic 53 — Pride and Prejudice

### 💡 Tip 92: Sign Your Work

Craftspeople of old signed their work. A stonemason's mark, a silversmith's hallmark. They were proud of what they made and willing to be held accountable for it.

Pragmatic Programmers should feel the same way about their code:

```
WHAT PRIDE IN YOUR WORK MEANS:

  ✅ You write code you'd be happy to show anyone
  ✅ You leave code better than you found it
  ✅ You take ownership — bugs are your bugs, improvements are your joy
  ✅ You don't hide problems; you surface them
  ✅ You don't ship something you wouldn't use yourself
```

### Prejudice Against Bad Code

The other side of pride: **refuse to make bad compromises**. Have a professional prejudice against:
- Code you don't understand
- "Quick hacks" that become permanent
- Tests you skip "just this once"
- Documentation you defer forever

```
THE CRAFTSPERSON'S STANDARD:

  "We who cut mere stones must always be envisioning cathedrals."

  Even if your current task is small and unglamorous, do it with
  the care and skill of someone building something that lasts.
```

---

## 📊 Chapter Summary — And The Whole Book

```
┌──────────────────────────────────────────────────────────────────┐
│                    CHAPTER 9 MENTAL MODEL                        │
│                                                                  │
│  PRAGMATIC TEAMS  → Apply all individual practices at scale     │
│                     Small, stable, trusted, autonomous teams    │
│                                                                  │
│  CARGO CULTS      → Adopt practices because they solve problems │
│                     not because Netflix or Google does them     │
│                                                                  │
│  STARTER KIT      → Version control + Testing + Automation      │
│                     These three are non-negotiable, always      │
│                                                                  │
│  DELIGHT USERS    → Solve their real problems, not their stated │
│                     requirements. Understand the why.           │
│                                                                  │
│  PRIDE            → Own your work. Sign it. Be willing to have  │
│                     your name on it.                            │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🗺️ The Entire Book In One View

```
CHAPTER 1: A PRAGMATIC PHILOSOPHY
  → It's your career. Take responsibility. Fix broken windows.
    Invest in your knowledge. Communicate.

CHAPTER 2: A PRAGMATIC APPROACH
  → Good design = easy to change (ETC). DRY. Orthogonal.
    Tracer bullets. Prototypes. Estimate.

CHAPTER 3: THE BASIC TOOLS
  → Plain text. Shell. Editor fluency. Version control.
    Debugging. Text manipulation. Daybooks.

CHAPTER 4: PRAGMATIC PARANOIA
  → Design by Contract. Crash early. Assert always.
    Balance resources. Take small steps.

CHAPTER 5: BEND, OR BREAK
  → Decouple. Respond to events. Think in transformations.
    Avoid inheritance. Externalize configuration.

CHAPTER 6: CONCURRENCY
  → Remove temporal coupling. Shared state is incorrect state.
    Use actors. Use blackboards.

CHAPTER 7: WHILE YOU ARE CODING
  → Trust your instincts. Code deliberately. Know Big-O.
    Refactor. Test to design. Property tests. Security. Naming.

CHAPTER 8: BEFORE THE PROJECT
  → Requirements are discovered. Challenge constraints.
    Work together. Be truly agile.

CHAPTER 9: PRAGMATIC PROJECTS
  → Scale practices to teams. Avoid cargo cults.
    Version control + Testing + Automation. Delight users. Pride.
```

---

## 💡 Key Takeaways

| # | Takeaway |
|---|---|
| 1 | **Pragmatic teams** apply all individual practices at the team level |
| 2 | **Copy practices that solve problems**, not practices that seem cool |
| 3 | **The Starter Kit is non-negotiable**: version control, tests, automation |
| 4 | **Your job is to delight users** — solve their real problems |
| 5 | **Take pride in your work** — sign it, own it, be accountable for it |
| 6 | **Kaizen**: the goal is continuous improvement, every day, forever |

---

## 🎯 The Pragmatic Programmer's North Star

> **Care About Your Craft** — There is no point in developing software unless you care about doing it well.

> **Think! About Your Work** — Don't run on autopilot. Constantly critique what you're doing, in real time, every day.

---

*← [Chapter 8 — Before the Project](08-before-the-project.md) | [Back to Index](../README.md)*
