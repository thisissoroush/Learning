# Chapter 11 — Developing Production-Ready Services

> *"In order to be production-ready, a service must implement security, use externalized configuration, and be observable."*

---

## 🎯 Core Concept

Getting a service to pass tests is one thing. Making it production-ready requires **security**, **configurability**, and **observability**. These are cross-cutting concerns that every service needs — the Microservice Chassis pattern provides a reusable foundation.

---

## 🔐 Security in Microservices

Traditional monolith: security is centralized in one place.  
Microservices: the API Gateway authenticates; services must authorize.

```
Security Flow:
Client ──token──▶ API Gateway (authenticates) ──JWT──▶ Services (authorize)

JWT (JSON Web Token) = Access Token:
  Header: { alg: HS256, typ: JWT }
  Payload: { userId: 123, roles: ["ADMIN"], exp: 1234567890 }
  Signature: HMAC(header + payload, secret)

Services verify JWT signature → trust user identity from payload
No need to call auth service per request!
```

**Access Token Pattern**:
1. Client logs in → Auth Service returns JWT
2. Client sends JWT in `Authorization: Bearer <token>` header
3. API Gateway validates JWT → passes user info to services
4. Each service extracts user context from JWT without calling auth service

---

## ⚙️ Externalized Configuration

Services need environment-specific config (DB URLs, API keys, feature flags). Hard-coding is dangerous.

```
Problem: Hard-coded config
  DataSource ds = new DataSource("jdbc:mysql://prod-db/orders", "root", "secret123");
  // What about dev? What about rotating passwords?

Solution: Externalized Configuration
  String url = System.getenv("DB_URL");    // Push-based (env vars)
  String url = configService.get("DB_URL"); // Pull-based (config server)
```

**Push-based** (env vars, Kubernetes ConfigMaps/Secrets):
- Simple, no extra infrastructure
- Set at deployment time

**Pull-based** (Spring Cloud Config Server, HashiCorp Vault):
- Dynamic refresh without restart
- Centralized management
- Better for secrets rotation

---

## 👁️ Observability Patterns

Distributed systems are hard to debug without proper observability.

### Health Check API
```
GET /actuator/health → { "status": "UP" }

Load balancer polls health endpoint:
  - UP → route traffic here
  - DOWN → remove from rotation and alert
```

### Log Aggregation
```
Without aggregation:
  Developer must SSH into 10 different servers to see logs ❌

With aggregation:
  All services → Logstash/Fluentd → Elasticsearch → Kibana
  Search all service logs in one place ✅
```

### Distributed Tracing
```
Request flows through: API Gateway → Order Service → Kitchen Service → ...

Without tracing: impossible to see the full journey

With tracing (Zipkin, Jaeger):
  Every request gets a trace ID (propagated in headers)
  Each service records its span with timing
  Visualize the full request chain and find the bottleneck
  
  TraceID: abc123
    Span 1: API Gateway (2ms)
    Span 2: Order Service (50ms)
      Span 3: Kitchen Service (30ms)
      Span 4: Accounting Service (20ms)
```

### Application Metrics
```
Services expose metrics:
  - Request rate, error rate, latency (RED metrics)
  - Business metrics: orders/minute, revenue/hour

Prometheus scrapes metrics → Grafana visualizes dashboards
Alert when error_rate > 5% or latency_p99 > 500ms
```

### Exception Tracking
```
When an exception occurs:
  1. Capture full stack trace
  2. Send to exception tracking service (Sentry, Bugsnag)
  3. Deduplicate (same exception = one alert)
  4. Alert on-call developer
  5. Track resolution
```

### Audit Logging
```
Who did what and when:
  User 123 cancelled order 456 at 2024-01-15 14:30:00

Important for:
  - Compliance (financial regulations)
  - Debugging ("what happened to this order?")
  - Security investigation
```

---

## 🏗️ Microservice Chassis Pattern

Every service needs all the above. Implementing from scratch each time is wasteful.

```
Microservice Chassis = reusable foundation library:
  - Health checks
  - Metrics collection
  - Distributed tracing
  - Log formatting
  - Externalized config

Spring Boot + Spring Cloud = Java Microservice Chassis

New services: inherit chassis → focus on business logic only
```

**Service Mesh** (Istio, Linkerd) — next evolution:
- Move cross-cutting concerns to infrastructure (sidecar proxy)
- Services don't need to implement tracing, retries, circuit breaking
- Sidecar proxy handles it transparently

---

## 💡 Key Takeaways

| Insight | Implication |
|---------|-------------|
| Authenticate at the API Gateway, authorize in services | JWT access tokens propagate identity without calling auth service |
| Never hard-code configuration | Externalize everything; use env vars or a config server |
| You can't debug what you can't see | Implement all 6 observability patterns from day one |
| Distributed tracing is non-negotiable | Without trace IDs, debugging cross-service requests is guesswork |
| Microservice chassis prevents duplication | Create shared infrastructure once; services focus on business logic |

---

*← [Back to Microservices Patterns](../README.md)*
