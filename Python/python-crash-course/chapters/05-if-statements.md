# Chapter 5 — if Statements

> **Part I: Basics**

---

## 🎯 What This Chapter Covers

Conditional tests, `if`/`elif`/`else` chains, `and`/`or`, `in`/`not in`, and using `if` with lists.

---

## ✅ Conditional Tests

```python
# Equality (case-sensitive)
car = 'bmw'
car == 'bmw'    # True
car == 'BMW'    # False
car.lower() == 'bmw'   # True — case-insensitive check

# Inequality
car != 'audi'   # True

# Numerical comparisons
age = 19
age < 21    # True
age <= 21   # True
age > 21    # False
age >= 21   # False
age == 19   # True

# Checking multiple conditions
age_0 = 22
age_1 = 18
age_0 >= 21 and age_1 >= 21   # False (both must be True)
age_0 >= 21 or age_1 >= 21    # True  (either can be True)

# Checking membership
requested_toppings = ['mushrooms', 'onions', 'pineapple']
'mushrooms' in requested_toppings    # True
'pepperoni' in requested_toppings    # False
'pepperoni' not in requested_toppings  # True
```

---

## 🔀 if / elif / else

```python
age = 12

# Simple if
if age >= 18:
    print("You can vote.")

# if-else
if age >= 18:
    print("You can vote.")
else:
    print("You cannot vote yet.")

# if-elif-else chain
if age < 4:
    print("Your admission is free.")
elif age < 18:
    print("Your admission is $25.")
elif age < 65:
    print("Your admission is $40.")
else:
    print("Your admission is $20.")

# Multiple independent if statements (all are checked)
requested_toppings = ['mushrooms', 'extra cheese']
if 'mushrooms' in requested_toppings:
    print("Adding mushrooms.")
if 'pepperoni' in requested_toppings:
    print("Adding pepperoni.")
if 'extra cheese' in requested_toppings:
    print("Adding extra cheese.")

# Use elif when only ONE branch should run;
# use separate if when MULTIPLE branches can run
```

---

## 📋 if Statements with Lists

```python
requested_toppings = ['mushrooms', 'green peppers', 'extra cheese']
available_toppings = ['mushrooms', 'olives', 'green peppers', 'pepperoni', 'pineapple', 'extra cheese']

for topping in requested_toppings:
    if topping in available_toppings:
        print(f"Adding {topping}.")
    else:
        print(f"Sorry, we don't have {topping}.")

# Check if list is empty before looping
requested_toppings = []
if requested_toppings:
    for topping in requested_toppings:
        print(f"Adding {topping}.")
else:
    print("Are you sure you want a plain pizza?")

# Empty list is falsy — if list: is True only when non-empty
```

---

## 🔑 Key Takeaways

- `==` tests equality (case-sensitive); `.lower()` for case-insensitive comparison
- `and` requires both conditions True; `or` requires at least one
- `in` tests membership; `not in` tests absence
- `elif` chains: only the first matching condition runs
- Separate `if` statements: all are checked independently
- Empty list, empty string, 0, and `None` are all **falsy** in boolean context
- `if my_list:` is True when the list is non-empty — Pythonic way to check
