# 🌱 Spring Core — Interview Questions (Junior → Architect)

Covers the Spring Framework foundation: IoC container, DI, AOP, bean lifecycle, SpEL, and Spring context.

---

## 🟢 Junior Level

---

### 1. What is the Spring IoC container and what problem does it solve?

**A:** IoC (Inversion of Control) is a design principle where object creation and dependency wiring is delegated to a container instead of being done by the objects themselves.

**Without IoC:**
```java
public class OrderService {
    // Tight coupling — creates its own dependencies
    private final UserRepository userRepo = new JdbcUserRepository(new DataSource(...));
    private final EmailService emailService = new SmtpEmailService("smtp.gmail.com", 587);
}
```

**With Spring IoC:**
```java
@Service
public class OrderService {
    // Spring provides (injects) the dependencies — loose coupling
    private final UserRepository userRepo;
    private final EmailService emailService;

    public OrderService(UserRepository userRepo, EmailService emailService) {
        this.userRepo = userRepo;
        this.emailService = emailService;
    }
}
```

Benefits: testability (swap implementations), loose coupling, lifecycle management, easier configuration.

---

### 2. What is the `ApplicationContext` and how does it differ from `BeanFactory`?

**A:**

| Feature | `BeanFactory` | `ApplicationContext` |
|---------|--------------|---------------------|
| Bean instantiation | Lazy (on first `getBean()`) | Eager (at startup) |
| Event publishing | No | Yes (`ApplicationEventPublisher`) |
| Internationalization | No | Yes (`MessageSource`) |
| `@Autowired` / `@Component` | No | Yes |
| AOP | Limited | Full |
| Use when | Resource-constrained envs | Always (Spring Boot) |

```java
// ApplicationContext implementations
AnnotationConfigApplicationContext ctx =
    new AnnotationConfigApplicationContext(AppConfig.class);

// Spring Boot — creates this automatically
// Access via @Autowired ApplicationContext ctx;
ctx.getBean(OrderService.class);
ctx.getBeanDefinitionNames();
ctx.publishEvent(new OrderCreatedEvent(orderId));
```

---

### 3. What are the Spring stereotype annotations?

**A:**

| Annotation | Purpose | Detected by |
|-----------|---------|-------------|
| `@Component` | Generic Spring-managed bean | Component scan |
| `@Service` | Business logic layer (semantics only) | Component scan |
| `@Repository` | Data access layer — translates SQL exceptions | Component scan |
| `@Controller` | Spring MVC web controller | Component scan |
| `@RestController` | `@Controller` + `@ResponseBody` | Component scan |
| `@Configuration` | Java config class, declares `@Bean`s | Component scan |

```java
@Service
public class UserService {
    private final UserRepository repo;
    public UserService(UserRepository repo) { this.repo = repo; }
}

@Repository
public class JpaUserRepository implements UserRepository {
    // DataAccessException translation applied automatically
}

@Configuration
public class AppConfig {
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(12);
    }
}
```

---

### 4. What are the three types of dependency injection?

**A:**

```java
@Service
public class OrderService {

    // 1. Constructor injection — PREFERRED
    // - Immutable, testable, mandatory dependencies explicit
    // - Spring recommends this (single constructor auto-wired)
    private final UserRepository userRepo;
    private final EmailService emailService;

    public OrderService(UserRepository userRepo, EmailService emailService) {
        this.userRepo = userRepo;
        this.emailService = emailService;
    }

    // 2. Setter injection — optional dependencies
    private NotificationService notificationService;

    @Autowired(required = false)
    public void setNotificationService(NotificationService ns) {
        this.notificationService = ns;
    }

    // 3. Field injection — AVOID in production code
    // - Not testable without Spring context
    // - Hides dependencies
    @Autowired
    private AuditService auditService; // bad practice
}
```

---

### 5. What are bean scopes in Spring?

**A:**

| Scope | Instances | Lifecycle |
|-------|-----------|-----------|
| `singleton` (default) | One per `ApplicationContext` | Lives as long as context |
| `prototype` | New per `getBean()` or injection point | Caller manages lifecycle |
| `request` | One per HTTP request | Web apps only |
| `session` | One per HTTP session | Web apps only |
| `application` | One per `ServletContext` | Web apps only |
| `websocket` | One per WebSocket session | Web apps only |

```java
@Component
@Scope("singleton")   // default — omit this annotation
public class CacheService { }

@Component
@Scope("prototype")   // new instance every time injected
public class ReportGenerator { }

// Injecting prototype into singleton — common pitfall!
@Service
public class OrderService {
    @Autowired
    private ApplicationContext ctx;

    public void process() {
        // Get fresh instance each time
        ReportGenerator gen = ctx.getBean(ReportGenerator.class);
        gen.generate();
    }
    // Or use @Lookup method injection / ObjectProvider<T>
}
```

---

### 6. What is `@Autowired` and how does Spring resolve ambiguity?

**A:**

```java
// Basic injection — by type
@Autowired
private PaymentService paymentService;

// Ambiguity when multiple implementations exist
@Service("stripePayment")
public class StripePaymentService implements PaymentService {}

@Service("paypalPayment")
public class PayPalPaymentService implements PaymentService {}

// Resolution options:
// 1. @Qualifier — specify by name
@Autowired
@Qualifier("stripePayment")
private PaymentService paymentService;

// 2. @Primary — mark preferred implementation
@Service @Primary
public class StripePaymentService implements PaymentService {}

// 3. Inject all implementations
@Autowired
private List<PaymentService> allPaymentServices;

@Autowired
private Map<String, PaymentService> paymentServiceMap;
// {"stripePayment": ..., "paypalPayment": ...}

// 4. @Resource — inject by name (JSR-250)
@Resource(name = "stripePayment")
private PaymentService paymentService;
```

---

### 7. What is component scanning and `@ComponentScan`?

**A:**

```java
// Enable scanning for @Component, @Service, @Repository, @Controller, etc.
@Configuration
@ComponentScan(
    basePackages = "com.myapp",
    excludeFilters = @ComponentScan.Filter(
        type = FilterType.ANNOTATION,
        classes = TestComponent.class
    )
)
public class AppConfig {}

// Spring Boot — @SpringBootApplication includes @ComponentScan
// Scans the package of the main class and all sub-packages

// Manually import beans not in scan path
@Configuration
@Import({ThirdPartyConfig.class, SecurityConfig.class})
public class AppConfig {}
```

---

### 8. What is the Spring bean lifecycle?

**A:**

```java
@Component
public class DatabasePool implements InitializingBean, DisposableBean {

    // 1. Instantiation — constructor called
    public DatabasePool() { System.out.println("1. Constructor"); }

    // 2. Populate properties — @Autowired fields injected
    @Autowired
    private DataSourceConfig config;

    // 3. BeanNameAware, BeanFactoryAware, ApplicationContextAware called

    // 4. BeanPostProcessor.postProcessBeforeInitialization()

    // 5. @PostConstruct — initialization
    @PostConstruct
    public void init() {
        System.out.println("5. @PostConstruct — init pool");
        openConnections();
    }

    // 6. InitializingBean.afterPropertiesSet() (or init-method)
    @Override
    public void afterPropertiesSet() {
        System.out.println("6. afterPropertiesSet");
    }

    // 7. BeanPostProcessor.postProcessAfterInitialization() — proxy wrapping

    // 8. Bean ready for use

    // 9. @PreDestroy — shutdown
    @PreDestroy
    public void shutdown() {
        System.out.println("9. @PreDestroy — closing connections");
        closeConnections();
    }

    // 10. DisposableBean.destroy()
    @Override
    public void destroy() {
        System.out.println("10. destroy");
    }
}
```

---

## 🟡 Mid Level

---

### 9. What is Spring AOP and how does it work?

**A:** AOP (Aspect-Oriented Programming) allows cross-cutting concerns (logging, security, transactions) to be modularized:

```java
// Aspect — cross-cutting concern
@Aspect
@Component
public class LoggingAspect {

    // Pointcut — where to apply
    @Pointcut("execution(* com.myapp.service.*.*(..))")
    private void serviceLayer() {}

    // Before advice — runs before method
    @Before("serviceLayer()")
    public void logBefore(JoinPoint jp) {
        log.info("Calling {}", jp.getSignature().getName());
    }

    // After returning — runs after successful return
    @AfterReturning(pointcut = "serviceLayer()", returning = "result")
    public void logAfter(JoinPoint jp, Object result) {
        log.info("Completed {} with result {}", jp.getSignature().getName(), result);
    }

    // After throwing
    @AfterThrowing(pointcut = "serviceLayer()", throwing = "ex")
    public void logException(JoinPoint jp, Exception ex) {
        log.error("Exception in {}: {}", jp.getSignature().getName(), ex.getMessage());
    }

    // Around — full control
    @Around("@annotation(Timed)")
    public Object measureTime(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.currentTimeMillis();
        try {
            return pjp.proceed();
        } finally {
            log.info("{} took {}ms", pjp.getSignature().getName(),
                System.currentTimeMillis() - start);
        }
    }
}

// Custom annotation for pointcut
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Timed {}
```

---

### 10. How does Spring AOP work under the hood (proxy mechanism)?

**A:** Spring AOP uses **dynamic proxies** — it wraps your bean in a proxy that intercepts calls:

```
[Caller] → [Proxy (JDK Dynamic or CGLIB)] → [Aspect code] → [Real bean]
```

- **JDK dynamic proxy** — used when bean implements an interface; proxies the interface
- **CGLIB proxy** — used when no interface; subclasses the concrete class (default in Spring Boot)

**Self-invocation problem:**
```java
@Service
public class OrderService {
    @Transactional
    public void createOrder(Order order) {
        // ...
        this.notifyUser(order); // PROBLEM: self-invocation bypasses proxy!
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void notifyUser(Order order) {
        // This runs in the SAME transaction — proxy not involved
    }
}

// Fix: inject self (ugly) or restructure to separate class
@Autowired
private OrderService self; // Spring injects the proxy

self.notifyUser(order); // now goes through proxy
```

---

### 11. What is Spring Expression Language (SpEL)?

**A:**

```java
// @Value with SpEL
@Value("${app.name}")                    // property placeholder
@Value("#{systemProperties['user.home']}") // SpEL system property
@Value("#{T(Math).PI}")                  // static method call
@Value("#{orderService.defaultDiscount * 100}") // bean property
@Value("#{someList.size() > 0 ? someList[0] : 'empty'}") // conditional

// In @Cacheable key expressions
@Cacheable(key = "#user.id + '_' + #order.status")
public List<Order> findOrders(User user, OrderStatus order) { ... }

// In @PreAuthorize (Spring Security)
@PreAuthorize("hasRole('ADMIN') or #userId == authentication.principal.id")
public User getUser(Long userId) { ... }

// In @ConditionalOnExpression
@ConditionalOnExpression("${feature.newCheckout:false} and '${env}' == 'production'")
public class NewCheckoutService { }

// Programmatic SpEL
ExpressionParser parser = new SpelExpressionParser();
Expression exp = parser.parseExpression("'Hello World'.toUpperCase()");
String result = exp.getValue(String.class); // "HELLO WORLD"
```

---

### 12. How does `@Conditional` and `@Profile` work?

**A:**

```java
// @Profile — activate beans for specific environments
@Configuration
@Profile("production")
public class ProductionConfig {
    @Bean DataSource dataSource() { return new HikariDataSource(prodSettings); }
}

@Configuration
@Profile("!production")  // not production
public class DevConfig {
    @Bean DataSource dataSource() { return new EmbeddedDatabaseBuilder().build(); }
}

// Activate: spring.profiles.active=production

// @ConditionalOnProperty — conditional on config
@Bean
@ConditionalOnProperty(name = "feature.email.enabled", havingValue = "true", matchIfMissing = false)
public EmailService emailService() { return new SmtpEmailService(); }

// @ConditionalOnClass — conditional on classpath
@Bean
@ConditionalOnClass(name = "com.amazonaws.services.s3.AmazonS3")
public StorageService s3Storage() { return new S3StorageService(); }

// @ConditionalOnMissingBean — if no other bean of this type
@Bean
@ConditionalOnMissingBean(PasswordEncoder.class)
public PasswordEncoder defaultPasswordEncoder() {
    return new BCryptPasswordEncoder();
}

// Custom condition
public class FeatureFlagCondition implements Condition {
    @Override
    public boolean matches(ConditionContext ctx, AnnotatedTypeMetadata metadata) {
        return "true".equals(ctx.getEnvironment().getProperty("feature.newCheckout"));
    }
}
@Conditional(FeatureFlagCondition.class)
public class NewCheckoutController { }
```

---

### 13. What is `BeanPostProcessor` and when do you implement it?

**A:**

```java
@Component
public class ValidatingBeanPostProcessor implements BeanPostProcessor {

    @Override
    public Object postProcessBeforeInitialization(Object bean, String beanName) throws BeansException {
        // Called before @PostConstruct — can replace the bean
        if (bean instanceof Configurable cfg && cfg.validate() == false) {
            throw new BeanCreationException(beanName, "Configuration invalid");
        }
        return bean; // return same bean or a wrapper
    }

    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName) throws BeansException {
        // Called after @PostConstruct — AOP proxy wrapping happens here
        if (bean.getClass().isAnnotationPresent(Audited.class)) {
            return Proxy.newProxyInstance(
                bean.getClass().getClassLoader(),
                bean.getClass().getInterfaces(),
                new AuditProxy(bean)
            );
        }
        return bean;
    }
}
```

Spring uses `BeanPostProcessor` internally for: `@Autowired` processing, `@Transactional` proxy creation, `@Async` proxy creation, and AOP advice weaving.

---

### 14. What is `ApplicationEvent` and how do you use the event system?

**A:**

```java
// Define event
public record OrderCreatedEvent(Long orderId, String customerId) {}

// Publish
@Service
public class OrderService {
    @Autowired ApplicationEventPublisher events;

    @Transactional
    public Order createOrder(CreateOrderCmd cmd) {
        Order order = orderRepo.save(new Order(cmd));
        events.publishEvent(new OrderCreatedEvent(order.getId(), cmd.getCustomerId()));
        return order;
    }
}

// Listen — synchronous (same thread, same transaction by default)
@Component
public class InventoryListener {
    @EventListener
    public void onOrderCreated(OrderCreatedEvent event) {
        inventoryService.reserve(event.orderId());
    }

    // Run AFTER transaction commits
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void sendConfirmationEmail(OrderCreatedEvent event) {
        emailService.sendOrderConfirmation(event.customerId());
    }

    // Async listener
    @EventListener
    @Async
    public void updateAnalytics(OrderCreatedEvent event) {
        analyticsService.record(event);
    }
}

// Ordered listeners
@EventListener
@Order(1)  // lower = higher priority
public void firstListener(OrderCreatedEvent event) {}

@EventListener
@Order(2)
public void secondListener(OrderCreatedEvent event) {}
```

---

## 🔴 Senior Level

---

### 15. How do Spring's `@Transactional` propagation levels work?

**A:**

```java
@Service
public class OrderService {
    @Autowired PaymentService paymentService;

    @Transactional(propagation = Propagation.REQUIRED)  // default
    // Join existing TX if present; create new TX if not
    public void processOrder(Order order) {
        orderRepo.save(order);
        paymentService.charge(order); // joins this transaction
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    // Always starts a NEW transaction; suspends existing one
    public void logAudit(AuditEntry entry) {
        auditRepo.save(entry); // independent TX — commits even if outer rolls back
    }

    @Transactional(propagation = Propagation.NESTED)
    // Savepoint within outer TX — rollback to savepoint on failure
    public void riskyOperation() {
        // If this fails, only this operation rolls back; outer TX continues
    }

    @Transactional(propagation = Propagation.SUPPORTS)
    // Use TX if present; run without if not
    public Order readOrder(Long id) { return orderRepo.findById(id).orElseThrow(); }

    @Transactional(propagation = Propagation.NOT_SUPPORTED)
    // Suspend current TX; run without TX
    public void fireAndForget() { ... }

    @Transactional(propagation = Propagation.NEVER)
    // Throw if called within a TX
    public void mustRunOutsideTransaction() { ... }

    @Transactional(propagation = Propagation.MANDATORY)
    // Throw if called WITHOUT a TX — must be in TX
    public void mustRunInTransaction() { ... }
}
```

---

### 16. How do you implement a custom Spring annotation with AOP?

**A:**

```java
// Define custom annotation
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface RateLimit {
    int requestsPerMinute() default 60;
    String key() default ""; // SpEL expression for key
}

// Implement the aspect
@Aspect
@Component
public class RateLimitAspect {
    @Autowired private RateLimiter rateLimiter;
    private final ExpressionParser parser = new SpelExpressionParser();

    @Around("@annotation(rateLimit)")
    public Object enforceRateLimit(ProceedingJoinPoint pjp, RateLimit rateLimit) throws Throwable {
        // Evaluate SpEL key expression
        String key = evaluateKey(rateLimit.key(), pjp);

        if (!rateLimiter.allowRequest(key, rateLimit.requestsPerMinute())) {
            throw new RateLimitExceededException("Rate limit exceeded for: " + key);
        }

        return pjp.proceed();
    }

    private String evaluateKey(String keyExpr, ProceedingJoinPoint pjp) {
        if (keyExpr.isEmpty()) return pjp.getSignature().toShortString();
        MethodSignature sig = (MethodSignature) pjp.getSignature();
        EvaluationContext ctx = new MethodBasedEvaluationContext(
            pjp.getTarget(), sig.getMethod(), pjp.getArgs(), new DefaultParameterNameDiscoverer()
        );
        return parser.parseExpression(keyExpr).getValue(ctx, String.class);
    }
}

// Usage
@RateLimit(requestsPerMinute = 10, key = "#userId")
public OrderResponse createOrder(String userId, CreateOrderRequest req) { ... }
```

---

### 17. What is `FactoryBean` and when do you use it?

**A:**

```java
// FactoryBean<T> — creates complex objects that can't be declared as @Bean easily
public class ConnectionPoolFactoryBean implements FactoryBean<ConnectionPool> {

    private String jdbcUrl;
    private int poolSize = 10;

    @Override
    public ConnectionPool getObject() throws Exception {
        // Complex initialization
        ConnectionPool pool = new ConnectionPool();
        pool.setJdbcUrl(jdbcUrl);
        pool.setPoolSize(poolSize);
        pool.initialize(); // blocking initialization
        return pool;
    }

    @Override
    public Class<?> getObjectType() { return ConnectionPool.class; }

    @Override
    public boolean isSingleton() { return true; }
}

// Register
@Bean
public ConnectionPoolFactoryBean connectionPool() {
    ConnectionPoolFactoryBean factory = new ConnectionPoolFactoryBean();
    factory.setJdbcUrl("jdbc:postgresql://localhost/mydb");
    factory.setPoolSize(20);
    return factory;
}

// Inject — Spring injects the ConnectionPool, not the FactoryBean
@Autowired
ConnectionPool pool;

// To get the FactoryBean itself: use "&" prefix
@Autowired
@Qualifier("&connectionPool")
ConnectionPoolFactoryBean factory;
```

---

## 🏛️ Architect Level

---

### 18. How do you design a modular Spring application?

**A:**

```java
// Separate modules — each with its own @Configuration
// order-module/src/main/java/com/myapp/order/OrderModuleConfig.java
@Configuration
@ComponentScan(basePackages = "com.myapp.order")
@Import(PersistenceConfig.class)
public class OrderModuleConfig {
    @Bean
    public OrderService orderService(OrderRepository repo, DomainEventPublisher events) {
        return new OrderService(repo, events);
    }
}

// inventory-module — decoupled, communicates via events or interfaces
@Configuration
@ComponentScan("com.myapp.inventory")
public class InventoryModuleConfig { }

// Root config — composes modules
@Configuration
@Import({OrderModuleConfig.class, InventoryModuleConfig.class, SecurityConfig.class})
public class RootConfig { }

// Module contract — define interfaces in a shared API module
// order-api/src/main/java/com/myapp/order/api/OrderService.java
public interface OrderService {
    Order createOrder(CreateOrderCommand cmd);
    Optional<Order> findById(UUID id);
}
// Implementations in order-impl, unknown to other modules
```

---

### 19. How does Spring handle circular dependencies and how do you fix them?

**A:**

```java
// Circular dependency — Spring throws BeanCurrentlyInCreationException
// ServiceA → ServiceB → ServiceA (constructor injection — fatal)

// Fix 1: Restructure — extract shared logic to a third service
@Service class ServiceC { /* shared logic */ }
@Service class ServiceA { public ServiceA(ServiceC c) {} }
@Service class ServiceB { public ServiceB(ServiceC c) {} }

// Fix 2: @Lazy — breaks the cycle at injection time
@Service
public class ServiceA {
    public ServiceA(@Lazy ServiceB b) { } // ServiceB created on first use
}

// Fix 3: Setter injection — cycle allowed (Spring uses proxy placeholder)
@Service
public class ServiceA {
    private ServiceB serviceB;
    @Autowired
    public void setServiceB(ServiceB b) { this.serviceB = b; }
}

// Fix 4: ApplicationContext.getBean() — lookup on demand (least preferred)
@Service
public class ServiceA {
    @Autowired ApplicationContext ctx;
    public void doWork() {
        ctx.getBean(ServiceB.class).operate(); // lazy lookup
    }
}
```

Circular dependencies usually indicate a design problem — prefer Fix 1.

---

### 20. How do you test Spring components in isolation?

**A:**

```java
// Unit test — no Spring context
class OrderServiceTest {
    @Mock UserRepository userRepo;
    @Mock EmailService emailService;
    @InjectMocks OrderService orderService;

    @BeforeEach void setUp() { MockitoAnnotations.openMocks(this); }

    @Test
    void shouldCreateOrder() {
        when(userRepo.findById(1L)).thenReturn(Optional.of(new User("Alice")));
        Order result = orderService.create(new CreateOrderCmd(1L, List.of(...)));
        assertThat(result).isNotNull();
        verify(emailService).sendConfirmation(any());
    }
}

// Integration test — partial context
@SpringJUnitConfig(classes = {OrderService.class, OrderServiceConfig.class})
class OrderServiceIntegrationTest {
    @Autowired OrderService orderService;
    @MockBean UserRepository userRepo; // Spring mock in context

    @Test void contextLoads() { assertNotNull(orderService); }
}

// AOP test — verify aspect is applied
@SpringBootTest
class RateLimitAspectTest {
    @Autowired OrderController controller;

    @Test
    void shouldThrowRateLimitExceeded() {
        // Call 61 times — 61st should fail
        for (int i = 0; i < 60; i++) controller.createOrder(req);
        assertThrows(RateLimitExceededException.class, () -> controller.createOrder(req));
    }
}
```
