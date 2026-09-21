# Chapter 16 — Downloading Data

> **Part II: Project — Data Visualization (2/3)**

---

## 🎯 What This Chapter Covers

Parsing CSV files with Python's `csv` module, working with JSON data, and mapping world data with Plotly.

---

## 📄 Reading CSV Files

```python
from pathlib import Path
import csv

# Read a CSV file
path = Path('weather_data/sitka_weather_2021_simple.csv')
lines = path.read_text().splitlines()

reader = csv.reader(lines)
header_row = next(reader)   # get headers

# Show column names and indices
for index, column_header in enumerate(header_row):
    print(index, column_header)
# 0 STATION
# 1 NAME
# 2 DATE
# 3 PRCP
# 4 TAVG
# 5 TMAX
# 6 TMIN

# Extract data
dates, highs, lows = [], [], []
for row in reader:
    current_date = datetime.strptime(row[2], '%Y-%m-%d')
    try:
        high = int(row[4])
        low = int(row[5])
    except ValueError:
        print(f"Missing data for {current_date}")
    else:
        dates.append(current_date)
        highs.append(high)
        lows.append(low)
```

---

## 📅 Plotting Dates

```python
import matplotlib.pyplot as plt
from datetime import datetime

fig, ax = plt.subplots()
ax.plot(dates, highs, color='red', alpha=0.5)
ax.plot(dates, lows, color='blue', alpha=0.5)
ax.fill_between(dates, highs, lows, facecolor='blue', alpha=0.1)

# Format date axis automatically
fig.autofmt_xdate()

title = "Daily High and Low Temperatures, 2021\nSitka, AK"
ax.set_title(title, fontsize=20)
ax.set_ylabel("Temperature (F)", fontsize=16)
ax.tick_params(axis='x', labelsize=10)
plt.show()
```

---

## 🌍 Working with JSON — World Maps

```python
from pathlib import Path
import json
import plotly.express as px

# Load GeoJSON earthquake data
path = Path('eq_data/eq_data_30_day_m1.geojson')
contents = path.read_text(encoding='utf-8')
all_eq_data = json.loads(contents)

# Extract data
all_eq_dicts = all_eq_data['features']

mags, lons, lats, eq_titles = [], [], [], []
for eq_dict in all_eq_dicts:
    mags.append(eq_dict['properties']['mag'])
    lons.append(eq_dict['geometry']['coordinates'][0])
    lats.append(eq_dict['geometry']['coordinates'][1])
    eq_titles.append(eq_dict['properties']['title'])

# Plotly world map
title = 'Global Earthquakes'
fig = px.scatter_geo(
    lat=lats,
    lon=lons,
    size=mags,                          # bubble size = magnitude
    title=title,
    color=mags,
    color_continuous_scale='Viridis',
    labels={'color': 'Magnitude'},
    projection='natural earth',
    hover_name=eq_titles,
)
fig.show()
fig.write_html('global_earthquakes.html')
```

---

## 🔑 Key Takeaways

- `csv.reader(lines)` parses CSV; `next(reader)` reads (and discards) the header row
- `datetime.strptime(date_str, '%Y-%m-%d')` parses dates from strings
- `fig.autofmt_xdate()` automatically rotates/formats date labels on x-axis
- `ax.fill_between(x, y1, y2)` fills the area between two lines
- `json.loads(text)` parses JSON string into Python dict/list
- Plotly `scatter_geo` creates world maps with lat/lon data
- `hover_name=titles` adds tooltip text shown on hover
