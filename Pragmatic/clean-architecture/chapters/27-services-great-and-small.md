# Chapter 27 — Services: Great and Small

> *"Services, in and of themselves, do not define an architecture."*

---

## 🎯 Core Concept

Micro-services and SOA are popular, but they are **not automatically architecture**. The architecture is defined by boundaries and the Dependency Rule — not by the physical separation of processes.

---

## ❌ Two Fallacies About Services

### Fallacy 1: Services are strongly decoupled
Services are decoupled at the variable level, but they are **coupled by shared data**. If a new field is added to a shared record, every service that touches that field must change.

### Fallacy 2: Services support independent development/deployment
When a cross-cutting feature is added (like "kitty delivery" to a taxi app), **all services must change simultaneously** — there is no real independence.

---

## 🐱 The Kitty Problem

```
TaxiUI → TaxiFinder → TaxiSelector → TaxiDispatcher
```

Adding "kitten delivery" requires changes to **ALL services** — they were coupled by the business feature, not decoupled by process boundaries.

**The fix:** Design services with internal component architectures that follow the Dependency Rule:

```
TaxiService
├── Rides (component)
│   └── implements RideAbstractBase
└── Kittens (component)  ← new feature, no change to existing
    └── implements RideAbstractBase
```

---

## ✅ Component-Based Services

Services should be internally structured using SOLID principles:
- Each service = set of abstract classes in jar files
- New features = new jar files extending abstract classes
- Deploying a new feature = adding jar files, not redeploying services

---

## 💡 Key Takeaways

- Services are **expensive function calls** across process/network boundaries — not architecture by themselves
- Architectural boundaries run **through** services, not between them
- Cross-cutting concerns break service independence — design for it with internal component architecture
- A single service can be a full component, or contain multiple components separated by boundaries

---

*← [Back to Clean Architecture](../README.md)*
