# Chapter 13 — Java

> *"Java interviews often focus on the distinctions that trip people up: overload vs. override, checked vs. unchecked exceptions, generics, and collections."*  
> — Gayle Laakmann McDowell

---

## 🎯 Core Concept

The Java chapter targets the nuances that separate candidates who "write Java" from those who **understand it**. These are the concepts that appear as trick questions or implicit assumptions in interview problems.

---

## 🔑 How Java Passes Arguments

```java
// Java is ALWAYS pass-by-value.
// For primitives: copy of the value
// For objects:    copy of the REFERENCE (not the object itself!)

void increment(int x) { x++; }  // does NOT change caller's x

void clearList(List<String> list) {
    list = new ArrayList<>();  // DOES NOT change caller's list!
    // You reassigned the LOCAL reference — caller's reference unchanged
}

void addToList(List<String> list) {
    list.add("hello");  // DOES change caller's list!
    // Both local and caller reference point to the SAME object
}
```

---

## 🔄 Overloading vs. Overriding

```java
// OVERLOADING: same name, different parameters → resolved at COMPILE time
class Printer {
    void print(String s) { System.out.println("String: " + s); }
    void print(int n)    { System.out.println("Int: "    + n); }
}

// OVERRIDING: subclass redefines parent method → resolved at RUNTIME
class Animal {
    void speak() { System.out.println("..."); }
}
class Dog extends Animal {
    @Override
    void speak() { System.out.println("Woof!"); }  // runtime dispatch
}

Animal a = new Dog();
a.speak(); // → "Woof!" (dynamic dispatch, NOT "...")
```

---

## ⚠️ Checked vs. Unchecked Exceptions

```java
// CHECKED: Must be declared in throws clause or caught
// Extends Exception (not RuntimeException)
void readFile(String path) throws IOException {
    // compiler FORCES you to handle this
}

// UNCHECKED: Do NOT need to be declared
// Extends RuntimeException
throw new IllegalArgumentException("x must be positive");
throw new NullPointerException();
throw new ArrayIndexOutOfBoundsException();

// RULE: Checked for recoverable conditions (file not found)
//       Unchecked for programming errors (null deref, bad args)
```

---

## 🔷 Java Generics — Type Erasure

```java
// Generics are erased at compile time — they exist only for type safety
List<String> strings = new ArrayList<>();
// At runtime, this is just List (raw type). JVM doesn't know <String>.

// Type bounds:
<T extends Comparable<T>>  // T must implement Comparable
<T extends Number>          // T must be Number or a subclass

// Wildcards:
List<?>           // unknown type (read-only in most cases)
List<? extends T> // T or any subclass — producer (read)
List<? super T>   // T or any superclass — consumer (write)

// PECS: Producer Extends, Consumer Super
void copy(List<? extends Number> src, List<? super Number> dst) {
    for (Number n : src) dst.add(n);
}
```

---

## 📦 Collections Hierarchy

```
COLLECTION HIERARCHY
──────────────────────────────────────────────────────────
  Iterable
    └── Collection
          ├── List          (ordered, duplicates OK)
          │     ├── ArrayList    (O(1) access, O(n) insert/delete)
          │     └── LinkedList   (O(1) front insert, O(n) access)
          ├── Set           (no duplicates)
          │     ├── HashSet      (O(1) ops, no order)
          │     ├── LinkedHashSet (O(1) ops, insertion order)
          │     └── TreeSet      (O(log n) ops, sorted)
          └── Queue
                ├── ArrayDeque   (stack or queue, use this!)
                └── PriorityQueue (min-heap by default)

  Map (NOT Collection, but part of framework)
    ├── HashMap        (O(1) ops, no order)
    ├── LinkedHashMap  (O(1) ops, insertion order)
    └── TreeMap        (O(log n) ops, sorted keys)
──────────────────────────────────────────────────────────
```

---

## 🔒 equals() and hashCode() Contract

```java
// If you override equals(), you MUST override hashCode().
// If a.equals(b), then a.hashCode() MUST equal b.hashCode().
// (but not vice versa — hash collisions are OK)

class Point {
    int x, y;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Point)) return false;
        Point p = (Point) o;
        return x == p.x && y == p.y;
    }

    @Override
    public int hashCode() {
        return Objects.hash(x, y);  // consistent with equals
    }
}
// If you break this contract, HashSet and HashMap will behave incorrectly!
```

---

## 🧵 Interfaces vs. Abstract Classes

```
INTERFACE:                    ABSTRACT CLASS:
  All methods public            Can have any access modifier
  No state (fields)             Can have instance fields
  Multiple inheritance OK       Single inheritance only
  Good for:                     Good for:
    defining capabilities         sharing implementation
    Runnable, Comparable          Template Method pattern
    Serializable                  base class with hooks

// When to use interface: "CAN DO" relationship
//   A Dog CAN be Comparable, CAN be Serializable
// When to use abstract class: "IS A" relationship
//   A Dog IS AN Animal (shares Animal state and behavior)
```

---

## 💡 Key Takeaways

| Concept | Key Rule |
|---------|---------|
| Pass by value | Objects pass reference copies — reassigning local ref doesn't affect caller |
| Overload vs. Override | Overload = compile-time; Override = runtime dispatch |
| Checked exceptions | Must declare or catch; for recoverable errors |
| Generics type erasure | Types erased at runtime; exist only for compile-time safety |
| PECS | Producer Extends, Consumer Super for wildcards |
| equals/hashCode | Override both or neither; contract must be consistent |
| Interface vs. Abstract | Interface = "can do"; Abstract = "is a" |

---

*[← Chapter 12](19-c-and-cpp.md) | [Back to Index](../README.md) | [Chapter 14 — Databases →](21-databases.md)*
