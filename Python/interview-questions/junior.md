# 🟢 Python — Junior Interview Questions

---

## 1. What are Python's built-in data types?

**A:**
- **Numeric:** `int`, `float`, `complex`
- **Sequence:** `str`, `list`, `tuple`, `range`
- **Mapping:** `dict`
- **Set:** `set`, `frozenset`
- **Boolean:** `bool`
- **None:** `NoneType`

```python
x = 42           # int
y = 3.14         # float
name = "Alice"   # str
items = [1, 2]   # list (mutable)
coords = (1, 2)  # tuple (immutable)
d = {"a": 1}     # dict
s = {1, 2, 3}    # set
```

---

## 2. What is the difference between a list and a tuple?

**A:**
- `list` — mutable, ordered, allows duplicates: `[1, 2, 3]`
- `tuple` — immutable, ordered, allows duplicates: `(1, 2, 3)`

Use tuples for data that shouldn't change (coordinates, RGB values, dict keys). Lists for collections you'll modify.

```python
lst = [1, 2, 3]
lst[0] = 99     # OK

tup = (1, 2, 3)
tup[0] = 99     # TypeError: 'tuple' object does not support item assignment
```

---

## 3. How does Python handle indentation?

**A:** Indentation is **syntax** in Python — it defines code blocks (no braces). Consistent indentation (4 spaces, per PEP 8) is required:

```python
if True:
    print("indented block")
    if True:
        print("nested block")
print("back to top level")
```

`IndentationError` is raised for mixed or inconsistent indentation.

---

## 4. What is the difference between `==` and `is`?

**A:**
- `==` — value equality
- `is` — identity (same object in memory)

```python
a = [1, 2, 3]
b = [1, 2, 3]
print(a == b)  # True — same values
print(a is b)  # False — different objects

c = a
print(a is c)  # True — same object
```

Common pitfall: `is None` is correct; `== None` works but is discouraged by PEP 8.

---

## 5. What are Python's comparison operators and boolean operators?

**A:**
```python
# Comparison
x == y, x != y, x < y, x > y, x <= y, x >= y

# Boolean
True and False  # False
True or False   # True
not True        # False

# Python also supports chaining
1 < x < 10      # equivalent to 1 < x and x < 10
```

---

## 6. How do you handle exceptions in Python?

**A:**
```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Error: {e}")
except (TypeError, ValueError):
    print("Type or value problem")
else:
    print("No exception — runs only if try succeeded")
finally:
    print("Always runs — cleanup")
```

Raise your own: `raise ValueError("invalid input")`

---

## 7. What are list comprehensions?

**A:** A concise way to create lists:

```python
# Traditional
squares = []
for x in range(10):
    squares.append(x ** 2)

# List comprehension
squares = [x ** 2 for x in range(10)]

# With condition
evens = [x for x in range(20) if x % 2 == 0]

# Dict comprehension
d = {k: v for k, v in zip("abc", [1, 2, 3])}  # {'a': 1, 'b': 2, 'c': 3}
```

---

## 8. What is a function in Python? What are `*args` and `**kwargs`?

**A:**
```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

# *args — variable positional arguments (tuple)
def add(*args):
    return sum(args)
add(1, 2, 3)  # 6

# **kwargs — variable keyword arguments (dict)
def info(**kwargs):
    for k, v in kwargs.items():
        print(f"{k}: {v}")
info(name="Alice", age=30)
```

---

## 9. What is the difference between `append`, `extend`, and `insert` on a list?

**A:**
```python
lst = [1, 2, 3]

lst.append(4)       # [1, 2, 3, 4] — adds one element
lst.extend([5, 6])  # [1, 2, 3, 4, 5, 6] — adds all elements of iterable
lst.insert(0, 0)    # [0, 1, 2, 3, 4, 5, 6] — insert at index
```

---

## 10. How does Python's `dict` work? How do you check if a key exists?

**A:**
```python
d = {"name": "Alice", "age": 30}

# Access
d["name"]           # "Alice" — KeyError if missing
d.get("name")       # "Alice" — None if missing
d.get("x", "N/A")   # "N/A" — default value

# Check existence
"name" in d         # True
"x" not in d        # True

# Iterate
for k, v in d.items(): pass
for k in d.keys(): pass
for v in d.values(): pass
```

---

## 11. What is a class in Python? How do you define one?

**A:**
```python
class Animal:
    def __init__(self, name: str):
        self.name = name

    def speak(self) -> str:
        return f"{self.name} makes a sound"

class Dog(Animal):
    def speak(self) -> str:
        return f"{self.name} says Woof!"

d = Dog("Rex")
print(d.speak())  # Rex says Woof!
```

`__init__` is the constructor. `self` is the instance reference (like `this` in other languages).

---

## 12. What are Python's string formatting options?

**A:**
```python
name = "Alice"
age = 30

# f-string (preferred, Python 3.6+)
f"Hello, {name}! You are {age} years old."

# .format()
"Hello, {}! You are {} years old.".format(name, age)

# %-style (old)
"Hello, %s! You are %d years old." % (name, age)
```

---

## 13. What is `None` in Python?

**A:** `None` is Python's null value — the singleton representing "nothing":

```python
x = None
print(x is None)   # True (use `is`, not ==)
print(type(None))  # <class 'NoneType'>
```

Functions with no `return` statement implicitly return `None`.

---

## 14. What is the difference between `range()` and `list(range())`?

**A:**
- `range()` returns a lazy range object — doesn't store all values in memory
- `list(range())` materializes all values into a list

```python
r = range(10)      # range(0, 10) — lazy, O(1) memory
l = list(range(10)) # [0, 1, ..., 9] — O(n) memory

for i in range(1000000):  # fine — no large allocation
    pass
```

---

## 15. What are Python's access modifiers?

**A:** Python doesn't enforce access control at the language level — it uses conventions:

- `name` — public
- `_name` — "protected" by convention, internal use (not enforced)
- `__name` — name-mangled to `_ClassName__name`, discourages accidental access

```python
class Foo:
    def __init__(self):
        self.public = 1
        self._internal = 2
        self.__private = 3

f = Foo()
f.public     # OK
f._internal  # Works, but "don't touch"
f.__private  # AttributeError
f._Foo__private  # Works — name mangling
```
