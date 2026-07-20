# Chapter 9 — Making Implicit Concepts Explicit

> *"Many transformations of domain models and the corresponding code changes are about finding concepts that have been lurking implicitly and making them explicit."*

---

## 🎯 Core Concept

The biggest leaps in model quality come from surfacing **implicit concepts** — things the domain experts understand intuitively but that haven't been named or modeled yet. When you find these hidden concepts and make them explicit objects in the model, complexity often dissolves.

---

## 🔍 How to Find Hidden Concepts

### 1. Listen to Language
When domain experts use a word repeatedly that doesn't appear in your model, that's a signal.

```
Domain expert says:
  "We need to check if the order is eligible..."
  "...only eligible customers can..."
  "...eligibility is determined by..."

Your model has no "Eligibility" object → it's implicit!
Make it explicit: class EligibilityPolicy { ... }
```

### 2. Scrutinize Awkwardness
When the code for a concept is spread across multiple objects, or when a method feels like it doesn't belong, something implicit is trying to surface.

```
AWKWARD (implicit concept):
  if (customer.getAccountAge() > 30 
      && customer.getPaymentHistory().hasNoDefaults()
      && customer.getCreditScore() > 700) {
    // grant premium access
  }

EXPLICIT (concept surfaced):
  if (premiumEligibilityPolicy.isSatisfiedBy(customer)) {
    // grant premium access
  }
```

### 3. Contemplate Contradictions
When domain experts disagree or give conflicting rules, there's often a missing concept that reconciles them.

### 4. Read Domain Literature
Books, papers, and industry standards often contain the concepts you need, already named and defined.

---

## 📐 SPECIFICATION Pattern

One of the most powerful implicit concepts to make explicit is **business rules that determine whether something qualifies**.

A **Specification** is an object that encapsulates a business rule and can answer yes/no about whether a domain object satisfies it.

```java
// Before: rule buried in application code
public List<Customer> getOverdueCustomers() {
    List<Customer> result = new ArrayList<>();
    for (Customer c : customers) {
        if (c.getBalance() < 0 && 
            c.getDaysSinceLastPayment() > 30) {
            result.add(c);
        }
    }
    return result;
}

// After: Specification makes the rule explicit
public class OverdueCustomerSpec implements Specification<Customer> {
    public boolean isSatisfiedBy(Customer customer) {
        return customer.getBalance() < 0 
            && customer.getDaysSinceLastPayment() > 30;
    }
}

// Usage: readable, reusable, testable
List<Customer> overdue = customerRepo.findSatisfying(overdueSpec);
```

**Three uses of Specification:**

| Use | Description | Example |
|-----|-------------|---------|
| **Validation** | Check if an object satisfies a rule | "Is this order valid?" |
| **Selection** | Filter a collection | "Find all overdue invoices" |
| **Construction** | Describe what needs to be created | "Build a Cargo that goes to Rotterdam" |

**Composing Specifications:**

```java
Specification<Customer> premium = new PremiumCustomerSpec();
Specification<Customer> overdue = new OverdueSpec();

// Composite specs
Specification<Customer> premiumAndOverdue = premium.and(overdue);
Specification<Customer> premiumOrNew = premium.or(new NewCustomerSpec());
Specification<Customer> notPremium = premium.not();
```

---

## 🔒 Explicit Constraints

Some constraints are buried in methods as guard clauses. Making them explicit objects or methods gives them visibility and a name.

```java
// BEFORE: constraint buried in method
public void addItem(LineItem item) {
    if (items.size() >= maxItems) 
        throw new IllegalStateException();
    if (totalAmount() + item.amount() > creditLimit)
        throw new CreditLimitExceededException();
    items.add(item);
}

// AFTER: constraints are named
private void checkOrderConstraints(LineItem item) {
    assertWithinItemLimit(item);
    assertWithinCreditLimit(item);
}
```

---

## 💡 Key Takeaways

| Technique | When to Use |
|-----------|-------------|
| Listen to language | When experts use a term your model doesn't have |
| Scrutinize awkwardness | When code for one concept is spread across multiple objects |
| Specification pattern | When validation, filtering, or selection rules appear in multiple places |
| Explicit constraints | When business rules are buried in method bodies |

```
IMPLICIT → EXPLICIT transformation:
  
  Hidden rule in code    →  Named Specification object
  Guard clause           →  Explicit constraint method  
  Repeated if-statement  →  Policy object
  Expert jargon ignored  →  Model concept with that name
```

---

*← [Back to Domain-Driven Design](../README.md)*
