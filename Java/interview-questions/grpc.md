# 📡 gRPC in Java — Interview Questions (Junior → Architect)

---

## 🟢 Junior Level

---

### 1. How do you set up gRPC in a Java project?

**A:**

```xml
<!-- pom.xml -->
<dependencies>
    <dependency>
        <groupId>io.grpc</groupId>
        <artifactId>grpc-netty-shaded</artifactId>
        <version>1.60.0</version>
    </dependency>
    <dependency>
        <groupId>io.grpc</groupId>
        <artifactId>grpc-protobuf</artifactId>
        <version>1.60.0</version>
    </dependency>
    <dependency>
        <groupId>io.grpc</groupId>
        <artifactId>grpc-stub</artifactId>
        <version>1.60.0</version>
    </dependency>
</dependencies>

<build>
    <extensions>
        <extension>
            <groupId>kr.motd.maven</groupId>
            <artifactId>os-maven-plugin</artifactId>
            <version>1.7.1</version>
        </extension>
    </extensions>
    <plugins>
        <plugin>
            <groupId>org.xolstice.maven.plugins</groupId>
            <artifactId>protobuf-maven-plugin</artifactId>
            <configuration>
                <protocArtifact>com.google.protobuf:protoc:3.25.1:exe:${os.detected.classifier}</protocArtifact>
                <pluginId>grpc-java</pluginId>
                <pluginArtifact>io.grpc:protoc-gen-grpc-java:1.60.0:exe:${os.detected.classifier}</pluginArtifact>
            </configuration>
            <executions>
                <execution>
                    <goals>
                        <goal>compile</goal>
                        <goal>compile-custom</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

---

### 2. How do you implement a gRPC server in Java?

**A:**

```java
// Service implementation
public class OrderServiceImpl extends OrderServiceGrpc.OrderServiceImplBase {

    private final OrderRepository repo;

    public OrderServiceImpl(OrderRepository repo) {
        this.repo = repo;
    }

    @Override
    public void getOrder(GetOrderRequest request, StreamObserver<Order> responseObserver) {
        try {
            Order order = repo.findById(request.getId())
                .map(this::toProto)
                .orElseThrow(() -> new OrderNotFoundException(request.getId()));

            responseObserver.onNext(order);
            responseObserver.onCompleted();
        } catch (OrderNotFoundException e) {
            responseObserver.onError(
                Status.NOT_FOUND.withDescription(e.getMessage()).asRuntimeException());
        } catch (Exception e) {
            responseObserver.onError(
                Status.INTERNAL.withDescription("Internal error").withCause(e).asRuntimeException());
        }
    }

    @Override
    public void createOrder(CreateOrderRequest request, StreamObserver<Order> responseObserver) {
        if (request.getItemsList().isEmpty()) {
            responseObserver.onError(
                Status.INVALID_ARGUMENT.withDescription("items cannot be empty").asRuntimeException());
            return;
        }
        // ... create order
    }
}

// Start server
public class GrpcServer {
    public static void main(String[] args) throws Exception {
        Server server = ServerBuilder.forPort(50051)
            .addService(new OrderServiceImpl(repo))
            .addService(ProtoReflectionService.newInstance()) // for grpcurl
            .intercept(new AuthInterceptor())
            .build()
            .start();

        Runtime.getRuntime().addShutdownHook(new Thread(server::shutdown));
        server.awaitTermination();
    }
}
```

---

### 3. How do you implement a gRPC client in Java?

**A:**

```java
// Blocking stub — synchronous
ManagedChannel channel = ManagedChannelBuilder
    .forAddress("order-service", 50051)
    .usePlaintext() // dev only; use TLS in prod
    .build();

OrderServiceGrpc.OrderServiceBlockingStub blockingStub =
    OrderServiceGrpc.newBlockingStub(channel);

// Async stub — non-blocking
OrderServiceGrpc.OrderServiceStub asyncStub =
    OrderServiceGrpc.newStub(channel);

// Future stub — returns ListenableFuture
OrderServiceGrpc.OrderServiceFutureStub futureStub =
    OrderServiceGrpc.newFutureStub(channel);

// Synchronous call
try {
    Order order = blockingStub
        .withDeadlineAfter(5, TimeUnit.SECONDS)
        .getOrder(GetOrderRequest.newBuilder().setId("order-1").build());
    System.out.println(order.getTotal());
} catch (StatusRuntimeException e) {
    if (e.getStatus().getCode() == Status.Code.NOT_FOUND) {
        System.out.println("Order not found");
    }
}

// Async call
asyncStub.getOrder(request, new StreamObserver<Order>() {
    @Override public void onNext(Order value) { process(value); }
    @Override public void onError(Throwable t) { handleError(t); }
    @Override public void onCompleted() { done(); }
});

// Cleanup
channel.shutdown().awaitTermination(5, TimeUnit.SECONDS);
```

---

### 4. How do you implement streaming in Java gRPC?

**A:**

```java
// Server-side streaming
@Override
public void watchOrders(WatchRequest request, StreamObserver<Order> responseObserver) {
    while (!Thread.currentThread().isInterrupted()) {
        Order latestOrder = pollForUpdates(request.getCustomerId());
        if (latestOrder != null) {
            responseObserver.onNext(latestOrder);
        }
        try { Thread.sleep(1000); }
        catch (InterruptedException e) {
            break;
        }
    }
    responseObserver.onCompleted();
}

// Client-side streaming
@Override
public StreamObserver<OrderItem> uploadItems(StreamObserver<UploadSummary> responseObserver) {
    List<OrderItem> collected = new ArrayList<>();
    return new StreamObserver<>() {
        @Override public void onNext(OrderItem item) { collected.add(item); }
        @Override public void onError(Throwable t) { /* handle */ }
        @Override public void onCompleted() {
            processItems(collected);
            responseObserver.onNext(UploadSummary.newBuilder()
                .setItemCount(collected.size()).build());
            responseObserver.onCompleted();
        }
    };
}

// Bidirectional streaming
@Override
public StreamObserver<ChatMessage> chat(StreamObserver<ChatMessage> responseObserver) {
    return new StreamObserver<>() {
        @Override public void onNext(ChatMessage msg) {
            responseObserver.onNext(ChatMessage.newBuilder()
                .setText("Echo: " + msg.getText()).build());
        }
        @Override public void onError(Throwable t) { }
        @Override public void onCompleted() { responseObserver.onCompleted(); }
    };
}
```

---

## 🟡 Mid Level

---

### 5. How do you implement server interceptors in Java gRPC?

**A:**

```java
// Authentication interceptor
public class AuthInterceptor implements ServerInterceptor {

    static final Metadata.Key<String> AUTH_HEADER =
        Metadata.Key.of("Authorization", ASCII_STRING_MARSHALLER);
    static final Context.Key<String> USER_ID_KEY = Context.key("userId");

    @Override
    public <ReqT, RespT> ServerCall.Listener<ReqT> interceptCall(
        ServerCall<ReqT, RespT> call,
        Metadata headers,
        ServerCallHandler<ReqT, RespT> next)
    {
        String token = headers.get(AUTH_HEADER);
        if (token == null || !token.startsWith("Bearer ")) {
            call.close(Status.UNAUTHENTICATED.withDescription("Missing token"), new Metadata());
            return new ServerCall.Listener<>() {};
        }

        try {
            String userId = validateToken(token.substring(7));
            Context ctx = Context.current().withValue(USER_ID_KEY, userId);
            return Contexts.interceptCall(ctx, call, headers, next);
        } catch (Exception e) {
            call.close(Status.UNAUTHENTICATED.withDescription("Invalid token"), new Metadata());
            return new ServerCall.Listener<>() {};
        }
    }
}

// Logging interceptor
public class LoggingInterceptor implements ServerInterceptor {
    @Override
    public <ReqT, RespT> ServerCall.Listener<ReqT> interceptCall(
        ServerCall<ReqT, RespT> call, Metadata headers, ServerCallHandler<ReqT, RespT> next)
    {
        long start = System.currentTimeMillis();
        String method = call.getMethodDescriptor().getFullMethodName();

        ServerCall<ReqT, RespT> loggingCall = new ForwardingServerCall.SimpleForwardingServerCall<>(call) {
            @Override public void close(Status status, Metadata trailers) {
                log.info("RPC {} duration={}ms status={}",
                    method, System.currentTimeMillis() - start, status.getCode());
                super.close(status, trailers);
            }
        };
        return next.startCall(loggingCall, headers);
    }
}

// Register
Server server = ServerBuilder.forPort(50051)
    .addService(new OrderServiceImpl())
    .intercept(new LoggingInterceptor()) // last added = first executed
    .intercept(new AuthInterceptor())
    .build();
```

---

### 6. How do you integrate gRPC with Spring Boot?

**A:**

```xml
<!-- grpc-spring-boot-starter -->
<dependency>
    <groupId>net.devh</groupId>
    <artifactId>grpc-server-spring-boot-starter</artifactId>
    <version>2.15.0.RELEASE</version>
</dependency>
```

```java
// Server — just annotate the service
@GrpcService(interceptors = {AuthInterceptor.class, LoggingInterceptor.class})
public class OrderGrpcService extends OrderServiceGrpc.OrderServiceImplBase {
    @Autowired OrderService orderService;

    @Override
    public void getOrder(GetOrderRequest request, StreamObserver<Order> responseObserver) {
        orderService.findById(request.getId())
            .map(this::toProto)
            .ifPresentOrElse(
                order -> { responseObserver.onNext(order); responseObserver.onCompleted(); },
                () -> responseObserver.onError(
                    Status.NOT_FOUND.withDescription("Order not found").asRuntimeException())
            );
    }
}

// Client — inject the stub
@GrpcClient("inventory-service")
OrderServiceGrpc.OrderServiceBlockingStub inventoryStub;
```

```yaml
# application.yml
grpc:
  server:
    port: 9090
  client:
    inventory-service:
      address: static://inventory:50051
      negotiation-type: plaintext
      deadline: 5s
```

---

### 7. How do you handle deadlines and cancellation in Java gRPC?

**A:**

```java
// Client — set deadline
Order order = blockingStub
    .withDeadlineAfter(3, TimeUnit.SECONDS)
    .getOrder(request);

// Server — check if cancelled during processing
@Override
public void heavyOperation(Request request, StreamObserver<Response> responseObserver) {
    Context context = Context.current();

    for (int i = 0; i < 1000; i++) {
        if (context.isCancelled()) {
            // Client cancelled or deadline exceeded — stop work
            responseObserver.onError(context.cancellationCause());
            return;
        }
        doWork(i);
    }
    responseObserver.onNext(buildResponse());
    responseObserver.onCompleted();
}

// Propagate deadline to downstream calls
Context deadlineContext = context.withDeadlineAfter(2, TimeUnit.SECONDS, scheduler);
deadlineContext.run(() -> {
    // Calls within this block inherit the deadline
    inventoryStub.checkStock(request);
});
```

---

### 8. How do you test gRPC services in Java?

**A:**

```java
// Use GrpcCleanupRule — starts in-process server (no network needed)
@ExtendWith(GrpcCleanupExtension.class)
class OrderServiceTest {

    @RegisterExtension
    static final GrpcCleanupExtension grpcCleanup = new GrpcCleanupExtension();

    private OrderServiceGrpc.OrderServiceBlockingStub stub;

    @BeforeEach
    void setUp() throws Exception {
        OrderRepository mockRepo = mock(OrderRepository.class);
        when(mockRepo.findById("order-1")).thenReturn(Optional.of(testOrder()));

        String serverName = InProcessServerBuilder.generateName();

        grpcCleanup.register(
            InProcessServerBuilder.forName(serverName)
                .directExecutor()
                .addService(new OrderServiceImpl(mockRepo))
                .build()
                .start()
        );

        ManagedChannel channel = grpcCleanup.register(
            InProcessChannelBuilder.forName(serverName).directExecutor().build()
        );

        stub = OrderServiceGrpc.newBlockingStub(channel);
    }

    @Test
    void shouldReturnOrder() {
        Order order = stub.getOrder(GetOrderRequest.newBuilder().setId("order-1").build());
        assertThat(order.getId()).isEqualTo("order-1");
    }

    @Test
    void shouldThrowNotFoundForMissingOrder() {
        StatusRuntimeException ex = assertThrows(StatusRuntimeException.class,
            () -> stub.getOrder(GetOrderRequest.newBuilder().setId("missing").build()));
        assertThat(ex.getStatus().getCode()).isEqualTo(Status.Code.NOT_FOUND);
    }
}
```

---

## 🔴 Senior Level

---

### 9. How do you configure TLS and mTLS for gRPC in Java?

**A:**

```java
// Server — TLS
Server server = NettyServerBuilder.forPort(50051)
    .sslContext(SslContextBuilder
        .forServer(certFile, keyFile)
        .build())
    .addService(new OrderServiceImpl())
    .build();

// Server — mTLS (verify client certificate)
Server server = NettyServerBuilder.forPort(50051)
    .sslContext(SslContextBuilder
        .forServer(serverCert, serverKey)
        .trustManager(caCert)
        .clientAuth(ClientAuth.REQUIRE)
        .build())
    .addService(new OrderServiceImpl())
    .build();

// Client — mTLS
ManagedChannel channel = NettyChannelBuilder
    .forAddress("order-service", 50051)
    .sslContext(GrpcSslContexts.forClient()
        .keyManager(clientCert, clientKey)
        .trustManager(caCert)
        .build())
    .build();

// With Spring Boot + grpc-spring-boot-starter
// application.yml
grpc:
  server:
    security:
      enabled: true
      certificate-chain: classpath:server.crt
      private-key: classpath:server.key
      client-auth: REQUIRE
      trust-cert-collection: classpath:ca.crt
```

---

### 10. How do you implement load balancing and service discovery for gRPC in Java?

**A:**

```java
// DNS round-robin (Kubernetes headless service)
ManagedChannel channel = ManagedChannelBuilder
    .forTarget("dns:///order-service.default.svc.cluster.local:50051")
    .defaultLoadBalancingPolicy("round_robin")
    .usePlaintext()
    .build();

// Service config — retry policy and timeout
String serviceConfig = """
    {
        "loadBalancingConfig": [{"round_robin": {}}],
        "methodConfig": [{
            "name": [{"service": "order.v1.OrderService"}],
            "retryPolicy": {
                "maxAttempts": 3,
                "initialBackoff": "0.1s",
                "maxBackoff": "1s",
                "backoffMultiplier": 2.0,
                "retryableStatusCodes": ["UNAVAILABLE", "DEADLINE_EXCEEDED"]
            },
            "timeout": "10s"
        }]
    }
    """;

ManagedChannel channel = ManagedChannelBuilder
    .forTarget("order-service:50051")
    .defaultServiceConfig(parseServiceConfig(serviceConfig))
    .enableRetry()
    .build();

// With Spring Cloud LoadBalancer
@GrpcClient("order-service") // resolved via Spring Cloud service registry
OrderServiceGrpc.OrderServiceBlockingStub stub;
```

---

## 🏛️ Architect Level

---

### 11. How do you design a gRPC API for a microservices system in Java?

**A:**

**Proto organization (buf.build):**
```
proto/
├── buf.yaml
├── common/
│   └── v1/
│       ├── pagination.proto
│       ├── money.proto
│       └── timestamp.proto
└── order/
    └── v1/
        ├── order.proto          # messages
        └── order_service.proto  # service
```

**Follow Google API Design Guide:**
```protobuf
service OrderService {
    // Standard CRUD
    rpc GetOrder(GetOrderRequest) returns (Order);
    rpc ListOrders(ListOrdersRequest) returns (ListOrdersResponse);
    rpc CreateOrder(CreateOrderRequest) returns (Order);
    rpc UpdateOrder(UpdateOrderRequest) returns (Order);
    rpc DeleteOrder(DeleteOrderRequest) returns (google.protobuf.Empty);

    // Custom methods — verb_noun
    rpc CancelOrder(CancelOrderRequest) returns (Order);
    rpc BatchGetOrders(BatchGetOrdersRequest) returns (BatchGetOrdersResponse);
    rpc WatchOrders(WatchOrdersRequest) returns (stream Order);
}
```

**Versioning strategy:**
- Package versioning: `package order.v1` → `package order.v2`
- Use `buf breaking` in CI to prevent accidental breaking changes on v1
- Additive-only changes within a version

**Spring Boot gRPC service template:**
```java
@GrpcService
public class OrderGrpcService extends OrderServiceGrpc.OrderServiceImplBase {

    @Autowired private OrderApplicationService orderService;
    @Autowired private OrderProtoMapper mapper;

    @Override
    public void createOrder(CreateOrderRequest req, StreamObserver<Order> obs) {
        try {
            var command = mapper.toCommand(req);
            var order = orderService.createOrder(command);
            obs.onNext(mapper.toProto(order));
            obs.onCompleted();
        } catch (ValidationException e) {
            obs.onError(Status.INVALID_ARGUMENT
                .withDescription(e.getMessage())
                .asRuntimeException());
        }
    }
}
```
