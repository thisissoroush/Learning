# 🐇 RabbitMQ — Interview Questions

---

### 1. What is RabbitMQ and what messaging model does it use?

**A:** RabbitMQ is an open-source message broker implementing the AMQP 0-9-1 protocol. It uses a **broker model** where producers publish messages to exchanges, which route them to queues, from which consumers read.

```
Producer → Exchange → Binding → Queue → Consumer
```

Key concepts:
- **Producer** — application that sends messages
- **Exchange** — receives messages from producers and routes to queues
- **Queue** — buffer that stores messages
- **Binding** — rule linking an exchange to a queue (with optional routing key)
- **Consumer** — application that receives messages from a queue
- **Virtual Host (vhost)** — logical isolation (like namespaces)

---

### 2. What are the four exchange types?

**A:**

```
Direct Exchange — routes by exact routing key match
Producer → Exchange (routing_key="order.created") → Queue "order-created"

Fanout Exchange — broadcasts to ALL bound queues (ignores routing key)
Producer → Fanout Exchange → Queue A
                           → Queue B
                           → Queue C

Topic Exchange — routes by routing key pattern (* = one word, # = zero or more)
routing_key="order.created.eu"  → matches "order.*.eu", "order.#", "*.created.*"

Headers Exchange — routes by message header attributes (rarely used)
```

```python
# Python (pika)
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()

# Direct exchange
channel.exchange_declare(exchange="orders", exchange_type="direct", durable=True)
channel.queue_declare(queue="order-created", durable=True)
channel.queue_bind(queue="order-created", exchange="orders", routing_key="order.created")

channel.basic_publish(
    exchange="orders",
    routing_key="order.created",
    body=json.dumps({"order_id": "123"}),
    properties=pika.BasicProperties(
        delivery_mode=pika.DeliveryMode.Persistent,  # survive broker restart
        content_type="application/json",
    )
)

# Fanout — all queues receive
channel.exchange_declare(exchange="notifications", exchange_type="fanout", durable=True)
channel.basic_publish(exchange="notifications", routing_key="", body=b"broadcast")

# Topic exchange
channel.exchange_declare(exchange="events", exchange_type="topic", durable=True)
channel.queue_bind(queue="eu-orders", exchange="events", routing_key="order.*.eu")
channel.queue_bind(queue="all-orders", exchange="events", routing_key="order.#")
```

---

### 3. What is message acknowledgment and why is it critical?

**A:** Acknowledgment tells RabbitMQ that a message was successfully processed and can be removed from the queue.

```python
# Auto-ack (dangerous — message lost if consumer crashes)
channel.basic_consume(queue="orders", on_message_callback=callback, auto_ack=True)

# Manual ack (safe — message re-queued on crash)
def callback(ch, method, properties, body):
    try:
        process_order(json.loads(body))
        ch.basic_ack(delivery_tag=method.delivery_tag)   # ✅ success
    except Exception as e:
        ch.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=True    # True = re-queue, False = discard/DLQ
        )

channel.basic_consume(queue="orders", on_message_callback=callback, auto_ack=False)

# basic_reject vs basic_nack:
# basic_reject — reject single message
# basic_nack   — reject one or multiple (multiple=True rejects all unacked)
ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)  # send to DLQ
```

Without acknowledgment, if a consumer crashes after receiving a message but before processing it, the message is **lost permanently**.

---

### 4. What is a Dead Letter Exchange (DLX)?

**A:** A DLX receives messages that are rejected, expired, or overflow a queue. Enables dead-letter queues for failed message handling:

```python
# Configure DLX on queue declaration
channel.queue_declare(
    queue="orders",
    durable=True,
    arguments={
        "x-dead-letter-exchange": "orders.dlx",
        "x-dead-letter-routing-key": "order.failed",
        "x-message-ttl": 30000,      # message expires after 30s → DLX
        "x-max-length": 10000,       # max 10k messages → overflow → DLX
    }
)

# Set up the DLX and dead letter queue
channel.exchange_declare(exchange="orders.dlx", exchange_type="direct", durable=True)
channel.queue_declare(queue="orders.failed", durable=True)
channel.queue_bind(queue="orders.failed", exchange="orders.dlx", routing_key="order.failed")

# Messages go to DLX when:
# 1. Consumer nacks with requeue=False
# 2. Message TTL expires
# 3. Queue length limit exceeded
```

---

### 5. What is prefetch count and why does it matter?

**A:** Prefetch count limits how many unacknowledged messages a consumer can hold at once. Critical for fairness and preventing consumer overload:

```python
# Without prefetch — consumer gets ALL messages, others starve
# With prefetch=1 — fair dispatch (slow consumers don't hoard)

channel.basic_qos(prefetch_count=1)   # process one at a time
channel.basic_qos(prefetch_count=10)  # batch of 10 (better throughput)

# Global prefetch (applies to connection, not just channel)
channel.basic_qos(prefetch_count=100, global_qos=True)
```

**prefetch_count=1** → Round-robin fairness (slow consumers get fewer messages)
**prefetch_count=0** → Unlimited (all messages sent to consumer immediately)
**prefetch_count=N** → Consumer gets N messages max before acking

---

### 6. What are quorum queues vs classic queues vs streams?

**A:**

| | Classic Queue | Quorum Queue | Stream |
|--|--------------|-------------|--------|
| Replication | Mirrored (deprecated) | Raft consensus | Append-only log |
| Durability | Optional | Always durable | Always durable |
| Message ordering | FIFO | FIFO | FIFO |
| Message replay | No | No | Yes |
| Use case | General, legacy | HA reliable | High-throughput, replay |
| Min nodes | 1 | 3 | 1 |

```python
# Quorum queue (recommended for HA)
channel.queue_declare(
    queue="orders",
    durable=True,
    arguments={"x-queue-type": "quorum"}
)

# Stream queue (Kafka-like replay)
channel.queue_declare(
    queue="events",
    durable=True,
    arguments={
        "x-queue-type": "stream",
        "x-max-length-bytes": 500_000_000,  # 500MB retention
        "x-stream-max-segment-size-bytes": 100_000_000,
    }
)
```

---

### 7. How does RabbitMQ clustering work?

**A:**

```bash
# RabbitMQ cluster — nodes share metadata (exchanges, queues, bindings)
# but queue contents are NOT replicated by default (classic queues)

# Join cluster
rabbitmqctl stop_app
rabbitmqctl join_cluster rabbit@node1
rabbitmqctl start_app

# Check cluster status
rabbitmqctl cluster_status

# Quorum queues — data IS replicated via Raft
# Requires quorum (majority) to commit: 3 nodes → tolerate 1 failure
# 5 nodes → tolerate 2 failures
```

```yaml
# Docker Compose cluster
services:
  rabbitmq1:
    image: rabbitmq:3.12-management
    hostname: rabbitmq1
    environment:
      RABBITMQ_ERLANG_COOKIE: "secret-cookie"   # must match across nodes
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: password

  rabbitmq2:
    image: rabbitmq:3.12-management
    hostname: rabbitmq2
    environment:
      RABBITMQ_ERLANG_COOKIE: "secret-cookie"
    depends_on:
      - rabbitmq1
```

---

### 8. What is the Shovel and Federation plugin?

**A:**

| | Shovel | Federation |
|--|--------|-----------|
| Purpose | Move messages between brokers | Sync exchanges/queues across brokers |
| Direction | One-way | Bi-directional possible |
| Use case | DR, bridge separate clusters | Multi-datacenter, geo-distribution |
| Scope | Queue level | Exchange or queue level |

```bash
# Enable plugins
rabbitmq-plugins enable rabbitmq_shovel rabbitmq_federation

# Configure shovel via CLI
rabbitmqctl set_parameter shovel my-shovel \
  '{"src-uri": "amqp://source:5672", "src-queue": "source-queue",
    "dest-uri": "amqp://dest:5672",   "dest-queue": "dest-queue"}'

# Federation — link exchanges across data centers
rabbitmqctl set_parameter federation-upstream us-east \
  '{"uri": "amqp://us-east.rabbit.company.com", "max-hops": 1}'
```

---

### 9. How do you implement retry logic with RabbitMQ?

**A:**

```python
# Pattern: DLX + TTL for retry with backoff

def setup_retry_topology(channel, queue_name: str, max_retries: int = 5):
    # Main queue → on failure → retry queue → after TTL → back to main
    retry_queue = f"{queue_name}.retry"
    failed_queue = f"{queue_name}.failed"

    # Main queue
    channel.queue_declare(
        queue=queue_name, durable=True,
        arguments={
            "x-dead-letter-exchange": "",   # default exchange
            "x-dead-letter-routing-key": retry_queue,
        }
    )

    # Retry queue (TTL sends back to main after delay)
    channel.queue_declare(
        queue=retry_queue, durable=True,
        arguments={
            "x-dead-letter-exchange": "",
            "x-dead-letter-routing-key": queue_name,
            "x-message-ttl": 30000,          # 30s retry delay
        }
    )

    # Failed queue (after max retries)
    channel.queue_declare(queue=failed_queue, durable=True)

def process_with_retry(ch, method, properties, body):
    headers = properties.headers or {}
    retry_count = headers.get("x-retry-count", 0)

    try:
        process_message(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        if retry_count >= 5:
            # Send to failed queue
            ch.basic_publish(exchange="", routing_key="orders.failed", body=body)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            # Send to retry queue with incremented counter
            ch.basic_publish(
                exchange="", routing_key="orders.retry",
                body=body,
                properties=pika.BasicProperties(
                    headers={"x-retry-count": retry_count + 1}
                )
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
```

---

### 10. How do you monitor RabbitMQ?

**A:**

```bash
# Management HTTP API
curl -u admin:password http://localhost:15672/api/overview
curl -u admin:password http://localhost:15672/api/queues
curl -u admin:password http://localhost:15672/api/queues/%2F/orders

# Key metrics to monitor:
# messages_ready        — queued, waiting to be consumed (alert if growing)
# messages_unacknowledged — being processed (alert if stuck high)
# consumers             — number of consumers (alert if 0)
# publish_rate          — messages/s published
# deliver_rate          — messages/s delivered
# memory                — broker memory (alert at 0.8 * vm_memory_high_watermark)
# disk_free             — alert when disk space low
```

```yaml
# Prometheus exporter
services:
  rabbitmq-exporter:
    image: kbudde/rabbitmq-exporter:latest
    environment:
      RABBIT_URL: http://rabbitmq:15672
      RABBIT_USER: admin
      RABBIT_PASSWORD: password

# Prometheus alert rules
- alert: RabbitMQQueueGrowing
  expr: rabbitmq_queue_messages_ready > 1000
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Queue {{ $labels.queue }} has {{ $value }} messages"

- alert: RabbitMQNoConsumers
  expr: rabbitmq_queue_consumers == 0 and rabbitmq_queue_messages_ready > 0
  for: 1m
  labels:
    severity: critical
```

---

### 11. What are common RabbitMQ performance patterns?

**A:**

```python
# 1. Publisher confirms — ensure messages reach the broker
channel.confirm_delivery()

def confirm_callback(frame):
    if frame.method.NAME == "Basic.Ack":
        print("Message confirmed")
    else:
        print("Message NACKed — resend")

channel.add_on_return_callback(confirm_callback)
channel.basic_publish(..., mandatory=True)  # Nack if no queue bound

# 2. Persistent messages + durable queues
properties = pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent)

# 3. Batch publishing
for msg in messages:
    channel.basic_publish(exchange="events", routing_key="", body=msg)
connection.process_data_events()  # flush

# 4. Connection pooling
import threading
_connection_pool = threading.local()

def get_channel():
    if not hasattr(_connection_pool, "channel"):
        conn = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
        _connection_pool.channel = conn.channel()
    return _connection_pool.channel

# 5. Consumer concurrency — multiple workers on same queue
# Run multiple consumer processes pointing at same queue
# RabbitMQ round-robins to them automatically

# 6. Lazy queues — store messages on disk (reduce RAM)
channel.queue_declare(
    queue="bulk-import",
    arguments={"x-queue-mode": "lazy"}
)
```

---

### 12. What is the difference between AMQP 0-9-1 and AMQP 1.0?

**A:**

| | AMQP 0-9-1 | AMQP 1.0 |
|--|-----------|---------|
| Model | Exchange → Queue → Consumer | Peer-to-peer links |
| Exchanges | Central routing component | Not defined |
| Queues | Explicit | Addressed nodes |
| RabbitMQ native | Yes | Plugin support |
| Azure Service Bus | No | Yes |
| ActiveMQ | No | Yes |
| Adoption | RabbitMQ ecosystem | Enterprise/cloud |

RabbitMQ natively implements AMQP 0-9-1. AMQP 1.0 is supported via plugin but with different semantics.

---

### 13. How do you secure RabbitMQ?

**A:**

```bash
# 1. Change default credentials immediately
rabbitmqctl add_user admin strongpassword
rabbitmqctl set_user_tags admin administrator
rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"
rabbitmqctl delete_user guest

# 2. TLS configuration
# In rabbitmq.conf:
listeners.ssl.default = 5671
ssl_options.cacertfile = /path/to/ca.crt
ssl_options.certfile   = /path/to/server.crt
ssl_options.keyfile    = /path/to/server.key
ssl_options.verify     = verify_peer
ssl_options.fail_if_no_peer_cert = false

# 3. vhost isolation
rabbitmqctl add_vhost production
rabbitmqctl add_vhost staging
rabbitmqctl set_permissions -p production app_user ".*" ".*" ".*"
# app_user can't see staging vhost at all

# 4. Least-privilege permissions per user
# Format: configure_regex publish_regex consume_regex
rabbitmqctl set_permissions -p / read_only_user "^$" "^$" ".*"  # consume only

# 5. Disable unused plugins
rabbitmq-plugins disable rabbitmq_mqtt rabbitmq_stomp
```

---

### 14. How does the competing consumers pattern work?

**A:**

```python
# Multiple consumers on the same queue — RabbitMQ round-robins messages
# Scale by adding more consumer processes/threads

# Worker 1
channel.basic_qos(prefetch_count=1)  # fair dispatch
channel.basic_consume(queue="tasks", on_message_callback=process_task)
channel.start_consuming()

# Worker 2 — same queue, same code, different process
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="tasks", on_message_callback=process_task)
channel.start_consuming()

# With prefetch=1: slow worker gets fewer messages, fast worker gets more
# Without prefetch: RabbitMQ sends N/workers to each equally (fast workers idle)
```

---

### 15. What is the Outbox Pattern with RabbitMQ?

**A:**

```python
# Problem: publish message AND save to DB atomically
# Solution: save to outbox table in same DB transaction, relay later

# Step 1: In application (Django + pika)
from django.db import transaction

def create_order(data: dict) -> Order:
    with transaction.atomic():
        order = Order.objects.create(**data)
        # Save event to outbox — same transaction
        OutboxMessage.objects.create(
            exchange="orders",
            routing_key="order.created",
            body=json.dumps({"order_id": str(order.id)}),
        )
    return order

# Step 2: Background relay process
def relay_outbox():
    while True:
        with transaction.atomic():
            messages = OutboxMessage.objects.select_for_update(skip_locked=True).filter(
                published_at__isnull=True
            )[:100]

            for msg in messages:
                channel.basic_publish(
                    exchange=msg.exchange,
                    routing_key=msg.routing_key,
                    body=msg.body.encode(),
                    properties=pika.BasicProperties(delivery_mode=2)
                )
                msg.published_at = timezone.now()
                msg.save()

        time.sleep(0.5)
```
