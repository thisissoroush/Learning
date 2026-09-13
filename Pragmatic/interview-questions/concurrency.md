# ⚡ Concurrency & Parallelism — Interview Questions

Language-agnostic concepts. The most misunderstood topic in backend interviews.

---

### 1. What is the difference between concurrency and parallelism?

**A:**

- **Concurrency** — multiple tasks make progress by interleaving execution on one or more CPUs. About *dealing with* many things at once (structure).
- **Parallelism** — multiple tasks literally execute simultaneously on multiple CPUs. About *doing* many things at once (execution).

```
Concurrency (1 CPU):
  Task A: ----run----pause--------run----
  Task B: ----------run----pause----run--

Parallelism (2 CPUs):
  CPU1 Task A: ----run----run----run----
  CPU2 Task B: ----run----run----run----

Both: concurrent tasks executing in parallel
```

**Rob Pike (Go co-creator):** "Concurrency is about structure, parallelism is about execution. Concurrency enables parallelism, but they are not the same thing."

---

### 2. What is the difference between a process and a thread?

**A:**

| | Process | Thread |
|--|---------|--------|
| Memory | Own address space (isolated) | Shared address space |
| Communication | IPC (pipes, sockets, shared memory) | Shared memory directly |
| Creation cost | High (new address space, page tables) | Low (new stack, registers) |
| Fault isolation | A crash doesn't affect other processes | A crash kills the entire process |
| Context switch | Expensive | Cheaper |
| Example | `fork()`, separate programs | `pthread`, Java Thread |

---

### 3. What is a race condition?

**A:** A race condition occurs when the outcome of a program depends on the relative timing or ordering of multiple threads accessing shared state.

```python
# Race condition example
balance = 0

def deposit(amount):
    global balance
    # NOT ATOMIC: read → compute → write (three steps)
    temp = balance      # thread A reads 0
                        # thread B reads 0 (before A writes!)
    temp += amount      # thread A: 0 + 100 = 100
                        # thread B: 0 + 200 = 200
    balance = temp      # thread A writes 100
                        # thread B writes 200 ← 100 is lost!

# Expected: balance = 300 after both deposits
# Actual:   balance = 100 or 200 depending on timing

# Fix: atomic operation or lock
import threading
lock = threading.Lock()

def deposit_safe(amount):
    global balance
    with lock:
        balance += amount  # protected: only one thread at a time
```

---

### 4. What is a deadlock and how do you prevent it?

**A:** A deadlock occurs when two or more threads are permanently blocked, each waiting for a resource held by another.

```
Deadlock conditions (all four must hold):
1. Mutual exclusion — resource held by only one thread at a time
2. Hold and wait — thread holds resources while waiting for others
3. No preemption — resources cannot be forcibly taken
4. Circular wait — A waits for B, B waits for A

Example:
  Thread 1: lock(A), then try lock(B) ← blocked by Thread 2
  Thread 2: lock(B), then try lock(A) ← blocked by Thread 1
  → Deadlock!
```

```python
# Prevention — consistent lock ordering (break circular wait)
# ALWAYS acquire locks in the same order across ALL threads

# BAD — threads can acquire in different order
def transfer_bad(from_acc, to_acc, amount):
    with from_acc.lock:           # Thread A: locks account 1
        with to_acc.lock:         # Thread A: waits for account 2
            transfer(from_acc, to_acc, amount)

# Thread B: locks account 2, waits for account 1 → DEADLOCK

# GOOD — sort by account ID, always lock lower ID first
def transfer_safe(from_acc, to_acc, amount):
    first, second = sorted([from_acc, to_acc], key=lambda a: a.id)
    with first.lock:
        with second.lock:
            transfer(from_acc, to_acc, amount)
# Now both threads always lock in the same order → no circular wait
```

**Other prevention strategies:** Lock timeout (`tryLock(timeout)`), lock-free algorithms, immutable data.

---

### 5. What is starvation?

**A:** A thread is perpetually denied the resources it needs because other threads keep getting priority.

```
Starvation example:
  Low-priority thread waits for a lock
  High-priority threads keep acquiring the lock first
  → Low-priority thread waits forever (starves)

vs Deadlock: deadlock = no thread makes progress
vs Starvation: other threads make progress, starved thread doesn't

Prevention:
  - Fair locks (FIFO ordering — threads served in arrival order)
  - Aging: gradually increase priority of waiting threads
  - Priority inversion avoidance
```

---

### 6. What is a Mutex? What is a Semaphore?

**A:**

**Mutex (Mutual Exclusion Lock):**
```
- Binary lock: locked or unlocked
- Only the thread that locked it can unlock it (ownership)
- Used to protect a critical section (one thread at a time)

lock()    → enter critical section
unlock()  → leave critical section

"I own the bathroom key — no one else can enter until I leave"
```

**Semaphore:**
```
- Counter-based: initialized to N
- Any thread can signal (increment) or wait (decrement)
- No ownership — one thread can signal, another can wait
- Binary semaphore (N=1) ≈ mutex but without ownership
- Counting semaphore (N>1): limits concurrent access to N threads

Use: connection pool (max 10 connections), rate limiting
"10 parking spaces — take a ticket to enter, return ticket to leave"
```

```python
import threading

# Mutex
mutex = threading.Lock()
with mutex:  # auto-releases even on exception
    critical_section()

# Semaphore (max 5 concurrent DB connections)
db_semaphore = threading.Semaphore(5)
with db_semaphore:
    conn = get_db_connection()
    query(conn)
```

---

### 7. What are atomic operations?

**A:** Operations that complete as a single, indivisible step — no other thread can observe an intermediate state.

```java
// NOT atomic — read-modify-write is three steps
int counter = 0;
counter++;  // reads counter, adds 1, writes back — race condition

// Atomic — hardware-guaranteed single operation
import java.util.concurrent.atomic.AtomicInteger;

AtomicInteger counter = new AtomicInteger(0);
counter.incrementAndGet();  // atomic — no lock needed
counter.addAndGet(5);
counter.compareAndSet(10, 20);  // CAS: set to 20 only if currently 10
```

**Compare-And-Swap (CAS):** The foundation of lock-free algorithms.
```
while (true) {
    int expected = counter.get();
    int newValue = expected + 1;
    if (counter.compareAndSet(expected, newValue)) break; // retry if failed
}
```

---

### 8. What is thread safety?

**A:** Code is thread-safe if it functions correctly when executed by multiple threads simultaneously, without requiring additional synchronization from the caller.

**Strategies for thread safety:**

1. **Immutability** — immutable objects are thread-safe by design (no state to corrupt)
2. **Confinement** — keep mutable state within a single thread (ThreadLocal, actor model)
3. **Synchronization** — mutex, synchronized, locks
4. **Atomic variables** — hardware-level atomics for simple counters/flags
5. **Thread-safe collections** — ConcurrentHashMap, CopyOnWriteArrayList, BlockingQueue
6. **Lock-free algorithms** — CAS loops (complex but high performance)

```python
# NOT thread-safe
cache = {}
def get_or_compute(key):
    if key not in cache:  # Thread A checks — not in cache
                          # Thread B checks — not in cache
        result = expensive_compute(key)
        cache[key] = result  # Both compute and store — duplicate work, possible race
    return cache[key]

# Thread-safe with lock
lock = threading.Lock()
def get_or_compute_safe(key):
    with lock:  # Only one thread at a time
        if key not in cache:
            cache[key] = expensive_compute(key)
        return cache[key]
```

---

### 9. What is the Producer-Consumer pattern?

**A:** Producers generate data; consumers process it. A bounded queue between them decouples production rate from consumption rate and provides backpressure.

```python
import queue, threading

class Producer(threading.Thread):
    def __init__(self, q: queue.Queue):
        super().__init__()
        self.q = q

    def run(self):
        while True:
            item = generate_item()
            self.q.put(item)         # blocks if queue is full (backpressure)

class Consumer(threading.Thread):
    def __init__(self, q: queue.Queue):
        super().__init__()
        self.q = q

    def run(self):
        while True:
            item = self.q.get()      # blocks if queue is empty
            process(item)
            self.q.task_done()

# Bounded queue — prevents producer from overwhelming consumer
q = queue.Queue(maxsize=100)

producers = [Producer(q) for _ in range(2)]
consumers = [Consumer(q) for _ in range(4)]

for t in producers + consumers: t.start()
```

---

### 10. What is the Actor model?

**A:** Each "actor" is an independent unit with its own state, communicating exclusively through message passing. No shared memory between actors → no shared-state concurrency bugs.

```
Actor A ──message──→ Actor B mailbox → Actor B processes sequentially
                                      → Actor B sends reply to Actor C

Properties:
  - Each actor has a mailbox (message queue)
  - Actors process one message at a time (no internal races)
  - No shared memory between actors
  - Failure isolation — a crashed actor doesn't crash others

Implementations: Akka (Java/Scala), Erlang/OTP, Orleans (.NET), Proto.Actor
```

---

### 11. What is optimistic vs pessimistic concurrency?

**A:**

**Pessimistic concurrency:** Assumes conflicts will happen — lock the resource before access. Use when conflicts are frequent.
```sql
-- Lock row for update (no one else can read or write until transaction commits)
SELECT * FROM orders WHERE id = 42 FOR UPDATE;
UPDATE orders SET status = 'shipped' WHERE id = 42;
COMMIT;
```

**Optimistic concurrency:** Assumes conflicts are rare — read freely, check for conflict at write time. Use when conflicts are infrequent (most reads).
```python
# Read
order = db.get(42)
version = order.version

# Process
order.status = "shipped"

# Write — check if version changed (someone else modified it)
rows_affected = db.execute(
    "UPDATE orders SET status=? WHERE id=42 AND version=?",
    ("shipped", version)
)
if rows_affected == 0:
    raise ConflictException("Order was modified concurrently")
# Retry or return conflict to caller
```

---

### 12. What is async programming and how does it differ from multithreading?

**A:**

**Multithreading:** Multiple OS threads run concurrently. Context switching between threads is managed by the OS scheduler. Good for CPU-bound work.

**Async (cooperative multitasking):** Single thread runs tasks, voluntarily yields control when waiting for I/O. The event loop runs the next ready task. Good for I/O-bound work.

```python
# Async — one thread, many tasks, non-blocking I/O
import asyncio

async def fetch_user(id: int):
    await asyncio.sleep(1)  # yields control; event loop runs other tasks
    return {"id": id}

async def main():
    # Concurrent without threads — all run "simultaneously" in one thread
    user1, user2, user3 = await asyncio.gather(
        fetch_user(1),
        fetch_user(2),
        fetch_user(3),
    )
    # All three start immediately, total time ≈ 1s (not 3s)

# vs Synchronous:
def fetch_user_sync(id): time.sleep(1); return {"id": id}
# fetch_user_sync(1), fetch_user_sync(2), fetch_user_sync(3) → 3s total
```

**Rule of thumb:**
- I/O-bound (network, disk) → async or multithreading (either works)
- CPU-bound (computation) → multiprocessing (multiple CPU cores)

---

### 13. What is the memory visibility problem?

**A:** Modern CPUs cache memory values in CPU registers or L1/L2 cache. Without synchronization, one thread's write may not be visible to another thread.

```java
class SharedState {
    private boolean running = true;  // not volatile!

    void stop()   { running = false; }  // Thread A writes false
    void execute() {
        while (running) {  // Thread B may NEVER see false
            doWork();       // because running is cached in Thread B's register
        }
    }
}

// Fix: volatile forces reads/writes to go to main memory
private volatile boolean running = true;
// OR: use AtomicBoolean, OR: synchronize the method
```

**Java Memory Model guarantees visibility through:**
- `volatile` fields
- `synchronized` blocks
- `java.util.concurrent.atomic` classes
- Thread start/join

---

### 14. What is a condition variable / monitor?

**A:** A condition variable allows a thread to wait for a specific condition to become true, atomically releasing the lock while waiting.

```python
import threading

class BoundedBuffer:
    def __init__(self, capacity: int):
        self.buffer = []
        self.capacity = capacity
        self.lock = threading.Lock()
        self.not_full  = threading.Condition(self.lock)
        self.not_empty = threading.Condition(self.lock)

    def put(self, item):
        with self.not_full:
            while len(self.buffer) == self.capacity:
                self.not_full.wait()  # releases lock, waits, re-acquires on wake
            self.buffer.append(item)
            self.not_empty.notify()  # wake one waiting consumer

    def get(self):
        with self.not_empty:
            while len(self.buffer) == 0:
                self.not_empty.wait()
            item = self.buffer.pop(0)
            self.not_full.notify()  # wake one waiting producer
            return item
```

---

### 15. What is a concurrent payment scenario and how do you handle it?

**A:** A classic senior-level question: "User A and User B simultaneously try to withdraw $500 from an account with $700 balance."

```
Without protection:
  Thread A reads balance = 700
  Thread B reads balance = 700
  Thread A: 700 - 500 = 200, writes 200
  Thread B: 700 - 500 = 200, writes 200
  Result: balance = 200 (should be -300! $500 lost)

Solution 1: Pessimistic locking (database FOR UPDATE)
  Thread A: SELECT FOR UPDATE → locks row, reads 700
  Thread B: SELECT FOR UPDATE → blocks (waits for A)
  Thread A: withdraw 500, balance = 200, COMMIT → releases lock
  Thread B: reads fresh balance 200, 200 < 500 → REJECT
  Result: correct, one succeeds, one fails

Solution 2: Optimistic locking (version column)
  Thread A reads: balance=700, version=1
  Thread B reads: balance=700, version=1
  Thread A: UPDATE accounts SET balance=200, version=2 WHERE id=X AND version=1 → 1 row affected
  Thread B: UPDATE accounts SET balance=200, version=2 WHERE id=X AND version=1 → 0 rows affected (A changed it)
  Thread B: retry → reads balance=200, 200 < 500 → REJECT
  Result: correct

Solution 3: Serializable transaction isolation
  DB guarantees that concurrent transactions are serialized — one runs as if the other finished first
```
