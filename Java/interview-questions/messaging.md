# ☁️ Java Messaging & Kafka Interview Questions

> Covers Spring Kafka, RabbitMQ, JMS/ActiveMQ, Kafka Streams, event-driven patterns, and distributed messaging architecture.

---

## 🟢 Junior

---

### 1. What is Apache Kafka and what problem does it solve?

**A:** Kafka is a distributed, fault-tolerant, high-throughput event streaming platform. It decouples producers from consumers, enables async communication, replay of events, and horizontal scaling. Core concepts:

- **Topic** – a named log of records
- **Partition** – ordered, immutable sequence within a topic (unit of parallelism)
- **Broker** – a Kafka server
- **Producer** – writes records to topics
- **Consumer** – reads records from topics
- **Consumer Group** – a group of consumers that share partition assignments (each partition read by exactly one consumer in the group)
- **Offset** – an integer that uniquely identifies each record in a partition; consumers track their position via offsets

```
Topic: orders (3 partitions)
┌──────────────┬──────────────┬──────────────┐
│ Partition 0  │ Partition 1  │ Partition 2  │
│ [0][1][2][3] │ [0][1][2]    │ [0][1][2][3] │
└──────────────┴──────────────┴──────────────┘
     ↑                ↑               ↑
  Consumer A       Consumer B      Consumer C
  (Group: orders-svc)
```

---

### 2. How do you set up Spring Kafka in a Spring Boot application?

**A:** Add the dependency, configure bootstrap servers, and enable Kafka:

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.kafka</groupId>
    <artifactId>spring-kafka</artifactId>
</dependency>
```

```yaml
# application.yml
spring:
  kafka:
    bootstrap-servers: localhost:9092
    consumer:
      group-id: my-consumer-group
      auto-offset-reset: earliest
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.apache.kafka.common.serialization.StringDeserializer
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.apache.kafka.common.serialization.StringSerializer
```

```java
@SpringBootApplication
@EnableKafka  // enables @KafkaListener detection; auto-applied in Boot, explicit with custom configs
public class App { public static void main(String[] args) { SpringApplication.run(App.class, args); } }
```

---

### 3. How do you produce messages with `KafkaTemplate`?

**A:** `KafkaTemplate` is the primary Spring abstraction for sending to Kafka:

```java
@Service
@RequiredArgsConstructor
public class OrderProducer {

    private final KafkaTemplate<String, String> kafkaTemplate;

    // Fire-and-forget
    public void send(String orderId, String payload) {
        kafkaTemplate.send("orders", orderId, payload);
    }

    // With callback
    public void sendWithCallback(String orderId, String payload) {
        kafkaTemplate.send("orders", orderId, payload)
            .whenComplete((result, ex) -> {
                if (ex != null) {
                    log.error("Failed to send order {}", orderId, ex);
                } else {
                    RecordMetadata meta = result.getRecordMetadata();
                    log.info("Sent to partition {} offset {}", meta.partition(), meta.offset());
                }
            });
    }

    // Sending a ProducerRecord for full control
    public void sendWithHeaders(String orderId, String payload) {
        ProducerRecord<String, String> record = new ProducerRecord<>("orders", orderId, payload);
        record.headers().add("source", "order-svc".getBytes());
        kafkaTemplate.send(record);
    }
}
```

---

### 4. How does `@KafkaListener` work?

**A:** `@KafkaListener` marks a method as a Kafka consumer. Spring creates a `MessageListenerContainer` per listener:

```java
@Component
public class OrderConsumer {

    // Basic listener
    @KafkaListener(topics = "orders", groupId = "order-processor")
    public void handleOrder(String payload) {
        System.out.println("Received: " + payload);
    }

    // With ConsumerRecord for metadata access
    @KafkaListener(topics = "orders", groupId = "order-processor")
    public void handleWithMetadata(ConsumerRecord<String, String> record) {
        log.info("topic={}, partition={}, offset={}, key={}, value={}",
            record.topic(), record.partition(), record.offset(),
            record.key(), record.value());
    }

    // Listening to multiple topics
    @KafkaListener(topics = {"orders", "payments"}, groupId = "audit-group")
    public void auditEvents(String message) { }

    // With explicit container factory
    @KafkaListener(
        topics = "orders",
        groupId = "order-processor",
        containerFactory = "orderKafkaListenerContainerFactory"
    )
    public void handleWithFactory(String payload) { }
}
```

---

### 5. What is a Consumer Group and why is it important?

**A:** A consumer group is a set of consumers that cooperate to consume a topic. Each partition is assigned to exactly one consumer in the group at a time, enabling parallel processing. Multiple groups can consume the same topic independently (pub/sub pattern).

```
Topic: orders (4 partitions P0–P3)

Group: order-processor (2 consumers)       Group: audit-service (1 consumer)
├── Consumer A: [P0, P1]                   └── Consumer X: [P0, P1, P2, P3]
└── Consumer B: [P2, P3]

Adding Consumer C to order-processor triggers rebalance:
├── Consumer A: [P0]
├── Consumer B: [P1, P2]
└── Consumer C: [P3]
```

```java
// Same topic, two independent groups
@KafkaListener(topics = "orders", groupId = "order-processor")
public void process(String order) { /* fulfillment logic */ }

@KafkaListener(topics = "orders", groupId = "audit-service")
public void audit(String order) { /* audit logic */ }
```

---

### 6. What is `auto-offset-reset` and when does it matter?

**A:** `auto-offset-reset` determines where to start reading when no committed offset exists (new group, or topic reset):

| Value | Behavior |
|-------|----------|
| `earliest` | Start from the very first message in the partition |
| `latest` (default) | Start from new messages arriving after consumer starts |
| `none` | Throw an exception if no offset is found |

```yaml
spring:
  kafka:
    consumer:
      auto-offset-reset: earliest   # good for new services catching up
```

```java
// Programmatic override per listener
@KafkaListener(
    topics = "orders",
    groupId = "new-group",
    properties = {"auto.offset.reset=earliest"}
)
public void handle(String msg) { }
```

---

### 7. What is RabbitMQ and how does it differ from Kafka?

**A:** RabbitMQ is a traditional message broker implementing AMQP. Key differences:

| Feature | Kafka | RabbitMQ |
|---------|-------|----------|
| Model | Log-based, pull | Queue-based, push |
| Message retention | Configurable (days/forever) | Deleted on ack |
| Ordering | Per-partition | Per-queue |
| Replay | Yes (rewind offsets) | No (once consumed, gone) |
| Throughput | Very high (millions/sec) | High (tens of thousands/sec) |
| Routing | Topic + partition key | Exchange routing (fanout, direct, topic, headers) |
| Use case | Event streaming, audit log, replay | Task queues, RPC, flexible routing |

```java
// Spring RabbitMQ basics
@Component
public class OrderListener {

    @RabbitListener(queues = "orders.queue")
    public void handleOrder(String message) {
        System.out.println("Got: " + message);
    }
}

@Service
@RequiredArgsConstructor
public class OrderSender {

    private final RabbitTemplate rabbitTemplate;

    public void send(String message) {
        rabbitTemplate.convertAndSend("orders.exchange", "orders.routing.key", message);
    }
}
```

---

### 8. What are RabbitMQ Exchanges, Queues, and Bindings?

**A:** The RabbitMQ routing model:

- **Exchange** – receives messages from producers and routes them to queues
- **Queue** – stores messages; consumers subscribe to queues
- **Binding** – rule linking an exchange to a queue (with optional routing key)

Exchange types:

| Type | Routing Logic |
|------|---------------|
| `direct` | Exact match of routing key |
| `fanout` | Broadcast to all bound queues |
| `topic` | Pattern match (`*` = one word, `#` = zero or more) |
| `headers` | Match on message headers |

```java
@Configuration
public class RabbitConfig {

    @Bean
    public TopicExchange ordersExchange() {
        return new TopicExchange("orders.exchange");
    }

    @Bean
    public Queue ordersQueue() {
        return QueueBuilder.durable("orders.queue").build();
    }

    @Bean
    public Queue paymentsQueue() {
        return QueueBuilder.durable("payments.queue").build();
    }

    @Bean
    public Binding ordersBinding(TopicExchange ordersExchange, Queue ordersQueue) {
        return BindingBuilder.bind(ordersQueue)
                             .to(ordersExchange)
                             .with("orders.#");
    }

    @Bean
    public Binding paymentsBinding(TopicExchange ordersExchange, Queue paymentsQueue) {
        return BindingBuilder.bind(paymentsQueue)
                             .to(ordersExchange)
                             .with("payments.#");
    }
}
```

---

### 9. What is JMS and how do you use it with Spring?

**A:** JMS (Java Message Service) is the Java EE API for messaging. Spring provides `JmsTemplate` and `@JmsListener` over any JMS provider (ActiveMQ, IBM MQ, etc.):

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-activemq</artifactId>
</dependency>
```

```yaml
spring:
  activemq:
    broker-url: tcp://localhost:61616
    user: admin
    password: admin
```

```java
// Producer
@Service
@RequiredArgsConstructor
public class JmsOrderSender {

    private final JmsTemplate jmsTemplate;

    public void sendOrder(String order) {
        jmsTemplate.convertAndSend("orders.queue", order);
    }

    public void sendWithPriority(String order) {
        jmsTemplate.send("orders.queue", session -> {
            TextMessage msg = session.createTextMessage(order);
            msg.setJMSPriority(9);
            return msg;
        });
    }
}

// Consumer
@Component
public class JmsOrderConsumer {

    @JmsListener(destination = "orders.queue")
    public void receiveOrder(String order) {
        System.out.println("Processing: " + order);
    }

    @JmsListener(destination = "orders.queue", containerFactory = "jmsListenerContainerFactory")
    public void receiveMessage(Message message) throws JMSException {
        if (message instanceof TextMessage) {
            System.out.println(((TextMessage) message).getText());
        }
    }
}
```

---

### 10. What does `@EnableKafka` do and when do you need it explicitly?

**A:** `@EnableKafka` triggers Spring's `KafkaListenerAnnotationBeanPostProcessor`, which scans for `@KafkaListener` annotations and registers listener containers. In Spring Boot with `spring-kafka` on the classpath, `KafkaAutoConfiguration` applies it automatically. You need it explicitly when:

1. Using a non-Boot Spring application (`@Configuration` class)
2. Defining a custom `KafkaListenerContainerFactory` and want full control
3. Testing with `@SpringBootTest` but excluding auto-configuration

```java
@Configuration
@EnableKafka   // required in plain Spring (not Boot)
public class KafkaConfig {

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, String> kafkaListenerContainerFactory(
            ConsumerFactory<String, String> consumerFactory) {
        var factory = new ConcurrentKafkaListenerContainerFactory<String, String>();
        factory.setConsumerFactory(consumerFactory);
        return factory;
    }
}
```

---

## 🟡 Mid

---

### 11. What is the difference between at-least-once and exactly-once delivery?

**A:** These describe delivery semantics — how the system handles failures:

| Semantic | Description | Risk |
|----------|-------------|------|
| **At-most-once** | Ack before processing; message lost if crash | Data loss |
| **At-least-once** | Ack after processing; retry on failure | Duplicates |
| **Exactly-once** | Processed exactly once end-to-end | Complex, higher latency |

```java
// At-least-once (default Spring Kafka)
// Auto-commit is OFF; offset committed after successful processing
// On failure → message is re-delivered → duplicates possible

@KafkaListener(topics = "orders")
public void process(String order) {
    orderService.save(order);  // if crash here, message redelivered on restart
    // offset committed AFTER this returns successfully
}

// Making it idempotent (safe for at-least-once)
@KafkaListener(topics = "orders")
public void processIdempotent(ConsumerRecord<String, OrderEvent> record) {
    String eventId = record.key();
    if (!processedEvents.contains(eventId)) {
        orderService.save(record.value());
        processedEvents.add(eventId);  // dedupe store (Redis, DB unique constraint, etc.)
    }
}
```

```yaml
# Disable auto-commit for at-least-once
spring:
  kafka:
    consumer:
      enable-auto-commit: false
    listener:
      ack-mode: record   # commit after each record
```

---

### 12. What is an Idempotent Producer in Kafka?

**A:** With retries enabled, network timeouts can cause the producer to re-send a record already written by the broker, resulting in duplicates. The idempotent producer assigns a **Producer ID (PID)** and a **sequence number** to each record. The broker deduplicates based on `(PID, partition, sequence)`:

```java
@Configuration
public class IdempotentProducerConfig {

    @Bean
    public ProducerFactory<String, String> producerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class);

        // Enable idempotence
        props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);

        // These are auto-set when idempotence is enabled, but explicit for clarity:
        props.put(ProducerConfig.ACKS_CONFIG, "all");          // wait for all replicas
        props.put(ProducerConfig.RETRIES_CONFIG, Integer.MAX_VALUE);
        props.put(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION, 5);

        return new DefaultKafkaProducerFactory<>(props);
    }

    @Bean
    public KafkaTemplate<String, String> kafkaTemplate(ProducerFactory<String, String> pf) {
        return new KafkaTemplate<>(pf);
    }
}
```

> Idempotent producer only guarantees no duplicates **within a single producer session**. For cross-session or multi-topic guarantees, use **transactional producer**.

---

### 13. How does a Transactional Producer work in Spring Kafka?

**A:** A transactional producer wraps multiple sends (and optionally consumer offset commits) in an atomic transaction. Either all writes land or none do:

```java
@Configuration
public class TransactionalKafkaConfig {

    @Bean
    public ProducerFactory<String, String> producerFactory() {
        Map<String, Object> props = Map.of(
            ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092",
            ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class,
            ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class
        );
        var factory = new DefaultKafkaProducerFactory<String, String>(props);
        factory.setTransactionIdPrefix("order-tx-");  // enables transactions
        return factory;
    }

    @Bean
    public KafkaTemplate<String, String> kafkaTemplate(ProducerFactory<String, String> pf) {
        return new KafkaTemplate<>(pf);
    }
}
```

```java
@Service
@RequiredArgsConstructor
public class TransactionalOrderService {

    private final KafkaTemplate<String, String> kafkaTemplate;

    @Transactional   // Spring @Transactional wraps Kafka transaction
    public void processOrderAtomically(String orderId) {
        kafkaTemplate.send("orders", orderId, "ORDER_CREATED");
        kafkaTemplate.send("inventory", orderId, "RESERVE_STOCK");
        kafkaTemplate.send("payments", orderId, "CHARGE_CUSTOMER");
        // All three sent atomically; if any fails, broker rolls back all
    }

    // Explicit executeInTransaction
    public void processManual(String orderId) {
        kafkaTemplate.executeInTransaction(ops -> {
            ops.send("orders", orderId, "ORDER_CREATED");
            ops.send("audit", orderId, "AUDIT_EVENT");
            return true;
        });
    }
}
```

```yaml
# Consumers must be configured to only read committed messages
spring:
  kafka:
    consumer:
      isolation-level: read_committed  # skip uncommitted/aborted messages
```

---

### 14. How does offset management work in Spring Kafka?

**A:** Offsets track how far each consumer group has read in each partition. They're stored in the internal Kafka topic `__consumer_offsets`.

```yaml
# AckMode controls WHEN offsets are committed
spring:
  kafka:
    listener:
      ack-mode: RECORD        # after each record (safest, lowest throughput)
      # ack-mode: BATCH       # after each poll batch
      # ack-mode: TIME        # every N milliseconds
      # ack-mode: COUNT       # after N records
      # ack-mode: COUNT_TIME  # whichever comes first
      # ack-mode: MANUAL      # listener calls Acknowledgment.acknowledge()
      # ack-mode: MANUAL_IMMEDIATE  # commits immediately (not buffered)
```

```java
// Manual acknowledgement — maximum control
@KafkaListener(topics = "orders", containerFactory = "manualAckFactory")
public void handleWithManualAck(
        ConsumerRecord<String, String> record,
        Acknowledgment ack) {
    try {
        orderService.process(record.value());
        ack.acknowledge();   // commit offset only on success
    } catch (RecoverableException e) {
        // do NOT ack — message will be redelivered
        log.error("Temporary failure, will retry", e);
    }
}

@Bean
public ConcurrentKafkaListenerContainerFactory<String, String> manualAckFactory(
        ConsumerFactory<String, String> cf) {
    var factory = new ConcurrentKafkaListenerContainerFactory<String, String>();
    factory.setConsumerFactory(cf);
    factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.MANUAL);
    return factory;
}
```

---

### 15. How do you configure a `ConcurrentKafkaListenerContainerFactory`?

**A:** This factory creates `ConcurrentMessageListenerContainer` instances, each with multiple consumer threads:

```java
@Configuration
@EnableKafka
public class KafkaContainerFactoryConfig {

    @Bean
    public ConsumerFactory<String, OrderEvent> consumerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "order-group");
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, JsonDeserializer.class);
        props.put(JsonDeserializer.TRUSTED_PACKAGES, "com.example.events");
        return new DefaultKafkaConsumerFactory<>(props,
                new StringDeserializer(),
                new JsonDeserializer<>(OrderEvent.class));
    }

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, OrderEvent> orderContainerFactory(
            ConsumerFactory<String, OrderEvent> cf) {

        var factory = new ConcurrentKafkaListenerContainerFactory<String, OrderEvent>();
        factory.setConsumerFactory(cf);

        // Concurrency: number of consumer threads (≤ number of partitions)
        factory.setConcurrency(3);

        // Batch listening
        factory.setBatchListener(true);

        // Ack mode
        factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.RECORD);

        // Poll timeout
        factory.getContainerProperties().setPollTimeout(3000);

        // Error handler
        factory.setCommonErrorHandler(new DefaultErrorHandler(
                new DeadLetterPublishingRecoverer(kafkaTemplate()),
                new FixedBackOff(1000L, 3L)
        ));

        // Message filter (skip test events in prod)
        factory.setRecordFilterStrategy(record ->
                "TEST".equals(record.value().getType()));

        return factory;
    }
}
```

---

### 16. How do you implement a Batch Listener in Spring Kafka?

**A:** Batch listeners receive all records from a single `poll()` call at once, enabling bulk processing:

```java
@Configuration
public class BatchKafkaConfig {

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, String> batchFactory(
            ConsumerFactory<String, String> cf) {
        var factory = new ConcurrentKafkaListenerContainerFactory<String, String>();
        factory.setConsumerFactory(cf);
        factory.setBatchListener(true);   // KEY: enables batch mode
        factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.BATCH);
        return factory;
    }
}

@Component
public class BatchOrderConsumer {

    // List<String> — simplest form
    @KafkaListener(topics = "orders", containerFactory = "batchFactory")
    public void handleBatch(List<String> orders) {
        log.info("Processing batch of {} orders", orders.size());
        orderRepository.saveAll(orders.stream()
            .map(this::parse)
            .collect(toList()));
    }

    // List<ConsumerRecord> — with metadata
    @KafkaListener(topics = "orders", containerFactory = "batchFactory")
    public void handleBatchWithMeta(List<ConsumerRecord<String, String>> records,
                                    Acknowledgment ack) {
        try {
            records.forEach(r -> processRecord(r));
            ack.acknowledge();
        } catch (Exception e) {
            // partial failures: nack from specific offset
            ack.nack(records.indexOf(failedRecord), Duration.ofSeconds(1));
        }
    }

    // ConsumerRecords — access to per-partition grouping
    @KafkaListener(topics = "orders", containerFactory = "batchFactory")
    public void handleConsumerRecords(ConsumerRecords<String, String> records) {
        records.partitions().forEach(tp -> {
            List<ConsumerRecord<String, String>> partitionRecords = records.records(tp);
            log.info("Partition {}: {} records", tp.partition(), partitionRecords.size());
        });
    }
}
```

---

### 17. What is the Dead Letter Topic pattern in Spring Kafka?

**A:** When a message fails repeatedly, it's forwarded to a Dead Letter Topic (DLT) instead of blocking the consumer forever:

```java
@Configuration
public class DltKafkaConfig {

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, String> kafkaListenerContainerFactory(
            ConsumerFactory<String, String> cf,
            KafkaTemplate<String, String> template) {

        // DeadLetterPublishingRecoverer: forwards failed messages to <topic>.DLT
        DeadLetterPublishingRecoverer recoverer = new DeadLetterPublishingRecoverer(template,
                (record, ex) -> new TopicPartition(
                        record.topic() + ".DLT",
                        record.partition()   // preserve partition affinity
                ));

        // Retry 3 times with 1s backoff, then send to DLT
        DefaultErrorHandler errorHandler = new DefaultErrorHandler(
                recoverer,
                new FixedBackOff(1000L, 3L)
        );

        // Don't retry on these exceptions (send straight to DLT)
        errorHandler.addNotRetryableExceptions(
                InvalidMessageException.class,
                JsonParseException.class
        );

        var factory = new ConcurrentKafkaListenerContainerFactory<String, String>();
        factory.setConsumerFactory(cf);
        factory.setCommonErrorHandler(errorHandler);
        return factory;
    }
}

// Consumer for the DLT
@Component
public class DltConsumer {

    @KafkaListener(topics = "orders.DLT", groupId = "dlt-handler")
    public void handleDlt(
            ConsumerRecord<String, String> record,
            @Header(KafkaHeaders.DLT_EXCEPTION_MESSAGE) String exMessage,
            @Header(KafkaHeaders.DLT_ORIGINAL_TOPIC) String originalTopic,
            @Header(KafkaHeaders.DLT_ORIGINAL_OFFSET) long originalOffset) {

        log.error("DLT received from topic={}, offset={}, error={}",
                originalTopic, originalOffset, exMessage);
        // alert, store to DB, manual review, etc.
    }
}
```

---

### 18. How do you configure Dead Letter Queues in RabbitMQ with Spring AMQP?

**A:** RabbitMQ DLQ routes rejected/expired/failed messages to a separate exchange and queue:

```java
@Configuration
public class RabbitDlqConfig {

    // Dead letter exchange and queue
    @Bean
    public DirectExchange deadLetterExchange() {
        return new DirectExchange("orders.dlx");
    }

    @Bean
    public Queue deadLetterQueue() {
        return QueueBuilder.durable("orders.dlq").build();
    }

    @Bean
    public Binding deadLetterBinding() {
        return BindingBuilder.bind(deadLetterQueue())
                             .to(deadLetterExchange())
                             .with("orders.dead");
    }

    // Main queue: point to DLX on failure
    @Bean
    public Queue ordersQueue() {
        return QueueBuilder.durable("orders.queue")
                .withArgument("x-dead-letter-exchange", "orders.dlx")
                .withArgument("x-dead-letter-routing-key", "orders.dead")
                .withArgument("x-message-ttl", 30000)   // optional: TTL before DLQ
                .build();
    }

    @Bean
    public DirectExchange ordersExchange() {
        return new DirectExchange("orders.exchange");
    }

    @Bean
    public Binding ordersBinding() {
        return BindingBuilder.bind(ordersQueue()).to(ordersExchange()).with("orders");
    }
}

// Consumer that rejects failed messages to DLQ
@Component
public class RabbitOrderConsumer {

    @RabbitListener(queues = "orders.queue")
    public void handle(String order, Channel channel,
                       @Header(AmqpHeaders.DELIVERY_TAG) long tag) throws IOException {
        try {
            process(order);
            channel.basicAck(tag, false);
        } catch (Exception e) {
            // requeue=false → routes to DLX/DLQ
            channel.basicNack(tag, false, false);
        }
    }
}
```

---

### 19. How do you implement retry topics in Spring Kafka?

**A:** Retry topics allow failed messages to be retried with delays without blocking the main topic. Spring Kafka 2.7+ has first-class retry topic support:

```java
@Configuration
@EnableKafka
@EnableKafkaRetryTopic   // enables non-blocking retry topics
public class RetryTopicConfig {

    @Bean
    public RetryTopicConfiguration orderRetryConfig(KafkaTemplate<String, String> template) {
        return RetryTopicConfigurationBuilder
                .newInstance()
                .fixedBackOff(1000L)           // 1 second between retries
                .maxAttempts(4)                 // 1 original + 3 retries
                .retryTopicSuffix("-retry")
                .dltSuffix("-dlt")
                .includeTopic("orders")
                .create(template);
    }
}

@Component
public class RetryableOrderConsumer {

    // Retry topics created automatically: orders-retry-0, orders-retry-1, etc.
    // After all retries: orders-dlt
    @RetryableTopic(
        attempts = "4",
        backoff = @Backoff(delay = 1000, multiplier = 2),   // exponential: 1s, 2s, 4s
        dltTopicSuffix = "-dead",
        retryTopicSuffix = "-retry",
        exclude = {InvalidDataException.class}   // don't retry these
    )
    @KafkaListener(topics = "orders")
    public void handleOrder(String order) {
        // If this throws, message goes to orders-retry-N
        orderService.process(order);
    }

    @DltHandler
    public void handleDlt(String order) {
        log.error("Order failed all retries: {}", order);
        alertingService.notify(order);
    }
}
```

---

### 20. What is `SeekToCurrentErrorHandler` and `DefaultErrorHandler`?

**A:** Error handlers determine what happens when a `@KafkaListener` throws an exception:

- **`SeekToCurrentErrorHandler`** (deprecated in 2.8): re-seeks the failed partition to the failed offset, effectively retrying in-place.
- **`DefaultErrorHandler`** (2.8+, replacement): combines retry with pluggable recovery.

```java
@Configuration
public class ErrorHandlerConfig {

    @Bean
    public DefaultErrorHandler defaultErrorHandler(KafkaTemplate<String, String> template) {

        // Recovery: send to DLT after exhausting retries
        var recoverer = new DeadLetterPublishingRecoverer(template);

        // Retry policy
        var backOff = new ExponentialBackOffWithMaxRetries(3);
        backOff.setInitialInterval(1000L);
        backOff.setMultiplier(2.0);
        backOff.setMaxInterval(10000L);

        var handler = new DefaultErrorHandler(recoverer, backOff);

        // Fatal exceptions → skip retries, go straight to DLT
        handler.addNotRetryableExceptions(
                DeserializationException.class,
                MessageConversionException.class
        );

        // Retryable even though they're RuntimeExceptions
        handler.addRetryableExceptions(TransientDataAccessException.class);

        // Listener for monitoring
        handler.setRetryListeners((record, ex, attempt) ->
                log.warn("Retry attempt {} for offset {} on {}",
                        attempt, record.offset(), record.topic()));

        return handler;
    }
}
```

---

## 🔴 Senior

---

### 21. How do you implement Kafka Streams with Spring Boot?

**A:** Kafka Streams is a client library for real-time stream processing. Spring provides `@EnableKafkaStreams` and auto-configuration:

```yaml
spring:
  kafka:
    streams:
      application-id: order-analytics
      bootstrap-servers: localhost:9092
      properties:
        default.key.serde: org.apache.kafka.common.serialization.Serdes$StringSerde
        default.value.serde: org.apache.kafka.common.serialization.Serdes$StringSerde
```

```java
@Configuration
@EnableKafkaStreams
public class OrderStreamConfig {

    public static final String INPUT_TOPIC = "orders";
    public static final String OUTPUT_TOPIC = "order-analytics";

    @Bean
    public KStream<String, OrderEvent> orderStream(StreamsBuilder builder) {

        // Simple filter + map pipeline
        KStream<String, OrderEvent> orders = builder.stream(INPUT_TOPIC,
                Consumed.with(Serdes.String(), orderEventSerde()));

        // Branch by status
        Map<String, KStream<String, OrderEvent>> branches = orders.split(Named.as("branch-"))
                .branch((key, value) -> "COMPLETED".equals(value.getStatus()), Branched.as("completed"))
                .branch((key, value) -> "FAILED".equals(value.getStatus()), Branched.as("failed"))
                .defaultBranch(Branched.as("pending"));

        // Count orders per customer (tumbling window of 1 hour)
        branches.get("branch-completed")
                .groupByKey()
                .windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofHours(1)))
                .count(Materialized.as("order-counts-store"))
                .toStream()
                .map((windowedKey, count) -> KeyValue.pair(
                        windowedKey.key(),
                        new CustomerStats(windowedKey.key(), count, windowedKey.window().start())))
                .to(OUTPUT_TOPIC);

        // Join orders with customer profiles
        KTable<String, CustomerProfile> profiles = builder.table("customer-profiles",
                Materialized.as("profiles-store"));

        orders.join(profiles,
                (order, profile) -> new EnrichedOrder(order, profile),
                Joined.with(Serdes.String(), orderEventSerde(), customerProfileSerde()))
              .to("enriched-orders");

        return orders;
    }

    // Query the state store directly (interactive queries)
    @Autowired
    private KafkaStreamsRegistry streamsRegistry;

    public long getOrderCount(String customerId) {
        ReadOnlyWindowStore<String, Long> store = streamsRegistry
                .getKafkaStreams(orderStream(null), "order-counts-store")
                .store(StoreQueryParameters.fromNameAndType("order-counts-store",
                        QueryableStoreTypes.windowStore()));
        // query store...
        return 0L;
    }
}
```

---

### 22. How do you implement the Outbox Pattern in Spring?

**A:** The Outbox pattern solves the dual-write problem: writing to both a database and a message broker atomically. Instead of writing to the broker directly, write to an `outbox` table in the same DB transaction, then relay asynchronously:

```sql
-- outbox table
CREATE TABLE outbox_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aggregate_type VARCHAR(255) NOT NULL,
    aggregate_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    published BOOLEAN NOT NULL DEFAULT false,
    published_at TIMESTAMP
);
```

```java
// Entity
@Entity @Table(name = "outbox_events")
@Data @Builder
public class OutboxEvent {
    @Id @GeneratedValue private UUID id;
    private String aggregateType;
    private String aggregateId;
    private String eventType;
    @Column(columnDefinition = "jsonb") private String payload;
    private LocalDateTime createdAt;
    private boolean published;
    private LocalDateTime publishedAt;
}

// Writing order + outbox in ONE transaction
@Service
@RequiredArgsConstructor
@Transactional
public class OrderService {

    private final OrderRepository orderRepository;
    private final OutboxEventRepository outboxRepository;
    private final ObjectMapper objectMapper;

    public Order createOrder(CreateOrderRequest req) {
        Order order = orderRepository.save(Order.from(req));

        // Same transaction: write outbox record
        outboxRepository.save(OutboxEvent.builder()
                .aggregateType("Order")
                .aggregateId(order.getId().toString())
                .eventType("OrderCreated")
                .payload(objectMapper.writeValueAsString(new OrderCreatedEvent(order)))
                .createdAt(LocalDateTime.now())
                .build());

        return order;  // both committed atomically or both rolled back
    }
}

// Polling publisher (scheduled relay)
@Component
@RequiredArgsConstructor
public class OutboxPoller {

    private final OutboxEventRepository outboxRepository;
    private final KafkaTemplate<String, String> kafkaTemplate;

    @Scheduled(fixedDelay = 500)
    @Transactional
    public void pollAndPublish() {
        List<OutboxEvent> unpublished = outboxRepository
                .findTop100ByPublishedFalseOrderByCreatedAtAsc();

        unpublished.forEach(event -> {
            kafkaTemplate.send(
                    event.getAggregateType().toLowerCase() + "s",
                    event.getAggregateId(),
                    event.getPayload()
            ).whenComplete((result, ex) -> {
                if (ex == null) {
                    event.setPublished(true);
                    event.setPublishedAt(LocalDateTime.now());
                    outboxRepository.save(event);
                }
            });
        });
    }
}
```

> **Alternative**: Use Debezium CDC (Change Data Capture) to stream outbox table changes directly to Kafka without polling — zero-latency, no polling overhead.

---

### 23. How does `@TransactionalEventListener` work for transactional messaging?

**A:** `@TransactionalEventListener` fires Spring application events bound to a transaction phase, ensuring the event is published only after the DB transaction commits:

```java
// Event class
public record OrderCreatedEvent(String orderId, String customerId, BigDecimal amount) {}

// Publisher (fires the Spring event, not Kafka directly)
@Service
@RequiredArgsConstructor
@Transactional
public class OrderService {

    private final OrderRepository repository;
    private final ApplicationEventPublisher eventPublisher;

    public Order createOrder(CreateOrderRequest req) {
        Order order = repository.save(Order.from(req));
        // This event is held until transaction commits
        eventPublisher.publishEvent(new OrderCreatedEvent(
                order.getId(), order.getCustomerId(), order.getAmount()));
        return order;
    }
}

// Listener: receives event AFTER transaction commits
@Component
@RequiredArgsConstructor
public class OrderEventRelay {

    private final KafkaTemplate<String, String> kafkaTemplate;

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void onOrderCreated(OrderCreatedEvent event) {
        // Safe: DB is committed, now publish to Kafka
        kafkaTemplate.send("orders", event.orderId(), toJson(event));
    }

    @TransactionalEventListener(phase = TransactionPhase.AFTER_ROLLBACK)
    public void onRollback(OrderCreatedEvent event) {
        log.warn("Order creation rolled back: {}", event.orderId());
    }

    // WARNING: if Kafka send fails here, the DB is already committed → use Outbox pattern
    // @TransactionalEventListener + Kafka is NOT atomic; use as a best-effort optimization
}
```

**Phases:**
| Phase | When |
|-------|------|
| `BEFORE_COMMIT` | Just before commit (can veto) |
| `AFTER_COMMIT` | After successful commit |
| `AFTER_ROLLBACK` | After rollback |
| `AFTER_COMPLETION` | After commit or rollback |

---

### 24. How do you implement the Saga pattern with Kafka?

**A:** The Saga pattern manages distributed transactions as a sequence of local transactions with compensating transactions on failure. Two styles: **Choreography** (events trigger next steps) and **Orchestration** (central coordinator):

```java
// ── CHOREOGRAPHY SAGA ──

// Step 1: Order service creates order and emits event
@Service
public class OrderService {
    @Transactional
    public void createOrder(CreateOrderRequest req) {
        Order order = orderRepo.save(new Order(req, OrderStatus.PENDING));
        kafkaTemplate.send("order.created", order.getId(), toJson(order));
    }
}

// Step 2: Inventory service reserves stock
@KafkaListener(topics = "order.created")
public void onOrderCreated(String payload) {
    Order order = parse(payload);
    try {
        inventoryService.reserve(order);
        kafkaTemplate.send("inventory.reserved", order.getId(), toJson(order));
    } catch (InsufficientStockException e) {
        kafkaTemplate.send("inventory.reservation.failed", order.getId(), toJson(order));
    }
}

// Step 3a: Payment service charges customer
@KafkaListener(topics = "inventory.reserved")
public void onInventoryReserved(String payload) {
    Order order = parse(payload);
    try {
        paymentService.charge(order);
        kafkaTemplate.send("payment.processed", order.getId(), toJson(order));
    } catch (PaymentException e) {
        kafkaTemplate.send("payment.failed", order.getId(), toJson(order));
    }
}

// Compensating transaction: undo inventory reservation on payment failure
@KafkaListener(topics = "payment.failed")
public void onPaymentFailed(String payload) {
    Order order = parse(payload);
    inventoryService.release(order);   // compensate
    kafkaTemplate.send("inventory.released", order.getId(), toJson(order));
    kafkaTemplate.send("order.cancelled", order.getId(), toJson(order));
}
```

```java
// ── ORCHESTRATION SAGA (with state machine) ──

@Component
@RequiredArgsConstructor
public class OrderSagaOrchestrator {

    private final KafkaTemplate<String, String> kafkaTemplate;
    private final SagaStateRepository sagaStateRepo;

    @KafkaListener(topics = {"inventory.reserved", "inventory.reservation.failed",
                             "payment.processed", "payment.failed"})
    public void handleSagaEvent(ConsumerRecord<String, String> record) {
        SagaState state = sagaStateRepo.findByOrderId(record.key());

        switch (record.topic()) {
            case "inventory.reserved" -> {
                state.setStep(SagaStep.INVENTORY_RESERVED);
                sagaStateRepo.save(state);
                kafkaTemplate.send("payment.commands", record.key(), "CHARGE");
            }
            case "payment.processed" -> {
                state.setStep(SagaStep.COMPLETED);
                sagaStateRepo.save(state);
                kafkaTemplate.send("order.commands", record.key(), "CONFIRM");
            }
            case "inventory.reservation.failed", "payment.failed" -> {
                compensate(state, record.topic());
            }
        }
    }

    private void compensate(SagaState state, String failureTopic) {
        // issue compensating commands based on how far saga progressed
        if (state.getStep().ordinal() >= SagaStep.INVENTORY_RESERVED.ordinal()) {
            kafkaTemplate.send("inventory.commands", state.getOrderId(), "RELEASE");
        }
        kafkaTemplate.send("order.commands", state.getOrderId(), "CANCEL");
    }
}
```

---

### 25. How do you use Avro with Spring Cloud Schema Registry?

**A:** Avro provides schema-based binary serialization. Schema Registry stores and versions schemas, enabling schema evolution:

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-stream-binder-kafka</artifactId>
</dependency>
<dependency>
    <groupId>io.confluent</groupId>
    <artifactId>kafka-avro-serializer</artifactId>
    <version>7.5.0</version>
</dependency>
```

```json
// src/main/avro/OrderEvent.avsc
{
  "type": "record",
  "name": "OrderEvent",
  "namespace": "com.example.events",
  "fields": [
    {"name": "orderId", "type": "string"},
    {"name": "customerId", "type": "string"},
    {"name": "amount", "type": "double"},
    {"name": "status", "type": {"type": "enum", "name": "OrderStatus",
      "symbols": ["PENDING", "COMPLETED", "CANCELLED"]}},
    {"name": "metadata", "type": ["null", "string"], "default": null}
  ]
}
```

```yaml
spring:
  kafka:
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: io.confluent.kafka.serializers.KafkaAvroSerializer
      properties:
        schema.registry.url: http://localhost:8081
        auto.register.schemas: true
    consumer:
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: io.confluent.kafka.serializers.KafkaAvroDeserializer
      properties:
        schema.registry.url: http://localhost:8081
        specific.avro.reader: true   # deserialize to generated Java class
```

```java
// Generated class (from avro-maven-plugin)
@KafkaListener(topics = "orders")
public void handleAvroOrder(OrderEvent event) {   // typed, generated class
    log.info("Order {} for customer {} amount {}",
            event.getOrderId(), event.getCustomerId(), event.getAmount());
}

@Service
public class AvroOrderProducer {
    private final KafkaTemplate<String, OrderEvent> kafkaTemplate;

    public void send(Order order) {
        OrderEvent event = OrderEvent.newBuilder()
                .setOrderId(order.getId())
                .setCustomerId(order.getCustomerId())
                .setAmount(order.getAmount())
                .setStatus(OrderStatus.PENDING)
                .build();
        kafkaTemplate.send("orders", order.getId(), event);
    }
}
```

**Schema Evolution Compatibility Modes:**

| Mode | Allowed changes |
|------|----------------|
| `BACKWARD` | Add fields with defaults, remove fields |
| `FORWARD` | Remove fields with defaults, add fields |
| `FULL` | Both backward and forward compatible |
| `NONE` | No compatibility check |

---

### 26. How do you implement Event Sourcing with Spring?

**A:** Event Sourcing stores every state change as an immutable event. Current state is derived by replaying events:

```java
// Event hierarchy
public sealed interface OrderEvent permits
    OrderCreated, OrderItemAdded, OrderConfirmed, OrderCancelled {}

public record OrderCreated(String orderId, String customerId, Instant timestamp) implements OrderEvent {}
public record OrderItemAdded(String orderId, String productId, int qty, BigDecimal price) implements OrderEvent {}
public record OrderConfirmed(String orderId, Instant timestamp) implements OrderEvent {}

// Event store (Kafka-backed or DB)
@Entity @Table(name = "event_store")
public class StoredEvent {
    @Id @GeneratedValue private Long id;
    private String aggregateId;
    private String aggregateType;
    private String eventType;
    private long version;
    @Column(columnDefinition = "jsonb") private String payload;
    private Instant occurredAt;
}

// Aggregate with event sourcing
@Aggregate
public class Order {

    private String id;
    private String customerId;
    private List<OrderItem> items = new ArrayList<>();
    private OrderStatus status;
    private long version;

    // Apply events to rebuild state
    public static Order reconstitute(List<OrderEvent> events) {
        Order order = new Order();
        events.forEach(order::apply);
        return order;
    }

    private void apply(OrderEvent event) {
        switch (event) {
            case OrderCreated e -> {
                this.id = e.orderId();
                this.customerId = e.customerId();
                this.status = OrderStatus.DRAFT;
                this.version++;
            }
            case OrderItemAdded e -> {
                this.items.add(new OrderItem(e.productId(), e.qty(), e.price()));
                this.version++;
            }
            case OrderConfirmed e -> {
                this.status = OrderStatus.CONFIRMED;
                this.version++;
            }
            case OrderCancelled e -> {
                this.status = OrderStatus.CANCELLED;
                this.version++;
            }
        }
    }
}

// Repository that persists/loads events
@Repository
@RequiredArgsConstructor
public class OrderEventRepository {

    private final StoredEventJpaRepository jpaRepo;
    private final KafkaTemplate<String, String> kafkaTemplate;
    private final ObjectMapper mapper;

    @Transactional
    public void append(String orderId, List<OrderEvent> newEvents, long expectedVersion) {
        long currentVersion = jpaRepo.maxVersionByAggregateId(orderId).orElse(-1L);
        if (currentVersion != expectedVersion) {
            throw new OptimisticLockException("Version conflict on order " + orderId);
        }

        newEvents.forEach(event -> {
            StoredEvent stored = new StoredEvent();
            stored.setAggregateId(orderId);
            stored.setAggregateType("Order");
            stored.setEventType(event.getClass().getSimpleName());
            stored.setPayload(mapper.writeValueAsString(event));
            stored.setVersion(++currentVersion);
            stored.setOccurredAt(Instant.now());
            jpaRepo.save(stored);

            // Publish to Kafka (for projections/read models)
            kafkaTemplate.send("order-events", orderId, stored.getPayload());
        });
    }

    public List<OrderEvent> load(String orderId) {
        return jpaRepo.findByAggregateIdOrderByVersionAsc(orderId)
                .stream()
                .map(this::deserialize)
                .collect(toList());
    }
}
```

---

### 27. What is Kafka Connect and when would you use it over a custom producer?

**A:** Kafka Connect is a framework for reliably streaming data between Kafka and external systems (databases, S3, Elasticsearch, etc.) using reusable, configurable connectors:

```json
// Source Connector: PostgreSQL → Kafka (Debezium CDC)
{
  "name": "orders-postgres-source",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "debezium",
    "database.password": "secret",
    "database.dbname": "ordersdb",
    "table.include.list": "public.orders,public.outbox_events",
    "topic.prefix": "dbserver1",
    "plugin.name": "pgoutput",
    "transforms": "outbox",
    "transforms.outbox.type": "io.debezium.transforms.outbox.EventRouter"
  }
}
```

```json
// Sink Connector: Kafka → Elasticsearch
{
  "name": "orders-es-sink",
  "config": {
    "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
    "tasks.max": "3",
    "topics": "orders",
    "connection.url": "http://elasticsearch:9200",
    "type.name": "_doc",
    "key.ignore": "false",
    "schema.ignore": "true",
    "transforms": "unwrap",
    "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState"
  }
}
```

```java
// When to use Kafka Connect vs custom producer:
// ✅ Kafka Connect: DB change capture, file ingestion, S3/ES sync, no custom logic needed
// ✅ Custom producer: complex business logic, enrichment, conditional publishing, fine-grained control

// Programmatically deploying connectors via REST
@Service
public class KafkaConnectManager {

    private final RestTemplate restTemplate;

    public void deployConnector(String name, Map<String, String> config) {
        Map<String, Object> body = Map.of("name", name, "config", config);
        restTemplate.postForEntity(
                "http://kafka-connect:8083/connectors",
                body, String.class);
    }

    public ConnectorStatus getStatus(String name) {
        return restTemplate.getForObject(
                "http://kafka-connect:8083/connectors/{name}/status",
                ConnectorStatus.class, name);
    }
}
```

---

### 28. How does exactly-once semantics work end-to-end in Kafka?

**A:** True exactly-once requires coordination between producer, broker, and consumer:

```
Producer (idempotent + transactional)
    ↓ beginTransaction()
    ↓ send to topic A
    ↓ send to topic B
    ↓ sendOffsetsToTransaction(consumer offsets)  ← atomic consume+produce
    ↓ commitTransaction()
Consumer (isolation.level=read_committed)
    ↓ only reads committed records
```

```java
@Configuration
public class ExactlyOnceConfig {

    @Bean
    public ProducerFactory<String, String> exactlyOnceProducerFactory() {
        return new DefaultKafkaProducerFactory<>(Map.of(
                ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092",
                ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true,
                ProducerConfig.TRANSACTIONAL_ID_CONFIG, "eos-producer-1",
                ProducerConfig.ACKS_CONFIG, "all"
        ));
    }

    @Bean
    public ConsumerFactory<String, String> exactlyOnceConsumerFactory() {
        return new DefaultKafkaConsumerFactory<>(Map.of(
                ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092",
                ConsumerConfig.GROUP_ID_CONFIG, "eos-group",
                ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_committed",
                ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false
        ));
    }

    // EOSMode.V2 (Kafka 3.0+): per-partition transactions (better performance)
    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, String> eosContainerFactory() {
        var factory = new ConcurrentKafkaListenerContainerFactory<String, String>();
        factory.setConsumerFactory(exactlyOnceConsumerFactory());
        factory.getContainerProperties().setEosMode(ContainerProperties.EOSMode.V2);
        return factory;
    }
}
```

**EOS guarantees stack:**
1. **Idempotent producer** → no duplicate writes per producer session
2. **Transactions** → atomic multi-topic writes
3. **`read_committed`** → consumers skip aborted records
4. **`sendOffsetsToTransaction`** → atomic consume-transform-produce

---

## 🏛️ Architect

---

### 29. How do you design a Kafka-based system for high throughput with ordering guarantees?

**A:** Ordering and throughput are in tension in Kafka. Design considerations:

```
Ordering in Kafka is only guaranteed WITHIN a partition.
Throughput scales with partition count, but more partitions = more consumers.

Strategy: Partition by business key (orderId, customerId, accountId)
→ All events for the same entity land in the same partition
→ Processed sequentially by one consumer thread
```

```java
// Producer: ensure ordering by key
@Service
public class OrderEventProducer {

    private final KafkaTemplate<String, String> kafkaTemplate;

    public void emit(OrderEvent event) {
        // Kafka routes same key to same partition via hash(key) % numPartitions
        kafkaTemplate.send(new ProducerRecord<>(
                "orders",
                null,               // partition: null = let Kafka decide by key
                event.orderId(),    // key → consistent partition
                toJson(event)
        ));
    }
}

// Consumer: concurrency = number of partitions
@KafkaListener(
    topics = "orders",
    groupId = "order-processor",
    concurrency = "12"    // must not exceed partition count
)
public void handle(ConsumerRecord<String, String> record) {
    // All events for one orderId arrive at one thread in order
}
```

```yaml
# Partition count: balance between parallelism and overhead
# Rule of thumb: partitions = (target throughput) / (throughput per consumer)
# Example: 100k msg/s target, 10k msg/s per consumer → 10 partitions

# Producer tuning for throughput
spring:
  kafka:
    producer:
      batch-size: 131072         # 128KB batches
      linger-ms: 5               # wait up to 5ms to fill batch
      compression-type: lz4      # fast compression
      buffer-memory: 33554432    # 32MB send buffer
```

**Global ordering (all partitions):** Use a single partition (sacrifices parallelism) or implement a sequencer pattern — a dedicated service assigns monotonically increasing sequence numbers before enqueuing.

---

### 30. How do you handle schema evolution and backward compatibility in a Kafka-based microservices architecture?

**A:** Schema evolution strategy is critical for zero-downtime deployments in a polyglot event ecosystem:

```
Compatibility matrix (Avro/Protobuf/JSON Schema):

BACKWARD: New schema can read OLD data     → deploy consumers first
FORWARD:  Old schema can read NEW data     → deploy producers first
FULL:     Both directions                  → deploy in any order
```

```java
// SAFE evolution examples (BACKWARD compatible):

// v1
public record OrderCreated(String orderId, String customerId) {}

// v2: add optional field with default → BACKWARD compatible
public record OrderCreated(
        String orderId,
        String customerId,
        @Nullable String channelId      // null = old consumers ignore it
) {}

// UNSAFE: renaming a field without alias → BREAKS backward compatibility
// UNSAFE: removing a required field
// UNSAFE: changing field type (String → Integer)

// Avro alias for field rename (safe evolution)
{
  "name": "userId",               // new name
  "aliases": ["customerId"],      // old name consumers can still read
  "type": "string"
}
```

```java
// Versioned event handling in consumers
@Component
public class OrderEventHandler {

    @KafkaListener(topics = "orders")
    public void handle(ConsumerRecord<String, GenericRecord> record) {
        GenericRecord avro = record.value();
        String schemaVersion = avro.getSchema().getProp("version");

        switch (schemaVersion) {
            case "1" -> handleV1(avro);
            case "2" -> handleV2(avro);
            default  -> handleLatest(avro);
        }
    }

    // Or use Avro's ReflectDatumReader with schema resolution
}

// CI/CD integration: schema compatibility check before deployment
// mvn schema-registry:validate
// confluent schema-registry schemas compatibility check
```

```yaml
# Schema Registry: enforce compatibility at registration time
spring:
  cloud:
    schema-registry:
      avro:
        schema-locations: classpath:avro/*.avsc
      compatibility-mode: FULL_TRANSITIVE   # strictest: all previous versions must be compatible
```

---

### 31. How do you design for consumer lag monitoring and backpressure in Kafka?

**A:** Consumer lag (difference between latest offset and committed offset) is the primary health signal. Architect a layered response:

```java
// Expose lag metrics via Micrometer
@Configuration
public class KafkaLagMonitoringConfig {

    @Bean
    public KafkaMetricsCollector kafkaMetricsCollector(
            AdminClient adminClient, MeterRegistry registry) {
        return new KafkaMetricsCollector(adminClient, registry);
    }
}

@Component
@RequiredArgsConstructor
@Slf4j
public class KafkaMetricsCollector {

    private final AdminClient adminClient;
    private final MeterRegistry registry;

    @Scheduled(fixedDelay = 30_000)
    public void collectLag() {
        try {
            Map<TopicPartition, OffsetAndMetadata> committed = adminClient
                    .listConsumerGroupOffsets("order-processor")
                    .partitionsToOffsetAndMetadata().get();

            Map<TopicPartition, Long> endOffsets = adminClient
                    .listOffsets(committed.keySet().stream()
                            .collect(toMap(tp -> tp, tp -> OffsetSpec.latest())))
                    .all().get()
                    .entrySet().stream()
                    .collect(toMap(Map.Entry::getKey, e -> e.getValue().offset()));

            committed.forEach((tp, offsetMeta) -> {
                long lag = endOffsets.get(tp) - offsetMeta.offset();
                Gauge.builder("kafka.consumer.lag", lag, Long::doubleValue)
                        .tag("topic", tp.topic())
                        .tag("partition", String.valueOf(tp.partition()))
                        .tag("group", "order-processor")
                        .register(registry);

                if (lag > 10_000) {
                    log.warn("High consumer lag: topic={}, partition={}, lag={}",
                            tp.topic(), tp.partition(), lag);
                }
            });
        } catch (Exception e) {
            log.error("Failed to collect Kafka lag", e);
        }
    }
}
```

```yaml
# Autoscaling based on lag (KEDA - Kubernetes Event-Driven Autoscaler)
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: order-processor-scaler
spec:
  scaleTargetRef:
    name: order-processor
  minReplicaCount: 2
  maxReplicaCount: 12    # must not exceed partition count
  triggers:
    - type: kafka
      metadata:
        bootstrapServers: kafka:9092
        consumerGroup: order-processor
        topic: orders
        lagThreshold: "1000"    # scale up when lag > 1000 per partition
        offsetResetPolicy: latest
```

---

### 32. How do you architect a multi-region Kafka deployment with data sovereignty requirements?

**A:** Multi-region Kafka involves replication decisions, latency trade-offs, and regulatory compliance:

```
Architecture options:

1. Active-Active (MirrorMaker 2)
   Region A: kafka-a                  Region B: kafka-b
   orders.A → [MM2] →  orders.A@B    orders.B → [MM2] → orders.B@A
   ✅ Full availability    ❌ Eventual consistency, offset translation needed

2. Active-Passive (disaster recovery)
   Primary: kafka-primary → [MM2] → Secondary: kafka-dr
   ✅ Simple, consistent  ❌ RPO > 0, RTO depends on failover speed

3. Hub-and-Spoke (central aggregation)
   Regional clusters → [MM2] → Global cluster (analytics, audit)
   ✅ Data locality for writes  ✅ Global view for reads
```

```yaml
# MirrorMaker 2 configuration
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaMirrorMaker2
metadata:
  name: mm2-eu-to-us
spec:
  clusters:
    - alias: eu
      bootstrapServers: kafka-eu.example.com:9093
    - alias: us
      bootstrapServers: kafka-us.example.com:9093
  mirrors:
    - sourceCluster: eu
      targetCluster: us
      sourceConnector:
        config:
          replication.factor: 3
          topics: "orders.*,payments.*"
          topics.blacklist: ".*\.internal,.*-retry"
      checkpointConnector:
        config:
          checkpoints.topic.replication.factor: 3
          emit.checkpoints.interval.seconds: "5"
      topicsPattern: "orders.*"
      groupsPattern: "order-processor"
```

```java
// Data sovereignty: ensure PII stays in region
@Service
public class RegionAwareEventRouter {

    private final Map<String, KafkaTemplate<String, String>> regionalTemplates;

    public void route(OrderEvent event) {
        String region = extractRegion(event.getCustomerId());

        // EU customers: EU cluster only (GDPR)
        // US customers: US cluster
        KafkaTemplate<String, String> template = regionalTemplates.get(region);
        template.send("orders", event.orderId(), toJson(event));

        // Publish non-PII summary to global cluster for analytics
        globalTemplate.send("order-analytics", event.orderId(), toAnonymizedJson(event));
    }
}
```

---

### 33. How do you implement CQRS with Kafka as the event bus and maintain read model consistency?

**A:** CQRS separates write (command) and read (query) models. Kafka propagates events to build and update read models:

```
Write Side (Commands → Domain Events → Kafka)
    OrderService.createOrder() 
    → OrderCreated event persisted to event store
    → published to Kafka topic "order-events"

Read Side (Events → Projections → Query Models)
    Kafka consumer → OrderSummaryProjection → PostgreSQL (for API queries)
    Kafka consumer → OrderSearchProjection  → Elasticsearch (for search)
    Kafka consumer → DashboardProjection    → Redis (for real-time dashboards)
```

```java
// Write side: pure domain model, emits events
@Service
@RequiredArgsConstructor
public class OrderCommandHandler {

    private final OrderEventStore eventStore;

    public void handle(CreateOrderCommand cmd) {
        // Load aggregate from event store
        List<OrderEvent> history = eventStore.loadEvents(cmd.orderId());
        Order order = Order.reconstitute(history);

        // Execute command → produces new events
        List<OrderEvent> newEvents = order.createOrder(cmd);

        // Persist events (outbox pattern for atomicity)
        eventStore.append(cmd.orderId(), newEvents, order.getVersion());
    }
}

// Read side: build queryable projections
@Component
@RequiredArgsConstructor
public class OrderSummaryProjection {

    private final OrderSummaryRepository queryDb;
    private final ElasticsearchClient esClient;

    @KafkaListener(topics = "order-events", groupId = "order-summary-projection")
    @Transactional
    public void project(ConsumerRecord<String, String> record) {
        OrderEvent event = deserialize(record.value());

        switch (event) {
            case OrderCreated e -> {
                queryDb.save(new OrderSummary(e.orderId(), e.customerId(),
                        OrderStatus.PENDING, e.timestamp()));
                esClient.index(i -> i.index("orders").id(e.orderId())
                        .document(Map.of("customerId", e.customerId(), "status", "PENDING")));
            }
            case OrderConfirmed e -> {
                queryDb.updateStatus(e.orderId(), OrderStatus.CONFIRMED);
                esClient.update(u -> u.index("orders").id(e.orderId())
                        .doc(Map.of("status", "CONFIRMED")));
            }
        }
    }
}

// Rebuilding a projection from scratch (replay)
@Service
public class ProjectionRebuilder {

    public void rebuild(String projectionName) {
        // Reset consumer group offset to beginning
        adminClient.alterConsumerGroupOffsets(
                projectionName + "-projection",
                partitions.stream().collect(toMap(tp -> tp,
                        tp -> new OffsetAndMetadata(0L)))
        ).all().get();

        // Consumer will replay all events from offset 0
        log.info("Projection {} reset; it will rebuild on next startup", projectionName);
    }
}
```

---

### 34. How do you design a fault-tolerant RabbitMQ topology for a high-availability payment system?

**A:** High-availability RabbitMQ for payments requires careful topology design across quorum queues, publisher confirms, and consumer acks:

```java
@Configuration
public class PaymentRabbitTopology {

    // Quorum queues: Raft-based replication (recommended over mirrored queues)
    @Bean
    public Queue paymentsQueue() {
        return QueueBuilder.durable("payments.queue")
                .quorum()                              // replicated across cluster nodes
                .withArgument("x-dead-letter-exchange", "payments.dlx")
                .withArgument("x-delivery-limit", 3)   // max requeue count before DLQ
                .build();
    }

    @Bean
    public Queue paymentsDlq() {
        return QueueBuilder.durable("payments.dlq")
                .quorum()
                .build();
    }

    @Bean
    public DirectExchange paymentsExchange() {
        return ExchangeBuilder.directExchange("payments.exchange")
                .durable(true)
                .build();
    }

    @Bean
    public DirectExchange paymentsDlx() {
        return ExchangeBuilder.directExchange("payments.dlx").durable(true).build();
    }

    @Bean
    public Binding paymentsBinding() {
        return BindingBuilder.bind(paymentsQueue()).to(paymentsExchange()).with("payment");
    }

    @Bean
    public Binding dlqBinding() {
        return BindingBuilder.bind(paymentsDlq()).to(paymentsDlx()).with("payment.dead");
    }

    // Publisher confirms for guaranteed delivery
    @Bean
    public RabbitTemplate rabbitTemplate(ConnectionFactory cf) {
        var template = new RabbitTemplate(cf);
        template.setConfirmCallback((correlationData, ack, cause) -> {
            if (!ack) {
                log.error("Payment message not confirmed by broker: {}", cause);
                // retry or alert
            }
        });
        template.setReturnsCallback(returned -> {
            log.error("Payment message returned: {} → {}",
                    returned.getRoutingKey(), returned.getReplyText());
        });
        template.setMandatory(true);  // enable returns
        return template;
    }
}

// Consumer with manual ack
@Component
public class PaymentConsumer {

    @RabbitListener(
        queues = "payments.queue",
        ackMode = "MANUAL",
        concurrency = "3-10"   // min 3, auto-scale to 10
    )
    public void processPayment(
            Message message,
            Channel channel,
            @Header(AmqpHeaders.DELIVERY_TAG) long tag) throws Exception {

        PaymentCommand cmd = deserialize(message.getBody());
        try {
            paymentGateway.charge(cmd);
            channel.basicAck(tag, false);           // success: remove from queue
        } catch (TransientException e) {
            channel.basicNack(tag, false, true);    // requeue for retry
        } catch (FatalException e) {
            channel.basicNack(tag, false, false);   // don't requeue → DLX → DLQ
        }
    }
}
```

---

### 35. What are the trade-offs between Kafka, RabbitMQ, and a database-backed queue (e.g., PostgreSQL SKIP LOCKED) for a task queue?

**A:** Each approach has a distinct sweet spot:

| Dimension | Kafka | RabbitMQ | DB Queue (PG SKIP LOCKED) |
|-----------|-------|----------|--------------------------|
| **Throughput** | Millions/sec | Tens of thousands/sec | Thousands/sec |
| **Latency** | ~5ms (batched) | ~1ms | ~10ms |
| **Replay** | ✅ Unlimited | ❌ No | ❌ No (deleted on ack) |
| **Ordering** | Per-partition | Per-queue | Custom ORDER BY |
| **Routing** | Topic + key | Exchange rules | SQL WHERE |
| **Priority queues** | ❌ Manual workaround | ✅ Native | ✅ ORDER BY priority |
| **Operational complexity** | High (ZK/KRaft, schema reg) | Medium | Low (already have DB) |
| **Exactly-once** | ✅ (EOS) | ❌ (at-least-once) | ✅ (DB transactions) |
| **Best for** | Event streaming, audit, CQRS | Task queues, RPC, complex routing | Simple job queues, small teams |

```java
// PostgreSQL SKIP LOCKED job queue — zero additional infrastructure
@Repository
public class PgJobQueue {

    @Transactional
    public Optional<Job> poll(String jobType) {
        return jdbcTemplate.query("""
                SELECT id, payload, attempt
                FROM jobs
                WHERE job_type = ? AND status = 'PENDING' AND scheduled_at <= now()
                ORDER BY priority DESC, created_at ASC
                LIMIT 1
                FOR UPDATE SKIP LOCKED   -- skip rows locked by other workers
                """,
                (rs, i) -> new Job(rs.getLong("id"), rs.getString("payload"), rs.getInt("attempt")),
                jobType
        ).stream().findFirst().map(job -> {
            jdbcTemplate.update("UPDATE jobs SET status='PROCESSING', attempt=attempt+1 WHERE id=?",
                    job.id());
            return job;
        });
    }
}
```

**Decision guide:**
- **Use Kafka**: Event-driven microservices, audit logs, event sourcing, replay needed, high volume
- **Use RabbitMQ**: Complex routing rules, priority queues, RPC patterns, existing AMQP expertise
- **Use DB queue**: Team already runs Postgres, low volume (<10k/day), simplicity over scale, transactional consistency critical

---

### 36. How do you implement distributed tracing across Kafka message boundaries?

**A:** Kafka messages break the HTTP request chain; you must propagate trace context via message headers:

```java
// Producer: inject trace context into Kafka headers
@Configuration
public class TracingKafkaConfig {

    @Bean
    public ProducerInterceptor<String, String> tracingProducerInterceptor(Tracer tracer) {
        return new ProducerInterceptor<>() {
            @Override
            public ProducerRecord<String, String> onSend(ProducerRecord<String, String> record) {
                Span span = tracer.currentSpan();
                if (span != null) {
                    // W3C TraceContext propagation
                    TraceContext ctx = span.context();
                    record.headers().add("traceparent",
                            ("00-" + ctx.traceIdString() + "-" + ctx.spanIdString() + "-01")
                                    .getBytes(StandardCharsets.UTF_8));
                    record.headers().add("tracestate", "".getBytes());
                }
                return record;
            }
            // ... other required methods
        };
    }
}

// Consumer: extract and continue trace
@Component
public class TracingOrderConsumer {

    private final Tracer tracer;

    @KafkaListener(topics = "orders")
    public void handle(ConsumerRecord<String, String> record) {
        // Extract trace context from headers
        Header traceparent = record.headers().lastHeader("traceparent");
        Span span;
        if (traceparent != null) {
            TraceContext parentCtx = parseTraceParent(new String(traceparent.value()));
            span = tracer.spanBuilder("kafka.consume")
                    .setParent(Context.current().with(Span.wrap(parentCtx)))
                    .setAttribute("messaging.system", "kafka")
                    .setAttribute("messaging.destination", record.topic())
                    .setAttribute("messaging.kafka.partition", record.partition())
                    .startSpan();
        } else {
            span = tracer.spanBuilder("kafka.consume").startSpan();
        }

        try (Scope scope = span.makeCurrent()) {
            processOrder(record.value());
        } catch (Exception e) {
            span.recordException(e);
            span.setStatus(StatusCode.ERROR);
            throw e;
        } finally {
            span.end();
        }
    }
}
```

```yaml
# Spring Boot auto-configuration (Micrometer Tracing + Brave/OTel)
spring:
  application:
    name: order-processor
management:
  tracing:
    sampling:
      probability: 1.0     # 100% in dev; use 0.1 in prod
  zipkin:
    tracing:
      endpoint: http://zipkin:9411/api/v2/spans
```

> Spring Kafka 3.x with Micrometer Tracing auto-instruments `KafkaTemplate` sends and `@KafkaListener` receives with no custom code if `spring-boot-starter-actuator` + `micrometer-tracing-bridge-brave` are on the classpath.

---

*Last updated: 2026 · Spring Boot 3.x · Spring Kafka 3.x · Apache Kafka 3.x*
