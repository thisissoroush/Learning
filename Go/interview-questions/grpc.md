# 📡 gRPC in Go — Interview Questions (Junior → Architect)

---

## 🟢 Junior Level

---

### 1. What is gRPC and why is it preferred over REST for internal services?

**A:** gRPC is a high-performance RPC framework from Google that uses **Protocol Buffers** (protobuf) for serialization and **HTTP/2** for transport.

| | gRPC | REST |
|--|------|------|
| Protocol | HTTP/2 | HTTP/1.1 (usually) |
| Serialization | Protobuf (binary, compact) | JSON (text, verbose) |
| Contract | Strongly typed `.proto` file | Informal (OpenAPI optional) |
| Code gen | Yes — client + server stubs | Manual or generator |
| Streaming | Bidirectional | Limited (SSE, WebSocket workarounds) |
| Browser support | Limited (grpc-web needed) | Native |

gRPC is preferred internally for: lower latency, smaller payload, strict contracts, and generated clients in any language.

---

### 2. What is a `.proto` file and how do you structure one?

**A:**

```protobuf
syntax = "proto3";

package order.v1;

option go_package = "github.com/myorg/myapp/gen/order/v1;orderv1";

import "google/protobuf/timestamp.proto";

// Service definition
service OrderService {
  rpc CreateOrder(CreateOrderRequest) returns (CreateOrderResponse);
  rpc GetOrder(GetOrderRequest) returns (Order);
  rpc ListOrders(ListOrdersRequest) returns (ListOrdersResponse);
  rpc WatchOrders(WatchOrdersRequest) returns (stream Order);  // server stream
  rpc UploadItems(stream OrderItem) returns (UploadSummary);  // client stream
  rpc Chat(stream ChatMessage) returns (stream ChatMessage);  // bidirectional
}

// Messages
message Order {
  string id = 1;
  string customer_id = 2;
  double total = 3;
  OrderStatus status = 4;
  google.protobuf.Timestamp created_at = 5;
  repeated OrderItem items = 6;
}

message OrderItem {
  string product_id = 1;
  int32 quantity = 2;
  double unit_price = 3;
}

enum OrderStatus {
  ORDER_STATUS_UNSPECIFIED = 0;
  ORDER_STATUS_PENDING = 1;
  ORDER_STATUS_CONFIRMED = 2;
  ORDER_STATUS_SHIPPED = 3;
}

message CreateOrderRequest {
  string customer_id = 1;
  repeated OrderItem items = 2;
}

message CreateOrderResponse {
  Order order = 1;
}
```

---

### 3. How do you generate Go code from a `.proto` file?

**A:**

```bash
# Install tools
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

# Generate
protoc \
  --go_out=. \
  --go_opt=paths=source_relative \
  --go-grpc_out=. \
  --go-grpc_opt=paths=source_relative \
  proto/order/v1/order.proto

# Better: use buf (modern tool — handles imports, linting, breaking changes)
# buf.yaml in repo root
buf generate

# Generated files:
# gen/order/v1/order.pb.go       — message types
# gen/order/v1/order_grpc.pb.go  — service client + server interfaces
```

---

### 4. How do you implement a gRPC server in Go?

**A:**

```go
import (
    "google.golang.org/grpc"
    pb "github.com/myorg/myapp/gen/order/v1"
)

// Implement the generated server interface
type OrderServer struct {
    pb.UnimplementedOrderServiceServer // embed for forward compatibility
    repo OrderRepository
}

func (s *OrderServer) CreateOrder(ctx context.Context, req *pb.CreateOrderRequest) (*pb.CreateOrderResponse, error) {
    if req.CustomerId == "" {
        return nil, status.Error(codes.InvalidArgument, "customer_id is required")
    }

    order, err := s.repo.Create(ctx, req.CustomerId, req.Items)
    if err != nil {
        return nil, status.Errorf(codes.Internal, "failed to create order: %v", err)
    }

    return &pb.CreateOrderResponse{Order: toProtoOrder(order)}, nil
}

func main() {
    lis, err := net.Listen("tcp", ":50051")
    if err != nil {
        log.Fatal(err)
    }

    srv := grpc.NewServer(
        grpc.UnaryInterceptor(loggingInterceptor),
    )
    pb.RegisterOrderServiceServer(srv, &OrderServer{})

    reflection.Register(srv) // enable grpcurl/grpc-ui in dev

    log.Println("gRPC server listening on :50051")
    if err := srv.Serve(lis); err != nil {
        log.Fatal(err)
    }
}
```

---

### 5. How do you implement a gRPC client in Go?

**A:**

```go
func main() {
    conn, err := grpc.NewClient(
        "order-service:50051",
        grpc.WithTransportCredentials(insecure.NewCredentials()), // dev only
        // grpc.WithTransportCredentials(credentials.NewTLS(tlsConfig)), // prod
    )
    if err != nil {
        log.Fatal(err)
    }
    defer conn.Close()

    client := pb.NewOrderServiceClient(conn)

    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    resp, err := client.CreateOrder(ctx, &pb.CreateOrderRequest{
        CustomerId: "cust-123",
        Items: []*pb.OrderItem{
            {ProductId: "prod-1", Quantity: 2, UnitPrice: 29.99},
        },
    })
    if err != nil {
        // Handle gRPC errors
        st, _ := status.FromError(err)
        log.Printf("Code: %s, Message: %s", st.Code(), st.Message())
        return
    }

    fmt.Println("Created order:", resp.Order.Id)
}
```

---

### 6. What are gRPC status codes and how do you use them?

**A:**

```go
import (
    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/status"
)

// Return status errors from server handlers
func (s *OrderServer) GetOrder(ctx context.Context, req *pb.GetOrderRequest) (*pb.Order, error) {
    order, err := s.repo.Get(ctx, req.Id)
    if errors.Is(err, ErrNotFound) {
        return nil, status.Errorf(codes.NotFound, "order %s not found", req.Id)
    }
    if err != nil {
        return nil, status.Errorf(codes.Internal, "database error: %v", err)
    }
    return toProtoOrder(order), nil
}

// Common codes
// codes.OK              — success
// codes.InvalidArgument — bad request (wrong input)
// codes.NotFound        — resource doesn't exist
// codes.AlreadyExists   — conflict
// codes.PermissionDenied — forbidden
// codes.Unauthenticated — not logged in
// codes.Internal        — server error
// codes.Unavailable     — service temporarily unavailable (retry)
// codes.DeadlineExceeded — timeout

// Check on client side
if st, ok := status.FromError(err); ok {
    switch st.Code() {
    case codes.NotFound:
        fmt.Println("not found")
    case codes.Unavailable:
        fmt.Println("retry later")
    }
}
```

---

### 7. What is protobuf field numbering and why does it matter?

**A:** Field numbers identify fields in the binary encoding — they must never change once deployed:

```protobuf
message User {
  string id = 1;    // field number 1
  string name = 2;  // field number 2
  string email = 3; // field number 3
}
```

**Rules:**
- Field numbers 1–15 use 1 byte (use for frequently set fields)
- Field numbers 16–2047 use 2 bytes
- **Never** change or reuse a field number — breaks binary compatibility
- To remove a field, mark it `reserved`:

```protobuf
message User {
  reserved 4, 5;            // old field numbers, never reuse
  reserved "phone", "fax";  // old field names
  string id = 1;
  string name = 2;
  string email = 3;
  string mobile = 6;        // new field, new number
}
```

---

### 8. What is `UnimplementedXxxServer` and why must you embed it?

**A:** Generated server interfaces include a `UnimplementedXxxServer` struct that returns `codes.Unimplemented` for all methods. You embed it so:

1. Your server compiles even if you haven't implemented all methods yet
2. New methods added to the proto in future versions don't break your code

```go
type MyServer struct {
    pb.UnimplementedOrderServiceServer // MUST embed
    // your fields
}

// Only implement the methods you need
func (s *MyServer) GetOrder(ctx context.Context, req *pb.GetOrderRequest) (*pb.Order, error) {
    // ...
}

// CreateOrder, ListOrders, etc. return codes.Unimplemented automatically
```

Without embedding, adding a new RPC to the proto breaks the build.

---

## 🟡 Mid Level

---

### 9. How do you implement server-side and client-side streaming?

**A:**

```go
// Server-side streaming — server sends multiple messages
func (s *OrderServer) WatchOrders(req *pb.WatchOrdersRequest, stream pb.OrderService_WatchOrdersServer) error {
    for {
        select {
        case <-stream.Context().Done():
            return stream.Context().Err()
        case order := <-s.orderUpdates:
            if err := stream.Send(toProtoOrder(order)); err != nil {
                return err // client disconnected
            }
        }
    }
}

// Client-side streaming — client sends multiple messages
func (s *OrderServer) UploadItems(stream pb.OrderService_UploadItemsServer) error {
    var items []*pb.OrderItem
    for {
        item, err := stream.Recv()
        if err == io.EOF {
            break // client finished sending
        }
        if err != nil {
            return err
        }
        items = append(items, item)
    }
    // Process all items
    return stream.SendAndClose(&pb.UploadSummary{ItemCount: int32(len(items))})
}

// Bidirectional streaming
func (s *OrderServer) Chat(stream pb.OrderService_ChatServer) error {
    for {
        msg, err := stream.Recv()
        if err == io.EOF {
            return nil
        }
        if err != nil {
            return err
        }
        if err := stream.Send(&pb.ChatMessage{Text: "Echo: " + msg.Text}); err != nil {
            return err
        }
    }
}
```

---

### 10. How do you implement unary and streaming interceptors?

**A:**

```go
// Unary interceptor — runs for every unary RPC
func LoggingInterceptor(
    ctx context.Context,
    req any,
    info *grpc.UnaryServerInfo,
    handler grpc.UnaryHandler,
) (any, error) {
    start := time.Now()
    resp, err := handler(ctx, req)
    log.Printf("RPC %s duration=%v err=%v", info.FullMethod, time.Since(start), err)
    return resp, err
}

// Chaining multiple interceptors
import "google.golang.org/grpc"

srv := grpc.NewServer(
    grpc.ChainUnaryInterceptor(
        RecoveryInterceptor,
        AuthInterceptor,
        LoggingInterceptor,
        TracingInterceptor,
    ),
    grpc.ChainStreamInterceptor(
        StreamAuthInterceptor,
        StreamLoggingInterceptor,
    ),
)

// Auth interceptor
func AuthInterceptor(ctx context.Context, req any, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (any, error) {
    md, ok := metadata.FromIncomingContext(ctx)
    if !ok {
        return nil, status.Error(codes.Unauthenticated, "no metadata")
    }
    tokens := md.Get("authorization")
    if len(tokens) == 0 {
        return nil, status.Error(codes.Unauthenticated, "no token")
    }
    userID, err := validateToken(tokens[0])
    if err != nil {
        return nil, status.Error(codes.Unauthenticated, "invalid token")
    }
    ctx = context.WithValue(ctx, userIDKey, userID)
    return handler(ctx, req)
}
```

---

### 11. How do you pass metadata (headers) in gRPC?

**A:**

```go
// Client: send metadata
ctx := context.Background()
md := metadata.Pairs(
    "authorization", "Bearer "+token,
    "x-request-id", requestID,
    "x-tenant-id", tenantID,
)
ctx = metadata.NewOutgoingContext(ctx, md)
resp, err := client.GetOrder(ctx, req)

// Server: receive metadata
func (s *OrderServer) GetOrder(ctx context.Context, req *pb.GetOrderRequest) (*pb.Order, error) {
    md, ok := metadata.FromIncomingContext(ctx)
    if !ok {
        return nil, status.Error(codes.InvalidArgument, "no metadata")
    }
    tenantID := md.Get("x-tenant-id")
    // ...
}

// Server: send metadata in response header/trailer
func (s *OrderServer) GetOrder(ctx context.Context, req *pb.GetOrderRequest) (*pb.Order, error) {
    header := metadata.Pairs("x-request-id", "abc-123")
    grpc.SendHeader(ctx, header)

    trailer := metadata.Pairs("x-duration-ms", "42")
    grpc.SetTrailer(ctx, trailer)
    // ...
}

// Client: receive response headers
var header, trailer metadata.MD
resp, err := client.GetOrder(
    ctx, req,
    grpc.Header(&header),
    grpc.Trailer(&trailer),
)
```

---

### 12. How do you implement deadlines and cancellation?

**A:**

```go
// Always set deadlines on client calls
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

resp, err := client.GetOrder(ctx, req)
if err != nil {
    if status.Code(err) == codes.DeadlineExceeded {
        log.Println("request timed out")
    }
}

// Server: propagate context — automatically cancelled when client deadline exceeds
func (s *OrderServer) GetOrder(ctx context.Context, req *pb.GetOrderRequest) (*pb.Order, error) {
    // Pass ctx to all downstream calls
    order, err := s.repo.Get(ctx, req.Id) // cancels if client disconnects
    if ctx.Err() != nil {
        return nil, status.FromContextError(ctx.Err()).Err()
    }
    return toProtoOrder(order), err
}

// Check deadline remaining on server
if deadline, ok := ctx.Deadline(); ok {
    remaining := time.Until(deadline)
    if remaining < 100*time.Millisecond {
        return nil, status.Error(codes.DeadlineExceeded, "insufficient time remaining")
    }
}
```

---

### 13. How do you use `buf` for proto management?

**A:** `buf` is the modern replacement for raw `protoc` — handles linting, breaking change detection, and generation:

```yaml
# buf.yaml
version: v2
lint:
  use:
    - DEFAULT
breaking:
  use:
    - FILE  # detect breaking changes at file level

# buf.gen.yaml
version: v2
plugins:
  - remote: buf.build/protocolbuffers/go
    out: gen
    opt: paths=source_relative
  - remote: buf.build/grpc/go
    out: gen
    opt: paths=source_relative
```

```bash
buf lint                    # lint .proto files
buf breaking --against .git#branch=main  # detect breaking changes vs main
buf generate                # generate code
buf push                    # push to Buf Schema Registry
```

**Key buf lint rules:**
- `FIELD_LOWER_SNAKE_CASE` — field names must be snake_case
- `RPC_RESPONSE_STANDARD_NAME` — response messages named `XxxResponse`
- `ENUM_ZERO_VALUE_SUFFIX` — zero value must end in `_UNSPECIFIED`

---

### 14. How do you handle errors with rich details?

**A:** `status.Status` can carry structured error details beyond just a code and message:

```go
import "google.golang.org/grpc/status"
import "google.golang.org/genproto/googleapis/rpc/errdetails"

func (s *OrderServer) CreateOrder(ctx context.Context, req *pb.CreateOrderRequest) (*pb.CreateOrderResponse, error) {
    // Validation error with field violations
    if req.CustomerId == "" || len(req.Items) == 0 {
        st := status.New(codes.InvalidArgument, "validation failed")
        st, _ = st.WithDetails(&errdetails.BadRequest{
            FieldViolations: []*errdetails.BadRequest_FieldViolation{
                {Field: "customer_id", Description: "must not be empty"},
                {Field: "items", Description: "must have at least one item"},
            },
        })
        return nil, st.Err()
    }
    // ...
}

// Client: extract details
if err != nil {
    st := status.Convert(err)
    for _, detail := range st.Details() {
        switch t := detail.(type) {
        case *errdetails.BadRequest:
            for _, v := range t.FieldViolations {
                fmt.Printf("Field %s: %s\n", v.Field, v.Description)
            }
        }
    }
}
```

---

## 🔴 Senior Level

---

### 15. How do you implement connection pooling and load balancing for gRPC?

**A:**

```go
// gRPC connections are multiplexed over HTTP/2 — one connection handles many RPCs concurrently
// BUT for load balancing, you need multiple connections to multiple backends

conn, err := grpc.NewClient(
    "dns:///order-service:50051", // DNS round-robin (Kubernetes headless service)
    grpc.WithDefaultServiceConfig(`{
        "loadBalancingConfig": [{"round_robin": {}}],
        "methodConfig": [{
            "name": [{"service": "order.v1.OrderService"}],
            "retryPolicy": {
                "maxAttempts": 4,
                "initialBackoff": "0.1s",
                "maxBackoff": "1s",
                "backoffMultiplier": 2.0,
                "retryableStatusCodes": ["UNAVAILABLE", "DEADLINE_EXCEEDED"]
            },
            "timeout": "5s"
        }]
    }`),
    grpc.WithTransportCredentials(credentials.NewTLS(tlsCfg)),
)

// For service mesh (Istio/Linkerd) — connection management handled externally
// Just use a single address; the mesh proxies and load-balances transparently
```

---

### 16. How do you implement server reflection and health checking?

**A:**

```go
import (
    "google.golang.org/grpc/health"
    "google.golang.org/grpc/health/grpc_health_v1"
    "google.golang.org/grpc/reflection"
)

func main() {
    srv := grpc.NewServer()

    // Register your services
    pb.RegisterOrderServiceServer(srv, &OrderServer{})

    // Health check (used by Kubernetes probes, grpc-health-probe)
    healthSrv := health.NewServer()
    grpc_health_v1.RegisterHealthServer(srv, healthSrv)
    healthSrv.SetServingStatus("order.v1.OrderService", grpc_health_v1.HealthCheckResponse_SERVING)

    // Server reflection (for grpcurl, grpc-ui in dev/staging)
    if os.Getenv("GRPC_REFLECTION") == "true" {
        reflection.Register(srv)
    }

    // Kubernetes liveness probe
    // grpc-health-probe -addr=:50051
}
```

```yaml
# Kubernetes probe
livenessProbe:
  exec:
    command: ["/bin/grpc-health-probe", "-addr=:50051"]
  initialDelaySeconds: 10
readinessProbe:
  exec:
    command: ["/bin/grpc-health-probe", "-addr=:50051", "-service=order.v1.OrderService"]
```

---

### 17. How do you add TLS and mutual TLS (mTLS) to gRPC?

**A:**

```go
// Server — TLS
creds, err := credentials.NewServerTLSFromFile("server.crt", "server.key")
srv := grpc.NewServer(grpc.Creds(creds))

// Server — mTLS (verify client certificates)
cert, _ := tls.LoadX509KeyPair("server.crt", "server.key")
ca, _ := os.ReadFile("ca.crt")
pool := x509.NewCertPool()
pool.AppendCertsFromPEM(ca)

tlsConfig := &tls.Config{
    Certificates: []tls.Certificate{cert},
    ClientAuth:   tls.RequireAndVerifyClientCert,
    ClientCAs:    pool,
}
srv := grpc.NewServer(grpc.Creds(credentials.NewTLS(tlsConfig)))

// Client — mTLS
clientCert, _ := tls.LoadX509KeyPair("client.crt", "client.key")
tlsConfig := &tls.Config{
    Certificates: []tls.Certificate{clientCert},
    RootCAs:      pool,
    ServerName:   "order-service",
}
conn, _ := grpc.NewClient("order-service:50051",
    grpc.WithTransportCredentials(credentials.NewTLS(tlsConfig)))
```

In production with a service mesh (Istio/Linkerd), mTLS is handled automatically at the infrastructure level — your code uses `insecure.NewCredentials()` inside the mesh.

---

### 18. How do you implement gRPC-Gateway to expose a REST API?

**A:** grpc-gateway generates a reverse proxy that translates REST → gRPC:

```protobuf
import "google/api/annotations.proto";

service OrderService {
  rpc GetOrder(GetOrderRequest) returns (Order) {
    option (google.api.http) = {
      get: "/v1/orders/{id}"
    };
  }
  rpc CreateOrder(CreateOrderRequest) returns (CreateOrderResponse) {
    option (google.api.http) = {
      post: "/v1/orders"
      body: "*"
    };
  }
}
```

```go
// Run gRPC and REST on the same port using cmux
mux := cmux.New(lis)
grpcL := mux.MatchWithWriters(cmux.HTTP2MatchHeaderFieldSendSettings("content-type", "application/grpc"))
httpL := mux.Match(cmux.HTTP1Fast())

grpcSrv := grpc.NewServer()
pb.RegisterOrderServiceServer(grpcSrv, &OrderServer{})

gwMux := runtime.NewServeMux()
pb.RegisterOrderServiceHandlerFromEndpoint(ctx, gwMux, "localhost:50051", []grpc.DialOption{grpc.WithInsecure()})
httpSrv := &http.Server{Handler: gwMux}

go grpcSrv.Serve(grpcL)
go httpSrv.Serve(httpL)
mux.Serve()
```

---

## 🏛️ Architect Level

---

### 19. How do you design a gRPC service for a microservices architecture?

**A:**

**Proto organization:**
```
proto/
├── buf.yaml
├── order/
│   └── v1/
│       ├── order.proto        # messages
│       └── order_service.proto # service (imports messages)
├── inventory/
│   └── v1/
└── common/
    └── v1/
        ├── pagination.proto   # shared types
        └── money.proto
```

**Versioning strategy:**
- Package versioning: `package order.v1` → `package order.v2` for breaking changes
- Additive-only changes within a version (new fields, new RPCs)
- Run `buf breaking` in CI to enforce no breaking changes on `v1`

**Service design:**
```protobuf
// Follow Google API Design Guide
service OrderService {
  // Standard methods: List, Get, Create, Update, Delete
  rpc ListOrders(ListOrdersRequest) returns (ListOrdersResponse);
  rpc GetOrder(GetOrderRequest) returns (Order);
  rpc CreateOrder(CreateOrderRequest) returns (Order);
  rpc UpdateOrder(UpdateOrderRequest) returns (Order);
  rpc DeleteOrder(DeleteOrderRequest) returns (google.protobuf.Empty);

  // Custom methods use verb + noun
  rpc CancelOrder(CancelOrderRequest) returns (Order);
  rpc BatchGetOrders(BatchGetOrdersRequest) returns (BatchGetOrdersResponse);
}
```

**Resilience:**
- Always set deadlines — no timeout = potential goroutine leak
- Retry policy in service config for `UNAVAILABLE` and `DEADLINE_EXCEEDED`
- Circuit breaker at the client (use `grpc.WithConnectParams` + interceptor)
- Bulkhead: separate connection pools per downstream service

---

### 20. How do you test gRPC services in Go?

**A:**

```go
// Unit test — use bufconn (in-process, no network)
import "google.golang.org/grpc/test/bufconn"

func startServer(t *testing.T) pb.OrderServiceClient {
    lis := bufconn.Listen(1024 * 1024)
    srv := grpc.NewServer()
    pb.RegisterOrderServiceServer(srv, &OrderServer{repo: &mockRepo{}})

    go srv.Serve(lis)
    t.Cleanup(srv.Stop)

    conn, _ := grpc.NewClient("passthrough://bufnet",
        grpc.WithContextDialer(func(ctx context.Context, _ string) (net.Conn, error) {
            return lis.DialContext(ctx)
        }),
        grpc.WithTransportCredentials(insecure.NewCredentials()),
    )
    t.Cleanup(func() { conn.Close() })
    return pb.NewOrderServiceClient(conn)
}

func TestGetOrder(t *testing.T) {
    client := startServer(t)
    ctx := context.Background()

    resp, err := client.GetOrder(ctx, &pb.GetOrderRequest{Id: "order-1"})
    require.NoError(t, err)
    assert.Equal(t, "order-1", resp.Id)
}

func TestGetOrder_NotFound(t *testing.T) {
    client := startServer(t)
    _, err := client.GetOrder(context.Background(), &pb.GetOrderRequest{Id: "missing"})
    assert.Equal(t, codes.NotFound, status.Code(err))
}
```
