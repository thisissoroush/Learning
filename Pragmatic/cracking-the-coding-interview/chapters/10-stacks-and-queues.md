# Chapter 3 — Stacks & Queues

> *"Stacks are for depth-first; queues are for breadth-first. Knowing which one to reach for is half the battle."*  
> — Gayle Laakmann McDowell

---

## 🎯 Core Concept

Stacks and queues are abstract data types with constrained access — and that constraint is exactly what makes them powerful. They enforce an ordering discipline that solves a whole class of problems elegantly.

---

## 📚 Stack — LIFO (Last In, First Out)

```
STACK VISUAL
────────────────────────────────────
  push(1) → [1]
  push(2) → [1, 2]
  push(3) → [1, 2, 3]
  pop()   → returns 3, stack = [1, 2]
  peek()  → returns 2, stack = [1, 2]  (no removal)
  isEmpty → false
────────────────────────────────────
```

```java
// Java: use Deque<T> as a stack (not legacy Stack<T>)
Deque<Integer> stack = new ArrayDeque<>();
stack.push(1);     // push to top
stack.push(2);
int top = stack.pop();   // removes top → 2
int peek = stack.peek(); // reads top → 1 (no removal)
```

**Real-world uses:** Function call stack, undo/redo, DFS traversal, expression evaluation, balanced parentheses.

---

## 🚌 Queue — FIFO (First In, First Out)

```
QUEUE VISUAL
────────────────────────────────────
  offer(1) → [1]
  offer(2) → [1, 2]
  offer(3) → [1, 2, 3]
  poll()   → returns 1, queue = [2, 3]
  peek()   → returns 2, queue = [2, 3] (no removal)
────────────────────────────────────
```

```java
// Java: use Deque<T> as a queue (or LinkedList)
Queue<Integer> queue = new ArrayDeque<>();
queue.offer(1);    // enqueue
queue.offer(2);
int front = queue.poll();  // dequeue → 1
int peek  = queue.peek();  // read front → 2
```

**Real-world uses:** BFS traversal, task scheduling, producer-consumer, level-order tree traversal.

---

## 🔥 Classic Problem: Stack with Min in O(1)

How do you track the minimum element in a stack in O(1) time and space per operation?

```java
// KEY INSIGHT: Maintain a second "min stack" in parallel.
// Every time you push, also push current min onto minStack.

class MinStack {
    private Deque<Integer> stack    = new ArrayDeque<>();
    private Deque<Integer> minStack = new ArrayDeque<>();

    public void push(int val) {
        stack.push(val);
        int newMin = minStack.isEmpty()
            ? val
            : Math.min(val, minStack.peek());
        minStack.push(newMin); // track min AT THIS LEVEL
    }

    public void pop() {
        stack.pop();
        minStack.pop(); // keep in sync!
    }

    public int getMin() {
        return minStack.peek(); // O(1)!
    }
}

// Trace: push(5), push(3), push(7), push(2)
// stack:    [5, 3, 7, 2]
// minStack: [5, 3, 3, 2]
// getMin() → 2 ✓
// pop(), getMin() → 3 ✓ (7 was removed, but min restores!)
```

---

## 🔄 Implement Queue Using Two Stacks

A classic interview problem: simulate a queue using only stacks.

```java
class QueueViaStacks {
    private Deque<Integer> inbox  = new ArrayDeque<>();
    private Deque<Integer> outbox = new ArrayDeque<>();

    public void offer(int val) {
        inbox.push(val); // always enqueue to inbox
    }

    public int poll() {
        if (outbox.isEmpty()) {
            // Lazy transfer: flip inbox into outbox
            while (!inbox.isEmpty())
                outbox.push(inbox.pop());
        }
        return outbox.pop();
    }
}

// WHY IT WORKS:
// inbox:  newest on top  [5, 4, 3, 2, 1] (1 came first)
// flip →
// outbox: oldest on top  [1, 2, 3, 4, 5] → poll() → 1 ✓

// AMORTIZED: each element moves at most twice → O(1) amortized
```

---

## 🎯 Implement Stack Using Two Queues

The reverse problem:

```java
class StackViaQueues {
    private Queue<Integer> q1 = new ArrayDeque<>();
    private Queue<Integer> q2 = new ArrayDeque<>();

    public void push(int val) {
        q2.offer(val);                    // put new element in q2
        while (!q1.isEmpty())             // drain q1 into q2
            q2.offer(q1.poll());
        Queue<Integer> temp = q1;         // swap q1 and q2
        q1 = q2;
        q2 = temp;
        // q1 now has new element at front (LIFO achieved)
    }

    public int pop() { return q1.poll(); }
    public int peek() { return q1.peek(); }
}
```

---

## 🧱 Three Stacks in One Array

One of the book's classic "think outside the box" problems:

```
APPROACH 1: Fixed division (simplest)
  Array of size 3n:
  Stack 1: [0 .. n-1]
  Stack 2: [n .. 2n-1]
  Stack 3: [2n .. 3n-1]
  Drawback: wastes space if stacks are unequal sizes

APPROACH 2: Dynamic (complex, the real answer)
  Use a linked list of "cells" within the array.
  Each cell stores: value + index of previous element.
  Free list tracks unused cells.
  Stacks can grow/shrink dynamically and share space.
```

---

## 💡 Key Takeaways

| Concept | Key Point |
|---------|-----------|
| Stack (LIFO) | DFS, undo, expression evaluation, call stack |
| Queue (FIFO) | BFS, scheduling, producer-consumer |
| MinStack | Shadow min-stack in parallel, pushed/popped in sync |
| Queue via Stacks | Lazy transfer: O(1) amortized via inbox/outbox flip |
| Stack via Queues | Push is O(n), pop/peek are O(1) |
| Java | Use `ArrayDeque` for both stack and queue (not `Stack<T>`) |

---

*[← Chapter 2](09-linked-lists.md) | [Back to Index](../README.md) | [Chapter 4 — Trees & Graphs →](11-trees-and-graphs.md)*
