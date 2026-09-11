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

---

## 16. What is the difference between `deepcopy` and `copy`?

**A:**
```python
import copy

original = [[1, 2], [3, 4]]

shallow = copy.copy(original)       # new outer list, shared inner lists
deep    = copy.deepcopy(original)   # fully independent copy

shallow[0][0] = 99
print(original[0][0]) # 99 — inner list shared!

deep[0][0] = 99
# original unchanged — fully independent
```

Use `deepcopy` when your data structure contains nested mutable objects.

---

## 17. What are `*args` unpacking and `**kwargs` unpacking at call site?

**A:**
```python
def greet(name, greeting, punctuation):
    return f"{greeting}, {name}{punctuation}"

args = ("Alice", "Hello", "!")
greet(*args)  # unpacks tuple as positional arguments

kwargs = {"name": "Alice", "greeting": "Hi", "punctuation": "."}
greet(**kwargs)  # unpacks dict as keyword arguments

# Combine both
greet(*("Alice",), **{"greeting": "Hey", "punctuation": "?"})
```

---

## 18. How does `enumerate` work and when do you use it?

**A:**
```python
fruits = ["apple", "banana", "cherry"]

# Instead of range(len(...))
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")

# With start index
for i, fruit in enumerate(fruits, start=1):
    print(f"{i}: {fruit}")  # 1: apple, 2: banana, 3: cherry
```

---

## 19. What is `zip` and how do you use it?

**A:**
```python
names = ["Alice", "Bob", "Charlie"]
scores = [95, 87, 72]

for name, score in zip(names, scores):
    print(f"{name}: {score}")

# zip stops at the shortest iterable
# Use itertools.zip_longest for full coverage

# Unzip with *
pairs = [(1, "a"), (2, "b"), (3, "c")]
numbers, letters = zip(*pairs)
# numbers = (1, 2, 3), letters = ('a', 'b', 'c')
```

---

## 20. What is `sorted` vs `.sort()`?

**A:**
- `.sort()` — in-place, modifies the list, returns `None`
- `sorted()` — returns a new sorted iterable, works on any iterable

```python
nums = [3, 1, 4, 1, 5]
nums.sort()                   # in-place
nums.sort(reverse=True)       # descending

sorted_nums = sorted(nums)            # new list
sorted_strs = sorted("hello")         # works on strings too: ['e', 'h', 'l', 'l', 'o']

# Custom key
people = [{"name": "Bob", "age": 30}, {"name": "Alice", "age": 25}]
sorted(people, key=lambda p: p["age"])  # sort by age
```

---

## 21. What are `set` operations in Python?

**A:**
```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

a | b   # union:        {1, 2, 3, 4, 5, 6}
a & b   # intersection: {3, 4}
a - b   # difference:   {1, 2}
a ^ b   # symmetric diff: {1, 2, 5, 6}

# Membership test is O(1) — much faster than list
42 in {1, 42, 99}   # True
```

---

## 22. What is `defaultdict` and `Counter`?

**A:**
```python
from collections import defaultdict, Counter

# defaultdict — no KeyError, auto-creates default value
word_lists = defaultdict(list)
word_lists["fruits"].append("apple")   # no need to check if key exists

# Counter — counts hashable objects
text = "hello world"
c = Counter(text.split())
# Counter({'hello': 1, 'world': 1})

c = Counter("abracadabra")
c.most_common(2)  # [('a', 5), ('b', 2)]
c["a"]            # 5
c["z"]            # 0 (no KeyError)
```

---

## 23. What is `global` and `nonlocal`?

**A:**
```python
x = 10

def modify_global():
    global x
    x = 99  # modifies the module-level x

def outer():
    count = 0
    def inner():
        nonlocal count  # refers to outer's count
        count += 1
    inner()
    return count  # 1
```

Avoid `global` — it makes code hard to reason about. `nonlocal` is occasionally useful for closures.

---

## 24. What is the `in` operator and what does it check?

**A:**
```python
# List — O(n) linear search
3 in [1, 2, 3, 4]      # True

# Set — O(1) hash lookup
3 in {1, 2, 3, 4}      # True (prefer for membership tests)

# Dict — checks keys
"name" in {"name": "Alice"}  # True

# String — substring check
"ell" in "hello"        # True

# Custom class — implement __contains__
class MyRange:
    def __contains__(self, item): return 0 <= item < 10
5 in MyRange()   # True
```

---

## 25. What is `isinstance` vs `type()`?

**A:**
```python
class Animal: pass
class Dog(Animal): pass

d = Dog()

type(d) == Dog      # True — exact type only
isinstance(d, Dog)  # True
isinstance(d, Animal)  # True — also matches parent classes

# isinstance is preferred — respects inheritance
# type() is useful when you need EXACT type check
```

---

## 26. What is string slicing?

**A:**
```python
s = "Hello, World!"

s[0]       # 'H'
s[-1]      # '!'
s[0:5]     # 'Hello'
s[7:]      # 'World!'
s[:5]      # 'Hello'
s[::2]     # every 2nd char: 'Hlo ol!'
s[::-1]    # reversed: '!dlroW ,olleH'

# Strings are immutable — slicing creates a new string
```

---

## 27. What are f-string expressions and formatting options?

**A:**
```python
import math

x = 3.14159
name = "Alice"

f"{x:.2f}"          # '3.14' — 2 decimal places
f"{x:>10.2f}"       # '      3.14' — right-aligned, width 10
f"{1000000:,}"      # '1,000,000' — thousands separator
f"{255:#x}"         # '0xff' — hex with prefix
f"{name!r}"         # "'Alice'" — repr()
f"{name!s}"         # 'Alice' — str()
f"{2 + 2}"          # '4' — expressions
f"{math.pi:.4f}"    # '3.1416'
```

---

## 28. What is `pass`, `continue`, and `break`?

**A:**
```python
# pass — no-op placeholder (empty block, stub)
class EmptyClass:
    pass

def not_implemented():
    pass

# continue — skip to next iteration
for i in range(10):
    if i % 2 == 0:
        continue    # skip even numbers
    print(i)        # prints 1, 3, 5, 7, 9

# break — exit loop entirely
for i in range(10):
    if i == 5:
        break       # stops at 5
    print(i)
```

---

## 29. How do you open and read files in Python?

**A:**
```python
# Read entire file
with open("file.txt", "r", encoding="utf-8") as f:
    content = f.read()

# Read line by line (memory-efficient for large files)
with open("file.txt") as f:
    for line in f:
        print(line.strip())

# Read all lines into a list
lines = f.readlines()

# Write
with open("out.txt", "w") as f:
    f.write("Hello
")

# Append
with open("out.txt", "a") as f:
    f.write("More
")
```

Always use `with` — ensures the file is closed even on exception.

---

## 30. What is `os.path` and `pathlib`?

**A:**
```python
import os
from pathlib import Path

# os.path (older)
os.path.join("dir", "file.txt")     # "dir/file.txt"
os.path.exists("file.txt")
os.path.basename("/path/to/file.txt")  # "file.txt"

# pathlib (modern, preferred)
p = Path("dir") / "file.txt"       # Path object, / operator
p.exists()
p.name          # "file.txt"
p.stem          # "file"
p.suffix        # ".txt"
p.read_text()   # read file contents
p.write_text("hello")

for f in Path(".").glob("*.py"):    # find all .py files
    print(f)
```
