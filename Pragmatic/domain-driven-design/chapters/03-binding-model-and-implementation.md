# Chapter 3 — Binding Model and Implementation

> *"If the design, or some central part of it, does not map to the domain model, that model is of little value, and the correctness of the software is suspect."*

---

## 🎯 Core Concept

**Model-Driven Design (MDD)** demands one thing above all: the code must directly reflect the domain model. There is no separate "analysis model" and "design model" — they are the same model. When you change the code, you change the model. When you evolve the model, the code must follow.

---

## ❌ When Model and Code Diverge

Evans describes two real projects that failed in the same way despite opposite processes:

**Project A:** Started with a rich, elaborate domain model from months of analysis. When developers tried to implement it, they found it didn't translate to workable code. So they abandoned the model and wrote ad hoc code. The model became decoration.

**Project B:** No modeling at all. Code was hacked together feature by feature. The result was bloated, unmaintainable, and opaque — just like Project A.

**The common failure:** In both cases, the code did not reflect any coherent domain model.

---

## ✅ Model-Driven Design

```
ANALYSIS MODEL (broken):
  Analysts build model ──► Developers build code ──► They don't match
  (model dies in the handoff)

MODEL-DRIVEN DESIGN (working):
  ┌───────────────────────────────────────┐
  │            Single Model               │
  │                                       │
  │  serves both analysis AND design      │
  │  lives in code AND conversations      │
  │  evolves through iteration            │
  └───────────────────────────────────────┘
```

**The rule:** Design a portion of the software to reflect the domain model in a **very literal** way. The mapping must be obvious. A developer reading the code should be able to see the model.

---

## 🔧 PCB Example: Procedural vs. Model-Driven

**The problem:** PCB engineers need to assign layout rules to groups of nets (wires) called "buses." The layout tool doesn't support the bus concept, so engineers wrote file-parsing scripts.

**Procedural scripts (before):**
```python
# 1. Sort net list by net name
# 2. Read each line, find bus name pattern
# 3. For each matching name, parse the net name
# 4. Append net name with rule to rules file
# 5. Repeat until bus name no longer matches
```

These scripts work, but they don't capture the **concept** of a bus. Every new requirement means a new script. Different file formats require starting over.

**Model-Driven Design (after):**

```
          ┌──────────────┐
          │  AbstractNet  │
          │  + assignRule()│
          │  + assignedRules()│
          └──────┬────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
    ┌───────┐         ┌───────┐
    │  Net  │────────▶│  Bus  │
    │       │  0..1   │       │
    └───────┘         └───────┘
```

```java
// Net inherits rules from its Bus:
class Net extends AbstractNet {
    private Bus bus;

    Set assignedRules() {
        Set result = new HashSet();
        result.addAll(super.assignedRules());
        result.addAll(bus.assignedRules());
        return result;
    }
}
```

Now the **concept of bus** is explicit in the model and in the code. New requirements fit naturally. Tests are simple. File format changes only affect import/export services — not the core model.

---

## 👁️ Letting the Bones Show

When a design is based on a model that reflects the domain's real concerns, **users benefit too**. The model's structure shows through the UI.

**Counterexample:** Internet Explorer "Favorites" are actually files on the filesystem. But IE shows a UI pretending they're a special "favorites collection." When a user tries to save a page with `:` in the title, they get a confusing error about illegal filename characters. The mismatch between the user-facing model and the underlying model causes confusion.

**The principle:** Don't create an illusion of a model different from the underlying one — unless the illusion is perfect. Better to expose the real model and let users leverage their existing knowledge.

---

## 🤝 Hands-On Modelers

A common org-chart mistake: separate "architects/modelers" from "developers." The modelers design the abstraction, the developers implement it.

**Why this fails:**
1. **Intent is lost in handoff** — subtle model choices don't survive a document
2. **Feedback is delayed** — modelers don't learn about implementation problems until months later
3. **Developers become code monkeys** — they can't improve the model when they don't own it

**The rule:** Any technical person contributing to the model must spend time touching the code. Any developer changing code must understand how the model works.

```
❌ WRONG: Modeler ──design──► Developer ──code──► System
                   (one-way, no feedback)

✓ RIGHT:  Modeler = Developer (or tight collaboration)
          Everyone both models AND codes
          Changes flow in both directions
```

---

## 💡 Key Takeaways

| Insight | Implication |
|---------|-------------|
| There is only one model, not analysis + design | Never let model and code diverge |
| Literal mapping between model and code is essential | Class names, methods, and relationships must echo the domain |
| Developers must understand and own the model | Separate architects and developers kills MODEL-DRIVEN DESIGN |
| The model should guide implementation choices | When the model is hard to implement, fix the model |
| Users are also served by a coherent model | Don't create illusions — expose the real model |

---

*← [Back to Domain-Driven Design](../README.md)*
