# Chapter 8 — Reuse Patterns

> *"Code reuse sounds great in theory. In distributed systems, it creates hidden coupling."*

---

## 🎯 Core Concept

In distributed architectures, **code reuse creates coupling**. Every time a service depends on shared code, a change in that code can ripple through multiple services, defeating the independence that microservices promise. There are four patterns for handling shared code — each with distinct trade-offs.

---

## 🔁 Pattern 1: Code Replication

**Idea:** Copy the shared code into each service that needs it.

```
Service A         Service B         Service C
────────          ────────          ────────
validation.go     validation.go     validation.go
(identical copy)  (identical copy)  (identical copy)
```

**Benefits:**
- Zero coupling between services
- Each service can evolve its copy independently
- No deployment coordination needed

**Shortcomings:**
- Bug fixes must be applied to N copies
- Easy for copies to drift apart (inconsistency)

**When to use:**
- Simple, stable utility code (formatters, converters)
- When the code is unlikely to change
- When the overhead of a shared library is not justified

---

## 📦 Pattern 2: Shared Library

**Idea:** Package shared code into a versioned library (JAR, DLL, GEM) bound at compile time.

```
        ┌──────────────────────────────────┐
        │        shared-utils.jar v2.3     │
        └──────────────────────────────────┘
                 ▲          ▲          ▲
           Service A   Service B   Service C
```

### Dependency Management Challenges

```
shared-utils.jar v2.3 released (breaking change)

Service A: Updated to v2.3 ✓ (deployed)
Service B: Still on v2.0   ✗ (compatibility issues)
Service C: Not updated yet  (forgot!)

→ Services now on different library versions → behavior inconsistency
```

### Versioning Strategies

```
Strategy 1: Version Deprecation
  - Release v2.0, keep v1.x alive
  - Set sunset date for v1.x
  - Services migrate at their own pace
  - Con: Maintain two versions simultaneously

Strategy 2: Communicate Breaking Changes Early
  - Alert all teams before breaking changes
  - Coordinate deployment windows
  - Con: Requires team coordination overhead

Strategy 3: Semantic Versioning
  MAJOR.MINOR.PATCH
  Major = breaking change → services must update
  Minor = new features, backward compatible
  Patch = bug fixes, backward compatible
```

**When to use:**
- Shared utility/infrastructure code (logging, security, metrics)
- Code that changes infrequently
- When all services using the library share the same deployment cadence (rare)

---

## 🌐 Pattern 3: Shared Service

**Idea:** Extract shared logic into a standalone service. All other services call it at runtime.

```
Service A ──────▶ ┌─────────────────────┐
Service B ──────▶ │  Notification Service│
Service C ──────▶ └─────────────────────┘
                          │
                  sends SMS, Email, etc.
```

### Trade-Offs

**Change Risk:**
```
Bug in Notification Service logic
→ ALL callers affected simultaneously ✗

With shared library:
→ Only services using that version affected
→ Others unaffected (different version)
```

**Performance:**
```
Shared Library:  in-process call → nanoseconds
Shared Service:  network call → 50-300ms + retry logic + circuit breaker
```

**Scalability:**
```
Shared Service scales independently ✓
→ As demand grows, scale only the shared service
→ Shared Library scales with each service instance
```

**Fault Tolerance:**
```
Shared Service down → ALL callers fail ✗
Shared Library bug → only deployed services with that bug affected
```

**When to use:**
- Functionality that must be centrally controlled (audit logging, compliance)
- Domain logic that MUST stay consistent across services
- Functionality that changes frequently and all consumers must get instantly

---

## 🚗 Pattern 4: Sidecars and Service Mesh

**Idea:** Infrastructure concerns (logging, monitoring, circuit breakers, service discovery) are handled by a sidecar process co-deployed with each service.

```
  ┌────────────────────────────────────┐
  │  Pod / Container Group             │
  │  ┌──────────────┐ ┌─────────────┐ │
  │  │  My Service  │ │   Sidecar   │ │
  │  │  (business   │ │  (logging,  │ │
  │  │   logic)     │ │  metrics,   │ │
  │  │              │ │  auth, etc) │ │
  │  └──────────────┘ └─────────────┘ │
  └────────────────────────────────────┘
```

**Service Mesh** (e.g., Istio, Linkerd): Coordinates sidecars across all services, providing:
- Mutual TLS between services
- Distributed tracing
- Traffic control and canary releases
- Observability without code changes

**When to use:**
- Infrastructure/cross-cutting concerns (not domain logic)
- Polyglot environments (sidecars work regardless of language)
- When you need consistency across all services without code changes

---

## ⚖️ Comparison Summary

| Pattern | Coupling | Change Risk | Performance | Scalability | When To Use |
|---------|----------|-------------|-------------|-------------|-------------|
| Code Replication | None | Low (isolated) | Best | N/A | Simple, stable utilities |
| Shared Library | Compile-time | Medium | Very Good | With each service | Infrastructure, utilities |
| Shared Service | Runtime | High | Worst | Independent | Central domain logic, compliance |
| Sidecar | None (infra) | Low | Good | Independent | Cross-cutting infrastructure |

---

## 🏢 Sysops Squad Saga: Two Reuse Decisions

### Infrastructure Code (Logging, Metrics, Security)
**Decision: Sidecar + Service Mesh**
- All services need consistent observability
- Language-agnostic
- No coordination overhead for updates

### Common Notification Logic
**Decision: Shared Service**
- Notification rules must be consistent (all services must send same way)
- Changes must take effect immediately for all callers
- The notification service scales independently from callers

---

## 💡 Key Takeaways

| Insight | Implication |
|---------|-------------|
| Shared code = shared coupling | Every dependency is a trade-off — be intentional |
| Infrastructure code ≠ domain code | Use libraries/sidecars for infra, shared service for domain |
| Shared service creates runtime coupling | A shared service going down = all callers fail |
| Versioning strategies matter | Plan how you'll handle breaking changes before releasing shared libraries |
| Reuse platforms (service mesh) eliminate most infra sharing problems | Prefer infrastructure reuse via sidecar, not code duplication |

---

*← [Back to Software Architecture: The Hard Parts](../README.md)*
