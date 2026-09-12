# 🌿 Celery — Interview Questions (Junior → Architect)

Covers Celery task queues, beat scheduler, monitoring, and production patterns in Python.

---

## 🟢 Junior Level

---

### 1. What is Celery and what problem does it solve?

**A:** Celery is a distributed task queue for Python — it lets you run code asynchronously in background worker processes.

**Why you need it:**
- Web request handlers should return in < 200ms
- Some work takes seconds/minutes (emails, PDF generation, ML inference, data import)
- Some work should be scheduled (nightly reports, cache warming)
- Some work should be retried on failure (payment processing, webhook delivery)

```
[Web Request] → [Django/FastAPI] → [Enqueue task] → [Redis/RabbitMQ broker]
                                                           ↓
[Browser gets immediate response]              [Celery worker processes task]
```

---

### 2. How do you set up Celery with Django?

**A:**

```python
# celery.py (next to settings.py)
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")

app = Celery("myproject")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()  # finds tasks.py in all INSTALLED_APPS

# settings.py
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/1"
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 300  # 5 minutes hard limit
CELERY_TASK_SOFT_TIME_LIMIT = 240  # 4 minutes soft limit (raises SoftTimeLimitExceeded)

# myapp/tasks.py
from celery import shared_task

@shared_task
def send_welcome_email(user_id: int):
    from myapp.models import User  # import inside to avoid circular imports
    user = User.objects.get(id=user_id)
    send_email(user.email, "Welcome!", "...")

# Enqueue from view
send_welcome_email.delay(user.id)         # async
send_welcome_email.apply_async(args=[user.id], countdown=60)  # delayed by 60s
```

---

### 3. How do you run Celery workers?

**A:**

```bash
# Start a worker
celery -A myproject worker --loglevel=info

# With concurrency (default = CPU cores)
celery -A myproject worker --concurrency=4 --loglevel=info

# With specific queues
celery -A myproject worker --queues=critical,default --loglevel=info

# Prefetch — how many tasks to fetch at once
celery -A myproject worker --prefetch-multiplier=1  # one at a time (fair)

# Celery Beat — scheduler
celery -A myproject beat --loglevel=info

# Both in one process (dev only — not for production)
celery -A myproject worker --beat --loglevel=info
```

---

### 4. How do you configure task retries?

**A:**

```python
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError

@shared_task(
    bind=True,           # gives access to self (the task instance)
    max_retries=5,
    default_retry_delay=60,  # 60 seconds between retries
)
def send_webhook(self, url: str, payload: dict):
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)  # exponential backoff
        # retry delays: 1s, 2s, 4s, 8s, 16s

@shared_task(
    bind=True,
    autoretry_for=(ConnectionError, TimeoutError),  # auto-retry these exceptions
    retry_backoff=True,       # exponential backoff
    retry_backoff_max=600,    # cap at 10 minutes
    retry_jitter=True,        # add randomness to avoid thundering herd
    max_retries=10,
)
def call_external_api(self, data: dict):
    return api_client.post(data)
```

---

### 5. What are Celery task states?

**A:**

```python
# States: PENDING → STARTED → SUCCESS / FAILURE / RETRY / REVOKED

result = send_welcome_email.delay(user_id=42)

result.id         # task UUID
result.state      # "PENDING", "STARTED", "SUCCESS", etc.
result.ready()    # True if done (SUCCESS or FAILURE)
result.successful() # True if SUCCESS
result.failed()   # True if FAILURE

# Wait for result (blocks — avoid in web requests)
value = result.get(timeout=10)

# Check without blocking
if result.ready():
    print(result.result)
else:
    print("still running")

# Custom states
@shared_task(bind=True)
def long_task(self, total: int):
    for i in range(total):
        self.update_state(state="PROGRESS", meta={"current": i, "total": total})
        do_work(i)
    return {"status": "done", "processed": total}
```

---

## 🟡 Mid Level

---

### 6. How do you route tasks to specific queues?

**A:**

```python
# settings.py — define queues with priority
CELERY_TASK_QUEUES = {
    "critical": {"exchange": "critical", "routing_key": "critical"},
    "default":  {"exchange": "default",  "routing_key": "default"},
    "low":      {"exchange": "low",      "routing_key": "low"},
}
CELERY_TASK_DEFAULT_QUEUE = "default"

# Route specific tasks
CELERY_TASK_ROUTES = {
    "myapp.tasks.process_payment": {"queue": "critical"},
    "myapp.tasks.send_email":      {"queue": "default"},
    "myapp.tasks.generate_report": {"queue": "low"},
    "myapp.tasks.*":               {"queue": "default"},  # catch-all
}

# Per-task routing
@shared_task(queue="critical")
def process_payment(order_id: int): ...

# Send to specific queue at call time
send_email.apply_async(args=[user_id], queue="low")

# Workers per queue
# celery -A myapp worker --queues=critical --concurrency=8   # dedicated high-priority
# celery -A myapp worker --queues=default  --concurrency=4
# celery -A myapp worker --queues=low      --concurrency=2
```

---

### 7. How do you schedule periodic tasks with Celery Beat?

**A:**

```python
# settings.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "cleanup-expired-sessions": {
        "task": "myapp.tasks.cleanup_sessions",
        "schedule": crontab(hour=3, minute=0),      # 3 AM daily
    },
    "send-daily-digest": {
        "task": "myapp.tasks.send_digest",
        "schedule": crontab(hour=8, minute=0, day_of_week="1-5"),  # weekdays 8 AM
    },
    "refresh-product-cache": {
        "task": "myapp.tasks.refresh_cache",
        "schedule": 300.0,   # every 5 minutes
    },
    "monthly-report": {
        "task": "myapp.tasks.generate_monthly_report",
        "schedule": crontab(day_of_month=1, hour=6, minute=0),  # 1st of month at 6 AM
        "args": ("full",),
    },
}

# django-celery-beat — store schedules in DB (dynamic, no redeploy needed)
# pip install django-celery-beat
INSTALLED_APPS += ["django_celery_beat"]
# celery -A myapp beat --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

---

### 8. How do you handle task failures and dead letters?

**A:**

```python
# Task-level error handling
@shared_task(bind=True, max_retries=3)
def process_order(self, order_id: int):
    try:
        order = Order.objects.get(id=order_id)
        payment_gateway.charge(order)
    except Order.DoesNotExist:
        # Don't retry — data issue
        logger.error("Order %d not found", order_id)
        return  # task completes without error
    except PaymentGatewayError as exc:
        # Retry — transient failure
        raise self.retry(exc=exc, countdown=60)
    except Exception as exc:
        # Log unexpected errors, don't retry
        logger.exception("Unexpected error processing order %d", order_id)
        raise  # marks task as FAILURE

# Global error handler
@app.task(bind=True)
def on_task_failure(self, exc, task_id, args, kwargs, einfo):
    logger.critical("Task %s failed: %s", task_id, exc)
    alert_ops_team(task_id, exc)

# Failure signal
from celery.signals import task_failure

@task_failure.connect
def handle_task_failure(task_id, exception, args, kwargs, traceback, einfo, **kw):
    # Send to Sentry, PagerDuty, etc.
    sentry_sdk.capture_exception(exception)
```

---

### 9. How do you chain and group tasks?

**A:**

```python
from celery import chain, group, chord

# chain — sequential (output of one → input of next)
result = chain(
    fetch_data.s(url),
    process_data.s(),      # receives fetch_data's result
    store_results.s(),
).apply_async()

# group — parallel execution
result = group(
    send_email.s(user_id) for user_id in user_ids
).apply_async()

# Wait for all
results = result.get()  # list of results

# chord — parallel then callback when all done
result = chord(
    group(process_item.s(item) for item in items),
    aggregate_results.s()  # called with list of all results
).apply_async()

# Immutable signature — don't pass previous result
chain(
    notify_admin.si("Deployment started"),  # .si() = immutable
    deploy_code.s(version),
    notify_admin.si("Deployment done"),
)
```

---

### 10. How do you implement idempotent tasks?

**A:**

```python
@shared_task(bind=True, max_retries=5)
def process_payment(self, order_id: int, idempotency_key: str):
    # Check if already processed
    if PaymentRecord.objects.filter(idempotency_key=idempotency_key).exists():
        logger.info("Payment %s already processed, skipping", idempotency_key)
        return {"status": "already_processed"}

    with transaction.atomic():
        order = Order.objects.select_for_update().get(id=order_id)
        if order.status == "paid":
            return {"status": "already_paid"}

        result = payment_gateway.charge(order.total, idempotency_key=idempotency_key)

        order.status = "paid"
        order.save()

        PaymentRecord.objects.create(
            order=order,
            idempotency_key=idempotency_key,
            transaction_id=result.transaction_id
        )

    return {"status": "success", "transaction_id": result.transaction_id}

# Always generate idempotency key at enqueue time
key = f"payment-{order.id}-{order.version}"
process_payment.delay(order.id, key)
```

---

## 🔴 Senior Level

---

### 11. How do you monitor Celery in production?

**A:**

```python
# Flower — real-time monitoring web UI
# pip install flower
# celery -A myapp flower --port=5555
# Exposes: active tasks, worker stats, task history, queues

# Celery events — programmatic monitoring
from celery.events import EventReceiver

def monitor():
    with app.connection() as connection:
        recv = EventReceiver(connection, handlers={
            "task-sent":    on_task_sent,
            "task-started": on_task_started,
            "task-failed":  on_task_failed,
            "task-succeeded": on_task_succeeded,
        })
        recv.capture(limit=None, timeout=None)

# Prometheus metrics via celery-prometheus-exporter
# or instrument signals yourself:
from celery.signals import task_prerun, task_postrun, task_failure

TASK_DURATION = Histogram("celery_task_duration_seconds", "Task duration", ["task_name"])
TASK_FAILURES = Counter("celery_task_failures_total", "Task failures", ["task_name"])

@task_prerun.connect
def task_started(task_id, task, args, kwargs, **kw):
    task._start_time = time.monotonic()

@task_postrun.connect
def task_finished(task_id, task, args, kwargs, retval, state, **kw):
    duration = time.monotonic() - getattr(task, "_start_time", time.monotonic())
    TASK_DURATION.labels(task_name=task.name).observe(duration)

@task_failure.connect
def task_failed(task_id, exception, **kw):
    TASK_FAILURES.labels(task_name=task.name).inc()
```

---

### 12. How do you implement the transactional outbox with Celery?

**A:**

```python
# Problem: enqueue task THEN commit DB — task may run before DB commit
# Or: commit DB THEN enqueue — DB commit succeeds but broker write fails

# Solution 1: transaction.on_commit (Django)
from django.db import transaction

def create_order(data: dict) -> Order:
    with transaction.atomic():
        order = Order.objects.create(**data)
        # task only enqueued AFTER transaction commits
        transaction.on_commit(lambda: send_confirmation.delay(order.id))
    return order

# Solution 2: Outbox table — true exactly-once
class OutboxMessage(models.Model):
    task_name = models.CharField(max_length=255)
    task_args = models.JSONField()
    task_kwargs = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True)

def create_order_with_outbox(data):
    with transaction.atomic():
        order = Order.objects.create(**data)
        OutboxMessage.objects.create(
            task_name="myapp.tasks.send_confirmation",
            task_args=[order.id],
        )
    return order

# Background worker sends outbox messages
@shared_task
def process_outbox():
    pending = OutboxMessage.objects.filter(sent_at__isnull=True).select_for_update(skip_locked=True)[:50]
    for msg in pending:
        app.send_task(msg.task_name, args=msg.task_args, kwargs=msg.task_kwargs)
        msg.sent_at = timezone.now()
        msg.save()
```

---

## 🏛️ Architect Level

---

### 13. How do you design Celery for high availability and scale?

**A:**

**Broker HA:**
```python
# Redis Sentinel
CELERY_BROKER_URL = "sentinel://sentinel1:26379;sentinel2:26379;sentinel3:26379/mymaster/0"

# RabbitMQ cluster
CELERY_BROKER_URL = "amqp://user:pass@rabbit1:5672,rabbit2:5672,rabbit3:5672/myvhost"
```

**Worker scaling:**
```yaml
# Kubernetes HPA based on queue depth
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: celery-worker
spec:
  scaleTargetRef:
    name: celery-worker-deployment
  minReplicaCount: 2
  maxReplicaCount: 50
  triggers:
    - type: redis
      metadata:
        address: redis:6379
        listName: celery
        listLength: "10"  # scale up when queue > 10 items
```

**Worker configuration for scale:**
```python
# Prefetch — critical for fairness with long tasks
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # fetch one at a time
CELERY_TASK_ACKS_LATE = True           # ack after completion (safer)
CELERY_TASK_REJECT_ON_WORKER_LOST = True  # requeue on worker crash
```

---

### 14. When should you use Celery vs alternatives?

**A:**

| Tool | Best for | Limitations |
|------|----------|-------------|
| **Celery** | Complex workflows, chains, chords, scheduling, multiple brokers | Heavy, complex config |
| **Huey** | Simpler tasks, Redis only, small teams | Less features |
| **Dramatiq** | Simpler API, better defaults (acks_late by default) | Smaller ecosystem |
| **arq** | Async-native (asyncio), Redis only | Less mature |
| **Asynq** (Go) | Not Python, but comparison point | — |
| **Django-Q** | Django-only, simple setup, ORM-backed | Less powerful |
| **FastAPI + BackgroundTasks** | Very simple, in-process | No retry, no persistence |

**Choose Celery when:**
- You need: scheduled tasks + retries + monitoring + complex workflows
- Multiple worker types with different queues
- Team already knows Celery

**Avoid Celery when:**
- Tasks are simple and rare — `BackgroundTasks` or `asyncio.create_task` suffice
- Team finds the operational complexity (broker, workers, beat) too heavy for the problem
