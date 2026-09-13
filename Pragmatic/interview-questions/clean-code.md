# 🧹 Clean Code & Code Quality — Interview Questions

---

### 1. What makes code maintainable?

**A:** This is a senior-level judgment question — there's no single answer, but maintainability has measurable characteristics:

**1. Readability** — code communicates intent clearly
```python
# UNREADABLE
def p(d, n):
    return [(x[0], x[1] * n) for x in d if x[2]]

# READABLE — same logic, clear intent
def apply_discount(products: list[Product], multiplier: float) -> list[tuple]:
    return [
        (product.name, product.price * multiplier)
        for product in products
        if product.is_eligible_for_discount
    ]
```

**2. Small, focused functions** — each does one thing
**3. Meaningful names** — variables, functions, classes reveal intent
**4. Minimal surprise** — code does what its name suggests
**5. Low coupling** — changes in one place don't ripple everywhere
**6. High test coverage of critical paths** — changes are safe to make
**7. Consistency** — same problems solved the same way throughout

---

### 2. How do you recognize bad code? What are code smells?

**A:**

**Long Method:** Method that does too much — hard to name, hard to test
```python
# 200-line method — split into smaller, named steps
def process_order(order_id):
    # 50 lines of validation
    # 50 lines of payment
    # 50 lines of inventory
    # 50 lines of notification
```

**God Class:** One class that knows and does everything

**Feature Envy:** Method uses data from another class more than its own
```python
class OrderService:
    def process(self, order):
        total = order.customer.address.region.tax_rate * order.subtotal
        # This method is more interested in Customer/Address/Region than Order
```

**Data Clumps:** Same 3-4 variables always appear together → extract to a class
```python
# Instead of: city, state, zip, country (everywhere)
address = Address(city, state, zip, country)
```

**Switch/If-else chains on type:**
```python
if isinstance(payment, CreditCard): ...
elif isinstance(payment, PayPal): ...  # → Strategy or polymorphism
```

**Primitive Obsession:** Using primitives for domain concepts
```python
user_id: str  # what is this? → UserId type
email: str    # → Email value object with validation
money: float  # → Money(amount, currency)
```

**Shotgun Surgery:** One change requires many small changes across many classes → poor cohesion

**Dead Code:** Commented-out code, unused methods, unreachable branches

---

### 3. When is duplication actually better than the wrong abstraction?

**A:** This is one of the best senior-level questions.

**The wrong abstraction is worse than duplication** because:
- Wrong abstractions cause coupling between unrelated things
- Changing one breaks the other
- Abstraction built too early, before understanding patterns

```python
# Two functions that look the same:
def format_shipping_address(address):
    return f"{address.street}, {address.city}, {address.state} {address.zip}"

def format_billing_address(address):
    return f"{address.street}, {address.city}, {address.state} {address.zip}"

# Temptation: extract to format_address(address) — same code!

# But over time they diverge:
# Shipping adds: apartment numbers, delivery instructions
# Billing adds: company name, VAT number, PO Box handling

# If abstracted too early: one change breaks the other, or we add messy conditionals
# Better: keep them separate until the pattern is truly stable

# The "Rule of Three" heuristic:
# 1st time: just do it
# 2nd time: note the duplication, but resist
# 3rd time: now it's worth abstracting
```

**Sandi Metz:** "Duplication is far cheaper than the wrong abstraction."

---

### 4. What makes a good function name?

**A:** A good name is a mini-specification — it tells you what, not how.

```python
# BAD — vague, unhelpful
def process(data): ...
def handle(x): ...
def do_stuff(order): ...
def calc(items, discount): ...

# GOOD — intent is clear
def validate_shipping_address(address: Address) -> ValidationResult: ...
def calculate_discounted_total(items: list[OrderItem], discount: Discount) -> Money: ...
def send_order_confirmation_email(order: Order, recipient: EmailAddress) -> None: ...

# Boolean functions: should read as a question
def is_eligible_for_free_shipping(order: Order) -> bool: ...  # not: check_free_shipping
def has_pending_payments(account: Account) -> bool: ...       # not: pending_payments

# Collections: plural
def find_active_users() -> list[User]: ...   # not: get_user, fetch_user

# Commands vs queries (CQS)
# Commands: do something, no return value
def ship_order(order: Order) -> None: ...
# Queries: return something, no side effects
def get_order_total(order: Order) -> Money: ...
```

---

### 5. What is the Single Responsibility Principle in the context of clean code?

**A:** A function or class should have only one reason to change — it should be about one concept.

```python
# VIOLATION — this function does too many things
def generate_and_send_invoice(order_id: str):
    order = db.get_order(order_id)
    items = "\n".join(f"{i.name}: ${i.price}" for i in order.items)
    html = f"<html><body><h1>Invoice #{order_id}</h1>{items}</body></html>"
    pdf = pdfkit.from_string(html, False)
    smtp = smtplib.SMTP("smtp.gmail.com", 587)
    smtp.sendmail("billing@company.com", order.customer.email, pdf)

# FIXED — three separate concerns
def generate_invoice_html(order: Order) -> str: ...
def convert_html_to_pdf(html: str) -> bytes: ...
def email_pdf(recipient: str, pdf: bytes) -> None: ...

def send_invoice(order: Order) -> None:
    html = generate_invoice_html(order)
    pdf = convert_html_to_pdf(html)
    email_pdf(order.customer.email, pdf)
```

---

### 6. What is refactoring and when should you do it?

**A:** Refactoring changes the structure of existing code without changing its external behavior — making it easier to understand and modify.

**When to refactor:**
- Before adding a feature — make the feature easy to add first
- When fixing a bug — understand the code, then clean it
- During code review — identify smells before they harden
- Boy Scout Rule: leave the code cleaner than you found it

**Common refactoring techniques:**
```python
# Extract Method — too-long function
def checkout(cart):
    # Before: all in one method
    # After: extract into named steps
    validate_cart(cart)
    calculate_totals(cart)
    process_payment(cart)
    send_confirmation(cart)

# Rename Variable — reveals intent
# x → user_age, d → response_body, temp → discounted_price

# Replace Magic Number with Named Constant
# if age > 18 → if age > LEGAL_AGE_OF_MAJORITY

# Extract Class — when one class does too much
# UserService → split into UserAuthService, UserProfileService

# Replace Conditional with Polymorphism
# if type == "X" → subclass or strategy

# Introduce Parameter Object — data clumps
# (city, state, zip, country) → Address
```

---

### 7. What is technical debt?

**A:** Technical debt is the accumulated cost of shortcuts, poor decisions, and deferred refactoring. Like financial debt — compounds over time (interest).

```
Types of technical debt:
  Intentional debt: "We'll clean this up after the launch"
  Unintentional debt: Code that was good at the time but is now outdated
  Incremental debt: Tiny shortcuts that accumulate

Symptoms:
  - "I'm afraid to touch that code"
  - Simple changes take days
  - Bug count grows faster than bug fixing
  - New engineers can't understand the codebase
  - High defect injection rate on changes

How to pay it down:
  - Treat tech debt as work items (backlog)
  - 20% of sprint capacity for debt reduction
  - Refactor before adding features in affected area
  - Boy Scout rule on every PR
  - Never let debt accumulate in critical hot paths
```

---

### 8. What makes code testable?

**A:** Testable code has these properties:

**1. Single Responsibility** — if a function does one thing, there's one thing to test

**2. Dependency Injection** — dependencies can be replaced with test doubles
```python
# UNTESTABLE — hardcoded dependency
class OrderService:
    def process(self, order_id):
        order = MySQLDatabase().get(order_id)  # can't replace this in tests

# TESTABLE — injected dependency
class OrderService:
    def __init__(self, repo: OrderRepository):  # can inject InMemoryOrderRepository in tests
        self.repo = repo

    def process(self, order_id):
        order = self.repo.get(order_id)
```

**3. Pure functions where possible** — given the same input, always returns the same output, no side effects
```python
# Pure — easy to test
def calculate_tax(subtotal: float, rate: float) -> float:
    return subtotal * rate

# Impure — depends on external state
def calculate_tax(order_id: str) -> float:
    order = db.get(order_id)      # external dep
    rate = tax_service.get_rate() # external dep
    return order.subtotal * rate
```

**4. No global state** — global mutable state makes tests order-dependent

**5. Small functions** — fewer edge cases per function, easier to cover

---

### 9. What is the difference between mocking, stubbing, and faking?

**A:**

| Term | What it does | Returns | Verifies |
|------|-------------|---------|----------|
| **Stub** | Provides canned answers | Hardcoded values | No |
| **Mock** | Records calls for verification | Configurable | Yes (was method called?) |
| **Fake** | Working implementation (simplified) | Real computation | No |
| **Spy** | Real object + tracks calls | Real values | Yes |

```python
# Stub — just returns a value
class StubEmailService:
    def send(self, email, message): pass  # does nothing, returns None

# Mock — verifies behavior
mock_email = MagicMock()
service.register(user)
mock_email.send.assert_called_once_with("alice@example.com", ANY)

# Fake — real working implementation (simpler)
class InMemoryUserRepository:
    def __init__(self): self.users = {}
    def save(self, user): self.users[user.id] = user
    def get(self, id): return self.users.get(id)
# Real logic, no DB — fast and deterministic
```

**Guideline:** Prefer fakes for repositories (real behavior without I/O), mocks for verifying collaborator interactions, stubs for simple return values.

---

### 10. What is the difference between unit, integration, and end-to-end tests?

**A:**

```
Test Pyramid:
         /E2E\        ← Few, slow, brittle, high confidence
        /-----\
       / Integ \      ← Some, slower, real infrastructure
      /----------\
     / Unit Tests \   ← Many, fast, isolated

Unit test:
  Tests one unit (function/class) in isolation
  All dependencies mocked/stubbed
  Milliseconds to run
  Tests: business logic, algorithms, edge cases

Integration test:
  Tests multiple units working together
  May use real database, real file system
  Seconds to run
  Tests: DB queries work, API calls return right shape

E2E test:
  Tests complete user flow through the system
  Real infrastructure, real network
  Minutes to run
  Tests: critical user journeys work end-to-end
```

**Anti-patterns:**
- Ice cream cone: mostly E2E (expensive, slow, fragile)
- Testing implementation details (brittle when refactoring)
- No tests in the triangle at all

---

### 11. What is code review and what should you look for?

**A:** Code review is a systematic examination of code before merging, combining knowledge sharing with quality enforcement.

**What to look for:**

```
Correctness:
  □ Does it handle edge cases? (empty input, null, concurrent access)
  □ Are there security vulnerabilities? (injection, auth bypass)
  □ Does it handle errors? (missing try/catch, unchecked errors)

Design:
  □ Does it follow SRP? Is it doing too much?
  □ Are abstractions at the right level?
  □ Does it introduce unnecessary coupling?
  □ Is it consistent with existing patterns?

Readability:
  □ Are names meaningful?
  □ Is it self-documenting? (or needs comments to explain why)
  □ Are complex sections explained?

Tests:
  □ Are there tests for the changed behavior?
  □ Do the tests test the right things (not implementation)?
  □ Are edge cases covered?

Performance:
  □ Any O(n²) in hot paths?
  □ Any N+1 queries?
  □ Any unnecessary allocations?
```

**Code review culture:**
- Review the code, not the person
- Ask questions instead of making demands
- Explain the *why* behind suggestions
- Approve with confidence, not just "LGTM" without reading
