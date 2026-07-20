# Chapter 7 — SRP: The Single Responsibility Principle

> *"A module should be responsible to one, and only one, actor."*

---

## 🎯 Core Concept

SRP is **not** "a function should do one thing." That's a different rule. SRP says: a module should have **one reason to change**, meaning it serves **one actor** (a group of stakeholders).

---

## ⚠️ Symptom 1: Accidental Duplication

```
class Employee {
    calculatePay()   // ← CFO's team owns this
    reportHours()    // ← COO's team owns this
    save()           // ← CTO's team owns this
}
```

Both `calculatePay()` and `reportHours()` use a shared `regularHours()` helper.

**Problem:** CFO asks to change overtime calculation → developer updates `regularHours()` → COO's reports are now broken with wrong numbers. Three actors coupled in one class.

---

## ⚠️ Symptom 2: Merges

When two teams modify the same file for different reasons, merges conflict. The more actors touch a class, the more dangerous concurrent edits become.

---

## ✅ Solution: Separate by Actor

```
EmployeeData (plain data, no methods)
    ↑           ↑           ↑
PayCalculator  HourReporter  EmployeeSaver
(CFO actor)   (COO actor)   (CTO actor)
```

Or use a Facade to keep the old interface:

```
EmployeeFacade
  → delegates calculatePay() → PayCalculator
  → delegates reportHours()  → HourReporter
  → delegates save()         → EmployeeSaver
```

---

## 🔗 SRP at Different Levels

| Level | Principle |
|-------|-----------|
| Functions | Do one thing |
| Classes/Modules | SRP — one actor |
| Components | Common Closure Principle |
| Architecture | Axis of Change → Architectural Boundaries |

---

## 💡 Key Takeaways

- SRP = one reason to change = one actor (not one function)
- Coupling multiple actors in one class leads to accidental bugs and merge conflicts
- Separate code that changes for different reasons into different classes
- Use Facade pattern to present a unified interface over separated classes

---

*← [Back to Clean Architecture](../README.md)*
