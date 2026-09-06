# Chapter 8 — Function- and Class-Based Views

> *"Django views are just functions. A view takes an HTTP request and returns an HTTP response. That's it."*

---

## 🎯 Core Concept

This chapter covers the principles that govern ALL views — both FBVs and CBVs: keep business logic out of views, keep URLconfs clean, use URL namespaces, and understand that every view is fundamentally a function: `request → response`.

---

## 🤔 FBVs vs CBVs: When to Use Which

```
Function-Based Views (FBVs):
✓ Simple, explicit
✓ Easy to understand for beginners
✓ Great for custom error handlers (403, 404, 500)
✓ When you need fine-grained control over HTTP methods
✗ More repetition when logic is similar across views

Class-Based Views (CBVs):
✓ DRY via inheritance
✓ Built-in generic views (ListView, DetailView, etc.)
✓ Mixins for reusable behavior
✗ More complex — requires understanding MRO
✗ Hard to debug when inheritance is deep
```

**Two Scoops Recommendation:**
- Use CBVs most of the time (with generic views)
- Use FBVs when CBVs would be more complex
- Use FBVs for error handlers

---

## 🔗 Clean URLconf Design

### Keep Views Out of URLconf

```python
# BAD: Inline views in urls.py
urlpatterns = [
    path("flavors/", lambda request: HttpResponse("Hello")),  # ← Terrible!
]

# GOOD: Import views, keep urls.py clean
from flavors import views

urlpatterns = [
    path("flavors/", views.FlavorListView.as_view(), name="flavor_list"),
    path("flavors/<int:pk>/", views.FlavorDetailView.as_view(), name="flavor_detail"),
]
```

### Loose Coupling in URLconfs

```python
# BAD: Tightly coupled
from flavors.views import FlavorListView  # Specific import

# GOOD: Import the module
from flavors import views  # Then use views.FlavorListView
```

---

## 📛 URL Namespaces — Always Use Them!

URL namespaces prevent name collisions between apps:

```python
# config/urls.py
urlpatterns = [
    path("flavors/", include("flavors.urls", namespace="flavors")),
    path("stores/", include("stores.urls", namespace="stores")),
]

# In templates:
{% url "flavors:list" %}
{% url "stores:detail" store.pk %}

# In Python code:
from django.urls import reverse
reverse("flavors:list")
reverse("flavors:detail", kwargs={"pk": 1})
```

Without namespaces, `{% url "list" %}` is ambiguous — which app's list?

---

## 🏢 Views Are Functions

The fundamental truth about Django views:

```python
# A view is just this:
# HttpRequest → (some processing) → HttpResponse

# FBV version:
def flavor_list(request: HttpRequest) -> HttpResponse:
    flavors = Flavor.objects.published()
    return render(request, "flavors/list.html", {"flavors": flavors})

# CBV version (same thing, more structure):
class FlavorListView(ListView):
    template_name = "flavors/list.html"
    queryset = Flavor.objects.published()
    context_object_name = "flavors"
```

---

## 🚫 Keep Business Logic Out of Views

```python
# BAD: Business logic in view
def validate_and_create_order(request):
    # All this logic should NOT be in a view
    if request.user.subscription_tier not in ['gold', 'platinum']:
        return HttpResponseForbidden()
    if Order.objects.filter(user=request.user, status='pending').count() > 3:
        messages.error(request, "Too many pending orders")
        return redirect("order_list")
    # ... more business logic
    order = Order.objects.create(user=request.user)
    # ... even more business logic

# GOOD: Business logic in model/service layer
def validate_and_create_order(request):
    try:
        order = Order.create_for_user(request.user)  # Logic in model!
    except OrderLimitExceeded:
        messages.error(request, "Too many pending orders")
        return redirect("order_list")
    except InsufficientPermissions:
        return HttpResponseForbidden()
    return redirect("order_detail", pk=order.pk)
```

---

## 🚫 Never Use locals() as Context

```python
# BAD: Using locals() as template context
def flavor_detail(request, pk):
    flavor = get_object_or_404(Flavor, pk=pk)
    ratings = flavor.reviews.all()
    is_owner = (request.user == flavor.creator)
    
    return render(request, "flavor_detail.html", locals())
    # ↑ Passes ALL local variables! Unclear interface, fragile
    # Adding ANY local variable accidentally exposes it to templates

# GOOD: Explicit context dictionary
def flavor_detail(request, pk):
    flavor = get_object_or_404(Flavor, pk=pk)
    return render(request, "flavor_detail.html", {
        "flavor": flavor,
        "ratings": flavor.reviews.all(),
        "is_owner": request.user == flavor.creator,
    })
    # ↑ Explicit, clear, intentional
```

---

## 💡 Key Takeaways

| Rule | Why |
|------|-----|
| **Views are just functions** | HttpRequest → HttpResponse — that's the whole model |
| **Business logic out of views** | Views handle HTTP; models/services handle logic |
| **Clean URLconfs** | Import modules not individual views; no inline views |
| **URL namespaces always** | Prevent name collisions, enable `"flavors:list"` |
| **Never `locals()` as context** | Implicit, fragile, unclear interface |
| **FBVs for custom error handlers** | 403, 404, 500 — simpler as FBVs |

---

*← [Back to Two Scoops of Django](../README.md)*
