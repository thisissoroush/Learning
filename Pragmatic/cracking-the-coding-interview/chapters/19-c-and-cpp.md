# Chapter 12 — C and C++

> *"C++ gives you enough rope to shoot yourself in the foot. Understanding pointers, memory, and the object model separates strong C++ candidates from weak ones."*  
> — Gayle Laakmann McDowell

---

## 🎯 Core Concept

The C/C++ chapter covers the low-level concepts that C++ interviews focus on: **memory management, pointers, references, virtual dispatch, and smart pointers**. These topics are irrelevant if you're interviewing in Java or Python — but essential for systems, embedded, and game development roles.

---

## 🧠 Memory Layout

```
PROCESS MEMORY MAP (simplified)
──────────────────────────────────────────────────────────
  High address
  ┌─────────────────┐
  │   STACK         │ ← Local variables, function args,
  │   (grows ↓)     │   return addresses. Automatically freed.
  ├─────────────────┤
  │   (free space)  │
  ├─────────────────┤
  │   HEAP          │ ← Dynamic allocation (new / malloc).
  │   (grows ↑)     │   Manually managed — YOU must free!
  ├─────────────────┤
  │   BSS           │ ← Uninitialized global/static variables
  ├─────────────────┤
  │   DATA          │ ← Initialized global/static variables
  ├─────────────────┤
  │   TEXT (code)   │ ← Program instructions (read-only)
  └─────────────────┘
  Low address
──────────────────────────────────────────────────────────
  Stack: fast, size-limited, auto-freed
  Heap:  slow, unlimited, YOU must free → memory leaks if you forget
```

---

## 👉 Pointers vs. References

```cpp
int x = 5;

// POINTER: stores a memory address, can be null, can be reassigned
int* ptr = &x;          // ptr stores the address of x
*ptr = 10;              // dereference: modify x through ptr
ptr = nullptr;          // can be null
int* ptr2 = new int(7); // heap allocation
delete ptr2;            // must free!

// REFERENCE: alias for existing variable, cannot be null, cannot be rebound
int& ref = x;           // ref is another name for x
ref = 20;               // x is now 20
// ref = y;             // ERROR: cannot rebind a reference

// FUNCTION PARAMETER RULES:
void byValue(int n)    { n = 100; }  // copy, original unchanged
void byPointer(int* p) { *p = 100; } // modifies original via deref
void byReference(int& r){ r = 100; } // modifies original directly
```

---

## 🏗️ Classes and Virtual Dispatch

```cpp
class Shape {
public:
    virtual double area() const = 0;    // pure virtual → abstract class
    virtual void draw() const {         // virtual with default impl
        std::cout << "Drawing shape\n";
    }
    virtual ~Shape() {}                 // ALWAYS virtual destructor!
};

class Circle : public Shape {
private:
    double radius;
public:
    Circle(double r) : radius(r) {}
    double area() const override {      // override keyword (C++11)
        return 3.14159 * radius * radius;
    }
};

// Virtual dispatch uses VTABLE:
Shape* s = new Circle(5.0);
s->area();   // calls Circle::area(), not Shape::area()
             // resolved at RUNTIME via vtable pointer
delete s;    // calls ~Circle() then ~Shape() (virtual destructor!)
```

---

## 💾 Smart Pointers (Modern C++ — Prefer Always)

```cpp
#include <memory>

// unique_ptr: sole ownership, auto-deletes when out of scope
std::unique_ptr<int> up = std::make_unique<int>(42);
// *up = 42, auto-freed when up goes out of scope
// Cannot copy, CAN move:
auto up2 = std::move(up); // up is now null

// shared_ptr: shared ownership, reference counted
auto sp1 = std::make_shared<int>(42);
auto sp2 = sp1;  // refcount = 2
// deleted when refcount reaches 0

// weak_ptr: observes a shared_ptr without owning it
// Used to break circular references
std::weak_ptr<int> wp = sp1;
if (auto sp3 = wp.lock()) {  // check if still alive
    std::cout << *sp3;
}

// RULE: Prefer smart pointers over raw new/delete
//       Use unique_ptr by default, shared_ptr when sharing needed
```

---

## 🔑 Key C/C++ Concepts for Interviews

```
VIRTUAL DESTRUCTOR: If a class has ANY virtual methods,
  make the destructor virtual. Otherwise deleting via base
  class pointer causes undefined behavior (partial destruct).

RULE OF THREE (pre-C++11):
  If you define any of: destructor, copy constructor, copy
  assignment operator → define all three.

RULE OF FIVE (C++11+):
  Add: move constructor, move assignment operator.

COPY vs. MOVE:
  Copy:  makes a full duplicate (expensive for large objects)
  Move:  transfers ownership, leaves source in valid empty state

STACK OVERFLOW:
  Infinite recursion or very deep call stacks overflow the stack.
  Typical stack size: 1–8MB.
  Use iteration + explicit stack for deep recursion.
```

---

## 💡 Key Takeaways

| Concept | Key Rule |
|---------|---------|
| Stack vs Heap | Stack = auto-managed, fast; Heap = manual, flexible |
| Pointers vs References | Pointer can be null/reassigned; reference cannot |
| Virtual destructor | Always declare virtual if class has virtual methods |
| Smart pointers | `unique_ptr` by default; `shared_ptr` when sharing needed |
| Virtual dispatch | Resolved at runtime via vtable; enables polymorphism |
| Rule of Three/Five | Define all related special methods or none |
| `override` keyword | Explicit override catches spelling/signature mistakes |

---

*[← Chapter 11](18-testing.md) | [Back to Index](../README.md) | [Chapter 13 — Java →](20-java.md)*
