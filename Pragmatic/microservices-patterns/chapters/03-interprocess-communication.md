# Chapter 3 — Interprocess Communication in a Microservice Architecture

> *"I favor an architecture consisting of loosely coupled services that communicate with one another using asynchronous messaging."*

---

## 🎯 Core Concept

In a monolith, modules call each other with simple method calls. In microservices, services are separate processes — they must communicate over the network. This changes everything. Chapter 3 covers the full landscape of IPC options: **synchronous REST and gRPC**, **asynchronous messaging**, and critical patterns like **Circuit Breaker**, **Service Discovery**, and **Transactional Messaging**.

The book's clear recommendation: **prefer asynchronous messaging** because it maximizes availability.

---

## 🔀 Interaction Styles — Two Dimensions

```
                    ONE-TO-ONE            ONE-TO-MANY
                 ┌──────────────┐      ┌─────────────────────┐
SYNCHRONOUS      │ Request/     │      │ (not commonly used) │
                 │ Response     │      │                     │
                 └──────────────┘      └─────────────────────┘
                 ┌──────────────┐      ┌─────────────────────┐
ASYNCHRONOUS     │ Async Req/   │      │ Publish/Subscribe   │
                 │ Response     │      │ Publish/Async Resp  │
                 │ One-way Notif│      │                     │
                 └──────────────┘      └─────────────────────┘
```

---

## 🌐 Synchronous IPC — REST

**REST** is the most popular choice. It uses HTTP verbs on resources.

```
Order Service REST API
GET    /orders/{orderId}    → retrieve order
POST   /orders              → create order
PUT    /orders/{orderId}    → update order
DELETE /orders/{orderId}    → cancel order
POST   /orders/{orderId}/cancel  → custom action
```

**Richardson REST Maturity Model:**

| Level | Description |
|-------|-------------|
| 0 | Single HTTP endpoint, action in body |
| 1 | Resources (URLs per resource) |
| 2 | HTTP verbs (GET, POST, PUT, DELETE) ← most APIs here |
| 3 | HATEOAS (links in responses) |

**Pros**: Simple, familiar, firewall-friendly, no broker needed  
**Cons**: Synchronous coupling, both sides must be up, fetching multiple resources is inefficient

---

## ⚡ Synchronous IPC — gRPC

**gRPC** is a binary protocol using Protocol Buffers. It solves REST's verb mapping problem.

```protobuf
// Order Service gRPC API definition
service OrderService {
  rpc createOrder(CreateOrderRequest) returns (CreateOrderReply) {}
  rpc cancelOrder(CancelOrderRequest) returns (CancelOrderReply) {}
  rpc reviseOrder(ReviseOrderRequest) returns (ReviseOrderReply) {}
}

message CreateOrderRequest {
  int64 restaurantId = 1;
  int64 consumerId   = 2;
  repeated LineItem lineItems = 3;
}
```

**Pros**: Rich operations, efficient binary format, bidirectional streaming, strongly typed  
**Cons**: More complex JS clients, older firewalls may not support HTTP/2

---

## 🔒 Pattern: Circuit Breaker

When Service A calls Service B synchronously and B is slow or down, A's threads pile up waiting — eventually A becomes unavailable too. The **Circuit Breaker** prevents this cascade.

```
Circuit Breaker States:

CLOSED (normal)          OPEN (failing)            HALF-OPEN (testing)
┌──────────────┐         ┌──────────────┐           ┌──────────────┐
│ All requests │         │ Requests fail│           │ Test request │
│ pass through │──fault──▶ immediately  │──timeout──▶ passes through│
│              │ rate    │ (fast fail)  │           │              │
└──────────────┘ exceeds └──────────────┘           └──────┬───────┘
                threshold                                   │success
                                                            ▼ CLOSED
```

Three protection mechanisms:
1. **Network timeouts** — never block indefinitely
2. **Limit outstanding requests** — reject if too many pending
3. **Circuit breaker** — trip after N failures, allow recovery after timeout

Library: **Netflix Hystrix** (JVM) or **Polly** (.NET)

---

## 🔍 Service Discovery

In microservices, service instances come and go dynamically. Clients cannot use static IPs.

### Application-Level Discovery (Self Registration + Client-Side Discovery)

```
┌──────────────┐  register  ┌──────────────────┐
│ Service      │──────────▶│ Service Registry  │
│ Instance     │            │ (e.g., Eureka)   │
└──────────────┘            └────────┬─────────┘
                                     │ query
┌──────────────┐  invoke    ┌────────▼─────────┐
│ Client       │◀──────────│ Client Discovery  │
│ Service      │            │ Library           │
└──────────────┘            └──────────────────┘
```

**Patterns used**: Self Registration + Client-Side Discovery  
**Tools**: Netflix Eureka + Ribbon, Spring Cloud  
**Downside**: Language-specific; you need a library per language

### Platform-Provided Discovery (3rd Party Registration + Server-Side Discovery)

```
┌──────────────┐  DNS name  ┌──────────────────┐
│ Client       │──────────▶│ Platform Router  │
│ Service      │            │ (Kubernetes,etc) │
└──────────────┘            └────────┬─────────┘
                                     │ routes to
                            ┌────────▼─────────┐
                            │ Service Instance  │
                            │ (looked up from   │
                            │  registry)        │
                            └──────────────────┘
```

**Patterns used**: 3rd Party Registration + Server-Side Discovery  
**Tools**: Kubernetes, Docker Swarm  
**Advantage**: Language-agnostic; zero application code needed

---

## 📨 Asynchronous Messaging

Messages are sent to **channels**. Senders don't block. Recipients process at their own pace.

```
Message Structure:
┌────────────────────────────┐
│  Header                    │
│  - messageId               │
│  - type (Command/Event/Doc)│
│  - replyTo channel         │
│  - correlationId           │
├────────────────────────────┤
│  Body (JSON, Avro, etc.)   │
└────────────────────────────┘

Channel Types:
  Point-to-Point  → one sender, one receiver (commands)
  Publish-Subscribe → one sender, many receivers (events)
```

### Message Broker Comparison

| Broker | Type | Ordering | Use Case |
|--------|------|----------|---------|
| RabbitMQ | AMQP | Per-queue | General purpose |
| Apache Kafka | Log-based | Per-partition | High throughput, event streaming |
| AWS SQS | Cloud | Best-effort | Simple queueing |
| AWS Kinesis | Cloud | Per-shard | Real-time analytics |

### Competing Consumers + Message Ordering

Problem: Scaling consumers can cause out-of-order processing.

```
Solution: Sharded (Partitioned) Channels

Sender uses shard-key (e.g., orderId) → routes to same partition
Same partition → always processed by same consumer instance

Order events for orderId=123:
  Created → Shard 0 → Consumer A
  Updated → Shard 0 → Consumer A   ✅ in order
  Cancelled → Shard 0 → Consumer A
```

### Handling Duplicate Messages

Most brokers guarantee **at-least-once** delivery — duplicates happen.

```
Strategy 1: Idempotent handlers
  Cancelling an already-cancelled order → harmless

Strategy 2: Track message IDs
  INSERT INTO PROCESSED_MESSAGES (msg_id) VALUES (?)
  → fails on duplicate → safe to discard
```

---

## ⚛️ Pattern: Transactional Outbox

**Problem**: A service updates the database AND publishes a message. If it crashes between the two, the message is lost.

**Solution**: Write the message to an **OUTBOX** table in the same DB transaction. A separate process publishes from the outbox.

```
Order Service:
┌─────────────────────────────────────────────────┐
│  BEGIN TRANSACTION                               │
│    INSERT INTO ORDERS (...)                      │
│    INSERT INTO OUTBOX (type, payload, dest) ...  │
│  COMMIT                                          │
└─────────────────────────────────────────────────┘
        ↑ atomic — both or neither

Message Relay:
┌──────────────────────────────────────────────────┐
│  Poll OUTBOX table (or tail transaction log)     │
│  → Publish each message to broker                │
│  → Delete from OUTBOX                            │
└──────────────────────────────────────────────────┘
```

Two ways to implement the relay:

| Pattern | How | Trade-off |
|---------|-----|-----------|
| **Polling Publisher** | SELECT * FROM OUTBOX periodically | Simple, but has latency + DB load |
| **Transaction Log Tailing** | Read DB commit log (binlog, WAL) | Low latency, but more complex |

Tools: **Debezium** (Kafka), **Eventuate Tram** (open source by the author)

---

## 📈 Improving Availability with Async

**Synchronous calls reduce availability** multiplicatively:

```
If each service is 99.5% available:

  createOrder() → calls Consumer Service + Restaurant Service + Kitchen Service
  = 99.5% × 99.5% × 99.5% = ~98.5% availability

→ Every synchronous call reduces availability
```

**Solution**: Finish processing *after* returning a response

```
Old (synchronous):
Client → Order Service → Consumer Service (sync)
                       → Restaurant Service (sync)
                       → Kitchen Service (sync)

New (async):
1. Order Service creates Order in PENDING state
2. Order Service returns 202 Accepted to client ← immediate response
3. Order Service sends async messages to other services
4. Other services validate and confirm via messages
5. Order transitions to APPROVED state
```

This pattern requires the client to poll or use WebSockets for the final result.

---

## 💡 Key Takeaways

| Insight | Implication |
|---------|-------------|
| Synchronous IPC reduces availability — every call adds a dependency | Prefer async messaging for inter-service calls |
| Circuit Breaker prevents cascade failures | Every synchronous proxy should have one |
| Service discovery is non-trivial in dynamic environments | Use platform-provided discovery (Kubernetes) when possible |
| Transactional outbox solves the dual-write problem | Never publish directly in a transaction; write to outbox first |
| Message ordering is preserved with sharded channels | Use orderId as shard key for order events |
| REST for external APIs; async messaging for internal service collaboration | Mix is fine — but know the trade-offs |

---

*← [Back to Microservices Patterns](../README.md)*
