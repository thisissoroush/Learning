# Microservices Patterns

**Author**: Chris Richardson  
**Published**: 2019 · Manning Publications  
**Category**: Software Architecture / Distributed Systems

---

## 📖 About This Book

*Microservices Patterns* is the practical guide to building production-ready microservice systems. Author Chris Richardson — creator of microservices.io — teaches you how to solve the real challenges that arise when you break a monolith into services: distributed data management, transaction coordination, API design, observability, testing, and deployment.

The book is organized around a **pattern language** — a collection of named, interrelated solutions to recurring problems. Rather than preaching microservices as the answer to everything, Richardson objectively describes each pattern's benefits, drawbacks, and trade-offs.

The running example throughout is **FTGO** (Food to Go), a food delivery application that starts as a monolith suffering from "monolithic hell" and is progressively transformed into a microservice architecture.

---

## 🗺️ The Pattern Language at a Glance

```
Application Architecture
  ├── Monolithic Architecture
  └── Microservice Architecture
        │
        ├── Decomposition
        │     ├── Decompose by Business Capability
        │     └── Decompose by Subdomain (DDD)
        │
        ├── Data Management
        │     ├── Database per Service
        │     ├── Saga (choreography / orchestration)
        │     ├── API Composition
        │     └── CQRS
        │
        ├── Communication
        │     ├── Remote Procedure Invocation (REST, gRPC)
        │     ├── Messaging (async, message broker)
        │     ├── Circuit Breaker
        │     └── Transactional Outbox
        │
        ├── External API
        │     ├── API Gateway
        │     └── Backends for Frontends (BFF)
        │
        ├── Business Logic
        │     ├── Transaction Script
        │     ├── Domain Model (DDD Aggregates)
        │     ├── Domain Events
        │     └── Event Sourcing
        │
        ├── Testing
        │     ├── Consumer-Driven Contract Tests
        │     ├── Component Tests
        │     └── End-to-End Tests
        │
        ├── Observability
        │     ├── Health Check API
        │     ├── Log Aggregation
        │     ├── Distributed Tracing
        │     ├── Application Metrics
        │     ├── Exception Tracking
        │     └── Audit Logging
        │
        ├── Deployment
        │     ├── Service as Container
        │     ├── Service as VM
        │     ├── Serverless
        │     └── Service Mesh
        │
        └── Refactoring
              ├── Strangler Application
              └── Anti-Corruption Layer
```

---

## 📚 Chapters

| # | Chapter | Core Pattern |
|---|---------|-------------|
| [01](chapters/01-escaping-monolithic-hell.md) | Escaping Monolithic Hell | Monolithic vs. Microservice Architecture |
| [02](chapters/02-decomposition-strategies.md) | Decomposition Strategies | Decompose by Business Capability / Subdomain |
| [03](chapters/03-interprocess-communication.md) | Interprocess Communication | REST, gRPC, Messaging, Circuit Breaker |
| [04](chapters/04-managing-transactions-with-sagas.md) | Managing Transactions with Sagas | Saga Pattern (choreography & orchestration) |
| [05](chapters/05-designing-business-logic.md) | Designing Business Logic | DDD Aggregates, Domain Events |
| [06](chapters/06-event-sourcing.md) | Event Sourcing | Event Sourcing, CQRS |
| [07](chapters/07-implementing-queries.md) | Implementing Queries | API Composition, CQRS Views |
| [08](chapters/08-external-api-patterns.md) | External API Patterns | API Gateway, BFF |
| [09](chapters/09-testing-part1.md) | Testing: Part 1 | Test Pyramid, Unit Tests, Contract Tests |
| [10](chapters/10-testing-part2.md) | Testing: Part 2 | Integration, Component, E2E Tests |
| [11](chapters/11-production-ready-services.md) | Production-Ready Services | Observability, Security, Configuration |
| [12](chapters/12-deploying-microservices.md) | Deploying Microservices | Containers, Kubernetes, Serverless |
| [13](chapters/13-refactoring-to-microservices.md) | Refactoring to Microservices | Strangler Application, ACL |

---

## 💡 Key Takeaways

→ [View all 20 key takeaways](key-takeaways.md)

**The five most important ideas:**

1. **Microservices are not a silver bullet** — they solve complexity problems but introduce distributed systems complexity. Only adopt when the monolith complexity exceeds the cost of distribution.

2. **Database per service is non-negotiable** — each service owns its data. Use Sagas to maintain consistency across service boundaries.

3. **Prefer asynchronous messaging for inter-service communication** — synchronous calls chain failures; messaging buffers them.

4. **Observability from day one** — distributed tracing, log aggregation, and metrics are not optional in a distributed system.

5. **Strangle, don't rewrite** — migrate incrementally using the Strangler Application pattern. Stop adding to the monolith; implement new features as services.

---

## 🔗 Related Books in This Repo

- [Clean Architecture](../clean-architecture/README.md) — architectural principles that complement microservice design
- [The Pragmatic Programmer](../the-pragmatic-programmer/README.md) — software craftsmanship fundamentals

---

*[← Back to Pragmatic](../README.md)*
