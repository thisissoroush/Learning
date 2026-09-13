# 🏛️ Design Patterns — Interview Questions

Language-agnostic. Focus on understanding *what problem* each pattern solves and *when NOT to use it*.

---

### 1. What is a design pattern and why do they matter?

**A:** Design patterns are reusable solutions to commonly occurring problems in software design. They are a shared vocabulary — saying "use Strategy here" communicates a whole design decision instantly.

**Three categories (Gang of Four):**
- **Creational** — how objects are created (Factory, Builder, Singleton, Prototype, Abstract Factory)
- **Structural** — how objects are composed (Adapter, Decorator, Facade, Proxy, Composite)
- **Behavioral** — how objects communicate (Strategy, Observer, Command, Chain of Responsibility, State, Template Method, Mediator)

**When NOT to use a pattern:** When the problem doesn't actually warrant it. Patterns add indirection and complexity — apply only when the forces they address genuinely exist in your codebase.

---

### 2. What is the Factory pattern and when do you use it?

**A:** Factory encapsulates object creation logic, returning an object without exposing the instantiation details.

```python
# Without factory — creation scattered everywhere
conn1 = MySQLConnection(host, user, password)
conn2 = PostgresConnection(dsn)

# With factory — creation centralized, caller decoupled from concrete type
class DatabaseFactory:
    @staticmethod
    def create(driver: str) -> DatabaseConnection:
        match driver:
            case "mysql":    return MySQLConnection(os.getenv("MYSQL_DSN"))
            case "postgres": return PostgresConnection(os.getenv("PG_DSN"))
            case "sqlite":   return SQLiteConnection(":memory:")
            case _: raise ValueError(f"Unknown driver: {driver}")

db = DatabaseFactory.create(config.DB_DRIVER)
```

**Use when:** You need to create objects whose type is determined at runtime, or you want to centralize complex creation logic.

**Don't use when:** You only ever create one type — a plain constructor is simpler.

---

### 3. What is the Abstract Factory pattern?

**A:** Abstract Factory creates *families* of related objects without specifying their concrete classes. Factory of Factories.

```go
// Each factory creates a consistent family of UI components
type UIFactory interface {
    CreateButton() Button
    CreateCheckbox() Checkbox
}

type WindowsFactory struct{}
func (f WindowsFactory) CreateButton() Button    { return WindowsButton{} }
func (f WindowsFactory) CreateCheckbox() Checkbox { return WindowsCheckbox{} }

type MacOSFactory struct{}
func (f MacOSFactory) CreateButton() Button    { return MacButton{} }
func (f MacOSFactory) CreateCheckbox() Checkbox { return MacCheckbox{} }

// Application uses the factory — never knows about Windows vs Mac
func buildApp(factory UIFactory) {
    btn := factory.CreateButton()
    chk := factory.CreateCheckbox()
    // btn and chk are always from the same family (consistent look)
}
```

**Use when:** Your system needs to work with multiple families of related products and must stay consistent within a family.

---

### 4. What is the Builder pattern?

**A:** Constructs complex objects step-by-step, separating construction from representation.

```java
// Without builder — constructor hell (which param is which?)
Order order = new Order("customer-1", "product-5", 3, 29.99, "USD", "EXPRESS", true, null);

// With builder — readable, validation at build time
Order order = Order.builder()
    .customerId("customer-1")
    .productId("product-5")
    .quantity(3)
    .unitPrice(29.99)
    .currency("USD")
    .shippingMethod(ShippingMethod.EXPRESS)
    .giftWrapped(true)
    .build(); // can validate here — all fields set, enforce required ones

// Also enables immutable objects (no setters needed)
```

**Use when:** Object has many optional parameters, or creation requires multiple steps with validation.

**Don't use when:** Object is simple with 1-3 required parameters — a constructor is cleaner.

---

### 5. What is the Singleton pattern and what are its problems?

**A:** Ensures a class has exactly one instance and provides a global access point.

```csharp
public sealed class Configuration
{
    private static readonly Lazy<Configuration> _instance =
        new(() => new Configuration(), LazyThreadSafetyMode.ExecutionAndPublication);

    private Configuration() { Load(); }
    public static Configuration Instance => _instance.Value;
    public string DatabaseUrl { get; private set; }
}
```

**Problems with Singleton:**
1. **Global state** — hidden dependency, makes code hard to reason about
2. **Testability** — can't swap with a test double without hacking
3. **SRP violation** — manages its own lifecycle AND its responsibilities
4. **Tight coupling** — callers reach out to global state instead of receiving it

**Better alternative:** Dependency injection — register as singleton in DI container, inject as interface. Same lifetime, no global state.

---

### 6. What is the Adapter pattern?

**A:** Converts the interface of a class into another interface that clients expect. Makes incompatible interfaces work together.

```typescript
// Existing interface your code depends on
interface Logger {
    log(level: string, message: string): void;
}

// Third-party library with different interface
class ThirdPartyLoggingLib {
    writeLog(severity: number, msg: string, timestamp: Date): void { ... }
}

// Adapter — wraps incompatible class, exposes expected interface
class ThirdPartyLoggerAdapter implements Logger {
    private lib: ThirdPartyLoggingLib;

    log(level: string, message: string): void {
        const severity = level === "error" ? 3 : level === "warn" ? 2 : 1;
        this.lib.writeLog(severity, message, new Date());
    }
}

// Existing code unchanged — just plug in the adapter
const logger: Logger = new ThirdPartyLoggerAdapter(new ThirdPartyLoggingLib());
```

---

### 7. What is the Decorator pattern?

**A:** Wraps an object to add new behavior without subclassing. Stackable at runtime.

```python
from abc import ABC, abstractmethod

class DataSource(ABC):
    @abstractmethod
    def write(self, data: bytes): ...
    @abstractmethod
    def read(self) -> bytes: ...

class FileDataSource(DataSource):
    def write(self, data): open(self.path, "wb").write(data)
    def read(self): return open(self.path, "rb").read()

class CompressionDecorator(DataSource):
    def __init__(self, source: DataSource):
        self._source = source

    def write(self, data):
        self._source.write(gzip.compress(data))    # add compression

    def read(self):
        return gzip.decompress(self._source.read())

class EncryptionDecorator(DataSource):
    def write(self, data):
        self._source.write(encrypt(data))          # add encryption

    def read(self):
        return decrypt(self._source.read())

# Stack decorators at runtime
source = EncryptionDecorator(CompressionDecorator(FileDataSource("data.bin")))
source.write(b"secret data")  # compressed then encrypted
```

**vs Inheritance:** Inheritance is static (chosen at compile time). Decorators compose at runtime.

---

### 8. What is the Facade pattern?

**A:** Provides a simplified interface to a complex subsystem.

```go
// Complex subsystem — many moving parts
type VideoConverter struct{}
func (v *VideoConverter) Convert(file string, format string) VideoFile {
    // involves codec finder, bitrate reader, buffer reader, audio mixer...
    codecFactory := NewCodecFactory()
    sourceCodec := codecFactory.Extract(file)
    destinationCodec := NewOgg()
    reader := NewBitrateReader(file, sourceCodec)
    buffer := reader.Read(sourceCodec)
    // ... 50 more lines
}

// Facade — simple interface for common use case
type VideoConversionFacade struct {
    converter *VideoConverter
    // other subsystem components...
}

func (f *VideoConversionFacade) ConvertVideo(filename, format string) string {
    // Hides all complexity behind one method
    video := f.converter.Convert(filename, format)
    return video.Save()
}

// Client only needs this:
facade := &VideoConversionFacade{}
outputFile := facade.ConvertVideo("funny-cats.ogg", "mp4")
```

---

### 9. What is the Proxy pattern and what are its types?

**A:** Provides a surrogate that controls access to another object.

```java
// Types of proxies:
// 1. Virtual proxy — lazy initialization (don't load until needed)
class ImageProxy implements Image {
    private String filename;
    private RealImage realImage;  // null until first use

    public void display() {
        if (realImage == null) realImage = new RealImage(filename); // load on demand
        realImage.display();
    }
}

// 2. Protection proxy — access control
class SecureDocumentProxy implements Document {
    public String getContent(User user) {
        if (!user.hasPermission("READ_DOCUMENTS")) throw new AccessDeniedException();
        return realDocument.getContent(user);
    }
}

// 3. Remote proxy — hides network call (gRPC stubs, Feign clients)

// 4. Caching proxy — memoize expensive calls
class CachingRepository implements UserRepository {
    public User findById(Long id) {
        return cache.computeIfAbsent(id, key -> realRepo.findById(key));
    }
}

// 5. Logging proxy — add logging transparently
// (Most AOP frameworks generate proxies automatically)
```

---

### 10. What is the Composite pattern?

**A:** Composes objects into tree structures to represent part-whole hierarchies. Lets clients treat individual objects and compositions uniformly.

```python
from abc import ABC, abstractmethod

class FileSystemItem(ABC):
    @abstractmethod
    def size(self) -> int: ...
    @abstractmethod
    def display(self, indent: int = 0): ...

class File(FileSystemItem):
    def __init__(self, name: str, size: int):
        self.name, self._size = name, size

    def size(self) -> int: return self._size
    def display(self, indent=0): print(" " * indent + f"📄 {self.name} ({self._size}B)")

class Directory(FileSystemItem):
    def __init__(self, name: str):
        self.name = name
        self.children: list[FileSystemItem] = []

    def add(self, item: FileSystemItem): self.children.append(item)
    def size(self) -> int: return sum(c.size() for c in self.children)
    def display(self, indent=0):
        print(" " * indent + f"📁 {self.name}/")
        for child in self.children: child.display(indent + 2)

# Client treats File and Directory identically
root = Directory("root")
root.add(File("readme.md", 1024))
docs = Directory("docs")
docs.add(File("api.md", 512))
root.add(docs)

print(root.size())   # sums recursively — same call on file or directory
root.display()       # renders tree — same call on file or directory
```

---

### 11. What is the Strategy pattern?

**A:** Defines a family of algorithms, encapsulates each one, and makes them interchangeable. Lets the algorithm vary independently from clients that use it.

```go
type SortStrategy interface {
    Sort(data []int) []int
}

type BubbleSort struct{}
func (b BubbleSort) Sort(data []int) []int { /* O(n²) */ }

type QuickSort struct{}
func (q QuickSort) Sort(data []int) []int { /* O(n log n) */ }

type MergeSort struct{}
func (m MergeSort) Sort(data []int) []int { /* O(n log n), stable */ }

type Sorter struct {
    strategy SortStrategy
}

func (s *Sorter) SetStrategy(strategy SortStrategy) { s.strategy = strategy }
func (s *Sorter) Sort(data []int) []int { return s.strategy.Sort(data) }

// Select at runtime
sorter := &Sorter{}
if len(data) < 10 {
    sorter.SetStrategy(BubbleSort{})
} else {
    sorter.SetStrategy(QuickSort{})
}
result := sorter.Sort(data)
```

---

### 12. What is the difference between Strategy and Factory?

**A:** This is a classic interview question — they address different problems.

| | Strategy | Factory |
|--|----------|---------|
| **Purpose** | Select *how* to do something (algorithm) | Select *what* to create (object) |
| **Focus** | Behavior at runtime | Object creation |
| **Changes** | The operation being performed | The type being instantiated |
| **Result** | The same context runs differently | A new object of different type |

```python
# Strategy — SAME object, DIFFERENT behavior
class Compressor:
    def __init__(self, strategy: CompressionStrategy):
        self.strategy = strategy  # swap algorithm

    def compress(self, data: bytes) -> bytes:
        return self.strategy.compress(data)  # same interface, different impl

# Factory — creates DIFFERENT objects based on input
class NotificationFactory:
    def create(self, channel: str) -> Notification:
        match channel:
            case "email": return EmailNotification()
            case "sms":   return SMSNotification()
            # returns different types
```

---

### 13. What is the Observer pattern?

**A:** Defines a one-to-many dependency so that when one object (Subject) changes state, all its dependents (Observers) are notified automatically.

```typescript
interface Observer {
    update(event: OrderEvent): void;
}

class Order {  // Subject
    private observers: Observer[] = [];

    subscribe(observer: Observer) { this.observers.push(observer); }
    unsubscribe(observer: Observer) { this.observers = this.observers.filter(o => o !== observer); }

    private notify(event: OrderEvent) {
        this.observers.forEach(o => o.update(event));
    }

    ship() {
        this.status = "SHIPPED";
        this.notify({ type: "SHIPPED", orderId: this.id, timestamp: new Date() });
    }
}

class EmailNotifier implements Observer {
    update(event: OrderEvent) { sendEmail(event); }
}

class InventoryUpdater implements Observer {
    update(event: OrderEvent) { releaseReservation(event.orderId); }
}

class AnalyticsTracker implements Observer {
    update(event: OrderEvent) { trackEvent(event); }
}

// Wire up
const order = new Order();
order.subscribe(new EmailNotifier());
order.subscribe(new InventoryUpdater());
order.subscribe(new AnalyticsTracker());
order.ship(); // all three notified
```

**Modern equivalent:** Domain events / event bus / message broker.

---

### 14. What is the Command pattern?

**A:** Encapsulates a request as an object, allowing parameterization, queuing, logging, and undo/redo.

```python
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self): ...
    @abstractmethod
    def undo(self): ...

class TransferMoneyCommand(Command):
    def __init__(self, from_acc, to_acc, amount):
        self.from_acc, self.to_acc, self.amount = from_acc, to_acc, amount

    def execute(self):
        self.from_acc.debit(self.amount)
        self.to_acc.credit(self.amount)

    def undo(self):
        self.from_acc.credit(self.amount)
        self.to_acc.debit(self.amount)

class CommandProcessor:
    def __init__(self):
        self.history: list[Command] = []

    def execute(self, command: Command):
        command.execute()
        self.history.append(command)

    def undo_last(self):
        if self.history:
            self.history.pop().undo()

# Supports: queuing, logging, undo, replay
processor = CommandProcessor()
processor.execute(TransferMoneyCommand(alice_acc, bob_acc, 100))
processor.undo_last()  # reverses the transfer
```

---

### 15. What is the Chain of Responsibility pattern?

**A:** Passes requests along a chain of handlers. Each handler decides to process or pass it to the next.

```go
type Handler interface {
    SetNext(handler Handler) Handler
    Handle(request *Request) *Response
}

type BaseHandler struct { next Handler }

func (h *BaseHandler) SetNext(next Handler) Handler { h.next = next; return next }
func (h *BaseHandler) Handle(r *Request) *Response {
    if h.next != nil { return h.next.Handle(r) }
    return nil
}

type AuthHandler struct { BaseHandler }
func (h *AuthHandler) Handle(r *Request) *Response {
    if !r.IsAuthenticated() { return &Response{Status: 401} }
    return h.BaseHandler.Handle(r)
}

type RateLimitHandler struct { BaseHandler }
func (h *RateLimitHandler) Handle(r *Request) *Response {
    if !rateLimiter.Allow(r.IP) { return &Response{Status: 429} }
    return h.BaseHandler.Handle(r)
}

type BusinessHandler struct { BaseHandler }
func (h *BusinessHandler) Handle(r *Request) *Response {
    return processRequest(r)
}

// Build chain
auth := &AuthHandler{}
rateLimit := &RateLimitHandler{}
business := &BusinessHandler{}
auth.SetNext(rateLimit).SetNext(business)

response := auth.Handle(request)
```

---

### 16. What is the State pattern?

**A:** Allows an object to alter its behavior when its internal state changes. The object will appear to change its class.

```java
interface OrderState {
    void confirm(Order order);
    void ship(Order order);
    void deliver(Order order);
    void cancel(Order order);
}

class PendingState implements OrderState {
    public void confirm(Order o) { o.setState(new ConfirmedState()); }
    public void ship(Order o)    { throw new InvalidStateException("Must confirm first"); }
    public void cancel(Order o)  { o.setState(new CancelledState()); }
}

class ConfirmedState implements OrderState {
    public void confirm(Order o) { throw new InvalidStateException("Already confirmed"); }
    public void ship(Order o)    { o.setState(new ShippedState()); }
    public void cancel(Order o)  { o.setState(new CancelledState()); }
}

class ShippedState implements OrderState {
    public void deliver(Order o) { o.setState(new DeliveredState()); }
    public void cancel(Order o)  { throw new InvalidStateException("Cannot cancel shipped order"); }
}

// Instead of if/else chains based on status string
// Each state encapsulates its own transitions
```

---

### 17. What is the Template Method pattern?

**A:** Defines the skeleton of an algorithm in a base class, deferring some steps to subclasses.

```python
from abc import ABC, abstractmethod

class DataImporter(ABC):
    # Template method — the algorithm skeleton
    def import_data(self, source: str):
        raw = self.read(source)        # step 1
        parsed = self.parse(raw)       # step 2
        validated = self.validate(parsed) # step 3
        self.save(validated)           # step 4
        self.notify()                  # step 5 (hook — optional override)

    @abstractmethod
    def read(self, source: str) -> bytes: ...

    @abstractmethod
    def parse(self, data: bytes) -> list: ...

    def validate(self, data: list) -> list:  # default implementation
        return [row for row in data if row]  # filter empty

    @abstractmethod
    def save(self, data: list): ...

    def notify(self): pass  # hook — subclasses may override or not

class CSVImporter(DataImporter):
    def read(self, source): return open(source, "rb").read()
    def parse(self, data): return csv.reader(data.decode().splitlines())
    def save(self, data): db.bulk_insert(data)

class JSONImporter(DataImporter):
    def read(self, source): return requests.get(source).content
    def parse(self, data): return json.loads(data)
    def save(self, data): db.upsert(data)
    def notify(self): slack.post("JSON import complete") # overrides hook
```

---

### 18. What is the Mediator pattern?

**A:** Defines an object that encapsulates how a set of objects interact, reducing direct coupling between them.

```typescript
// Without Mediator — components know about each other
class ChatRoom {
    private users: User[] = [];
    sendMessage(sender: User, message: string) {
        this.users
            .filter(u => u !== sender)
            .forEach(u => u.receive(message, sender));
    }
    addUser(user: User) { this.users.push(user); user.setChatRoom(this); }
}

class User {
    private chatRoom: ChatRoom;
    send(message: string) { this.chatRoom.sendMessage(this, message); }
    receive(message: string, from: User) { console.log(`${from.name}: ${message}`); }
}

// ChatRoom IS the mediator — users only talk to it, not to each other
// Adding new features (moderation, logging) → change ChatRoom only
```

**Real-world equivalents:** Message brokers (Kafka, RabbitMQ), event buses, MediatR library.

---

### 19. When would you NOT use a design pattern?

**A:** This is the most important pattern question. Patterns have a cost — they add abstraction and indirection.

**Don't use when:**
1. **The problem is simpler than the pattern** — a function is cleaner than a Strategy
2. **Premature abstraction** — you don't yet know the variation that the pattern is meant to handle
3. **Performance-critical hot paths** — virtual dispatch and indirection have a cost
4. **Small codebases** — patterns shine in large systems with multiple variations
5. **The team doesn't know the pattern** — an unknown pattern is worse than no pattern

```python
# Don't apply Strategy because "it might need multiple algorithms someday"
# When there's only ever one algorithm:
class Sorter:
    strategy: SortStrategy  # YAGNI — adds complexity for no current benefit

# Just write the function:
def sort(data: list) -> list:
    return sorted(data)  # clean, simple, testable
```

**Rule:** Apply a pattern when you feel the pain the pattern solves, not before.

---

### 20. What is the Prototype pattern?

**A:** Creates new objects by cloning an existing object (the prototype) rather than constructing from scratch.

```go
type Shape interface {
    Clone() Shape
    Draw()
}

type Circle struct {
    X, Y, Radius int
    Color        string
}

func (c *Circle) Clone() Shape {
    clone := *c  // copy struct
    return &clone
}

// Use when object creation is expensive (DB lookup, complex initialization)
// Or when you need many similar objects with slight variations

templateCircle := &Circle{X: 0, Y: 0, Radius: 10, Color: "red"}

for i := 0; i < 100; i++ {
    circle := templateCircle.Clone().(*Circle)
    circle.X = i * 20  // vary only what's different
    circles = append(circles, circle)
}
```
