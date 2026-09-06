# Chapter 17 — Building REST APIs With Django REST Framework

> *"When in doubt, use Django REST Framework. It's the industry standard for Django APIs."*

---

## 🎯 Core Concept

Django REST Framework (DRF) is the standard way to build REST APIs in Django. It provides serializers, viewsets, authentication, permissions, and pagination — all following REST principles and Django conventions.

---

## 📦 Installation

```python
# requirements/base.txt
djangorestframework==3.13.1
django-filter==21.1    # Optional: filtering support

# settings/base.py
INSTALLED_APPS = [
    ...
    "rest_framework",
    "django_filters",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",  # Login required by default
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}
```

---

## 📝 Serializers — Converting Models to JSON

```python
# flavors/api/serializers.py
from rest_framework import serializers
from flavors.models import Flavor


class FlavorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flavor
        fields = ["id", "title", "slug", "scoops_left", "is_published"]


class FlavorDetailSerializer(serializers.ModelSerializer):
    """Extended serializer with nested data."""
    reviews = serializers.SerializerMethodField()

    class Meta:
        model = Flavor
        fields = ["id", "title", "slug", "price", "reviews"]

    def get_reviews(self, obj):
        return [{"text": r.text, "rating": r.rating} for r in obj.reviews.all()]
```

---

## 👁️ API Views with ViewSets

```python
# flavors/api/views.py
from rest_framework import viewsets, permissions
from flavors.models import Flavor
from .serializers import FlavorSerializer


class FlavorViewSet(viewsets.ModelViewSet):
    """
    ViewSet provides CRUD endpoints automatically:
    GET    /api/flavors/         → list all
    POST   /api/flavors/         → create new
    GET    /api/flavors/{id}/    → retrieve one
    PUT    /api/flavors/{id}/    → update all fields
    PATCH  /api/flavors/{id}/    → partial update
    DELETE /api/flavors/{id}/    → delete
    """
    queryset = Flavor.objects.all()
    serializer_class = FlavorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Optionally filter by is_published."""
        queryset = Flavor.objects.all()
        is_published = self.request.query_params.get('is_published')
        if is_published is not None:
            queryset = queryset.filter(is_published=is_published)
        return queryset

    def perform_create(self, serializer):
        """Set creator to current user on create."""
        serializer.save(creator=self.request.user)
```

---

## 🔗 URL Configuration

```python
# flavors/api/urls.py
from rest_framework.routers import DefaultRouter
from .views import FlavorViewSet

router = DefaultRouter()
router.register(r'flavors', FlavorViewSet, basename='flavor')

urlpatterns = router.urls
# Generates:
# /api/flavors/         (list + create)
# /api/flavors/{id}/    (retrieve, update, delete)
```

```python
# config/urls.py
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("flavors.api.urls")),
]
```

---

## 🔐 Authentication Methods

```python
# Session auth (for browser-based clients)
"rest_framework.authentication.SessionAuthentication"

# Token auth (for mobile/SPA clients)
# settings.py
INSTALLED_APPS += ["rest_framework.authtoken"]
"rest_framework.authentication.TokenAuthentication"

# JWT auth (modern standard)
pip install djangorestframework-simplejwt
"rest_framework_simplejwt.authentication.JWTAuthentication"
```

---

## 🔒 Permissions

```python
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Custom permission: only the owner can edit."""

    def has_object_permission(self, request, view, obj):
        # Read permissions for any request (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions only for the owner
        return obj.creator == request.user


# Use in ViewSet:
class FlavorViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
```

---

## 📋 Validation in Serializers

```python
class FlavorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flavor
        fields = ["title", "scoops_left", "is_published"]

    def validate_title(self, value):
        """Validate single field."""
        if "ice cream" not in value.lower():
            raise serializers.ValidationError("Title must mention ice cream")
        return value

    def validate(self, data):
        """Cross-field validation."""
        if data.get("is_published") and data.get("scoops_left", 0) == 0:
            raise serializers.ValidationError(
                "Can't publish a flavor with 0 scoops left"
            )
        return data
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **ModelSerializer** | Converts model to/from JSON automatically |
| **ViewSet** | Single class provides CRUD — use `router.register()` |
| **Router** | Generates URL patterns automatically from ViewSets |
| **perform_create()** | Override to set fields from request (like `creator`) |
| **Object-level permissions** | `has_object_permission()` for per-object access |
| **Serializer validation** | Same pattern as form validation: `validate_field()` + `validate()` |

---

*← [Back to Two Scoops of Django](../README.md)*
