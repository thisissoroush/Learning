# 📨 Apache Kafka — Interview Questions

---

### 1. What is Kafka and how does it differ from traditional message brokers?

**A:** Kafka is a distributed event streaming platform — a persistent, ordered, replayable log of events.

| | Kafka | Traditional Broker (RabbitMQ) |
|--|-------|------------------------------|
| Model | Distributed log | Message queue |
| Retention | Time/size based (default 7 days) | Until consumed |
| Replay | Yes — any consumer can re-read | No |
| Ordering | Per partition | Per queue |
| Routing | Consumer pulls by partition | Broker pushes to consumer |
| Throughput | Millions/s | Hundreds of thousands/s |
| Consumers | Any number reads same data | Message deleted after consume |
| Use case | Event streaming, audit log, CDC | Task queues, RPC, work queues |

---

### 2. What are topics, partitions, and offsets?

**A:**

```
Topic "orders" (3 partitions):

Partition 0: [msg0] [msg1] [msg3] [msg5]  ← offset: 0, 1, 2, 3
Partition 1: [msg0] [msg2] [msg4]          ← offset: 0, 1, 2
Partition 2: [msg0] [msg6]                 ← offset: 0, 1
```

- **Topic** — logical channel for a stream of related events
- **Partition** — ordered, immutable sequence of records; unit of parallelism
- **Offset** — position of a message within a partition (monotonically increasing)
- **Replication** — each partition has N replicas (leader + followers) across brokers

```bash
# Create topic
kafka-topics.sh --bootstrap-server kafka:9092 \
  --create --topic orders \
  --partitions 6 \
  --replication-factor 3

# Describe topic
kafka-topics.sh --bootstrap-server kafka:9092 --describe --topic orders

# List topics
kafka-topics.sh --bootstrap-server kafka:9092 --list

# Increase partitions (can only increase, never decrease)
kafka-topics.sh --bootstrap-server kafka:9092 \
  --alter --topic orders --partitions 12
```

---

### 3. How do producers work? What is the partitioning strategy?

**A:**

```python
from confluent_kafka import Producer

producer = Producer({
    "bootstrap.servers": "kafka1:9092,kafka2:9092,kafka3:9092",
    "acks": "all",                    # wait for all ISR replicas to ack
    "retries": 5,
    "retry.backoff.ms": 500,
    "linger.ms": 5,                   # batch for 5ms (higher throughput)
    "batch.size": 16384,              # batch up to 16KB
    "compression.type": "snappy",     # compress batches
    "enable.idempotence": True,       # exactly-once on producer side
})

def delivery_callback(err, msg):
    if err:
        print(f"Delivery failed: {err}")
    else:
        print(f"Delivered to {msg.topic()} [{msg.partition()}] @ {msg.offset()}")

# Partitioning strategies:
# 1. No key → round-robin (even load but no ordering guarantee)
producer.produce("orders", value=json.dumps(event).encode(), callback=delivery_callback)

# 2. Key → consistent hash → same key always goes to same partition (ordering per key)
producer.produce("orders",
    key=order_id.encode(),          # same customer → same partition → ordered
    value=json.dumps(event).encode(),
    callback=delivery_callback)

# 3. Custom partitioner
# 4. Sticky partitioner (default since 2.4 — batches to same partition until full)

producer.flush()  # wait for all outstanding messages to be delivered
```

---

### 4. How do consumer groups work?

**A:**

```
Topic "orders" (6 partitions) with Consumer Group "order-service":

Without consumer group (each consumer reads ALL partitions):
  Consumer A reads P0, P1, P2, P3, P4, P5

With consumer group "order-service" (2 consumers):
  Consumer A reads P0, P1, P2
  Consumer B reads P3, P4, P5

With consumer group "order-service" (6 consumers):
  Consumer A reads P0
  Consumer B reads P1
  Consumer C reads P2
  ...etc (1 partition per consumer)

With consumer group "order-service" (7 consumers):
  6 consume, 1 is idle (more consumers than partitions = waste)
```

```python
from confluent_kafka import Consumer, KafkaException

consumer = Consumer({
    "bootstrap.servers": "kafka:9092",
    "group.id": "order-service",
    "auto.offset.reset": "earliest",    # start from beginning if no committed offset
    # "auto.offset.reset": "latest",    # start from now
    "enable.auto.commit": False,        # manual commit for safety
    "max.poll.interval.ms": 300000,     # 5 min before rebalance
    "session.timeout.ms": 45000,
})

consumer.subscribe(["orders"])

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())

        process_event(msg.value())

        # Commit AFTER processing
        consumer.commit(asynchronous=False)

finally:
    consumer.close()
```

---

### 5. What is offset management? What is the difference between auto-commit and manual commit?

**A:**

```python
# Auto-commit (dangerous)
consumer = Consumer({
    "enable.auto.commit": True,
    "auto.commit.interval.ms": 5000,  # commits every 5s
})
# Problem: if consumer crashes after 3s, offset already committed → messages lost

# Manual commit (safe — commit after processing)
consumer = Consumer({"enable.auto.commit": False})

# Synchronous commit (slower but guaranteed)
consumer.commit(asynchronous=False)

# Asynchronous commit (faster, possible reprocessing on crash)
consumer.commit(asynchronous=True)

# Commit specific offsets
from confluent_kafka import TopicPartition
consumer.commit(offsets=[
    TopicPartition("orders", partition=0, offset=42 + 1)  # +1 = next offset to read
])

# Reset offset (reprocess from beginning)
# kafka-consumer-groups.sh --reset-offsets --to-earliest --group order-service --topic orders --execute

# Check consumer lag
# kafka-consumer-groups.sh --describe --group order-service --bootstrap-server kafka:9092
```

---

### 6. What is exactly-once delivery in Kafka?

**A:**

```
Delivery semantics:
- At-most-once: ack before process → message can be lost (auto-commit before processing)
- At-least-once: process then ack → message can be reprocessed (default with manual commit)
- Exactly-once: transactional → never lost, never duplicated
```

```python
# Exactly-once on producer side (idempotent producer)
producer = Producer({
    "enable.idempotence": True,      # adds sequence numbers to deduplicate
    "acks": "all",
    "max.in.flight.requests.per.connection": 5,  # required for idempotence
})

# Exactly-once: consume-process-produce (transactional)
producer = Producer({
    "transactional.id": "order-service-1",  # unique per producer instance
    "enable.idempotence": True,
})
producer.init_transactions()

try:
    producer.begin_transaction()

    # Read from input topic
    msg = consumer.poll(1.0)

    # Process and produce to output
    processed = transform(msg.value())
    producer.produce("processed-orders", value=processed)

    # Commit offsets within the transaction
    producer.send_offsets_to_transaction(
        consumer.position(consumer.assignment()),
        consumer.consumer_group_metadata()
    )

    producer.commit_transaction()  # atomic: produce + offset commit
except Exception:
    producer.abort_transaction()
```

---

### 7. What is log compaction?

**A:** Log compaction retains only the **latest value per key**, discarding older records. Creates an ever-updated snapshot:

```
Before compaction:
[key=user1, val={"name":"Alice"}]
[key=user2, val={"name":"Bob"}]
[key=user1, val={"name":"Alice Smith"}]  ← newer
[key=user3, val={"name":"Carol"}]
[key=user2, val=null]                    ← tombstone (delete)

After compaction:
[key=user1, val={"name":"Alice Smith"}]
[key=user3, val={"name":"Carol"}]
# user2 removed (tombstone + no newer value)
```

```bash
# Create compacted topic
kafka-topics.sh --create --topic users \
  --config cleanup.policy=compact \
  --config min.cleanable.dirty.ratio=0.1 \
  --config segment.ms=3600000

# Hybrid: retain for 7 days, then compact
--config "cleanup.policy=compact,delete"
--config retention.ms=604800000
```

---

### 8. What is Kafka Streams?

**A:** Kafka Streams is a library for building real-time stream processing applications that read from and write to Kafka:

```java
// Java example (Kafka Streams is Java-native)
StreamsBuilder builder = new StreamsBuilder();

KStream<String, Order> orders = builder.stream("orders");

// Filter + transform
KStream<String, ProcessedOrder> processed = orders
    .filter((key, order) -> order.getTotal() > 0)
    .mapValues(order -> new ProcessedOrder(order.getId(), order.getTotal() * 1.1));

processed.to("processed-orders");

// Aggregation with windowing
orders
    .groupByKey()
    .windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofMinutes(5)))
    .count()
    .toStream()
    .to("order-counts-per-5min");

// Join two streams
KStream<String, Payment> payments = builder.stream("payments");

orders.join(payments,
    (order, payment) -> new OrderWithPayment(order, payment),
    JoinWindows.ofTimeDifferenceWithNoGrace(Duration.ofSeconds(30)),
    StreamJoined.with(Serdes.String(), orderSerde, paymentSerde)
).to("orders-with-payments");

// Run
KafkaStreams streams = new KafkaStreams(builder.build(), config);
streams.start();
Runtime.getRuntime().addShutdownHook(new Thread(streams::close));
```

---

### 9. What is the Schema Registry?

**A:** Schema Registry stores and validates Avro/JSON/Protobuf schemas for Kafka messages, ensuring compatibility:

```python
from confluent_kafka.avro import AvroProducer
from confluent_kafka import avro

# Define schema
order_schema = avro.loads("""
{
  "type": "record",
  "name": "Order",
  "namespace": "com.myapp",
  "fields": [
    {"name": "order_id", "type": "string"},
    {"name": "customer_id", "type": "string"},
    {"name": "total", "type": "double"}
  ]
}
""")

producer = AvroProducer({
    "bootstrap.servers": "kafka:9092",
    "schema.registry.url": "http://schema-registry:8081",
}, default_value_schema=order_schema)

producer.produce(
    topic="orders",
    key="order-123",
    value={"order_id": "order-123", "customer_id": "cust-1", "total": 99.99}
)

# Schema compatibility modes:
# BACKWARD — new schema can read old data (add optional fields with defaults)
# FORWARD  — old schema can read new data
# FULL     — both BACKWARD and FULL
# NONE     — no compatibility check
```

---

### 10. What is Kafka Connect?

**A:** Kafka Connect is a framework for streaming data between Kafka and external systems (databases, file systems, search indexes, etc.):

```json
// Debezium PostgreSQL Source Connector — CDC (Change Data Capture)
// Streams DB changes (INSERT/UPDATE/DELETE) to Kafka topics
{
  "name": "postgres-source",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "debezium",
    "database.password": "secret",
    "database.dbname": "mydb",
    "database.server.name": "mydb",
    "table.include.list": "public.orders,public.users",
    "plugin.name": "pgoutput"
  }
}

// Elasticsearch Sink Connector — index Kafka events in ES
{
  "name": "elasticsearch-sink",
  "config": {
    "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
    "connection.url": "http://elasticsearch:9200",
    "topics": "orders",
    "key.ignore": "false",
    "schema.ignore": "true",
    "type.name": "_doc"
  }
}
```

```bash
# Deploy connector
curl -X POST http://connect:8083/connectors \
  -H "Content-Type: application/json" \
  -d @connector-config.json

# Check status
curl http://connect:8083/connectors/postgres-source/status
```

---

### 11. How do you monitor Kafka?

**A:**

```bash
# Consumer lag — most important metric
kafka-consumer-groups.sh \
  --bootstrap-server kafka:9092 \
  --describe --group order-service

# Output:
# GROUP         TOPIC   PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
# order-service orders  0          1000            1050            50
# order-service orders  1          2000            2000            0

# JMX metrics via Prometheus JMX Exporter
# Key JMX metrics:
# kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec
# kafka.server:type=BrokerTopicMetrics,name=BytesInPerSec
# kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions  ← 0 = healthy
# kafka.controller:type=KafkaController,name=ActiveControllerCount ← must be 1
# kafka.network:type=RequestMetrics,name=TotalTimeMs               ← latency
```

```yaml
# Kafka Exporter (Prometheus)
kafka_consumergroup_lag > 10000  # alert
kafka_controller_active_count != 1  # critical
kafka_topic_partition_under_replicated > 0  # alert
```

---

### 12. What is partition leadership and ISR?

**A:**

```
Topic "orders" partition 0:
  Broker 1: LEADER     ← all reads and writes go here
  Broker 2: Follower (ISR)  ← replicates from leader
  Broker 3: Follower (ISR)  ← replicates from leader

ISR (In-Sync Replicas) — replicas that are fully caught up with leader
  If follower falls behind by > replica.lag.time.max.ms → removed from ISR

acks=all → leader waits for ALL ISR to confirm before acking producer
acks=1   → leader acks immediately (data loss risk if leader fails)
acks=0   → no ack (fire and forget)

min.insync.replicas=2 — with acks=all, at least 2 replicas must be in ISR
```

```bash
# Check ISR health
kafka-topics.sh --describe --topic orders --bootstrap-server kafka:9092
# If ISR < replication factor → alert!

# Leader re-election after failure
kafka-leader-election.sh --bootstrap-server kafka:9092 \
  --election-type preferred --all-topic-partitions
```

---

### 13. What are common Kafka performance tuning configurations?

**A:**

```properties
# Producer — high throughput
linger.ms=20                     # wait up to 20ms to batch
batch.size=65536                 # 64KB batches
compression.type=lz4             # fast compression
max.in.flight.requests.per.connection=5
buffer.memory=33554432           # 32MB producer buffer

# Consumer — high throughput
fetch.min.bytes=1048576          # wait for 1MB before returning
fetch.max.wait.ms=500            # or up to 500ms
max.poll.records=500             # process 500 at a time
max.partition.fetch.bytes=1048576

# Broker — high throughput
num.network.threads=8
num.io.threads=16
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
log.flush.interval.messages=10000
log.flush.interval.ms=1000

# Retention
log.retention.hours=168          # 7 days
log.retention.bytes=107374182400 # 100GB per partition
log.segment.bytes=1073741824     # 1GB per segment
```

---

### 14. How do you handle schema evolution in Kafka?

**A:**

```
Backward compatible changes (safe — new consumer can read old messages):
  ✅ Add optional field with default value
  ✅ Remove field (old consumers ignore unknown fields)
  ❌ Rename field
  ❌ Change field type

Forward compatible changes (old consumer can read new messages):
  ✅ Add optional field with default value (old consumer ignores it)
  ❌ Remove required field
```

```python
# Avro schema evolution example
# V1 schema
v1 = """{"type":"record","name":"Order","fields":[
  {"name":"id","type":"string"},
  {"name":"total","type":"double"}
]}"""

# V2 schema (backward compatible — adds optional field with default)
v2 = """{"type":"record","name":"Order","fields":[
  {"name":"id","type":"string"},
  {"name":"total","type":"double"},
  {"name":"currency","type":"string","default":"USD"}  ← has default
]}"""

# Register schema (Schema Registry checks compatibility)
curl -X POST http://schema-registry:8081/subjects/orders-value/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"schema": "..."}'
```

---

### 15. How do you implement the Kafka Outbox pattern?

**A:**

```python
# Transactional Outbox — atomic DB write + event
from django.db import transaction, models

class OutboxEvent(models.Model):
    topic = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    value = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=False)

def create_order(data: dict) -> Order:
    with transaction.atomic():
        order = Order.objects.create(**data)
        OutboxEvent.objects.create(
            topic="orders",
            key=str(order.id),
            value={"event": "OrderCreated", "order_id": str(order.id)},
        )
    return order

# Relay task (runs periodically)
def relay_outbox_events():
    events = OutboxEvent.objects.select_for_update(skip_locked=True).filter(
        published=False
    ).order_by("created_at")[:100]

    for event in events:
        producer.produce(
            topic=event.topic,
            key=event.key.encode(),
            value=json.dumps(event.value).encode(),
        )

    producer.flush()

    for event in events:
        event.published = True
    OutboxEvent.objects.bulk_update(events, ["published"])
```

---

### 16. What is the difference between Kafka and Redis Streams?

**A:**

| | Kafka | Redis Streams |
|--|-------|--------------|
| Persistence | Disk (durable) | In-memory + optional AOF |
| Throughput | Very high (millions/s) | High (hundreds of thousands/s) |
| Replication | Built-in cluster | Redis Cluster |
| Consumer groups | Yes | Yes |
| Message replay | Yes (up to retention) | Yes (with persistence) |
| Schema registry | Confluent Schema Registry | None |
| Complexity | High | Low |
| Use case | Large-scale streaming | Lighter workloads, existing Redis |
| Retention | Time/size-based | Memory-limited |

---

### 17. How do you secure Kafka?

**A:**

```properties
# server.properties — enable TLS + SASL
listeners=SASL_SSL://0.0.0.0:9093
advertised.listeners=SASL_SSL://kafka1.example.com:9093

ssl.keystore.location=/var/ssl/kafka.server.keystore.jks
ssl.keystore.password=keystorepass
ssl.truststore.location=/var/ssl/kafka.server.truststore.jks
ssl.truststore.password=truststorepass

sasl.enabled.mechanisms=SCRAM-SHA-512
sasl.mechanism.inter.broker.protocol=SCRAM-SHA-512
security.inter.broker.protocol=SASL_SSL

# ACLs
allow.everyone.if.no.acl.found=false
authorizer.class.name=kafka.security.authorizer.AclAuthorizer
```

```bash
# Create user
kafka-configs.sh --bootstrap-server kafka:9093 \
  --alter --add-config "SCRAM-SHA-512=[iterations=8192,password=secret]" \
  --entity-type users --entity-name alice

# Grant access
kafka-acls.sh --bootstrap-server kafka:9093 \
  --add --allow-principal User:alice \
  --operation Read --operation Write \
  --topic orders --group order-service
```
