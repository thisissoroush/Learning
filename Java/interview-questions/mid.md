# ☕ Java — Mid-Level Interview Questions

---

### 1. What are lambda expressions and functional interfaces?

**A:** Lambda expressions are anonymous functions — they implement functional interfaces (interfaces with exactly one abstract method):

```java
// Functional interface
@FunctionalInterface
interface Transformer<T, R> {
    R transform(T input);
}

// Lambda syntax: (params) -> expression
Transformer<String, Integer> length = s -> s.length();
Transformer<Integer, Integer> square = x -> x * x;

// Built-in functional interfaces
Function<String, Integer> fn = String::length;
Predicate<String> isEmpty = String::isEmpty;
Consumer<String> print = System.out::println;
Supplier<String> hello = () -> "Hello";
BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;
UnaryOperator<String> upper = String::toUpperCase;
Comparator<String> byLength = Comparator.comparingInt(String::length);

// Multi-line lambda
Runnable r = () -> {
    System.out.println("Step 1");
    System.out.println("Step 2");
};
```

---

### 2. What is the Stream API and how do you use it?

**A:** Streams provide a declarative, lazy pipeline for processing sequences of elements:

```java
List<String> names = List.of("Alice", "Bob", "Charlie", "Anna", "Dave");

// Pipeline: source → intermediate ops (lazy) → terminal op (triggers execution)
List<String> result = names.stream()
    .filter(n -> n.startsWith("A"))       // intermediate — lazy
    .map(String::toUpperCase)             // intermediate — lazy
    .sorted()                             // intermediate — lazy
    .collect(Collectors.toList());        // terminal — executes pipeline
// ["ALICE", "ANNA"]

// Common terminals
long count   = stream.count();
Optional<T> first = stream.findFirst();
boolean any  = stream.anyMatch(predicate);
boolean all  = stream.allMatch(predicate);
int sum      = stream.mapToInt(Integer::parseInt).sum();
String joined = stream.collect(Collectors.joining(", "));
Map<Boolean, List<String>> partitioned = stream.collect(Collectors.partitioningBy(predicate));
Map<Integer, List<String>> grouped = stream.collect(Collectors.groupingBy(String::length));

// Parallel stream
long count = hugeList.parallelStream()
    .filter(expensiveCheck)
    .count();

// flatMap — flatten nested collections
List<List<Integer>> nested = List.of(List.of(1,2), List.of(3,4));
List<Integer> flat = nested.stream()
    .flatMap(Collection::stream)
    .collect(Collectors.toList()); // [1, 2, 3, 4]
```

---

### 3. What are method references?

**A:** Method references are shorthand for lambdas that call an existing method:

```java
// Static method reference: ClassName::staticMethod
Function<String, Integer> parse = Integer::parseInt;
// equivalent: s -> Integer.parseInt(s)

// Instance method on specific instance: instance::method
String prefix = "Hello ";
Function<String, String> addPrefix = prefix::concat;

// Instance method on arbitrary instance: ClassName::instanceMethod
Function<String, String> upper = String::toUpperCase;
// equivalent: s -> s.toUpperCase()

// Constructor reference: ClassName::new
Supplier<ArrayList<String>> listFactory = ArrayList::new;
Function<String, Person> personFactory = Person::new;

// Usage
List<String> strings = List.of("1", "2", "3");
List<Integer> numbers = strings.stream()
    .map(Integer::parseInt)   // static method ref
    .collect(Collectors.toList());

strings.forEach(System.out::println); // instance method on System.out
```

---

### 4. What is the difference between `Comparable` and `Comparator`?

**A:**

```java
// Comparable — natural ordering (implement in the class)
class Person implements Comparable<Person> {
    String name;
    int age;

    @Override
    public int compareTo(Person other) {
        return Integer.compare(this.age, other.age); // natural order by age
    }
}

List<Person> people = new ArrayList<>(personList);
Collections.sort(people); // uses compareTo

// Comparator — external, custom ordering
Comparator<Person> byName = Comparator.comparing(p -> p.name);
Comparator<Person> byAgeDesc = Comparator.comparingInt(Person::getAge).reversed();
Comparator<Person> complex = Comparator.comparing(Person::getLastName)
                                       .thenComparing(Person::getFirstName)
                                       .thenComparingInt(Person::getAge);

people.sort(byName);
people.stream().sorted(byAgeDesc).collect(Collectors.toList());
```

---

### 5. What is the Java Memory Model? What are heap and stack?

**A:**

```
JVM Memory:
┌─────────────────────────────────────────┐
│  Heap (GC-managed, all threads share)   │
│  ├── Young Generation                    │
│  │   ├── Eden Space                      │
│  │   └── Survivor Spaces (S0, S1)        │
│  └── Old Generation (Tenured)            │
├─────────────────────────────────────────┤
│  Metaspace (class metadata)              │
├─────────────────────────────────────────┤
│  Stack (per thread, LIFO)               │
│  ├── Frame for main()                    │
│  │   ├── local variables                 │
│  │   ├── operand stack                   │
│  │   └── reference to current method    │
│  └── Frame for doWork()                  │
└─────────────────────────────────────────┘
```

- **Stack** — primitive values + object references stored per method frame; fast; fixed size; `StackOverflowError`
- **Heap** — all objects live here; GC manages; `OutOfMemoryError`

```java
void method() {
    int x = 5;              // stack (primitive value)
    String s = "hello";     // stack (reference) → Heap (String object)
    Person p = new Person(); // stack (reference) → Heap (Person object)
}
```

---

### 6. How does garbage collection work in Java?

**A:** Java uses generational GC — most objects die young:

**Generations:**
- **Eden** — new objects allocated here
- **Survivor (S0/S1)** — objects that survived at least one minor GC
- **Old Gen** — long-lived objects promoted from Young Gen

**GC algorithms:**
- **G1GC** (default since Java 9) — region-based, predictable pause times
- **ZGC** (Java 15+) — sub-millisecond pauses, for large heaps
- **Shenandoah** — concurrent, low-pause

```bash
# JVM flags
-Xms512m -Xmx4g           # initial/max heap
-XX:+UseG1GC              # force G1
-XX:MaxGCPauseMillis=200  # target pause time
-XX:+PrintGCDetails       # GC logging
-Xlog:gc*:gc.log          # Java 11+ unified logging
```

**Eligible for GC:** Object with no reachable references (not the same as `null` — you can null a variable without making the object unreachable if other refs exist).

---

### 7. What are `HashMap` internals? How does it handle collisions?

**A:**

**Structure:** Array of buckets (linked list or tree per bucket):

```
Index:  0   1   2   3  ...  n-1
        ↓   ↓       ↓
      [K,V] [K,V]  [K,V]→[K,V]  ← collision (same bucket)
```

**Put operation:**
1. `hash = key.hashCode()` → spread with `(h ^ h >>> 16)`
2. `index = hash & (capacity - 1)` → which bucket
3. If empty → store entry
4. If collision → compare `hashCode` + `equals`
   - Match → update value
   - No match → add to chain (linked list)

**Java 8 optimization:** When a bucket's linked list grows beyond 8 nodes, it converts to a **Red-Black Tree** (O(log n) instead of O(n)).

**Key requirements for keys:** `hashCode` and `equals` must be consistent — if `a.equals(b)` then `a.hashCode() == b.hashCode()`.

```java
// Default capacity: 16, load factor: 0.75
// Resizes (doubles) when size > capacity * loadFactor
Map<String, Integer> map = new HashMap<>(32, 0.5f); // custom
```

---

### 8. What is `ConcurrentHashMap` vs `Collections.synchronizedMap`?

**A:**

```java
// synchronizedMap — wraps entire map in single lock
Map<String, Integer> syncMap = Collections.synchronizedMap(new HashMap<>());
// Every operation: single lock → contention under concurrency

// ConcurrentHashMap — segment-level locking (Java 7) / CAS (Java 8)
ConcurrentHashMap<String, Integer> chm = new ConcurrentHashMap<>();
// Reads: lock-free
// Writes: bucket-level locking → much less contention

// Atomic operations (thread-safe)
chm.putIfAbsent("key", 0);
chm.computeIfAbsent("key", k -> expensiveCompute(k));
chm.compute("counter", (k, v) -> v == null ? 1 : v + 1);
chm.merge("counter", 1, Integer::sum);
```

**Use `ConcurrentHashMap`** for concurrent read-write access. Use `Collections.synchronizedMap` when you need to synchronize compound operations (iterate + modify) with external locking.

---

### 9. What are generics and type erasure?

**A:**

```java
// Generic class
class Box<T> {
    private T value;
    Box(T value) { this.value = value; }
    T get() { return value; }
}

Box<String> stringBox = new Box<>("hello");
Box<Integer> intBox = new Box<>(42);

// Generic method
<T extends Comparable<T>> T max(T a, T b) {
    return a.compareTo(b) >= 0 ? a : b;
}

// Wildcards
void printList(List<?> list) { ... }              // unknown type
void addNumbers(List<? extends Number> list) { }  // Number or subtype (read-only)
void fillList(List<? super Integer> list) { }     // Integer or supertype (write-ok)

// Type erasure — generics are compile-time only; runtime has no type info
// List<String> and List<Integer> are both just List at runtime
// Can't do: new T(), instanceof T, T.class
```

---

### 10. What are the `Comparable` contract and `equals`/`hashCode` contract?

**A:**

**equals/hashCode contract:**
- If `a.equals(b)` → `a.hashCode() == b.hashCode()` (MUST)
- If `a.hashCode() == b.hashCode()` → `a.equals(b)` may or may not be true

```java
class Point {
    int x, y;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Point p)) return false;
        return x == p.x && y == p.y;
    }

    @Override
    public int hashCode() {
        return Objects.hash(x, y); // consistent with equals
    }
}
```

**Breaking the contract** → `HashMap`/`HashSet` will lose your object or create duplicates.

---

### 11. What is the difference between `Iterator` and `ListIterator`?

**A:**

```java
List<String> list = new ArrayList<>(List.of("a", "b", "c"));

// Iterator — forward only, can remove
Iterator<String> it = list.iterator();
while (it.hasNext()) {
    String s = it.next();
    if (s.equals("b")) it.remove(); // safe removal during iteration
}

// ListIterator — bidirectional, can add/set/remove
ListIterator<String> lit = list.listIterator();
while (lit.hasNext()) {
    String s = lit.next();
    lit.set(s.toUpperCase()); // replace current
}
while (lit.hasPrevious()) {
    System.out.println(lit.previous());
}

// Enhanced for = iterator under the hood
// Don't modify list inside enhanced for — ConcurrentModificationException
```

---

### 12. What is `volatile` and when do you use it?

**A:** `volatile` ensures that reads/writes to a variable go directly to main memory — not cached in CPU registers or thread-local caches:

```java
class StopFlag {
    private volatile boolean stopped = false; // without volatile, loop may never see true

    void stop() { stopped = true; }

    void run() {
        while (!stopped) { // reads fresh value from main memory
            doWork();
        }
    }
}
```

**`volatile` guarantees:**
- Visibility — changes visible across threads
- Ordering — no instruction reordering around volatile reads/writes

**`volatile` does NOT guarantee:**
- Atomicity — `count++` is still a race condition even with `volatile`

```java
// Use AtomicInteger for atomic compound ops
AtomicInteger counter = new AtomicInteger(0);
counter.incrementAndGet(); // atomic
counter.compareAndSet(expected, newValue); // CAS
```

---

### 13. What is the `synchronized` keyword?

**A:**

```java
class Counter {
    private int count = 0;

    // Synchronized method — locks on 'this'
    synchronized void increment() {
        count++;
    }

    // Synchronized block — locks on specific object (finer granularity)
    void addMany(int n) {
        synchronized (this) {
            count += n;
        }
    }

    // Static synchronized — locks on the Class object
    private static int instances = 0;
    static synchronized void registerInstance() {
        instances++;
    }
}
```

**Key properties:**
- Only one thread holds the lock at a time
- Reentrant — a thread can re-acquire a lock it already holds
- Guarantees visibility (like `volatile`) + atomicity

---

### 14. What are `Runnable`, `Callable`, `Future`, and `CompletableFuture`?

**A:**

```java
// Runnable — no return, no checked exception
Runnable r = () -> System.out.println("running");
new Thread(r).start();

// Callable — returns a value, can throw checked exception
Callable<String> c = () -> fetchFromDatabase();

// ExecutorService + Future
ExecutorService executor = Executors.newFixedThreadPool(4);
Future<String> future = executor.submit(c);
String result = future.get(5, TimeUnit.SECONDS); // blocking wait

// CompletableFuture — composable async (Java 8+)
CompletableFuture<String> cf = CompletableFuture
    .supplyAsync(() -> fetchUser(id))          // async
    .thenApply(user -> user.getName())          // transform
    .thenCompose(name -> lookupOrders(name))    // flatMap
    .exceptionally(ex -> "fallback")            // error handling
    .whenComplete((result, ex) -> log(result)); // always runs

// Combine
CompletableFuture<String> user  = CompletableFuture.supplyAsync(() -> fetchUser());
CompletableFuture<String> prefs = CompletableFuture.supplyAsync(() -> fetchPrefs());
CompletableFuture.allOf(user, prefs)
    .thenRun(() -> combine(user.join(), prefs.join()));
```

---

### 15. What are design patterns commonly asked in Java interviews?

**A:**

**Singleton:**
```java
public class Singleton {
    private static volatile Singleton instance;
    private Singleton() {}
    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) instance = new Singleton(); // double-checked locking
            }
        }
        return instance;
    }
    // Better: use enum singleton or Bill Pugh (static holder)
}
```

**Builder:**
```java
class Person {
    final String name; final int age; final String email;
    private Person(Builder b) { name = b.name; age = b.age; email = b.email; }
    static class Builder {
        String name; int age; String email;
        Builder name(String n) { name = n; return this; }
        Builder age(int a) { age = a; return this; }
        Builder email(String e) { email = e; return this; }
        Person build() { return new Person(this); }
    }
}
Person p = new Person.Builder().name("Alice").age(30).build();
```

**Factory:**
```java
interface Notification { void send(String msg); }
class EmailNotification implements Notification { ... }
class SMSNotification implements Notification { ... }

class NotificationFactory {
    static Notification create(String type) {
        return switch(type) {
            case "email" -> new EmailNotification();
            case "sms"   -> new SMSNotification();
            default      -> throw new IllegalArgumentException(type);
        };
    }
}
```

---

### 16. What is `var` (local variable type inference, Java 10+)?

**A:**

```java
// var infers the type from the right-hand side
var list = new ArrayList<String>(); // ArrayList<String>
var map  = new HashMap<String, List<Integer>>(); // inferred
var name = "Alice"; // String

// In enhanced for
for (var entry : map.entrySet()) {
    System.out.println(entry.getKey() + ": " + entry.getValue());
}

// NOT allowed:
// var x;            // no initializer
// var x = null;     // can't infer type
// var[] arr;        // no array declaration
// method params     // params can't use var

// var is not a keyword — it's a reserved type name
var var = "valid field name?"; // No — 'var' as variable name is allowed but confusing
```

---

### 17. What are text blocks (Java 15+)?

**A:**

```java
// Before text blocks
String json = "{\n" +
              "  \"name\": \"Alice\",\n" +
              "  \"age\": 30\n" +
              "}";

// Text block — triple-quoted, preserves formatting
String json = """
        {
          "name": "Alice",
          "age": 30
        }
        """;

// SQL
String sql = """
        SELECT u.name, o.total
        FROM users u
        JOIN orders o ON o.user_id = u.id
        WHERE u.is_active = true
        ORDER BY o.created_at DESC
        """;

// Indentation stripped based on the closing """
// \n is embedded; use \<newline> to suppress line break
```

---

### 18. What is the difference between `throw` and `throws`?

**A:**

```java
// throw — actually throws an exception at runtime
void validate(int age) {
    if (age < 0) throw new IllegalArgumentException("Age cannot be negative: " + age);
}

// throws — declares that a method MAY throw a checked exception
void readFile(String path) throws IOException, FileNotFoundException {
    // ...
}

// You can declare unchecked exceptions in throws (but not required)
void risky() throws RuntimeException { ... }

// Custom exception
class OrderNotFoundException extends RuntimeException { // unchecked
    OrderNotFoundException(String orderId) {
        super("Order not found: " + orderId);
    }
}

class InsufficientFundsException extends Exception { // checked
    final double amount;
    InsufficientFundsException(double amount) {
        super("Insufficient funds: need " + amount);
        this.amount = amount;
    }
}
```

---

### 19. What is the `Iterable` interface and how do you implement it?

**A:**

```java
class Range implements Iterable<Integer> {
    private final int start, end;

    Range(int start, int end) {
        this.start = start;
        this.end = end;
    }

    @Override
    public Iterator<Integer> iterator() {
        return new Iterator<>() {
            int current = start;

            @Override public boolean hasNext() { return current < end; }
            @Override public Integer next() {
                if (!hasNext()) throw new NoSuchElementException();
                return current++;
            }
        };
    }
}

// Now usable in enhanced for loop
for (int i : new Range(1, 6)) {
    System.out.println(i); // 1 2 3 4 5
}
```

---

### 20. What are common Java 8+ features?

**A:**

```java
// Default and static interface methods
interface Logger {
    void log(String msg);
    default void logError(String msg) { log("ERROR: " + msg); } // default impl
    static Logger noOp() { return msg -> {}; }                   // factory
}

// Stream.of, Stream.iterate, Stream.generate
Stream.of(1, 2, 3)
Stream.iterate(0, n -> n + 2).limit(5)  // 0, 2, 4, 6, 8
Stream.generate(Math::random).limit(10)

// Map improvements
map.forEach((k, v) -> System.out.println(k + "=" + v));
map.getOrDefault("missing", 0);
map.computeIfAbsent("key", k -> new ArrayList<>());
map.merge("count", 1, Integer::sum);

// Collectors
Collectors.toUnmodifiableList() // Java 10
Collectors.counting()
Collectors.summarizingInt(String::length)
Collectors.toMap(Person::getName, Person::getAge)
Collectors.groupingBy(Person::getDept, Collectors.counting())

// LocalDate / LocalTime / LocalDateTime (immutable, thread-safe)
LocalDate date = LocalDate.now();
LocalDate next = date.plusDays(7);
DateTimeFormatter fmt = DateTimeFormatter.ofPattern("yyyy-MM-dd");
String formatted = date.format(fmt);
```
