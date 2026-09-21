# Chapter 19 — User Accounts

> **Part II: Project — Learning Log (2/3)**

---

## 🎯 What This Chapter Covers

User registration, login/logout, restricting access, connecting data to users, and letting users own their own data.

---

## 🔐 Login and Logout

```python
# ll_project/urls.py
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('learning_logs.urls')),
]
# django.contrib.auth.urls provides: login/, logout/, password_change/, etc.
```

```html
<!-- registration/login.html -->
{% extends "learning_logs/base.html" %}
{% block content %}
  {% if form.errors %}
    <p>Your username and password didn't match. Please try again.</p>
  {% endif %}
  <form method="post" action="{% url 'login' %}">
    {% csrf_token %}
    {{ form.as_div }}
    <button name="submit">Log in</button>
  </form>
{% endblock content %}
```

```python
# settings.py — redirect after login/logout
LOGIN_REDIRECT_URL = 'learning_logs:index'
LOGOUT_REDIRECT_URL = 'learning_logs:index'
```

---

## 📝 User Registration

```python
# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm

def register(request):
    """Register a new user."""
    if request.method != 'POST':
        form = UserCreationForm()
    else:
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)        # log in automatically
            return redirect('learning_logs:index')
    context = {'form': form}
    return render(request, 'registration/register.html', context)
```

---

## 🔒 Restricting Access

```python
# Require login for specific views
from django.contrib.auth.decorators import login_required

@login_required
def topics(request):
    ...

# Redirect unauthenticated users to login page
# settings.py
LOGIN_URL = 'login'
```

```html
<!-- base.html — show login/logout links -->
{% if user.is_authenticated %}
  Hello, {{ user.username }}.
  <a href="{% url 'logout' %}">Log out</a>
{% else %}
  <a href="{% url 'login' %}">Log in</a>
  <a href="{% url 'users:register' %}">Register</a>
{% endif %}
```

---

## 👤 Connecting Data to Users

```python
# models.py — add owner to Topic
from django.contrib.auth.models import User

class Topic(models.Model):
    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.text
```

```bash
python manage.py makemigrations learning_logs
# Provide a default for existing rows:
# 1 — select an existing user id (e.g. 1 for superuser)
python manage.py migrate
```

```python
# views.py — filter by current user
@login_required
def topics(request):
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics}
    return render(request, 'learning_logs/topics.html', context)

# Protect individual topic views
from django.http import Http404

@login_required
def topic(request, topic_id):
    topic = Topic.objects.get(id=topic_id)
    if topic.owner != request.user:
        raise Http404    # 404 instead of 403 — doesn't reveal data exists
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)
```

---

## 📋 Forms for Adding Data

```python
# forms.py
from django import forms
from .models import Topic, Entry

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['text']
        labels = {'text': ''}

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['text']
        labels = {'text': ''}
        widgets = {'text': forms.Textarea(attrs={'cols': 80})}

# views.py — add new topic
@login_required
def new_topic(request):
    if request.method != 'POST':
        form = TopicForm()
    else:
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)    # don't save yet
            new_topic.owner = request.user          # set owner
            new_topic.save()                        # now save
            return redirect('learning_logs:topics')
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)
```

---

## 🔑 Key Takeaways

- `include('django.contrib.auth.urls')` provides login, logout, password management for free
- `@login_required` decorator redirects unauthenticated users to `LOGIN_URL`
- `request.user` gives you the current logged-in user in any view
- Use `Http404` instead of `Http403` when unauthorized — doesn't leak data existence
- `form.save(commit=False)` creates the model instance without saving — lets you add extra fields before saving
- `{% csrf_token %}` is mandatory in every POST form — Django rejects forms without it
- `filter(owner=request.user)` ensures users only see their own data
