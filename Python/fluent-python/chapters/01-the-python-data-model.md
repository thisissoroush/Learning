# Chapter 1 — The Python Data Model

> *"A Pythonic Card Deck"* — the opening example that reveals everything about how Python works under the hood.

---

## 🎯 Core Concept

The **Python Data Model** is the API that makes your objects behave like built-in types. By implementing *special methods* (dunder methods), your objects integrate seamlessly with the language: `len()`, `for`, `[]`, `+`, `with`, `repr()`, and more all work through this model.

---

## 🃏 A Pythonic Card Deck

```python
import collections

Card = collections.namedtuple('Card', ['rank', 'suit'])

class FrenchDeck:
    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suits = 'spades diamonds clubs hearts'.split()

    def __init__(self):
        self._cards = [Card(rank, suit)
                       for suit in self.suits
                       for rank in self.ranks]

    def __len__(self):
        return len(self._cards)

    def __getitem__(self, position):
        return self._cards[position]

deck = FrenchDeck()

# These all work automatically — no extra code needed:
len(deck)          # 52  →  __len__
deck[0]            # Card(rank='2', suit='spades')  →  __getitem__
deck[-1]           # Card(rank='A', suit='hearts')
deck[12::13]       # all aces (slicing works via __getitem__)

import random
random.choice(deck)     # random card — works because of __getitem__

for card in deck:       # iteration — works via __getitem__
    print(card)

Card('Q', 'hearts') in deck  # membership test — works via __iter__ (falls back to __getitem__)
```

**Key insight:** implementing just `__len__` and `__getitem__` gave us: len(), indexing, slicing, iteration, `in` operator, `reversed()`, `random.choice()`, and `sorted()` — for free.

---

## 🔮 How Special Methods Work

```
User code        Python runtime
───────────────────────────────────
len(obj)    →    obj.__len__()
obj[key]    →    obj.__getitem__(key)
obj + other →    obj.__add__(other)
repr(obj)   →    obj.__repr__()
str(obj)    →    obj.__str__()
bool(obj)   →    obj.__bool__()
iter(obj)   →    obj.__iter__()
next(obj)   →    obj.__next__()
```

Special methods are called **by the Python interpreter**, not directly by user code. You write `len(deck)`, not `deck.__len__()`.

---

## 🧮 Emulating Numeric Types

```python
from math import hypot

class Vector:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Vector({self.x!r}, {self.y!r})'

    def __abs__(self):
        return hypot(self.x, self.y)

    def __bool__(self):
        return bool(abs(self))   # False only if magnitude is 0

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

v1 = Vector(2, 4)
v2 = Vector(3, 1)

v1 + v2     # Vector(5, 5)
v1 * 3      # Vector(6, 12)
abs(v1)     # 4.47...
bool(Vector(0, 0))  # False
repr(v1)    # "Vector(2, 4)"
```

---

## 📋 Overview of Special Methods

```
Category           Methods
────────────────────────────────────────────────────────
String / bytes     __repr__  __str__  __format__  __bytes__
Collection         __len__  __getitem__  __setitem__  __delitem__  __contains__
Iteration          __iter__  __reversed__  __next__
Callable           __call__
Context manager    __enter__  __exit__
Numeric            __add__  __sub__  __mul__  __truediv__  __floordiv__
                   __abs__  __neg__  __pos__  __bool__
Comparison         __lt__  __le__  __eq__  __ne__  __gt__  __ge__
Attribute access   __getattr__  __setattr__  __delattr__  __dir__
Class creation     __init__  __new__  __del__
```

---

## 💡 Why `len()` Is Not a Method

`len(x)` is a built-in function, not `x.len()`, because Python treats it as a special case for performance — CPython can read the size of a built-in collection directly from a C struct field, without a method call. The data model makes this uniform: `len(obj)` calls `obj.__len__()` consistently.

---

## 🔑 Key Takeaways

- The Python Data Model is a framework of special methods that integrate custom objects into the language
- Implement `__repr__` always — it's used in debugging, logging, and the REPL
- Prefer `__bool__` returning `bool(len(self))` so empty objects are falsy
- You write `len(x)`, not `x.__len__()` — let the interpreter call dunder methods
- The power of the data model: a few special methods = dozens of built-in behaviors
