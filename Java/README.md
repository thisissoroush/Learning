# ☕ Java — Learning Resources

This section contains interview preparation materials for Java and the Spring ecosystem — covering language fundamentals, concurrency, frameworks, ORMs, security, messaging, build tools, and production patterns.

---

## 🎯 Interview Questions

### Core Language

| Level | File | Focus |
|-------|------|-------|
| 🟢 Junior | [interview-questions/junior.md](interview-questions/junior.md) | Primitives, OOP, collections, exceptions, records, sealed classes, Optional |
| 🟡 Mid | [interview-questions/mid.md](interview-questions/mid.md) | Streams, lambdas, generics, concurrency, memory model, HashMap internals, CompletableFuture |
| 🔴 Senior | [interview-questions/senior.md](interview-questions/senior.md) | JIT, GC, JVM profiling, virtual threads, structured concurrency, VarHandle, reflection |
| 🏛️ Architect | [interview-questions/architect.md](interview-questions/architect.md) | Microservices, CQRS/ES, distributed transactions, observability, zero-downtime, ArchUnit |

### Framework & Library Specific

| Topic | File | Focus |
|-------|------|-------|
| 🌱 Spring Boot | [interview-questions/spring-boot.md](interview-questions/spring-boot.md) | Auto-configuration, beans, MVC, WebFlux, actuator, caching, @Transactional, testing |
| 🗄️ Hibernate / JPA | [interview-questions/hibernate-jpa.md](interview-questions/hibernate-jpa.md) | Entity lifecycle, relationships, N+1, caching, locking, Spring Data JPA, multi-tenancy |
| 🔐 Spring Security | [interview-questions/spring-security.md](interview-questions/spring-security.md) | JWT, OAuth2, method security, custom filters, CSRF, CORS, testing |
| 📬 Messaging | [interview-questions/messaging.md](interview-questions/messaging.md) | Kafka (Spring Kafka), RabbitMQ (Spring AMQP), outbox pattern, Saga, transactional events |
| 📡 gRPC | [interview-questions/grpc.md](interview-questions/grpc.md) | Proto setup, streaming, interceptors, TLS/mTLS, load balancing, Spring Boot integration |

### Tooling

| Topic | File | Focus |
|-------|------|-------|
| 🔨 Maven & Gradle | [interview-questions/maven-gradle.md](interview-questions/maven-gradle.md) | Lifecycle, scopes, multi-module, CI/CD, custom plugins, BOM, build performance |
| 🧪 Testing | [interview-questions/testing.md](interview-questions/testing.md) | JUnit 5, Mockito, AssertJ, MockMvc, DataJpaTest, Testcontainers, WireMock, contract testing |

---

## 🔑 Key Themes

- **Spring Boot convention over configuration** — auto-wired, opinionated defaults with easy overrides
- **Reactive programming** — Spring WebFlux + Project Reactor for non-blocking I/O at scale
- **Virtual threads (Java 21)** — simplify concurrency without reactive complexity
- **Immutability first** — records, sealed classes, `Collections.unmodifiableX`
- **Observability built in** — Micrometer, OpenTelemetry, Actuator
- **DDD alignment** — bounded contexts, domain events, CQRS, outbox pattern

---

## 🔗 Related Sections

- [C# - .Net/interview-questions](../C%23%20-%20.Net/interview-questions/README.md) — Similar enterprise framework ecosystem
- [Go/interview-questions](../Go/interview-questions/README.md) — Go's approach to the same problems
