# Chapter 2 — An Array of Sequences

> *"Python inherited from ABC the uniform handling of sequences."*

---

## 🎯 Core Concept

Python's sequence types share a common interface. Understanding the taxonomy — container vs. flat, mutable vs. immutable — and mastering list comprehensions, unpacking, slicing, and pattern matching makes you dramatically more productive.

---

## 🗂️ Sequence Taxonomy

```
Sequences
│
├── Container sequences (hold references to objects of any type)
│   ├── list          — mutable
│   ├── tuple         — immutable
│   └── collections.deque — mutable
│
└── Flat sequences (physically store values, not references — compact, faster)
    ├── str            — immutable
    ├── bytes          — immutable
    ├── bytearray      — mutable
    └── array.array    — mutable
```

---

## 📝 List Comprehensions

```python
# Classic: verbose
squares = []
for x in range(10):
    squares.append(x**2)

# Listcomp: concise, faster, more readable
squares = [x**2 for x in range(10)]

# Filter + transform in one expression
even_squares = [x**2 for x in range(10) if x % 2 == 0]

# Cartesian product
colors = ['black', 'white']
sizes  = ['S', 'M', 'L']
tshirts = [(c, s) for c in colors for s in sizes]
# [('black', 'S'), ('black', 'M'), ('black', 'L'),
#  ('white', 'S'), ('white', 'M'), ('white', 'L')]

# Generator expressions (lazy — saves memory)
gen = (x**2 for x in range(1_000_000))  # no list built in memory
sum(gen)   # compute on the fly
```

---

## 📦 Tuples as Records

```python
# Tuples are more than immutable lists — each position has MEANING
tokyo  = ('Tokyo',  'JP', 36.933, (35.689722, 139.691667))
delhi  = ('Delhi',  'IN', 21.935, (28.613889,  77.208889))

# Unpacking preserves meaning
city, country, pop, coords = delhi
lat, lon = coords

# Swap without temp variable (unpacking)
a, b = b, a

# Star to grab excess
first, *rest = range(5)      # first=0, rest=[1,2,3,4]
*head, last  = range(5)      # head=[0,1,2,3], last=4
a, *b, c     = range(5)      # a=0, b=[1,2,3], c=4
```

---

## 🎯 Pattern Matching with Sequences (Python 3.10+)

```python
def handle_command(command):
    match command.split():
        case ['quit']:
            print('Quitting')
        case ['go', direction] if direction in ('north','south','east','west'):
            print(f'Going {direction}')
        case ['get', obj]:
            print(f'Getting {obj}')
        case ['drop', *objects]:
            print(f'Dropping: {objects}')
        case _:
            print(f'Unknown command: {command!r}')

handle_command('go north')   # Going north
handle_command('drop sword shield') # Dropping: ['sword', 'shield']
```

---

## ✂️ Slicing

```python
s = 'bicycle'
s[::3]       # 'bye'
s[::-1]      # 'elcycib'  (reverse)
s[1:5]       # 'icyc'

# Named slices — document intent
invoice = """
0.....6.................................40........52...55........
1909  Pimoroni PiBrella                     $17.50    3    $52.50
1489  6mm Tactile Switch x20                $4.95    2     $9.90
"""
SKU    = slice(0, 6)
DESC   = slice(6, 40)
UNIT_PRICE = slice(40, 52)
QTY   = slice(52, 55)

for item in invoice.split('\n')[2:]:
    print(item[DESC].strip(), item[UNIT_PRICE].strip())

# Assigning to slices
l = list(range(10))
l[2:5] = [20, 30]       # replace slice
del l[5:7]              # delete slice
```

---

## ➕ `+` and `*` with Sequences

```python
# + — concatenate
[1, 2] + [3, 4]         # [1, 2, 3, 4]
'hello' + ' ' + 'world' # 'hello world'

# * — repeat
[0] * 3                 # [0, 0, 0]
'ha' * 3                # 'hahaha'

# PITFALL: list of lists with *
board = [['_'] * 3] * 3   # WRONG — 3 references to SAME inner list!
board[1][1] = 'X'
# [['_', 'X', '_'], ['_', 'X', '_'], ['_', 'X', '_']]  ← all changed!

# CORRECT: list comprehension creates independent lists
board = [['_'] * 3 for _ in range(3)]
board[1][1] = 'X'
# [['_', '_', '_'], ['_', 'X', '_'], ['_', '_', '_']]  ✓
```

---

## 🔄 `list.sort` vs `sorted`

```python
fruits = ['grape', 'raspberry', 'apple', 'banana']

# sorted() → returns NEW sorted list, original unchanged
sorted(fruits)                   # ['apple', 'banana', 'grape', 'raspberry']
sorted(fruits, reverse=True)     # descending
sorted(fruits, key=len)          # by length: ['grape', 'apple', 'banana', 'raspberry']

# list.sort() → sorts IN PLACE, returns None (convention: mutating methods return None)
fruits.sort()
fruits.sort(key=len, reverse=True)
```

---

## 📊 When a List Is Not the Answer

```python
# array.array — compact storage for numeric data (C-level types)
from array import array
floats = array('d', (random.random() for i in range(10**7)))
# 80MB less memory than a list of floats

# deque — O(1) appends and pops from both ends
from collections import deque
dq = deque(range(10), maxlen=10)
dq.appendleft(-1)   # rotates right, drops rightmost: deque([-1, 0, 1, ..., 8])
dq.rotate(3)        # rotate elements

# memoryview — zero-copy slicing of binary data
mv = memoryview(bytes(range(10)))
mv[2:5].tolist()    # [2, 3, 4] — no copy
```

---

## 🔑 Key Takeaways

- List comprehensions are more readable AND faster than `map`/`filter` for most cases
- Generator expressions save memory when you don't need a list
- Tuples convey meaning through position — treat each slot as a named field
- Pattern matching (`match/case`) elegantly deconstructs sequences
- Never use `[x] * n` for mutable inner objects — use a listcomp instead
- `array.array` and `memoryview` for performance-critical numeric/binary work
