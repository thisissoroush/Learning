# Chapter 13 — Contracts

> *"A contract is a promise between two parts of a system. Breaking it breaks trust."*

---

## 🎯 Core Concept

In distributed architectures, services communicate through **contracts** — the agreed interface between a consumer and a provider. How strict or loose those contracts are has massive implications for how independently services can evolve. This chapter explores strict vs. loose contracts and a powerful pattern called **stamp coupling**.

---

## 📜 What Is a Contract?

```
Any interface point between two services:
  ✓ REST API endpoint signatures
  ✓ Message queue payload schemas
  ✓ gRPC proto definitions
  ✓ Database schemas (when shared)
  ✓ Event message formats

A contract defines: what data is sent, in what format, 
with what field names and types.
```

---

## 🔒 Strict Contracts

Strict contracts are **tightly defined** — consumer and provider must agree exactly on field names, types, and structure.

```
Provider defines strict JSON schema:
{
  "customerId": "string (required)",
  "orderDate": "ISO-8601 date (required)",
  "totalAmount": "number (required)",
  "currency": "string (required, 3-char ISO code)"
}

Consumer must send exactly this. Any deviation = failure.
```

**Benefits:**
- Clear expectations on both sides
- Easier to validate and test
- Type safety (especially with tools like Protobuf/gRPC)

**Shortcomings:**
- Any change requires coordination across services
- Adding a new field requires consumer changes even if consumer doesn't need it
- Slows down independent evolution of services
- Creates ripple effects when schemas change

---

## 🔓 Loose Contracts

Loose contracts are **tolerant** — consumers only use what they need, providers can add new fields without breaking consumers.

```
Provider adds new field "promotionCode" to response:
  { customerId, orderDate, totalAmount, currency, promotionCode }

Strict contract consumer: BREAKS (unexpected field)
Loose contract consumer: FINE (ignores unknown fields)
```

**The Tolerant Reader Pattern:**
```
Consumer reads only the fields it needs.
Ignores any extra fields it doesn't recognize.
This allows providers to evolve their schema without breaking existing consumers.
```

**Benefits:**
- Services can evolve independently
- Adding fields doesn't break existing consumers
- Providers have more flexibility

**Shortcomings:**
- Less clarity about what's actually required
- Harder to validate (what's optional vs. required?)
- Can lead to "ghost fields" — data sent but never consumed

---

## ⚖️ Strict vs. Loose Trade-Offs

| Dimension | Strict Contracts | Loose Contracts |
|-----------|-----------------|-----------------|
| **Evolutionary independence** | Low | High |
| **Type safety** | High | Low |
| **Change coordination** | Required | Minimal |
| **Validation clarity** | High | Low |
| **Versioning complexity** | High | Low |
| **Best for** | Stable interfaces, external APIs | Internal services, rapid evolution |

---

## 📬 Contracts in Microservices

**Consumer-Driven Contract Testing:**

```
Instead of provider defining the contract unilaterally:
  
  Consumer publishes what it NEEDS from provider
  Provider verifies it satisfies all consumer contracts
  
  Tools: Pact, Spring Cloud Contract

Benefit: Provider knows exactly what consumers depend on,
making it safe to change anything NOT in a consumer contract.
```

---

## 📦 Stamp Coupling

**Stamp coupling** occurs when a service passes a full data structure to another service, even though the receiver only needs a small portion of it.

```
Example of Over-Coupling via Stamp Coupling:
  
  Order Service sends to Shipping Service:
  {
    orderId, customerId, customerName, customerEmail,
    customerCreditScore, orderDate, totalAmount,
    productIds, productNames, unitPrices,
    shippingAddress,    ← Shipping only needs this
    billingAddress,
    paymentMethod,
    loyaltyPoints
  }
  
  Shipping Service only needs: orderId + shippingAddress
  But now it's coupled to the entire Order schema!
```

**Problems with stamp coupling:**
- Any change to Order schema may require Shipping changes
- Shipping has access to data it shouldn't (security concern)
- Larger payloads consume more bandwidth and memory
- Higher cognitive overhead for service developers

**Better approach — send only what's needed:**
```
Order Service → Shipping Service:
  {
    orderId: "12345",
    shippingAddress: { street, city, zip, country }
  }
```

---

## 📡 Bandwidth Implications

```
Stamp coupling at scale:
  
  Order event payload: 4 KB
  Events per second: 10,000
  Services consuming: 15
  
  Total bandwidth: 4 KB × 10,000 × 15 = 600 MB/sec
  
  If each service only needed 0.2 KB:
  Optimized payload: 0.2 KB × 10,000 × 15 = 30 MB/sec
  
  20x bandwidth reduction!
```

---

## 🔀 Stamp Coupling for Workflow Management

One valid use of stamp coupling: **passing a workflow context document** between orchestration steps.

```
Workflow Orchestrator sends to each service:
  {
    workflowId: "wf-789",
    correlationId: "corr-456",
    currentStep: "payment",
    orderData: { ... },  ← full order context
    customerData: { ... }
  }

Each service reads what it needs and passes the document along.
The "stamp" becomes the workflow state carrier.

This is acceptable when:
  - The overhead of individual API calls would be worse
  - The workflow document IS the state
  - All recipients genuinely need parts of the full context
```

---

## 💡 Key Takeaways

| Insight | Implication |
|---------|-------------|
| Strict contracts increase safety but reduce flexibility | Use for external/stable interfaces; avoid for rapidly-evolving internal services |
| Loose contracts enable independent evolution | Implement the Tolerant Reader pattern as a default for internal services |
| Consumer-Driven Contract Testing reverses contract ownership | Consumers define what they need; providers verify they satisfy it |
| Stamp coupling creates hidden dependencies | Send only the data the consumer actually needs |
| Bandwidth matters at scale | Small payload differences multiply enormously with high event volume |

---

*← [Back to Software Architecture: The Hard Parts](../README.md)*
