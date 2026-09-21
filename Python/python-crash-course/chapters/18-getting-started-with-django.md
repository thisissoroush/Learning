# Chapter 18 — Getting Started with Django

> **Part II: Project — Learning Log (1/3)**

---

## 🎯 What This Chapter Covers

Setting up a Django project, creating models, using the admin site, building views, templates, and URLs.

---

## 🏗️ Project Setup

```bash
# Create virtual environment and install Django
python -m venv ll_env
source ll_env/bin/activate       # macOS/Linux
ll_env\Scripts\activate          # Windows

pip install django

# Create project and app
django-admin startproject ll_project .
python manage.py startapp learning_logs

# Run development server
python manage.py runserver       # http://localhost:8000
```

```python
# ll_project/settings.py — register the app
INSTALLED_APPS = [
    'django.contrib.admin',
    ...
    'learning_logs',   # add this
]
```

---

## 📊 Models

```python
# learning_logs/models.py
from django.db import models

class Topic(models.Model):
    """A topic the user is learning about."""
    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

class Entry(models.Model):
    """A journal entry about a particular topic."""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'entries'

    def __str__(self):
        return f"{self.text[:50]}..."
```

```bash
# Create and apply migrations
python manage.py makemigrations learning_logs
python manage.py migrate
```

---

## 🔑 Admin Site

```python
# learning_logs/admin.py
from django.contrib import admin
from .models import Topic, Entry

admin.site.register(Topic)
admin.site.register(Entry)
```

```bash
# Create admin superuser
python manage.py createsuperuser
# Visit http://localhost:8000/admin/
```

---

## 🔗 URLs

```python
# ll_project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('learning_logs.urls')),
]

# learning_logs/urls.py
from django.urls import path
from . import views

app_name = 'learning_logs'
urlpatterns = [
    path('', views.index, name='index'),
    path('topics/', views.topics, name='topics'),
    path('topics/<int:topic_id>/', views.topic, name='topic'),
]
```

---

## 👁️ Views

```python
# learning_logs/views.py
from django.shortcuts import render
from .models import Topic

def index(request):
    """The home page for Learning Log."""
    return render(request, 'learning_logs/index.html')

def topics(request):
    """Show all topics."""
    topics = Topic.objects.order_by('date_added')
    context = {'topics': topics}
    return render(request, 'learning_logs/topics.html', context)

def topic(request, topic_id):
    """Show a single topic and all its entries."""
    topic = Topic.objects.get(id=topic_id)
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)
```

---

## 🎨 Templates

```html
<!-- learning_logs/templates/learning_logs/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Learning Log</title>
</head>
<body>
  <p>
    <a href="{% url 'learning_logs:index' %}">Learning Log</a> -
    <a href="{% url 'learning_logs:topics' %}">Topics</a>
  </p>
  <hr>
  {% block content %}{% endblock content %}
</body>
</html>

<!-- topics.html -->
{% extends "learning_logs/base.html" %}
{% block content %}
  <p>Topics</p>
  <ul>
    {% for topic in topics %}
      <li>
        <a href="{% url 'learning_logs:topic' topic.id %}">
          {{ topic.text }}
        </a>
      </li>
    {% empty %}
      <li>No topics have been added yet.</li>
    {% endfor %}
  </ul>
{% endblock content %}
```

---

## 🔑 Key Takeaways

- Django's MTV: **M**odels (data), **T**emplates (HTML), **V**iews (logic)
- `makemigrations` creates migration files; `migrate` applies them to the DB
- `on_delete=models.CASCADE` deletes related entries when a topic is deleted
- `auto_now_add=True` automatically sets the timestamp when the object is created
- `app_name = 'learning_logs'` in urls.py enables namespaced URL reversing
- `{% url 'learning_logs:topics' %}` in templates generates URLs by name — no hardcoding
- `{% extends "base.html" %}` + `{% block content %}` = template inheritance
