# Spring Boot Interview Questions

Organized by seniority: Junior → Mid → Senior → Architect.
Each answer is concise but complete; expand during the interview as needed.

---

## 🟢 Junior Level

### 1. What is Spring Boot and how does it differ from the Spring Framework?

**A:** Spring Boot is an opinionated, convention-over-configuration layer on top of the Spring Framework. It eliminates boilerplate XML/Java config, provides embedded servers (Tomcat, Jetty, Undertow), and ships production-ready defaults via **starter dependencies** and **auto-configuration**.

| Spring Framework | Spring Boot |
|---|---|
| Manual bean wiring | Auto-configuration |
| External server (WAR) | Embedded server (JAR) |
| Explicit dependency versions | Curated BOM via `spring-boot-starter-*` |
| No built-in metrics/health | Actuator out of the box |

```java
// Minimal runnable Spring Boot application
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

---

### 2. What does `@SpringBootApplication` do?

**A:** It is a composed annotation that combines three annotations:

```java
@SpringBootConfiguration   // @Configuration — marks this as a config class
@EnableAutoConfiguration   // triggers Spring Boot's auto-configuration machinery
@ComponentScan             // scans the current package and sub-packages for beans
public @interface SpringBootApplication { ... }
```

You can customize exclusions:

```java
@SpringBootApplication(exclude = { DataSourceAutoConfiguration.class })
public class Application { ... }
```

---

### 3. What are the stereotype annotations and when do you use each?

**A:**

| Annotation | Semantic purpose | Extras |
|---|---|---|
| `@Component` | Generic Spring-managed bean | Base annotation |
| `@Service` | Business logic layer | No extra behaviour — semantic clarity |
| `@Repository` | Data-access layer | Wraps persistence exceptions → `DataAccessException` |
| `@Controller` | Spring MVC view controller | Returns view names |
| `@RestController` | REST API controller | `@Controller` + `@ResponseBody` |

```java
@Service
public class OrderService {
    private final OrderRepository repo;

    public OrderService(OrderRepository repo) {   // constructor injection (preferred)
        this.repo = repo;
    }
}

@Repository
public interface OrderRepository extends JpaRepository<Order, Long> { }
```

---

### 4. What are Spring Boot Starter dependencies?

**A:** Starters are convenience POMs that bundle a set of compatible dependency coordinates under a single artifact. They follow the naming pattern `spring-boot-starter-<feature>`.

```xml
<!-- Web: Spring MVC + embedded Tomcat + Jackson -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>

<!-- JPA: Hibernate + Spring Data + JDBC -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>

<!-- Testing: JUnit 5 + Mockito + MockMvc + AssertJ -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>
```

The `spring-boot-dependencies` BOM manages all version numbers — you never need to specify versions for managed starters.

---

### 5. How do you externalise configuration with `@Value` and `application.properties`?

**A:** `@Value` injects a single property using Spring's EL syntax.

```yaml
# application.yml
app:
  timeout: 5000
  name: "My Service"
```

```java
@Component
public class AppConfig {

    @Value("${app.timeout}")
    private int timeout;

    @Value("${app.name:default-name}")   // colon = default value
    private String name;
}
```

Prefer `@ConfigurationProperties` for structured config (see Q14).

---

### 6. What is Spring Boot Actuator?

**A:** Actuator exposes operational endpoints over HTTP (or JMX) for monitoring and management.

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,env,loggers
  endpoint:
    health:
      show-details: always
```

Key built-in endpoints:

| Endpoint | Purpose |
|---|---|
| `/actuator/health` | Liveness / readiness |
| `/actuator/metrics` | Micrometer metrics |
| `/actuator/env` | Environment properties |
| `/actuator/loggers` | Change log levels at runtime |
| `/actuator/threaddump` | JVM thread state |

---

### 7. How do you create a REST controller?

**A:**

```java
@RestController
@RequestMapping("/api/v1/products")
public class ProductController {

    private final ProductService service;

    public ProductController(ProductService service) {
        this.service = service;
    }

    @GetMapping("/{id}")
    public ResponseEntity<Product> getById(@PathVariable Long id) {
        return service.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<Product> create(@Valid @RequestBody ProductDto dto) {
        Product saved = service.create(dto);
        URI location = URI.create("/api/v1/products/" + saved.getId());
        return ResponseEntity.created(location).body(saved);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable Long id) {
        service.delete(id);
    }
}
```

---

### 8. How do Spring profiles work?

**A:** Profiles allow environment-specific configuration. Activate via:

- `application-{profile}.yml` files
- `spring.profiles.active` property
- `SPRING_PROFILES_ACTIVE` environment variable

```yaml
# application.yml (common)
spring:
  application:
    name: my-service

# application-dev.yml
spring:
  datasource:
    url: jdbc:h2:mem:testdb

# application-prod.yml
spring:
  datasource:
    url: jdbc:postgresql://prod-host:5432/mydb
```

```java
@Configuration
@Profile("prod")
public class ProdSecurityConfig {
    // only active in prod profile
}

@Bean
@Profile("!prod")   // active when NOT prod
public DataSource devDataSource() { ... }
```

Activate from command line:
```bash
java -jar app.jar --spring.profiles.active=prod
```

---

### 9. What is the Spring Bean lifecycle?

**A:** Beans go through a well-defined lifecycle managed by the `ApplicationContext`:

```
Instantiation → Property Injection → BeanNameAware → BeanFactoryAware →
ApplicationContextAware → @PostConstruct / afterPropertiesSet() →
[In use] → @PreDestroy / destroy()
```

```java
@Component
public class MyBean implements InitializingBean, DisposableBean {

    @PostConstruct                      // preferred — JSR-250
    public void init() {
        System.out.println("Bean ready");
    }

    @Override
    public void afterPropertiesSet() {  // InitializingBean — alternative
        // ...
    }

    @PreDestroy                         // preferred — JSR-250
    public void cleanup() {
        System.out.println("Bean destroyed");
    }

    @Override
    public void destroy() { }           // DisposableBean — alternative
}
```

You can also declare lifecycle methods in `@Bean`:
```java
@Bean(initMethod = "start", destroyMethod = "stop")
public ConnectionPool pool() { return new ConnectionPool(); }
```

---

### 10. What is `ResponseEntity` and when do you use it?

**A:** `ResponseEntity<T>` gives full control over the HTTP response — status code, headers, and body.

```java
// Return 201 Created with Location header
return ResponseEntity
    .created(URI.create("/orders/" + order.getId()))
    .header("X-Custom-Header", "value")
    .body(order);

// Conditional response
return exists
    ? ResponseEntity.ok(resource)
    : ResponseEntity.notFound().build();

// 204 No Content
return ResponseEntity.noContent().build();

// Custom status
return ResponseEntity.status(HttpStatus.ACCEPTED).body(dto);
```

Use it when you need to control status or headers. For simple happy-path returns, `@ResponseStatus` on the method is cleaner.

---

## 🔵 Mid Level

### 11. How does Spring Boot auto-configuration work internally?

**A:** Auto-configuration is driven by `@EnableAutoConfiguration`, which imports `AutoConfigurationImportSelector`. This class reads the list of candidate configuration classes from:

- **Spring Boot 2.x:** `META-INF/spring.factories` (key `EnableAutoConfiguration`)
- **Spring Boot 3.x:** `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`

Each candidate class is annotated with `@AutoConfiguration` (or `@Configuration`) and **conditional annotations** that gate it:

```java
@AutoConfiguration
@ConditionalOnClass(DataSource.class)               // classpath check
@ConditionalOnMissingBean(DataSource.class)         // only if user hasn't defined one
@ConditionalOnProperty(name = "spring.datasource.url") // property must exist
public class DataSourceAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public DataSource dataSource(DataSourceProperties props) {
        return DataSourceBuilder.create()
                .url(props.getUrl())
                .build();
    }
}
```

**Key conditionals:**

| Annotation | Condition |
|---|---|
| `@ConditionalOnClass` | Class present on classpath |
| `@ConditionalOnMissingBean` | No bean of that type defined by user |
| `@ConditionalOnProperty` | Property key/value matches |
| `@ConditionalOnWebApplication` | Running as a servlet/reactive web app |
| `@ConditionalOnResource` | Resource file exists |

Debug with `--debug` flag or `spring.autoconfigure.report=true` to see the **conditions report**.

---

### 12. Explain `@ConfigurationProperties` and its advantages over `@Value`.

**A:** `@ConfigurationProperties` binds a whole namespace of properties to a POJO, with type safety, validation, and IDE completion.

```yaml
# application.yml
mail:
  host: smtp.example.com
  port: 587
  username: user@example.com
  retry:
    max-attempts: 3
    delay-ms: 1000
```

```java
@ConfigurationProperties(prefix = "mail")
@Validated                          // enables JSR-303 validation
public class MailProperties {

    @NotBlank
    private String host;

    @Min(1) @Max(65535)
    private int port;

    private String username;
    private Retry retry = new Retry();  // nested object with defaults

    @Data
    public static class Retry {
        private int maxAttempts = 3;
        private long delayMs = 500;
    }
    // getters/setters or use @ConfigurationPropertiesScan + Lombok
}
```

Enable scanning (Spring Boot 2.2+):
```java
@SpringBootApplication
@ConfigurationPropertiesScan   // or @EnableConfigurationProperties(MailProperties.class)
public class Application { ... }
```

**Advantages over `@Value`:**

- Relaxed binding (`mail.max-attempts` = `mail.maxAttempts` = `MAIL_MAX_ATTEMPTS`)
- JSR-303 validation on the whole group
- IDE auto-completion with `spring-boot-configuration-processor`
- Immutable records supported (Spring Boot 2.6+)

---

### 13. How does exception handling work with `@ControllerAdvice` and `@ExceptionHandler`?

**A:**

```java
@RestControllerAdvice   // = @ControllerAdvice + @ResponseBody
public class GlobalExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ErrorResponse handleNotFound(ResourceNotFoundException ex,
                                        WebRequest request) {
        return new ErrorResponse(
            HttpStatus.NOT_FOUND.value(),
            ex.getMessage(),
            Instant.now()
        );
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ErrorResponse handleValidation(MethodArgumentNotValidException ex) {
        List<String> errors = ex.getBindingResult().getFieldErrors()
            .stream()
            .map(fe -> fe.getField() + ": " + fe.getDefaultMessage())
            .toList();
        return new ErrorResponse(400, "Validation failed", Instant.now(), errors);
    }

    @ExceptionHandler(Exception.class)           // catch-all
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ErrorResponse handleGeneric(Exception ex) {
        log.error("Unhandled exception", ex);
        return new ErrorResponse(500, "Internal error", Instant.now());
    }
}

// Error response DTO (use RFC 7807 ProblemDetail in Spring 6 / Boot 3)
public record ErrorResponse(int status, String message, Instant timestamp,
                             List<String> details) {
    public ErrorResponse(int status, String message, Instant timestamp) {
        this(status, message, timestamp, List.of());
    }
}
```

`@ControllerAdvice` can be scoped:
```java
@ControllerAdvice(basePackages = "com.example.orders")
@ControllerAdvice(assignableTypes = OrderController.class)
```

---

### 14. Explain `@Transactional` — propagation and isolation levels.

**A:**

**Propagation** controls what happens when a transactional method calls another:

| Propagation | Behaviour |
|---|---|
| `REQUIRED` *(default)* | Join existing tx; create new if none |
| `REQUIRES_NEW` | Always create a new tx; suspend current |
| `SUPPORTS` | Join if exists; non-tx if none |
| `NOT_SUPPORTED` | Always run non-tx; suspend existing |
| `MANDATORY` | Must have an existing tx; throw if none |
| `NEVER` | Must NOT have a tx; throw if one exists |
| `NESTED` | Savepoint within existing tx (rollback partial) |

**Isolation** controls visibility of concurrent transactions' data:

| Isolation | Dirty Read | Non-repeatable Read | Phantom Read |
|---|---|---|---|
| `READ_UNCOMMITTED` | ✅ possible | ✅ | ✅ |
| `READ_COMMITTED` *(most DBs default)* | ❌ | ✅ | ✅ |
| `REPEATABLE_READ` | ❌ | ❌ | ✅ |
| `SERIALIZABLE` | ❌ | ❌ | ❌ |

```java
@Service
@Transactional(readOnly = true)         // class-level default
public class OrderService {

    @Transactional                       // overrides to readOnly=false
    public Order placeOrder(OrderRequest req) {
        Order order = orderRepo.save(new Order(req));
        paymentService.charge(order);    // if this throws, order save rolls back
        return order;
    }

    @Transactional(
        propagation = Propagation.REQUIRES_NEW,
        isolation   = Isolation.SERIALIZABLE,
        timeout     = 30,
        rollbackFor = {PaymentException.class}
    )
    public void processPayment(Long orderId) { ... }
}
```

**Gotcha:** `@Transactional` uses a proxy — calling a transactional method *from within the same bean* bypasses the proxy and the transaction.

---

### 15. How does Spring Data JPA work? Explain repository abstraction, derived queries, and custom queries.

**A:**

```java
// 1. Extend a repository interface — Spring Data generates the implementation
public interface ProductRepository extends JpaRepository<Product, Long> {

    // 2. Derived query — method name is parsed into JPQL
    List<Product> findByCategory(String category);
    Optional<Product> findBySkuAndActiveTrue(String sku);
    List<Product> findByPriceBetweenOrderByPriceAsc(BigDecimal min, BigDecimal max);
    long countByCategory(String category);

    // 3. @Query — explicit JPQL
    @Query("SELECT p FROM Product p WHERE p.price < :maxPrice AND p.stock > 0")
    List<Product> findAffordableInStock(@Param("maxPrice") BigDecimal maxPrice);

    // 4. Native SQL
    @Query(value = "SELECT * FROM products WHERE category = ?1 LIMIT ?2",
           nativeQuery = true)
    List<Product> findTopByCategory(String category, int limit);

    // 5. Projections
    List<ProductSummary> findByCategory(String category, Class<ProductSummary> type);

    // 6. Modifying query
    @Modifying
    @Transactional
    @Query("UPDATE Product p SET p.price = p.price * :factor WHERE p.category = :cat")
    int adjustPriceByCategory(@Param("factor") BigDecimal factor,
                              @Param("cat") String cat);
}

// Projection interface
interface ProductSummary {
    String getName();
    BigDecimal getPrice();
}
```

---

### 16. How does pagination work with `Pageable`?

**A:**

```java
// Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    Page<Order> findByCustomerId(Long customerId, Pageable pageable);

    @Query("SELECT o FROM Order o WHERE o.status = :status")
    Slice<Order> findByStatus(@Param("status") OrderStatus status, Pageable pageable);
}

// Service
public Page<OrderDto> getCustomerOrders(Long customerId, int page, int size) {
    Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());
    return orderRepo.findByCustomerId(customerId, pageable)
                    .map(orderMapper::toDto);
}

// Controller — Spring MVC auto-resolves Pageable from request params
// GET /orders?page=0&size=20&sort=createdAt,desc
@GetMapping("/orders")
public Page<OrderDto> list(Pageable pageable) {
    return orderService.list(pageable);
}
```

- `Page<T>` — includes total element count (extra COUNT query)
- `Slice<T>` — only knows if there's a next page (lighter, no COUNT)

Configure defaults:
```java
@PageableDefault(size = 20, sort = "createdAt", direction = Sort.Direction.DESC)
```

---

### 17. How do `@Cacheable`, `@CacheEvict`, and `@CachePut` work?

**A:**

```yaml
# application.yml — using Caffeine (in-process)
spring:
  cache:
    type: caffeine
    caffeine:
      spec: maximumSize=1000,expireAfterWrite=10m
```

```java
@EnableCaching   // on @Configuration or @SpringBootApplication
```

```java
@Service
public class ProductService {

    // Cache the result; skip method if key already cached
    @Cacheable(value = "products", key = "#id",
               condition = "#id > 0",
               unless = "#result == null")
    public Product findById(Long id) {
        return repo.findById(id).orElse(null);   // DB hit only on cache miss
    }

    // Update the cache with the new value (always executes method)
    @CachePut(value = "products", key = "#result.id")
    public Product update(ProductDto dto) {
        return repo.save(mapper.toEntity(dto));
    }

    // Remove a specific entry
    @CacheEvict(value = "products", key = "#id")
    public void delete(Long id) {
        repo.deleteById(id);
    }

    // Evict everything in the cache
    @CacheEvict(value = "products", allEntries = true)
    public void clearAll() { }
}
```

For Redis-backed caching, swap the dependency and config:
```yaml
spring:
  cache:
    type: redis
  data:
    redis:
      host: localhost
      port: 6379
```

---

### 18. How does `@Async` work and what are its pitfalls?

**A:**

```java
@SpringBootApplication
@EnableAsync
public class Application { ... }

@Configuration
public class AsyncConfig implements AsyncConfigurer {

    @Override
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor exec = new ThreadPoolTaskExecutor();
        exec.setCorePoolSize(4);
        exec.setMaxPoolSize(10);
        exec.setQueueCapacity(500);
        exec.setThreadNamePrefix("async-");
        exec.initialize();
        return exec;
    }

    @Override
    public AsyncUncaughtExceptionHandler getAsyncUncaughtExceptionHandler() {
        return new SimpleAsyncUncaughtExceptionHandler();
    }
}

@Service
public class ReportService {

    @Async
    public CompletableFuture<Report> generateReport(Long id) {
        // runs in the thread pool, not the caller's thread
        Report report = heavyComputation(id);
        return CompletableFuture.completedFuture(report);
    }
}
```

**Pitfalls:**
1. Works via proxy — calling `@Async` method from *within the same bean* skips the async proxy.
2. `void` return type swallows exceptions unless you set `AsyncUncaughtExceptionHandler`.
3. `ThreadLocal` values (e.g., `SecurityContextHolder`) are not propagated automatically — use `DelegatingSecurityContextTaskExecutor`.
4. Without a custom executor, Spring uses `SimpleAsyncTaskExecutor` which creates a new thread per call (no pooling).

---

### 19. How does task scheduling work with `@Scheduled`?

**A:**

```java
@SpringBootApplication
@EnableScheduling
public class Application { ... }

@Component
public class DataSyncJob {

    // Fixed delay: 5s after last execution completes
    @Scheduled(fixedDelay = 5_000)
    public void syncFromPartner() { ... }

    // Fixed rate: every 10s regardless of execution time (can overlap)
    @Scheduled(fixedRate = 10_000)
    public void healthPing() { ... }

    // Cron: "seconds minutes hours day month weekday"
    @Scheduled(cron = "0 0 2 * * *")        // daily at 2 AM
    public void nightlyReport() { ... }

    // Property-driven cron (externalised)
    @Scheduled(cron = "${jobs.sync.cron:0 */15 * * * *}")
    public void configurableSync() { ... }
}
```

For distributed locking (avoid duplicate runs in a cluster), pair with **ShedLock** or **Quartz Scheduler**.

---

### 20. Explain Spring Boot testing layers: `@SpringBootTest`, `@WebMvcTest`, `@DataJpaTest`.

**A:**

```java
// ① Full application context — integration test
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class OrderIntegrationTest {

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    void placeOrder_returnsCreated() {
        ResponseEntity<OrderDto> resp = restTemplate.postForEntity(
            "/api/v1/orders", new OrderRequest(...), OrderDto.class);
        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.CREATED);
    }
}

// ② Slice — only web layer (Controllers, Filters, HandlerInterceptors)
@WebMvcTest(ProductController.class)
class ProductControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private ProductService productService;   // service is mocked out

    @Test
    void getProduct_returns200() throws Exception {
        given(productService.findById(1L)).willReturn(Optional.of(sampleProduct()));

        mockMvc.perform(get("/api/v1/products/1").accept(MediaType.APPLICATION_JSON))
               .andExpect(status().isOk())
               .andExpect(jsonPath("$.name").value("Widget"))
               .andDo(print());
    }
}

// ③ Slice — only JPA layer (repositories, entities, Flyway/Liquibase)
@DataJpaTest   // uses in-memory H2 by default
class OrderRepositoryTest {

    @Autowired
    private OrderRepository orderRepository;

    @Test
    void findByCustomerId_returnsMatchingOrders() {
        Order order = orderRepository.save(new Order(customerId: 42L));
        List<Order> found = orderRepository.findByCustomerId(42L);
        assertThat(found).hasSize(1).extracting(Order::getId).containsExactly(order.getId());
    }
}
```

| Annotation | Context scope | Speed |
|---|---|---|
| `@SpringBootTest` | Full context | Slow |
| `@WebMvcTest` | Web layer only | Fast |
| `@DataJpaTest` | JPA layer only | Fast |
| `@DataRedisTest` | Redis layer only | Fast |
| `@RestClientTest` | `RestTemplate`/`WebClient` + mock server | Fast |

---

## 🟠 Senior Level

### 21. How does Spring MVC content negotiation and `HttpMessageConverter` work?

**A:** Spring MVC selects the response format based on:

1. **`Accept` header** — `Accept: application/json` → `MappingJackson2HttpMessageConverter`
2. **URL extension** (deprecated) — `/product.xml`
3. **Request parameter** — `?format=xml`

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Override
    public void configureContentNegotiation(ContentNegotiationConfigurer configurer) {
        configurer
            .favorParameter(true)               // ?format=json
            .parameterName("format")
            .ignoreAcceptHeader(false)
            .defaultContentType(MediaType.APPLICATION_JSON)
            .mediaType("json", MediaType.APPLICATION_JSON)
            .mediaType("xml",  MediaType.APPLICATION_XML);
    }

    @Override
    public void extendMessageConverters(List<HttpMessageConverter<?>> converters) {
        // Add or reorder converters
        converters.add(0, new MappingJackson2HttpMessageConverter(customObjectMapper()));
    }
}
```

Custom converter example:
```java
public class CsvHttpMessageConverter extends AbstractHttpMessageConverter<List<?>> {

    public CsvHttpMessageConverter() {
        super(new MediaType("text", "csv"));
    }

    @Override
    protected void writeInternal(List<?> rows, HttpOutputMessage output) throws IOException {
        // write CSV rows to output.getBody()
    }
}
```

---

### 22. How does Spring WebFlux differ from Spring MVC? When would you choose it?

**A:** Spring WebFlux is Spring's reactive, non-blocking web stack built on **Project Reactor** (`Mono`/`Flux`) and Netty.

```java
// Spring MVC — one thread per request (blocking)
@GetMapping("/products/{id}")
public Product getProduct(@PathVariable Long id) {
    return productService.findById(id);   // thread blocked during DB I/O
}

// Spring WebFlux — reactive, non-blocking
@GetMapping("/products/{id}")
public Mono<Product> getProduct(@PathVariable Long id) {
    return productService.findById(id);   // returns immediately; Netty handles I/O
}

// Functional endpoint style (alternative to annotations)
@Bean
public RouterFunction<ServerResponse> routes(ProductHandler handler) {
    return RouterFunctions.route()
        .GET("/products/{id}", handler::getById)
        .POST("/products",     handler::create)
        .build();
}

@Component
public class ProductHandler {
    public Mono<ServerResponse> getById(ServerRequest req) {
        Long id = Long.parseLong(req.pathVariable("id"));
        return productService.findById(id)
            .flatMap(p  -> ServerResponse.ok().bodyValue(p))
            .switchIfEmpty(ServerResponse.notFound().build());
    }
}
```

**Choose WebFlux when:**
- I/O-bound workloads (many concurrent connections, streaming, SSE)
- Integrating with reactive data sources (R2DBC, Reactive MongoDB)
- Gateway/proxy pattern

**Stick with MVC when:**
- CPU-bound, CRUD applications
- Team unfamiliar with reactive paradigm
- Many blocking dependencies that can't be wrapped cheaply

---

### 23. How do you use `WebClient` and when does it replace `RestTemplate`?

**A:** `WebClient` is the non-blocking, reactive HTTP client. `RestTemplate` is in maintenance mode since Spring 5.

```java
@Configuration
public class WebClientConfig {

    @Bean
    public WebClient githubWebClient() {
        return WebClient.builder()
            .baseUrl("https://api.github.com")
            .defaultHeader(HttpHeaders.ACCEPT, MediaType.APPLICATION_JSON_VALUE)
            .defaultHeader(HttpHeaders.AUTHORIZATION, "Bearer " + token)
            .codecs(c -> c.defaultCodecs().maxInMemorySize(2 * 1024 * 1024))
            .filter(ExchangeFilterFunctions.statusError(
                HttpStatusCode::is4xxClientError,
                r -> Mono.error(new ClientException(r.statusCode()))))
            .build();
    }
}

@Service
public class GithubService {

    private final WebClient client;

    // Reactive usage
    public Mono<GithubUser> getUser(String username) {
        return client.get()
            .uri("/users/{username}", username)
            .retrieve()
            .onStatus(HttpStatus.NOT_FOUND::equals, r -> Mono.error(new UserNotFoundException()))
            .bodyToMono(GithubUser.class)
            .timeout(Duration.ofSeconds(5))
            .retryWhen(Retry.backoff(3, Duration.ofSeconds(1)));
    }

    // Blocking usage (in MVC context)
    public GithubUser getUserBlocking(String username) {
        return getUser(username).block();
    }

    // Stream of events
    public Flux<RepoEvent> streamEvents(String repo) {
        return client.get()
            .uri("/repos/{repo}/events", repo)
            .retrieve()
            .bodyToFlux(RepoEvent.class);
    }
}
```

---

### 24. Explain `ApplicationEvent` and the event listener mechanism.

**A:** Spring's event model decouples components via publish/subscribe.

```java
// 1. Define an event
public class OrderPlacedEvent extends ApplicationEvent {
    private final Order order;

    public OrderPlacedEvent(Object source, Order order) {
        super(source);
        this.order = order;
    }

    public Order getOrder() { return order; }
}

// Modern: use any POJO (no need to extend ApplicationEvent)
public record InvoiceRequestedEvent(Long orderId, String email) { }

// 2. Publish
@Service
public class OrderService {

    private final ApplicationEventPublisher publisher;

    public Order placeOrder(OrderRequest req) {
        Order order = orderRepo.save(new Order(req));
        publisher.publishEvent(new OrderPlacedEvent(this, order));
        publisher.publishEvent(new InvoiceRequestedEvent(order.getId(), req.email()));
        return order;
    }
}

// 3. Listen — synchronous by default
@Component
public class NotificationListener {

    @EventListener
    public void onOrderPlaced(OrderPlacedEvent event) {
        emailService.sendConfirmation(event.getOrder());
    }

    // Conditional
    @EventListener(condition = "#event.order.totalAmount > 1000")
    public void onHighValueOrder(OrderPlacedEvent event) { ... }

    // Async listener (requires @EnableAsync)
    @Async
    @EventListener
    public void onInvoiceRequested(InvoiceRequestedEvent event) {
        invoiceService.generate(event.orderId());
    }

    // Transactional — fire only after commit
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void afterCommit(OrderPlacedEvent event) {
        outboxService.enqueue(event);
    }
}
```

`@TransactionalEventListener` is key for the **Transactional Outbox pattern** — it guarantees the event is only processed if the originating transaction commits.

---

### 25. How do you implement custom Actuator health indicators and metrics?

**A:**

```java
// Custom HealthIndicator
@Component
public class ExternalApiHealthIndicator implements HealthIndicator {

    private final ExternalApiClient client;

    @Override
    public Health health() {
        try {
            boolean ok = client.ping();
            return ok
                ? Health.up().withDetail("api", "reachable").build()
                : Health.down().withDetail("api", "unreachable").build();
        } catch (Exception ex) {
            return Health.down(ex).withDetail("error", ex.getMessage()).build();
        }
    }
}

// Reactive health indicator (WebFlux)
@Component
public class ReactiveDbHealthIndicator implements ReactiveHealthIndicator {
    @Override
    public Mono<Health> health() {
        return reactiveRepo.count()
            .map(n -> Health.up().withDetail("count", n).build())
            .onErrorReturn(Health.down().build());
    }
}

// Custom metrics with Micrometer
@Component
public class OrderMetrics {

    private final Counter ordersPlaced;
    private final Timer  orderProcessingTime;
    private final AtomicLong activeOrders;

    public OrderMetrics(MeterRegistry registry) {
        this.ordersPlaced = Counter.builder("orders.placed")
            .tag("env", "prod")
            .description("Total orders placed")
            .register(registry);

        this.orderProcessingTime = Timer.builder("orders.processing.time")
            .publishPercentiles(0.5, 0.95, 0.99)
            .register(registry);

        this.activeOrders = registry.gauge(
            "orders.active", new AtomicLong(0));
    }

    public void recordOrderPlaced() {
        ordersPlaced.increment();
        activeOrders.incrementAndGet();
    }

    public <T> T timeProcessing(Supplier<T> task) {
        return orderProcessingTime.record(task);
    }
}
```

Metrics are auto-exported to Prometheus (`/actuator/prometheus`), Datadog, InfluxDB, etc. via Micrometer registry auto-configuration.

---

### 26. How do you write a `MockMvc` test with request/response verification?

**A:**

```java
@WebMvcTest(ProductController.class)
@Import(SecurityTestConfig.class)   // disable security or provide test config
class ProductControllerTest {

    @Autowired MockMvc mockMvc;
    @Autowired ObjectMapper objectMapper;
    @MockBean  ProductService productService;

    @Test
    void createProduct_withValidBody_returns201() throws Exception {
        ProductDto input = new ProductDto("Widget", new BigDecimal("9.99"));
        Product saved  = new Product(1L, "Widget", new BigDecimal("9.99"));

        given(productService.create(any())).willReturn(saved);

        mockMvc.perform(post("/api/v1/products")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(objectMapper.writeValueAsString(input)))
               .andExpect(status().isCreated())
               .andExpect(header().string("Location", containsString("/products/1")))
               .andExpect(jsonPath("$.id").value(1))
               .andExpect(jsonPath("$.name").value("Widget"))
               .andDo(print());
    }

    @Test
    void createProduct_withInvalidBody_returns400() throws Exception {
        mockMvc.perform(post("/api/v1/products")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content("{}"))          // missing required fields
               .andExpect(status().isBadRequest())
               .andExpect(jsonPath("$.errors").isArray());
    }
}
```

---

### 27. How does Spring Security integrate with Spring Boot at a high level?

**A:**

```java
// Spring Boot auto-configures a default SecurityFilterChain with form login
// Override it to customise:

@Configuration
@EnableWebSecurity
@EnableMethodSecurity   // enables @PreAuthorize, @Secured
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .csrf(AbstractHttpConfigurer::disable)          // REST APIs: stateless
            .sessionManagement(sm ->
                sm.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/v1/auth/**").permitAll()
                .requestMatchers("/actuator/health").permitAll()
                .requestMatchers(HttpMethod.GET, "/api/v1/products/**").hasRole("USER")
                .anyRequest().authenticated())
            .oauth2ResourceServer(oauth2 ->
                oauth2.jwt(jwt ->
                    jwt.jwtAuthenticationConverter(jwtAuthConverter())))
            .build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}

// Method security
@RestController
public class AdminController {

    @GetMapping("/admin/users")
    @PreAuthorize("hasRole('ADMIN')")
    public List<User> listUsers() { ... }

    @DeleteMapping("/admin/users/{id}")
    @PreAuthorize("hasRole('ADMIN') and #id != authentication.principal.id")
    public void deleteUser(@PathVariable Long id) { ... }
}
```

The `SecurityFilterChain` is a servlet filter chain sitting in front of the `DispatcherServlet`. Auto-configuration backs off completely as soon as you define your own `SecurityFilterChain` bean.

---

### 28. What is `@DataJpaTest` and how do you test with a real database (Testcontainers)?

**A:**

```java
// Default: replaces datasource with H2 in-memory
@DataJpaTest
class ProductRepositoryTest {

    @Autowired ProductRepository repo;
    @Autowired TestEntityManager em;

    @Test
    void findByCategoryOrderedByPrice() {
        em.persist(new Product("A", "TOOLS", new BigDecimal("5.00")));
        em.persist(new Product("B", "TOOLS", new BigDecimal("3.00")));
        em.flush();

        List<Product> tools = repo.findByCategoryOrderByPriceAsc("TOOLS");
        assertThat(tools).extracting(Product::getName).containsExactly("B", "A");
    }
}

// With Testcontainers — real PostgreSQL
@DataJpaTest
@AutoConfigureTestDatabase(replace = Replace.NONE)   // do NOT replace with H2
@Testcontainers
class ProductRepositoryPostgresTest {

    @Container
    static PostgreSQLContainer<?> postgres =
        new PostgreSQLContainer<>("postgres:16-alpine");

    @DynamicPropertySource
    static void overrideProps(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url",      postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired ProductRepository repo;

    @Test
    void canPersistAndRetrieve() {
        Product p = repo.save(new Product("Widget", "TOOLS", BigDecimal.TEN));
        assertThat(repo.findById(p.getId())).isPresent();
    }
}
```

---

## 🔴 Architect Level

### 29. How would you design a Spring Boot service for high-availability and observability?

**A:** A production-grade service combines several cross-cutting concerns:

```java
// 1. Structured logging with correlation IDs (MDC)
@Component
public class CorrelationIdFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest req,
                                    HttpServletResponse res,
                                    FilterChain chain) throws IOException, ServletException {
        String correlationId = Optional.ofNullable(req.getHeader("X-Correlation-ID"))
            .orElse(UUID.randomUUID().toString());
        MDC.put("correlationId", correlationId);
        res.addHeader("X-Correlation-ID", correlationId);
        try {
            chain.doFilter(req, res);
        } finally {
            MDC.clear();
        }
    }
}

// 2. Circuit breaker with Resilience4j
@Service
public class InventoryClient {

    @CircuitBreaker(name = "inventory", fallbackMethod = "inventoryFallback")
    @Retry(name = "inventory")
    @TimeLimiter(name = "inventory")
    public CompletableFuture<InventoryStatus> checkStock(Long productId) {
        return CompletableFuture.supplyAsync(() -> inventoryApi.getStatus(productId));
    }

    public CompletableFuture<InventoryStatus> inventoryFallback(Long id, Exception ex) {
        log.warn("Inventory circuit open for product {}: {}", id, ex.getMessage());
        return CompletableFuture.completedFuture(InventoryStatus.UNKNOWN);
    }
}

// 3. Distributed tracing — Micrometer Tracing (Brave/OTEL)
// auto-configured with spring-boot-starter-actuator + micrometer-tracing-bridge-otel
// adds traceId/spanId to MDC automatically

// 4. Graceful shutdown
// application.yml
server:
  shutdown: graceful
spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s
```

**Architecture pillars:**
- **Observability:** structured logs (JSON), distributed traces (OTEL), metrics (Micrometer → Prometheus)
- **Resilience:** circuit breaker, retry, timeout, bulkhead (Resilience4j)
- **Config:** externalized via Spring Cloud Config or Kubernetes ConfigMaps
- **Graceful degradation:** fallbacks, cache-aside for non-critical data
- **Health:** liveness vs readiness probes mapped to `/actuator/health/liveness` and `/actuator/health/readiness`

---

### 30. How does Spring Cloud Config work and how would you manage secrets?

**A:** Spring Cloud Config externalizes configuration across environments and services.

```yaml
# Config Server — application.yml
spring:
  cloud:
    config:
      server:
        git:
          uri: https://github.com/myorg/config-repo
          search-paths: "{application}"
          default-label: main
```

```java
// Config Server
@SpringBootApplication
@EnableConfigServer
public class ConfigServerApplication { ... }
```

```yaml
# Config Client — bootstrap.yml (or application.yml in Boot 2.4+)
spring:
  application:
    name: order-service
  config:
    import: "configserver:http://config-server:8888"
  cloud:
    config:
      fail-fast: true
      retry:
        max-attempts: 6
```

**Refresh without restart:**
```java
@RefreshScope    // bean rebuilt when /actuator/refresh is called
@RestController
public class FeatureFlagController {
    @Value("${features.newCheckout:false}")
    private boolean newCheckout;
}
```

**Secrets management strategy:**

| Layer | Tool |
|---|---|
| Local dev | `application-local.yml` (gitignored) |
| CI/CD | GitHub Actions secrets → env vars |
| Kubernetes | External Secrets Operator → K8s Secrets |
| Production | HashiCorp Vault / AWS Secrets Manager |

```yaml
# Spring Cloud Vault integration
spring:
  cloud:
    vault:
      uri: https://vault.company.com
      authentication: KUBERNETES
      kv:
        enabled: true
        backend: secret
        default-context: order-service
```

---

### 31. Explain Spring Boot's auto-configuration ordering and how to write your own starter.

**A:** Custom starters follow a precise structure:

```
my-feature-spring-boot-starter/        ← thin POM, depends on autoconfigure
my-feature-spring-boot-autoconfigure/  ← actual code
```

```java
// AutoConfiguration class
@AutoConfiguration
@ConditionalOnClass(MyFeatureClient.class)
@ConditionalOnProperty(prefix = "my.feature", name = "enabled", havingValue = "true",
                       matchIfMissing = true)
@EnableConfigurationProperties(MyFeatureProperties.class)
public class MyFeatureAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public MyFeatureClient myFeatureClient(MyFeatureProperties props) {
        return new MyFeatureClient(props.getApiKey(), props.getTimeout());
    }
}
```

```java
// Properties
@ConfigurationProperties(prefix = "my.feature")
public class MyFeatureProperties {
    private String apiKey;
    private Duration timeout = Duration.ofSeconds(5);
    // getters/setters
}
```

```
# Spring Boot 3.x: META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
com.mycompany.MyFeatureAutoConfiguration
```

**Ordering guarantees:**
```java
@AutoConfiguration(after = DataSourceAutoConfiguration.class)
@AutoConfigureBefore(HibernateJpaAutoConfiguration.class)
public class MyDataAutoConfiguration { ... }
```

Add `spring-boot-configuration-processor` to generate `META-INF/spring-configuration-metadata.json` for IDE completion.

---

### 32. How does Spring Integration fit into a Spring Boot application?

**A:** Spring Integration implements **Enterprise Integration Patterns (EEP)** — message channels, transformers, routers, filters, and adapters.

```java
@Configuration
@EnableIntegration
public class FileProcessingIntegration {

    // 1. Inbound adapter — poll a directory for new files
    @Bean
    public IntegrationFlow inboundFileFlow() {
        return IntegrationFlow
            .from(Files.inboundAdapter(new File("/data/incoming"))
                       .patternFilter("*.csv"),
                  e -> e.poller(Pollers.fixedDelay(5, TimeUnit.SECONDS)))
            .transform(Files.toStringTransformer())            // File → String
            .split(new FileSplitter())                         // split CSV lines
            .filter((String line) -> !line.startsWith("#"))    // skip comments
            .transform(csvLineToOrder())                       // String → Order
            .aggregate(aggregatorSpec -> aggregatorSpec
                .correlationExpression("payload.batchId")
                .releaseStrategy(g -> g.size() >= 100))        // batch of 100
            .handle(orderBatchHandler())                       // process batch
            .get();
    }

    // 2. Error handling channel
    @Bean
    public IntegrationFlow errorFlow() {
        return IntegrationFlow.from("errorChannel")
            .handle(m -> log.error("Integration error: {}", m.getPayload()))
            .get();
    }

    // 3. Gateway — synchronous API over an integration flow
    @MessagingGateway
    public interface OrderGateway {
        @Gateway(requestChannel = "orders.input")
        CompletableFuture<OrderResult> submit(Order order);
    }
}
```

Use Spring Integration for: file/FTP/S3 ingestion pipelines, message broker adapters (Kafka, RabbitMQ, JMS), ETL workflows.

---

### 33. What are the `@Transactional` proxy pitfalls and how do you solve them?

**A:**

**Pitfall 1: Self-invocation bypasses proxy**

```java
@Service
public class OrderService {

    @Transactional
    public void placeOrder() { ... }

    public void placeOrders(List<OrderRequest> reqs) {
        reqs.forEach(r -> placeOrder(r));   // ❌ no transaction — proxy bypassed
    }

    // Fix 1: inject self via @Autowired / @Lazy
    @Autowired
    private OrderService self;

    public void placeOrders(List<OrderRequest> reqs) {
        reqs.forEach(r -> self.placeOrder(r));  // ✅ goes through proxy
    }

    // Fix 2: extract to a separate bean (preferred — better design anyway)
}

// Fix 3: use AspectJ weaving (compile-time/load-time) — no proxy at all
```

**Pitfall 2: Exception type not triggering rollback**

```java
// @Transactional only rolls back on RuntimeException and Error by default
@Transactional(rollbackFor = Exception.class)   // also roll back on checked exceptions
public void riskyOp() throws IOException { ... }
```

**Pitfall 3: `REQUIRES_NEW` with same connection**

`REQUIRES_NEW` suspends the current tx and opens a new connection. If your DB pool is exhausted, deadlock. Size your pool accordingly or use asynchronous processing.

**Pitfall 4: `readOnly = true` performance**

`readOnly` hints to Hibernate to skip dirty checking and to the JDBC driver/DB to use a read replica. It does NOT prevent writes — just optimizes.

---

### 34. How do liveness and readiness probes map to Actuator endpoints in Kubernetes?

**A:** Spring Boot 2.3+ ships `LivenessStateHealthIndicator` and `ReadinessStateHealthIndicator` as first-class Actuator endpoints.

```yaml
# application.yml
management:
  endpoint:
    health:
      probes:
        enabled: true       # activates /actuator/health/liveness and /readiness
      show-details: always
  health:
    livenessstate:
      enabled: true
    readinessstate:
      enabled: true
```

```yaml
# Kubernetes Deployment
livenessProbe:
  httpGet:
    path: /actuator/health/liveness
    port: 8080
  initialDelaySeconds: 20
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /actuator/health/readiness
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 5
  failureThreshold: 2
```

```java
// Programmatic state change — e.g., drain before shutdown
@Component
public class WarmupListener {

    private final ApplicationContext ctx;

    @EventListener(ApplicationReadyEvent.class)
    public void onReady() {
        // Signal readiness after warm-up tasks complete
        AvailabilityChangeEvent.publish(ctx,
            ReadinessState.ACCEPTING_TRAFFIC);
    }

    @EventListener(ContextClosedEvent.class)
    public void onShutdown() {
        // Signal refusing traffic before graceful shutdown
        AvailabilityChangeEvent.publish(ctx,
            ReadinessState.REFUSING_TRAFFIC);
    }
}
```

**Semantic difference:**
- **Liveness** — is the JVM alive and not deadlocked? Failure → container restart.
- **Readiness** — is the app ready to serve traffic? Failure → removed from load balancer.

---

### 35. Explain the Spring Boot `ApplicationContext` hierarchy and how parent/child contexts interact.

**A:** Spring Boot typically creates a **single** `AnnotationConfigServletWebServerApplicationContext`. But in certain setups (Spring Cloud, multi-web-app deployments), you get a hierarchy:

```
BootstrapContext (Spring Cloud — resolves config server)
        ↓
  ParentContext (root — services, repositories, shared beans)
        ↓
  ChildContext  (web — controllers, filters, view resolvers)
```

**Rules:**
- Child can see parent beans, but NOT vice versa.
- `@Bean` definitions in child **shadow** parent beans of the same type.
- Each context has its own `BeanFactory` — `@Scope`, `@Transactional` proxies are per-context.

```java
// Programmatic parent-child wiring
AnnotationConfigApplicationContext parent = new AnnotationConfigApplicationContext();
parent.register(SharedConfig.class);
parent.refresh();

AnnotationConfigApplicationContext child = new AnnotationConfigApplicationContext();
child.setParent(parent);
child.register(WebConfig.class);
child.refresh();
```

**Context events fire bottom-up:** `ContextRefreshedEvent` fires in child first, then propagates to parent.

**Lazy initialization** (performance optimization):
```yaml
spring:
  main:
    lazy-initialization: true   # all beans lazy — reduces startup time
```

Individual override:
```java
@Bean
@Lazy(false)   // eager despite global lazy setting
public CriticalCache criticalCache() { ... }
```

---

### 36. How would you implement the Transactional Outbox pattern in Spring Boot?

**A:** The Outbox pattern guarantees at-least-once delivery of domain events by writing them to the same DB transaction as the business data, then relaying them asynchronously.

```java
// 1. Outbox table entity
@Entity
@Table(name = "outbox_events")
public class OutboxEvent {
    @Id @GeneratedValue
    private UUID id;
    private String aggregateType;   // "Order"
    private String aggregateId;
    private String eventType;       // "OrderPlaced"
    @Column(columnDefinition = "jsonb")
    private String payload;
    private Instant createdAt;
    private boolean published;
}

// 2. Write outbox entry in the same transaction as the business operation
@Service
@Transactional
public class OrderService {

    @TransactionalEventListener(phase = TransactionPhase.BEFORE_COMMIT)
    public void storeInOutbox(OrderPlacedEvent event) {
        OutboxEvent outbox = new OutboxEvent();
        outbox.setAggregateType("Order");
        outbox.setAggregateId(event.getOrder().getId().toString());
        outbox.setEventType("OrderPlaced");
        outbox.setPayload(objectMapper.writeValueAsString(event.getOrder()));
        outboxRepo.save(outbox);   // same transaction — atomic
    }
}

// 3. Relay poller — publishes unpublished events to Kafka/RabbitMQ
@Component
public class OutboxRelay {

    @Scheduled(fixedDelay = 1_000)
    @Transactional
    public void relay() {
        List<OutboxEvent> pending = outboxRepo.findTop100ByPublishedFalse();
        pending.forEach(event -> {
            kafkaTemplate.send(event.getEventType(), event.getPayload());
            event.setPublished(true);
        });
    }
}
```

For production, use **Debezium CDC** (Change Data Capture) on the outbox table instead of polling — it tails the PostgreSQL WAL and produces Kafka events with millisecond latency and no polling overhead.

---

### 37. How does Spring Boot handle circular dependencies and how should you resolve them?

**A:** Spring detects circular dependencies at startup and throws `BeanCurrentlyInCreationException` (with constructor injection) or silently creates incomplete beans (with field injection — dangerous).

```java
// ❌ Circular constructor injection — fails fast (correct behaviour)
@Service
public class A {
    public A(B b) { }   // A needs B
}
@Service
public class B {
    public B(A a) { }   // B needs A → circular!
}
```

**Resolution strategies (in order of preference):**

```java
// ✅ 1. Refactor — extract shared logic to a third service C
@Service public class C { /* shared logic */ }

// ✅ 2. Use @Lazy on one side — defer injection until first use
@Service
public class B {
    public B(@Lazy A a) { }
}

// ✅ 3. Setter/field injection to break the constructor cycle
@Service
public class B {
    @Autowired void setA(A a) { this.a = a; }
}

// ✅ 4. ApplicationContext.getBean() as last resort
```

In Spring Boot 2.6+, circular dependencies via field/setter injection are also **forbidden by default**:

```yaml
spring:
  main:
    allow-circular-references: false   # default in Boot 2.6+
```

Encountering a circular dependency is almost always a **design smell** — the two services belong in one, or they share a dependency that belongs in a third.

---

### 38. Describe the full request lifecycle in Spring MVC from socket to response.

**A:**

```
HTTP Request (TCP)
      ↓
Servlet Container (Tomcat) — NIO connector, thread pool
      ↓
FilterChain (SecurityFilter, CORSFilter, LoggingFilter, CorrelationIdFilter …)
      ↓
DispatcherServlet.service()
      ↓
HandlerMapping → resolves controller method (RequestMappingHandlerMapping)
      ↓
HandlerAdapter (selects RequestMappingHandlerAdapter)
      ↓
ArgumentResolvers (bind @PathVariable, @RequestBody, @RequestParam, Pageable …)
      → HttpMessageConverter reads request body (Jackson JSON → POJO)
      ↓
HandlerInterceptors.preHandle()
      ↓
Controller method executes
      ↓
HandlerInterceptors.postHandle()
      ↓
ReturnValueHandlers (e.g., ResponseEntityExceptionHandler)
      → HttpMessageConverter writes response body (POJO → JSON)
      ↓
HandlerInterceptors.afterCompletion()
      ↓
ExceptionHandlerExceptionResolver (if exception thrown — @ExceptionHandler / @ControllerAdvice)
      ↓
HTTP Response (status, headers, body)
```

Key extension points:

| Extension point | Purpose |
|---|---|
| `HandlerInterceptor` | Pre/post per-request logic (auth, logging) |
| `HandlerMethodArgumentResolver` | Bind custom types from request |
| `HttpMessageConverter` | Read/write custom media types |
| `ResponseBodyAdvice` | Wrap/modify response body globally |
| `@ControllerAdvice` | Global exception handling & model attributes |

---

## Quick Reference Cheat Sheet

| Topic | Key Annotations / Classes |
|---|---|
| Application bootstrap | `@SpringBootApplication`, `SpringApplication` |
| Auto-configuration | `@AutoConfiguration`, `@Conditional*`, `AutoConfigurationImportSelector` |
| Stereotype | `@Component`, `@Service`, `@Repository`, `@RestController` |
| Config binding | `@ConfigurationProperties`, `@Value`, `@Profile` |
| Web | `@RequestMapping`, `@GetMapping`, `ResponseEntity`, `@ControllerAdvice` |
| Reactive | `Mono`, `Flux`, `WebClient`, `RouterFunction`, `@EnableWebFlux` |
| Async / Scheduling | `@Async`, `@EnableAsync`, `@Scheduled`, `@EnableScheduling` |
| Events | `ApplicationEvent`, `@EventListener`, `@TransactionalEventListener` |
| Transactions | `@Transactional`, `Propagation.*`, `Isolation.*` |
| Data JPA | `JpaRepository`, `@Query`, `Pageable`, `Page`, `Slice` |
| Caching | `@Cacheable`, `@CacheEvict`, `@CachePut`, `@EnableCaching` |
| Actuator | `/actuator/health`, `HealthIndicator`, `MeterRegistry` |
| Security | `SecurityFilterChain`, `@EnableMethodSecurity`, `@PreAuthorize` |
| Cloud Config | `@EnableConfigServer`, `@RefreshScope`, `@DynamicPropertySource` |
| Testing | `@SpringBootTest`, `@WebMvcTest`, `@DataJpaTest`, `MockMvc`, `TestRestTemplate` |
