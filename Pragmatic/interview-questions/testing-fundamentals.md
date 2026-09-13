# 🧪 Testing Fundamentals — Interview Questions

Language-agnostic testing concepts that apply across frameworks.

---

### 1. What is the test pyramid?

**A:** The test pyramid describes the ideal distribution of tests by type — more fast/cheap tests at the bottom, fewer slow/expensive tests at the top.

```
          /\
         /E2E\           5%  — Slow, brittle, expensive, high confidence
        /------\
       /Contract\        5%  — Consumer-driven API contracts
      /----------\
     / Integration\      20% — Real infrastructure (DB, cache, queues)
    /--------------\
   /   Unit Tests   \    70% — Fast, isolated, many
  /------------------\

Anti-patterns:
  Ice cream cone:  mostly E2E, few unit (expensive, slow CI)
  Testing trophy:  more integration than unit (acceptable if fast infra)
  No tests:        relying on manual QA (fragile)
```

---

### 2. What is the difference between unit, integration, and E2E tests?

**A:**

```
Unit test:
  Tests one unit (function/class) in isolation
  All dependencies replaced with test doubles
  Speed: milliseconds
  Focus: algorithm correctness, business logic, edge cases

Integration test:
  Tests multiple units working together
  May use real database, real cache, real file system
  Speed: seconds
  Focus: DB queries work, caches invalidate, events publish

End-to-End (E2E) test:
  Tests a complete user flow through the entire system
  Real infrastructure, real network, browser automation
  Speed: minutes
  Focus: critical user journeys work (checkout, login, payment)

What each catches:
  Unit: logic errors, edge cases, algorithmic bugs
  Integration: ORM mapping errors, SQL correctness, message serialization
  E2E: routing errors, auth failures, environment-specific bugs
```

---

### 3. What is Test-Driven Development (TDD)?

**A:** Write the test first, then write the minimum code to make it pass, then refactor.

```
RED → GREEN → REFACTOR

RED:    Write a failing test (defines desired behavior)
GREEN:  Write minimum code to make test pass (even if ugly)
REFACTOR: Clean up without breaking the test

Benefits:
  - Forces you to think about design before implementation
  - Results in 100% testable code (you write tests first, so code is always testable)
  - Tests document intended behavior
  - Refactoring is safe (tests catch regressions)

Example TDD cycle:
  1. Write: test_add_negative_numbers()  → RED (function doesn't exist)
  2. Write: def add(a, b): return a + b  → GREEN
  3. Refactor: add type hints, docstring  → still GREEN
  4. Write: test_add_overflow()          → RED
  5. Handle overflow in add()            → GREEN
  6. Repeat
```

---

### 4. What is the Arrange-Act-Assert (AAA) pattern?

**A:**

```python
def test_order_total_with_discount():
    # ARRANGE — set up test data, mocks, initial state
    items = [
        OrderItem(product=Product("Widget", price=100), quantity=2),
        OrderItem(product=Product("Gadget", price=50),  quantity=1),
    ]
    order = Order(items=items)
    discount = Discount(percentage=10)  # 10% off

    # ACT — execute the behavior being tested
    total = order.calculate_total(discount)

    # ASSERT — verify the expected outcome
    assert total == 225.0  # (200 + 50) * 0.9

# One test = one behavior = clear failure messages
# If test fails at arrange: test setup problem
# If test fails at act: invocation problem
# If test fails at assert: logic problem
```

---

### 5. What are test doubles? Mocks, stubs, fakes, and spies?

**A:**

```
Test Double: generic term for any replacement for a real dependency in a test

Stub:  Returns a hardcoded value. No verification.
       "When asked, return 42"
       Use: simple responses, no need to verify calls

Mock:  Verifies expected behavior. Was it called? With what args?
       "Expect exactly one call to send() with this email address"
       Use: verifying side effects (emails sent, events published)

Fake:  Working, simplified implementation. Real behavior, test-friendly.
       InMemoryRepository — stores in a dict instead of DB
       Use: repositories, caches — real behavior without I/O

Spy:   Wraps a real object, records calls while letting them through.
       Use: when you need real behavior AND want to verify calls

Dummy: Placeholder passed to satisfy signature but never actually used.
       Use: required parameters that don't affect the test
```

---

### 6. What is the difference between black-box and white-box testing?

**A:**

```
Black-box testing: test behavior without knowing internals
  Input → [?????] → Output
  "Given valid order, expect confirmation email"
  "Given invalid card, expect 422 response"
  Tests: what the system DOES, not HOW it does it
  Advantages: tests don't break on refactoring, aligns with user perspective

White-box testing: test with knowledge of internals
  Input → [known code path] → Output
  "Verify that the cache is checked before the DB"
  "Verify that retry is called exactly 3 times"
  Advantages: can test specific paths, edge cases
  Disadvantages: brittle (breaks when implementation changes)

Rule of thumb:
  Prefer black-box (test behavior, not implementation)
  Use white-box for complex algorithms where internal state matters
  Test behavior, not implementation details
```

---

### 7. What is property-based testing?

**A:** Instead of writing specific examples, define properties that must hold for all inputs. A framework generates random inputs to find counterexamples.

```python
from hypothesis import given, strategies as st

# Traditional: test specific examples
def test_reverse_example():
    assert reverse("hello") == "olleh"

# Property-based: define invariants that hold for ALL strings
@given(st.text())
def test_reverse_is_its_own_inverse(s: str):
    assert reverse(reverse(s)) == s  # true for any string

@given(st.integers(), st.integers())
def test_add_is_commutative(a: int, b: int):
    assert add(a, b) == add(b, a)  # must hold for any integers

@given(st.lists(st.integers(), min_size=1))
def test_sort_preserves_length(lst: list):
    assert len(sort(lst)) == len(lst)  # length unchanged

# Framework generates hundreds of random inputs, finds edge cases you'd never think of
# Common findings: empty string, negative numbers, unicode, overflow
```

---

### 8. What is contract testing?

**A:** Tests that verify the interface between two services (consumer and provider) matches expectations. Prevents integration failures.

```
Consumer-Driven Contract Testing:
  Consumer defines expectations (contract): "I expect GET /orders/{id} to return {id, total, status}"
  Provider verifies: "Does my API satisfy this contract?"

Without contract testing:
  Provider changes response shape → Consumer breaks → Discovered in production

With contract testing:
  Provider CI runs consumer contracts → Fails if contract broken → Never reaches production

Tools: Pact, Spring Cloud Contract

Flow:
  1. Consumer writes test → generates pact file (contract)
  2. Pact file published to Pact Broker
  3. Provider pulls pact files → runs verification
  4. Provider CI fails if any consumer contract violated
  5. Safe to deploy: consumer and provider are compatible
```

---

### 9. What is mutation testing?

**A:** Automatically introduces bugs ("mutations") into code and checks if tests catch them. Measures test quality, not just coverage.

```
Original code:
  if order.total > 100:
      apply_free_shipping(order)

Mutation 1 (operator change):
  if order.total >= 100:  ← changed > to >=
  → Test suite catches this? If not: test gap

Mutation 2 (condition negation):
  if not (order.total > 100):
  → Test suite catches this? If not: test gap

Mutation 3 (return value):
  return False  # instead of returning actual result
  → Test suite catches this?

Mutation score = killed_mutations / total_mutations
High score (>80%): tests are effective
Low score: coverage looks good but tests don't verify behavior

Tools: PIT (Java), mutmut (Python), Stryker (JS)
```

---

### 10. What makes tests maintainable?

**A:**

```
1. Test behavior, not implementation
   BAD:  assert mock_repo.save.call_count == 1  (brittle)
   GOOD: assert db.get_order(order_id).status == "confirmed"  (black-box)

2. One assertion per test (approximately)
   Multiple assertions → multiple reasons to fail → unclear which is the problem

3. Descriptive test names that document behavior
   BAD:  test_order()
   GOOD: test_order_total_includes_tax_when_customer_is_in_taxable_region()

4. DRY test setup via fixtures, not copy-paste
   Shared setup → one place to update when model changes

5. Don't share state between tests
   Each test creates its own data → tests are independent → run in any order

6. Don't test third-party libraries
   Test YOUR code that uses the library, not the library itself

7. Delete tests when they stop adding value
   A test that always passes, never fails, and is hard to understand → delete it

8. Fast tests = tests that run
   Slow tests → skipped locally → run only in CI → problems found late
   Keep unit tests under 100ms, integration under 5s
```
