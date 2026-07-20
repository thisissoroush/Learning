# Chapter 2 — Decomposition Strategies

> *"The key challenge, which is the essence of the microservice architecture, is the functional decomposition of the application into services."*

---

## 🎯 Core Concept

If chapter 1 asks *why* to use microservices, chapter 2 answers *how* to split your application into them. This is the hardest problem in microservice architecture — there is no algorithm, only strategies. The two primary strategies are **Decompose by Business Capability** and **Decompose by DDD Subdomain**. Along the way, we must eliminate **god classes** that make decomposition nearly impossible.

---

## 🏛️ What Is Software Architecture?

The **4+1 View Model** describes architecture across four complementary lenses:

```
┌──────────────────────────────────────────────────────────┐
│                  4+1 View Model                          │
│                                                          │
│  Logical View        Implementation View                 │
│  (classes, packages) (modules, JARs, WARs)               │
│                                                          │
│  Process View        Deployment View                     │
│  (processes, IPC)    (machines, networks)                │
│                                                          │
│  +1 Scenarios (animate the views — use cases)            │
└──────────────────────────────────────────────────────────┘
```

Architecture matters because it determines the **-ilities** (quality attributes):
- Maintainability, testability, deployability → *development time*
- Scalability, reliability, security → *runtime*

---

## 🔷 Architectural Styles

### Hexagonal Architecture (preferred for microservices)

Each microservice should internally follow the **hexagonal architecture** style:

```
         ┌─────────────────────────────────┐
         │                                 │
REST ───▶│ Inbound    ┌────────────────┐   │
API      │ Adapters   │                │   │──▶ Database
         │            │  Business      │   │    (outbound
MSG ───▶│            │  Logic         │   │     adapter)
broker   │            │                │   │──▶ Message
         │            └────────────────┘   │    broker
         │ (inbound ports)  (outbound ports)│
         └─────────────────────────────────┘

Business logic at center — adapters on the outside
```

- **Inbound adapters**: REST API, gRPC, message consumers — they call the business logic
- **Outbound adapters**: Database DAOs, external service clients — called by the business logic
- **Ports**: Interfaces between adapters and business logic

---

## 📋 Step 1 — Identify System Operations

Before decomposing into services, identify the **system operations** your application must handle.

### Process:
1. Analyze requirements (user stories) → create a **high-level domain model**
2. Identify **commands** (create, update, delete) and **queries** (read) from verbs in the stories

```
User Story: "As a consumer, I want to place an order"
                 ↓
Domain Model nouns: Consumer, Order, Restaurant, Courier
                 ↓
System Operations:
  Commands: createOrder(), acceptOrder(), cancelOrder()
  Queries:  findAvailableRestaurants(), findOrderById()
```

### Example: FTGO System Operations

| Operation | Service | Type |
|-----------|---------|------|
| `createOrder()` | Order Service | Command |
| `acceptOrder()` | Kitchen Service | Command |
| `noteUpdatedLocation()` | Delivery Service | Command |
| `findAvailableRestaurants()` | Restaurant Service | Query |

Each command has **preconditions** (what must be true before) and **postconditions** (what becomes true after).

---

## 🏢 Step 2a — Decompose by Business Capability

**Pattern: Decompose by Business Capability**  
> Define services corresponding to business capabilities — what a business *does* to generate value.

Business capabilities are **stable** (what you do doesn't change, only *how* you do it).

### FTGO Business Capabilities → Services

```
Supplier Management
├── Courier Management      → Courier Service
└── Restaurant Management   → Restaurant Service

Consumer Management         → Consumer Service

Order Taking & Fulfillment
├── Order Management        → Order Service
├── Restaurant Order Mgmt   → Kitchen Service
└── Delivery Management     → Delivery Service

Accounting                  → Accounting Service
```

Key insight: **Three different restaurant capabilities** → three different services (Restaurant Service, Kitchen Service, Accounting Service). They represent completely different aspects of restaurant operations.

---

## 🧩 Step 2b — Decompose by DDD Subdomain

**Pattern: Decompose by Subdomain**  
> Define services corresponding to DDD subdomains — each with its own bounded context.

DDD's **Bounded Context** = the scope of a domain model. Each bounded context maps to one or more services.

```
FTGO Subdomains → Services
┌─────────────────┐     ┌─────────────────────┐
│ Order Taking    │────▶│ Order Service        │
│ Subdomain       │     │ (Order domain model) │
└─────────────────┘     └─────────────────────┘

┌─────────────────┐     ┌─────────────────────┐
│ Kitchen         │────▶│ Kitchen Service      │
│ Subdomain       │     │ (Ticket domain model)│
└─────────────────┘     └─────────────────────┘
```

DDD and microservices align perfectly:
- **Subdomain** ↔ **Service**
- **Bounded Context** ↔ **Service boundary**
- **Ubiquitous Language** ↔ **Service's domain model**

---

## 📏 Decomposition Guidelines (from OOD)

Two principles from Robert C. Martin apply at the service level:

| Principle | Service-Level Application |
|-----------|--------------------------|
| **SRP** — Single Responsibility | Each service has one reason to change |
| **CCP** — Common Closure | Things that change together belong in the same service |

---

## 🚧 Obstacles to Decomposition

### 1. Network Latency
Too many round-trips between services → combine services or use batch APIs.

### 2. Synchronous Communication → Reduced Availability
If Service A calls Service B synchronously, A's availability depends on B's.
Solution: use asynchronous messaging (see chapter 3).

### 3. Maintaining Data Consistency
Transactions cannot span services. Solution: **Sagas** (see chapter 4).

### 4. God Classes 🔥

**God classes** are the biggest obstacle. They are bloated classes used everywhere — they prevent decomposition because splitting them would require all services to share the same object.

```
Order God Class (WRONG — traditional approach)
┌──────────────────────────────────────────────┐
│ Order                                         │
│  - orderId, orderStatus, orderLineItems       │
│  - deliveryAddress, deliveryTime              │
│  - paymentInfo, transactionId                 │
│  - restaurantId, courierId                    │
│                                               │
│  + create(), cancel(), accept(), reject()     │
│  + assignCourier(), notePickedUp()            │
│  + authorizeCard(), noteDelivered()           │
└──────────────────────────────────────────────┘
         ↑ Every service needs this class!
```

### DDD Solution: Multiple Domain Models

Instead, each service has its **own version** of Order:

```
Order Service            Kitchen Service          Delivery Service
┌──────────────┐         ┌─────────────┐          ┌──────────────┐
│ Order        │         │ Ticket      │          │ Delivery     │
│  - orderId   │         │  - ticketId │          │  - orderId   │
│  - status    │         │  - status   │          │  - pickup    │
│  - consumer  │         │  - lineItems│          │  - dropoff   │
│  - restaurant│         │  - prepTime │          │  - courier   │
│  - total     │         └─────────────┘          └──────────────┘
└──────────────┘
```

Each service has a **simpler, focused view** of what an Order means to it. Data consistency across these views is maintained via events (sagas).

---

## 🔗 Step 3 — Define Service APIs

After identifying services, assign system operations to services, then determine collaboration:

```
createOrder() flow:
Client
  │
  ▼
Order Service ──verify consumer──▶ Consumer Service
              ──validate order──▶  Restaurant Service
              ──create ticket──▶   Kitchen Service
              ──authorize card──▶  Accounting Service
```

Operations exist for two reasons:
1. **External requests** — invoked by clients
2. **Internal collaboration** — invoked by other services

---

## 💡 Key Takeaways

| Insight | Implication |
|---------|-------------|
| Decomposition is an art, not a science | Use business capabilities and DDD subdomains as your guide |
| SRP and CCP apply at the service level | Each service = one reason to change |
| God classes prevent decomposition | Use DDD — give each service its own domain model |
| Services reference each other by primary key, not object reference | Loose coupling across service boundaries |
| System operations are the architectural scenarios | Define them before assigning them to services |

---

*← [Back to Microservices Patterns](../README.md)*
