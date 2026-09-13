# 🧩 Object-Oriented Programming — Interview Questions

Language-agnostic OOP concepts. Examples use pseudocode or multiple languages.

---

### 1. What are the four pillars of OOP and what do they actually mean?

**A:**

| Pillar | Core idea | Common misunderstanding |
|--------|-----------|------------------------|
| **Encapsulation** | Bundle data + behavior; hide internals | "Just making fields private" |
| **Abstraction** | Expose only what's needed; hide complexity | Confused with encapsulation |
| **Inheritance** | Reuse and extend behavior from parent | Inheritance = code reuse (wrong: it's for substitutability) |
| **Polymorphism** | Same interface, different behavior | Only runtime polymorphism counts (compile-time also exists) |

---

### 2. What is the difference between Encapsulation and Abstraction?

**A:**

- **Encapsulation** — *how* we hide: bundling data and methods, using access modifiers. A mechanism.
- **Abstraction** — *what* we hide: hiding implementation details behind a simpler interface. A concept.

```python
class BankAccount:
    # Encapsulation: _balance is private, only accessible via methods
    def __init__(self):
        self._balance = 0.0
        self._transactions = []

    # Abstraction: caller only sees deposit/withdraw/balance
    # They have no idea about _transactions, internal validation, audit logic
    def deposit(self, amount: float):
        self._validate_amount(amount)
        self._balance += amount
        self._transactions.append(("deposit", amount))

    @property
    def balance(self) -> float:
        return self._balance

    def _validate_amount(self, amount):  # hidden detail
        if amount <= 0: raise ValueError("Amount must be positive")
```

---

### 3. What is polymorphism and what are its types?

**A:**

**Subtype (runtime) polymorphism** — the most important kind in OOP:
```java
class Animal { void speak() { System.out.println("..."); } }
class Dog extends Animal { @Override void speak() { System.out.println("Woof!"); } }
class Cat extends Animal { @Override void speak() { System.out.println("Meow!"); } }

Animal a = new Dog();
a.speak();  // "Woof!" — determined at runtime by actual type
```

**Parametric polymorphism (generics):**
```java
List<String> strings = new ArrayList<>();
List<Integer> ints = new ArrayList<>();
// Same List code works for any type
```

**Ad-hoc polymorphism (overloading):**
```java
void log(String msg) { ... }
void log(int code, String msg) { ... }
void log(Exception e) { ... }
// Same name, different signatures — resolved at compile time
```

---

### 4. What is the difference between Inheritance and Composition?

**A:**

**Inheritance** — "is-a" relationship. Subclass *is a* superclass.
```python
class Vehicle:
    def refuel(self): ...

class Car(Vehicle):
    def drive(self): ...
    # Car IS-A Vehicle — gets refuel() automatically
```

**Composition** — "has-a" relationship. Object *contains* another object.
```python
class Engine:
    def start(self): ...

class Brakes:
    def apply(self): ...

class Car:
    def __init__(self):
        self.engine = Engine()  # Car HAS-A Engine
        self.brakes = Brakes()  # Car HAS-A Brakes

    def drive(self):
        self.engine.start()
```

**Why composition is often better:**
- Inheritance couples child to parent's internals
- Deep hierarchies become rigid and fragile
- Composition is flexible — swap components at runtime
- Multiple inheritance causes diamond problem; multiple composition is fine

---

### 5. What is the difference between Association, Aggregation, and Composition?

**A:** All three describe relationships between objects, but with different ownership and lifecycle implications:

```
Association — objects know about each other, no ownership
  Teacher ──── Student (teacher can have multiple students, student can have multiple teachers)
  Lifecycle: independent — deleting teacher doesn't affect students

Aggregation — one contains the other, but contained can exist independently
  Department ◇──── Employee (department has employees, but employee can exist without department)
  Lifecycle: independent — deleting department doesn't delete employees

Composition — one owns the other; contained cannot exist independently
  House ◆──── Room (rooms belong to a specific house)
  Lifecycle: dependent — deleting house deletes its rooms
```

```python
# Composition — Room cannot exist without House
class House:
    def __init__(self):
        self.rooms = [Room("living"), Room("bedroom")]  # created AND destroyed with House

# Aggregation — Employee can exist without Department
class Department:
    def __init__(self, employees: list[Employee]):  # employees created externally
        self.employees = employees
```

---

### 6. What is virtual dispatch and how does it work?

**A:** Virtual dispatch is the mechanism by which the runtime determines which method implementation to call based on the actual type of the object, not the declared type.

```
vtable (virtual function table) — each class has a pointer table:

Animal vtable:     Dog vtable:       Cat vtable:
  speak → Animal::speak  speak → Dog::speak    speak → Cat::speak

Animal* a = new Dog();
a->speak();
// 1. Follow pointer to Dog object
// 2. Look up speak in Dog's vtable
// 3. Call Dog::speak
// Determined at RUNTIME — not at compile time
```

```csharp
class Animal { public virtual void Speak() { Console.Write("..."); } }
class Dog : Animal { public override void Speak() { Console.Write("Woof"); } }

Animal a = new Dog();
a.Speak();  // "Woof" — virtual dispatch to Dog.Speak

// Non-virtual (no override):
class Cat : Animal { public new void Speak() { Console.Write("Meow"); } } // hides, not overrides
Animal c = new Cat();
c.Speak();  // "..." — resolved at compile time by declared type, NOT runtime type
```

---

### 7. When should you use an interface vs an abstract class?

**A:**

| Use Interface when | Use Abstract Class when |
|-------------------|------------------------|
| Defining a contract multiple unrelated types must fulfill | Sharing code + defining contract for closely related types |
| Multiple "inheritance" needed | One inheritance hierarchy is sufficient |
| No shared state or implementation | Some default implementation to share |
| Defining a role/capability (Printable, Serializable) | Defining a family (Animal → Dog, Cat) |

```java
// Interface — unrelated types, defines capability
interface Serializable { byte[] serialize(); }
// User, Order, Config can all implement it — nothing in common otherwise

// Abstract class — family with shared behavior
abstract class Shape {
    protected String color;  // shared state

    public abstract double area(); // must implement

    public String describe() {    // shared implementation
        return color + " shape with area " + area();
    }
}
```

**Modern rule (Java 8+, C# 8+):** Interfaces can have default implementations, so the distinction is less sharp. Still prefer interfaces — they don't restrict the inheritance hierarchy.

---

### 8. What is an Anemic Domain Model vs a Rich Domain Model?

**A:** A classic debate from Domain-Driven Design:

**Anemic Domain Model (anti-pattern):**
```python
# Data bag with no behavior
class Order:
    customer_id: str
    items: list
    status: str
    total: float
    # No methods — just data

# All logic in a separate service (procedural disguised as OOP)
class OrderService:
    def confirm(self, order: Order):
        if order.status != "pending": raise ValueError()
        order.status = "confirmed"
        order.total = sum(i.price * i.qty for i in order.items)
        self.repo.save(order)
```

**Rich Domain Model:**
```python
class Order:
    def __init__(self, customer_id: str):
        self._customer_id = customer_id
        self._items: list[OrderItem] = []
        self._status = OrderStatus.PENDING

    def add_item(self, product: Product, qty: int):
        if self._status != OrderStatus.PENDING:
            raise DomainError("Cannot add items to a confirmed order")
        self._items.append(OrderItem(product, qty))

    def confirm(self):
        if not self._items:
            raise DomainError("Cannot confirm empty order")
        self._status = OrderStatus.CONFIRMED
        # Invariants enforced by the object itself

    @property
    def total(self) -> float:
        return sum(i.total for i in self._items)
```

Rich model: domain logic lives *with* the data it operates on. Harder to achieve, but makes invariants easier to enforce.

---

### 9. What is Immutability and why does it matter?

**A:** An immutable object cannot be modified after construction. Any "change" produces a new object.

```java
// Mutable — dangerous in concurrent environments
class MutablePoint {
    public int x, y;
}

// Immutable — safe to share across threads, easy to reason about
final class ImmutablePoint {
    private final int x, y;

    public ImmutablePoint(int x, int y) { this.x = x; this.y = y; }
    public int x() { return x; }
    public int y() { return y; }

    public ImmutablePoint withX(int newX) { return new ImmutablePoint(newX, y); } // new object
    public ImmutablePoint translate(int dx, int dy) { return new ImmutablePoint(x+dx, y+dy); }
}
```

**Benefits of immutability:**
- Thread-safe by construction — no synchronization needed
- Safe to share references — callers can't mutate your state
- Easy to reason about — value never changes after creation
- Value objects (Money, Email, UUID) should always be immutable

---

### 10. What is a Value Object?

**A:** An object that represents a descriptive aspect of the domain with no conceptual identity. Two value objects with the same values are equal.

```csharp
// Entity — has identity (same ID = same thing, even if properties differ)
class Customer {
    public Guid Id { get; }  // identity
    public string Name { get; set; }
}

// Value Object — no identity (equal if values are equal)
record Money(decimal Amount, string Currency)
{
    public Money Add(Money other) {
        if (Currency != other.Currency) throw new ArgumentException("Currency mismatch");
        return new Money(Amount + other.Amount, Currency);
    }
}

var a = new Money(100, "USD");
var b = new Money(100, "USD");
a == b;  // true — same values = same value object

// Value objects should be:
// 1. Immutable
// 2. Equality by value (not reference)
// 3. Self-validating (constructor rejects invalid state)
// 4. Side-effect-free operations return new instances
```

---

### 11. Why would you prefer composition over inheritance? (Senior-level answer)

**A:** This question tests deep understanding, not just pattern recall.

**1. Inheritance is the strongest coupling in OOP.** The subclass is tightly coupled to the parent's implementation. When the parent changes, the subclass may silently break.

**2. Inheritance violates encapsulation.** The subclass can see and depend on the parent's protected members — internal implementation details leak down.

**3. The fragile base class problem.** Adding a method to a base class can break subclasses in unexpected ways (method name collision, changed behavior).

**4. Inheritance is static.** Behavior is determined at compile time. Composition can be changed at runtime.

**5. The "banana-gorilla-jungle" problem.** You wanted a banana but got the gorilla holding it and the entire jungle.

```python
# Inheritance trap:
class List:
    def add(self, item): ...
    def add_all(self, items): ...  # calls add() internally

class CountingList(List):
    count = 0
    def add(self, item):
        self.count += 1
        super().add(item)
    # Problem: add_all calls add() → double counting!

# Composition avoids this entirely:
class CountingList:
    def __init__(self):
        self._list = []
        self.count = 0

    def add(self, item):
        self.count += 1
        self._list.append(item)
```

---

### 12. What is the difference between method overriding and method overloading?

**A:**

```java
class Calculator {
    // OVERLOADING — same name, different signatures (compile-time polymorphism)
    int add(int a, int b)           { return a + b; }
    double add(double a, double b)  { return a + b; }  // different param types
    int add(int a, int b, int c)    { return a + b + c; } // different param count
}

class ScientificCalculator extends Calculator {
    // OVERRIDING — same signature, different implementation (runtime polymorphism)
    @Override
    int add(int a, int b) {
        log("adding " + a + " and " + b);
        return super.add(a, b);
    }
}
```

| | Overloading | Overriding |
|--|------------|-----------|
| Resolution | Compile time | Runtime (virtual dispatch) |
| Signatures | Must differ | Must be identical |
| Access modifier | Can differ freely | Can only widen (protected → public) |
| Return type | Can differ | Must be same (or covariant) |
| `@Override` | Not applicable | Use it always |
