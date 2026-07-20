# Chapter 2: What Staff Engineers Actually Do
## *The Five Core Activities That Replace Writing Code as Your Primary Output*

---

## 🎯 Core Concept

The honest answer to "what do Staff engineers do?" is: they keep doing what made them successful as Senior engineers — building relationships, writing software, coordinating projects. But the **misleading** part of that answer is this: at the Senior level, those activities *were* the work. At the Staff level, they're **auxiliary** to the actual work.

> **The shift:** Your primary product is no longer code. It's organizational clarity, technical direction, and the growth of the engineers around you. Code is now a tool you use to stay grounded — not the deliverable.

---

## 🗺️ The Five Core Activities

```
┌─────────────────────────────────────────────────────────────────────────┐
│             WHAT STAFF ENGINEERS ACTUALLY DO                             │
│                                                                          │
│  1. SETTING TECHNICAL DIRECTION                                          │
│     Speaking for technology's long-term needs                           │
│     Like a part-time product manager for the tech stack                 │
│                                                                          │
│  2. MENTORSHIP & SPONSORSHIP                                             │
│     Growing engineers around you (not just yourself)                    │
│     Sponsorship > Mentorship at this level                              │
│                                                                          │
│  3. PROVIDING ENGINEERING PERSPECTIVE                                    │
│     Injecting technical context into org decisions                      │
│     Being pulled into "the room" at critical moments                    │
│                                                                          │
│  4. EXPLORATION                                                          │
│     Trusted agents for ambiguous, important problems                    │
│     "What if we reduced infra costs by 10x?"                           │
│                                                                          │
│  5. BEING GLUE                                                           │
│     The unglamorous coordination that keeps teams moving                │
│     Invisible but high-impact                                           │
│                                                                          │
│  + Still writing SOME code (varies significantly by archetype)          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🧭 Activity 1: Setting Technical Direction

Staff engineers speak for technology — because technology cannot speak for itself.

### The Part-Time Product Manager for Tech

```
PRODUCT MANAGER               STAFF ENGINEER'S TECH PM ROLE
─────────────────             ──────────────────────────────
Speaks for users              Speaks for technology
"What do customers want?"     "What does our stack need?"
Roadmaps features             Roadmaps technical health
Balances now vs future        Balances now vs future

Both: Pragmatic, deliberate, focused on long-term trend of progress
```

### What It Looks Like in Practice

- **Finding and advocating for** effective architectural approaches across teams
- **Editing and aligning** different teams' technical approaches (even when not asked)
- **Nudging** designs toward long-term correctness, not just short-term functionality

> *"I feel most impactful when I can facilitate setting a technical vision for an area and get people moving toward that vision."* — Joy Ebertz

### The Critical Mindset Shift

```
SENIOR ENGINEER:              STAFF ENGINEER:
────────────────              ───────────────
"What tech do I want         "What does the organization
 to learn/use?"               actually need?"

"This is the right           "What's the real problem
 technology choice."          behind this decision?"

Accountable to self          Accountable to the business first,
                             then themselves
```

---

## 🌱 Activity 2: Mentorship and Sponsorship

The popular image of heroic leadership — one brilliant person whose decisions change everything — is mostly PR. The real leverage at Staff level comes from **growing the engineers around you**.

### Mentorship vs. Sponsorship

```
MENTORSHIP                    SPONSORSHIP
──────────                    ───────────
Sharing experience            Putting your thumb directly on the scale
Giving advice                 Advocating for someone in rooms they're not in
Answering questions           Nominating people for opportunities
Low direct risk               Your reputation is attached
                              High direct impact

Both matter. Sponsorship has more impact per hour invested.
```

### The Leverage Math

```
Senior Engineer heroics:
  Your output → 1x impact

Staff Engineer growing 5 engineers:
  Your coaching → 5 engineers × each 1.2x better → 6x+ impact

Staff Engineer sponsoring 2 engineers into new roles:
  → 2 engineers with expanded scope → ongoing multiplier effect
```

### Example: Michelle Bu at Stripe

> *"In my current role, I feel energized when someone I've sponsored sends an announcement that they've shipped their work... It's these teams, not me, who are doing the hard work day-to-day. I measure my impact based on their progress."*

Michelle keeps a list of folks she considers highly capable and actively advocates for them as visible opportunities arise. She scales her impact by disseminating mental models — like a shared vocabulary for categorizing APIs — that spread organically through the org.

---

## 🚪 Activity 3: Providing Engineering Perspective

When a critical, time-sensitive decision needs to be made — an org restructure, an unusual hire, a roadmap pivot — the right people often aren't in the room. Staff engineers frequently get pulled into these moments unexpectedly.

### The Unexpected-Decision Problem

```
ROUTINE DECISIONS:           UNEXPECTED DECISIONS:
─────────────────            ─────────────────────
Process handles it           Who do you call?
Right people automatically   Often the wrong people
in the room                  Short timeline
                             High stakes
                             Engineering context missing

Staff engineers plug this gap — they get pulled in
because they carry cross-cutting context.
```

### Real Examples of Where Engineering Perspective Matters

| Situation | What's Missing Without Engineering Input |
|---|---|
| Org restructure decision | Which teams depend on each other? What breaks? |
| Interviewing for new exec | Does this candidate understand technical tradeoffs? |
| Roadmap for next quarter | Which "easy" features are actually 6-month efforts? |
| Contract with enterprise customer | Can we actually support these SLAs? |
| Acquisition due diligence | What's the real state of their technical debt? |

> *"I have a seat at the table at higher-level engineering discussions... We discuss problems that span teams which are both technical and non-technical in nature."* — Dan Na

---

## 🔭 Activity 4: Exploration

Sometimes the most important work is figuring out *what* the important work is.

### The Hill-Climbing Problem

```
HILL-CLIMBING ALGORITHM:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  You're on a mountain.
  You turn around. Look for the highest nearby point.
  Walk there. Repeat.

  Result: You reach the top of WHATEVER MOUNTAIN YOU'RE ON.
  Problem: You might not be on the right mountain.

  🌫️ On a foggy day? You might miss a higher peak just out of sight.

ORGANIZATIONAL HILL-CLIMBING:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Company is optimized for current business
  → Hard to explore adjacent opportunities
  → Hard to see threats until they're close
  → Hard to question what made you successful

  Solution: Assign trusted explorers to leave the mountain.
```

### What Exploration Looks Like

- *"Can we reduce infrastructure costs by 10x?"* — needs someone to stop optimizing current infra and think from scratch
- *"Could we support multi-region in 6 months instead of 3 years?"* — needs someone to explore the actual constraints
- *"Our database has 3 months of disk space remaining"* — needs someone to find a path that isn't just "buy bigger servers"

> *"This is some of the most rewarding and the riskiest work companies do. It takes a great deal of organizational trust to be trusted with this work."*

### The Organizational Trust Required

Exploration requires trust that if you *fail*, it reflects on the problem difficulty — not on your competence. This trust is earned over time through a track record of judgment.

---

## 🧲 Activity 5: Being Glue

[Tanya Reilly's seminal post "Being Glue"](https://noidea.dog/glue) describes the unglamorous but critical coordination work that makes organizations function.

### What Glue Work Looks Like

```
VISIBLE WORK (gets credit)       GLUE WORK (often invisible)
───────────────────────────      ──────────────────────────────
Shipping a feature               Writing the runbook
Building a service               Clarifying requirements
Code review                      Scheduling the review meeting
Designing the architecture       Making sure all stakeholders saw it
Writing the design doc           Following up when people didn't respond
                                 Keeping the project moving when stalled
                                 Noticing what's missing
                                 Onboarding the new engineer
```

### Why Staff Engineers Take Responsibility for Glue

1. **Their organizational reach** makes them effective at cross-team coordination
2. **Their modeling** signals that glue work is valued, not below anyone's station
3. **Their experience** lets them do glue work efficiently
4. High-impact organizations often have Staff engineers doing glue work *behind the scenes*

> ⚠️ **Warning:** Early-career engineers who do disproportionate glue work often get stuck. They're valuable, but not perceived as "technical." Glue work is only safe to do in volume once your technical reputation is established.

---

## 💻 But Will You Still Write Code?

The universal Staff engineer question. The honest answer: **Yes, but much less — and it varies by archetype.**

```
CODING % BY ARCHETYPE & ROLE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Tech Lead     ████████░░░░░░░░░░░░   ~20-30%
  Architect     █████░░░░░░░░░░░░░░░   ~10-20%
  Solver        ██████████████░░░░░░   ~40-60% (when deep in problem)
  Right Hand    ██░░░░░░░░░░░░░░░░░░   ~5-10%

  Senior Eng    ███████████████████░   ~70-80%
```

### What They Code

| Engineer | What They Actually Write |
|---|---|
| **Ras Kasa Williams** (Mailchimp) | Code regularly but less than teammates; "hand to keyboard" to stay informed |
| **Katie Sylor-Miller** (Etsy) | Mostly SQL for data analysis; JS/PHP occasionally to unblock teams |
| **Joy Ebertz** (Split) | Some coding in early ramp-up; moves toward strategy and vision |
| **Bert Fan** (Slack) | Prototyping concepts that will likely be thrown away; builds apps to test developer experience |

> *"The more senior you get, the less your job is about code... The higher you get, the more your job becomes about mentoring and growing the people around you."* — Joy Ebertz

### The Danger Signal

If you're spending most of your time coding as a Staff engineer, ask yourself: **"Is this important work that only I can do, or am I doing it because it's comfortable?"**

The latter is a warning sign that you're avoiding the harder, higher-leverage Staff-level work.

---

## ⏳ The Slow Feedback Loop Problem

Perhaps the biggest adjustment for new Staff engineers:

```
SENIOR ENGINEER FEEDBACK LOOP:
  Write code → Test → Ship → See results → Repeat
  Time: Hours to days

STAFF ENGINEER FEEDBACK LOOP:
  Influence strategy → Teams adopt → Architecture changes → Business results
  Time: Weeks to months to years
```

### How to Stay Sane

- **Accept that some days feel unproductive** — this is normal at the Staff level
- **Keep short-feedback-loop activities** in your week (code reviews, 1:1s, quick edits)
- **Track your indirect impact** — who did you unblock? What decision did you improve?
- **Measure quarterly, not daily** — the work shows up over longer timeframes

> *"None of them regretted their transition into their current roles"* — despite wishing they had more coding time, every Staff engineer interviewed said the impact and personal growth justified the change.

---

## ✅ Key Takeaways

| # | Takeaway |
|---|---|
| 1 | **Code is now a tool, not the deliverable** — your primary output is organizational clarity |
| 2 | **Setting technical direction** is like being a part-time PM for your tech stack |
| 3 | **Sponsorship outweighs mentorship** in leverage — advocate for others in rooms they're not in |
| 4 | **Engineering perspective in decisions** is one of the highest-leverage activities you can do |
| 5 | **Exploration work** requires high organizational trust and a track record of good judgment |
| 6 | **Glue work is real and important** — don't let it be invisible, and don't let early-career engineers drown in it |
| 7 | **The feedback loop slows dramatically** — learn to track impact over weeks and months, not days |
| 8 | **Coding continues, just less** — if you're coding all the time, ask whether it's important or just comfortable |

---

*← [Chapter 1 - Archetypes](01-staff-engineer-archetypes.md) | [Back to Index](../README.md) | Next: [Chapter 3 - Does the Title Matter?](03-does-the-title-matter.md) →*
