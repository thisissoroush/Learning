# 📬 Messaging in Go — Interview Questions (Junior → Architect)

Covers Kafka (franz-go / sarama), NATS, and Asynq (Redis-backed task queues).

---

## 🟢 Junior Level

---

### 1. What messaging systems are commonly used in Go and when do you choose each?

**A:**

| System | Type | Best for |
|--------|------|----------|
| **Kafka** | Distributed log | High-throughput event streaming, audit logs, replay |
| **NATS** | Lightweight pub/sub | Low-latency internal messaging, request/reply, IoT |
| **RabbitMQ** | Message broker | Task queues, routing, dead-letter, AMQP ecosystem |
| **Asynq** | Redis task queue | Background jobs, scheduled tasks, simpler than Kafka |
| **Redis Streams** | Persistent pub/sub | Lightweight Kafka alternative, smaller scale |

**Decision guide:**
- Need durability and replay → **Kafka**
- Need low latency, simple pub/sub → **NATS**
- Need task queues with retries, scheduling → **Asynq**
- Already have Redis → **Asynq or Redis Streams**

---

### 2. How do you produce messages to Kafka with `franz-go`?

**A:**

```go
import "github.com/twmb/franz-go/pkg/kgo"

client, err := kgo.NewClient(
    kgo.SeedBrokers("kafka:9092"),
    kgo.DefaultProduceTopic("orders"),
    kgo.ProducerBatchCompression(kgo.SnappyCompression()),
    kgo.RequiredAcks(kgo.AllISRAcks()), // strongest durability
)
if err != nil {
    log.Fatal(err)
}
defer client.Close()

// Produce synchronously
record := &kgo.Record{
    Topic: "orders",
    Key:   []byte("order-123"),      // same key → same partition (ordering)
    Value: []byte(`{"id":"order-123","status":"created"}`),
    Headers: []kgo.RecordHeader{
        {Key: "event-type", Value: []byte("OrderCreated")},
        {Key: "trace-id",   Value: []byte(traceID)},
    },
}

if err := client.ProduceSync(ctx, record).FirstErr(); err != nil {
    return fmt.Errorf("produce: %w", err)
}

// Produce async (higher throughput)
client.Produce(ctx, record, func(r *kgo.Record, err error) {
    if err != nil {
        log.Printf("produce error: %v", err)
    }
})
```

---

### 3. How do you consume messages from Kafka with `franz-go`?

**A:**

```go
client, err := kgo.NewClient(
    kgo.SeedBrokers("kafka:9092"),
    kgo.ConsumerGroup("order-service"),
    kgo.ConsumeTopics("orders"),
    kgo.ConsumeResetOffset(kgo.NewOffset().AtStart()), // or AtEnd()
)
if err != nil {
    log.Fatal(err)
}
defer client.Close()

// Poll loop
for {
    fetches := client.PollFetches(ctx)
    if fetches.IsClientClosed() {
        return
    }
    fetches.EachError(func(topic string, partition int32, err error) {
        log.Printf("fetch error topic=%s partition=%d: %v", topic, partition, err)
    })

    fetches.EachRecord(func(record *kgo.Record) {
        if err := processRecord(ctx, record); err != nil {
            log.Printf("processing error: %v", err)
            // decide: log and continue, or crash and let Kafka redeliver
        }
    })

    // Commit offsets after processing
    if err := client.CommitUncommittedOffsets(ctx); err != nil {
        log.Printf("commit error: %v", err)
    }
}
```

---

### 4. What is a Kafka consumer group and why does it matter?

**A:** A consumer group allows multiple consumers to share the work of consuming a topic:

```
Topic "orders" (4 partitions):
  Partition 0 → Consumer A (in group "order-service")
  Partition 1 → Consumer B
  Partition 2 → Consumer C
  Partition 3 → Consumer D
```

**Key properties:**
- Each partition is consumed by exactly **one** consumer in the group at a time
- Adding consumers scales consumption up to the number of partitions
- Kafka tracks each group's offset independently — different groups replay independently
- If a consumer dies, Kafka rebalances partitions to surviving consumers

```go
// Scale horizontally: run 4 instances of your service
// Each instance connects to the same consumer group
// Kafka distributes the 4 partitions across the 4 instances (1 each)
```

---

### 5. How do you use NATS for pub/sub?

**A:**

```go
import "github.com/nats-io/nats.go"

// Connect
nc, err := nats.Connect("nats://localhost:4222",
    nats.RetryOnFailedConnect(true),
    nats.MaxReconnects(-1), // infinite reconnects
    nats.ReconnectWait(2*time.Second),
)
if err != nil {
    log.Fatal(err)
}
defer nc.Close()

// Publish
err = nc.Publish("orders.created", []byte(`{"id":"order-1"}`))

// Subscribe (async)
sub, err := nc.Subscribe("orders.*", func(msg *nats.Msg) {
    fmt.Printf("Received on %s: %s\n", msg.Subject, string(msg.Data))
})
defer sub.Unsubscribe()

// Queue subscribe — like Kafka consumer group (one handler per message)
sub, err = nc.QueueSubscribe("orders.created", "order-processors", func(msg *nats.Msg) {
    processOrder(msg.Data) // only one subscriber in the group handles each message
})

// Request/Reply
resp, err := nc.Request("inventory.check", []byte(`{"sku":"ABC"}`), 5*time.Second)
fmt.Println("Response:", string(resp.Data))
```

---

### 6. How do you use Asynq for background tasks?

**A:**

```go
import "github.com/hibiken/asynq"

// Define task types
const TypeSendEmail = "email:send"

type SendEmailPayload struct {
    To      string
    Subject string
    Body    string
}

// Enqueue (producer side)
func EnqueueSendEmail(client *asynq.Client, to, subject, body string) error {
    payload, _ := json.Marshal(SendEmailPayload{To: to, Subject: subject, Body: body})
    task := asynq.NewTask(TypeSendEmail, payload,
        asynq.MaxRetry(5),
        asynq.Timeout(30*time.Second),
        asynq.Deadline(time.Now().Add(1*time.Hour)),
    )
    _, err := client.Enqueue(task)
    return err
}

// Enqueue with delay
client.Enqueue(task, asynq.ProcessIn(10*time.Minute))

// Enqueue with specific time
client.Enqueue(task, asynq.ProcessAt(time.Now().Add(24*time.Hour)))

// Worker (consumer side)
func handleSendEmail(ctx context.Context, t *asynq.Task) error {
    var p SendEmailPayload
    if err := json.Unmarshal(t.Payload(), &p); err != nil {
        return fmt.Errorf("unmarshal: %w", err)
    }
    return emailClient.Send(ctx, p.To, p.Subject, p.Body)
}

srv := asynq.NewServer(
    asynq.RedisClientOpt{Addr: "localhost:6379"},
    asynq.Config{
        Concurrency: 10,
        Queues: map[string]int{
            "critical": 6,
            "default":  3,
            "low":      1,
        },
    },
)

mux := asynq.NewServeMux()
mux.HandleFunc(TypeSendEmail, handleSendEmail)

srv.Run(mux)
```

---

## 🟡 Mid Level

---

### 7. How do you ensure exactly-once or at-least-once delivery in Kafka?

**A:**

**At-least-once (default):** Message may be redelivered. Make consumers idempotent.

```go
// Commit offsets AFTER processing (not before)
fetches.EachRecord(func(r *kgo.Record) {
    if err := process(ctx, r); err != nil {
        log.Fatal(err) // crash → Kafka redelivers from last commit
    }
})
client.CommitUncommittedOffsets(ctx) // commit after successful processing
```

**Idempotent producer (exactly-once on produce side):**
```go
client, _ := kgo.NewClient(
    kgo.SeedBrokers("kafka:9092"),
    kgo.ProducerIdempotent(), // Kafka deduplicates retried messages
)
```

**Transactional exactly-once (consume-transform-produce):**
```go
client, _ := kgo.NewClient(
    kgo.TransactionalID("my-service-1"),
)
client.BeginTransaction()
// produce to output topic
// commit transaction — atomically commits offsets + output messages
client.EndTransaction(ctx, kgo.TryCommit)
```

**Consumer idempotency — inbox pattern:**
```go
func process(ctx context.Context, r *kgo.Record) error {
    offsetKey := fmt.Sprintf("%s:%d:%d", r.Topic, r.Partition, r.Offset)
    if alreadyProcessed(offsetKey) { return nil }
    // do work
    markProcessed(offsetKey)
    return nil
}
```

---

### 8. How do you handle consumer rebalancing in Kafka?

**A:** During a rebalance (consumer joins/leaves group), Kafka pauses consumption and redistributes partitions. franz-go handles this via hooks:

```go
client, _ := kgo.NewClient(
    kgo.SeedBrokers("kafka:9092"),
    kgo.ConsumerGroup("my-group"),
    kgo.OnPartitionsAssigned(func(ctx context.Context, c *kgo.Client, assigned map[string][]int32) {
        log.Printf("Partitions assigned: %v", assigned)
        // Initialize per-partition state
    }),
    kgo.OnPartitionsRevoked(func(ctx context.Context, c *kgo.Client, revoked map[string][]int32) {
        log.Printf("Partitions revoked: %v", revoked)
        // Flush in-flight work for revoked partitions
        // Commit offsets before they're reassigned
        c.CommitUncommittedOffsets(ctx)
    }),
    kgo.OnPartitionsLost(func(ctx context.Context, c *kgo.Client, lost map[string][]int32) {
        // Lost without clean revoke (crash/timeout) — don't commit
        log.Printf("Partitions lost: %v", lost)
    }),
)
```

---

### 9. How do you use JetStream with NATS for persistence?

**A:** NATS core is fire-and-forget. JetStream adds persistence, acknowledgements, and replay:

```go
import "github.com/nats-io/nats.go/jetstream"

nc, _ := nats.Connect("nats://localhost:4222")
js, _ := jetstream.New(nc)

// Create a stream (persists messages)
stream, _ := js.CreateOrUpdateStream(ctx, jetstream.StreamConfig{
    Name:      "ORDERS",
    Subjects:  []string{"orders.>"},
    Retention: jetstream.LimitsPolicy,
    MaxAge:    7 * 24 * time.Hour,
    Storage:   jetstream.FileStorage,
    Replicas:  3, // cluster replicas
})

// Publish with acknowledgement
ack, err := js.Publish(ctx, "orders.created", []byte(`{"id":"order-1"}`))
if err != nil {
    log.Fatal("publish failed:", err)
}
log.Println("sequence:", ack.Sequence) // server assigned sequence number

// Durable consumer
consumer, _ := stream.CreateOrUpdateConsumer(ctx, jetstream.ConsumerConfig{
    Name:          "order-processor",
    Durable:       "order-processor",
    AckPolicy:     jetstream.AckExplicitPolicy,
    MaxAckPending: 100,
    FilterSubject: "orders.created",
})

// Consume
cc, _ := consumer.Consume(func(msg jetstream.Msg) {
    if err := processOrder(msg.Data()); err != nil {
        msg.Nak() // redeliver
        return
    }
    msg.Ack() // remove from pending
})
defer cc.Stop()
```

---

### 10. How do you implement dead letter queues (DLQ)?

**A:**

**Kafka — manual DLQ:**
```go
const maxRetries = 3

func processWithDLQ(ctx context.Context, r *kgo.Record, producer *kgo.Client) {
    var retries int
    var err error

    for retries < maxRetries {
        err = processRecord(ctx, r)
        if err == nil {
            return
        }
        retries++
        time.Sleep(time.Duration(retries) * time.Second) // backoff
    }

    // Send to DLQ topic after all retries exhausted
    dlqRecord := &kgo.Record{
        Topic: r.Topic + ".dlq",
        Key:   r.Key,
        Value: r.Value,
        Headers: append(r.Headers,
            kgo.RecordHeader{Key: "error", Value: []byte(err.Error())},
            kgo.RecordHeader{Key: "retries", Value: []byte(strconv.Itoa(retries))},
        ),
    }
    producer.ProduceSync(ctx, dlqRecord)
}
```

**Asynq — built-in dead queue:**
```go
// Tasks that exhaust retries go to "archived" queue automatically
// Inspect via asynq CLI or web UI
// asynq dash

// Re-enqueue from archive
inspector := asynq.NewInspector(asynq.RedisClientOpt{Addr: "localhost:6379"})
inspector.RunAllArchivedTasks("default") // re-run all archived
```

---

### 11. How do you implement rate-limited message processing?

**A:**

```go
import "golang.org/x/time/rate"

// Process at most 100 messages per second
limiter := rate.NewLimiter(rate.Limit(100), 10) // 100/s, burst 10

for {
    fetches := client.PollFetches(ctx)
    fetches.EachRecord(func(r *kgo.Record) {
        // Wait for rate limiter before processing
        if err := limiter.Wait(ctx); err != nil {
            return
        }
        processRecord(ctx, r)
    })
}

// Worker pool pattern — bounded concurrency
sem := make(chan struct{}, 20) // max 20 concurrent workers

fetches.EachRecord(func(r *kgo.Record) {
    sem <- struct{}{}
    go func(rec *kgo.Record) {
        defer func() { <-sem }()
        processRecord(ctx, rec)
    }(r)
})
```

---

## 🔴 Senior Level

---

### 12. How do you implement the outbox pattern with Kafka in Go?

**A:**

```go
// 1. Write business data + outbox record in one DB transaction
func (s *OrderService) CreateOrder(ctx context.Context, cmd CreateOrderCmd) (*Order, error) {
    tx, err := s.db.BeginTx(ctx, nil)
    if err != nil { return nil, err }
    defer tx.Rollback()

    order := &Order{ID: uuid.New().String(), CustomerID: cmd.CustomerID}

    _, err = tx.ExecContext(ctx,
        "INSERT INTO orders (id, customer_id) VALUES ($1, $2)", order.ID, order.CustomerID)
    if err != nil { return nil, err }

    payload, _ := json.Marshal(OrderCreatedEvent{OrderID: order.ID})
    _, err = tx.ExecContext(ctx,
        "INSERT INTO outbox (topic, key, payload) VALUES ($1, $2, $3)",
        "orders", order.ID, payload)
    if err != nil { return nil, err }

    return order, tx.Commit()
}

// 2. Outbox relay — polls and publishes
func (r *OutboxRelay) Run(ctx context.Context) {
    for {
        select {
        case <-ctx.Done():
            return
        case <-time.After(500 * time.Millisecond):
            r.publishBatch(ctx)
        }
    }
}

func (r *OutboxRelay) publishBatch(ctx context.Context) {
    rows, _ := r.db.QueryContext(ctx,
        "SELECT id, topic, key, payload FROM outbox WHERE published = false ORDER BY id LIMIT 100 FOR UPDATE SKIP LOCKED")
    defer rows.Close()

    var records []*kgo.Record
    var ids []int64
    for rows.Next() {
        var id int64; var topic, key, payload string
        rows.Scan(&id, &topic, &key, &payload)
        records = append(records, &kgo.Record{Topic: topic, Key: []byte(key), Value: []byte(payload)})
        ids = append(ids, id)
    }

    if len(records) == 0 { return }

    if err := r.producer.ProduceSync(ctx, records...).FirstErr(); err != nil {
        log.Printf("publish failed: %v", err)
        return
    }

    r.db.ExecContext(ctx, "UPDATE outbox SET published = true WHERE id = ANY($1)", pq.Array(ids))
}
```

---

### 13. How do you design a Kafka consumer for high throughput?

**A:**

```go
// Parallel processing with per-partition goroutines (preserves ordering)
func consume(ctx context.Context, client *kgo.Client) {
    // Use a channel per partition to preserve order within partition
    partitionWorkers := make(map[int32]chan *kgo.Record)
    var mu sync.Mutex

    getOrCreateWorker := func(partition int32) chan *kgo.Record {
        mu.Lock()
        defer mu.Unlock()
        if ch, ok := partitionWorkers[partition]; ok {
            return ch
        }
        ch := make(chan *kgo.Record, 100)
        partitionWorkers[partition] = ch
        go func() {
            for record := range ch {
                if err := processRecord(ctx, record); err != nil {
                    log.Printf("error: %v", err)
                }
            }
        }()
        return ch
    }

    for {
        fetches := client.PollFetches(ctx)
        fetches.EachRecord(func(r *kgo.Record) {
            getOrCreateWorker(r.Partition) <- r
        })
        client.CommitUncommittedOffsets(ctx)
    }
}
```

**Throughput levers:**
- `kgo.FetchMaxBytes` — fetch larger batches
- `kgo.FetchMaxWait` — wait longer per fetch (batching)
- Per-partition goroutines — parallel without losing order
- Async commits — don't block on commit
- Larger consumer group — more partitions processed in parallel

---

## 🏛️ Architect Level

---

### 14. How do you design an event-driven architecture in Go?

**A:**

**Event types:**
```go
// Domain events — things that happened
type OrderCreated struct {
    OrderID    string    `json:"order_id"`
    CustomerID string    `json:"customer_id"`
    Total      float64   `json:"total"`
    OccurredAt time.Time `json:"occurred_at"`
    Version    int       `json:"version"` // schema version
}

// Commands — things to do (sent to specific service)
type ProcessPayment struct {
    OrderID string  `json:"order_id"`
    Amount  float64 `json:"amount"`
}
```

**Topic design:**
```
orders          — order domain events (all order events in one topic, keyed by order ID)
payments        — payment domain events
inventory       — inventory events
notifications   — outbound notification commands

# OR: one topic per event type (simpler routing, more topics)
orders.created
orders.cancelled
orders.shipped
```

**Schema registry:** Use Confluent Schema Registry or Buf Schema Registry — enforce backward compatibility, prevent breaking changes.

**Event versioning:**
```go
type EventEnvelope struct {
    Topic     string          `json:"topic"`
    EventType string          `json:"event_type"`
    Version   int             `json:"version"`
    Payload   json.RawMessage `json:"payload"`
}

// Consumer upcasts old versions to current
func upcast(e EventEnvelope) (OrderCreated, error) {
    switch e.Version {
    case 1:
        var v1 OrderCreatedV1
        json.Unmarshal(e.Payload, &v1)
        return OrderCreated{OrderID: v1.ID, CustomerID: v1.Customer}, nil // migrate
    case 2:
        var v2 OrderCreated
        json.Unmarshal(e.Payload, &v2)
        return v2, nil
    default:
        return OrderCreated{}, fmt.Errorf("unknown version %d", e.Version)
    }
}
```

---

### 15. How do you monitor and operate a Kafka-based system in production?

**A:**

**Key metrics:**
```
consumer_lag              — messages behind (most important: alert if growing)
produce_rate              — messages/second produced
consume_rate              — messages/second consumed
fetch_latency_p99         — time to fetch a batch
commit_latency_p99        — time to commit offsets
```

**Consumer lag monitoring:**
```go
// franz-go lag hook
client, _ := kgo.NewClient(
    kgo.WithHooks(&kgo.HookFetchRecordBuffered{}),
)

// Or use external tool
// kafka-consumer-groups --bootstrap-server kafka:9092 --describe --group order-service

// Prometheus exporter
// kafka_burrow_topic_partition_offset_lag — standard alert metric
```

**Alerting rules:**
- Consumer lag > 1000 AND not decreasing for 5m → page on-call
- Producer error rate > 0.1% → alert
- Under-replicated partitions > 0 → critical (broker issue)
- Offline partitions > 0 → critical

**Operational runbook items:**
- DLQ depth grows → investigate processing errors, replay after fix
- Rebalancing storm → check consumer heartbeat timeout, reduce session.timeout.ms
- Offset reset needed → `kafka-consumer-groups --reset-offsets --to-earliest --execute`
