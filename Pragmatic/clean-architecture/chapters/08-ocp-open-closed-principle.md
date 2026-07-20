# Chapter 8 — OCP: The Open-Closed Principle

> *"A software artifact should be open for extension but closed for modification."*

---

## 🎯 Core Concept

You should be able to add new behavior by **adding new code**, not by **changing existing code**. This is the most fundamental reason we study software architecture.

---

## 🔬 Thought Experiment

**Scenario:** Financial summary displayed on a web page (scrollable, red negatives). Stakeholders now want a black-and-white printed report (paginated, negatives in parentheses).

**Bad approach:** Modify existing code everywhere.  
**Good approach:** Separate concerns so zero existing code changes.

---

## 🏗️ OCP at Architectural Scale

Apply **SRP** first (separate calculation from presentation), then apply **DIP** to control dependency direction:

```
Database ──► Interactor ◄── Controller
                 ▲
             Presenters
                 ▲
              Views
```

**Arrows point toward higher-level components.** The Interactor (business rules) is protected from ALL changes — to the DB, Controller, Presenters, and Views. Higher-level = more protected.

---

## 🛡️ Protection Hierarchy

```
Most protected:   Interactor (business rules)
                  ↑
                  Controller
                  ↑
                  Presenters
Least protected:  Views (UI details)
```

Changes at the bottom never ripple up. New features = new components at the bottom.

---

## 💡 Key Takeaways

- OCP = extend behavior by adding code, not modifying existing code
- Partition system into components; arrange them in a dependency hierarchy
- Higher-level components are protected from lower-level changes
- This is achieved by combining SRP (what changes) + DIP (direction of dependencies)

---

*← [Back to Clean Architecture](../README.md)*
