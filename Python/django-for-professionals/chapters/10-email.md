# Chapter 10 — Email

> *"Django takes care of the mechanics of email. You configure the settings, and it handles the rest."*

---

## 🎯 Core Concept

Professional Django applications send transactional emails: account confirmations, password resets, and notifications. Django's email framework makes this easy — the key is using an external **email service** (SendGrid, Mailgun, Amazon SES) in production instead of local SMTP.

---

## 📧 Email Backends

Django supports multiple email backends for different environments:

```python
# settings.py

# Development: print emails to console (no emails actually sent)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Development: save emails to files
EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = BASE_DIR / "sent_emails"

# Production: use real SMTP server
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_PORT = 587
EMAIL_HOST_USER = "apikey"
EMAIL_HOST_PASSWORD = env("SENDGRID_API_KEY")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = "noreply@yourdomain.com"
```

---

## 🔍 Seeing Emails in Development

```bash
# django-allauth sends a confirmation email on signup
# With console backend, it appears in docker-compose logs:
$ docker-compose logs

# You'll see something like:
# Content-Type: text/plain; charset="utf-8"
# Subject: [example.com] Please Confirm Your E-mail Address
# From: webmaster@localhost
# To: testuser3@email.com
#
# Hello from example.com!
# You're receiving this email because user testuser3 signed up...
# http://127.0.0.1:8000/accounts/confirm-email/abc123/
```

---

## 📨 Customizing allauth Email Templates

allauth's email templates live in `templates/account/email/`:

```
templates/
└── account/
    └── email/
        ├── email_confirmation_subject.txt     ← Subject line
        └── email_confirmation_message.txt     ← Email body
```

```
# templates/account/email/email_confirmation_subject.txt
Please Confirm Your Email Address for {{ site_name }}
```

```
# templates/account/email/email_confirmation_message.txt
Hello {{ user.username }},

Thank you for signing up at {{ site_name }}!

Please confirm your email address by clicking:
{{ activate_url }}

This link expires in {{ expiration_days }} days.

- The {{ site_name }} Team
```

---

## ✉️ Email Confirmation Flow

```
User signs up
      ↓
allauth creates account (inactive if ACCOUNT_EMAIL_VERIFICATION = "mandatory")
      ↓
Sends confirmation email → User inbox
      ↓
User clicks link → /accounts/confirm-email/<key>/
      ↓
Account activated → User can log in
```

---

## 🔐 Password Reset Flow

Django's built-in auth provides password reset:

```
User visits /accounts/password/reset/
      ↓
Enters email address → Submit
      ↓
If email exists: sends reset email with link
      ↓
User clicks link → /accounts/password/reset/confirm/<uidb64>/<token>/
      ↓
Sets new password
      ↓
Redirect to login
```

All this works out of the box with `django.contrib.auth.urls` — you just need email configured.

---

## 🌐 Production Email Services

```
SendGrid:
  EMAIL_HOST = "smtp.sendgrid.net"
  EMAIL_PORT = 587
  EMAIL_HOST_USER = "apikey"
  EMAIL_HOST_PASSWORD = env("SENDGRID_API_KEY")

Mailgun:
  EMAIL_HOST = "smtp.mailgun.org"
  EMAIL_PORT = 587
  EMAIL_HOST_USER = env("MAILGUN_USER")
  EMAIL_HOST_PASSWORD = env("MAILGUN_PASSWORD")

Amazon SES:
  Use django-ses package
```

---

## 🧪 Testing Email

```python
# In tests, Django automatically uses in-memory email backend
from django.core import mail
from django.test import TestCase


class EmailTest(TestCase):
    def test_send_email(self):
        mail.send_mail(
            "Subject here",
            "Here is the message.",
            "from@example.com",
            ["to@example.com"],
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Subject here")
```

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **Console backend for dev** | See emails in `docker-compose logs` without sending |
| **SMTP backend for prod** | Use SendGrid, Mailgun, or SES in production |
| **allauth handles registration emails** | Customize via templates, not code |
| **Password reset is free** | django.contrib.auth provides it, just configure email |
| **Environment variables for API keys** | Never hardcode email credentials |
| **Test with mail.outbox** | Django test framework captures sent emails |

---

*← [Back to Django for Professionals](../README.md)*
