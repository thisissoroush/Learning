# Chapter 13 — Refactoring to Microservices

> *"The goal is to incrementally transform the monolith into a set of microservices using the Strangler application pattern."*

---

## 🎯 Core Concept

You rarely migrate a monolith to microservices all at once — it's too risky. Instead, you **strangle the monolith** incrementally: new features become services, and existing functionality is extracted one piece at a time. The monolith shrinks while the microservices ecosystem grows.

---

## ❓ Why Refactor a Monolith?

```
Signs you need to refactor:
  ✗ Development is slow — changes take weeks to release
  ✗ Scaling is painful — can't scale one component independently  
  ✗ Technology stack is obsolete and hard to upgrade
  ✗ Large team coordination overhead
  ✗ Deployments are risky and infrequent
  ✗ Testing takes forever — no confidence
```

**When NOT to refactor**: If the monolith works well and you're not experiencing these problems, don't migrate just because it's fashionable.

---

## 🌿 Pattern: Strangler Application

Named after the strangler fig tree — a plant that grows around a tree and eventually replaces it.

```
Phase 1: Monolith handles everything
  ┌─────────────────────────────┐
  │         Monolith            │
  │  Order | Restaurant | User  │
  └─────────────────────────────┘

Phase 2: Extract services incrementally
  ┌──────────────────┐    ┌──────────────────┐
  │     Monolith     │    │  Delivery Service │
  │  Order |  User   │    │  (new service)    │
  │  Restaurant      │    └──────────────────┘
  └──────────────────┘

Phase 3: Monolith shrinks
  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │  Order   │  │Restaurant│  │  User    │  │Delivery  │
  │ Service  │  │ Service  │  │ Service  │  │ Service  │
  └──────────┘  └──────────┘  └──────────┘  └──────────┘
```

---

## 🛠️ Strategy 1: Implement New Features as Services

The safest strategy: **never add to the monolith again**.

```
New requirement: "Notify customers when order is delayed"

❌ Old way: Add to the monolith
✅ New way: Create Delayed Delivery Service

Delayed Delivery Service:
  - Subscribes to order events from monolith
  - Tracks delays independently
  - Sends notifications via Notification Service
  - No changes to monolith codebase!
```

**Integration Glue**: How does the new service communicate with the monolith?
- REST API calls from service to monolith
- Events published by monolith (add event publishing incrementally)
- Shared database (temporary — avoid long-term)

---

## 🎨 Strategy 2: Separate the Presentation Layer

Decouple the frontend from the backend first — often the quickest win.

```
Before:
  Browser → Monolith (HTML + Business Logic + Data)

After:
  Browser → Frontend App (React/Angular SPA)
              ↓
         API Gateway
              ↓
         Monolith (now just a backend API)

Impact: Decouples UI development. Teams can move independently.
No business logic extracted yet, but deployment is now separate.
```

---

## ⛏️ Strategy 3: Extract Business Capabilities into Services

The hardest but most valuable strategy — extracting existing monolith modules.

```
Example: Extracting Delivery Management

1. Identify domain: Delivery (couriers, routes, status updates)

2. Design domain model for Delivery Service:
   - Delivery entity
   - Courier entity  
   - separate DB schema

3. Build the Delivery Service with its own DB

4. Create integration glue:
   - API for monolith to call Delivery Service
   - Events for Delivery Service to subscribe to

5. Redirect traffic from monolith to Delivery Service

6. Remove delivery code from monolith
```

---

## 🔗 Integration Glue Patterns

When service and monolith must collaborate:

### Anti-Corruption Layer (ACL)
```
Monolith uses "OrderStatus: 1, 2, 3"  (integer codes)
Service uses "OrderStatus: PENDING, APPROVED, REJECTED"

ACL translates between the two models:
  Service → ACL → Monolith
  
Prevents monolith's messy model from corrupting the new service's clean model
```

### Data Consistency Across Service + Monolith
```
Problem: Service has its DB, monolith has its DB
         They both need consistent data

Solution: Saga spans both
  Step 1: Monolith updates order status
  Step 2: Service updates delivery record
  (coordinated via messaging/events)
```

---

## 📊 Migration Roadmap

```
Month 1-2:  Set up infrastructure (Docker, Kubernetes, message broker)
            Implement microservice chassis
            Extract first simple service (lowest risk)

Month 3-6:  Implement new features as services only
            Extract 2-3 more services
            Build deployment pipeline

Month 6-12: Extract core domain services (Order, Restaurant, etc.)
            Monolith shrinks significantly

Month 12+:  Monolith is retired or becomes a thin legacy adapter
```

---

## 💡 Key Takeaways

| Insight | Implication |
|---------|-------------|
| Don't big-bang rewrite the monolith | Use the Strangler pattern — incremental is safer |
| Stop adding to the monolith | All new features go in new services |
| Extract services one at a time | Start with lowest-risk, highest-value candidates |
| Anti-corruption layer protects service integrity | Don't let monolith's legacy model pollute new services |
| Data consistency across boundaries is hard | Use sagas even when one participant is the monolith |
| The journey takes months to years | Plan for it; track progress; celebrate milestones |

---

*← [Back to Microservices Patterns](../README.md)*
