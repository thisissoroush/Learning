# Chapter 8 — Functions

> **Part I: Basics**

---

## 🎯 What This Chapter Covers

Defining functions, positional/keyword arguments, default values, return values, `*args`, `**kwargs`, and organizing code in modules.

---

## 🔧 Defining Functions

```python
# Basic function
def greet_user():
    """Display a simple greeting."""   # docstring
    print("Hello!")

greet_user()    # Hello!

# With parameter
def greet_user(username):
    """Display a simple greeting."""
    print(f"Hello, {username.title()}!")

greet_user('jesse')    # Hello, Jesse!
```

---

## 📨 Passing Arguments

```python
def describe_pet(animal_type, pet_name):
    print(f"\nI have a {animal_type}.")
    print(f"My {animal_type}'s name is {pet_name.title()}.")

# Positional — order matters
describe_pet('hamster', 'harry')
describe_pet('dog', 'willie')

# Keyword — order doesn't matter
describe_pet(animal_type='hamster', pet_name='harry')
describe_pet(pet_name='harry', animal_type='hamster')   # same result

# Default values — defaults at the END
def describe_pet(pet_name, animal_type='dog'):
    print(f"\nI have a {animal_type}.")
    print(f"My {animal_type}'s name is {pet_name.title()}.")

describe_pet(pet_name='willie')        # uses default 'dog'
describe_pet('willie')                 # same — positional
describe_pet('harry', 'hamster')       # overrides default
```

---

## 📤 Return Values

```python
# Returning a simple value
def get_formatted_name(first_name, last_name):
    """Return a full name, neatly formatted."""
    full_name = f"{first_name} {last_name}"
    return full_name.title()

musician = get_formatted_name('jimi', 'hendrix')
print(musician)   # Jimi Hendrix

# Optional argument
def get_formatted_name(first_name, last_name, middle_name=''):
    if middle_name:
        full_name = f"{first_name} {middle_name} {last_name}"
    else:
        full_name = f"{first_name} {last_name}"
    return full_name.title()

# Returning a dictionary
def build_person(first_name, last_name, age=None):
    person = {'first': first_name, 'last': last_name}
    if age:
        person['age'] = age
    return person

musician = build_person('jimi', 'hendrix', age=27)
print(musician)   # {'first': 'jimi', 'last': 'hendrix', 'age': 27}
```

---

## 📋 Passing Lists

```python
def greet_users(names):
    for name in names:
        print(f"Hello, {name.title()}!")

usernames = ['hannah', 'ty', 'margot']
greet_users(usernames)

# Modifying a list in a function (changes the original)
def print_models(unprinted_designs, completed_models):
    while unprinted_designs:
        current_design = unprinted_designs.pop()
        print(f"Printing model: {current_design}")
        completed_models.append(current_design)

# Prevent modification — pass a copy with [:]
print_models(unprinted_designs[:], completed_models)
```

---

## 🌟 Arbitrary Arguments

```python
# *args — collect any number of positional args into a tuple
def make_pizza(*toppings):
    print("\nMaking a pizza with the following toppings:")
    for topping in toppings:
        print(f"- {topping}")

make_pizza('pepperoni')
make_pizza('mushrooms', 'green peppers', 'extra cheese')

# Mix positional + arbitrary
def make_pizza(size, *toppings):
    print(f"\nMaking a {size}-inch pizza with:")
    for topping in toppings:
        print(f"- {topping}")

make_pizza(16, 'pepperoni')
make_pizza(12, 'mushrooms', 'green peppers', 'extra cheese')

# **kwargs — collect keyword args into a dictionary
def build_profile(first, last, **user_info):
    user_info['first_name'] = first
    user_info['last_name'] = last
    return user_info

user_profile = build_profile('albert', 'einstein',
                             location='princeton',
                             field='physics')
print(user_profile)
# {'location': 'princeton', 'field': 'physics', 'first_name': 'albert', 'last_name': 'einstein'}
```

---

## 📦 Modules

```python
# pizza.py — the module
def make_pizza(size, *toppings):
    print(f"\nMaking a {size}-inch pizza.")

# making_pizzas.py — using the module
import pizza
pizza.make_pizza(16, 'pepperoni')

# Import specific function
from pizza import make_pizza
make_pizza(16, 'pepperoni')

# Alias for function
from pizza import make_pizza as mp
mp(16, 'pepperoni')

# Alias for module
import pizza as p
p.make_pizza(16, 'pepperoni')

# Import everything (avoid — pollutes namespace)
from pizza import *
make_pizza(16, 'pepperoni')
```

---

## 🔑 Key Takeaways

- Positional args: order matters. Keyword args: name matters.
- Default values must come after parameters without defaults
- `return` sends a value back; can return any type including dicts and lists
- Pass `list[:]` to a function to prevent it from modifying the original
- `*args` → tuple of positional args; `**kwargs` → dict of keyword args
- Modules organize related functions into reusable files
- Use `import module` (explicit) over `from module import *` (pollutes namespace)
