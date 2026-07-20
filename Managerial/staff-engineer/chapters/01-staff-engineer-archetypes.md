# Chapter 1: Staff Engineer Archetypes
## *The Four Patterns Hidden Behind a Single Title*

---

## 🎯 Core Concept

Every company calls them "Staff Engineer" — but underneath that single title hide **four fundamentally different roles**. Career ladders apply the same expectations to everyone, but real Staff engineers cluster into four distinct archetypes with different daily work, different success criteria, and different company contexts where they thrive.

> **Key insight:** Before pursuing a Staff role, understand *which archetype* you're actually pursuing — and whether your company even has room for it.

---

## 🗺️ The Four Archetypes

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       THE 4 STAFF ENGINEER ARCHETYPES                    │
│                                                                          │
│   TECH LEAD           ARCHITECT           SOLVER          RIGHT HAND    │
│   ─────────           ─────────           ──────          ──────────    │
│                                                                          │
│   Guides 1 team       Owns a domain       Digs into       Extends an    │
│   or cluster          (API, infra,        knotty          executive's   │
│                        storage, cloud)    problems        reach         │
│                                                                          │
│   Partners with       Combines deep       Goes deep       Borrows       │
│   1–3 managers        tech + business     until solved,   authority     │
│                       knowledge           then moves on   from sponsor  │
│                                                                          │
│   Most code           Less code           Variable        Little code   │
│   delegation          Arch reviews        Mostly deep     Mostly org    │
│   cross-team          vision setting      technical       & cultural    │
│   relationships                                                          │
│                                                                          │
│   AVAILABILITY: ──────────────────────────────────────────────────────  │
│   All companies    100+ engineers     Individual-     1000+ engineers   │
│   agile-oriented   + complex debt     ownership       orgs only         │
│                                       cultures                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔵 Archetype 1: Tech Lead

The **most common** Staff archetype. Tech Leads guide the approach and execution of one team or a small cluster of teams.

### What They Do

```
TECH LEAD TYPICAL WEEK:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Monday     → 1:1 with PM on roadmap shuffle
  Tuesday    → Architecture review for Q3 initiative
  Wednesday  → Code review + unblocking 2 team members
  Thursday   → Cross-team dependencies meeting + design doc
  Friday     → Strategy doc + team retro facilitation

  Weekly %:
  ├── Coding:            ~20% (down from 70% as Senior)
  ├── Coordination:      ~30%
  ├── Design/strategy:   ~25%
  └── Mentorship/1:1s:  ~25%
```

### Key Characteristics
- **Carries the team's context** — first call when roadmap needs shuffling
- **Delegates complex projects** to grow teammates, not to avoid work
- **Defines technical vision** while stepping in to build alignment on hard issues
- **Ratio:** ~1 Tech Lead per 8 engineers — the most accessible archetype

### Example: Diana Pojar at Slack
> Diana is the Staff Data Engineer and Tech Lead for the Data Platform team. Her focus: working on projects with strategic value to the company while driving technical design and up-leveling her team. Her time splits roughly 50/50 between technical leadership and execution/mentoring.

### Is Tech Lead Right for You?
✅ You enjoy long-term relationships with the same people and problems  
✅ You want to be deeply involved in how a team succeeds day-to-day  
✅ You're energized by mentoring and unblocking others  
❌ You hate management-adjacent work (roadmaps, PMs, coordination)  
❌ You want to stay heads-down in code  

---

## 🟢 Archetype 2: Architect

**Architects** are responsible for the direction, quality, and approach within a **critical technical domain** — the company's API design, frontend stack, storage strategy, or cloud infrastructure.

### What They Do

```
ARCHITECT TYPICAL WEEK:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Monday     → API design review for 3 teams
  Tuesday    → Architecture document drafting
  Wednesday  → RFC feedback + vendor evaluation
  Thursday   → Engineering all-hands + leadership sync
  Friday     → Mentoring session + strategy update

  Domain ownership (example: Keavy McMinn at Fastly):
  ├── Set API strategy for the entire org
  ├── Approve significant API changes
  ├── Research + recommend new approaches
  └── Build shared vocabulary across teams
```

### The Toxic Myth vs. Reality

```
❌ MYTH:                          ✅ REALITY:
──────────────────────────────    ──────────────────────────────
Architects design in isolation    Architects earn authority by
and hand specs to others to       demonstrating consistently
implement.                        good judgment through deep
                                  engagement with business needs,
                                  user goals, and technical
                                  constraints.
```

### Key Characteristics
- Domain must be **complex** AND **enduringly central** to company success
- Deep business understanding — not just technical knowledge
- Earned organizational authority, not positional authority
- Some companies require architects to code; others explicitly forbid it

### Example: Katie Sylor-Miller at Etsy
> As Frontend Architect, Katie looks at what *all* of Etsy is doing in the frontend space — not just one team. She's responsible for future direction, problem identification, and technical advocacy company-wide.

### Is Architect Right for You?
✅ You love deep mastery of a specific domain  
✅ You want to shape direction across many teams  
✅ You're patient — architectural change takes years  
❌ You don't want to stay in one technical area long-term  
❌ You hate influencing without authority  

---

## 🟡 Archetype 3: Solver

**Solvers** are trusted agents dropped into critical, knotty problems — the ones that either lack a clear approach or carry high execution risk.

### What They Do

```
SOLVER LIFECYCLE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Leadership identifies        ←── "Our primary database has
  critical problem                  3 months of disk space left"

       ↓
  Solver gets assigned         ←── Trusted, experienced engineer
  to the problem                    with track record

       ↓
  Digs deep, works through     ←── Weeks to months of focus
  ambiguity and complexity

       ↓
  Problem contained/solved     ←── Hands off to team for maintenance

       ↓
  Solver moves to next fire    ←── Often feels transient
```

### Key Characteristics
- Works on **pre-identified organizational priorities** — less org wrangling needed
- **Stops working on problems once contained** — can feel transient
- Requires a soft touch when handing off "solved" problems to maintenance teams
- Most common in companies that value **individuals over teams** as planning units

### Example: Nelson Elhage at Stripe
> Nelson and two other senior engineers spent a year building Sorbet (Stripe's static Ruby type checker) from scratch — then worked on Payment Architecture. Both were critical organizational bets where senior engineers were pulled from normal work to solve high-priority problems.

### Is Solver Right for You?
✅ You love diving deep into hairy technical problems  
✅ You're energized by variety — different problems every few months  
✅ You're comfortable with ambiguity and organizational chaos  
❌ You want community and long-term relationships with a team  
❌ You need recognition for the work after you leave it  

---

## 🔴 Archetype 4: Right Hand

The **rarest** archetype. Right Hands extend a senior executive's attention, borrowing their scope and authority to operate in particularly complex organizations.

### What They Do

```
RIGHT HAND MODEL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  VP of Infrastructure (Matthew)
         │
         │  "I need 10x more bandwidth"
         │
         ▼
  Right Hand (Rick Boone)
         │
         ├── Attends VP's staff meetings
         ├── Removes important problems from VP's plate
         ├── Dives into fires → edits approach → delegates
         ├── Operates with VP's borrowed authority
         └── Must think: "What would Matthew do here?"

  Problems addressed:
  ─────────────────────────────────────────────
  Business × Technology × People × Culture × Process
  (Never purely technical)
```

### The "Hand of the King" Mental Model

Rick Boone compared his role to two famous fictional characters:
- **Hand of the King** (Game of Thrones) — operates with the king's authority to act on their behalf
- **Leo McGarry** (The West Wing) — "I serve at the pleasure of the President"

> *"People need to be confident that I'll always give the same answer that Matthew would give if he were there."* — Rick Boone

### Key Characteristics
- **Borrowed authority** — only valid while aligned with the sponsoring executive
- Works on problems where business + technology + people all intersect
- Always onto the next fire before the current one is fully resolved
- Requires 1000+ engineer organizations to justify

### Is Right Hand Right for You?
✅ You love organizational complexity as much as technical complexity  
✅ You're deeply aligned with leadership values  
✅ You're energized by the highest-priority problems  
❌ You want long-term ownership of outcomes  
❌ You need clear separation between your role and politics  

---

## 📊 Archetypes by Company Stage

```
COMPANY GROWTH → ARCHETYPE AVAILABILITY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Engineers:   10─────────50──────────100──────────500──────1000+

  Tech Lead:   ████████████████████████████████████████████████
               (Available from the start)

  Solver:      ────────────████████████████████████████████████
               (Depends on culture: individual vs team ownership)

  Architect:   ────────────────────────████████████████████████
               (Emerges ~100 engineers)

  Right Hand:  ────────────────────────────────────────────████
               (Emerges ~1000 engineers)
```

---

## 🔄 Moving Between Archetypes

You're not locked into one archetype forever. Over a 30–40 year career, most engineers sample multiple archetypes:

| Career Phase | Common Pattern |
|---|---|
| First Staff role | Tech Lead (most accessible) |
| Mid-career | Architect (if domain expertise deepens) |
| Senior Staff+ | Solver or Right Hand (if org grows large enough) |
| Any phase | Depends heavily on company type and culture |

> **The key question:** What kind of work *energizes* you? Tech Leads and Architects work with the same people for years. Solvers and Right Hands bounce between fires and have more transactional relationships. Neither is better — they're just different.

---

## ✅ Key Takeaways

| # | Takeaway |
|---|---|
| 1 | **There are 4 archetypes**, not 1 Staff Engineer role — understand which one you're pursuing |
| 2 | **Tech Lead is most accessible** — 1 per 8 engineers, available at all company sizes |
| 3 | **Architect requires a domain** that is both complex and enduringly central to the business |
| 4 | **Solver thrives in individual-ownership cultures** — less common in team-centric agile orgs |
| 5 | **Right Hand only exists at 1000+ engineer orgs** and requires executive sponsorship |
| 6 | **Match archetype to your energy** — the work you find draining will drain your performance too |
| 7 | **Career ladders obscure this** — two people with the same title may do fundamentally different jobs |

---

*← [Back to Index](../README.md) | Next: [Chapter 2 - What Staff Engineers Actually Do](02-what-staff-engineers-actually-do.md) →*
