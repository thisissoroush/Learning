# Chapter 4 — Working with Lists

> **Part I: Basics**

---

## 🎯 What This Chapter Covers

`for` loops, `range()`, numerical lists, list comprehensions, slices, tuples, and PEP 8 style.

---

## 🔁 Looping Through a List

```python
magicians = ['alice', 'david', 'carolina']

for magician in magicians:
    print(magician)
# alice
# david
# carolina

for magician in magicians:
    print(f"{magician.title()}, that was a great trick!")
    print(f"I can't wait to see your next trick, {magician.title()}.\n")

# After loop — runs once, not per iteration
print("Thank you, everyone!")
```

**Indentation is everything:**
```python
for magician in magicians:
    print(magician)         # inside loop — runs each iteration
print("Done")               # outside loop — runs once after
```

---

## 🔢 Numerical Lists with `range()`

```python
# range(stop) — 0 to stop-1
for value in range(5):
    print(value)   # 0 1 2 3 4

# range(start, stop)
for value in range(1, 6):
    print(value)   # 1 2 3 4 5

# range(start, stop, step)
for value in range(2, 11, 2):
    print(value)   # 2 4 6 8 10

# Convert to list
numbers = list(range(1, 6))   # [1, 2, 3, 4, 5]

# Statistics
digits = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
min(digits)    # 0
max(digits)    # 9
sum(digits)    # 45
```

---

## ⚡ List Comprehensions

```python
# Traditional loop
squares = []
for value in range(1, 11):
    squares.append(value ** 2)

# List comprehension — one line
squares = [value**2 for value in range(1, 11)]
print(squares)   # [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]

# With condition
evens = [x for x in range(20) if x % 2 == 0]
# [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

# Transforming strings
names = ['alice', 'bob', 'charlie']
upper_names = [name.upper() for name in names]
# ['ALICE', 'BOB', 'CHARLIE']
```

---

## 🔪 Slicing a List

```python
players = ['charles', 'martina', 'michael', 'florence', 'eli']

# list[start:stop] — stop is exclusive
print(players[0:3])    # ['charles', 'martina', 'michael']
print(players[1:4])    # ['martina', 'michael', 'florence']

# Omit start — from beginning
print(players[:3])     # ['charles', 'martina', 'michael']

# Omit stop — to end
print(players[2:])     # ['michael', 'florence', 'eli']

# Last n items
print(players[-3:])    # ['michael', 'florence', 'eli']

# Loop through a slice
for player in players[:3]:
    print(player.title())

# Copy a list — IMPORTANT: use [:] not =
my_foods = ['pizza', 'falafel', 'carrot cake']
friend_foods = my_foods[:]      # independent copy
friend_foods = my_foods         # same list! — changes affect both
```

---

## 🔒 Tuples — Immutable Lists

```python
# Tuples use parentheses — cannot be changed
dimensions = (200, 50)
print(dimensions[0])   # 200
print(dimensions[1])   # 50

# dimensions[0] = 250   # TypeError: tuple does not support assignment

# Loop through tuple
for dimension in dimensions:
    print(dimension)

# Single-item tuple needs trailing comma
point = (3,)

# Can reassign the variable (not the tuple)
dimensions = (400, 100)   # new tuple, not modifying old one

# Use tuples for values that should NEVER change:
# window size, database credentials, days of the week
```

---

## 🎨 PEP 8 Style Guidelines

```python
# Indentation: 4 spaces (not tabs)
for value in range(5):
    print(value)

# Line length: 79 characters max for code

# Blank lines:
# - 2 blank lines between functions/classes
# - 1 blank line between logical sections

# Comments: space after # symbol
# Good:
# This is a comment
# Not: #This is a comment
```

---

## 🔑 Key Takeaways

- `for item in list:` iterates over every element; indent the loop body
- `range(start, stop, step)` generates number sequences without storing them
- List comprehensions: `[expr for item in iterable if condition]` — concise and Pythonic
- Slicing: `list[1:4]` returns elements at index 1, 2, 3 (stop is exclusive)
- `list[:]` makes a true copy; `list2 = list1` makes both point to the same list
- Tuples are immutable — use for data that must not change
- PEP 8: 4-space indentation, 79-char line limit, 2 blank lines between functions
