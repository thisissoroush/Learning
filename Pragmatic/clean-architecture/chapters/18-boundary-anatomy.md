# Chapter 18 — Boundary Anatomy

> *"The boundaries in a system will often be a mixture of local chatty boundaries and boundaries more concerned with latency."*

---

## 🎯 Core Concept

Boundaries come in different physical forms, each with different cost, speed, and overhead characteristics.

---

## 📦 Types of Boundaries

### 1. Monolith (Source-Level Decoupling)
- Single executable, single address space
- Communication: **function calls** (very fast, very cheap)
- Boundaries exist as disciplined code separation
- Dynamic polymorphism manages internal dependencies

### 2. Deployment Components (JAR/DLL/Shared Libraries)
- Dynamically linked at runtime
- Communication: still **function calls** (cheap)
- Physical separation at deployment, not at runtime

### 3. Local Processes
- Separate OS processes, same machine
- Communication: **sockets, mailboxes, message queues** (moderate cost)
- Be careful of excessive "chattiness"

### 4. Services
- Fully separate processes, possibly on different machines
- Communication: **network packets** (expensive, high latency)
- Latency: tens of milliseconds to seconds
- Minimize chatty communication across service boundaries

---

## 🔁 Boundary Crossing Direction

```
Low-level Client ──calls──> High-level Service    (no inversion needed)

High-level Client ──> [Interface] <── Low-level ServiceImpl  (DI inversion)
```

All source code dependencies must **point toward the higher-level component**, regardless of flow of control direction.

---

## 💡 Key Takeaways

| Boundary Type | Communication | Cost |
|---|---|---|
| Monolith | Function calls | Very low |
| Deployment | Function calls | Low |
| Local Process | IPC/Sockets | Medium |
| Service | Network | High |

- Choose boundary type based on **operational needs**, not fashion
- Most systems use **multiple boundary types**

---

*← [Back to Clean Architecture](../README.md)*
