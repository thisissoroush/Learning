# Chapter 29 — Clean Embedded Architecture

> *"Although software does not wear out, it can be destroyed from within by unmanaged dependencies on firmware and hardware."*

---

## 🎯 Core Concept

Embedded software that is tightly coupled to hardware becomes **firmware** — brittle, hard to test, and impossible to evolve. Clean architecture applies to embedded systems too.

---

## 📐 The Three Layers

```
┌─────────────────────┐
│      Software       │  ← business logic, long useful life
├─────────────────────┤
│   HAL / OSAL        │  ← abstraction layers
├─────────────────────┤
│  Firmware/Hardware  │  ← will change, will become obsolete
└─────────────────────┘
```

---

## 🔑 Key Abstractions

| Layer | Purpose |
|-------|---------|
| **HAL** (Hardware Abstraction Layer) | Hides GPIO, timers, flash from software |
| **PAL** (Processor Abstraction Layer) | Hides processor-specific C extensions |
| **OSAL** (OS Abstraction Layer) | Hides RTOS details from application code |

**Example:**
```c
// ❌ Firmware: tied to hardware
Led_TurnOn(5);           // GPIO bit 5

// ✅ Software: expresses intent
Indicate_LowBattery();   // what, not how
```

---

## 🧪 The Target-Hardware Bottleneck

If you can only test on target hardware, every test cycle is slow and risky. A clean embedded architecture allows **off-target testing**:

```
✅ Run business logic tests on your laptop
✅ Mock HAL for unit tests
✅ Only hardware-specific code needs target
```

---

## 💡 Key Takeaways

- Hardware changes — don't let it infect your business logic
- HAL, PAL, and OSAL are your shields against hardware coupling
- A clean embedded architecture is testable off the target
- "Make it work" is not enough — structure it for a long useful life
- Firmware engineers write firmware; software engineers write software — know the difference

---

*← [Back to Clean Architecture](../README.md)*
