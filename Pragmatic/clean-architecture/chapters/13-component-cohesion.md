# Chapter 13 — Component Cohesion

> *"Which classes belong in which components? Three principles guide this decision."*

---

## 🎯 Core Concept

Component cohesion answers: **which classes go together?** Three principles create a tension triangle — good architects find the right balance for their context.

---

## 🔺 The Three Principles

### REP — Reuse/Release Equivalence Principle
> *"The granule of reuse is the granule of release."*

Classes grouped into a component must be **releasable together** — same version, same release tracking, same changelog. If you can't release them as a coherent unit, they don't belong together.

### CCP — Common Closure Principle
> *"Gather into components those classes that change for the same reasons and at the same times."*

This is **SRP for components**. If a change touches many components, deployments multiply. If a change touches one component, deployment is simple. Group by axis of change.

### CRP — Common Reuse Principle
> *"Don't force users of a component to depend on things they don't need."*

This is **ISP for components**. When you depend on a component, you depend on ALL classes in it. Don't bundle unrelated classes together — every forced dependency is a liability.

---

## ⚖️ The Tension Triangle

```
         REP
        /   \
 Too many    Too many
 releases    changes per
 needed      release
      \     /
  CRP ──── CCP
```

| Focus on... | Risk |
|---|---|
| REP + CRP only | Too many components impacted by simple changes |
| CCP + REP only | Too many unnecessary releases |
| CCP + CRP only | Hard to reuse components |

---

## 📅 Evolution Over Time

- **Early project**: CCP dominates — developability matters more than reusability
- **Mature project**: REP and CRP gain importance as external consumers appear
- The triangle position shifts as the project matures

---

## 💡 Key Takeaways

- REP: group things that are released together
- CCP: group things that change together (minimize deployment blast radius)
- CRP: don't bundle things that aren't used together (minimize unnecessary coupling)
- Balance all three — the right position depends on your team and stage

---

*← [Back to Clean Architecture](../README.md)*
