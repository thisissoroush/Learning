# ☕ Java — Junior Interview Questions

---

### 1. What are the eight primitive types in Java?

**A:**

| Type | Size | Range | Default |
|------|------|-------|---------|
| `byte` | 8-bit | -128 to 127 | 0 |
| `short` | 16-bit | -32,768 to 32,767 | 0 |
| `int` | 32-bit | ~-2.1B to 2.1B | 0 |
| `long` | 64-bit | ~-9.2E18 to 9.2E18 | 0L |
| `float` | 32-bit | IEEE 754 | 0.0f |
| `double` | 64-bit | IEEE 754 | 0.0d |
| `char` | 16-bit | '\u0000' to '\uffff' | '\u0000' |
| `boolean` | JVM-dependent | true/false | false |

```java
int age = 30;
long population = 8_000_000_000L;
double pi = 3.14159;
char grade = 'A';
boolean active = true;
```

---

### 2. What is the difference between `==` and `.equals()`?

**A:**
- `==` compares **references** (memory addresses) for objects, and **values** for primitives
- `.equals()` compares **content/value** — overridden by `String`, `Integer`, etc.

```java
String a = new String("hello");
String b = new String("hello");

a == b          // false — different objects
a.equals(b)     // true  — same content

// String pool
String c = "hello";
String d = "hello";
c == d          // true  — same pool reference (interned)

// Integer cache (-128 to 127)
Integer x = 127; Integer y = 127;
x == y          // true  — cached
Integer p = 128; Integer q = 128;
p == q          // false — not cached
```

---

### 3. What is the difference between `String`, `StringBuilder`, and `StringBuffer`?

**A:**

| | `String` | `StringBuilder` | `StringBuffer` |
|--|---------|----------------|---------------|
| Mutability | Immutable | Mutable | Mutable |
| Thread-safe | Yes (immutable) | No | Yes (synchronized) |
| Performance | Slow for concat | Fast | Slower than SB |
| Use when | Fixed strings | Single-thread concat | Multi-thread concat |

```java
// String — creates new object on every concat
String s = "Hello";
s += " World"; // new String object

// StringBuilder — mutates in place
StringBuilder sb = new StringBuilder("Hello");
sb.append(" World");
sb.insert(5, ",");
sb.reverse();
String result = sb.toString();
```

---

### 4. What are the four pillars of OOP in Java?

**A:**

1. **Encapsulation** — hide internal state, expose through methods
```java
class BankAccount {
    private double balance; // hidden
    public void deposit(double amount) { balance += amount; }
    public double getBalance() { return balance; }
}
```

2. **Inheritance** — child class extends parent
```java
class Animal { void speak() { System.out.println("..."); } }
class Dog extends Animal { @Override void speak() { System.out.println("Woof"); } }
```

3. **Polymorphism** — same interface, different behavior
```java
Animal a = new Dog();
a.speak(); // "Woof" — runtime polymorphism
```

4. **Abstraction** — hide implementation details
```java
interface Shape { double area(); }
class Circle implements Shape {
    double r;
    public double area() { return Math.PI * r * r; }
}
```

---

### 5. What is the difference between `abstract class` and `interface`?

**A:**

| | Abstract Class | Interface |
|--|---------------|-----------|
| Multiple inheritance | No | Yes |
| Fields | Yes (any type) | Only `public static final` |
| Constructors | Yes | No |
| Methods | Abstract + concrete | Default + static + abstract |
| Access modifiers | Any | Public by default |
| `extends`/`implements` | `extends` | `implements` |

```java
abstract class Vehicle {
    private String brand; // instance field allowed
    Vehicle(String brand) { this.brand = brand; }
    abstract void start();
    void stop() { System.out.println("Stopping"); } // concrete
}

interface Flyable {
    int MAX_ALTITUDE = 40000; // implicitly public static final
    void fly();
    default void land() { System.out.println("Landing"); }
}

class FlyingCar extends Vehicle implements Flyable {
    FlyingCar(String brand) { super(brand); }
    public void start() { System.out.println("Starting"); }
    public void fly() { System.out.println("Flying"); }
}
```

---

### 6. What are access modifiers in Java?

**A:**

| Modifier | Class | Package | Subclass | World |
|----------|-------|---------|----------|-------|
| `public` | ✅ | ✅ | ✅ | ✅ |
| `protected` | ✅ | ✅ | ✅ | ❌ |
| (default) | ✅ | ✅ | ❌ | ❌ |
| `private` | ✅ | ❌ | ❌ | ❌ |

```java
public class Person {
    public String name;       // accessible everywhere
    protected int age;        // accessible in package + subclasses
    int score;                // package-private (default)
    private String ssn;       // only within this class
}
```

---

### 7. What is the difference between `final`, `finally`, and `finalize`?

**A:**
- `final` — keyword: constant variable, no-override method, no-subclass class
- `finally` — block that always runs after try/catch
- `finalize` — deprecated method called by GC before object is collected

```java
// final
final int MAX = 100;          // constant
final class NoExtend {}       // can't be subclassed
class A { final void method() {} } // can't be overridden

// finally
try {
    int x = 10 / 0;
} catch (ArithmeticException e) {
    System.out.println("caught");
} finally {
    System.out.println("always runs"); // even if exception or return
}

// finalize (avoid — deprecated since Java 9)
@Override
protected void finalize() { /* cleanup — don't rely on this */ }
```

---

### 8. What are Java Collections? What is the difference between `List`, `Set`, and `Map`?

**A:**

| Interface | Ordered | Duplicates | Null | Common Impl |
|-----------|---------|------------|------|-------------|
| `List` | Yes (index) | Yes | Yes | `ArrayList`, `LinkedList` |
| `Set` | No | No | One null | `HashSet`, `TreeSet`, `LinkedHashSet` |
| `Map` | No (keys) | Keys: No, Values: Yes | One null key | `HashMap`, `TreeMap`, `LinkedHashMap` |

```java
List<String> list = new ArrayList<>();
list.add("a"); list.add("a"); // [a, a] — duplicates allowed

Set<String> set = new HashSet<>();
set.add("a"); set.add("a"); // {a} — no duplicates

Map<String, Integer> map = new HashMap<>();
map.put("age", 30);
map.getOrDefault("missing", 0); // 0
map.putIfAbsent("age", 25);     // no-op, already exists
```

---

### 9. What is the difference between `ArrayList` and `LinkedList`?

**A:**

| | `ArrayList` | `LinkedList` |
|--|------------|-------------|
| Internal structure | Dynamic array | Doubly linked list |
| Random access `get(i)` | O(1) | O(n) |
| Insert/delete at end | O(1) amortized | O(1) |
| Insert/delete at middle | O(n) | O(1) (with iterator) |
| Memory | Less | More (node overhead) |
| Use when | Read-heavy | Frequent insert/delete at head |

```java
// ArrayList — backed by array, great for indexed access
List<String> arrayList = new ArrayList<>();

// LinkedList — also implements Deque, good as stack/queue
Deque<String> deque = new LinkedList<>();
deque.push("first");
deque.pop();
```

---

### 10. How does exception handling work in Java?

**A:**

```java
// Checked exceptions — must be caught or declared
void readFile(String path) throws IOException {
    FileReader fr = new FileReader(path); // throws FileNotFoundException
}

// Unchecked exceptions (RuntimeException) — no need to declare
void divide(int a, int b) {
    if (b == 0) throw new ArithmeticException("division by zero");
}

// Try-catch-finally
try {
    String s = null;
    s.length(); // NullPointerException
} catch (NullPointerException e) {
    System.out.println("Caught: " + e.getMessage());
} catch (Exception e) {
    System.out.println("Generic: " + e.getMessage());
} finally {
    System.out.println("Always runs");
}

// Try-with-resources — auto-closes AutoCloseable
try (BufferedReader br = new BufferedReader(new FileReader("file.txt"))) {
    String line;
    while ((line = br.readLine()) != null) System.out.println(line);
} // br.close() called automatically

// Multi-catch
try { ... }
catch (IOException | SQLException e) { log(e); }
```

---

### 11. What is autoboxing and unboxing?

**A:** Automatic conversion between primitives and their wrapper classes:

```java
// Autoboxing — primitive → wrapper
Integer i = 42;           // int → Integer
List<Integer> list = new ArrayList<>();
list.add(5);              // int 5 → Integer.valueOf(5)

// Unboxing — wrapper → primitive
int x = i;                // Integer → int
int sum = list.get(0) + 1; // Integer → int, then +1

// Pitfall: NullPointerException on unboxing
Integer n = null;
int val = n; // NullPointerException!

// Pitfall: == comparison
Integer a = 200;
Integer b = 200;
a == b; // false — not cached (only -128 to 127 are cached)
a.equals(b); // true
```

---

### 12. What is a constructor and what are constructor chaining and constructor overloading?

**A:**

```java
class Person {
    String name;
    int age;
    String email;

    // Overloaded constructors
    Person(String name) {
        this(name, 0); // constructor chaining with this()
    }

    Person(String name, int age) {
        this(name, age, "unknown@email.com");
    }

    Person(String name, int age, String email) {
        this.name = name;
        this.age = age;
        this.email = email;
    }
}

class Employee extends Person {
    String department;

    Employee(String name, String department) {
        super(name); // must be first statement — calls parent constructor
        this.department = department;
    }
}
```

---

### 13. What are `static` members?

**A:** `static` members belong to the class, not any instance:

```java
class Counter {
    private static int count = 0;  // shared across all instances
    private int id;

    Counter() {
        count++;
        this.id = count;
    }

    static int getCount() { return count; } // static method — no 'this'
    int getId() { return id; }              // instance method

    static {
        System.out.println("Counter class loaded"); // static initializer
    }
}

Counter.getCount(); // call without instance
new Counter();
new Counter();
Counter.getCount(); // 2
```

---

### 14. What are varargs in Java?

**A:**

```java
// Varargs — variable-length argument list
int sum(int... numbers) {
    int total = 0;
    for (int n : numbers) total += n;
    return total;
}

sum();             // 0
sum(1, 2, 3);      // 6
sum(new int[]{1, 2, 3}); // array also works

// Rules:
// - Only one varargs parameter per method
// - Must be the last parameter
void log(String level, String... messages) { ... }
log("INFO", "Starting", "Ready");
```

---

### 15. What is the enhanced for loop and when do you use it?

**A:**

```java
// Works on arrays and anything implementing Iterable<T>
int[] numbers = {1, 2, 3, 4, 5};
for (int n : numbers) {
    System.out.println(n);
}

List<String> names = List.of("Alice", "Bob", "Charlie");
for (String name : names) {
    System.out.println(name);
}

Map<String, Integer> scores = Map.of("Alice", 95, "Bob", 87);
for (Map.Entry<String, Integer> entry : scores.entrySet()) {
    System.out.println(entry.getKey() + ": " + entry.getValue());
}

// Cannot modify list while iterating (ConcurrentModificationException)
// Use Iterator or removeIf() for in-place removal
names.removeIf(name -> name.startsWith("A"));
```

---

### 16. What is `instanceof` and pattern matching (Java 16+)?

**A:**

```java
Object obj = "Hello World";

// Classic instanceof
if (obj instanceof String) {
    String s = (String) obj; // manual cast required
    System.out.println(s.length());
}

// Pattern matching (Java 16+)
if (obj instanceof String s) {  // cast + bind in one
    System.out.println(s.length()); // s is available here
}

// In switch (Java 21 — pattern switch)
String result = switch (obj) {
    case Integer i -> "int: " + i;
    case String s  -> "string: " + s;
    case null      -> "null";
    default        -> "other";
};
```

---

### 17. What are wrapper classes?

**A:**

```java
// Primitive → Wrapper
Integer.valueOf(42)    // preferred over new Integer(42)
Double.valueOf(3.14)
Boolean.valueOf(true)

// Wrapper → Primitive
Integer i = 42;
i.intValue()    // 42
i.doubleValue() // 42.0

// Parsing Strings
int n = Integer.parseInt("42");
double d = Double.parseDouble("3.14");
boolean b = Boolean.parseBoolean("true");

// Useful constants
Integer.MAX_VALUE   // 2147483647
Integer.MIN_VALUE   // -2147483648
Integer.toBinaryString(255) // "11111111"
Integer.toHexString(255)    // "ff"
```

---

### 18. What is a record in Java (Java 16+)?

**A:** Records are immutable data carriers — auto-generate constructor, getters, `equals`, `hashCode`, `toString`:

```java
// Declare
record Point(int x, int y) {}

// Usage
Point p = new Point(3, 4);
p.x()        // 3 — accessor (not getX())
p.y()        // 4
p.toString() // "Point[x=3, y=4]"

// Records are immutable — no setters
// p.x = 5; // compile error

// Compact constructor — validation
record Range(int min, int max) {
    Range {
        if (min > max) throw new IllegalArgumentException("min > max");
    }
}

// Records can implement interfaces
record Color(int r, int g, int b) implements Comparable<Color> {
    public int compareTo(Color other) {
        return Integer.compare(this.r + this.g + this.b, other.r + other.g + other.b);
    }
}
```

---

### 19. What are sealed classes (Java 17+)?

**A:** Sealed classes restrict which classes can extend or implement them:

```java
// Only listed classes can extend Shape
sealed interface Shape permits Circle, Rectangle, Triangle {}

final class Circle implements Shape {
    double radius;
}

final class Rectangle implements Shape {
    double width, height;
}

non-sealed class Triangle implements Shape { // can be freely extended
    double base, height;
}

// Switch must be exhaustive when all cases are sealed
double area = switch (shape) {
    case Circle c    -> Math.PI * c.radius * c.radius;
    case Rectangle r -> r.width * r.height;
    case Triangle t  -> 0.5 * t.base * t.height;
}; // no default needed — compiler knows all cases
```

---

### 20. What is `Optional` and why use it?

**A:** `Optional<T>` makes the possibility of absence explicit — avoids `null` returns:

```java
import java.util.Optional;

// Create
Optional<String> empty = Optional.empty();
Optional<String> present = Optional.of("Hello");
Optional<String> nullable = Optional.ofNullable(possiblyNull);

// Use safely
optional.isPresent()           // true/false
optional.isEmpty()             // Java 11+
optional.get()                 // throws if empty — avoid
optional.orElse("default")     // value or default
optional.orElseGet(() -> compute()) // lazy default
optional.orElseThrow(() -> new NoSuchElementException())
optional.ifPresent(System.out::println)

// Transform
optional.map(String::toUpperCase)     // Optional<String>
optional.flatMap(s -> Optional.of(s)) // unwrap nested Optional
optional.filter(s -> s.length() > 3)  // Optional.empty() if predicate fails

// In practice
Optional<User> user = userRepo.findById(id);
String name = user.map(User::getName).orElse("Anonymous");
```
