# Chapter 6 — Object References, Mutability, and Recycling

> *"Variables are not boxes — they are labels attached to objects."*

---

## 🎯 Core Concept

Python variables are references, not containers. Misunderstanding this leads to subtle bugs with aliases, mutability, and garbage collection. This chapter clarifies identity vs. equality, shallow vs. deep copy, and how Python manages object lifetimes.

---

## 📦 Variables Are Not Boxes

```
Wrong mental model (Java/C-style):
  x = [1, 2, 3]
  [1,2,3] stored IN x

Correct mental model:
  [1, 2, 3] object exists in memory
  x is a LABEL (reference) attached to that object

a = [1, 2, 3]
b = a           # b is another label for the SAME list

b.append(4)
print(a)        # [1, 2, 3, 4] — a and b point to the same object!
```

```
Memory:
  a ──────┐
           ↓
          [1, 2, 3, 4]  ← one list object
  b ──────┘
```

---

## 🔍 Identity, Equality, and Aliases

```python
# == tests VALUE equality (__eq__)
# is  tests IDENTITY (same object in memory, same id())

a = [1, 2, 3]
b = [1, 2, 3]
a == b    # True  — same value
a is b    # False — different objects

a = [1, 2, 3]
b = a           # alias — same object
a == b    # True
a is b    # True
id(a) == id(b)  # True

# The only objects you should compare with 'is':
x is None       # True
x is not None
x is True
x is NotImplemented
```

---

## 📋 Copies Are Shallow by Default

```python
# Shallow copy — new outer container, shared inner objects
l1 = [[1, 2], [3, 4], [5, 6]]
l2 = list(l1)           # or l1.copy() or l1[:]

l1[0] is l2[0]          # True — inner lists are SHARED
l2[0].append(99)
l1                       # [[1, 2, 99], [3, 4], [5, 6]] — l1 affected!

# Shallow copy is fine for flat lists of immutables
nums = [1, 2, 3]
nums_copy = nums[:]
nums_copy[0] = 99
nums    # [1, 2, 3] — unaffected

# Deep copy — fully independent, recursively copied
import copy
l3 = copy.deepcopy(l1)
l3[0].append(0)
l1    # unchanged — l3 is fully independent

# Deep copy handles cycles
a = [1, 2]
a.append(a)             # self-referential!
b = copy.deepcopy(a)    # handles cycles without infinite recursion
```

---

## 🔄 Function Parameters as References

```python
# Python passes OBJECT REFERENCES — neither "by value" nor "by reference" exactly
# Think: "call by sharing" — function gets a reference to the same object

def append_to(element, to):
    to.append(element)
    return to

my_list = [1, 2, 3]
result = append_to(4, my_list)
my_list   # [1, 2, 3, 4] — modified! same object

# Rebinding the parameter does NOT affect the caller
def try_to_reassign(the_list):
    the_list = [99, 100]   # local rebinding — caller unaffected

my_list = [1, 2, 3]
try_to_reassign(my_list)
my_list    # [1, 2, 3] — unchanged
```

---

## ⚠️ Mutable Default Arguments — Famous Python Gotcha

```python
# DANGEROUS: mutable default is created ONCE at function definition
def add_item(item, collection=[]):   # [] created at def time, shared
    collection.append(item)
    return collection

add_item('a')   # ['a']
add_item('b')   # ['a', 'b']  ← same list!
add_item('c')   # ['a', 'b', 'c']  ← keeps growing

# CORRECT: use None as sentinel, create fresh default each call
def add_item(item, collection=None):
    if collection is None:
        collection = []
    collection.append(item)
    return collection

add_item('a')   # ['a']
add_item('b')   # ['b']  ← fresh list
```

---

## 🗑️ `del` and Garbage Collection

```python
# del removes a REFERENCE (label), not the object
a = [1, 2, 3]
b = a
del a           # removes label 'a'; object still alive (b holds it)
b               # [1, 2, 3] — still accessible via b

# Object collected only when reference count drops to 0
# CPython: reference counting + cyclic GC
# PyPy: different GC

# weakref — reference that doesn't prevent GC
import weakref

class Cheese:
    def __init__(self, kind):
        self.kind = kind
    def __repr__(self):
        return f'Cheese({self.kind!r})'

c = Cheese('Brie')
wref = weakref.ref(c)
wref()          # Cheese('Brie') — still alive
del c
wref()          # None — object was collected

# WeakValueDictionary — values don't prevent GC
cache = weakref.WeakValueDictionary()
```

---

## 🎭 Python's Tricks with Immutables

```python
# Integer caching (-5 to 256)
a = 256
b = 256
a is b    # True — cached

a = 257
b = 257
a is b    # False — not cached (CPython detail, don't rely on it)

# String interning — CPython interns short identifier-like strings
s1 = 'hello'
s2 = 'hello'
s1 is s2    # True (interned)

s1 = 'hello world'
s2 = 'hello world'
s1 is s2    # False (not interned)

# Tuple identity — empty tuple is singleton
() is ()    # True — always the same object
```

---

## 🔑 Key Takeaways

- Variables are labels (references), not containers — `b = a` creates an alias, not a copy
- Use `==` for value equality, `is` only for identity (especially `is None`, `is not None`)
- Assignment to a function parameter rebinds locally — it does NOT modify the caller's variable
- Shallow copy (`.copy()`, `[:]`) shares inner mutable objects — use `deepcopy` when needed
- NEVER use mutable defaults (`def f(x=[])`); use `None` and create fresh inside the function
- `del` removes a reference, not an object — object lives until all references are gone
