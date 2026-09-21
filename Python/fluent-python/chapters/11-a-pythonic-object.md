# Chapter 11 — A Pythonic Object

> *"Thanks to the Python data model, user-defined types can behave as naturally as the built-in types."*

---

## 🎯 Core Concept

Building a well-behaved Python object means implementing the right special methods so your class integrates naturally with Python's operators, built-in functions, and idioms. This chapter builds a `Vector2d` class step by step.

---

## 🏗️ Object Representations

```python
# Two string representations every class should have:
# __repr__  → unambiguous, developer-facing, ideally eval-able
# __str__   → readable, user-facing (fallback: __repr__)

class Vector2d:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return f'Vector2d({self.x!r}, {self.y!r})'
        # !r applies repr() to the value

    def __str__(self):
        return str(tuple(self))     # delegates to __iter__

    def __bytes__(self):
        return bytes([ord(self.typecode)]) + bytes(array(self.typecode, self))

    def __iter__(self):             # makes unpacking work: x, y = v
        return (i for i in (self.x, self.y))

    def __abs__(self):
        return math.hypot(self.x, self.y)

    def __bool__(self):
        return bool(abs(self))      # False only when magnitude is 0

    def __eq__(self, other):
        return tuple(self) == tuple(other)
```

---

## 🏭 Alternative Constructors

```python
class Vector2d:
    typecode = 'd'   # class attribute used in __bytes__ / frombytes

    @classmethod
    def frombytes(cls, octets):
        typecode = chr(octets[0])
        memv = memoryview(octets[1:]).cast(typecode)
        return cls(*memv)   # cls() not Vector2d() — subclass friendly

# Usage
v = Vector2d(3, 4)
octets = bytes(v)                     # serialise
v2 = Vector2d.frombytes(octets)       # reconstruct
v == v2   # True
```

---

## ⚖️ `classmethod` vs `staticmethod`

```python
class Demo:
    @classmethod
    def klassmeth(*args):
        return args    # first arg is the class itself

    @staticmethod
    def statmeth(*args):
        return args    # no implicit first arg

Demo.klassmeth()       # (<class 'Demo'>,)
Demo.klassmeth('spam') # (<class 'Demo'>, 'spam')
Demo.statmeth()        # ()
Demo.statmeth('spam')  # ('spam',)

# classmethod: used for alternative constructors — gets cls, works with subclasses
# staticmethod: just a plain function that lives in the class namespace
```

---

## 🔐 Hashable Vector2d

```python
class Vector2d:
    def __init__(self, x, y):
        self.__x = float(x)   # private with name mangling
        self.__y = float(y)

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    def __hash__(self):
        return hash((self.x, self.y))   # hash of a tuple of values

    # RULE: if __eq__ is defined, __hash__ must be defined too
    # Objects that compare equal must have the same hash

v = Vector2d(3, 4)
hash(v)                    # some integer
{v}                        # works — can be stored in set
{v: 'point'}               # works — can be dict key
v.x = 9                    # AttributeError — property is read-only (private __x)
```

---

## 🎰 `__slots__` — Memory Optimization

```python
class PixelVector:
    __slots__ = ('__x', '__y')    # store in fixed-size array, not __dict__

    def __init__(self, x, y):
        self.__x = x
        self.__y = y

# Memory savings: ~40-50% for objects with many instances
# Cost: cannot add arbitrary attributes; inheritance issues

import sys
v_normal = Vector2d(1, 2)
v_slotted = PixelVector(1, 2)

sys.getsizeof(v_normal.__dict__)   # ~232 bytes
# No __dict__ for slotted!

# When to use __slots__:
# - Millions of instances (data processing, coordinates, graph nodes)
# - Memory is a constraint
# - Class is essentially final
```

---

## 🎨 Formatted Displays

```python
class Vector2d:
    def __format__(self, fmt_spec=''):
        if fmt_spec.endswith('p'):          # polar coordinates
            fmt_spec = fmt_spec[:-1]
            coords = (abs(self), self.angle())
            outer_fmt = '<{}, {}>'
        else:                               # cartesian
            coords = self
            outer_fmt = '({}, {})'
        components = (format(c, fmt_spec) for c in coords)
        return outer_fmt.format(*components)

v = Vector2d(1, 1)
format(v)           # '(1.0, 1.0)'
format(v, '.3f')    # '(1.000, 1.000)'
format(v, '.3ep')   # '<1.414e+00, 7.854e-01>'  — polar
f'{v!r}'            # 'Vector2d(1.0, 1.0)'
```

---

## 🔑 Key Takeaways

- Always implement `__repr__` — it's used everywhere (REPL, logging, debugging)
- If `__eq__` is defined, define `__hash__` too (or set `__hash__ = None` to make unhashable)
- Use `@classmethod` for alternative constructors; `@staticmethod` rarely (module-level function is clearer)
- Make objects immutable with `@property` + private `__x` naming (name mangling: `_ClassName__x`)
- `__slots__` can halve memory usage for classes with many instances — use only when needed
- `__format__` enables `format(obj, spec)` and f-strings with format specs
