# ☕ Java — Senior Interview Questions

---

### 1. How does the JVM JIT compiler work?

**A:** The JVM interprets bytecode initially, then the JIT compiler compiles hot paths to native machine code:

**Tiers (HotSpot):**
1. Interpreted — all code starts here
2. C1 (client) compiler — fast compilation, basic optimizations
3. C2 (server) compiler — slow compilation, aggressive optimization (inlining, escape analysis, loop unrolling)

**Key optimizations:**
- **Method inlining** — replace method call with body (removes call overhead)
- **Escape analysis** — if object doesn't escape the method, allocate on stack (no GC)
- **Loop unrolling** — repeat loop body multiple times to reduce branch overhead
- **Dead code elimination** — remove provably unused code
- **Devirtualization** — convert virtual dispatch to direct call when type is known

```bash
# JVM diagnostics
-XX:+PrintCompilation           # log compiled methods
-XX:+UnlockDiagnosticVMOptions
-XX:+PrintInlining              # log inlining decisions
-XX:+EliminateAllocations       # scalar replacement (default on)
```

---

### 2. What is the difference between `ReentrantLock` and `synchronized`?

**A:**

| Feature | `synchronized` | `ReentrantLock` |
|---------|---------------|----------------|
| Interruptible | No | Yes (`lockInterruptibly()`) |
| Try-lock | No | Yes (`tryLock(timeout)`) |
| Fairness | No (unfair) | Configurable |
| Multiple conditions | No | Yes (`newCondition()`) |
| Explicit unlock | No (auto) | Required (`unlock()`) |

```java
ReentrantLock lock = new ReentrantLock(true); // fair
Condition notFull  = lock.newCondition();
Condition notEmpty = lock.newCondition();

// Bounded queue with conditions
void put(T item) throws InterruptedException {
    lock.lock();
    try {
        while (queue.size() == capacity) notFull.await();
        queue.offer(item);
        notEmpty.signal();
    } finally {
        lock.unlock(); // ALWAYS unlock in finally
    }
}

// Try without blocking
if (lock.tryLock(100, TimeUnit.MILLISECONDS)) {
    try { doWork(); }
    finally { lock.unlock(); }
} else {
    handleLockUnavailable();
}
```

---

### 3. What is `ThreadLocal` and what are its pitfalls?

**A:** `ThreadLocal` gives each thread its own independent copy of a variable:

```java
// Each thread has its own DateFormat (DateFormat is not thread-safe)
private static final ThreadLocal<SimpleDateFormat> formatter =
    ThreadLocal.withInitial(() -> new SimpleDateFormat("yyyy-MM-dd"));

String format(Date date) {
    return formatter.get().format(date); // thread-local instance
}

// Request context in web apps
public class RequestContext {
    private static final ThreadLocal<String> currentUser = new ThreadLocal<>();
    public static void setUser(String user) { currentUser.set(user); }
    public static String getUser() { return currentUser.get(); }
    public static void clear() { currentUser.remove(); } // IMPORTANT
}
```

**Pitfalls:**
- **Memory leak in thread pools** — threads are reused; if you don't call `remove()`, old values linger
- **Inheritance** — child threads don't inherit `ThreadLocal` values (use `InheritableThreadLocal`)
- **Hidden coupling** — values passed implicitly, hard to trace

---

### 4. How does `CompletableFuture` compare to reactive programming?

**A:**

```java
// CompletableFuture — imperative async, good for simple pipelines
CompletableFuture<User> user  = CompletableFuture.supplyAsync(() -> fetchUser(id));
CompletableFuture<Orders> orders = user.thenCompose(u -> fetchOrders(u.getId()));

// Limitations:
// - No backpressure
// - No built-in retry
// - Not lazy (starts immediately)

// Project Reactor (Spring WebFlux) — reactive, backpressure-aware
Mono<User> userMono = userService.findById(id)
    .timeout(Duration.ofSeconds(3))
    .retry(3)
    .onErrorResume(ex -> Mono.just(User.anonymous()));

Flux<Order> ordersFlux = orderService.findByUser(id)
    .filter(o -> o.getStatus() == ACTIVE)
    .take(10)
    .delayElements(Duration.ofMillis(100))
    .subscribeOn(Schedulers.boundedElastic());

// Flux = 0..N items; Mono = 0..1 item
// subscribe() triggers execution (lazy)
userMono.subscribe(
    user -> handleUser(user),
    error -> handleError(error),
    () -> onComplete()
);
```

---

### 5. What is the memory leak pattern in Java and how do you detect it?

**A:**

**Common memory leak causes:**
```java
// 1. Static collections holding references
class Cache {
    private static Map<String, Object> CACHE = new HashMap<>();
    // Objects never removed → never collected
    // Fix: use WeakHashMap, Caffeine/Guava cache with eviction
}

// 2. ThreadLocal not removed in thread pools
// Fix: always call remove() in finally

// 3. Inner class holding outer reference
class Outer {
    byte[] largeArray = new byte[10_000_000];
    class Inner { /* holds implicit reference to Outer */ }
}
// Fix: make inner class static

// 4. Listeners/callbacks not unregistered
eventBus.register(listener);
// Fix: eventBus.unregister(listener) in cleanup

// 5. Finalize() keeping objects alive
```

**Detection tools:**
```bash
# Heap dump
jmap -dump:format=b,file=heap.hprof <pid>

# Analyze with
# - Eclipse MAT (Memory Analyzer Tool)
# - JVisualVM
# - IntelliJ profiler

# JVM flags
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/tmp/heapdump.hprof

# Monitor GC
-Xlog:gc*:gc.log:time,uptime,level,tags
```

---

### 6. What is the `ForkJoinPool` and how does work stealing work?

**A:**

```java
// ForkJoinPool — designed for divide-and-conquer parallelism
// Work-stealing: idle threads steal tasks from busy threads' queues

class SumTask extends RecursiveTask<Long> {
    private final long[] arr;
    private final int from, to;
    private static final int THRESHOLD = 10_000;

    SumTask(long[] arr, int from, int to) {
        this.arr = arr; this.from = from; this.to = to;
    }

    @Override
    protected Long compute() {
        if (to - from <= THRESHOLD) {
            long sum = 0;
            for (int i = from; i < to; i++) sum += arr[i];
            return sum;
        }
        int mid = (from + to) / 2;
        SumTask left  = new SumTask(arr, from, mid);
        SumTask right = new SumTask(arr, mid, to);
        left.fork();                  // async execute left
        long rightResult = right.compute(); // compute right in current thread
        return left.join() + rightResult;   // wait for left
    }
}

ForkJoinPool pool = ForkJoinPool.commonPool();
long total = pool.invoke(new SumTask(bigArray, 0, bigArray.length));

// parallelStream() uses ForkJoinPool.commonPool() under the hood
```

---

### 7. How do you profile a Java application?

**A:**

**Async-profiler (lowest overhead, most accurate):**
```bash
# CPU profiling
./profiler.sh -d 30 -f cpu.html <pid>

# Allocation profiling
./profiler.sh -e alloc -d 30 -f alloc.html <pid>

# Wall clock (includes I/O waits)
./profiler.sh -e wall -d 30 -f wall.html <pid>
```

**JFR (Java Flight Recorder — built-in):**
```bash
# Start recording
jcmd <pid> JFR.start duration=60s filename=recording.jfr

# Analyze with JMC (Java Mission Control)
```

**JVM flags for allocation tracking:**
```bash
-XX:+UnlockDiagnosticVMOptions
-XX:+PrintTLAB              # thread-local allocation buffer stats
-XX:+FlightRecorder         # always on in Java 11+
```

**Key metrics to investigate:**
- CPU hot methods (flame graph top)
- Allocation pressure (bytes/s allocated)
- Lock contention (`jstack` or async-profiler lock mode)
- GC pause frequency and duration

---

### 8. What is `VarHandle` and how does it compare to `Unsafe`?

**A:**

```java
import java.lang.invoke.VarHandle;
import java.lang.invoke.MethodHandles;

class AtomicCounter {
    private volatile int count;

    private static final VarHandle COUNT;
    static {
        try {
            COUNT = MethodHandles.lookup()
                .findVarHandle(AtomicCounter.class, "count", int.class);
        } catch (NoSuchFieldException | IllegalAccessException e) {
            throw new ExceptionInInitializerError(e);
        }
    }

    int getAndIncrement() {
        return (int) COUNT.getAndAdd(this, 1); // atomic, no lock
    }

    boolean compareAndSet(int expected, int newValue) {
        return COUNT.compareAndSet(this, expected, newValue);
    }
}
```

**VarHandle vs `Unsafe`:**
- `VarHandle` — public API (Java 9+), type-safe, bounds-checked
- `sun.misc.Unsafe` — internal, unchecked, can crash JVM if misused
- Both provide atomic operations: CAS, volatile read/write, acquire/release fences
- VarHandle is the safe, supported replacement for Unsafe in library code

---

### 9. What are Java modules (JPMS — Java 9+)?

**A:**

```java
// module-info.java
module com.myapp.orders {
    requires java.base;                    // implicit, always
    requires java.sql;                     // depends on java.sql module
    requires com.google.gson;              // external dependency

    exports com.myapp.orders.api;          // public API — visible to others
    exports com.myapp.orders.dto to com.myapp.web; // restricted export

    opens com.myapp.orders.model;          // allows reflection (for frameworks)
    opens com.myapp.orders.config to com.google.gson; // restricted opens

    uses com.myapp.payments.PaymentService; // ServiceLoader consumer
    provides com.myapp.payments.PaymentService
        with com.myapp.orders.StripePaymentService; // ServiceLoader provider
}
```

**Key benefits:**
- Strong encapsulation — `internal` packages truly hidden
- Reliable configuration — missing dependencies detected at startup
- Smaller JREs with `jlink`

**Drawbacks:**
- Complexity — most Spring Boot apps use `--add-opens` to bypass restrictions
- Reflection-heavy frameworks need `opens` directives

---

### 10. How does serialization work and what are its pitfalls?

**A:**

```java
// Java serialization — convert object to byte stream
class Order implements Serializable {
    private static final long serialVersionUID = 1L; // version control

    private String id;
    private double total;
    private transient Connection db; // not serialized

    // Custom serialization
    private void writeObject(ObjectOutputStream out) throws IOException {
        out.defaultWriteObject();
        out.writeUTF(encryptedField());
    }

    private void readObject(ObjectInputStream in) throws IOException, ClassNotFoundException {
        in.defaultReadObject();
        this.decryptedField = decrypt(in.readUTF());
    }
}

// Serialize
try (ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("order.ser"))) {
    oos.writeObject(order);
}

// Deserialize
try (ObjectInputStream ois = new ObjectInputStream(new FileInputStream("order.ser"))) {
    Order order = (Order) ois.readObject();
}
```

**Pitfalls:**
- **Security** — deserialization is a common attack vector (`readObject` can execute code); never deserialize untrusted data with Java native serialization
- **Versioning** — changing class without updating `serialVersionUID` breaks deserialization
- **Performance** — Java serialization is slow and verbose

**Prefer:** JSON (Jackson), Protobuf, Avro, Kryo for serialization.

---

### 11. What are common `java.util.concurrent` tools?

**A:**

```java
// CountDownLatch — wait for N operations to complete
CountDownLatch latch = new CountDownLatch(3);
// 3 threads each call latch.countDown() when done
latch.await(); // blocks until count reaches 0

// CyclicBarrier — N threads wait for each other at a point
CyclicBarrier barrier = new CyclicBarrier(3, () -> System.out.println("All ready!"));
barrier.await(); // each thread calls this; all proceed when N threads waiting

// Semaphore — limit concurrent access
Semaphore semaphore = new Semaphore(5); // max 5 concurrent
semaphore.acquire();
try { accessSharedResource(); }
finally { semaphore.release(); }

// Phaser — flexible multi-phase coordination
Phaser phaser = new Phaser(3);
phaser.arriveAndAwaitAdvance(); // wait at phase barrier

// BlockingQueue — thread-safe producer/consumer
BlockingQueue<String> queue = new LinkedBlockingQueue<>(100);
queue.put("item");   // blocks if full
String item = queue.take(); // blocks if empty
queue.offer("item", 1, TimeUnit.SECONDS); // timed offer
queue.poll(1, TimeUnit.SECONDS);          // timed poll
```

---

### 12. What is reflection in Java and what are its performance implications?

**A:**

```java
// Inspect and invoke at runtime
Class<?> clazz = Class.forName("com.example.Person");
Object instance = clazz.getDeclaredConstructor().newInstance();

Field field = clazz.getDeclaredField("name");
field.setAccessible(true); // bypass access control
field.set(instance, "Alice");
System.out.println(field.get(instance));

Method method = clazz.getDeclaredMethod("greet", String.class);
method.setAccessible(true);
String result = (String) method.invoke(instance, "World");

// Annotation processing
for (Method m : clazz.getMethods()) {
    if (m.isAnnotationPresent(RequestMapping.class)) {
        RequestMapping rm = m.getAnnotation(RequestMapping.class);
        registerRoute(rm.value(), m);
    }
}
```

**Performance implications:**
- First access: security checks, class loading overhead
- Subsequent calls: faster but still ~10-100x slower than direct calls
- Use `MethodHandles` for hot paths — nearly direct-call speed
- Spring/JPA use reflection extensively — mitigated by caching method handles

---

### 13. What is a `WeakReference`, `SoftReference`, and `PhantomReference`?

**A:**

```java
// Strong reference — object stays alive as long as ref exists
Object strong = new Object();

// WeakReference — GC can collect it at any time
WeakReference<Object> weak = new WeakReference<>(new Object());
weak.get(); // null after GC

// SoftReference — GC collects when memory is low (before OOM)
SoftReference<byte[]> cache = new SoftReference<>(new byte[10_000_000]);
// Good for memory-sensitive caches

// PhantomReference — get() always returns null; used for cleanup
ReferenceQueue<Object> queue = new ReferenceQueue<>();
PhantomReference<Object> phantom = new PhantomReference<>(object, queue);

// WeakHashMap — entries evicted when keys are GC'd
WeakHashMap<Widget, CachedData> cache = new WeakHashMap<>();
// When widget is GC'd, cache entry auto-removed
```

**Use cases:**
- `WeakReference` — canonical maps, caches where staleness is ok
- `SoftReference` — caches (auto-cleared on memory pressure)
- `PhantomReference` — resource cleanup without finalizers

---

### 14. How do you implement a thread-safe singleton?

**A:**

```java
// 1. Enum singleton (best — thread-safe, serialization-safe, JVM-guaranteed)
public enum Singleton {
    INSTANCE;
    public void doWork() { ... }
}

// 2. Bill Pugh (static holder idiom) — lazy, thread-safe without synchronization
public class Singleton {
    private Singleton() {}
    private static class Holder {
        static final Singleton INSTANCE = new Singleton(); // initialized on first access
    }
    public static Singleton getInstance() { return Holder.INSTANCE; }
}

// 3. Double-checked locking (volatile required!)
public class Singleton {
    private static volatile Singleton instance;
    private Singleton() {}
    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null)
                    instance = new Singleton();
            }
        }
        return instance;
    }
}
```

---

### 15. What is structured concurrency (Java 21)?

**A:** Structured concurrency treats a group of related tasks as a single unit — if one fails, all are cancelled:

```java
import java.util.concurrent.StructuredTaskScope;

String fetchUserAndOrders(long userId) throws Exception {
    try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
        // Fork both tasks
        StructuredTaskScope.Subtask<User> userTask =
            scope.fork(() -> fetchUser(userId));
        StructuredTaskScope.Subtask<List<Order>> ordersTask =
            scope.fork(() -> fetchOrders(userId));

        scope.join();           // wait for both
        scope.throwIfFailed();  // propagate any failure

        // Both succeeded
        return combine(userTask.get(), ordersTask.get());
    }
    // Scope closed — all tasks guaranteed complete or cancelled
}
```

Benefits over `CompletableFuture`:
- Automatic cancellation of siblings on failure
- Thread dump shows clear parent-child task structure
- No leaked threads — scope guarantees cleanup

---

### 16. What are virtual threads (Java 21)?

**A:** Virtual threads are lightweight, JVM-managed threads — millions can exist concurrently:

```java
// Create a virtual thread
Thread.ofVirtual().start(() -> handleRequest());

// ExecutorService with virtual threads
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (int i = 0; i < 100_000; i++) {
        executor.submit(() -> handleRequest()); // 100K virtual threads, not OS threads
    }
}

// Spring Boot 3.2+ — enable globally
# application.properties
spring.threads.virtual.enabled=true
```

**How they work:**
- Virtual threads are mounted on OS threads (carrier threads) only when running
- On blocking I/O (`socket.read()`, DB query), virtual thread unmounts — carrier thread free to run others
- No need for reactive/async programming for I/O-bound concurrency

**Pitfalls:**
- **Thread pinning** — `synchronized` blocks pin virtual thread to carrier; use `ReentrantLock` instead
- Not for CPU-bound work — still limited by CPU cores
- `ThreadLocal` per-virtual-thread works but pool-reuse patterns break

---

### 17. What is the difference between `HashMap`, `TreeMap`, and `LinkedHashMap`?

**A:**

| | `HashMap` | `TreeMap` | `LinkedHashMap` |
|--|-----------|-----------|----------------|
| Order | None | Sorted (natural/Comparator) | Insertion order |
| `get`/`put` | O(1) avg | O(log n) | O(1) avg |
| Null keys | 1 allowed | Not allowed | 1 allowed |
| Implements | Map | SortedMap, NavigableMap | Map |
| Use when | Max performance | Sorted iteration | Ordered iteration |

```java
TreeMap<String, Integer> sorted = new TreeMap<>();
sorted.firstKey(); sorted.lastKey();
sorted.headMap("M");        // keys < "M"
sorted.subMap("A", "M");   // keys in range

LinkedHashMap<String, Integer> lhm = new LinkedHashMap<>(16, 0.75f, true); // access-order LRU
// With access-order=true, can be used as LRU cache:
// override removeEldestEntry to evict
```

---

### 18. How do you implement an LRU cache in Java?

**A:**

```java
// LinkedHashMap access-order approach
class LRUCache<K, V> extends LinkedHashMap<K, V> {
    private final int capacity;

    LRUCache(int capacity) {
        super(capacity, 0.75f, true); // accessOrder = true
        this.capacity = capacity;
    }

    @Override
    protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
        return size() > capacity;
    }
}

LRUCache<String, User> cache = new LRUCache<>(100);
cache.put("user:1", user);
cache.get("user:1"); // marks as recently used

// Thread-safe version
Map<String, User> syncCache = Collections.synchronizedMap(new LRUCache<>(100));

// Production: use Caffeine
Cache<String, User> caffeineCache = Caffeine.newBuilder()
    .maximumSize(1000)
    .expireAfterWrite(5, TimeUnit.MINUTES)
    .recordStats()
    .build();
```

---

### 19. What is the `Executor` framework?

**A:**

```java
// Thread pool types
Executors.newFixedThreadPool(8)        // fixed N threads
Executors.newCachedThreadPool()        // grows as needed, reuses idle
Executors.newSingleThreadExecutor()   // single thread, sequential
Executors.newScheduledThreadPool(4)   // for delayed/periodic tasks
Executors.newVirtualThreadPerTaskExecutor() // Java 21

// Directly: ThreadPoolExecutor for fine control
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    4,                        // corePoolSize
    16,                       // maximumPoolSize
    60L, TimeUnit.SECONDS,    // keepAlive for idle threads beyond core
    new LinkedBlockingQueue<>(1000), // task queue
    new ThreadFactory() {
        int count = 0;
        public Thread newThread(Runnable r) {
            Thread t = new Thread(r);
            t.setName("worker-" + count++);
            t.setDaemon(true);
            return t;
        }
    },
    new ThreadPoolExecutor.CallerRunsPolicy() // rejection: run in caller's thread
);

// Shutdown
executor.shutdown(); // no new tasks, finish existing
executor.awaitTermination(30, TimeUnit.SECONDS);
// or executor.shutdownNow() — interrupt running tasks
```

---

### 20. What are the `Comparator` composition methods?

**A:**

```java
List<Employee> employees = getEmployees();

// Multi-level sort
employees.sort(
    Comparator.comparing(Employee::getDepartment)
              .thenComparing(Employee::getSalary, Comparator.reverseOrder())
              .thenComparing(Employee::getName)
);

// Null-safe
Comparator<Employee> nullSafe = Comparator.comparing(
    Employee::getManager,
    Comparator.nullsFirst(Comparator.naturalOrder())
);

// Custom with key extractor
Comparator<String> byLength = Comparator.comparingInt(String::length)
                                         .thenComparing(Comparator.naturalOrder());

// Reverse
Comparator<Integer> desc = Comparator.<Integer>naturalOrder().reversed();

// Min/Max with comparator
Optional<Employee> highest = employees.stream()
    .max(Comparator.comparingDouble(Employee::getSalary));
