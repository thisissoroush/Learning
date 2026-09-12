# 🧪 Testing in Java — Interview Questions (Junior → Architect)

---

## 🟢 Junior Level

---

### 1. What is JUnit 5 and how do you write a basic test?

**A:**

```java
import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

class CalculatorTest {

    Calculator calculator; // no static — new instance per test

    @BeforeAll
    static void setUpClass() { System.out.println("Before all tests"); }

    @BeforeEach
    void setUp() { calculator = new Calculator(); }

    @AfterEach
    void tearDown() { /* cleanup */ }

    @AfterAll
    static void tearDownClass() { System.out.println("After all tests"); }

    @Test
    void testAdd() {
        assertEquals(5, calculator.add(2, 3));
        assertEquals(0, calculator.add(-1, 1));
    }

    @Test
    void testDivideByZero() {
        assertThrows(ArithmeticException.class, () -> calculator.divide(10, 0));
    }

    @Test
    @DisplayName("Subtract two positive numbers")
    void testSubtract() {
        assertAll(
            () -> assertEquals(2, calculator.subtract(5, 3)),
            () -> assertEquals(-2, calculator.subtract(3, 5)),
            () -> assertEquals(0, calculator.subtract(3, 3))
        );
    }

    @Test
    @Disabled("Not implemented yet")
    void testModulo() { }
}
```

---

### 2. What are the main JUnit 5 assertions?

**A:**

```java
// Basic assertions
assertEquals(expected, actual);
assertEquals(expected, actual, "message on failure");
assertNotEquals(unexpected, actual);
assertTrue(condition);
assertFalse(condition);
assertNull(obj);
assertNotNull(obj);

// Grouped assertions — all executed even if one fails
assertAll("address",
    () -> assertEquals("Paris", address.getCity()),
    () -> assertEquals("France", address.getCountry()),
    () -> assertNotNull(address.getZipCode())
);

// Exception assertions
Exception ex = assertThrows(IllegalArgumentException.class, () -> {
    new User(null, "email@test.com");
});
assertTrue(ex.getMessage().contains("name"));

// Timeout
assertTimeout(Duration.ofSeconds(1), () -> fastOperation());
assertTimeoutPreemptively(Duration.ofSeconds(1), () -> fastOperation());

// Array/collection
assertArrayEquals(new int[]{1, 2, 3}, result);
assertIterableEquals(List.of(1, 2, 3), resultList);
assertLinesMatch(List.of("line 1", "line 2"), actualLines);
```

---

### 3. What is Mockito and how do you mock dependencies?

**A:**

```java
import org.mockito.*;
import static org.mockito.Mockito.*;
import static org.mockito.ArgumentMatchers.*;

@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    UserRepository userRepo;

    @Mock
    EmailService emailService;

    @InjectMocks
    UserService userService; // injects mocks into constructor/fields

    @Test
    void shouldCreateUser() {
        // Arrange
        User user = new User("Alice", "alice@example.com");
        when(userRepo.save(any(User.class))).thenReturn(user);

        // Act
        User result = userService.create("Alice", "alice@example.com");

        // Assert
        assertEquals("Alice", result.getName());
        verify(userRepo).save(any(User.class));          // called once
        verify(emailService).sendWelcome("alice@example.com"); // called
        verifyNoMoreInteractions(emailService);
    }

    @Test
    void shouldThrowWhenEmailExists() {
        when(userRepo.findByEmail("alice@example.com"))
            .thenReturn(Optional.of(new User("Alice", "alice@example.com")));

        assertThrows(DuplicateEmailException.class,
            () -> userService.create("Alice", "alice@example.com"));

        verify(userRepo, never()).save(any());
    }
}
```

---

### 4. What is the AAA pattern in testing?

**A:** Arrange-Act-Assert — structure every test in three clear phases:

```java
@Test
void shouldCalculateOrderTotal() {
    // Arrange — set up test data and mocks
    Order order = new Order();
    order.addItem(new OrderItem("Widget", 10.00, 3)); // quantity 3
    order.addItem(new OrderItem("Gadget", 25.00, 1));

    // Act — execute the behavior being tested
    double total = order.calculateTotal();

    // Assert — verify the expected outcome
    assertEquals(55.00, total, 0.001);
}
```

---

### 5. What is parameterized testing in JUnit 5?

**A:**

```java
@ParameterizedTest
@ValueSource(strings = {"", " ", "\t", "\n"})
void shouldRejectBlankEmail(String blank) {
    assertThrows(IllegalArgumentException.class, () -> new User("Alice", blank));
}

@ParameterizedTest
@CsvSource({
    "Alice, 30, true",
    "Bob,   17, false",
    "Carol, 0,  false",
    "Dave,  18, true"
})
void testIsAdult(String name, int age, boolean expected) {
    assertEquals(expected, new User(name, age).isAdult());
}

@ParameterizedTest
@MethodSource("provideOrders")
void shouldCalculateTotal(List<OrderItem> items, double expectedTotal) {
    Order order = new Order(items);
    assertEquals(expectedTotal, order.total(), 0.01);
}

static Stream<Arguments> provideOrders() {
    return Stream.of(
        Arguments.of(List.of(new OrderItem("A", 10.0, 2)), 20.0),
        Arguments.of(List.of(new OrderItem("B", 5.0, 3)), 15.0),
        Arguments.of(Collections.emptyList(), 0.0)
    );
}
```

---

## 🟡 Mid Level

---

### 6. How do you use AssertJ for fluent assertions?

**A:**

```java
import static org.assertj.core.api.Assertions.*;

List<User> users = userService.findAll();

// Fluent, readable assertions
assertThat(users)
    .hasSize(3)
    .extracting(User::getName)
    .containsExactlyInAnyOrder("Alice", "Bob", "Charlie")
    .doesNotContain("Dave");

assertThat(user)
    .isNotNull()
    .hasFieldOrPropertyWithValue("name", "Alice")
    .hasFieldOrPropertyWithValue("age", 30);

assertThat(order.getTotal())
    .isPositive()
    .isGreaterThan(0.0)
    .isLessThanOrEqualTo(10000.0);

// Exception assertion
assertThatThrownBy(() -> userService.findById(-1))
    .isInstanceOf(IllegalArgumentException.class)
    .hasMessageContaining("invalid id")
    .hasNoCause();

// Soft assertions — collect all failures
SoftAssertions softly = new SoftAssertions();
softly.assertThat(user.getName()).isEqualTo("Alice");
softly.assertThat(user.getAge()).isEqualTo(30);
softly.assertAll(); // reports all failures at once
```

---

### 7. How do you test Spring MVC controllers with `MockMvc`?

**A:**

```java
@WebMvcTest(OrderController.class)  // loads only web layer
class OrderControllerTest {

    @Autowired MockMvc mockMvc;
    @MockBean OrderService orderService; // Spring-managed mock
    @Autowired ObjectMapper objectMapper;

    @Test
    void shouldReturnOrder() throws Exception {
        Order order = new Order(UUID.randomUUID(), "cust-1", BigDecimal.TEN);
        when(orderService.findById(any())).thenReturn(order);

        mockMvc.perform(get("/api/orders/{id}", order.getId())
                .header("Authorization", "Bearer " + validToken)
                .accept(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andExpect(content().contentType(MediaType.APPLICATION_JSON))
            .andExpect(jsonPath("$.id").value(order.getId().toString()))
            .andExpect(jsonPath("$.total").value(10.0))
            .andDo(print()); // print request/response for debugging
    }

    @Test
    void shouldReturn404WhenOrderNotFound() throws Exception {
        when(orderService.findById(any())).thenThrow(new OrderNotFoundException("not-found"));

        mockMvc.perform(get("/api/orders/{id}", "not-found"))
            .andExpect(status().isNotFound())
            .andExpect(jsonPath("$.message").exists());
    }

    @Test
    void shouldCreateOrder() throws Exception {
        CreateOrderRequest req = new CreateOrderRequest("cust-1", List.of(...));
        Order created = new Order(UUID.randomUUID(), "cust-1", BigDecimal.TEN);
        when(orderService.create(any())).thenReturn(created);

        mockMvc.perform(post("/api/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(req)))
            .andExpect(status().isCreated())
            .andExpect(header().exists("Location"));
    }
}
```

---

### 8. How do you test repositories with `@DataJpaTest`?

**A:**

```java
@DataJpaTest  // loads only JPA layer: entities, repositories, H2 in-memory by default
@AutoConfigureTestDatabase(replace = NONE) // use real DB (testcontainers)
@Testcontainers
class UserRepositoryTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired UserRepository repo;
    @Autowired TestEntityManager em; // for test setup

    @Test
    void shouldFindActiveUsersByAge() {
        // Arrange
        em.persist(new User("Alice", 30, true));
        em.persist(new User("Bob",   17, true));
        em.persist(new User("Carol", 30, false)); // inactive
        em.flush();

        // Act
        List<User> result = repo.findActiveUsersOlderThan(18);

        // Assert
        assertThat(result).hasSize(1)
            .extracting(User::getName)
            .containsOnly("Alice");
    }
}
```

---

### 9. How do you write integration tests with `@SpringBootTest`?

**A:**

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
class OrderIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    @Container
    static KafkaContainer kafka = new KafkaContainer(DockerImageName.parse("confluentinc/cp-kafka:7.4.0"));

    @DynamicPropertySource
    static void configure(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.kafka.bootstrap-servers", kafka::getBootstrapServers);
    }

    @Autowired TestRestTemplate restTemplate;
    @Autowired OrderRepository orderRepo;
    @Autowired KafkaTemplate<String, String> kafkaTemplate;

    @Test
    void shouldCreateOrderAndPublishEvent() {
        CreateOrderRequest req = new CreateOrderRequest("cust-1", List.of(new Item("p1", 2)));

        ResponseEntity<Order> response = restTemplate.postForEntity("/api/orders", req, Order.class);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(orderRepo.count()).isEqualTo(1);
        // Verify Kafka message was published...
    }
}
```

---

### 10. How do you test Kafka listeners?

**A:**

```java
@SpringBootTest
@EmbeddedKafka(partitions = 1, topics = {"orders", "orders.retry"})
class OrderListenerTest {

    @Autowired KafkaTemplate<String, String> kafkaTemplate;
    @Autowired OrderRepository repo;

    @Test
    void shouldProcessOrderEvent() throws Exception {
        String event = """
            {"orderId": "order-1", "customerId": "cust-1", "total": 99.99}
            """;

        kafkaTemplate.send("orders", "order-1", event);

        // Wait for async processing
        await().atMost(5, SECONDS)
               .untilAsserted(() -> assertThat(repo.findById("order-1")).isPresent());
    }
}
```

---

## 🔴 Senior Level

---

### 11. How do you implement test slices for different layers?

**A:**

```java
// @WebMvcTest  — Controller, Filter, HandlerMethodArgumentResolver
// @DataJpaTest — Repository, Entity, EntityManager
// @DataMongoTest — MongoDB repositories
// @DataRedisTest — Redis repositories
// @JsonTest    — JSON serialization/deserialization
// @RestClientTest — RestTemplate clients
// @SpringBootTest — full context (slow, use sparingly)

// Custom test slice
@JsonTest
class OrderSerializationTest {
    @Autowired JacksonTester<Order> json;

    @Test
    void shouldSerializeOrder() throws Exception {
        Order order = new Order("order-1", BigDecimal.TEN, OrderStatus.PENDING);

        assertThat(json.write(order))
            .hasJsonPathStringValue("$.id", "order-1")
            .hasJsonPathNumberValue("$.total", 10)
            .hasJsonPathStringValue("$.status", "PENDING")
            .doesNotHaveJsonPath("$.internalField"); // ensure no leaks
    }

    @Test
    void shouldDeserializeOrder() throws Exception {
        String content = """
            {"id": "order-1", "total": 10.0, "status": "PENDING"}
            """;
        assertThat(json.parse(content))
            .usingRecursiveComparison()
            .isEqualTo(new Order("order-1", BigDecimal.TEN, OrderStatus.PENDING));
    }
}
```

---

### 12. How do you use WireMock for stubbing external services?

**A:**

```java
@SpringBootTest(webEnvironment = RANDOM_PORT)
@AutoConfigureWireMock(port = 0) // random port, injected as wiremock.server.port
class PaymentClientTest {

    @Autowired PaymentClient paymentClient;

    @Test
    void shouldChargeSuccessfully() {
        stubFor(post(urlEqualTo("/charge"))
            .withHeader("Content-Type", equalTo("application/json"))
            .withRequestBody(matchingJsonPath("$.amount", equalTo("99.99")))
            .willReturn(aResponse()
                .withStatus(200)
                .withHeader("Content-Type", "application/json")
                .withBody("""
                    {"transactionId": "txn-123", "status": "SUCCESS"}
                    """)));

        PaymentResult result = paymentClient.charge(new ChargeRequest("99.99", "USD"));

        assertThat(result.getTransactionId()).isEqualTo("txn-123");
        assertThat(result.getStatus()).isEqualTo("SUCCESS");

        verify(postRequestedFor(urlEqualTo("/charge"))
            .withHeader("X-Api-Key", equalTo(expectedApiKey)));
    }

    @Test
    void shouldHandleTimeout() {
        stubFor(post(urlEqualTo("/charge"))
            .willReturn(aResponse().withFixedDelay(5000)));  // 5 second delay

        assertThatThrownBy(() -> paymentClient.charge(req))
            .isInstanceOf(PaymentTimeoutException.class);
    }
}
```

---

### 13. How do you test security configurations?

**A:**

```java
@WebMvcTest(OrderController.class)
@Import(SecurityConfig.class)
class OrderControllerSecurityTest {

    @Autowired MockMvc mockMvc;
    @MockBean OrderService service;

    @Test
    void shouldReturnUnauthorizedWhenNoToken() throws Exception {
        mockMvc.perform(get("/api/orders"))
            .andExpect(status().isUnauthorized());
    }

    @Test
    @WithMockUser(roles = "USER")
    void shouldAllowAuthenticatedUser() throws Exception {
        when(service.findAll()).thenReturn(Collections.emptyList());
        mockMvc.perform(get("/api/orders"))
            .andExpect(status().isOk());
    }

    @Test
    @WithMockUser(roles = "USER")
    void shouldForbidUserFromAdminEndpoint() throws Exception {
        mockMvc.perform(delete("/api/admin/orders/1"))
            .andExpect(status().isForbidden());
    }

    @Test
    @WithMockUser(roles = "ADMIN")
    void shouldAllowAdminToDelete() throws Exception {
        doNothing().when(service).delete(any());
        mockMvc.perform(delete("/api/admin/orders/1"))
            .andExpect(status().isNoContent());
    }
}
```

---

### 14. How do you measure and enforce test coverage with JaCoCo?

**A:**

```xml
<!-- pom.xml -->
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <executions>
        <execution>
            <id>prepare-agent</id>
            <goals><goal>prepare-agent</goal></goals>
        </execution>
        <execution>
            <id>report</id>
            <phase>test</phase>
            <goals><goal>report</goal></goals>
        </execution>
        <execution>
            <id>check</id>
            <goals><goal>check</goal></goals>
            <configuration>
                <rules>
                    <rule>
                        <element>BUNDLE</element>
                        <limits>
                            <limit>
                                <counter>LINE</counter>
                                <value>COVEREDRATIO</value>
                                <minimum>0.80</minimum> <!-- 80% line coverage -->
                            </limit>
                            <limit>
                                <counter>BRANCH</counter>
                                <value>COVEREDRATIO</value>
                                <minimum>0.70</minimum> <!-- 70% branch coverage -->
                            </limit>
                        </limits>
                    </rule>
                </rules>
                <excludes>
                    <exclude>**/*Application.class</exclude>
                    <exclude>**/dto/**</exclude>
                    <exclude>**/config/**</exclude>
                </excludes>
            </configuration>
        </execution>
    </executions>
</plugin>
```

```bash
mvn verify          # runs tests + coverage check
mvn jacoco:report   # generates HTML report at target/site/jacoco/
```

---

## 🏛️ Architect Level

---

### 15. How do you design a test strategy for a Java microservices system?

**A:**

**Test pyramid:**
```
          /\
         /E2E\          ← few, slow, fragile (Selenium, Playwright)
        /------\
       /Contract\       ← Pact consumer-driven contracts
      /----------\
     / Integration\     ← Testcontainers (real DB, Kafka, Redis)
    /--------------\
   /   Unit Tests   \   ← Many, fast, isolated (Mockito, JUnit 5)
  /------------------\
```

**Test types per layer:**
```java
// Unit — isolate domain logic with mocks
// Fast: milliseconds | Many: 70% of tests
@Test void orderTotalCalculation() { ... }

// Integration — real infrastructure
// Medium: seconds | Some: 20% of tests
@DataJpaTest @Testcontainers
void repositoryWithRealDB() { ... }

// Contract — consumer-driven (Pact)
// Medium: seconds | Per API boundary
@PactTestFor(providerName = "order-service")
void validateOrderContract() { ... }

// E2E — full stack in staging
// Slow: minutes | Few: 10% of tests
@Tag("e2e") void completeOrderFlow() { ... }
```

**Contract testing with Pact:**
```java
// Consumer defines expectations
@Pact(consumer = "web-frontend", provider = "order-service")
RequestResponsePact getOrderPact(PactDslWithProvider builder) {
    return builder
        .given("order 'ord-1' exists")
        .uponReceiving("get order")
        .path("/api/orders/ord-1")
        .method("GET")
        .willRespondWith()
        .status(200)
        .body(new PactDslJsonBody()
            .stringValue("id", "ord-1")
            .numberValue("total", 99.99))
        .toPact();
}

// Provider verifies
@Provider("order-service")
@PactBroker(host = "pact-broker.company.com")
class OrderServicePactVerificationTest {
    @TestTarget Target target = new HttpTarget(8080);
    @State("order 'ord-1' exists")
    void orderExists() { /* set up test data */ }
}
```
