# Chapter 15 — What Is Architecture?

> *"The goal of architecture is to minimize the human resources required to build and maintain the required system."*

---

## 🎯 Core Concept

Architecture is the **shape** given to a system — how it's divided into components, how those components are arranged, and how they communicate. Its purpose: support the **life cycle** of the system.

---

## 🏗️ What Architecture Supports

| Concern | What Good Architecture Does |
|---|---|
| **Development** | Makes the system easy to build by many teams independently |
| **Deployment** | Enables single-action deployment, no manual steps |
| **Operation** | Makes operational needs visible and understandable |
| **Maintenance** | Reduces spelunking and risk when adding features |

---

## 🔑 The Strategy: Leave Options Open

> *"The strategy is to leave as many options open as possible, for as long as possible."*

All software systems split into two elements:
- **Policy** — the business rules, the actual value
- **Details** — databases, web servers, frameworks, IO devices

The architect's job: make **policy** the center, treat **details as irrelevant** to that policy. This means decisions about details can be **deferred**.

### What You Don't Need to Decide Early
- Which database to use
- Which web framework to use
- Whether to use REST or micro-services
- Which dependency injection framework to use

**The longer you delay these decisions, the more information you have to make them correctly.**

---

## 📐 Architecture ≠ Framework

A software architect is still a **programmer**. Architects who stop coding lose touch with the problems they create for others.

The architecture of a system should make the **operation of the system apparent** — use cases, features, and behaviors should be first-class, visible entities.

---

## 💡 Key Takeaways

- Architecture is about **shape**: components, arrangements, communication
- Primary purpose: support the **life cycle** (development, deployment, operation, maintenance)
- Good architecture **minimizes human resources** needed to build and maintain
- Separate **policy** (what matters) from **details** (what doesn't, yet)
- A good architect maximizes the number of **decisions not made**

---

*← [Back to Clean Architecture](../README.md)*
