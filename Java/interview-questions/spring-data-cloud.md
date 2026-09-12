# ☁️ Spring Cloud & Spring Data — Interview Questions (Junior → Architect)

---

## 🟢 Spring Data — Junior Level

---

### 1. What is Spring Data and what does it provide?

**A:** Spring Data is an umbrella project providing consistent, repository-based data access across different stores:

- **Spring Data JPA** — relational databases via JPA/Hibernate
- **Spring Data MongoDB** — MongoDB
- **Spring Data Redis** — Redis
- **Spring Data Elasticsearch** — Elasticsearch
- **Spring Data R2DBC** — reactive relational DB access

Core idea: define an interface, Spring generates the implementation:

```java
// No implementation needed — Spring generates it
public interface UserRepository extends JpaRepository<User, Long> {

    // Derived from method name
    List<User> findByEmailAndIsActiveTrue(String email);

    // Custom JPQL
    @Query("SELECT u FROM User u WHERE u.age >= :minAge ORDER BY u.name")
    Page<User> findAdults(@Param("minAge") int minAge, Pageable pageable);

    // Native SQL
    @Query(value = "SELECT * FROM users WHERE created_at > :since", nativeQuery = true)
    List<User> findRecentUsers(@Param("since") LocalDateTime since);

    // Modifying — for UPDATE/DELETE
    @Modifying
    @Transactional
    @Query("UPDATE User u SET u.isActive = false WHERE u.lastLogin < :cutoff")
    int deactivateInactiveUsers(@Param("cutoff") LocalDateTime cutoff);
}
```

---

### 2. How do derived query methods work?

**A:** Spring Data parses method names and generates queries automatically:

```java
public interface OrderRepository extends JpaRepository<Order, Long> {

    // findBy + field + condition
    List<Order> findByStatus(OrderStatus status);
    List<Order> findByStatusAndUserId(OrderStatus status, Long userId);

    // Comparison keywords
    List<Order> findByTotalGreaterThan(BigDecimal amount);
    List<Order> findByCreatedAtBetween(LocalDateTime from, LocalDateTime to);

    // String operations
    List<User> findByNameContainingIgnoreCase(String term);
    List<User> findByEmailStartingWith(String prefix);

    // Null checks
    List<Order> findByDeletedAtIsNull();
    List<Order> findByPromoCodeIsNotNull();

    // Sorting + limiting
    List<Order> findTop5ByUserIdOrderByCreatedAtDesc(Long userId);
    Optional<Order> findFirstByUserIdOrderByCreatedAtDesc(Long userId);

    // Boolean
    List<User> findByIsActiveTrue();

    // Count / Exists
    long countByStatus(OrderStatus status);
    boolean existsByEmail(String email);

    // Delete
    void deleteByStatus(OrderStatus status);
}
```

---

### 3. How does pagination and sorting work in Spring Data?

**A:**

```java
// Repository — add Pageable parameter
public interface UserRepository extends JpaRepository<User, Long> {
    Page<User> findByIsActive(boolean active, Pageable pageable);
}

// Service — create Pageable
Pageable pageable = PageRequest.of(
    0,                            // page number (0-based)
    20,                           // page size
    Sort.by("createdAt").descending()
        .and(Sort.by("name"))     // secondary sort
);

Page<User> page = repo.findByIsActive(true, pageable);

// Page contents
page.getContent();         // List<User>
page.getTotalElements();   // total count
page.getTotalPages();      // total pages
page.getNumber();          // current page
page.getSize();            // page size
page.hasNext();            // has next page
page.hasPrevious();        // has previous page

// Slice — cheaper (no COUNT query)
Slice<User> slice = repo.findAllBy(Pageable.ofSize(20));
slice.hasNext();  // just checks if another page exists

// Sort only (no pagination)
List<User> sorted = repo.findAll(Sort.by("name").ascending());
```

---

### 4. What are Spring Data projections?

**A:**

```java
// Interface projection — select subset of fields
interface UserSummary {
    Long getId();
    String getName();
    String getEmail();
    // Only these 3 columns fetched
}

List<UserSummary> summaries = repo.findByIsActive(true, UserSummary.class);

// DTO projection — constructor expression
public record UserDto(Long id, String name, String email) {}

@Query("SELECT NEW com.myapp.dto.UserDto(u.id, u.name, u.email) FROM User u WHERE u.isActive = true")
List<UserDto> findActiveDtos();

// Dynamic projection — caller chooses
<T> List<T> findByIsActive(boolean active, Class<T> type);

// Usage
List<UserSummary> summaries = repo.findByIsActive(true, UserSummary.class);
List<User> full = repo.findByIsActive(true, User.class);

// SpEL in interface projection
interface UserView {
    String getName();
    @Value("#{target.firstName + ' ' + target.lastName}")
    String getFullName();
}
```

---

## 🟡 Spring Data — Mid Level

---

### 5. What is the Specification pattern in Spring Data JPA?

**A:**

```java
// Enable: extend JpaSpecificationExecutor<T>
public interface UserRepository extends JpaRepository<User, Long>,
                                         JpaSpecificationExecutor<User> {}

// Define specifications — reusable query predicates
public class UserSpecs {

    public static Specification<User> isActive() {
        return (root, query, cb) -> cb.isTrue(root.get("isActive"));
    }

    public static Specification<User> hasRole(String role) {
        return (root, query, cb) -> cb.equal(root.get("role"), role);
    }

    public static Specification<User> nameContains(String term) {
        return (root, query, cb) ->
            term == null ? null : cb.like(cb.lower(root.get("name")), "%" + term.toLowerCase() + "%");
    }

    public static Specification<User> ageAtLeast(int minAge) {
        return (root, query, cb) -> cb.greaterThanOrEqualTo(root.get("age"), minAge);
    }
}

// Compose with and/or/not
Specification<User> spec = UserSpecs.isActive()
    .and(UserSpecs.hasRole("admin"))
    .and(UserSpecs.nameContains(searchTerm))
    .and(UserSpecs.ageAtLeast(18));

Page<User> result = repo.findAll(spec, PageRequest.of(0, 20));
```

---

### 6. How do you use Spring Data Redis?

**A:**

```java
// RedisTemplate — low-level, type-safe
@Configuration
public class RedisConfig {
    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory factory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(factory);
        template.setKeySerializer(new StringRedisSerializer());
        template.setValueSerializer(new GenericJackson2JsonRedisSerializer());
        return template;
    }
}

@Service
public class CacheService {
    @Autowired RedisTemplate<String, Object> redis;

    public void cacheUser(User user) {
        redis.opsForValue().set("user:" + user.getId(), user, Duration.ofMinutes(30));
    }

    public User getUser(Long id) {
        return (User) redis.opsForValue().get("user:" + id);
    }

    // Hash operations
    redis.opsForHash().put("session:" + sessionId, "userId", userId.toString());
    redis.opsForHash().get("session:" + sessionId, "userId");

    // List operations
    redis.opsForList().leftPush("queue", task);
    redis.opsForList().rightPop("queue");

    // Set operations
    redis.opsForSet().add("online:users", userId.toString());
    redis.opsForSet().isMember("online:users", userId.toString());
}

// Spring Cache abstraction — works with Redis
@Cacheable(value = "users", key = "#id")
public User findById(Long id) { return repo.findById(id).orElseThrow(); }

@CacheEvict(value = "users", key = "#user.id")
public User update(User user) { return repo.save(user); }

@CachePut(value = "users", key = "#result.id")
public User create(User user) { return repo.save(user); }
```

---

### 7. How do you use Spring Data MongoDB?

**A:**

```java
// Entity
@Document(collection = "orders")
public class Order {
    @Id String id;  // mapped to MongoDB _id
    String customerId;

    @DBRef
    Customer customer;  // reference to another document

    List<OrderItem> items;  // embedded documents

    @Indexed(expireAfterSeconds = 3600)  // TTL index
    LocalDateTime expiresAt;

    @CompoundIndex(def = "{'customerId': 1, 'status': 1}")
    String status;
}

// Repository
public interface OrderRepository extends MongoRepository<Order, String> {
    List<Order> findByCustomerIdAndStatus(String customerId, String status);

    @Query("{ 'items.productId': ?0, 'status': { $in: ?1 } }")
    List<Order> findByProductAndStatuses(String productId, List<String> statuses);
}

// MongoTemplate — complex aggregations
@Service
public class OrderStats {
    @Autowired MongoTemplate mongo;

    public List<Document> revenueByCategory() {
        return mongo.aggregate(
            Aggregation.newAggregation(
                Aggregation.match(Criteria.where("status").is("COMPLETED")),
                Aggregation.unwind("items"),
                Aggregation.group("items.category")
                    .sum("items.price").as("revenue")
                    .count().as("count"),
                Aggregation.sort(Sort.by("revenue").descending()),
                Aggregation.limit(10)
            ),
            "orders",
            Document.class
        ).getMappedResults();
    }
}
```

---

## 🟢 Spring Cloud — Junior Level

---

### 8. What is Spring Cloud and what problems does it solve?

**A:** Spring Cloud provides tools for building distributed systems and microservices:

| Problem | Spring Cloud Solution |
|---------|----------------------|
| Service discovery | Eureka (server + client) |
| Load balancing | Spring Cloud LoadBalancer |
| Configuration | Spring Cloud Config Server |
| API Gateway | Spring Cloud Gateway |
| Circuit breaker | Resilience4j integration |
| Inter-service HTTP | OpenFeign |
| Distributed tracing | Micrometer Tracing |

---

### 9. How do you implement service discovery with Eureka?

**A:**

```java
// Eureka Server
@SpringBootApplication
@EnableEurekaServer
public class ServiceRegistry { ... }

// application.yml (server)
server:
  port: 8761
eureka:
  client:
    register-with-eureka: false
    fetch-registry: false

// Eureka Client
@SpringBootApplication
@EnableDiscoveryClient
public class OrderService { ... }

// application.yml (client)
spring:
  application:
    name: order-service
eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/
  instance:
    prefer-ip-address: true
    health-check-url-path: /actuator/health
    lease-renewal-interval-in-seconds: 10

// Discover and call another service
@Service
public class InventoryClient {
    @Autowired DiscoveryClient discoveryClient;
    @Autowired RestTemplate restTemplate;  // must be @LoadBalanced

    public InventoryStatus check(String productId) {
        // Uses "inventory-service" name — resolved via Eureka
        return restTemplate.getForObject(
            "http://inventory-service/api/inventory/" + productId,
            InventoryStatus.class
        );
    }
}

@Bean
@LoadBalanced
public RestTemplate restTemplate() { return new RestTemplate(); }
```

---

### 10. How does OpenFeign work?

**A:**

```java
// Enable
@SpringBootApplication
@EnableFeignClients
public class OrderService { ... }

// Define client — just an interface
@FeignClient(
    name = "inventory-service",
    fallback = InventoryClientFallback.class
)
public interface InventoryClient {

    @GetMapping("/api/inventory/{productId}")
    InventoryStatus checkStock(@PathVariable String productId);

    @PostMapping("/api/inventory/reserve")
    ReservationResult reserve(@RequestBody ReservationRequest request);

    @GetMapping("/api/inventory")
    Page<InventoryItem> list(
        @RequestParam int page,
        @RequestParam int size,
        @RequestParam(required = false) String category
    );
}

// Fallback — circuit breaker fallback
@Component
public class InventoryClientFallback implements InventoryClient {
    public InventoryStatus checkStock(String productId) {
        return InventoryStatus.unknown(); // safe fallback
    }
    public ReservationResult reserve(ReservationRequest request) {
        throw new ServiceUnavailableException("Inventory service unavailable");
    }
}

// Inject and use like a local service
@Service
public class OrderService {
    @Autowired InventoryClient inventoryClient;

    public Order createOrder(CreateOrderRequest req) {
        InventoryStatus stock = inventoryClient.checkStock(req.getProductId());
        if (!stock.isAvailable()) throw new OutOfStockException();
        // ...
    }
}

// Custom configuration
@Configuration
public class FeignConfig {
    @Bean
    public RequestInterceptor authInterceptor() {
        return template -> template.header("Authorization", "Bearer " + getToken());
    }

    @Bean
    public Retryer feignRetryer() {
        return new Retryer.Default(100, 1000, 3); // 3 retries
    }
}
```

---

## 🟡 Spring Cloud — Mid Level

---

### 11. How do you set up Spring Cloud Config Server?

**A:**

```java
// Config Server
@SpringBootApplication
@EnableConfigServer
public class ConfigServer { ... }

// application.yml (server)
server:
  port: 8888
spring:
  cloud:
    config:
      server:
        git:
          uri: https://github.com/myorg/config-repo
          default-label: main
          search-paths: "{application}"
          clone-on-start: true
          username: ${GIT_USER}
          password: ${GIT_TOKEN}
```

```yaml
# Config repo structure:
# config-repo/
# ├── application.yml          # shared by all
# ├── order-service.yml        # service-specific defaults
# └── order-service-prod.yml   # prod overrides

# Client
spring:
  application:
    name: order-service
  config:
    import: optional:configserver:http://config-server:8888
  cloud:
    config:
      profile: ${SPRING_PROFILES_ACTIVE:dev}
      fail-fast: true          # fail startup if config server unreachable
      retry:
        max-attempts: 6
```

```java
// Refresh config at runtime without restart
@RefreshScope
@Service
public class FeatureService {
    @Value("${feature.new-checkout:false}")
    private boolean newCheckout;
}

// Trigger refresh via Actuator
// POST /actuator/refresh

// Or use Spring Cloud Bus to broadcast refresh to all instances
// POST /actuator/busrefresh
```

---

### 12. How does Spring Cloud Gateway work?

**A:**

```yaml
# application.yml
spring:
  cloud:
    gateway:
      routes:
        - id: order-service
          uri: lb://order-service    # lb = load balanced via service registry
          predicates:
            - Path=/api/orders/**
          filters:
            - StripPrefix=1          # removes /api from path
            - AddRequestHeader=X-Gateway-Source, spring-cloud-gateway
            - CircuitBreaker=name=orderCircuitBreaker,fallbackUri=/fallback/orders

        - id: auth-service
          uri: lb://auth-service
          predicates:
            - Path=/api/auth/**
            - Method=POST

      default-filters:
        - DedupeResponseHeader=Access-Control-Allow-Origin
        - name: Retry
          args:
            retries: 3
            statuses: BAD_GATEWAY,SERVICE_UNAVAILABLE

      globalcors:
        cors-configurations:
          '[/**]':
            allowed-origins: "https://myapp.com"
            allowed-methods: "*"
            allowed-headers: "*"
```

```java
// Custom filter
@Component
public class JwtAuthFilter implements GlobalFilter, Ordered {

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String token = exchange.getRequest().getHeaders().getFirst("Authorization");
        if (token == null) {
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }
        Claims claims = jwtService.validate(token);
        ServerHttpRequest request = exchange.getRequest().mutate()
            .header("X-User-Id", claims.getSubject())
            .build();
        return chain.filter(exchange.mutate().request(request).build());
    }

    @Override
    public int getOrder() { return -100; } // run early
}
```

---

## 🔴 Senior Level

---

### 13. How do you implement circuit breaking with Resilience4j in Spring Cloud?

**A:**

```java
// application.yml
resilience4j:
  circuitbreaker:
    instances:
      inventoryService:
        failure-rate-threshold: 50          # open at 50% failure
        slow-call-rate-threshold: 100       # slow call = > 2s
        slow-call-duration-threshold: 2s
        wait-duration-in-open-state: 30s
        permitted-number-of-calls-in-half-open-state: 5
        sliding-window-size: 20
  retry:
    instances:
      inventoryService:
        max-attempts: 3
        wait-duration: 500ms
        retry-exceptions:
          - java.io.IOException
          - feign.RetryableException
  timelimiter:
    instances:
      inventoryService:
        timeout-duration: 3s

// Usage on Feign client
@FeignClient(
    name = "inventory-service",
    configuration = FeignConfig.class
)
@CircuitBreaker(name = "inventoryService", fallbackMethod = "checkStockFallback")
@Retry(name = "inventoryService")
@TimeLimiter(name = "inventoryService")
public interface InventoryClient {
    CompletableFuture<InventoryStatus> checkStock(String productId);
}

// Fallback
public CompletableFuture<InventoryStatus> checkStockFallback(String productId, Exception ex) {
    log.warn("Inventory service unavailable: {}", ex.getMessage());
    return CompletableFuture.completedFuture(InventoryStatus.ASSUME_AVAILABLE);
}
```

---

### 14. How does distributed tracing work with Spring Cloud?

**A:**

```yaml
# application.yml
management:
  tracing:
    sampling:
      probability: 1.0  # 100% sampling (reduce in production: 0.1 = 10%)
  otlp:
    tracing:
      endpoint: http://otel-collector:4318/v1/traces

# Auto-instrumented: HTTP requests (in + out), JDBC, Kafka, Redis
# Trace context propagated via B3 headers (X-B3-TraceId, X-B3-SpanId)
```

```java
// Custom spans
@Autowired Tracer tracer;

@Service
public class OrderService {
    public Order processOrder(CreateOrderCmd cmd) {
        Span span = tracer.nextSpan().name("process-order");
        try (Tracer.SpanInScope ws = tracer.withSpan(span.start())) {
            span.tag("order.customer", cmd.getCustomerId());
            span.tag("order.items", String.valueOf(cmd.getItems().size()));

            Order order = createOrder(cmd);
            span.tag("order.id", order.getId().toString());
            return order;
        } catch (Exception e) {
            span.error(e);
            throw e;
        } finally {
            span.end();
        }
    }
}

// Include trace ID in logs
// Micrometer Tracing automatically adds traceId and spanId to MDC:
// {"traceId": "abc123", "spanId": "def456", "message": "Order created"}
```

---

## 🏛️ Architect Level

---

### 15. How do you design a Spring Cloud microservices system?

**A:**

**Service topology:**
```
[Browser / Mobile]
        ↓
[Spring Cloud Gateway]         ← auth, rate limiting, routing, CORS
        ↓
[Spring Security Resource Server (JWT)]
        ↓
[Order Service]  ←→  [OpenFeign]  →  [Inventory Service]
                                  →  [Payment Service]
        ↓
[Kafka events]  →  [Notification Service]
                →  [Analytics Service]
        ↓
[Spring Cloud Config Server]   ← shared configuration
[Eureka Server]                ← service registry
[Zipkin / Jaeger]              ← distributed tracing
[Prometheus + Grafana]         ← metrics
```

**Production configuration:**
```yaml
# Per service
spring:
  application:
    name: order-service
  config:
    import: configserver:http://config-server:8888
  datasource:
    hikari:
      maximum-pool-size: 20
      connection-timeout: 30000

management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  health:
    readiness-state:
      enabled: true
    liveness-state:
      enabled: true

server:
  shutdown: graceful
spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s
```

**Key design principles:**
- API Gateway is the only public entry point
- All inter-service calls via OpenFeign with circuit breakers
- Events for async decoupling (Kafka)
- Each service has its own DB — no shared schemas
- Config in Config Server; secrets from Vault/K8s Secrets
