# Chapter 8 — External API Patterns

> *"The API gateway is the entry point into the application for API clients."*

---

## 🎯 Core Concept

External clients (mobile apps, browsers, third-party systems) shouldn't talk directly to individual microservices. An **API Gateway** is the single entry point that routes requests, handles cross-cutting concerns, and adapts the API for different client types.

---

## ❌ The Problem with Direct Client-to-Service Communication

```
Without API Gateway:
Mobile App → Order Service:8001
           → Restaurant Service:8002
           → Delivery Service:8003
           → Consumer Service:8004

Problems:
  1. Client must know addresses of ALL services
  2. Many round-trips (poor mobile performance)
  3. Services expose internal APIs to public internet
  4. Security concerns scattered across services
  5. Protocol mismatch (internal gRPC, client needs REST)
```

---

## 🚪 Pattern: API Gateway

```
External clients → API Gateway → Internal Services
                       │
                  ┌────┴────────────────────┐
                  │  Routing & Composition  │
                  │  Authentication         │
                  │  Rate limiting          │
                  │  SSL termination        │
                  │  Request transformation │
                  └─────────────────────────┘
```

**API Gateway responsibilities:**
- Route requests to the correct service
- Aggregate data from multiple services (API composition)
- Translate protocols (REST → gRPC internally)
- Handle authentication — validate JWT tokens
- Rate limiting and caching
- SSL termination

---

## 📱 Pattern: Backends for Frontends (BFF)

Different clients have different needs. BFF creates dedicated API gateways per client type.

```
Mobile App ──▶ Mobile BFF ──▶ Services
Browser    ──▶ Web BFF    ──▶ Services  
3rd Party  ──▶ Public API ──▶ Services

Benefits:
  - Each BFF optimized for its client's needs
  - Mobile BFF returns compact responses
  - Web BFF can return richer data
  - Teams own their BFF independently
```

---

## 🔧 Implementing an API Gateway

**Option 1: Off-the-shelf** (AWS API Gateway, Kong, Nginx)
- Pros: Feature-rich, managed, low operational overhead
- Cons: Less flexible for custom business logic

**Option 2: Build your own** (Netflix Zuul, Spring Cloud Gateway)
- Pros: Full control, custom logic
- Cons: Operational burden

**Option 3: GraphQL** — increasingly popular for flexible data fetching

```graphql
# Client specifies exactly what data it needs
query {
  order(id: "123") {
    status
    restaurant { name }
    deliveryTime
    lineItems { name, price }
  }
}
```

GraphQL resolvers call the appropriate services and compose the response.

---

## ⚖️ Trade-offs

| Approach | Pros | Cons |
|----------|------|------|
| Single API Gateway | Simple to manage | Risk of bottleneck; all teams share |
| BFF per client type | Optimized per client | More gateways to manage |
| GraphQL | Flexible, client-driven | Complex schema management |

---

## 💡 Key Takeaways

| Insight | Implication |
|---------|-------------|
| Don't expose internal services directly | API Gateway is mandatory for security and encapsulation |
| Different clients need different APIs | BFF pattern tailors APIs per client type |
| API Gateway can do API composition | Aggregates data from multiple services for clients |
| GraphQL is great for flexible data fetching | Reduces over/under-fetching for complex UIs |

---

*← [Back to Microservices Patterns](../README.md)*
