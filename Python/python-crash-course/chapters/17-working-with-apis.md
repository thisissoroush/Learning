# Chapter 17 — Working with APIs

> **Part II: Project — Data Visualization (3/3)**

---

## 🎯 What This Chapter Covers

Calling REST APIs with `requests`, parsing JSON responses, and visualizing API data with Plotly.

---

## 🌐 Using the GitHub API

```python
import requests
import plotly.express as px

# Make an API call and inspect the response
url = "https://api.github.com/search/repositories"
url += "?q=language:python+sort:stars+stars:>10000"

headers = {"Accept": "application/vnd.github.v3+json"}
r = requests.get(url, headers=headers)
print(f"Status code: {r.status_code}")  # 200 = success

# Parse the JSON response
response_dict = r.json()
print(f"Total repositories: {response_dict['total_count']}")
print(f"Complete results: {not response_dict['incomplete_results']}")

# Extract repo information
repo_dicts = response_dict['items']
print(f"Repositories returned: {len(repo_dicts)}")

repo_names, stars, hover_texts = [], [], []
for repo_dict in repo_dicts:
    repo_names.append(repo_dict['name'])
    stars.append(repo_dict['stargazers_count'])

    # Build hover text
    owner = repo_dict['owner']['login']
    description = repo_dict['description'] or ''
    hover_text = f"{owner}<br />{description}"
    hover_texts.append(hover_text)
```

---

## 📊 Visualizing API Data

```python
# Create bar chart of most-starred Python repos
title = "Most-Starred Python Projects on GitHub"
labels = {'x': 'Repository', 'y': 'Stars'}
fig = px.bar(
    x=repo_names,
    y=stars,
    title=title,
    labels=labels,
    hover_name=hover_texts,
)

fig.update_layout(
    title_font_size=28,
    xaxis_title_font_size=20,
    yaxis_title_font_size=20,
)
fig.update_traces(marker_color='SteelBlue', marker_opacity=0.6)
fig.show()
```

---

## 🔍 Inspecting API Responses

```python
# Check status code
r = requests.get(url, headers=headers)
if r.status_code == 200:
    response_dict = r.json()
elif r.status_code == 403:
    print("Rate limit exceeded — wait before retrying")

# Explore nested response structure
for repo_dict in repo_dicts[:5]:
    print(f"\nName: {repo_dict['name']}")
    print(f"  Owner: {repo_dict['owner']['login']}")
    print(f"  Stars: {repo_dict['stargazers_count']}")
    print(f"  Repository: {repo_dict['html_url']}")
    print(f"  Description: {repo_dict['description']}")
```

---

## 🔑 Key Takeaways

- `requests.get(url, headers=headers)` makes an HTTP GET request
- `r.status_code == 200` means success; 403 = rate limited; 404 = not found
- `r.json()` parses the JSON response into Python dict/list
- APIs often return paginated results — check `total_count` vs `len(items)`
- `hover_name` and `hover_data` add rich tooltip info to Plotly charts
- Rate limits: GitHub API allows 60 unauthenticated requests/hour (more with auth token)
- Always check `response_dict['incomplete_results']` — True means data was truncated
