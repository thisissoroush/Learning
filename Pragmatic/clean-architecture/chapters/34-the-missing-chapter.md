# Chapter 34 — The Missing Chapter

> *"The devil is in the implementation details."*  
> — Simon Brown

---

## 🎯 Core Concept

Good intentions can be destroyed by poor implementation choices. This chapter (by Simon Brown) shows that **how you organize and encapsulate code matters as much as the architectural vision itself**.

---

## 📦 Four Code Organization Approaches

### 1. Package by Layer (Horizontal)
```
com.myapp.web        → OrdersController
com.myapp.service    → OrdersService, OrdersServiceImpl
com.myapp.repository → OrdersRepository, JdbcOrdersRepository
```
- ✅ Simple, familiar  
- ❌ Doesn't scream business domain  
- ❌ Easy to accidentally bypass layers

### 2. Package by Feature (Vertical)
```
com.myapp.orders → OrdersController, OrdersService, 
                   OrdersServiceImpl, OrdersRepository,
                   JdbcOrdersRepository
```
- ✅ Groups by business concept  
- ✅ Easier to find all order-related code  
- ❌ Less separation of concerns within the feature

### 3. Ports and Adapters
```
com.myapp.domain           → Orders (interface), OrdersService
com.myapp.infrastructure   → OrdersController, JdbcOrdersRepository
```
- ✅ Inside (domain) independent of outside (infrastructure)  
- ✅ Clean boundaries between core and delivery mechanism  
- ❌ Possible "Périphérique anti-pattern" — infra code calling infra code

### 4. Package by Component
```
com.myapp.web        → OrdersController (public)
com.myapp.orders     → OrdersComponent (public interface)
                       OrdersServiceImpl (package-private)
                       JdbcOrdersRepository (package-private)
```
- ✅ Single entry point per component  
- ✅ Compiler enforces architectural rules  
- ✅ Stepping stone toward microservices

---

## 🔑 The Critical Insight: Encapsulation vs Organization

```java
// ❌ All types public = packages are just folders, zero encapsulation
public class JdbcOrdersRepository { ... }
public class OrdersServiceImpl { ... }

// ✅ Limit visibility — compiler enforces architecture
class JdbcOrdersRepository { ... }       // package-private
class OrdersServiceImpl { ... }          // package-private
public interface OrdersComponent { ... } // only this is visible
```

**If everything is `public`, all four approaches become identical** — just a layered architecture with no real boundaries.

---

## 📊 Visibility Comparison

| Approach | Can be package-private |
|----------|----------------------|
| Package by Layer | Impl classes only |
| Package by Feature | Almost everything except controller |
| Ports & Adapters | Impl classes only |
| Package by Component | Everything except the component interface |

---

## 💡 Key Takeaways

- Code organization + proper access modifiers = real architectural enforcement
- Use the compiler to enforce architecture — don't rely on discipline alone
- Over-using `public` makes all architectural approaches equivalent (bad)
- "Package by component" gives the strongest compiler-enforced boundaries in a monolith
- Think about decoupling mode: source-level, deployment-level, or service-level
- The missing advice: **think about how your architecture maps to code, and use language features to enforce it**

---

*← [Back to Clean Architecture](../README.md)*
