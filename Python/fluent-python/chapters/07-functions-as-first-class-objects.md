# Chapter 7 — Functions as First-Class Objects

> *"Functions in Python are first-class objects: created at runtime, assigned to variables, passed as arguments, returned from functions."*

---

## 🎯 Core Concept

In Python, functions are objects. They can be stored in variables, passed as arguments, returned from other functions, and stored in data structures. This enables a functional programming style that is often cleaner than OOP alternatives.

---

## 🧩 Functions Are Objects

```python
def factorial(n):
    """Returns n!"""
    return 1 if n < 2 else n * factorial(n - 1)

factorial.__doc__      # 'Returns n!'
type(factorial)        # <class 'function'>
factorial.__class__    # <class 'function'>

# Assign to a variable
fact = factorial
fact(5)               # 120

# Pass as argument
map(factorial, range(6))   # <map object>
list(map(factorial, range(6)))  # [1, 1, 2, 6, 24, 120]

# Store in a data structure
operations = {'double': lambda x: x*2, 'square': lambda x: x**2, 'negate': lambda x: -x}
operations['square'](5)   # 25
```

---

## 🔼 Higher-Order Functions

```python
# Functions that take functions as arguments OR return functions

# sorted with key function
fruits = ['strawberry', 'fig', 'apple', 'cherry', 'raspberry', 'banana']
sorted(fruits, key=len)         # ['fig', 'apple', 'cherry', 'banana', ...]
sorted(fruits, key=reversed)    # sorted by reversed spelling

# map / filter — functional classics
list(map(str.upper, fruits))
list(filter(lambda f: len(f) > 5, fruits))

# Modern replacements (often cleaner in Python)
[f.upper() for f in fruits]               # replaces map
[f for f in fruits if len(f) > 5]         # replaces filter

from functools import reduce
from operator import add
reduce(add, range(100))                    # 4950 — replaces sum
```

---

## ☎️ The Nine Kinds of Callable Objects

```python
# Test with callable()
callable(print)        # True
callable(42)           # False

# 1. User-defined functions
def f(): pass

# 2. Built-in functions
len, abs, open

# 3. Built-in methods
[].append

# 4. Methods (user-defined, defined in a class body)
class C:
    def method(self): pass

# 5. Classes (calling a class invokes __new__ then __init__)
int('42')

# 6. Class instances with __call__
class BingoCage:
    def __init__(self, items):
        self._items = list(items)
        random.shuffle(self._items)

    def pick(self):
        return self._items.pop()

    def __call__(self):
        return self.pick()

bingo = BingoCage(range(10))
bingo()          # calls __call__ — works like a function

# 7. Generator functions (contain yield)
# 8. Native coroutine functions (async def)
# 9. Asynchronous generator functions (async def + yield)
```

---

## 🎛️ Keyword-Only and Positional-Only Parameters

```python
def tag(name, *content, class_=None, **attrs):
    """Build HTML tags."""
    if class_ is not None:
        attrs['class'] = class_
    attr_pairs = (f' {attr}="{value}"' for attr, value in sorted(attrs.items()))
    attr_str = ''.join(attr_pairs)
    if content:
        elements = (f'<{name}{attr_str}>{c}</{name}>' for c in content)
        return '\n'.join(elements)
    else:
        return f'<{name}{attr_str} />'

tag('br')                           # '<br />'
tag('p', 'hello')                   # '<p>hello</p>'
tag('p', 'hello', 'world')          # '<p>hello</p>\n<p>world</p>'
tag('p', 'hello', id=33)            # '<p id="33">hello</p>'
tag('p', 'hello', class_='sidebar') # '<p class="sidebar">hello</p>'

# Positional-only parameters (Python 3.8+, / separator)
def divmod_pos(a, b, /):
    return divmod(a, b)

divmod_pos(10, 3)         # (3, 1) — OK
divmod_pos(a=10, b=3)     # TypeError — a and b are positional-only
```

---

## 🔧 The `operator` Module

```python
from operator import mul, add, itemgetter, attrgetter, methodcaller
from functools import reduce

# mul — avoids lambda
reduce(mul, range(1, 6))     # 120 (= 5!)
# instead of: reduce(lambda a, b: a * b, range(1, 6))

# itemgetter — extract fields from sequences
metro_data = [
    ('Tokyo',    'JP', 36.933),
    ('Delhi',    'IN', 21.935),
    ('Mexico',   'MX', 20.142),
]
for city in sorted(metro_data, key=itemgetter(1)):   # sort by country code
    print(city)

# itemgetter with multiple indices
cc_name = itemgetter(1, 0)
[cc_name(city) for city in metro_data]
# [('JP', 'Tokyo'), ('IN', 'Delhi'), ('MX', 'Mexico')]

# attrgetter — extract object attributes
from collections import namedtuple
LatLon = namedtuple('LatLon', 'lat lon')
Metropolis = namedtuple('Metropolis', 'name cc pop coord')
metro_areas = [
    Metropolis('Tokyo', 'JP', 36.933, LatLon(35.689722, 139.691667)),
    Metropolis('Delhi', 'IN', 21.935, LatLon(28.613889, 77.208889)),
]
name_lat = attrgetter('name', 'coord.lat')   # access nested attributes
for city in sorted(metro_areas, key=attrgetter('coord.lat')):
    print(name_lat(city))

# methodcaller — call a method by name
from operator import methodcaller
upper = methodcaller('upper')
upper('hello')   # 'HELLO'

hyphenate = methodcaller('replace', ' ', '-')
hyphenate('New York')  # 'New-York'
```

---

## 🧊 `functools.partial` — Freezing Arguments

```python
from operator import mul
from functools import partial

# Create triple from mul by fixing first arg
triple = partial(mul, 3)
triple(5)       # 15
triple(7)       # 21

list(map(triple, range(6)))   # [0, 3, 6, 9, 12, 15]

# Useful for adapting functions with wrong signature
import unicodedata
nfc = partial(unicodedata.normalize, 'NFC')
nfc('café')     # normalized form — NFC applied to any string

# Partial with keyword args
def tag(name, *content, class_=None, **attrs): ...
picture = partial(tag, 'img', class_='pic-frame')
picture(src='wumpus.jpeg')   # <img class="pic-frame" src="wumpus.jpeg" />
```

---

## 🔑 Key Takeaways

- Functions are first-class objects — assign, pass, return, store in data structures
- `callable()` tests whether an object can be invoked
- Use `operator.mul`, `itemgetter`, `attrgetter` instead of `lambda` for cleaner code
- `functools.partial` creates specialized versions of functions by freezing arguments
- `*args` capture variable positional args; keyword-only params follow `*` or `*args`
- Classes with `__call__` are callable — useful for stateful callables with extra API
