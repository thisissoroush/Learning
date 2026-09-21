# Chapter 16 — Operator Overloading

> *"Operator overloading allows user-defined objects to interoperate with infix operators."*

---

## 🎯 Core Concept

Python allows you to define the behavior of operators (`+`, `*`, `==`, `<`, etc.) for your own types by implementing special methods. The key rule: return `NotImplemented` when you can't handle the operation, so Python can try the reflected method on the other operand.

---

## ➕ Overloading `+` for Vector Addition

```python
class Vector:
    def __add__(self, other):
        try:
            pairs = itertools.zip_longest(self, other, fillvalue=0.0)
            return Vector(a + b for a, b in pairs)
        except TypeError:
            return NotImplemented    # let Python try other.__radd__(self)

    def __radd__(self, other):
        return self + other    # delegate: commutative operation

v1 = Vector([1, 2, 3])
v2 = Vector([10, 20, 30])

v1 + v2         # Vector([11, 22, 33])  — calls v1.__add__(v2)
(1, 2, 3) + v1  # Vector([2, 4, 6])    — tuple.__add__ fails, tries v1.__radd__((1,2,3))
v1 + 1          # TypeError (NotImplemented → Python has no other option)
```

---

## ✖️ Scalar Multiplication

```python
class Vector:
    def __mul__(self, scalar):
        try:
            factor = float(scalar)
        except TypeError:
            return NotImplemented
        return Vector(n * factor for n in self)

    def __rmul__(self, scalar):
        return self * scalar    # commutative

v = Vector([1, 2, 3])
v * 3       # Vector([3, 6, 9])
3 * v       # Vector([3, 6, 9]) — calls v.__rmul__(3)
```

---

## @ Matrix Multiplication Operator (Python 3.5+)

```python
class Vector:
    def __matmul__(self, other):
        if isinstance(other, Vector) and len(self) == len(other):
            return sum(a * b for a, b in zip(self, other))
        return NotImplemented

    def __rmatmul__(self, other):
        return self @ other

v1 = Vector([1, 2, 3])
v2 = Vector([4, 5, 6])
v1 @ v2     # 32  (= 1*4 + 2*5 + 3*6 — dot product)
```

---

## ⚖️ Rich Comparison Operators

```python
class Vector:
    def __eq__(self, other):
        if isinstance(other, Vector):
            return len(self) == len(other) and all(a == b for a, b in zip(self, other))
        return NotImplemented    # allow comparison with other types

    def __hash__(self):
        # Required when __eq__ is defined
        hashes = (hash(x) for x in self._components)
        return functools.reduce(operator.xor, hashes, 0)

# Augmented assignment operators
    def __iadd__(self, other):
        # NOT defined → Python falls back to __add__ and rebinds
        # If you want += to work in place, define __iadd__
        ...
```

---

## 📋 Arithmetic Operator Summary

```
Operator  Forward      Reversed     In-place
+         __add__      __radd__     __iadd__
-         __sub__      __rsub__     __isub__
*         __mul__      __rmul__     __imul__
/         __truediv__  __rtruediv__ __itruediv__
//        __floordiv__ __rfloordiv____ifloordiv__
%         __mod__      __rmod__     __imod__
**        __pow__      __rpow__     __ipow__
@         __matmul__   __rmatmul__  __imatmul__
&         __and__      __rand__     __iand__
|         __or__       __ror__      __ior__
^         __xor__      __rxor__     __ixor__
<<        __lshift__   __rlshift__  __ilshift__
>>        __rshift__   __rrshift__  __irshift__
```

---

## 🔑 Key Takeaways

- Return `NotImplemented` (not `raise TypeError`) when you can't handle an operand type — this lets Python try the reflected method
- Define both `__add__` and `__radd__` for commutative operations
- Never modify `self` in `__add__`/`__mul__` — return a new object; in-place is `__iadd__`/`__imul__`
- Always define `__hash__` when you define `__eq__`
- `NotImplemented` is a singleton; `NotImplementedError` is an exception — don't confuse them
