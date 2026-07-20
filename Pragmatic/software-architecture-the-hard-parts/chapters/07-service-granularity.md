# Chapter 7 — Service Granularity

> *"Micro means small, but how small is too small?"*

---

## 🎯 Core Concept

**Granularity** is about the *size* of a service — what it does. This is different from **modularity** (breaking things apart). Most distributed architecture problems are granularity problems, not modularity problems.

Getting granularity right requires **removing opinion** and applying two opposing force categories:
- **Granularity Disintegrators** → when to break a service apart
- **Granularity Integrators** → when to keep services together (or merge them)

---

## ⚡ Granularity Disintegrators (Reasons to Split)

### 1. Service Scope and Function (Cohesion)

Weak cohesion → split. Strong cohesion → keep together.

```
Strong cohesion (DON'T split just because):
  Notification Service → SMS, Email, Postal Letter
  All are about notifying a customer.
  Single responsibility = "notify the customer" ✓

Weak cohesion (DO split):
  "Customer Service" → profile maintenance + preferences + comments
  These relate to a broad scope "customer" — too broad!
  Split into: Profile Service, Preferences Service, Comments Service ✓
```

**Naming test:** If you can't give the "leftover" service a clean, descriptive name → the split is wrong.

### 2. Code Volatility

Measure rate of change per function within the service:

```
Notification Service change rates:
  SMS notification:          every 6 months
  Email notification:        every 6 months
  Postal Letter notification: EVERY WEEK ← volatile!

Result: Postal letter changes force full-service redeployment
        including stable SMS and Email code

Solution: Split into:
  Electronic Notification  (SMS + Email, changes rarely)
  Postal Letter Service    (changes weekly, small focused service)
```

### 3. Scalability and Throughput

Measure scale demands per function:

```
Notification Service throughput:
  SMS:           220,000 / minute  ← massive!
  Email:             500 / minute
  Postal Letter:       1 / minute  ← negligible

In a single service: Email and Postal Letter must scale to SMS demand
→ Waste of resources

Split into 3 services:
  SMS Service       → scales aggressively
  Email Service     → moderate scaling
  Letter Service    → minimal scaling ✓
```

### 4. Fault Tolerance

If one function in a service crashes and kills the whole service:

```
Single Notification Service:
  Email crashes (out-of-memory) → entire service down
  SMS stops too ✗

Split services:
  Email Service crashes → only email affected
  SMS Service continues ✓

Naming test after split:
  "Email Service" + "Other Notification Service" ← BAD name!
  "Email Service" + "Non-Email Service"          ← BAD name!
  "Email Service" + "SMS Service" + "Letter Service" ← GOOD ✓
```

### 5. Security

Sensitive operations need their own service boundary:

```
Customer Profile Service (single service):
  → Manage profile (name, address)
  → Manage credit card info  ← sensitive PCI data

Risk: Anyone who accesses the service for profile data
      might also reach credit card operations.

Split:
  Customer Profile Service  (general access)
  Credit Card Service       (restricted access, dedicated security) ✓
```

### 6. Extensibility

Split if the service will frequently grow with new similar contexts:

```
Payment Service: Credit Cards, Gift Cards, PayPal
→ Company plans to add: Reward Points, Store Credit, ApplePay, SamsungPay

Each addition = retest and redeploy all payment types!

Split:
  Credit Card Service → stable
  Gift Card Service   → stable
  PayPal Service      → stable
  Reward Points       → new, only its own tests/deployment
  (each new method = one new service)
```

---

## 🔒 Granularity Integrators (Reasons to Keep Together)

### 1. Database Transactions

If two services must participate in an ACID transaction → combine them.

```
Customer Profile Service + Password Service (split for security):

Registering a new customer:
  1. Profile Service: INSERT customer ✓ COMMITTED
  2. Password Service: INSERT password ✗ FAILS
  
Result: Customer record exists with no password → data corruption!

Only options:
  a) Combine into a single service (gets ACID back)
  b) Implement complex compensating transactions (Chapter 12)

If data integrity is critical → combine ✓
```

### 2. Workflow and Choreography

Services that must talk to each other erode the benefits of splitting:

```
5 separate customer services all called from one API request:

API → Service A → Service B → Service C → Service D → Service E

Assuming 300ms latency per hop:
  5 hops × 300ms = 1,500ms added latency!

Also: If Service C goes down, ALL requests fail (transitive dependency)

Rule of thumb:
  If 70%+ of requests require cross-service calls → combine
  If 70%+ of requests are atomic (one service) → keep split
```

### 3. Shared Code

If multiple services share domain-specific code in a shared library:

```
5 services all depend on SharedDomain.jar

SharedDomain.jar changes:
  All 5 services must be updated, tested, deployed together.
  
This is the monolith again — just distributed!

Solution: If domain code sharing is unavoidable → combine services
         (Infrastructure code sharing is OK via sidecar/library)
```

### 4. Data Relationships

If the data for two services is tightly related (foreign keys, joins):

```
Order Service + Order Item Service (split):
  order_item has FK → order
  
Separation requires removing FK → referential integrity is application's job
  → More bugs, more complexity

If tight data relationships exist → keep services together ✓
```

---

## ⚖️ Finding the Right Balance

```
Forces pulling APART:            Forces pulling TOGETHER:
─────────────────────            ──────────────────────
Weak cohesion                    Database transactions
Volatile code in one part        High inter-service workflow
Different scale needs            Shared domain code
Fault isolation needs            Tight data relationships
Security separation
Planned extensibility

THE GOAL: Equilibrium between disintegrators and integrators
```

### Decision Framework

```
For any proposed split, ask:
  1. Do these functions have weak or strong cohesion?
  2. Does each part change at a different rate?
  3. Does each part need different scale?
  4. Would isolation improve fault tolerance?
  5. Does security require separation?
  6. Is extensibility planned?

Then check the integrators:
  1. Is ACID required across the split?
  2. Do they communicate heavily with each other?
  3. Do they share domain code?
  4. Are their data tables tightly coupled?

If disintegrators outweigh integrators → split
If integrators outweigh disintegrators → keep together
```

---

## 🏢 Sysops Squad Saga: Two Granularity Decisions

### Ticket Assignment: Fine-Grained or Not?

```
Proposed split: 4 separate services
  Ticket Creation, Ticket Assignment, Ticket Routing, Ticket Completion

Analysis:
  Disintegrators:
    ✓ Different change rates (assignment changes most)
    ✓ Assignment needs independent scalability
  
  Integrators:
    ✗ Ticket workflow is highly sequential (one calls the next)
    ✗ ACID needed for assignment → routing → notification chain
    
Decision: Keep as 2 services
  Ticket Service   (creation + maintenance + completion)
  Assignment Service (assignment + routing as atomic pair)
```

### Customer Registration: One or Many?

```
Proposed split: 3 separate services
  Registration Service, Profile Service, Billing Service

Analysis:
  Disintegrators:
    ✓ Different security levels (billing = PCI)
    ✓ Different change rates
  
  Integrators:
    ✗ Registration creates customer + profile + billing in ONE transaction
    ✗ Splitting = ACID lost → partial registrations possible
    
Decision: 2 services
  Registration + Profile Service (combined for ACID on register)
  Billing Service (separate for security, compensating tx on failure)
```

---

## 💡 Key Takeaways

| Insight | Implication |
|---------|-------------|
| "Single responsibility" is subjective — use disintegrators instead | Apply 6 objective drivers rather than gut feeling |
| Both disintegrators AND integrators must be evaluated | A split that breaks ACID or creates constant workflow is a bad split |
| The naming test reveals bad splits | If leftover services can't be cleanly named, reconsider the boundary |
| More services talking = more latency, more failure risk | Count the percentage of requests that cross service boundaries |
| Granularity ≠ "as small as possible" | Granularity = right size for the actual trade-offs in your context |

---

*← [Back to Software Architecture: The Hard Parts](../README.md)*
