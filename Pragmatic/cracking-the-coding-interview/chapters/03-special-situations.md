# Chapter III — Special Situations

> *"The same rules apply, but the context and expectations shift depending on who you are and what you're interviewing for."*  
> — Gayle Laakmann McDowell

---

## 🎯 Core Concept

Not every candidate is a fresh CS graduate applying for a generic SWE role. CTCI dedicates a full chapter to how the process changes for **experienced engineers, testers, PMs, startup candidates, and bootcamp graduates**. Knowing your context lets you set the right expectations and tailor your preparation.

---

## 👔 Experienced Candidates

The most common misconception: *"I've been coding for 10 years, I shouldn't have to do LeetCode."*

```
WHAT CHANGES FOR EXPERIENCED ENGINEERS
──────────────────────────────────────────────────────────
  ✅ SAME: Algorithm and data structure questions
  ✅ SAME: Coding on a whiteboard or shared editor
  ✅ SAME: Big O analysis expectations

  ➕ ADDED: System design rounds (almost always)
  ➕ ADDED: Leadership / influence questions
  ➕ ADDED: Architectural trade-off discussions
  ➕ ADDED: Deeper behavioral (conflict, decisions made)

  📊 Higher bar: You're expected to arrive at
     correct solutions faster. Less hand-holding.
──────────────────────────────────────────────────────────
```

**System design is now mandatory:**
- For senior roles, expect 1–2 full system design rounds
- Chapters IX and XVI of this book cover this in depth
- Design questions like: "Design Twitter", "Design a URL shortener"

---

## 🧪 Testers / SDETs (Software Development Engineers in Test)

```
TESTER INTERVIEW FOCUS
──────────────────────────────────────────────────────────
  ① Coding (lighter than SWE)
      → Can write correct programs in a language
      → Debugging ability valued

  ② Test case design (HEAVY FOCUS)
      → How would you test a pen?
      → How would you test Google Maps?
      → How would you test a login form?

  ③ Test automation
      → Frameworks, scripting, CI/CD awareness

  MIND SHIFT: Testers think about BREAKING things,
              not building them. This is the skill.
──────────────────────────────────────────────────────────
```

**Example Test Case Design Approach (for "Test a Chair"):**

```
Step 1: Who uses it?
        → Office workers, children, elderly, people with disabilities

Step 2: What are the normal uses?
        → Sitting for long periods, reclining, rolling

Step 3: What could go wrong?
        → Structural failure under weight, wheel locks up,
          armrest breaks, gas cylinder leaks

Step 4: Define test categories:
        → Functional: Does it sit? Does it roll?
        → Load: Max weight capacity
        → Durability: 10,000 sit/stand cycles
        → Safety: Tip-over angle, sharp edges
        → Ergonomics: Posture support, adjustability
```

---

## 📋 Product Managers (PMs)

PMs at technical companies (Google, Facebook) do NOT code in interviews. But they interview heavily on:

```
PM INTERVIEW DIMENSIONS
──────────────────────────────────────────────────────────
  ① Customer obsession
      → "Walk me through how you'd improve Gmail"

  ② Prioritization and trade-offs
      → "You have 3 features and 2 engineers. What ships?"

  ③ Metrics and success definition
      → "How do you know if this feature succeeded?"

  ④ Cross-functional collaboration
      → "How do you work with engineering? With design?"

  ⑤ Analytical / estimation
      → "How many search queries does Google get per day?"
──────────────────────────────────────────────────────────
```

---

## 🚀 Startup Candidates

Startups optimize for **fit and immediate impact**, not process.

```
STARTUP INTERVIEWS DIFFER BECAUSE:
──────────────────────────────────────────────────────────
  Speed:    Often 1–2 rounds, not 5+
  Focus:    "Can you build this feature we need?"
            → May give you a real problem they face
  Culture:  Hustle, autonomy, wearing many hats
  Risk:     You're evaluating THEM as much as they are you
            → Check: funding runway, team, product traction

  Questions to ask a startup:
  → What's the hardest technical challenge right now?
  → What's the current runway?
  → How does the team make technical decisions?
──────────────────────────────────────────────────────────
```

---

## 🎓 Bootcamp / Non-Traditional Candidates

If you didn't get a CS degree, the honest reality:

```
WHAT HIRING MANAGERS THINK (and how to overcome it):
──────────────────────────────────────────────────────────
  Concern:  "Do they have the CS fundamentals?"
  Answer:   Prove it directly. Know Big O cold.
            Know trees, graphs, recursion deeply.

  Concern:  "Can they handle our codebase?"
  Answer:   Show GitHub projects with real complexity.
            Open source contributions carry weight.

  Concern:  "Will they grow?"
  Answer:   Learning trajectory > starting point.
            Show what you've built on your own.
──────────────────────────────────────────────────────────
```

---

## 💡 Key Takeaways

| Situation | Key Difference | Prep Focus |
|-----------|---------------|------------|
| Experienced SWE | System design is mandatory | Design at scale, architectural trade-offs |
| SDET / Tester | Test case design is the skill | How to test anything, edge cases, automation |
| PM | No coding; product thinking | Metrics, prioritization, customer obsession |
| Startup | Culture fit + immediate value | Real projects, adaptability, hustle stories |
| Bootcamp grad | CS fundamentals skepticism | Big O, data structures, GitHub portfolio |

---

*[← Chapter II](02-behind-the-scenes.md) | [Back to Index](../README.md) | [Chapter IV →](04-before-the-interview.md)*
