# Chapter 31 — The Web Is a Detail

> *"The web is just the latest in a series of oscillations that our industry has gone through since the 1960s."*

---

## 🎯 Core Concept

The web is a **delivery mechanism** — an IO device. It is not an architecture. Your business logic should be completely unaware of whether it is delivered via web, console, desktop, or API.

---

## 🔄 The Endless Pendulum

Computing power has been swinging between central and distributed since the 1960s:

```
Mainframes → Terminals → Client-Server → Web (thin) → Applets → 
Server-side → Ajax/SPA → Node.js → ... → (keeps swinging)
```

Each swing is a **detail**. Your core business logic should survive all of them.

---

## 🏗️ The Right Mental Model

```
❌ Wrong: "My app is a web app"
✅ Right: "My app delivers value; the web is one delivery mechanism"

Business Rules ──→ Use Cases ──→ [Web | Console | Mobile | API]
                                        ↑
                                   (just a plugin)
```

---

## 💡 Real-World Example

> Company Q changed its personal finance desktop app to "look like a browser" when the web became popular. Users hated it. They had to revert. If the business rules had been properly decoupled from the UI, this would have been a cosmetic swap, not a crisis.

---

## 💡 Key Takeaways

- The web is an IO device — treat it the way UNIX treated device independence
- Business rules should be ignorant of how they are delivered
- UI oscillations (web, mobile, desktop) are business decisions, not architectural ones
- Decouple use cases from the delivery mechanism so you can swap UIs cheaply
- The only way to survive marketing geniuses is proper decoupling

---

*← [Back to Clean Architecture](../README.md)*
