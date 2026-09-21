# Chapter 14 — Inheritance: For Better or Worse

> *"Inheritance is more trouble than it's worth."*

---

## 🎯 Core Concept

Python supports multiple inheritance, but it comes with complexity. This chapter covers the Method Resolution Order (MRO), the dangers of subclassing built-ins, and when to use mixins vs. composition.

---

## 🔝 The `super()` Function

```python
class Base:
    def method(self):
        print('Base.method')

class Sub(Base):
    def method(self):
        super().method()     # delegates to next in MRO — not necessarily Base!
        print('Sub.method')

# super() without args is equivalent to super(Sub, self) — preferred in Python 3
```

---

## 🚫 Subclassing Built-Ins Is Tricky

```python
# Built-in methods (C code) don't call subclass overrides
class DoppelDict(dict):
    def __setitem__(self, key, value):
        super().__setitem__(key, [value] * 2)  # store as doubled list

dd = DoppelDict()
dd['one'] = 1            # calls our __setitem__: {'one': [1, 1]}
dd.update({'two': 2})    # dict.update() calls C-level __setitem__, NOT our override!
dd  # {'one': [1, 1], 'two': 2}  ← update bypassed our override!

# Solution: subclass UserDict, UserList, UserString instead
from collections import UserDict

class DoppelDict(UserDict):
    def __setitem__(self, key, value):
        super().__setitem__(key, [value] * 2)

dd = DoppelDict()
dd['one'] = 1
dd.update({'two': 2})
dd   # {'one': [1, 1], 'two': [2, 2]}  ← both work correctly
```

---

## 🧵 Method Resolution Order (MRO)

```python
# Python uses C3 linearization to determine MRO
class A:
    def ping(self): print('ping:', self)

class B(A):
    def pong(self): print('pong:', self)

class C(A):
    def pong(self): print('PONG:', self)    # different from B.pong

class D(B, C):
    def ping(self): super().ping(); print('post-ping:', self)
    def pingpong(self):
        self.ping()
        super().ping()
        self.pong()
        super().pong()
        C.pong(self)     # bypass MRO — call C's pong directly

D.__mro__
# (<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)

d = D()
d.pong()   # pong: D — uses B.pong (B comes before C in MRO)
C.pong(d)  # PONG: D — explicitly call C.pong
```

```
MRO for D(B, C) where B(A), C(A):
  D → B → C → A → object
```

---

## 🔌 Mixin Classes

```python
# Mixin: provides methods to other classes without being a full class on its own
# No state, no __init__, single responsibility

class CaseInsensitiveMixin:
    """Mixin to make any Mapping case-insensitive."""
    def __getitem__(self, key):
        return super().__getitem__(key.casefold())

    def __contains__(self, key):
        return super().__contains__(key.casefold())

    def get(self, key, default=None):
        return super().get(key.casefold(), default)

class CIDict(CaseInsensitiveMixin, dict):
    pass

d = CIDict({'A': 1, 'B': 2})
d['a']        # 1 — case insensitive
'b' in d      # True

# Mixin rules:
# ✅ No state
# ✅ No __init__
# ✅ Single focused purpose
# ✅ Listed first in class definition (so super() calls reach the real class)
```

---

## 🌍 Multiple Inheritance in the Real World

```python
# Django's Class-Based Views use mixins extensively
class ListView(MultipleObjectMixin, BaseListView):
    pass

class CreateView(SingleObjectTemplateResponseMixin, BaseCreateView):
    pass

# Correct mixin usage:
# Each mixin adds one feature:
#   LoginRequiredMixin — auth check
#   PermissionRequiredMixin — permission check
#   UserPassesTestMixin — custom test

class MyView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'myapp.view_mymodel'
    template_name = 'myapp/page.html'
```

---

## 💡 Coping with Inheritance

```
Prefer composition over inheritance:
  Instead of MyDict(dict): use self._data = {}

Favor object composition:
  class Engine: ...
  class Car:
      def __init__(self):
          self.engine = Engine()   # HAS-A, not IS-A

Use ABCs for explicit interfaces:
  Inherit from ABC to declare what a class MUST implement

Use mixins for code reuse:
  Mixin provides method implementations, not identity

Avoid deep hierarchies:
  Three levels max; more = fragile and hard to debug

Subclass only designed-for-subclassing classes:
  Don't subclass dict, list, str — use UserDict, UserList, UserString
```

---

## 🔑 Key Takeaways

- `super()` follows MRO — not necessarily the direct parent
- Never subclass built-in `dict`, `list`, `str` — use `UserDict`, `UserList`, `UserString`
- MRO (Method Resolution Order) is computed with C3 linearization
- Mixins: no state, no `__init__`, single responsibility, listed first in base classes
- Favor composition over inheritance — it's more flexible and less coupled
- Multiple inheritance is powerful but adds complexity — use sparingly and with clear intent
