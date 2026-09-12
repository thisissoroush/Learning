# ☕ Java — Architect-Level Interview Questions

---

### 1. How do you design a Java microservices architecture?

**A:**

**Service decomposition (DDD):**
- Bounded contexts → services
- Each service owns its data (no shared DB)
- Domain events for cross-service communication

**Technology choices:**

```
[Client] → [API Gateway (Spring Cloud Gateway)]
              ↓
[Service A: Spring Boot + JPA + Kafka]
[Service B: Quarkus + Panache + REST]
[Service C: Micronaut + R2DBC (reactive)]
              ↓
[Kafka] → [Event consumers]
[PostgreSQL per service]
[Redis for caching/sessions]
[Elasticsearch for search]
```

**Spring Boot service skeleton:**
```java
@SpringBootApplication
@EnableKafka
public class OrderServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(OrderServiceApplication.class, args);
    }
}

// Domain-driven layers
// controller → service → domain → repository
// No domain knowledge in controller; no persistence in domain
```

**Key patterns:**
- API Gateway — single entry point, auth, rate limiting, routing
- Service discovery — Kubernetes DNS or Consul
- Circuit breaker — Resilience4j
- Distributed tracing — Micrometer + Zipkin/Jaeger
- Config — Spring Cloud Config or Kubernetes ConfigMaps

---

### 2. How do you implement CQRS and Event Sourcing in Java?

**A:**

```java
// Command side — writes
@Service
public class OrderCommandService {
    private final OrderRepository repo;
    private final ApplicationEventPublisher events;

    public Order createOrder(CreateOrderCommand cmd) {
        Order order = Order.create(cmd.getCustomerId(), cmd.getItems());
        repo.save(order);
        // Publish domain event — within transaction (outbox or @TransactionalEventListener)
        events.publishEvent(new OrderCreatedEvent(order.getId()));
        return order;
    }
}

// Event — domain event
public record OrderCreatedEvent(UUID orderId) {}

// Query side — reads from optimized read model
@Repository
public interface OrderSummaryRepository extends JpaRepository<OrderSummary, UUID> {
    @Query("""
        SELECT NEW com.myapp.dto.OrderDto(o.id, o.total, c.name)
        FROM Order o JOIN Customer c ON c.id = o.customerId
        WHERE o.status = :status
        ORDER BY o.createdAt DESC
        """)
    Page<OrderDto> findByStatus(@Param("status") OrderStatus status, Pageable pageable);
}

// Event Sourcing — store events, not state
@Entity
public class OrderEvent {
    @Id UUID id;
    UUID aggregateId;
    String eventType;
    String payload; // JSON
    LocalDateTime occurredAt;
    int version;
}

// Rebuild aggregate from events
public Order rehydrate(List<OrderEvent> events) {
    Order order = new Order();
    events.forEach(e -> order.apply(deserialize(e)));
    return order;
}
```

---

### 3. How do you handle distributed transactions in Java microservices?

**A:** Avoid 2-phase commit (slow, fragile). Use Saga pattern:

**Choreography Saga:**
```java
// OrderService publishes event → InventoryService reacts
@KafkaListener(topics = "orders")
public void onOrderCreated(OrderCreatedEvent event) {
    try {
        inventoryService.reserve(event.getOrderId(), event.getItems());
        kafkaTemplate.send("inventory", new InventoryReservedEvent(event.getOrderId()));
    } catch (InsufficientStockException e) {
        kafkaTemplate.send("inventory", new InventoryFailedEvent(event.getOrderId()));
    }
}
```

**Orchestration Saga with Axon Framework:**
```java
@Saga
public class OrderFulfillmentSaga {
    @Inject transient CommandGateway commandGateway;

    @StartSaga
    @SagaEventHandler(associationProperty = "orderId")
    public void on(OrderCreatedEvent event) {
        commandGateway.send(new ReserveInventoryCommand(event.getOrderId()));
    }

    @SagaEventHandler(associationProperty = "orderId")
    public void on(InventoryReservedEvent event) {
        commandGateway.send(new ProcessPaymentCommand(event.getOrderId()));
    }

    @EndSaga
    @SagaEventHandler(associationProperty = "orderId")
    public void on(PaymentConfirmedEvent event) {
        commandGateway.send(new FulfillOrderCommand(event.getOrderId()));
    }

    @SagaEventHandler(associationProperty = "orderId")
    public void on(InventoryFailedEvent event) {
        commandGateway.send(new CancelOrderCommand(event.getOrderId()));
        SagaLifecycle.end();
    }
}
```

---

### 4. How do you implement observability in a Java service fleet?

**A:**

**Micrometer + Prometheus + Grafana:**
```java
// Auto-configured by Spring Boot Actuator + Micrometer
// Add: spring-boot-starter-actuator + micrometer-registry-prometheus

@RestController
public class OrderController {
    private final MeterRegistry registry;
    private final Counter orderCounter;
    private final Timer orderLatency;

    OrderController(MeterRegistry registry) {
        this.registry = registry;
        this.orderCounter = Counter.builder("orders.created.total")
            .tag("service", "order-service")
            .register(registry);
        this.orderLatency = Timer.builder("orders.creation.duration")
            .publishPercentiles(0.5, 0.95, 0.99)
            .register(registry);
    }

    @PostMapping("/orders")
    public ResponseEntity<Order> create(@RequestBody CreateOrderRequest req) {
        return orderLatency.record(() -> {
            Order order = service.create(req);
            orderCounter.increment();
            return ResponseEntity.status(201).body(order);
        });
    }
}
```

**Distributed tracing with Micrometer Tracing (OpenTelemetry):**
```java
// application.properties
management.tracing.sampling.probability=1.0
management.otlp.tracing.endpoint=http://otel-collector:4318/v1/traces

// Auto-instrumented: HTTP requests, JDBC, Kafka
// Manual span:
@Autowired Tracer tracer;

Span span = tracer.nextSpan().name("processOrder").start();
try (Tracer.SpanInScope ws = tracer.withSpan(span)) {
    span.tag("order.id", orderId);
    processOrder(orderId);
} finally {
    span.end();
}
```

---

### 5. How do you design database access for a high-traffic Java service?

**A:**

**Connection pool tuning (HikariCP — Spring Boot default):**
```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000
      pool-name: OrderServicePool
      connection-test-query: SELECT 1
```

**Read/write split:**
```java
@Configuration
public class DataSourceConfig {
    @Bean @Primary
    DataSource primaryDataSource() { return primaryDS(); } // writes

    @Bean
    DataSource replicaDataSource() { return replicaDS(); } // reads

    @Bean
    DataSource routingDataSource() {
        Map<Object, Object> targets = Map.of("primary", primaryDataSource(), "replica", replicaDataSource());
        AbstractRoutingDataSource routing = new AbstractRoutingDataSource() {
            protected Object determineCurrentLookupKey() {
                return TransactionSynchronizationManager.isCurrentTransactionReadOnly() ? "replica" : "primary";
            }
        };
        routing.setTargetDataSources(targets);
        return routing;
    }
}

// Usage — route reads to replica automatically
@Transactional(readOnly = true) // routes to replica
public List<Order> findActiveOrders() { ... }
```

**Query optimization:**
```java
// Projections — select only needed columns
interface OrderSummary {
    UUID getId();
    BigDecimal getTotal();
    String getStatus();
}
List<OrderSummary> summaries = repo.findByStatus(status, OrderSummary.class);

// Bulk operations
repo.saveAll(orders);           // batched INSERT
@Modifying @Query("UPDATE Order o SET o.status = :s WHERE o.id IN :ids")
int bulkUpdateStatus(@Param("s") String s, @Param("ids") List<UUID> ids);
```

---

### 6. How do you implement multi-tenancy in Java?

**A:**

**Row-level with Hibernate Filters:**
```java
@Entity
@FilterDef(name = "tenantFilter", parameters = @ParamDef(name = "tenantId", type = String.class))
@Filter(name = "tenantFilter", condition = "tenant_id = :tenantId")
public class Order {
    @Column String tenantId;
    // ...
}

// Enable filter for each session
@Component
public class TenantHibernateInterceptor {
    @Autowired EntityManager em;

    public void enableTenantFilter(String tenantId) {
        Session session = em.unwrap(Session.class);
        session.enableFilter("tenantFilter").setParameter("tenantId", tenantId);
    }
}

// Request interceptor sets tenant context
@Component
public class TenantRequestInterceptor implements HandlerInterceptor {
    public boolean preHandle(HttpServletRequest req, HttpServletResponse res, Object handler) {
        String tenantId = req.getHeader("X-Tenant-ID");
        TenantContext.setCurrentTenant(tenantId);
        return true;
    }
    public void afterCompletion(...) { TenantContext.clear(); }
}
```

**Schema-per-tenant:**
```java
public class TenantSchemaConnectionProvider implements MultiTenantConnectionProvider {
    public Connection getConnection(String tenantId) throws SQLException {
        Connection conn = dataSource.getConnection();
        conn.createStatement().execute("SET search_path = " + tenantId);
        return conn;
    }
}
```

---

### 7. How do you design for zero-downtime deployment in Java?

**A:**

**Database migrations — Flyway / Liquibase:**
```sql
-- V1__add_email_verified.sql
ALTER TABLE users ADD COLUMN email_verified BOOLEAN; -- nullable first

-- V2__backfill_email_verified.sql (deploy after V1 is live)
UPDATE users SET email_verified = FALSE WHERE email_verified IS NULL;

-- V3__constrain_email_verified.sql (deploy after code no longer writes null)
ALTER TABLE users ALTER COLUMN email_verified SET NOT NULL DEFAULT FALSE;
```

**Kubernetes deployment:**
```yaml
strategy:
  rollingUpdate:
    maxUnavailable: 0
    maxSurge: 1

lifecycle:
  preStop:
    exec:
      command: ["sleep", "10"]  # let LB drain before SIGTERM

readinessProbe:
  httpGet: { path: /actuator/health/readiness, port: 8080 }
  initialDelaySeconds: 30
  periodSeconds: 5

livenessProbe:
  httpGet: { path: /actuator/health/liveness, port: 8080 }
```

**Spring Boot graceful shutdown:**
```yaml
server:
  shutdown: graceful
spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s
```

---

### 8. How do you enforce architecture rules in a Java codebase?

**A:**

**ArchUnit — testable architecture rules:**
```java
@AnalyzeClasses(packages = "com.myapp")
public class ArchitectureTest {

    @ArchTest
    ArchRule layeringRule = layeredArchitecture()
        .consideringAllDependencies()
        .layer("Controller").definedBy("..controller..")
        .layer("Service").definedBy("..service..")
        .layer("Repository").definedBy("..repository..")
        .layer("Domain").definedBy("..domain..")
        .whereLayer("Controller").mayOnlyBeAccessedByLayers("Controller")
        .whereLayer("Service").mayOnlyBeAccessedByLayers("Controller", "Service")
        .whereLayer("Repository").mayOnlyBeAccessedByLayers("Service")
        .whereLayer("Domain").mayNotAccessAnyLayer();

    @ArchTest
    ArchRule noCircularDeps = slices()
        .matching("com.myapp.(*)..")
        .should().beFreeOfCycles();

    @ArchTest
    ArchRule domainNoDependencies = noClasses()
        .that().resideInAPackage("..domain..")
        .should().dependOnClassesThat()
        .resideInAnyPackage("..repository..", "..controller..", "org.springframework..");

    @ArchTest
    ArchRule servicesMustBeAnnotated = classes()
        .that().resideInAPackage("..service..")
        .should().beAnnotatedWith(Service.class);
}
```

---

### 9. How do you implement resiliency patterns in Java?

**A:**

**Resilience4j (Circuit Breaker, Retry, Rate Limiter, Bulkhead):**
```java
// Circuit Breaker
CircuitBreakerConfig config = CircuitBreakerConfig.custom()
    .failureRateThreshold(50)               // open at 50% failure rate
    .slowCallRateThreshold(100)             // slow call = > 2s
    .slowCallDurationThreshold(Duration.ofSeconds(2))
    .waitDurationInOpenState(Duration.ofSeconds(30))
    .permittedNumberOfCallsInHalfOpenState(5)
    .slidingWindowSize(20)
    .build();

CircuitBreaker cb = CircuitBreaker.of("payment", config);

Supplier<PaymentResult> decorated = CircuitBreaker
    .decorateSupplier(cb, () -> paymentService.charge(amount));

Try.ofSupplier(decorated)
    .recover(CallNotPermittedException.class, ex -> PaymentResult.fallback())
    .recover(Exception.class, ex -> PaymentResult.error(ex.getMessage()));

// Retry
RetryConfig retryConfig = RetryConfig.custom()
    .maxAttempts(3)
    .waitDuration(Duration.ofMillis(500))
    .retryExceptions(IOException.class, TimeoutException.class)
    .ignoreExceptions(BusinessException.class)
    .build();

// Bulkhead — limit concurrent calls
BulkheadConfig bulkheadConfig = BulkheadConfig.custom()
    .maxConcurrentCalls(10)
    .maxWaitDuration(Duration.ofMillis(100))
    .build();

// Spring integration
@CircuitBreaker(name = "payment", fallbackMethod = "paymentFallback")
@Retry(name = "payment")
public PaymentResult charge(BigDecimal amount) { ... }

PaymentResult paymentFallback(BigDecimal amount, Exception ex) {
    log.warn("Payment service unavailable, using fallback", ex);
    return PaymentResult.queued(amount);
}
```

---

### 10. How do you approach performance testing and capacity planning for Java services?

**A:**

**Load testing with Gatling:**
```scala
class OrderSimulation extends Simulation {
  val scn = scenario("Create and query orders")
    .exec(http("Create Order")
      .post("/api/orders")
      .body(StringBody("""{"customerId": "c1", "items": [...]}"""))
      .check(status.is(201)))
    .pause(1.second)
    .exec(http("Get Order")
      .get("/api/orders/${orderId}")
      .check(status.is(200)))

  setUp(
    scn.inject(
      rampUsersPerSec(10).to(100).during(2.minutes),
      constantUsersPerSec(100).during(5.minutes)
    )
  ).protocols(http.baseUrl("http://order-service"))
   .assertions(
     global.responseTime.percentile3.lt(500),   // p99 < 500ms
     global.failedRequests.percent.lt(1)         // error rate < 1%
   )
}
```

**JVM tuning checklist:**
```bash
# Heap sizing
-Xms2g -Xmx2g          # set equal to avoid resizing pauses
-XX:+UseG1GC
-XX:MaxGCPauseMillis=100
-XX:G1HeapRegionSize=16m

# Container awareness (Java 11+)
-XX:+UseContainerSupport      # reads cgroup limits
-XX:MaxRAMPercentage=75.0     # use 75% of container RAM

# Native memory
-XX:MaxMetaspaceSize=256m

# JFR for profiling in production (minimal overhead)
-XX:StartFlightRecording=maxsize=100m,maxage=1d,dumponexit=true,filename=/tmp/jfr
```

**Key capacity metrics:**
- Requests per second at p99 < SLO
- Thread pool saturation (active/max threads)
- GC time as % of wall time (< 5% is good)
- DB connection pool wait time
- Heap utilization before/after GC
