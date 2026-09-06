# Chapter 4 — Fundamentals of Django App Design

> *"Each app should be tightly focused on its own task. If an app seems too complex, it should be broken up into smaller apps."*

---

## 🎯 Core Concept

**The Golden Rule of Django App Design:** Each Django app should do **one thing and do it well**. Inspired by the Unix philosophy, this keeps apps reusable, testable, and understandable.

---

## 🔑 The Golden Rule

> *"Each app should be tightly-focused on its task. If you can't describe what an app does in a single sentence, it may need to be split up."*

```
✅ Good app names (focused):
  - flavors/      ← ice cream flavors
  - blog/         ← blog posts and comments
  - payments/     ← payment processing
  - accounts/     ← user accounts

❌ Bad app names (too broad):
  - utils/        ← What IS this?
  - stuff/        ← Meaningless
  - misc/         ← Everything that "doesn't fit elsewhere"
  - core/         ← Better as utils, but still vague
```

---

## 📛 Naming Your Apps

Best practices:
1. **Single word** when possible: `blog`, `flavors`, `payments`
2. **Plural** when the app manages a collection: `orders`, `stores`
3. **Valid Python identifier**: no dashes, no spaces
4. **Understandable to newcomers**: the name should communicate purpose

```
# Good names:
$ python manage.py startapp flavors
$ python manage.py startapp stores
$ python manage.py startapp orders

# Bad names:
$ python manage.py startapp ice_cream_stuff
$ python manage.py startapp ice-cream     ← Invalid! Can't be imported
$ python manage.py startapp utils         ← Too vague
```

---

## 📏 When to Break Up an App

Signs an app needs splitting:

```
❌ models.py is over 200 lines
❌ views.py handles 10+ unrelated view types
❌ App does two clearly different things (e.g., blog + payments)
❌ App name causes confusion ("what does core/ do?")
❌ You keep reaching across app boundaries for related logic

Rule of thumb: If you can't describe the app in one sentence,
               split it into two apps.
```

---

## 📁 What Modules Belong in an App?

### Common Modules (Almost Always Present)

```
myapp/
├── __init__.py
├── admin.py        ← Admin panel configuration
├── apps.py         ← App configuration class
├── forms.py        ← Form classes
├── managers.py     ← Custom model managers
├── migrations/     ← Database migrations
├── models.py       ← Data models
├── signals.py      ← Django signals
├── tests/          ← Test suite (or tests.py for small apps)
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   └── test_forms.py
├── urls.py         ← URL patterns
└── views.py        ← View functions/classes
```

### Uncommon But Useful Modules

```
myapp/
├── api/            ← REST API views (when using DRF)
├── context_processors.py  ← Template context processors
├── decorators.py   ← Custom decorators
├── exceptions.py   ← Custom exceptions
├── middleware.py   ← Custom middleware
├── serializers.py  ← DRF serializers
├── tasks.py        ← Celery async tasks
└── utils.py        ← Utility functions
```

---

## 🏗️ Alternative App Architectures

### Service Layers (Rails-style)

Some projects use a service layer pattern:

```
flavors/
├── models.py        ← Data layer (ORM models)
├── services.py      ← Business logic layer
│   └── FlavorsService.create_flavor()
│   └── FlavorsService.archive_flavor()
└── views.py         ← Presentation layer (calls services)
```

**Two Scoops opinion:** Service layers add useful separation but increase complexity. They're better for larger teams where multiple developers work on the same domain.

### The Large Single App

All code in one big app:

```
myproject/
└── myapp/
    ├── models/
    │   ├── users.py
    │   ├── orders.py
    │   └── products.py
    └── views/
        ├── users.py
        └── orders.py
```

**Two Scoops opinion:** Works for small projects; becomes unwieldy as projects grow. Better for teams starting with a monolith they may decompose later.

---

## 🧪 App Design in Practice

```
icecreamlandia project:

flavors/        ← Manages ice cream flavors (CRUD)
  models: Flavor, Topping
  views: FlavorListView, FlavorDetailView
  
stores/         ← Manages ice cream stores
  models: Store, StoreHours
  views: StoreMapView, StoreDetailView

orders/         ← Manages customer orders
  models: Order, OrderItem
  views: OrderCheckoutView, OrderHistoryView

reviews/        ← Manages customer reviews
  models: Review
  views: ReviewCreateView

accounts/       ← User accounts and auth
  models: CustomUser
  views: SignupView, ProfileView
```

Each app can be developed, tested, and even deployed independently.

---

## 💡 Key Takeaways

| Rule | Rationale |
|------|-----------|
| **One app = one task** | Small, focused apps are reusable and testable |
| **If in doubt, keep it small** | Easier to merge small apps than split big ones |
| **Name apps clearly** | The name should communicate what the app does |
| **Singular or plural** | Use `flavors` not `flavor` for collections |
| **tests/ over tests.py** | Once tests grow, split into multiple test files |

---

*← [Back to Two Scoops of Django](../README.md)*
