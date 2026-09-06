# Chapter 10 — Best Practices for Class-Based Views

> *"Use mixins to compose behavior. Keep mixins focused on a single piece of functionality."*

---

## 🎯 Core Concept

Class-Based Views (CBVs) leverage Python's OOP to create reusable, composable view behavior. Django provides Generic Class-Based Views (GCBVs) for common patterns. The key skill: knowing which GCBV to use and how to compose mixins correctly.

---

## 📚 Which Generic CBV to Use?

| Task | GCBV to Use | Example |
|------|-------------|---------|
| Display a list of objects | `ListView` | Book list page |
| Display a single object | `DetailView` | Book detail page |
| Create an object | `CreateView` | New book form |
| Update an object | `UpdateView` | Edit book form |
| Delete an object | `DeleteView` | Delete book |
| Static page rendering | `TemplateView` | About page |
| HTTP redirects | `RedirectView` | Old URL → New URL |
| Generic form handling | `FormView` | Contact form |

---

## 📋 CBV Guidelines

```python
# 1. Constraining to authenticated users → LoginRequiredMixin FIRST
class FlavorDetailView(LoginRequiredMixin, DetailView):
    model = Flavor

# 2. Mixins before the GCBV (MRO order!)
class FlavorEditView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Flavor
    permission_required = "flavors.change_flavor"

# 3. Use template_name explicitly
class FlavorListView(ListView):
    model = Flavor
    template_name = "flavors/flavor_list.html"  # Explicit > implicit
    context_object_name = "flavors"             # Rename from object_list
```

---

## 🔀 Using Mixins

Mixins add behavior to CBVs:

```python
# A simple action mixin
class FlavorActionMixin:
    """Mixin that adds success messages to create/update views."""
    
    @property
    def success_msg(self):
        return NotImplemented  # Subclasses must define this

    def form_valid(self, form):
        messages.info(self.request, self.success_msg)
        return super().form_valid(form)


class FlavorCreateView(LoginRequiredMixin, FlavorActionMixin, CreateView):
    model = Flavor
    fields = ['title', 'slug', 'scoops_left', 'is_published']
    success_msg = "Flavor created!"  # Implements the abstract property


class FlavorUpdateView(LoginRequiredMixin, FlavorActionMixin, UpdateView):
    model = Flavor
    fields = ['title', 'slug', 'scoops_left', 'is_published']
    success_msg = "Flavor updated!"
```

### Mixin Rules

```
1. Mixins inherit from Python's object (not from Django views)
2. Base view class comes LAST in the inheritance list
3. Mixins come BEFORE the base view class
4. Keep mixins small and focused on ONE thing
```

---

## 🏗️ ModelForm + CBVs Example

```python
# models.py
class Flavor(TimeStampedModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    scoops_left = models.IntegerField(default=0)
    is_published = models.BooleanField(default=False)


# views.py
class FlavorCreateView(LoginRequiredMixin, CreateView):
    model = Flavor
    fields = ['title', 'slug', 'scoops_left', 'is_published']

    def form_valid(self, form):
        """Called when valid form data has been POSTed."""
        flavor = form.save(commit=False)
        flavor.creator = self.request.user   # Set before saving!
        flavor.save()
        return super().form_valid(form)


class FlavorUpdateView(LoginRequiredMixin, UpdateView):
    model = Flavor
    fields = ['title', 'slug', 'scoops_left', 'is_published']

    def get_object(self):
        """Ensure user can only edit their own flavors."""
        obj = super().get_object()
        if obj.creator != self.request.user:
            raise PermissionDenied
        return obj
```

---

## 🎯 Using django.views.generic.View Directly

For complex forms with multiple HTTP method handling:

```python
from django.views import View
from django.shortcuts import get_object_or_404, render, redirect


class FlavorView(View):
    """Handle both GET and POST for a flavor."""

    def get(self, request, *args, **kwargs):
        # Display the form
        flavor = get_object_or_404(Flavor, slug=kwargs['slug'])
        form = FlavorForm(instance=flavor)
        return render(request, "flavors/form.html", {"form": form, "flavor": flavor})

    def post(self, request, *args, **kwargs):
        # Process the form
        flavor = get_object_or_404(Flavor, slug=kwargs['slug'])
        form = FlavorForm(request.POST, instance=flavor)
        if form.is_valid():
            form.save()
            return redirect(flavor.get_absolute_url())
        return render(request, "flavors/form.html", {"form": form, "flavor": flavor})
```

---

## 💡 Key Takeaways

| Rule | Why |
|------|-----|
| **Right GCBV for right task** | ListView, DetailView, CreateView, UpdateView, DeleteView |
| **LoginRequiredMixin FIRST** | MRO: leftmost class = highest priority |
| **Mixins inherit from object** | Not from view classes — keep inheritance shallow |
| **form_valid() for post-save logic** | The hook for "after successful form submission" |
| **get_object() for access control** | Override to add per-object permission checks |
| **template_name explicit** | Don't rely on convention — be explicit |

---

*← [Back to Two Scoops of Django](../README.md)*
