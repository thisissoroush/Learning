# Chapter 17 — Iterators, Generators, and Classic Coroutines

> *"When I see patterns in my programs, I consider it a sign of trouble."*

---

## 🎯 Core Concept

Iteration is fundamental to Python. Generators provide lazy evaluation — computing values on demand instead of building full collections. `yield from` composes generators elegantly. Classic coroutines (pre-async) use `yield` as a two-way channel.

---

## 🔄 The Iterator Protocol

```python
# Iterable — has __iter__ returning an iterator
# Iterator — has __iter__ (returns self) + __next__

class Sentence:
    def __init__(self, text):
        self.text = text
        self.words = text.split()

    def __iter__(self):
        return SentenceIterator(self.words)

class SentenceIterator:
    def __init__(self, words):
        self.words = words
        self.index = 0

    def __next__(self):
        try:
            word = self.words[self.index]
        except IndexError:
            raise StopIteration()
        self.index += 1
        return word

    def __iter__(self):    # iterators must be iterable
        return self

# Never make the iterable its own iterator — separate concerns
# Iterable can be iterated many times; iterator is exhausted after one pass
```

---

## ✨ Generator Functions — The Pythonic Way

```python
# A generator function contains 'yield' — returns a generator object
class Sentence:
    def __init__(self, text):
        self.text = text

    def __iter__(self):
        for word in self.text.split():
            yield word    # suspends here, resumes on next()

# Even simpler — generator expression
class Sentence:
    def __init__(self, text):
        self.text = text

    def __iter__(self):
        return (word for word in self.text.split())
```

```
How a generator works:
  gen = Sentence('Hello World')
  it = iter(gen)        # calls __iter__ → returns generator object
  next(it)              # runs until first 'yield' → returns 'Hello'
  next(it)              # runs from after 'yield' → 'World'
  next(it)              # StopIteration
```

---

## 🔢 Arithmetic Progression Generator

```python
class ArithmeticProgression:
    def __init__(self, begin, step, end=None):
        self.begin = begin
        self.step = step
        self.end = end

    def __iter__(self):
        result_type = type(self.begin + self.step)
        result = result_type(self.begin)
        forever = self.end is None
        index = 0
        while forever or result < self.end:
            yield result
            index += 1
            result = self.begin + self.step * index

ap = ArithmeticProgression(0, 1, 3)
list(ap)    # [0, 1, 2]

ap_float = ArithmeticProgression(0, .1, .3)
list(ap_float)   # [0.0, 0.1, 0.2]

# Same with itertools
import itertools
gen = itertools.takewhile(lambda n: n < 3, itertools.count(0, 1))
list(gen)    # [0, 1, 2]
```

---

## 🔗 `yield from` — Subgenerators

```python
# yield from: delegates to a subgenerator, transparently passing values

def chain(*iterables):
    for it in iterables:
        yield from it    # yields each item from it, then moves to next

list(chain('AB', range(3)))   # ['A', 'B', 0, 1, 2]
# Equivalent to:
# for it in iterables:
#     for x in it:
#         yield x

# Traversing a tree
def tree(cls, level=0):
    yield cls.__name__, level
    for sub_cls in cls.__subclasses__():
        yield from tree(sub_cls, level + 1)

for cls, level in tree(BaseException):
    indent = ' ' * 4 * level
    print(f'{indent}{cls}')
```

---

## 📚 Generator Functions in Standard Library

```python
import itertools

# Filtering
itertools.compress('ABCDEF', [1,0,1,0,1,1])    # A C E F
itertools.dropwhile(lambda c: c < 3, [1,2,3,4,5,3])  # 3 4 5 3
itertools.filterfalse(lambda n: n % 2, range(10))    # 0 2 4 6 8
itertools.islice(range(10), 5, 10)              # 5 6 7 8 9

# Mapping
itertools.accumulate([1,2,3,4,5])               # 1 3 6 10 15 (running sum)
itertools.accumulate([1,2,3,4,5], operator.mul) # 1 2 6 24 120 (running product)
itertools.starmap(operator.mul, [(2,4),(3,5)])   # 8 15

# Merging
itertools.chain('ABC', range(3))                # A B C 0 1 2
itertools.chain.from_iterable(['ABC', 'DEF'])   # A B C D E F
itertools.zip_longest('AB', range(3), fillvalue=-1)  # (A,0) (B,1) (-1,2)
itertools.product('AB', range(2))               # (A,0) (A,1) (B,0) (B,1)

# Expanding
itertools.combinations('ABC', 2)     # AB AC BC
itertools.permutations('ABC', 2)     # AB AC BA BC CA CB
itertools.combinations_with_replacement('ABC', 2)  # AA AB AC BB BC CC
```

---

## 🔑 Key Takeaways

- Iterator protocol: `__iter__` + `__next__` + `StopIteration`
- Don't make an iterable its own iterator — separate iterable (reusable) from iterator (one-pass)
- Generator functions (`yield`) produce lazy, memory-efficient sequences
- `yield from subgen` delegates to a subgenerator, passing through all values
- `itertools` has powerful composable generators — learn them well
- Generators compute on demand: O(1) memory regardless of sequence length
