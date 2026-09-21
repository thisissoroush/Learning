# Chapter 9 — Classes

> **Part I: Basics**

---

## 🎯 What This Chapter Covers

Creating classes, `__init__`, instance attributes, methods, inheritance, `super()`, instances as attributes, importing classes.

---

## 🐕 Creating a Class

```python
class Dog:
    """A simple attempt to model a dog."""

    def __init__(self, name, age):
        """Initialize name and age attributes."""
        self.name = name    # instance attribute
        self.age = age

    def sit(self):
        """Simulate a dog sitting in response to a command."""
        print(f"{self.name} is now sitting.")

    def roll_over(self):
        """Simulate rolling over in response to a command."""
        print(f"{self.name} rolled over!")


# Creating an instance
my_dog = Dog('Willie', 6)
your_dog = Dog('Lucy', 3)

# Accessing attributes
print(f"My dog's name is {my_dog.name}.")   # My dog's name is Willie.
print(f"My dog is {my_dog.age} years old.")  # My dog is 6 years old.

# Calling methods
my_dog.sit()        # Willie is now sitting.
my_dog.roll_over()  # Willie rolled over!
your_dog.sit()      # Lucy is now sitting.
```

---

## 🚗 Working with Attributes

```python
class Car:
    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year
        self.odometer_reading = 0    # default value

    def get_descriptive_name(self):
        long_name = f"{self.year} {self.make} {self.model}"
        return long_name.title()

    def read_odometer(self):
        print(f"This car has {self.odometer_reading} miles on it.")

    def update_odometer(self, mileage):
        if mileage >= self.odometer_reading:
            self.odometer_reading = mileage
        else:
            print("You can't roll back an odometer!")

    def increment_odometer(self, miles):
        self.odometer_reading += miles


my_new_car = Car('audi', 'a4', 2024)
print(my_new_car.get_descriptive_name())   # 2024 Audi A4
my_new_car.update_odometer(23)
my_new_car.read_odometer()                 # This car has 23 miles on it.
```

---

## 🧬 Inheritance

```python
# Child class inherits from parent class
class ElectricCar(Car):
    """Represent aspects of a car, specific to electric vehicles."""

    def __init__(self, make, model, year):
        """Initialize attributes of the parent class."""
        super().__init__(make, model, year)   # call parent __init__
        self.battery_size = 40               # child-only attribute

    def describe_battery(self):
        print(f"This car has a {self.battery_size}-kWh battery.")

    # Override parent method
    def fill_gas_tank(self):
        print("This car doesn't have a gas tank!")


my_leaf = ElectricCar('nissan', 'leaf', 2024)
print(my_leaf.get_descriptive_name())   # 2024 Nissan Leaf (inherited)
my_leaf.describe_battery()              # This car has a 40-kWh battery.
```

---

## 🔌 Instances as Attributes

```python
class Battery:
    """A simple attempt to model a battery for an electric car."""

    def __init__(self, battery_size=40):
        self.battery_size = battery_size

    def describe_battery(self):
        print(f"This car has a {self.battery_size}-kWh battery.")

    def get_range(self):
        if self.battery_size == 40:
            range = 150
        elif self.battery_size == 65:
            range = 225
        print(f"This car can go about {range} miles on a full charge.")


class ElectricCar(Car):
    def __init__(self, make, model, year):
        super().__init__(make, model, year)
        self.battery = Battery()    # instance as attribute


my_leaf = ElectricCar('nissan', 'leaf', 2024)
my_leaf.battery.describe_battery()    # This car has a 40-kWh battery.
my_leaf.battery.get_range()
```

---

## 📦 Importing Classes

```python
# car.py — module with classes
class Car: ...
class ElectricCar(Car): ...

# my_car.py — using the module
from car import Car
from car import Car, ElectricCar         # multiple classes
import car                               # whole module (car.Car())
from car import Car as C                 # alias
```

---

## 🔑 Key Takeaways

- `__init__` runs automatically when an instance is created
- `self` refers to the current instance — always the first parameter
- Attributes defined with `self.name = value` are accessible throughout the class
- Set default values in `__init__`: `self.odometer_reading = 0`
- `super().__init__(...)` calls the parent's `__init__` — always call it first in child
- Override parent methods by redefining them in the child class
- Use instances as attributes to break complex classes into smaller collaborating objects
- Keep each class in its own module for clean organization
