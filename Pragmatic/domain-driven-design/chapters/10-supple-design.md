# Chapter 10 — Supple Design

> *"A supple design yields to the hand—it allows the code to speak for itself, and it invites change."*

---

## 🎯 Core Concept

A **supple design** is one that's easy to work with — easy to understand, easy to change, and easy to extend. It doesn't fight developers; it invites them to build on it. This chapter presents a set of patterns that make designs flexible and expressive.

---

## 🏷️ INTENTION-REVEALING INTERFACES

Name every significant piece of code so that the name communicates **what it does**, not **how it does it**.

```java
// BAD — reveals HOW, not WHAT
public List<Customer> getCustomersByDateRange(Date start, Date end,
        boolean includeInactive, String sortField, int limit) { ... }

// GOOD — reveals WHAT
public List<Customer> findActiveCustomersWithRecentOrders() { ... }

// Even better — Ubiquitous Language names
public List<Customer> findEligibleForRenewalCampaign() { ... }
```

The name should let a developer **use** the object without reading its implementation. If you have to read the code to understand what it does, the interface isn't revealing its intention.

---

## ⚡ SIDE-EFFECT-FREE FUNCTIONS

A **function** (in the functional sense) takes inputs and returns a result without changing any visible state. Methods that both compute something AND change state are dangerous.

```java
// DANGEROUS — side effect + computation mixed
public Money applyDiscount(Customer customer) {
    Money discount = calculateDiscount(customer);  // computation
    customer.setLastDiscountApplied(discount);      // side effect!
    return discount;
}

// SAFE — separated
public Money calculateDiscount(Customer customer) {  // pure function
    return customer.isPremium() ? price.times(0.9) : price;
}

public void recordDiscount(Customer customer, Money discount) {  // explicit side effect
    customer.setLastDiscountApplied(discount);
}
```

**Rule of thumb:** Put as much logic as possible into functions that return results without modifying state. Isolate operations that DO change state so their effects are obvious.

---

## 📋 ASSERTIONS

Make postconditions and invariants explicit. Don't just let them be implied by the code.

```java
public void transferFunds(Account from, Account to, Money amount) {
    from.debit(amount);
    to.credit(amount);
    
    // ASSERTION: explicit postcondition
    assert from.balance().plus(to.balance())
        .equals(originalFromBalance.plus(originalToBalance))
        : "Transfer must preserve total funds";
}
```

When operations have **complex side effects**, assertions document the intended contract. Tests can enforce them. Even comments saying "after this call, X will be true" make the design more communicative.

---

## 📐 CONCEPTUAL CONTOURS

Decompose design elements so that they align with natural "seams" in the domain. Don't split what belongs together; don't force together what doesn't.

```
WRONG CONTOUR (technical split):
  PaymentProcessor.calculateFees()
  PaymentProcessor.validateCard()
  PaymentProcessor.executeCharge()
  PaymentProcessor.sendReceipt()
  → All in one class; artificial boundary

RIGHT CONTOUR (domain seams):
  FeeCalculator.calculateFor(payment)        ← one concept
  CardValidator.validate(cardDetails)         ← one concept  
  ChargeExecutor.execute(payment)             ← one concept
  ReceiptSender.sendFor(completedPayment)     ← one concept
```

Ask: "If the domain changed in this area, which things would change together?" Those things should be in the same unit. Things that change independently should be separate.

---

## 🏝️ STANDALONE CLASSES

Every dependency you add to a class creates cognitive overhead for the reader. Push for classes that can be understood **in isolation**.

```
Complex class (hard to understand):
  Order → Customer → Account → CreditHistory → CreditAgency
  Order → Inventory → Warehouse → SupplyChain → ...
  
  To understand Order, you must understand all of these.

Standalone (understandable alone):
  Money — all operations on itself
  DateRange — start, end, overlaps(), includes()
  Percentage — self-contained arithmetic
```

The goal isn't to eliminate all dependencies, but to minimize them and make the remaining ones explicit.

---

## 🔄 CLOSURE OF OPERATIONS

When possible, define operations whose result is the same type as its inputs.

```java
// Closure of operations on Money:
Money price = new Money(10.00, USD);
Money tax = new Money(0.80, USD);
Money total = price.plus(tax);      // Money.plus(Money) → Money

// You can chain operations naturally:
Money final = price.plus(tax).times(quantity).minus(discount);
```

This is especially powerful for Value Objects. The operations "close over" the type — you stay in the same "space" throughout a computation.

---

## 💡 Key Takeaways

| Pattern | Goal | Key Question |
|---------|------|-------------|
| **Intention-Revealing Interfaces** | Names communicate what, not how | Can you use this without reading its body? |
| **Side-Effect-Free Functions** | Separate computation from state change | Does this method do more than one thing? |
| **Assertions** | Make postconditions explicit | What is guaranteed after this call? |
| **Conceptual Contours** | Align code with domain seams | What changes together? |
| **Standalone Classes** | Minimize dependencies | Can this be understood alone? |
| **Closure of Operations** | Fluent, chainable operations | Does the result type match the input type? |

```
SUPPLE DESIGN CHECKLIST:
  □ Can a developer use this class without reading its implementation?
  □ Are side effects isolated and obvious?
  □ Are important invariants stated explicitly?
  □ Are boundaries aligned with domain concepts?
  □ Can each class be understood without loading the whole system?
  □ Do operations on Values return the same type?
```

---

*← [Back to Domain-Driven Design](../README.md)*
