# 🦄 Django — Interview Questions (Junior → Architect)

A comprehensive set of Django-specific interview questions, organized from fundamentals to architecture-level design.

---

## 🟢 Junior Level

---

### 1. What is Django and what is its design philosophy?

**A:** Django is a high-level Python web framework that follows the **"batteries included"** philosophy — it ships with an ORM, admin panel, authentication, form handling, templating, sessions, and more out of the box.

**Design principles:**
- **DRY (Don't Repeat Yourself)** — one place for each piece of knowledge
- **Explicit is better than implicit** — configuration is clear, not magic
- **Loose coupling** — components (ORM, views, URLs) work independently

**MTV pattern (Django's MVC variant):**
- **Model** — data layer (ORM)
- **Template** — presentation layer
- **View** — business logic / request handling

---

### 2. What is the Django request/response lifecycle?

**A:** From browser to response:

```
Browser → WSGI/ASGI server (Gunicorn/Uvicorn)
       → Django middleware stack (top → bottom)
       → URL dispatcher (urls.py)
       → View function/class
       → (optional) Template rendering
       → Response
       → Middleware stack (bottom → top)
       → Browser
```

Each middleware can modify the request before the view and the response after.

---

### 3. What is `urls.py` and how does URL routing work?

**A:**

```python
# project/urls.py
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("myapp.urls")),  # delegate to app urls
]

# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("users/", views.user_list, name="user-list"),
    path("users/<int:pk>/", views.user_detail, name="user-detail"),
    path("users/<uuid:id>/orders/", views.user_orders, name="user-orders"),
]
```

URL converters: `int`, `str`, `uuid`, `slug`, `path`.

---

### 4. What is the difference between a function-based view and a class-based view?

**A:**

```python
# Function-based view (FBV)
from django.shortcuts import render, get_object_or_404

def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
    return render(request, "user_detail.html", {"user": user})

# Class-based view (CBV)
from django.views import View
from django.views.generic import DetailView, UpdateView

class UserDetailView(DetailView):
    model = User
    template_name = "user_detail.html"
    context_object_name = "user"
```

FBVs: simpler, explicit, easier to read. CBVs: reuse via inheritance, generic views reduce boilerplate. FBVs are preferred for complex custom logic; CBVs for CRUD.

---

### 5. What is the Django ORM? How do you query the database?

**A:**

```python
# Basic CRUD
user = User.objects.create(name="Alice", email="alice@example.com")

users = User.objects.all()
active = User.objects.filter(is_active=True)
one = User.objects.get(pk=1)            # raises DoesNotExist if not found
first = User.objects.filter(age__gte=18).first()

# Update
User.objects.filter(id=1).update(name="Bob")

# Delete
User.objects.filter(is_active=False).delete()

# Chaining
User.objects.filter(is_active=True).exclude(role="admin").order_by("-created_at")[:10]
```

Querysets are **lazy** — SQL isn't executed until evaluated (iteration, `list()`, `count()`, etc.).

---

### 6. What are field lookups in Django ORM?

**A:**

```python
User.objects.filter(name__exact="Alice")    # = 'Alice'
User.objects.filter(name__iexact="alice")   # case-insensitive
User.objects.filter(name__contains="li")    # LIKE '%li%'
User.objects.filter(name__startswith="Al")  # LIKE 'Al%'
User.objects.filter(age__gte=18)            # >= 18
User.objects.filter(age__lt=65)             # < 65
User.objects.filter(age__in=[25, 30, 35])   # IN (25, 30, 35)
User.objects.filter(bio__isnull=True)       # IS NULL
User.objects.filter(created__date=date.today())   # date part
User.objects.filter(name__regex=r'^A.*')    # regex
```

---

### 7. What is `get_object_or_404` and when do you use it?

**A:**

```python
from django.shortcuts import get_object_or_404

# Instead of:
try:
    user = User.objects.get(pk=pk)
except User.DoesNotExist:
    raise Http404

# Use:
user = get_object_or_404(User, pk=pk)
user = get_object_or_404(User, pk=pk, is_active=True)  # extra filters
```

Returns the object or raises `Http404` (which Django converts to a 404 response). Use in views where a missing object means the page doesn't exist.

---

### 8. What is Django's template language?

**A:**

```html
<!-- Variables -->
{{ user.name }}
{{ user.name|upper }}
{{ price|floatformat:2 }}

<!-- Tags -->
{% if user.is_authenticated %}
    <p>Hello, {{ user.username }}</p>
{% else %}
    <a href="{% url 'login' %}">Login</a>
{% endif %}

{% for item in items %}
    <li>{{ forloop.counter }}. {{ item.name }}</li>
{% empty %}
    <li>No items.</li>
{% endfor %}

<!-- Template inheritance -->
{% extends "base.html" %}
{% block content %}
    <h1>Page content</h1>
{% endblock %}

{% include "partials/navbar.html" %}
```

---

### 9. What is `settings.py` and what are the most important settings?

**A:**

```python
# Core settings
DEBUG = False          # Never True in production
SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = ["myapp.com"]

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": "5432",
    }
}

# Apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "rest_framework",
    "myapp",
]

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files (uploads)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

---

### 10. What is Django's admin panel and how do you register a model?

**A:**

```python
# admin.py
from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "stock", "is_active"]
    list_filter = ["is_active", "category"]
    search_fields = ["name", "description"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = [
        ("Basic Info", {"fields": ["name", "description"]}),
        ("Pricing", {"fields": ["price", "cost"]}),
        ("Inventory", {"fields": ["stock", "is_active"]}),
    ]
```

The admin is auto-generated from your models — useful for internal tools, content management, and debugging.

---

### 11. What are Django forms and how does validation work?

**A:**

```python
from django import forms
from .models import User

class UserForm(forms.ModelForm):
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        widgets = {"password": forms.PasswordInput}

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered.")
        return email

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") != cleaned.get("password_confirm"):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned

# In view
form = UserForm(request.POST)
if form.is_valid():
    form.save()
```

---

### 12. What is CSRF protection in Django and how does it work?

**A:** Django protects POST forms against **Cross-Site Request Forgery** by embedding a unique token per session:

```html
<form method="post">
    {% csrf_token %}  <!-- renders hidden input with token -->
    ...
</form>
```

Django's `CsrfViewMiddleware` verifies the token on every POST/PUT/PATCH/DELETE request. For AJAX:

```javascript
fetch("/api/data/", {
    method: "POST",
    headers: { "X-CSRFToken": getCookie("csrftoken") },
    body: JSON.stringify(data)
});
```

For APIs using token auth (DRF), CSRF is typically exempted on `SessionAuthentication`-excluded views.

---

### 13. What is `manage.py` and what are the most common commands?

**A:**

```bash
python manage.py runserver           # dev server
python manage.py runserver 0.0.0.0:8080

python manage.py makemigrations      # generate migrations from model changes
python manage.py migrate             # apply migrations
python manage.py showmigrations      # list migrations and their status

python manage.py createsuperuser     # create admin user
python manage.py shell               # interactive Python shell with Django context
python manage.py shell_plus          # (django-extensions) with auto-imports

python manage.py collectstatic       # gather static files
python manage.py test                # run tests
python manage.py check               # check for configuration issues
python manage.py dbshell             # database CLI
```

---

### 14. What is `ForeignKey`, `ManyToManyField`, and `OneToOneField`?

**A:**

```python
class Author(models.Model):
    name = models.CharField(max_length=200)

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")
    # Book belongs to one Author; Author has many Books

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Exactly one Profile per User

class Tag(models.Model):
    name = models.CharField(max_length=50)

class Article(models.Model):
    tags = models.ManyToManyField(Tag, blank=True)
    # Many Articles ↔ Many Tags

# Querying
author.books.all()           # reverse relation
book.author.name             # forward relation
article.tags.add(tag)
article.tags.filter(name="python")
```

---

### 15. What is `on_delete` in ForeignKey?

**A:** Defines what happens to related objects when the referenced object is deleted:

| Option | Behavior |
|--------|----------|
| `CASCADE` | Delete related objects too |
| `PROTECT` | Raise `ProtectedError` — prevents deletion |
| `SET_NULL` | Set FK to NULL (requires `null=True`) |
| `SET_DEFAULT` | Set FK to `default` value |
| `DO_NOTHING` | Do nothing in Python (may break DB integrity) |
| `RESTRICT` | Raise `RestrictedError` (similar to PROTECT, stricter) |

---

## 🟡 Mid Level

---

### 16. What is `select_related` vs `prefetch_related` and why do they matter?

**A:** Both solve the **N+1 query problem** — but differently:

```python
# N+1 PROBLEM: 1 query for posts + 1 per post for author = N+1 total
posts = Post.objects.all()
for post in posts:
    print(post.author.name)  # separate query per post!

# select_related — SQL JOIN; use for ForeignKey and OneToOne
posts = Post.objects.select_related("author").all()
# 1 query total (JOIN)

# prefetch_related — separate query + Python join; use for ManyToMany and reverse FK
articles = Article.objects.prefetch_related("tags").all()
# 2 queries: one for articles, one for all tags

# Combining
Post.objects.select_related("author").prefetch_related("comments__author")
```

`select_related` = one SQL JOIN. `prefetch_related` = separate SQL query with `IN (...)`, joined in Python.

---

### 17. What are Django signals and how do you use them?

**A:**

```python
from django.db.models.signals import post_save, pre_delete, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

# Connect signals in AppConfig.ready()
class MyAppConfig(AppConfig):
    def ready(self):
        import myapp.signals  # noqa: F401
```

**Pitfalls:**
- Signals are synchronous — slow handlers block the request
- `post_save` fires even inside a transaction that later rolls back; use `transaction.on_commit`
- Hidden coupling — hard to trace

---

### 18. What is `transaction.atomic` and `transaction.on_commit`?

**A:**

```python
from django.db import transaction

# Wrap operations in a transaction
with transaction.atomic():
    order = Order.objects.create(user=user, total=100)
    OrderItem.objects.create(order=order, product=product)
    # If anything raises, BOTH are rolled back

# As decorator
@transaction.atomic
def transfer_funds(from_acc, to_acc, amount):
    from_acc.balance -= amount
    to_acc.balance += amount
    from_acc.save()
    to_acc.save()

# on_commit — runs ONLY after the transaction successfully commits
def on_order_created():
    send_confirmation_email.delay(order.id)

with transaction.atomic():
    order = Order.objects.create(...)
    transaction.on_commit(on_order_created)
    # Email only sent if the transaction commits
```

---

### 19. What is Django REST Framework (DRF) and what are its core components?

**A:** DRF is a toolkit for building Web APIs on top of Django:

**Core components:**

```python
# Serializer — validates input, serializes output
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name"]
        read_only_fields = ["id"]

# ViewSet — combines list, create, retrieve, update, destroy
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["is_active"]

# Router — auto-generates URLs
router = DefaultRouter()
router.register("users", UserViewSet)
urlpatterns = router.urls
# Generates: /users/, /users/{pk}/
```

---

### 20. What is the difference between `APIView`, `GenericAPIView`, and `ViewSet`?

**A:**

| Class | What it provides |
|-------|-----------------|
| `APIView` | Base class, handle HTTP methods manually |
| `GenericAPIView` | Adds queryset, serializer_class, pagination |
| `ListCreateAPIView` | GET list + POST create |
| `RetrieveUpdateDestroyAPIView` | GET/PUT/PATCH/DELETE for one object |
| `ViewSet` | Combine actions, works with Router |
| `ModelViewSet` | Full CRUD ViewSet auto-wired to model |

```python
# APIView — most control, most code
class UserListView(APIView):
    def get(self, request):
        users = User.objects.all()
        return Response(UserSerializer(users, many=True).data)

    def post(self, request):
        s = UserSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data, status=201)

# ModelViewSet — least code, least control
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
```

---

### 21. How does DRF authentication and permission work?

**A:**

```python
# settings.py
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# Custom permission
class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner == request.user or request.user.is_staff

# On view
class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    authentication_classes = [JWTAuthentication]
```

---

### 22. What are DRF serializer validators?

**A:**

```python
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["name", "price", "stock"]

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value

    def validate(self, attrs):
        if attrs["price"] == 0 and attrs["stock"] > 0:
            raise serializers.ValidationError("Free products can't have stock.")
        return attrs

    # Field-level validator as standalone function
    name = serializers.CharField(validators=[
        UniqueValidator(queryset=Product.objects.all())
    ])
```

---

### 23. What is `Q` objects and complex filtering?

**A:** `Q` objects allow complex `OR`, `AND`, `NOT` queries:

```python
from django.db.models import Q

# OR
User.objects.filter(Q(name="Alice") | Q(name="Bob"))

# AND (same as chaining .filter())
User.objects.filter(Q(is_active=True) & Q(age__gte=18))

# NOT
User.objects.filter(~Q(role="banned"))

# Combining
User.objects.filter(
    (Q(country="US") | Q(country="CA")) & Q(is_active=True)
).exclude(Q(role="admin"))
```

---

### 24. What is `annotate` and `aggregate`?

**A:**

```python
from django.db.models import Count, Sum, Avg, Max, Min, F

# aggregate — returns a dict (single result across whole queryset)
Order.objects.aggregate(
    total_revenue=Sum("total"),
    avg_order=Avg("total"),
    order_count=Count("id")
)
# {"total_revenue": 50000, "avg_order": 150.0, "order_count": 333}

# annotate — adds a computed field per row
users = User.objects.annotate(
    order_count=Count("orders"),
    total_spent=Sum("orders__total")
).filter(order_count__gte=5).order_by("-total_spent")

for u in users:
    print(u.order_count, u.total_spent)

# F expressions — reference other fields in the DB
Product.objects.filter(stock__lt=F("reorder_level"))
Product.objects.update(price=F("price") * 1.1)  # 10% price increase
```

---

### 25. What is Django's caching framework?

**A:**

```python
# settings.py
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
    }
}

# Low-level API
from django.core.cache import cache

cache.set("user:42", user_data, timeout=300)   # 5 minutes
data = cache.get("user:42", default=None)
cache.delete("user:42")
cache.get_or_set("key", lambda: compute_value(), 60)

# Per-view caching
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)
def my_view(request): ...

# Template fragment
{% load cache %}
{% cache 300 "sidebar" user.id %}
    <!-- expensive block -->
{% endcache %}
```

---

### 26. What are Django migrations and how do you manage them?

**A:**

```bash
python manage.py makemigrations          # detect model changes, generate file
python manage.py makemigrations --name add_phone_to_user
python manage.py migrate                 # apply all pending migrations
python manage.py migrate myapp 0003      # migrate to a specific version
python manage.py migrate myapp zero      # unapply all migrations for app
python manage.py showmigrations          # list status
python manage.py sqlmigrate myapp 0001   # show SQL for a migration
python manage.py squashmigrations myapp 0001 0010  # squash into one
```

**Safe migration pattern (zero-downtime):**
1. Add nullable column → deploy → backfill → make non-nullable in next deploy

---

### 27. What is `RunPython` and `RunSQL` in migrations?

**A:** For data migrations or complex schema changes:

```python
# migrations/0005_populate_slugs.py
from django.db import migrations
from django.utils.text import slugify

def populate_slugs(apps, schema_editor):
    Article = apps.get_model("myapp", "Article")
    for article in Article.objects.all():
        article.slug = slugify(article.title)
        article.save(update_fields=["slug"])

def reverse_slugs(apps, schema_editor):
    Article = apps.get_model("myapp", "Article")
    Article.objects.all().update(slug="")

class Migration(migrations.Migration):
    dependencies = [("myapp", "0004_add_slug")]

    operations = [
        migrations.RunPython(populate_slugs, reverse_code=reverse_slugs),
        migrations.RunSQL("CREATE INDEX CONCURRENTLY idx_slug ON myapp_article(slug);",
                          reverse_sql="DROP INDEX idx_slug;"),
    ]
```

---

### 28. What is `related_name` and why is it important?

**A:** `related_name` defines the reverse accessor name from the related model back to this one:

```python
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    # Without related_name: user.post_set.all()
    # With related_name:    user.posts.all()

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    # Two FKs to User with different related names

# Use related_name="+" to disable the reverse relation
class Log(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
```

---

### 29. How do you write tests in Django?

**A:**

```python
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient

class UserAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", "alice@test.com", "pass")
        self.client.force_authenticate(user=self.user)

    def test_list_users(self):
        resp = self.client.get(reverse("user-list"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

    def test_create_user_unauthenticated(self):
        self.client.logout()
        resp = self.client.post(reverse("user-list"), {"email": "x@x.com"})
        self.assertEqual(resp.status_code, 401)

    def test_model_signal(self):
        user = User.objects.create_user("bob", "bob@test.com", "pass")
        self.assertTrue(Profile.objects.filter(user=user).exists())
```

---

### 30. What is `ContentType` framework?

**A:** Django's `contenttypes` framework provides a generic way to relate a model to any other model:

```python
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Comment(models.Model):
    # Generic FK — can comment on any object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    text = models.TextField()

# Usage
post = Post.objects.first()
Comment.objects.create(content_object=post, text="Great post!")

# Query
ct = ContentType.objects.get_for_model(Post)
comments = Comment.objects.filter(content_type=ct, object_id=post.id)
```

Used by Django's admin `LogEntry`, `django-taggit`, and notification systems.

---

## 🔴 Senior Level

---

### 31. How does Django's ORM generate SQL and how do you debug it?

**A:**

```python
# See the SQL for any queryset
qs = User.objects.filter(is_active=True).order_by("name")
print(qs.query)
# SELECT "auth_user"."id", ... FROM "auth_user" WHERE "auth_user"."is_active" = true ORDER BY ...

# Django Debug Toolbar — shows all queries per request in browser
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

# Log all SQL queries
LOGGING = {
    "version": 1,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "django.db.backends": {"handlers": ["console"], "level": "DEBUG"},
    },
}

# Count queries in a test
from django.test.utils import CaptureQueriesContext
from django.db import connection

with CaptureQueriesContext(connection) as ctx:
    result = list(User.objects.prefetch_related("orders").all())
print(f"Queries: {len(ctx)}")
```

---

### 32. How do you implement custom model managers and querysets?

**A:**

```python
class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class ProductQuerySet(models.QuerySet):
    def in_stock(self):
        return self.filter(stock__gt=0)

    def expensive(self, threshold=100):
        return self.filter(price__gte=threshold)

    def published(self):
        return self.filter(is_published=True, published_at__lte=timezone.now())

class Product(models.Model):
    is_active = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    stock = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    published_at = models.DateTimeField(null=True)

    objects = ProductQuerySet.as_manager()
    active = ActiveManager()

# Usage
Product.objects.in_stock().expensive(200).published()
Product.active.all()
```

---

### 33. How do you implement database indexing in Django models?

**A:**

```python
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)  # FK auto-indexed
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        indexes = [
            models.Index(fields=["status", "created_at"]),          # composite
            models.Index(fields=["-created_at"], name="order_date_desc"),  # DESC
            models.Index(fields=["user", "status"]),                 # filter common queries
        ]
        constraints = [
            models.UniqueConstraint(fields=["user", "reference"], name="unique_user_ref"),
            models.CheckConstraint(check=Q(total__gte=0), name="order_total_positive"),
        ]
```

For Postgres-specific indexes, use `django.contrib.postgres`:
```python
from django.contrib.postgres.indexes import GinIndex, BrinIndex

indexes = [GinIndex(fields=["search_vector"])]  # full-text search
```

---

### 34. How do you implement full-text search in Django?

**A:**

```python
# PostgreSQL full-text search (django.contrib.postgres)
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

# Simple search
Article.objects.annotate(
    search=SearchVector("title", "body")
).filter(search="django")

# Ranked search
vector = SearchVector("title", weight="A") + SearchVector("body", weight="B")
query = SearchQuery("django ORM")
Article.objects.annotate(
    rank=SearchRank(vector, query)
).filter(rank__gte=0.1).order_by("-rank")

# Stored search vector (performant — index the vector)
class Article(models.Model):
    search_vector = SearchVectorField(null=True)

    class Meta:
        indexes = [GinIndex(fields=["search_vector"])]

# Update vector on save via trigger or signal
```

---

### 35. What is Django's `Prefetch` object and when do you need it over `prefetch_related`?

**A:** `Prefetch` gives you control over the prefetch queryset — filtering, ordering, or annotating the related objects:

```python
from django.db.models import Prefetch

# Only prefetch active comments, ordered by date
posts = Post.objects.prefetch_related(
    Prefetch(
        "comments",
        queryset=Comment.objects.filter(is_approved=True).order_by("-created_at"),
        to_attr="approved_comments"  # stored as list, not manager
    )
)

for post in posts:
    print(post.approved_comments)  # list, no extra query
```

---

### 36. How do you handle file uploads in Django?

**A:**

```python
class Document(models.Model):
    file = models.FileField(upload_to="documents/%Y/%m/")
    image = models.ImageField(upload_to="images/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

# In view
def upload(request):
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

# Validate file type and size
class DocumentForm(forms.ModelForm):
    def clean_file(self):
        file = self.cleaned_data["file"]
        if file.size > 10 * 1024 * 1024:  # 10MB
            raise forms.ValidationError("File too large.")
        if not file.name.endswith((".pdf", ".docx")):
            raise forms.ValidationError("Only PDF and DOCX allowed.")
        return file
```

In production, serve files from S3/GCS with `django-storages`:
```python
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
```

---

### 37. How do you implement row-level permissions in Django?

**A:** Using DRF's `has_object_permission`:

```python
class IsOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        return obj.owner == request.user

# Django guardian — per-object permissions backed by DB
from guardian.shortcuts import assign_perm, get_objects_for_user

assign_perm("change_order", user, order)  # grant permission on specific object
get_objects_for_user(user, "change_order", Order)  # all orders user can change
```

---

### 38. What are Django's `abstract`, `proxy`, and `multi-table inheritance` models?

**A:**

```python
# Abstract — shared fields, no DB table created
class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Post(TimestampedModel):
    title = models.CharField(max_length=200)
    # Gets created_at and updated_at, only one table: myapp_post

# Proxy — same DB table, different Python behavior
class ActivePost(Post):
    objects = ActiveManager()

    class Meta:
        proxy = True
        ordering = ["-created_at"]

# Multi-table inheritance — separate tables, joined automatically
class Place(models.Model):
    name = models.CharField(max_length=100)

class Restaurant(Place):
    cuisine = models.CharField(max_length=50)
    # Two tables: place + restaurant, linked by PK
    # Expensive — requires JOIN; prefer composition over multi-table inheritance
```

---

### 39. How do you optimize Django for high-traffic?

**A:**

**Database:**
- `select_related` / `prefetch_related` — eliminate N+1
- `only("id", "name")` / `defer("bio")` — select only needed columns
- `values()` / `values_list()` — skip ORM object overhead
- `iterator(chunk_size=1000)` — stream large querysets
- `bulk_create()`, `bulk_update()` — batch writes
- Add missing indexes — check `EXPLAIN ANALYZE` in Postgres

```python
# Only fetch needed columns
User.objects.only("id", "email", "name")

# Skip model instantiation — returns dicts
User.objects.values("id", "email")

# Stream large results
for user in User.objects.all().iterator(chunk_size=2000):
    process(user)
```

**Caching:** Redis for querysets, template fragments, computed values.

**Serving:** Gunicorn + multiple workers; Nginx for static/media files; CDN for public assets.

---

### 40. How do you implement async views in Django?

**A:** Django 3.1+ supports async views (ASGI only):

```python
import asyncio
import httpx
from django.http import JsonResponse

# Async view — doesn't block the worker during I/O
async def dashboard(request):
    async with httpx.AsyncClient() as client:
        # Run both requests concurrently
        user_resp, stats_resp = await asyncio.gather(
            client.get("http://user-service/me"),
            client.get("http://stats-service/summary"),
        )
    return JsonResponse({
        "user": user_resp.json(),
        "stats": stats_resp.json(),
    })

# Async ORM (Django 4.1+)
async def user_list(request):
    users = [u async for u in User.objects.filter(is_active=True)]
    return JsonResponse({"users": [u.name for u in users]})
```

Run with Uvicorn: `uvicorn myproject.asgi:application`

---

## 🏛️ Architect Level

---

### 41. How do you design a multi-tenant Django application?

**A:**

**Row-level isolation (simplest):**
```python
class TenantManager(models.Manager):
    def get_queryset(self):
        from threading import local
        _thread_locals = local()
        tenant_id = getattr(_thread_locals, "tenant_id", None)
        if tenant_id:
            return super().get_queryset().filter(tenant_id=tenant_id)
        return super().get_queryset()

class TenantMiddleware:
    def __call__(self, request):
        subdomain = request.get_host().split(".")[0]
        try:
            tenant = Tenant.objects.get(subdomain=subdomain)
            request.tenant = tenant
            set_current_tenant(tenant.id)
        except Tenant.DoesNotExist:
            return HttpResponse("Tenant not found", status=404)
        return self.get_response(request)
```

**Schema isolation (Postgres):**
- Use `django-tenants` — one schema per tenant, automatic schema switching
- Strong isolation; harder to query across tenants

**Database isolation:** Separate DB per tenant — maximum isolation, much higher operational cost.

---

### 42. How do you design a Django service for zero-downtime deployments?

**A:**

**Migration strategy (expand-contract):**
1. **Expand:** Add new column (nullable) → deploy
2. **Migrate:** Backfill data
3. **Contract:** Make non-nullable, remove old column in later deploy

```python
# Step 1: Add nullable (deploy with old code — backward compatible)
migrations.AddField(model_name="user", name="email_verified",
                    field=models.BooleanField(null=True))

# Step 2: Backfill (RunPython migration)
def backfill(apps, schema_editor):
    User = apps.get_model("auth", "User")
    User.objects.filter(email_verified__isnull=True).update(email_verified=False)

# Step 3 (next deploy): Make required
migrations.AlterField(model_name="user", name="email_verified",
                      field=models.BooleanField(default=False))
```

**Kubernetes strategy:**
- `initContainer` runs `manage.py migrate` before pod starts
- Readiness probe `/readyz` blocks traffic until migration complete
- `RollingUpdate` with `maxUnavailable: 0`

---

### 43. How do you handle distributed caching and cache invalidation in Django?

**A:**

```python
# Cache versioning — bump version to invalidate all keys
cache.set("user:42", data, version=2)
cache.get("user:42", version=2)
cache.incr_version("user:42")  # old version keys become stale

# Cache tags (django-cache-maint or custom)
# Tag all caches for user 42
def cache_get(key, tags=None):
    if tags:
        for tag in tags:
            v = cache.get(f"tag:{tag}")
            if v is None: return None  # tag invalidated
    return cache.get(key)

# Invalidate all caches for a model on save
from django.db.models.signals import post_save

@receiver(post_save, sender=Product)
def invalidate_product_cache(sender, instance, **kwargs):
    cache.delete_many([
        f"product:{instance.id}",
        f"product_list",
        f"category:{instance.category_id}",
    ])

# Django cache framework cache_page + Vary headers
@cache_page(300)
@vary_on_cookie  # different cache per user
def my_view(request): ...
```

---

### 44. How do you implement event-driven architecture with Django and Celery?

**A:**

```python
# Domain events via Celery
from celery import shared_task

class Order(models.Model):
    def complete(self):
        self.status = "completed"
        self.save()
        # Publish domain events after commit
        transaction.on_commit(lambda: order_completed.delay(self.id))

@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def order_completed(self, order_id: int):
    try:
        order = Order.objects.get(id=order_id)
        # Fan out to multiple consumers
        send_confirmation_email.delay(order_id)
        update_inventory.delay(order_id)
        notify_warehouse.delay(order_id)
    except Exception as exc:
        raise self.retry(exc=exc)

# Periodic tasks (Celery Beat)
from celery.schedules import crontab

app.conf.beat_schedule = {
    "cleanup-expired-sessions": {
        "task": "myapp.tasks.cleanup_sessions",
        "schedule": crontab(hour=3, minute=0),  # 3 AM daily
    },
}
```

---

### 45. How do you design Django for a microservices decomposition?

**A:**

**Decomposition strategy:**
1. **Identify bounded contexts** — Auth, Orders, Inventory, Notifications
2. **Shared kernel** — `django-shared-models` or duplicate lightweight models
3. **API contracts** — DRF serializers define the interface; version them

**Inter-service communication:**
```python
# Synchronous: DRF → external service via httpx
import httpx

class OrderService:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url="http://inventory-service", timeout=5.0)

    async def reserve_stock(self, product_id: int, qty: int) -> bool:
        resp = await self.client.post("/reserve", json={"product_id": product_id, "qty": qty})
        return resp.status_code == 200

# Asynchronous: publish events to Kafka/RabbitMQ
from confluent_kafka import Producer

producer = Producer({"bootstrap.servers": "kafka:9092"})

def publish_event(topic: str, event: dict):
    producer.produce(topic, value=json.dumps(event).encode())
    producer.flush()
```

**Strangler Fig:** Route traffic to new service via Nginx; Django monolith still handles unextracted paths.
