# Chapter 6 — Dictionaries

> **Part I: Basics**

---

## 🎯 What This Chapter Covers

Creating and using dictionaries, looping through key-value pairs, nesting (dict in list, list in dict, dict in dict).

---

## 📚 Dictionaries

```python
# Dictionary: key-value pairs, any order (Python 3.7+ preserves insertion order)
alien_0 = {'color': 'green', 'points': 5}

# Access values by key
print(alien_0['color'])    # 'green'
print(alien_0['points'])   # 5

# Use get() — avoids KeyError with a default
point_value = alien_0.get('points', 'No point value assigned.')
print(point_value)   # 5
speed = alien_0.get('speed', 'No speed info.')
print(speed)         # 'No speed info.'
```

---

## ✏️ Modifying Dictionaries

```python
alien_0 = {'color': 'green', 'points': 5}

# Add new key-value pair
alien_0['x_position'] = 0
alien_0['y_position'] = 25

# Modify existing value
alien_0['color'] = 'yellow'

# Remove key-value pair
del alien_0['points']

# Start empty, build up
alien_0 = {}
alien_0['color'] = 'green'
alien_0['points'] = 5
```

---

## 🔁 Looping Through a Dictionary

```python
user_0 = {
    'username': 'efermi',
    'first': 'enrico',
    'last': 'fermi',
}

# Loop through key-value pairs
for key, value in user_0.items():
    print(f"\nKey: {key}")
    print(f"Value: {value}")

# Loop through keys only
for key in user_0.keys():
    print(key)
# Or: for key in user_0:  (same — default is keys)

# Loop through keys in sorted order
for key in sorted(user_0.keys()):
    print(f"{key.title()}, thank you for taking the poll.")

# Loop through values only
for value in user_0.values():
    print(value)

# Unique values only
favorite_languages = {
    'jen': 'python',
    'sarah': 'c',
    'edward': 'rust',
    'phil': 'python',
}
for language in set(favorite_languages.values()):   # set removes duplicates
    print(language.title())
```

---

## 🏗️ Nesting

```python
# 1. List of dictionaries
alien_0 = {'color': 'green', 'points': 5}
alien_1 = {'color': 'yellow', 'points': 10}
alien_2 = {'color': 'red', 'points': 15}
aliens = [alien_0, alien_1, alien_2]

for alien in aliens:
    print(alien)

# Build a list of dicts
aliens = []
for alien_number in range(30):
    new_alien = {'color': 'green', 'points': 5, 'speed': 'slow'}
    aliens.append(new_alien)

# 2. List in a dictionary
pizza = {
    'crust': 'thick',
    'toppings': ['mushrooms', 'extra cheese'],
}
print(f"You ordered a {pizza['crust']}-crust pizza "
      f"with the following toppings:")
for topping in pizza['toppings']:
    print(f"\t{topping}")

# 3. Dictionary in a dictionary
users = {
    'aeinstein': {
        'first': 'albert',
        'last': 'einstein',
        'location': 'princeton',
    },
    'mcurie': {
        'first': 'marie',
        'last': 'curie',
        'location': 'paris',
    },
}
for username, user_info in users.items():
    print(f"\nUsername: {username}")
    full_name = f"{user_info['first']} {user_info['last']}"
    location = user_info['location']
    print(f"\tFull name: {full_name.title()}")
    print(f"\tLocation: {location.title()}")
```

---

## 🔑 Key Takeaways

- Dictionaries store key-value pairs; access with `dict['key']`
- Use `dict.get('key', default)` to avoid `KeyError` on missing keys
- `.items()` → key-value pairs; `.keys()` → keys; `.values()` → values
- `del dict['key']` removes a key-value pair permanently
- Nesting: list of dicts (multiple similar objects), list in dict (multiple values per key), dict in dict (user profiles, configs)
- `set(values)` removes duplicates when looping through values
- Python 3.7+ preserves insertion order in dictionaries
