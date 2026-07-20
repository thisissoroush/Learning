# Chapter 9 — Testing Microservices: Part 1

> *"The microservice architecture makes individual services easier to test because they're much smaller than the monolithic application."*

---

## 🎯 Core Concept

Testing microservices is different from testing monoliths. Services are smaller and easier to test in isolation, but testing *interactions* between services is harder. The **test pyramid** guides what types of tests to write and in what proportion.

---

## 🔺 The Test Pyramid

```
        /\
       /  \
      / E2E\       ← Few, slow, fragile (test the whole system)
     /──────\
    /  Comp  \     ← Some (test one service in isolation)
   /──────────\
  / Integration\   ← More (test service + its dependencies)
 /──────────────\
/   Unit Tests   \  ← Many, fast, cheap (test individual classes)
──────────────────

Rule: more unit tests, fewer integration tests, very few E2E tests
```

### Why the Pyramid Matters for Microservices

- E2E tests are expensive and slow → avoid over-relying on them
- Unit tests give fast feedback → write many
- Consumer-driven contract tests fill the gap between unit and E2E

---

## 🧪 Types of Tests

| Type | What It Tests | Speed | Fragility |
|------|--------------|-------|-----------|
| **Unit** | Individual class/method | Fast | Low |
| **Integration** | Service + DB/messaging layer | Medium | Medium |
| **Component** | Whole service, mocked dependencies | Medium | Medium |
| **Contract** | Service interactions via agreed contracts | Medium | Low |
| **E2E** | All services together | Slow | High |

---

## ✅ Unit Tests in Microservices

Write unit tests for:

**Entities** — test business rules and state transitions
```java
@Test
void shouldApproveOrder() {
  Order order = Order.createOrder(CONSUMER_ID, RESTAURANT, LINE_ITEMS);
  order.approve();
  assertEquals(APPROVED, order.getState());
}
```

**Value Objects** — test equality and behavior
```java
@Test
void shouldAddMoney() {
  assertEquals(new Money(10), new Money(6).add(new Money(4)));
}
```

**Sagas** — test state machine transitions
```java
@Test
void shouldRejectOrderIfCardAuthorizationFails() {
  // Given: saga in card authorization step
  // When: card authorization fails
  // Then: saga sends RejectOrder command to Order Service
}
```

**Domain Services** — test business logic operations  
**Controllers** — test REST endpoint behavior  
**Event/Message Handlers** — test message handling logic

---

## 🤝 Consumer-Driven Contract Tests

The gap between unit tests and E2E tests. Each service pair has a **contract**:

```
Consumer (Order Service) defines expectations:
  - calls POST /consumers/{id}/validate
  - expects 200 OK with { status: "OK" }

Provider (Consumer Service) verifies:
  - it satisfies the contract without being invoked by Order Service
  
Tools: Pact, Spring Cloud Contract
```

```
Contract Test Flow:
  1. Consumer writes test that defines expected behavior
  2. Contract is shared (e.g., via git)
  3. Provider runs contract verification tests
  4. If provider passes → safe to deploy both services
```

---

## 💡 Key Takeaways

| Insight | Implication |
|---------|-------------|
| Follow the test pyramid | Invest heavily in unit tests, sparingly in E2E |
| Test each class in isolation | Use mocks for dependencies |
| Consumer-driven contracts prevent breaking changes | Both sides verify the contract independently |
| Sagas are testable as state machines | Each state transition is a unit test |

---

*← [Back to Microservices Patterns](../README.md)*
