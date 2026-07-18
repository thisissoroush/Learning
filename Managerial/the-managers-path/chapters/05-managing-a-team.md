# Chapter 5: Managing a Team
## *From individual coaching to team health — a totally different job*

---

## 🎯 Core Concept

Managing a team is **not** just "managing several individuals at once." It requires a completely new focus: the health and output of the collective unit, not just each person in it. Your job becomes identifying bottlenecks, driving decisions, and shielding/enabling the team to do their best work.

---

## 🛠️ Stay Technical (Even If You Write Less Code)

Engineering management is a **technical discipline**, not just people management. Staying technical matters because:

```
WHY YOU MUST STAY TECHNICAL:

  1. CREDIBILITY — Engineers must see you as technically capable
  2. SMELL TEST — You need instincts to evaluate technical decisions
  3. BOTTLENECK DETECTION — You feel pain points others report
  4. PRODUCT SENSE — You can identify shortest paths to features
  5. TRUST — Teams trust managers who understand what they do

HOW TO STAY TECHNICAL AT THIS LEVEL:

  • Write small features, bug fixes (don't block the team)
  • Do code reviews (secondary reviewer is fine)
  • Participate in incidents and on-call
  • Pair with engineers on problems
  • Attend postmortems
```

> If the build is slow, deploying takes too long, or on-call is a nightmare — you'll feel it when you try to ship a trivial task. That's valuable signal.

---

## 🔍 Debugging Dysfunctional Teams

When your team is struggling, treat it like a systems debugging problem. Here are the most common dysfunctions and their fixes:

### Dysfunction 1: Not Shipping

```
SYMPTOMS:                        ROOT CAUSES:
  • Missed deadlines               • Releases are painful & infrequent
  • Work "in progress" forever     • Features are too big to ship
  • Team seems stuck               • Poor tooling / manual testing
                                   • No culture of small deliverables

FIX: Push for more frequent releases.
  → Infrequent releases HIDE pain points.
  → Daily deploys force small commits, reveal tooling issues,
    reduce conflict over the release slot, and improve morale.
```

### Dysfunction 2: People Drama

```
TYPES:
  The Brilliant Jerk — high output, toxic to everyone around them
  The Energy Vampire — constant negativity, gossip, us-vs-them

FIX:
  → Address directly and quickly — don't let it fester
  → Public bad behavior requires public correction
  → If they won't change, move them out of the team
  → Brilliant jerks rarely get better; protect the team
```

### Dysfunction 3: Overwork

```
CAUSES:                          FIXES:
  Unstable production systems    → Dedicate 20% time to stability
  Crunch culture                 → Be physically present during crunches
  Poor planning                  → Order dinner, show appreciation
                                 → Ensure explicit break time after
```

### Dysfunction 4: Collaboration Problems

```
FIXES:
  → Regular touchbases with adjacent team leads
  → Never undermine peers publicly (even when frustrated)
  → Create social opportunities: lunch, off-sites, low-key events
  → Psychological safety comes from human connection first
```

---

## 🧭 The Shield: What It Is and Isn't

Many books say managers should "shield" their teams from organizational drama. This is partially true — but easily taken too far.

```
GOOD SHIELDING:                  BAD SHIELDING:
  ✅ Filter irrelevant drama       ❌ Hide important company news
  ✅ Translate strategy to goals   ❌ Pretend problems don't exist
  ✅ Give context, not chaos       ❌ Treat your team like children
  ✅ Let stress through when       ❌ Deny layoffs/changes until
     context helps them decide        rumors fill the vacuum
```

**Key truth:** Your team is made up of adults. They need *context* to make good decisions — not protection from reality. Give them enough information to understand *why* they're working on what they're working on.

---

## ⚖️ Driving Good Decisions

As the engineering manager, you are accountable for how decisions turn out — even though you're not making all of them yourself.

```
4 LEVERS FOR GOOD TEAM DECISIONS:

  1. DATA CULTURE
     → Add engineering metrics alongside product metrics
     → Track: time to complete features, bug rates, deploy frequency
     → Data depersonalizes arguments about priorities

  2. CUSTOMER EMPATHY
     → Understand who depends on your team's output
     → Context on customer impact guides where to invest effort

  3. FORWARD THINKING
     → Know the product roadmap 2 steps ahead
     → Use that to guide technical investment decisions

  4. RETROSPECTIVES
     → Review outcomes of past decisions
     → Were the hypotheses right? What did we learn?
```

---

## ⚔️ Conflict: Avoider vs. Tamer

Conflict-avoidant managers create the illusion of harmony while real problems fester.

```
JASON (Conflict Avoider):
  • Hates saying no — team gets overloaded
  • Uses consensus/voting to dodge responsibility
  • Charles never heard feedback → blindsided by team vote
  • Team describes him as "cool but nothing gets resolved"

LYDIA (Conflict Tamer):
  • Tells Charles directly in a 1-1 that priorities changed
  • Sets clear decision processes for the group
  • Doesn't enjoy difficult conversations — but has them
  • Team describes her as "tough but fair"
```

### The Dos and Don'ts

| DO | DON'T |
|---|---|
| Set up clear decision processes | Rely exclusively on consensus/voting |
| Address issues without creating drama | Turn a blind eye to simmering problems |
| Be kind (honest + caring) | Aim to be nice (pleasant + conflict-avoiding) |
| Get curious about your avoidance | Take conflict out on other teams |
| Make the call when needed | Use the team to avoid making hard decisions |

---

## 🦠 Team Cohesion Destroyers

The goal is **psychological safety** — a team where people take risks, share work in progress, and admit mistakes without fear.

### The Brilliant Jerk
High individual output, but creates fear and resentment. The team becomes less effective around them. Best practice: **don't hire them**. Once hired, removing them requires courage most managers don't muster quickly enough. Protect your team from the behavior publicly and directly.

### The Noncommunicator
Works in secret, doesn't share WIP, reverts others' commits, skips code review. Usually driven by fear of judgment. Address the root cause — is the team culture too harsh? Is this person an outsider?

### The Disrespectful Employee
Simply put: ask them directly if they want to be on the team. If yes, set clear expectations. If no, begin the transition. You cannot have someone who doesn't respect the team or their manager. It poisons everyone.

---

## 📐 Project Management Rules of Thumb

```
RULE 1: 10 productive engineering weeks per person per quarter
  (13 weeks minus vacations, reviews, incidents, onboarding)

RULE 2: Budget 20% for sustaining engineering
  (testing, cleanup, refactoring, legacy code, process improvement)
  Never schedule to 100% — it will slow you down

RULE 3: As deadlines approach, your job is to say NO
  → Partner with tech lead + PM to cut scope
  → Push back on "must-haves" that aren't must-haves

RULE 4: Use the doubling rule for quick estimates
  → Double your gut estimate for off-the-cuff answers
  → For anything > 2 weeks: double AND ask for planning time

RULE 5: Don't barrage engineers with random estimates
  → You handle uncertainty; don't pass all of it to the team
```

---

## 💡 Key Takeaways

| # | Takeaway |
|---|---|
| 1 | **Stay technical** — your credibility and instincts depend on it |
| 2 | **Teams not shipping = systems problem** — fix the process, not the people |
| 3 | **Deal with drama fast** — brilliant jerks poison everyone around them |
| 4 | **Shield appropriately** — context helps your team, ignorance hurts them |
| 5 | **Conflict avoidance is not kindness** — it's a slow poison |
| 6 | **Psychological safety is the foundation** — everything else builds on it |
| 7 | **20% slack is not optional** — it's what keeps your team from grinding to a halt |

---

*← [Chapter 4 - Managing People](04-managing-people.md) | [Back to Index](../README.md) | Next: [Chapter 6 - Managing Multiple Teams](06-managing-multiple-teams.md) →*
