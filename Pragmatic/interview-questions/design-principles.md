# 🧱 Software Design Principles — Interview Questions

Language-agnostic. Questions test understanding of *why* a principle exists, not just its definition.

---

### 1. What is the Single Responsibility Principle (SRP)?

**A:** A class (or module, function) should have only one reason to change — it should do one thing and do it well.

```python
# VIOLATION — UserService does authentication, email, AND persistence
class UserService:
    def register(self, email, password):
        hashed = bcrypt.hash(password)          # auth logic
        user = self.db.insert(email, hashed)    # persistence logic
        self.smtp.send(email, "Welcome!")        # email logic
        return user

# FIXED — each class has one reason to change
class PasswordHasher:
    def hash(self, password): return bcrypt.hash(password)

class UserRepository:
    def save(self, user): return self.db.insert(user)

class WelcomeEmailSender:
    def send(self, email): self.smtp.send(email, "Welcome!")

class UserRegistrationService:
    def register(self, email, password):
        user = User(email, self.hasher.hash(password))
        self.repo.save(user)
        self.email_sender.send(email)
        return user
```

**The "reason to change" framing matters:** if marketing changes email copy AND compliance changes password hashing rules, a single class would change for two unrelated reasons.

---

### 2. What is the Open/Closed Principle (OCP)?

**A:** Software entities should be **open for extension, closed for modification** — add new behavior without changing existing code.

```java
// VIOLATION — every new payment type requires modifying PaymentProcessor
class PaymentProcessor {
    void process(Payment p) {
        if (p.type == "credit_card") chargeCreditCard(p);
        else if (p.type == "paypal") chargePayPal(p);
        else if (p.type == "crypto") chargeCrypto(p); // modify every time
    }
}

// FIXED — new types extend without touching existing code
interface PaymentStrategy {
    void process(Payment payment);
}

class CreditCardStrategy implements PaymentStrategy { ... }
class PayPalStrategy implements PaymentStrategy { ... }
class CryptoStrategy implements PaymentStrategy { ... } // just add new class

class PaymentProcessor {
    private final PaymentStrategy strategy;
    void process(Payment p) { strategy.process(p); } // never changes
}
```

---

### 3. What is the Liskov Substitution Principle (LSP)?

**A:** Objects of a subtype must be substitutable for objects of their supertype without altering the correctness of the program.

```csharp
// VIOLATION — Square breaks Rectangle's contract
class Rectangle {
    public virtual int Width  { get; set; }
    public virtual int Height { get; set; }
    public int Area() => Width * Height;
}

class Square : Rectangle {
    public override int Width  { set { base.Width = base.Height = value; } }
    public override int Height { set { base.Width = base.Height = value; } }
}

// Code that works with Rectangle breaks with Square
void Test(Rectangle r) {
    r.Width = 5;
    r.Height = 3;
    // Caller expects Area() == 15
    // With Square: Area() == 9 — contract violated!
}

// FIX — don't inherit, model correctly
interface IShape { int Area(); }
class Rectangle : IShape { ... }
class Square    : IShape { ... }
```

**LSP violation signals:** subclass throws `NotImplementedException`, overrides to do nothing, or weakens postconditions.

---

### 4. What is the Interface Segregation Principle (ISP)?

**A:** Clients should not be forced to depend on interfaces they do not use. Prefer many small, focused interfaces over one large one.

```go
// VIOLATION — large interface forces implementors to implement unused methods
type Worker interface {
    Work()
    Eat()
    Sleep()
}

type Robot struct{}
func (r Robot) Work()  { /* works */ }
func (r Robot) Eat()   { panic("robots don't eat") }  // forced to implement
func (r Robot) Sleep() { panic("robots don't sleep") } // forced to implement

// FIXED — segregated interfaces
type Workable interface { Work() }
type Eatable  interface { Eat() }
type Sleepable interface { Sleep() }

type Human struct{}
func (h Human) Work()  { ... }
func (h Human) Eat()   { ... }
func (h Human) Sleep() { ... }

type Robot struct{}
func (r Robot) Work() { ... }  // only implements what it needs
```

---

### 5. What is the Dependency Inversion Principle (DIP)?

**A:** High-level modules should not depend on low-level modules. Both should depend on abstractions. Abstractions should not depend on details.

```typescript
// VIOLATION — OrderService (high-level) directly depends on MySQLDatabase (low-level)
class OrderService {
    private db = new MySQLDatabase(); // concrete dependency

    createOrder(order: Order): void {
        this.db.save(order); // tied to MySQL forever
    }
}

// FIXED — both depend on abstraction
interface OrderRepository {
    save(order: Order): void;
    findById(id: string): Order | null;
}

class MySQLOrderRepository implements OrderRepository { ... }
class InMemoryOrderRepository implements OrderRepository { ... } // for tests

class OrderService {
    constructor(private readonly repo: OrderRepository) {} // abstraction

    createOrder(order: Order): void {
        this.repo.save(order); // works with any implementation
    }
}
```

---

### 6. What is DRY and when is duplication actually better than abstraction?

**A:** **Don't Repeat Yourself** — every piece of knowledge should have a single, unambiguous, authoritative representation.

```python
# VIOLATION — duplication
def validate_user_email(email):
    if "@" not in email: raise ValueError("invalid")
    if len(email) > 255: raise ValueError("too long")

def validate_order_email(email):
    if "@" not in email: raise ValueError("invalid")  # duplicate knowledge
    if len(email) > 255: raise ValueError("too long")

# FIXED
def validate_email(email):
    if "@" not in email: raise ValueError("invalid")
    if len(email) > 255: raise ValueError("too long")
```

**When duplication is better:**
- Two pieces of code that *happen* to look the same but represent different concepts — coupling them creates the wrong abstraction
- The "Rule of Three": wait until you see three instances before abstracting
- Early abstraction is often wrong; wait for the right abstraction to emerge
- Sandi Metz: "duplication is far cheaper than the wrong abstraction"

---

### 7. What is KISS and how do you recognize a violation?

**A:** **Keep It Simple, Stupid** — prefer the simplest solution that works. Complexity is the enemy of maintainability.

```python
# VIOLATION — over-engineered
class TemperatureConverterFactory:
    def create_converter(self, unit_type):
        if unit_type == "celsius_to_fahrenheit":
            return CelsiusToFahrenheitConverter()
        # ...

class CelsiusToFahrenheitConverter(AbstractTemperatureConverter):
    def convert(self, value):
        return value * 9/5 + 32

# SIMPLE — just a function
def celsius_to_fahrenheit(c):
    return c * 9/5 + 32
```

**Signs of KISS violation:**
- Classes with only one method named `execute()` or `process()`
- Patterns applied to problems too simple to warrant them
- More code to wire the framework than to solve the problem

---

### 8. What is YAGNI?

**A:** **You Aren't Gonna Need It** — don't implement something until it is actually needed. Resist the temptation to add "future-proofing" that isn't required now.

```go
// VIOLATION — building a plugin system "just in case"
type NotificationProvider interface { Send(msg string) error }
type NotificationRegistry struct { providers map[string]NotificationProvider }
func (r *NotificationRegistry) Register(name string, p NotificationProvider) { ... }
func (r *NotificationRegistry) GetProvider(name string) NotificationProvider { ... }
// ... 200 lines of infrastructure for a system with one email provider

// YAGNI — just send the email
func sendWelcomeEmail(address, subject, body string) error {
    return smtpClient.Send(address, subject, body)
}
// Refactor to plugin system when the second provider appears
```

---

### 9. What is Separation of Concerns (SoC)?

**A:** Different concerns (responsibilities) of a program should be separated into distinct sections, so that each section addresses a separate concern.

```javascript
// VIOLATION — one function handles HTTP, business logic, and persistence
app.post('/orders', async (req, res) => {
    if (!req.body.customerId) return res.status(400).json({ error: 'missing customerId' });
    const customer = await db.query('SELECT * FROM customers WHERE id = $1', [req.body.customerId]);
    if (customer.rows[0].credit_limit < req.body.total) return res.status(422).json({ error: 'credit limit exceeded' });
    const order = await db.query('INSERT INTO orders ...', [...]);
    await emailClient.send(customer.rows[0].email, 'Order confirmed');
    res.status(201).json(order.rows[0]);
});

// FIXED — each concern in its own layer
// HTTP layer: routing/validation
// Service layer: business logic
// Repository layer: data access
// Email service: notifications
```

---

### 10. What is the Law of Demeter (Principle of Least Knowledge)?

**A:** An object should only talk to its immediate friends — don't reach through objects to talk to strangers.

```csharp
// VIOLATION — "train wreck" / violates LoD
decimal tax = order.GetCustomer().GetAddress().GetRegion().GetTaxRate();

// PROBLEMS:
// - Caller depends on the entire chain (Order, Customer, Address, Region)
// - Adding a null check at each step becomes your responsibility
// - Breaks when any part of the chain changes

// FIXED — encapsulate the traversal
decimal tax = order.GetTaxRate(); // Order delegates internally
// Inside Order:
// decimal GetTaxRate() => customer.GetRegion().GetTaxRate();
// Inside Customer:
// Region GetRegion() => address.Region;
```

**"Only talk to:"**
- Itself
- Its direct fields/properties
- Objects passed as parameters
- Objects it creates
- Its direct dependencies (injected)

---

### 11. What does "Composition over Inheritance" mean?

**A:** Prefer assembling behavior from small, composable parts (via interfaces/delegation) rather than building deep inheritance hierarchies.

```python
# INHERITANCE PROBLEM — fragile hierarchy
class Animal:
    def breathe(self): ...

class Dog(Animal):
    def run(self): ...
    def bark(self): ...

class FlyingDog(Dog):  # now what? multiple behaviors → inheritance explodes
    def fly(self): ...

# COMPOSITION — mix and match behaviors
class RunBehavior:
    def run(self): print("running")

class SwimBehavior:
    def swim(self): print("swimming")

class FlyBehavior:
    def fly(self): print("flying")

class Duck:
    def __init__(self):
        self.run = RunBehavior()
        self.swim = SwimBehavior()
        self.fly = FlyBehavior()
```

**Why inheritance hurts:**
- Inheritance is the strongest coupling in OOP
- Subclass depends on ALL of parent's internals
- The "banana, gorilla, jungle" problem — you wanted a banana but got the gorilla and the jungle too

---

### 12. What is High Cohesion and Low Coupling?

**A:**

- **Cohesion** — how related and focused the responsibilities within a module are. High cohesion = module does one well-defined thing.
- **Coupling** — how much modules depend on each other. Low coupling = changes in one module don't ripple into others.

```
HIGH COHESION (good)          LOW COHESION (bad)
────────────────────          ─────────────────
UserRepository: save,         UserManager: save user, send email,
                findById,                  format report, parse CSV,
                delete                     validate credit card
(all about user persistence)  (unrelated responsibilities)

LOW COUPLING (good)           HIGH COUPLING (bad)
───────────────────           ──────────────────
OrderService depends on       OrderService creates MySQLRepository
IOrderRepository (interface)  directly and calls internal methods
→ can swap implementation     → tied to MySQL forever
```

**Goal:** Modules that are easy to understand (high cohesion), easy to change (low coupling), and easy to test (both).

---

### 13. What does "Program to an Interface, Not an Implementation" mean?

**A:** Write code that depends on abstractions (interfaces, abstract types) rather than concrete implementations.

```go
// IMPLEMENTATION — tightly coupled
type OrderService struct {
    db *PostgresDB  // concrete — switching DB requires changing OrderService
}

// INTERFACE — loosely coupled
type OrderRepository interface {
    Save(order Order) error
    FindByID(id string) (Order, error)
}

type OrderService struct {
    repo OrderRepository  // abstraction — any implementation works
}

// Now you can inject:
// - PostgresOrderRepository in production
// - InMemoryOrderRepository in tests
// - RedisOrderRepository for caching
// Without changing OrderService at all
```

---

### 14. What is Encapsulation and why does it matter?

**A:** Encapsulation bundles data and the operations on that data together, hiding internal state and exposing only what's necessary.

```java
// NO ENCAPSULATION — data exposed, invariants can be broken
class BankAccount {
    public double balance;  // anyone can set balance = -999999
}
account.balance = -1000000; // legal, but makes no sense

// ENCAPSULATED — invariants enforced
class BankAccount {
    private double balance;

    public void deposit(double amount) {
        if (amount <= 0) throw new IllegalArgumentException("Amount must be positive");
        this.balance += amount;
    }

    public void withdraw(double amount) {
        if (amount > balance) throw new InsufficientFundsException();
        this.balance -= amount;
    }

    public double getBalance() { return balance; } // read-only access
}
```

Encapsulation is not just about `private` fields — it's about ensuring objects are always in a valid state by controlling how their state is modified.

---

### 15. What is Fail Fast?

**A:** Detect and report failures as early as possible rather than continuing with invalid state that causes mysterious failures later.

```python
# FAIL SLOW — problem discovered 500 lines later
def process_order(order_id: str, quantity: int, discount: float):
    order = db.get(order_id)   # returns None silently
    items = order.items        # AttributeError: NoneType has no 'items' — confusing!

# FAIL FAST — problem discovered immediately
def process_order(order_id: str, quantity: int, discount: float):
    if not order_id: raise ValueError("order_id is required")
    if quantity <= 0: raise ValueError(f"quantity must be positive, got {quantity}")
    if not 0 <= discount <= 1: raise ValueError(f"discount must be 0-1, got {discount}")

    order = db.get(order_id)
    if order is None: raise OrderNotFoundError(f"Order {order_id} not found")
    # Now safe to proceed — all preconditions verified
```

**Fail fast in systems:** circuit breakers trip early rather than letting cascading failures propagate. Startup checks validate config before serving traffic.

---

### 16. What is Information Hiding?

**A:** Hide implementation details so that the rest of the system is shielded from complexity and internal changes. Different from (but related to) encapsulation.

```go
// EXPOSES IMPLEMENTATION — callers depend on internal details
type UserCache struct {
    Data map[string]*User  // exported field — external code now depends on map
}

cache.Data["user:42"] = user  // external code knows it's a map internally

// HIDES IMPLEMENTATION — internal structure can change freely
type UserCache struct {
    data map[string]*User  // unexported
}

func (c *UserCache) Set(userID string, user *User) { c.data["user:"+userID] = user }
func (c *UserCache) Get(userID string) (*User, bool) { return c.data["user:"+userID] }

// Now we can change from map to Redis without touching any caller
```

---

### 17. What is the difference between all SOLID principles — and which one is most often violated?

**A:**

| Principle | In one sentence | Smell when violated |
|-----------|----------------|---------------------|
| SRP | One reason to change | God class, huge methods |
| OCP | Extend, don't modify | Switch/if-else on type |
| LSP | Subtypes are substitutable | Subclass throws NotImplemented |
| ISP | Small focused interfaces | Fat interface, empty implementations |
| DIP | Depend on abstractions | `new ConcreteClass()` in business logic |

**Most often violated:** SRP — it's the hardest to keep because responsibilities naturally accumulate in one place over time (feature gravity). OCP is second — `if/switch` on type is the most common code smell in OOP codebases.

**Which violation is most dangerous:** DIP — once high-level modules depend on low-level ones, the entire architecture becomes rigid and untestable.
