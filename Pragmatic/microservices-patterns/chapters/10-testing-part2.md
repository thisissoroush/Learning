# Chapter 10 — Testing Microservices: Part 2

> *"Component tests test a service in isolation, and end-to-end tests test the entire application."*

---

## 🎯 Core Concept

This chapter continues the testing strategy with **integration tests**, **component tests**, and **end-to-end tests**. The goal: test enough to be confident, without creating a slow and brittle test suite.

---

## 🔌 Integration Tests

Test how a service integrates with its infrastructure (DB, messaging) or another service's API — without deploying the full system.

```
Integration Test Scope:
  Service ↔ Database        (persistence integration tests)
  Service ↔ Message Broker  (publish/subscribe tests)
  Service ↔ Another Service (REST contract tests)
```

### Persistence Integration Tests
```java
// Test that OrderRepository correctly persists and loads orders
@Test
void shouldSaveAndLoadOrder() {
  Order order = Order.createOrder(...);
  orderRepository.save(order);
  
  Order loaded = orderRepository.findById(order.getId());
  assertEquals(order.getStatus(), loaded.getStatus());
}
// Uses embedded DB or test containers — real DB, not mocks
```

### Messaging Integration Tests
```
Publisher test: Publish event → verify message lands in broker
Subscriber test: Drop message in broker → verify handler invoked
```

### REST Integration Tests
```
Use Spring MockMVC or similar to test REST endpoints.
Service under test + real DB, but collaborating services are stubbed.
```

---

## 🧩 Component Tests

Test a **complete service in isolation** — all its layers, but with collaborating services replaced by stubs.

```
Component Test Setup:
  ┌─────────────────────────────────────────┐
  │  Order Service (real: all layers)       │
  │  - REST API, business logic, DB         │
  │  - Messaging infrastructure             │
  │                                         │
  │  [Consumer Service STUB]               │
  │  [Kitchen Service STUB]                │
  │  [Accounting Service STUB]             │
  └─────────────────────────────────────────┘
```

Write tests using **Gherkin** (Given/When/Then):
```gherkin
Scenario: Create order successfully
  Given a valid consumer
  And a valid restaurant
  When I place an order
  Then the order is in APPROVAL_PENDING state
  And an OrderCreated event is published
```

Component tests give high confidence that a service works correctly without the overhead of E2E tests.

---

## 🌐 End-to-End Tests

Test the **entire system** deployed together — all real services, real messaging, real databases.

```
E2E Test:
  Client → API Gateway → Order Service → Kitchen Service → Accounting Service
                                    ↕
                             Message Broker

Use sparingly — they are:
  - Slow (minutes to run)
  - Fragile (any service going down breaks them)
  - Hard to maintain
  - Expensive to set up
```

**Strategy**: only E2E test the happy path and most critical business flows.

---

## 🚀 The Deployment Pipeline

```
Code push → Unit Tests → Integration Tests → Component Tests → Deploy to Staging → E2E Tests → Deploy to Production
              (fast)        (medium)           (medium)                               (slow)
              
Fail fast: if unit tests fail, don't run integration tests
```

---

## 💡 Key Takeaways

| Insight | Implication |
|---------|-------------|
| Integration tests need real infrastructure | Use Testcontainers for real DB/broker in tests |
| Component tests isolate the service under test | Stub all external services — test business logic fully |
| Acceptance tests should be written in Gherkin | Readable by non-developers; documents behavior |
| E2E tests are a safety net, not the main defense | Run few, target critical paths only |
| Each test type has a place in the pyramid | Don't skip integration or component tests |

---

*← [Back to Microservices Patterns](../README.md)*
