# Chapter 20 — Business Rules

> *"Business rules are the reason a software system exists. They are the core functionality — the family jewels."*

---

## 🎯 Core Concept

Business rules are the rules and procedures that **make or save money**. They are the most important part of a system and must be protected from contamination by UI, database, or framework details.

---

## 🏛️ Two Types of Business Rules

### 1. Critical Business Rules (Entities)
- Rules that exist **regardless of automation**
- Example: A bank charges N% interest on a loan — this rule exists whether calculated by computer or abacus
- Encapsulated in **Entities** (objects with data + behavior)

```
Loan Entity:
  - principal
  - rate
  - period
  
  Methods:
  - makePayment()
  - applyInterest()
  - chargeLateFee()
```

Entities are **pure business** — no mention of DB, UI, or HTTP.

### 2. Application-Specific Rules (Use Cases)
- Rules that govern **how the automated system operates**
- Example: Don't show loan payment estimates until credit score ≥ 500
- Encapsulated in **Use Cases** (orchestrators of Entities)

```
Use Case: CreateLoan
  Input:  ContactInfo, CreditScore, LoanAmount
  Output: LoanEstimate or Error
  
  Steps:
  1. Validate contact info
  2. Check credit score ≥ 500
  3. Delegate to Loan entity for calculations
  4. Return estimate
```

---

## 🔄 Dependency Direction

```
Use Cases ──depend on──> Entities
UI/DB     ──depend on──> Use Cases
```

Entities know nothing about Use Cases. Use Cases know nothing about UI or DB.

---

## 📨 Request & Response Models

Use Cases accept simple **request data structures** and return simple **response data structures** — never framework objects like `HttpRequest` or database rows.

---

## 💡 Key Takeaways

- **Entities** = Critical Business Rules + Critical Business Data
- **Use Cases** = Application-specific orchestration rules
- Both must be isolated from UI, database, frameworks
- Keep business rules **independent and reusable**

---

*← [Back to Clean Architecture](../README.md)*
