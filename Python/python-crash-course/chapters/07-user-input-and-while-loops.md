# Chapter 7 — User Input and while Loops

> **Part I: Basics**

---

## 🎯 What This Chapter Covers

`input()`, converting input types, `while` loops, flags, `break`, `continue`, and using `while` with lists and dictionaries.

---

## ⌨️ The `input()` Function

```python
# input() always returns a string
message = input("Tell me something, and I will repeat it back to you: ")
print(message)

# For numbers — convert with int()
age = input("How old are you? ")
age = int(age)
if age >= 18:
    print("You can vote!")

# Modulo for even/odd
number = int(input("Enter a number: "))
if number % 2 == 0:
    print(f"\nThe number {number} is even.")
else:
    print(f"\nThe number {number} is odd.")

# Multi-line prompt
prompt = "If you tell us who you are, we can personalize the messages you see."
prompt += "\nWhat is your first name? "
name = input(prompt)
print(f"\nHello, {name}!")
```

---

## 🔄 while Loops

```python
# Basic while loop
current_number = 1
while current_number <= 5:
    print(current_number)
    current_number += 1

# User-controlled loop
prompt = "\nTell me something, and I will repeat it back to you:"
prompt += "\nEnter 'quit' to end the program. "

message = ""
while message != 'quit':
    message = input(prompt)
    if message != 'quit':
        print(message)

# Using a flag
active = True
while active:
    message = input(prompt)
    if message == 'quit':
        active = False
    else:
        print(message)

# break — exit immediately
while True:
    city = input("\nPlease enter the name of a city you have visited:")
    if city == 'quit':
        break
    else:
        print(f"I'd love to go to {city.title()}!")

# continue — skip rest of loop body, go back to condition
current_number = 0
while current_number < 10:
    current_number += 1
    if current_number % 2 == 0:
        continue        # skip even numbers
    print(current_number)   # prints 1 3 5 7 9
```

---

## 📋 while Loops with Lists and Dictionaries

```python
# Move items between lists
unconfirmed_users = ['alice', 'brian', 'candace']
confirmed_users = []

while unconfirmed_users:                      # True while non-empty
    current_user = unconfirmed_users.pop()
    print(f"Verifying user: {current_user.title()}")
    confirmed_users.append(current_user)

# Remove all instances of a value
pets = ['dog', 'cat', 'dog', 'goldfish', 'cat', 'rabbit', 'cat']
print(pets)
while 'cat' in pets:
    pets.remove('cat')
print(pets)    # ['dog', 'dog', 'goldfish', 'rabbit']

# Fill a dictionary from user input
responses = {}
polling_active = True
while polling_active:
    name = input("\nWhat is your name? ")
    response = input("Which mountain would you like to climb someday? ")
    responses[name] = response
    repeat = input("Would you like to let another person respond? (yes/no) ")
    if repeat == 'no':
        polling_active = False

for name, response in responses.items():
    print(f"{name} would like to climb {response}.")
```

---

## 🔑 Key Takeaways

- `input()` always returns a **string** — convert with `int()` or `float()` for numbers
- `while condition:` runs while condition is True; update condition inside loop
- A **flag** variable (`active = True/False`) cleanly controls complex loops
- `break` exits the loop immediately; `continue` skips to the next iteration
- `while my_list:` loops until the list is empty — useful for processing queues
- `while 'val' in my_list: my_list.remove('val')` removes all occurrences
- Avoid infinite loops: always ensure the condition eventually becomes False
