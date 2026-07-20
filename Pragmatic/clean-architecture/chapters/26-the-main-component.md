# Chapter 26 — The Main Component

> *"Think of Main as a plugin to the application."*

---

## 🎯 Core Concept

Every system needs one component that **bootstraps everything**: creates factories, loads configuration, injects dependencies, then hands control to the high-level system. This is `Main`.

---

## 🔌 Main as the Dirtiest Plugin

```
┌─────────────────────────────────┐
│           Application           │
│  (High-level policies & rules)  │
└────────────────▲────────────────┘
                 │ hands control to
┌────────────────┴────────────────┐
│              Main               │  ← outermost circle
│  - Creates factories            │
│  - Injects dependencies         │
│  - Loads configuration          │
│  - Starts the system            │
└─────────────────────────────────┘
```

- `Main` is the **lowest-level** component — the outermost circle in Clean Architecture
- It knows about everything; nothing knows about it
- It's the entry point the OS calls

---

## 🌍 Multiple Main Components

You can have many `Main` plugins for different contexts:

| Main Component | Purpose |
|----------------|---------|
| `MainDev` | Development config, test data |
| `MainTest` | Test doubles, mock databases |
| `MainProd` | Real services, production config |
| `MainUS` | US-specific configuration |
| `MainEU` | EU-specific configuration |

Each is just a different plugin — swap them without touching core logic.

---

## 💡 Key Takeaways

- `Main` is a **plugin** — dirty, detail-laden, but isolated
- Dependency injection frameworks live in `Main` — not in your business objects
- Treat `Main` as a configuration boundary: change deployment behavior by changing Main
- The rest of the system remains clean and unaware of Main's details

---

*← [Back to Clean Architecture](../README.md)*
