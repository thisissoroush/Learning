# Chapter 12 — Components

> *"Components are the units of deployment — the smallest entities that can be independently deployed."*

---

## 🎯 Core Concept

A **component** is the granule of deployment. In Java: `.jar` files. In .NET: `.dll` files. In Ruby: `.gem` files. Well-designed components are always **independently deployable** and therefore **independently developable**.

---

## 📜 A Brief History

| Era | Approach | Problem |
|---|---|---|
| 1950s-60s | Source code compiled at fixed memory addresses | Programs couldn't relocate; libraries hard-coded |
| 1960s-70s | Relocatable binaries + linking loaders | Slow link times as programs grew |
| 1980s | Separate linker phase | Link times grew to hours |
| 1990s+ | Moore's Law won; fast disks + RAM | Dynamic linking feasible again |

The evolution of components mirrors the evolution of deployment strategies — from static linking to dynamic plugins.

---

## 🔌 Plugin Architecture

Today we ship `.jar` files, `.dll` files, and shared libraries as **plugins** to existing applications. This casual default was a heroic feat 30 years ago.

```
Application ──loads──► ComponentA.jar
            ──loads──► ComponentB.dll
            ──loads──► FeatureX.gem
```

The lesson: **components should be independently replaceable plugins**, not tightly coupled blobs.

---

## 💡 Key Takeaways

- Components = units of deployment (jar, dll, gem, shared lib)
- Well-designed components retain independent deployability regardless of how they're bundled
- The plugin architecture we use today took 50 years of evolution to become easy
- Component boundaries are the building blocks of architecture

---

*← [Back to Clean Architecture](../README.md)*
