# Chapter 13 — Interfaces, Protocols, and ABCs

> *"An abstract class represents an interface."*

---

## 🎯 Core Concept

Python offers four ways to define interfaces — from most flexible to most strict: duck typing, goose typing (ABCs), structural typing (Protocol), and static typing. Knowing when to use each makes your code both flexible and safe.

---

## 🗺️ The Typing Map

```
Duck typing  →  Goose typing  →  Static Protocol  →  Inheritance
(runtime)       (runtime ABC)    (static check)      (explicit)

Most flexible ←────────────────────────────────────→ Most strict
```

---

## 🦆 Duck Typing — Protocols at Runtime

```python
# If it walks like a duck and quacks like a duck, it IS a duck
class Struggle:
    def __len__(self):
        return 23

from collections import abc
isinstance(Struggle(), abc.Sized)   # True — ABC checks for __len__

# Python digs sequences — if __getitem__ exists, Python tries it for iteration
class PigLatin:
    def __getitem__(self, pos):
        return 'oink'

for x in PigLatin():    # works! __getitem__(0), __getitem__(1), ...
    print(x)            # until IndexError
    break               # just get first one
```

---

## 🐢 Goose Typing — ABCs

```python
from abc import ABC, abstractmethod

class Tombola(ABC):
    @abstractmethod
    def load(self, iterable): ...     # must implement

    @abstractmethod
    def pick(self): ...               # must implement

    def loaded(self):                 # concrete method — uses abstract ones
        return bool(self.inspect())

    def inspect(self):
        items = []
        while True:
            try:
                items.append(self.pick())
            except LookupError:
                break
        self.load(items)
        return tuple(sorted(items))

# Subclassing an ABC — must implement ALL abstract methods
class BingoCage(Tombola):
    def __init__(self, items):
        self._randomizer = random.SystemRandom()
        self._items = []
        self.load(items)

    def load(self, items):
        self._items.extend(items)
        self._randomizer.shuffle(self._items)

    def pick(self):
        try:
            return self._items.pop()
        except IndexError:
            raise LookupError('pick from empty BingoCage')

cage = BingoCage(range(10))
isinstance(cage, Tombola)   # True
```

---

## 👻 Virtual Subclasses — `register()`

```python
# Register a class as a virtual subclass without inheritance
@Tombola.register
class TomboList(list):
    def pick(self):
        if self:
            position = randbelow(len(self))
            return self.pop(position)
        else:
            raise LookupError('pop from empty TomboList')

    load = list.extend

    def loaded(self):
        return bool(self)

    def inspect(self):
        return tuple(self)

# Now isinstance and issubclass work:
isinstance(TomboList(), Tombola)     # True — via register
issubclass(TomboList, Tombola)       # True — via register
# But Python doesn't check abstract methods on registered classes!
```

---

## 📐 Static Protocols (typing.Protocol)

```python
from typing import Protocol, runtime_checkable

class SupportsLessThan(Protocol):
    def __lt__(self, other: Any) -> bool: ...

# Any class with __lt__ satisfies this — no registration, no inheritance
class Temperature:
    def __init__(self, celsius: float):
        self.celsius = celsius

    def __lt__(self, other: 'Temperature') -> bool:
        return self.celsius < other.celsius

def top(series: Iterable[SupportsLessThan], n: int) -> list[SupportsLessThan]:
    return sorted(series, reverse=True)[:n]

top([Temperature(30), Temperature(20), Temperature(25)], 2)  # mypy: OK

# @runtime_checkable — enables isinstance checks
@runtime_checkable
class Drawable(Protocol):
    def draw(self) -> None: ...

class Circle:
    def draw(self) -> None: print('O')

isinstance(Circle(), Drawable)   # True — checks method presence at runtime
```

---

## 🔑 Key Takeaways

| Approach | When to use | Check happens |
|---------|------------|---------------|
| Duck typing | Flexible code, EAFP style | Runtime (on use) |
| `isinstance(obj, ABC)` | Need explicit runtime check | Runtime (fast C check) |
| `@register` | Third-party classes you can't modify | Runtime |
| `typing.Protocol` | Static checking, structural matching | Type checker / `@runtime_checkable` |
| Inherit ABC | Enforcement + shared concrete methods | Runtime |

- Prefer duck typing for flexibility; use ABCs when enforcement matters
- `Protocol` gives you duck typing WITH static checking — best of both worlds
- Never `isinstance` against concrete classes in library code — use ABCs
- `register()` lets you declare compatibility without touching the third-party class
