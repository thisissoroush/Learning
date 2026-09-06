# Chapter 9 — Best Practices for Function-Based Views

> *"FBVs: less code, no repeated code, simple views, business logic in models."*

---

## 🎯 Core Concept

FBVs are simple: a function takes a request and returns a response. This chapter covers: passing the HttpRequest to utilities, using decorators for cross-cutting concerns, and knowing when FBVs shine.

---

## 🔑 Passing the HttpRequest Object to Utilities

```python
# utils.py
from django.core.exceptions import PermissionDenied

def check_sprinkle_rights(request):
    if request.user.can_sprinkle or request.user.is_staff:
        request.flavors = Flavor.objects.filter(is_sprinkleable=True)
        return request   # Return enriched request
    raise PermissionDenied   # Triggers 403

# views.py
def sprinkle_list(request):
    request = check_sprinkle_rights(request)
    return render(request, "list.html", {"flavors": request.flavors})
```

---

## 🎀 Decorators

```python
import functools
from django.core.exceptions import PermissionDenied

def check_sprinkles(func):
    @functools.wraps(func)    # Preserve function metadata
    def inner(request, *args, **kwargs):
        if not (request.user.can_sprinkle or request.user.is_staff):
            raise PermissionDenied
        return func(request, *args, **kwargs)
    return inner

@login_required
@check_sprinkles
def sprinkle_detail(request, pk): ...
```

### Built-in Django Decorators

```python
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.cache import cache_page

@login_required                          # Must be authenticated
@permission_required('myapp.can_edit')   # Must have permission
@require_POST                            # POST only
@cache_page(60 * 15)                     # Cache 15 minutes
def my_view(request): ...
```

---

## 📊 Custom Error Handlers (Best Use Case for FBVs)

```python
# urls.py
handler403 = "myapp.views.permission_denied_view"
handler404 = "myapp.views.page_not_found_view"
handler500 = "myapp.views.server_error_view"

# views.py
def page_not_found_view(request, exception):
    return render(request, "errors/404.html", status=404)

def server_error_view(request):
    return render(request, "errors/500.html", status=500)
```

---

## ⚠️ FBV Guidelines

```
✓ Less view code is better
✓ Never repeat code in views
✓ Business logic in models, not views
✓ Keep views simple
✓ FBVs for custom error handlers
✗ Complex nested-if blocks → extract to model/utility
✗ More than 3 decorators → consider CBV with mixins
```

---

## 💡 Key Takeaways

| Pattern | Why |
|---------|-----|
| **Pass request to utilities** | Single argument; attach extra data to it |
| **@functools.wraps** | Preserves function metadata when decorating |
| **Decorators for cross-cutting concerns** | Auth, caching, rate-limiting = reusable |
| **FBVs for error handlers** | Simpler for 403/404/500 pages |
| **Conservative with decorators** | Too many = unclear execution order |

---

*← [Back to Two Scoops of Django](../README.md)*
