# Chapter 3 — Introducing Lists

> **Part I: Basics**

---

## 🎯 What This Chapter Covers

Creating lists, accessing elements, modifying lists (add, remove, sort), and avoiding index errors.

---

## 📋 What Is a List?

```python
# A list is an ordered, mutable collection of items
bicycles = ['trek', 'cannondale', 'redline', 'specialized']
print(bicycles)          # ['trek', 'cannondale', 'redline', 'specialized']

# Access by index (0-based)
print(bicycles[0])       # 'trek'
print(bicycles[1])       # 'cannondale'
print(bicycles[-1])      # 'specialized'  (last item)
print(bicycles[-2])      # 'redline'      (second to last)

# Use in expressions
print(f"My first bicycle was a {bicycles[0].title()}.")
```

---

## ✏️ Modifying Elements

```python
motorcycles = ['honda', 'yamaha', 'suzuki']

# Modify
motorcycles[0] = 'ducati'
print(motorcycles)   # ['ducati', 'yamaha', 'suzuki']

# Append — add to end
motorcycles.append('honda')
print(motorcycles)   # ['ducati', 'yamaha', 'suzuki', 'honda']

# Insert — add at index
motorcycles.insert(0, 'kawasaki')
print(motorcycles)   # ['kawasaki', 'ducati', 'yamaha', 'suzuki', 'honda']
```

---

## ❌ Removing Elements

```python
motorcycles = ['honda', 'yamaha', 'suzuki', 'ducati']

# del — remove by index (no return)
del motorcycles[0]
print(motorcycles)    # ['yamaha', 'suzuki', 'ducati']

# pop() — remove last (returns removed item)
popped = motorcycles.pop()
print(popped)         # 'ducati'
print(motorcycles)    # ['yamaha', 'suzuki']

# pop(index) — remove at index
first = motorcycles.pop(0)
print(first)          # 'yamaha'

# remove() — remove by value (first occurrence)
motorcycles = ['honda', 'yamaha', 'suzuki', 'ducati']
motorcycles.remove('yamaha')
print(motorcycles)    # ['honda', 'suzuki', 'ducati']
```

**When to use which:**
- `del` — know the index, don't need the value
- `pop()` — want to use the removed value  
- `remove()` — know the value, not the index

---

## 📊 Organizing a List

```python
cars = ['bmw', 'audi', 'toyota', 'subaru']

# sort() — permanent, alphabetical
cars.sort()
print(cars)           # ['audi', 'bmw', 'subaru', 'toyota']

# sort(reverse=True) — reverse alphabetical
cars.sort(reverse=True)
print(cars)           # ['toyota', 'subaru', 'bmw', 'audi']

# sorted() — temporary, non-destructive
print(sorted(cars))           # sorted copy
print(cars)                   # original unchanged

# reverse() — reverse current order (permanent)
cars.reverse()

# len() — list length
print(len(cars))      # 4
```

---

## ⚠️ Avoiding Index Errors

```python
motorcycles = ['honda', 'yamaha', 'suzuki']

# IndexError!
print(motorcycles[3])   # IndexError: list index out of range

# Use -1 for last item (always safe if list is non-empty)
print(motorcycles[-1])  # 'suzuki'

# Check length before accessing
if len(motorcycles) > 3:
    print(motorcycles[3])
```

---

## 🔑 Key Takeaways

- Lists are 0-indexed; `-1` is the last element
- `append()` adds to end; `insert(i, val)` adds at index `i`
- `del list[i]` removes without returning; `pop(i)` removes and returns
- `remove(val)` removes the first occurrence of a value
- `sort()` modifies in place; `sorted()` returns a new sorted list
- `len(list)` counts elements — critical for avoiding index errors
