# Chapter 12 — Common Patterns for Forms

> *"Forms are Django's most powerful feature. Use ModelForms for most cases; understand when to use plain Forms."*

---

## 🎯 Core Concept

Django forms validate data, display widgets, and convert raw HTTP data into Python objects. This chapter covers 5 essential patterns from simple ModelForms to complex multi-form scenarios.

---

## 📋 Pattern 1: Simple ModelForm with Default Validators

```python
# flavors/forms.py
from django import forms
from .models import Flavor


class FlavorForm(forms.ModelForm):
    class Meta:
        model = Flavor
        fields = ['title', 'slug', 'scoops_left', 'is_published']
```

```python
# views.py
class FlavorCreateView(LoginRequiredMixin, CreateView):
    model = Flavor
    form_class = FlavorForm   # Use our custom form
    # Or: fields = ['title', 'slug', ...]  # Django creates form automatically
```

---

## 📋 Pattern 2: Custom Field Validators

```python
# flavors/validators.py
from django.core.exceptions import ValidationError


def validate_tasty(value):
    """Ensure the flavor name contains 'Tasty'."""
    if "Tasty" not in value:
        msg = "Must start with the word 'Tasty'"
        raise ValidationError(msg)


# flavors/forms.py
class TastyIceCreamReviewForm(forms.ModelForm):
    class Meta:
        model = IceCreamReview
        fields = ['title', 'review', 'slug', 'rating']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].validators.append(validate_tasty)
        self.fields['review'].validators.append(validate_tasty)
```

---

## 📋 Pattern 3: Overriding Clean Stage of Validation

```python
class IceCreamReviewForm(forms.ModelForm):
    class Meta:
        model = IceCreamReview
        fields = ['title', 'review', 'slug', 'rating']

    def clean_slug(self):
        """Custom validation for the slug field."""
        return self.cleaned_data['slug'].lower()

    def clean(self):
        """Cross-field validation (checks multiple fields together)."""
        cleaned_data = super().clean()
        slug = cleaned_data.get("slug", "")
        title = cleaned_data.get("title", "")

        if slug not in title.lower():
            raise forms.ValidationError("Slug must be in title!")
        return cleaned_data
```

**When to use `clean()` vs `clean_<field>()`:**

```
clean_<field>():  → Validates ONE field
                    Return the cleaned value or raise ValidationError

clean():          → Cross-field validation
                    Return cleaned_data dict
                    Runs AFTER all individual field validation
```

---

## 📋 Pattern 4: Hacking Form Fields (2 CBVs, 2 Forms, 1 Model)

When different views need different fields on the same model:

```python
# Two forms for one model
class FlavorForm(forms.ModelForm):
    """Full form for admins."""
    class Meta:
        model = Flavor
        fields = ['title', 'slug', 'scoops_left', 'is_published', 'creator']


class FlavorPublicForm(forms.ModelForm):
    """Limited form for public users — no creator, no publish toggle."""
    class Meta:
        model = Flavor
        fields = ['title', 'slug', 'scoops_left']  # Subset of fields


# In views:
class FlavorAdminUpdateView(AdminMixin, UpdateView):
    form_class = FlavorForm     # Full form for admins

class FlavorUserUpdateView(LoginRequiredMixin, UpdateView):
    form_class = FlavorPublicForm  # Limited form for users
```

---

## 📋 Pattern 5: Reusable Search Mixin

```python
class TitleSearchMixin:
    """Mixin for adding search functionality to ListView."""

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            return queryset.filter(title__icontains=q)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_term'] = self.request.GET.get("q", "")
        return context


# Reuse in multiple views
class FlavorListView(TitleSearchMixin, ListView):
    model = Flavor

class StoreListView(TitleSearchMixin, ListView):
    model = Store
```

---

## 🔒 CSRF Protection

```html
<!-- Always include on all forms that modify data -->
<form method="post">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">Submit</button>
</form>
```

```python
# For AJAX POST requests — include CSRF in headers:
fetch('/api/flavors/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
})
```

---

## 💡 Key Takeaways

| Pattern | When to Use |
|---------|-------------|
| **Simple ModelForm** | 90% of forms — CRUD operations |
| **Custom validators** | Field-specific validation (add to `validators=`) |
| **clean_field()** | Single-field custom validation |
| **clean()** | Cross-field validation |
| **Multiple forms per model** | Different roles need different fields |
| **TitleSearchMixin** | Reusable search — add to any ListView |

---

*← [Back to Two Scoops of Django](../README.md)*
