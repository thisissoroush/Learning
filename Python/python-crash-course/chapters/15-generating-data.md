# Chapter 15 — Generating Data

> **Part II: Project — Data Visualization (1/3)**

---

## 🎯 What This Chapter Covers

Matplotlib basics, random walks, rolling dice, scatter plots, line charts, and bar charts with Plotly.

---

## 📊 Matplotlib Basics

```python
import matplotlib.pyplot as plt

# Simple line chart
input_values = [1, 2, 3, 4, 5]
squares = [1, 4, 9, 16, 25]

fig, ax = plt.subplots()
ax.plot(input_values, squares, linewidth=3)

# Chart labels and title
ax.set_title("Square Numbers", fontsize=24)
ax.set_xlabel("Value", fontsize=14)
ax.set_ylabel("Square of Value", fontsize=14)
ax.tick_params(axis='both', labelsize=14)

plt.show()

# Scatter plot
x_values = range(1, 1001)
y_values = [x**2 for x in x_values]

fig, ax = plt.subplots()
ax.scatter(x_values, y_values, c=y_values, cmap=plt.cm.Blues, s=10)
ax.set_title("Square Numbers", fontsize=24)
ax.axis([0, 1100, 0, 1_100_000])

plt.savefig('squares_plot.png', bbox_inches='tight')
```

---

## 🚶 Random Walk

```python
# random_walk.py
from random import choice

class RandomWalk:
    """A class to generate random walks."""

    def __init__(self, num_points=5000):
        self.num_points = num_points
        self.x_values = [0]
        self.y_values = [0]

    def fill_walk(self):
        """Calculate all the points in the walk."""
        while len(self.x_values) < self.num_points:
            x_direction = choice([1, -1])
            x_distance = choice([0, 1, 2, 3, 4])
            x_step = x_direction * x_distance

            y_direction = choice([1, -1])
            y_distance = choice([0, 1, 2, 3, 4])
            y_step = y_direction * y_distance

            if x_step == 0 and y_step == 0:
                continue    # skip non-movement

            self.x_values.append(self.x_values[-1] + x_step)
            self.y_values.append(self.y_values[-1] + y_step)

# Plotting the walk
import matplotlib.pyplot as plt
from random_walk import RandomWalk

while True:
    rw = RandomWalk(50_000)
    rw.fill_walk()

    fig, ax = plt.subplots(figsize=(15, 9))
    point_numbers = range(rw.num_points)
    ax.scatter(rw.x_values, rw.y_values, c=point_numbers,
               cmap=plt.cm.Blues, edgecolors='none', s=1)
    ax.set_aspect('equal')

    # Emphasize start and end points
    ax.scatter(0, 0, c='green', edgecolors='none', s=100)
    ax.scatter(rw.x_values[-1], rw.y_values[-1],
               c='red', edgecolors='none', s=100)

    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    plt.show()

    keep_running = input("Make another walk? (y/n): ")
    if keep_running == 'n':
        break
```

---

## 🎲 Rolling Dice with Plotly

```python
# die.py
from random import randint

class Die:
    """A class representing a single die."""

    def __init__(self, num_sides=6):
        self.num_sides = num_sides

    def roll(self):
        """Return a random value between 1 and number of sides."""
        return randint(1, self.num_sides)

# Plotting dice rolls
import plotly.express as px
from die import Die

# Roll two D6 dice
die_1 = Die()
die_2 = Die()

results = [die_1.roll() + die_2.roll() for _ in range(50_000)]

# Analyze results
max_result = die_1.num_sides + die_2.num_sides
poss_results = range(2, max_result + 1)
frequencies = [results.count(value) for value in poss_results]

# Visualize results
title = "Results of Rolling Two D6 Dice 50,000 Times"
labels = {'x': 'Result', 'y': 'Frequency of Result'}
fig = px.bar(x=poss_results, y=frequencies, title=title, labels=labels)
fig.update_layout(xaxis_dtick=1)
fig.show()

# Save to HTML
fig.write_html('dice_visual.html')
```

---

## 🔑 Key Takeaways

- `fig, ax = plt.subplots()` — the modern matplotlib way to create figures
- `ax.scatter(x, y, c=values, cmap=plt.cm.Blues)` — color-map based on data values
- `plt.savefig('file.png', bbox_inches='tight')` saves without whitespace
- `plt.show()` displays interactively; close to continue code
- Plotly creates interactive HTML charts — hover, zoom, pan
- `px.bar(x=values, y=frequencies)` — Plotly Express for quick, polished charts
- `fig.write_html('chart.html')` saves interactive chart for sharing
