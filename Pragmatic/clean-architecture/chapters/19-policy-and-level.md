# Chapter 19 — Policy and Level

> *"In a good architecture, the direction of dependencies is based on the level of the components they connect."*

---

## 🎯 Core Concept

Every policy in a software system can be ranked by **level**: its distance from the inputs and outputs. Higher-level policies change less often and for more important reasons.

---

## 📏 What Is "Level"?

**Level = distance from inputs and outputs.**

- Policies closest to IO (reading input, writing output) = **low level**
- Policies at the center of transformation = **high level**

### Example: Encryption Program

```
[Input Device] → [Read Chars] → [Translate/Encrypt] → [Write Chars] → [Output Device]
```

- `Translate` is the **highest-level** component (farthest from IO)
- `ReadChar` / `WriteChar` are **lowest-level** (directly touch IO)

**Wrong architecture:**
```java
function encrypt() {
  while(true) writeChar(translate(readChar()));
}
// encrypt() depends on low-level I/O — bad!
```

**Right architecture:**
```
Encrypt ──uses──> CharReader (interface)
Encrypt ──uses──> CharWriter (interface)
         ▲
ConsoleReader implements CharReader
ConsoleWriter implements CharWriter
```
Dependencies point **inward toward higher-level** policies.

---

## 📐 Why This Matters

| Level | Changes | Reason |
|---|---|---|
| High (business logic) | Rarely | Strategic decisions |
| Low (IO, UI, DB) | Frequently | Technical or user preference |

Low-level components **plug in** to high-level ones. Trivial changes at the bottom have **no impact** at the top.

---

## 💡 Key Takeaways

- Group policies by level: same-level policies change together
- Source code dependencies must point **toward higher-level policies**
- Low-level components are **plugins** to high-level components
- This principle is the heart of the Dependency Rule

---

*← [Back to Clean Architecture](../README.md)*
