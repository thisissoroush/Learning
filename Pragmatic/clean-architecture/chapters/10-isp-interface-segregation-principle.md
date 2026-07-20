# Chapter 10 — ISP: The Interface Segregation Principle

> *"Don't depend on things you don't need."*

---

## 🎯 Core Concept

Don't force users of a module to depend on methods they don't use. Fat interfaces create unnecessary coupling — a change to an unused method still forces recompilation and redeployment of all users.

---

## 🔬 The Problem

```
User1 ──► OPS (op1, op2, op3) ◄── User2
                     ◄── User3
```

`User1` only uses `op1`, but it depends on the entire `OPS` class. A change to `op2` forces `User1` to recompile and redeploy — even though `User1` doesn't care about `op2`.

---

## ✅ The Solution: Segregate Interfaces

```
User1 ──► U1Ops (op1)  ┐
User2 ──► U2Ops (op2)  ├── OPS implements all
User3 ──► U3Ops (op3)  ┘
```

Now `User1` only depends on `U1Ops`. Changes to `op2` or `op3` are invisible to `User1`.

---

## 🏗️ ISP at Architectural Level

The ISP isn't just about code — it's about **architectural dependencies**.

**Example:**
```
System S ──depends──► Framework F ──depends──► Database D
```

If `D` has features that `F` doesn't use, and those features change or break, `F` and `S` are forced to redeploy. You took on baggage you didn't need.

> ⚠️ Depending on something that carries baggage you don't need can cause unexpected failures.

---

## 📊 Static vs. Dynamic Languages

| Language Type | ISP Impact |
|---|---|
| Java, C# (static) | Source-level imports force recompilation |
| Ruby, Python (dynamic) | Inferred at runtime — less forced coupling |

Dynamic languages are naturally more flexible here, but ISP thinking still matters architecturally.

---

## 💡 Key Takeaways

- Fat interfaces create hidden coupling between unrelated users
- Segregate interfaces so each user depends only on what it uses
- At architectural scale: avoid depending on frameworks/modules that carry unneeded baggage
- Lean on small, focused interfaces — a change should only affect those who care

---

*← [Back to Clean Architecture](../README.md)*
