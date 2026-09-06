# Chapter 2 — Linked Lists

> *"Linked lists are where recursion and pointer manipulation meet. Master the runner technique and you've mastered most linked list problems."*  
> — Gayle Laakmann McDowell

---

## 🎯 Core Concept

Linked lists appear in interviews because they test **pointer manipulation, recursion, and two-pointer thinking** simultaneously. The key technique unique to this data structure is the **Runner (Floyd's) technique** — using two pointers moving at different speeds.

---

## 🔗 Anatomy of a Linked List

```
SINGLY LINKED LIST
──────────────────────────────────────────────────────────
  [Head] → [1|→] → [2|→] → [3|→] → [4|null]

  Each node contains:
    data:  the value
    next:  pointer to next node (null at tail)

DOUBLY LINKED LIST
──────────────────────────────────────────────────────────
  [Head] ↔ [1] ↔ [2] ↔ [3] ↔ [4] [Tail]

  Each node contains:
    data:  the value
    next:  pointer to next node
    prev:  pointer to previous node
──────────────────────────────────────────────────────────
```

```java
// Node definition
class ListNode {
    int val;
    ListNode next;
    ListNode(int val) { this.val = val; }
}
```

---

## ⏱️ Complexity: Array vs. Linked List

```
OPERATION        ARRAY    LINKED LIST
──────────────────────────────────────────────────────────
  Access by index   O(1)     O(n)
  Insert at front   O(n)     O(1)   ← LL wins!
  Insert at back    O(1)*    O(1)** ← tie (with tail ptr)
  Delete at front   O(n)     O(1)   ← LL wins!
  Search            O(n)     O(n)
  Memory            compact  extra pointer per node

  * amortized  ** if tail pointer maintained
```

---

## 🏃 The Runner Technique (Floyd's Two-Pointer)

The most important linked list pattern. Two pointers traverse the list at **different speeds**.

### Finding the Middle

```java
// Slow moves 1 step, Fast moves 2 steps.
// When fast reaches end, slow is at the middle.
ListNode findMiddle(ListNode head) {
    ListNode slow = head, fast = head;
    while (fast != null && fast.next != null) {
        slow = slow.next;         // 1 step
        fast = fast.next.next;    // 2 steps
    }
    return slow; // slow is now at the middle
}
```

### Detecting a Cycle (Floyd's Cycle Detection)

```java
// If there's a cycle, fast and slow will eventually meet.
boolean hasCycle(ListNode head) {
    ListNode slow = head, fast = head;
    while (fast != null && fast.next != null) {
        slow = slow.next;
        fast = fast.next.next;
        if (slow == fast) return true; // they met → cycle!
    }
    return false; // fast hit null → no cycle
}
```

### Kth-to-Last Element

```java
// Put fast k steps ahead. When fast hits end, slow is kth-to-last.
ListNode kthToLast(ListNode head, int k) {
    ListNode slow = head, fast = head;
    // Advance fast k steps ahead
    for (int i = 0; i < k; i++) {
        if (fast == null) return null; // list shorter than k
        fast = fast.next;
    }
    // Move both until fast hits end
    while (fast != null) {
        slow = slow.next;
        fast = fast.next;
    }
    return slow;
}
```

---

## 🔄 Reversing a Linked List

Fundamental operation — appears in many problems as a sub-step.

```java
// Iterative reversal: O(n) time, O(1) space
ListNode reverse(ListNode head) {
    ListNode prev = null, curr = head;
    while (curr != null) {
        ListNode next = curr.next; // save next
        curr.next = prev;          // reverse pointer
        prev = curr;               // advance prev
        curr = next;               // advance curr
    }
    return prev; // prev is now the new head
}

// State trace on [1→2→3→null]:
// prev=null, curr=1: next=2, 1→null, prev=1, curr=2
// prev=1,    curr=2: next=3, 2→1,    prev=2, curr=3
// prev=2,    curr=3: next=null, 3→2, prev=3, curr=null
// return 3   →  [3→2→1→null] ✓
```

---

## ⚠️ Common Linked List Mistakes

```
MISTAKE 1: Losing the list by forgetting to save next
  ❌  curr.next = prev; // you just lost the rest of the list!
  ✅  ListNode next = curr.next; curr.next = prev;

MISTAKE 2: Not handling empty list (null head)
  Always check: if (head == null) return ...;

MISTAKE 3: Off-by-one in runner technique
  Draw it out on paper. Check: does fast.next.next exist?

MISTAKE 4: Forgetting to update the tail
  For doubly linked lists: update BOTH next and prev.
```

---

## 🔑 Key Problem Patterns

| Problem | Technique |
|---------|-----------|
| Detect cycle | Floyd's slow/fast pointers |
| Find cycle start | Meet point → reset one to head → advance at same speed |
| Middle of list | Slow/fast pointers |
| Kth-to-last | Two pointers k apart |
| Reverse list | Iterative (prev, curr, next) |
| Merge two sorted lists | Merge sort merge step |
| Check palindrome | Find middle → reverse second half → compare |
| Remove duplicates | HashMap of seen values |

---

## 💡 Key Takeaways

| Concept | Key Point |
|---------|-----------|
| Runner technique | Two pointers at different speeds solves middle, cycle, kth-to-last |
| Reversal | Always save `next` before changing `curr.next` |
| Null checks | Always guard against null head and null next |
| Recursion | Linked lists and recursion pair naturally — think base case = null |
| vs. Arrays | LL wins at front insert/delete; loses at random access |

---

*[← Chapter 1](08-arrays-and-strings.md) | [Back to Index](../README.md) | [Chapter 3 — Stacks & Queues →](10-stacks-and-queues.md)*
