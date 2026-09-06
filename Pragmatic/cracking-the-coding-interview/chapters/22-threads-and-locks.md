# Chapter 15 — Threads & Locks

> *"Threading bugs are some of the hardest to find. The key: understand race conditions, deadlocks, and livelocks before writing threaded code."*  
> — Gayle Laakmann McDowell

---

## 🎯 Core Concept

Threading questions test your understanding of **shared mutable state**: race conditions, deadlocks, and how synchronization primitives (locks, semaphores, monitors) prevent them.

---

## ⚠️ Race Condition — The Core Problem

```java
// ❌ NOT THREAD-SAFE — race condition
class Counter {
    private int count = 0;
    public void increment() {
        count++;  // NOT atomic! Three steps: read → add → write
        // Two threads can interleave between steps → lost update
    }
}

// ✅ Fix 1: synchronized
public synchronized void increment() { count++; }

// ✅ Fix 2: AtomicInteger (lock-free, faster)
private AtomicInteger count = new AtomicInteger(0);
public void increment() { count.incrementAndGet(); }
```

---

## 🔐 Synchronization Primitives

```java
// SYNCHRONIZED BLOCK
synchronized (lockObject) { sharedData.modify(); }

// REENTRANT LOCK — more control
ReentrantLock lock = new ReentrantLock();
lock.lock();
try { sharedData.modify(); }
finally { lock.unlock(); } // ALWAYS in finally!

// SEMAPHORE — limit to N concurrent threads
Semaphore sem = new Semaphore(3);
sem.acquire();
try { doWork(); }
finally { sem.release(); }
```

---

## 💀 Deadlock — The Classic Interview Topic

```
DEADLOCK: Thread 1 holds A, waits for B.
          Thread 2 holds B, waits for A.
          Neither can proceed.

4 CONDITIONS (all must be true):
  1. Mutual Exclusion:  resource held by one thread only
  2. Hold and Wait:     thread holds while waiting for another
  3. No Preemption:     resources can't be forcibly taken
  4. Circular Wait:     circular chain of threads waiting

PREVENTION (break any one):
  → Lock ordering: always acquire locks A before B (breaks #4)
  → tryLock(timeout): give up if can't acquire (breaks #2)
  → Lock-free structures: ConcurrentHashMap, AtomicInteger
```

```java
// ❌ DEADLOCK: t1 acquires A then waits for B
//              t2 acquires B then waits for A
Thread t1 = new Thread(() -> {
    synchronized (lockA) { synchronized (lockB) { work(); } }
});
Thread t2 = new Thread(() -> {
    synchronized (lockB) { synchronized (lockA) { work(); } }
});

// ✅ FIX: same lock ORDER in both threads
Thread t2 = new Thread(() -> {
    synchronized (lockA) { synchronized (lockB) { work(); } }
});
```

---

## 🍽️ Dining Philosophers Problem

```
5 philosophers, 5 forks in a circle. Each needs 2 forks to eat.

NAIVE → DEADLOCK: Each picks up left fork, waits for right.
                  All 5 wait simultaneously.

SOLUTIONS:
  1. Asymmetric: Last philosopher picks RIGHT fork first.
     Breaks circular wait.

  2. Resource hierarchy: number forks 0–4.
     Always pick lower-numbered fork first.

  3. Limit concurrency: semaphore(4) allows max 4 to try.
     By pigeonhole, at least one can always eat.
```

---

## 🔄 Producer-Consumer with wait/notify

```java
class BoundedBuffer<T> {
    private final Queue<T> q = new LinkedList<>();
    private final int capacity;
    BoundedBuffer(int cap) { this.capacity = cap; }

    public synchronized void produce(T item) throws InterruptedException {
        while (q.size() == capacity) wait();  // full: release lock + sleep
        q.offer(item);
        notifyAll();  // wake waiting consumers
    }

    public synchronized T consume() throws InterruptedException {
        while (q.isEmpty()) wait();  // empty: release lock + sleep
        T item = q.poll();
        notifyAll();  // wake waiting producers
        return item;
    }
}
// wait(): atomically releases lock AND suspends thread
// notifyAll(): safer than notify() — wakes all waiters
```

---

## 💡 Key Takeaways

| Concept | Key Rule |
|---------|---------|
| Race condition | Unsynchronized read-modify-write on shared state |
| `synchronized` | Mutual exclusion; use smallest scope possible |
| `AtomicInteger` | Lock-free counters; prefer over synchronized |
| Deadlock | All 4 conditions must hold; break ANY one to prevent |
| Lock ordering | Always acquire multiple locks in the same order |
| Semaphore | Limits N concurrent threads (vs. lock = 1 at a time) |
| `wait/notify` | Producer-consumer; `wait()` releases the lock |
| `finally` | Always unlock in a finally block |

---

*[← Chapter 14](21-databases.md) | [Back to Index](../README.md) | [Chapter 16 — Moderate Problems →](23-moderate-problems.md)*
