# Chapter 13 — File/Image Uploads

> *"Django makes file uploads straightforward locally, but production requires cloud storage like Amazon S3 via django-storages."*

---

## 🎯 Core Concept

Handling **media files** (user-uploaded images, documents) requires separate configuration from static files. In development, Django serves them locally. In production, you **must** use cloud storage (S3, GCS, Azure Blob).

---

## 📁 Media vs Static Files

```
Static Files:                       Media Files:
────────────────────────────────────────────────────
Part of your codebase               User-uploaded content
CSS, JS, images                     Profile photos, book covers
STATIC_URL = "/static/"             MEDIA_URL = "/media/"
STATIC_ROOT = staticfiles/          MEDIA_ROOT = media/
Served by web server                Must be cloud storage in prod
```

---

## ⚙️ Media File Configuration

```python
# settings.py
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

```python
# django_project/urls.py
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    ...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# ↑ Only active when DEBUG=True — serves media files in development
```

> ⚠️ **Production warning:** `static()` only works with `DEBUG=True`. In production, use S3 or similar.

---

## 📷 ImageField in Models

```python
# books/models.py
class Book(models.Model):
    ...
    cover = models.ImageField(
        upload_to="covers/",   # Files stored in media/covers/
        blank=True,            # Optional — don't require image
    )
```

```bash
# ImageField requires Pillow
$ pip install Pillow~=9.0

# Add to requirements.txt
```

---

## 📤 Handling File Uploads in Forms

For model forms to handle file uploads, two things are needed:

1. **Form attribute** `enctype="multipart/form-data"` in HTML
2. **Pass `request.FILES`** to the form in the view

```html
<!-- In your template (critical!) -->
<form method="post" enctype="multipart/form-data">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">Upload</button>
</form>
```

```python
# In views.py
def book_create(request):
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)  # Don't forget FILES!
        if form.is_valid():
            form.save()
```

---

## ☁️ Production: django-storages + Amazon S3

```
# requirements.txt
django-storages~=1.12
boto3~=1.24        # AWS SDK for Python
```

```python
# settings.py (production only)
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"
```

With this configuration, when a user uploads an image:
```
User uploads file → Django → boto3 → S3 bucket
File URL: https://mybucket.s3.amazonaws.com/covers/harry_potter.jpg
```

---

## 🗂️ File Organization

```
media/             ← MEDIA_ROOT (local dev)
└── covers/        ← upload_to="covers/"
    ├── harry_potter.jpg
    └── lord_of_rings.png

# In production (S3):
# s3://mybucket/covers/harry_potter.jpg
```

---

## 🧪 Testing File Uploads

```python
# books/tests.py
from django.core.files.uploadedfile import SimpleUploadedFile

class BookTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.book = Book.objects.create(
            title="Harry Potter",
            author="JK Rowling",
            price="25.00",
            cover=SimpleUploadedFile(
                name="test_cover.jpg",
                content=b"",  # Minimal content
                content_type="image/jpeg"
            )
        )

    def test_book_has_cover(self):
        self.assertNotEqual(self.book.cover, "")
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **MEDIA_URL / MEDIA_ROOT** | Separate from static files — user-uploaded content |
| **enctype="multipart/form-data"** | Required for any form with file upload |
| **request.FILES** | File data is separate from request.POST |
| **Pillow** | Required for ImageField — always add to requirements |
| **django-storages + boto3** | Production file storage on AWS S3 |
| **blank=True on ImageField** | Makes image optional in forms |

---

*← [Back to Django for Professionals](../README.md)*
