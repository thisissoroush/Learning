# Chapter 6: Managing Multiple Teams
## *The plate-spinning phase — where you stop coding and start multiplying*

---

## 🎯 Core Concept

At this level (typically Director of Engineering), you are responsible for several teams you can no longer be embedded in. You are no longer a maker — you're a multiplier. The job is **breadth over depth**: keeping many plates spinning without letting any crash, while still staying technically credible enough to guide decisions.

> "If your team needs a manager more than they need an engineer, you have to accept that being that manager means you by definition can't be that engineer."
> — Cate Huston

---

## 💻 Staying Hands-On (Without Writing Production Code)

You're likely not writing code every day anymore. That's OK — but you must stay technically connected:

```
WAYS TO STAY TECHNICAL WITHOUT WRITING PRODUCTION CODE:

  ✅ Code reviews (secondary reviewer on key systems)
  ✅ Read PRs and check-ins regularly
  ✅ Attend and contribute to postmortems
  ✅ Pair with engineers on complex problems
  ✅ Fix minor bugs or write small scripts
  ✅ Engage deeply with architecture discussions
  ✅ Keep one half-day/week free for creative/technical work
     (blog posts, open source, conference talks, deep reading)

❌ DON'T: Write code that creates a support burden for the team
❌ DON'T: Go hands-off completely — you'll lose instinct
```

**The mastery threshold:** Before moving into this role, ensure you're fluent in at least one language — meaning you can be productive in a real codebase with standard tools. That fluency stays with you even when you stop daily coding.

---

## ⏰ Managing Your Time: Urgency vs. Importance

The most critical time management insight at this level:

```
                    NOT URGENT        |        URGENT
                ______________________|______________________
                |                    |                      |
   IMPORTANT    |   STRATEGIC        |   OBVIOUS WORK       |
                |   (make time!)     |   (just do it)       |
                |____________________|______________________|
                |                    |                      |
  UNIMPORTANT   |   OBVIOUS AVOID    |   TEMPTING           |
                |                    |   DISTRACTIONS       |
                |____________________|______________________|

Examples of IMPORTANT but NOT URGENT (these get neglected!):
  • Writing job descriptions before you urgently need to hire
  • Reviewing team health before someone quits
  • Having that peer conversation before it escalates
  • Developing your rising leaders before you need them
  • Preparing for meetings so they're productive
```

**The trap:** Email, Slack, and meetings *feel* urgent but often aren't. You will spend days feeling busy while neglecting the strategic work that matters most.

---

## 🎪 Plate Spinning: The New Mental Model

```
        [Team A]   [Team B]   [Team C]   [Team D]
           🍽️         🍽️         🍽️         🍽️
           |           |           |           |
           |           |           |           |
           └───────────┴───────────┴───────────┘
                              |
                          YOU (Director)

Your job: Keep each plate spinning — attend to each team
before it slows down enough to crash.

WHAT MAKES A PLATE WOBBLE:
  • Manager struggling quietly
  • Team losing engagement
  • Project falling behind without visibility
  • Attrition about to happen
  • Tech debt accumulating past the tipping point
```

**You get better at this with experience.** Instincts develop. You start recognizing early warning signs. But early on: follow up more than you think you need to.

---

## 📋 Delegation Framework

Not all tasks should be delegated the same way:

```
┌──────────────────────────────────────────────────────────┐
│              TASK FREQUENCY                              │
│                                                          │
│         FREQUENT              INFREQUENT                 │
│                                                          │
│ SIMPLE   Delegate             Do it yourself             │
│          (to tech leads)      (faster than explaining)   │
│                                                          │
│ COMPLEX  Delegate carefully   Use as training            │
│          (develop the team)   (for rising leaders)       │
└──────────────────────────────────────────────────────────┘

EXAMPLES:
  Simple + Frequent   → Daily standups, weekly status summaries
  Simple + Infrequent → Book a conference ticket, run a script
  Complex + Frequent  → Project planning, systems design, on-call
  Complex + Infrequent→ Performance reviews, hiring plans (train others on these)
```

**The long game:** If your teams can't operate without you, you can't be promoted. Develop people to do what only you know how to do.

---

## 🚨 Warning Signs to Watch For

Learn to detect trouble early. Classic signals:

```
SIGNAL 1: Sudden behavioral change
  Usually chatty person → quiet, leaves early, avoids chat
  = Personal issue OR preparing to quit
  → Have an honest 1-1 conversation ASAP

SIGNAL 2: Tech lead who hides
  Claims everything is fine, skips your 1-1s, vague updates
  = Probably hiding slow progress or scope creep
  → Ask for a project plan with milestones now

SIGNAL 3: Dead meetings
  Team sits silently while PM/TL talk for the whole meeting
  = Team isn't engaged or doesn't feel they have a say
  → Check whether they understand and own the goals

SIGNAL 4: Shifting priorities weekly
  Team's project list changes based on whoever asked last
  = No clear product direction; team is reactive not proactive
  → Work with product/business to set real quarterly goals

SIGNAL 5: Fragmented team identity
  Engineers know only their own system, no curiosity about others
  = Team is more loyal to their code than to the mission
  → Create cross-team learning and shared purpose
```

---

## 🗣️ Strategies for Saying No

At this level, saying no is a core competency — not a failure.

### "Yes, And" (for your boss)
```
Instead of: "No, we can't do that."
Say:        "Yes, we can do that — and here's what we'd need
             to delay or drop in order to make room for it."

This is improv comedy applied to leadership. It acknowledges
reality while staying positive and collaborative.
```

### Create a Policy (for repeated nos)
```
When you find yourself giving the same "no" repeatedly,
turn it into a documented policy:

"To adopt a new programming language, the team needs to:
  1. Identify 3 engineers who know it
  2. Document how we'd handle production support
  3. Establish logging/testing standards
  4. Get sign-off from the tech lead"

Now the "no" is a process, not a wall.
```

### "Help Me Say Yes" (for one-offs)
```
When an idea seems bad but you want to be fair:
  "Help me understand... what's the risk if this fails?"
  "How would we support this in production?"
  "What would we stop doing to make time for this?"

This line of questioning either helps them realize the flaw
themselves, or surprises you with a solid answer.
```

---

## 📊 Technical Health Signals

Move your technical focus from writing code to **observing and improving the system of work**:

```
HEALTH SIGNAL 1: Release Frequency
  → How often does code ship?
  → If not daily: WHY NOT?
  → Slow releases hide process pain, tool debt, and team friction

HEALTH SIGNAL 2: Code Check-in Frequency
  → Are engineers committing small chunks regularly?
  → Long-running branches = integration risk + hidden progress
  → Engineers who go silent for a week are usually struggling

HEALTH SIGNAL 3: Incident Frequency
  → How often do things break?
  → Is on-call burning people out?
  → Are you fixing causes or just symptoms?
  → Goal: engineers can do their best work EVERY DAY
```

---

## 💡 The Virtues of Laziness and Impatience

Larry Wall said laziness, impatience, and hubris are virtues of great programmers. They apply to great managers too — directed at **processes**, not people.

```
IMPATIENCE → Question whether things can be done faster
             by removing waste, not by asking people to work longer

LAZINESS   → Go home. Stop emailing at 11pm.
             When you overwork visibly, your team feels they must too.
             Forcing focus teaches the team to focus.

THE MATH:
  60-hour week to ship in 8 days ≠ working faster
  60-hour week = giving the company your free time

  REAL SPEED = same value, less total time.
  The way to get there is smarter process, not more hours.
```

---

## 💡 Key Takeaways

| # | Takeaway |
|---|---|
| 1 | **You are a multiplier now** — your output is your teams' output |
| 2 | **Prioritize important-but-not-urgent work** — it's what makes you strategic |
| 3 | **Delegation is your primary tool** — and it develops your people simultaneously |
| 4 | **Learn to read early warning signs** — prevention is cheaper than rescue |
| 5 | **"Yes, and" beats "no"** — frame constraints as tradeoffs, not walls |
| 6 | **Technical health signals are your dashboard** — release freq, check-in freq, incidents |
| 7 | **Go home** — your visible work habits set the culture for your entire org |

---

*← [Chapter 5 - Managing a Team](05-managing-a-team.md) | [Back to Index](../README.md) | Next: [Chapter 7 - Managing Managers](07-managing-managers.md) →*
