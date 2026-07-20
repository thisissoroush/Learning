# Chapter 9 — LSP: The Liskov Substitution Principle

> *"If S is a subtype of T, then objects of type T may be replaced with objects of type S without altering the correctness of the program."*

---

## 🎯 Core Concept

Subtypes must be **substitutable** for their base types. If your code expects a `Shape`, you should be able to pass a `Circle` or `Square` and have it behave correctly — without special-casing.

---

## ✅ Good Example: License

```
Billing ──uses──► License (calcFee())
                    ▲         ▲
             PersonalLicense  BusinessLicense
```

`Billing` doesn't care which subtype it uses. Both are freely substitutable. ✅

---

## ❌ Bad Example: Square/Rectangle

```java
Rectangle r = new Square();
r.setW(5);
r.setH(2);
assert(r.area() == 10); // FAILS! Square sets both W and H to 2
```

`Square` violates LSP because it changes the behavior contract of `Rectangle`. Now callers need `if (shape instanceof Square)` checks — that's the smell.

---

## 🌐 LSP at Architecture Level

LSP applies beyond inheritance — to **REST APIs, services, and interfaces** too.

**Example:** Taxi dispatch system — all drivers share the same REST endpoint format:
```
/pickupAddress/{addr}/pickupTime/{time}/destination/{dest}
```

One vendor uses `dest` instead of `destination`. Now you need special-case code:
```java
if (driver.getUri().startsWith("acme.com")) {
    // different format
}
```

This is an **LSP violation at the architectural level** — the service is not substitutable. The fix requires a configuration-driven dispatch module.

---

## 💡 Key Takeaways

- LSP violations force `if-instanceof` checks, polluting callers with type knowledge
- Apply LSP to interfaces, services, and REST APIs — not just class hierarchies
- A simple substitutability violation can corrupt an entire system's architecture
- The test: can you swap implementations without changing caller behavior?

---

*← [Back to Clean Architecture](../README.md)*
