# 📡 gRPC in Python — Interview Questions (Junior → Architect)

---

## 🟢 Junior Level

---

### 1. How do you set up gRPC in Python?

**A:**

```bash
pip install grpcio grpcio-tools
```

```protobuf
// proto/order/v1/order.proto
syntax = "proto3";
package order.v1;
option python_package = "gen.order.v1";

service OrderService {
  rpc GetOrder(GetOrderRequest) returns (Order);
  rpc CreateOrder(CreateOrderRequest) returns (Order);
  rpc WatchOrders(WatchRequest) returns (stream Order);
}

message Order {
  string id = 1;
  string customer_id = 2;
  double total = 3;
  string status = 4;
}

message GetOrderRequest { string id = 1; }
message CreateOrderRequest {
  string customer_id = 1;
  repeated OrderItem items = 2;
}
message OrderItem { string product_id = 1; int32 quantity = 2; }
message WatchRequest { string customer_id = 1; }
```

```bash
# Generate Python code
python -m grpc_tools.protoc \
  -I proto \
  --python_out=gen \
  --grpc_python_out=gen \
  proto/order/v1/order.proto

# Generates:
# gen/order/v1/order_pb2.py       — message classes
# gen/order/v1/order_pb2_grpc.py  — client stubs + server base
```

---

### 2. How do you implement a gRPC server in Python?

**A:**

```python
from concurrent import futures
import grpc
from gen.order.v1 import order_pb2, order_pb2_grpc

class OrderServiceServicer(order_pb2_grpc.OrderServiceServicer):

    def GetOrder(self, request, context):
        order = db.get_order(request.id)
        if not order:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Order {request.id} not found")
            return order_pb2.Order()

        return order_pb2.Order(
            id=order.id,
            customer_id=order.customer_id,
            total=float(order.total),
            status=order.status,
        )

    def CreateOrder(self, request, context):
        if not request.items:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "items cannot be empty")

        order = db.create_order(request.customer_id, list(request.items))
        return order_pb2.Order(id=order.id, customer_id=order.customer_id, total=float(order.total))

    def WatchOrders(self, request, context):
        """Server-side streaming"""
        for order in db.stream_orders(request.customer_id):
            if context.is_active():
                yield order_pb2.Order(id=order.id, status=order.status)
            else:
                break  # client disconnected

def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=[AuthInterceptor(), LoggingInterceptor()],
    )
    order_pb2_grpc.add_OrderServiceServicer_to_server(OrderServiceServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Server started on :50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
```

---

### 3. How do you implement a gRPC client in Python?

**A:**

```python
import grpc
from gen.order.v1 import order_pb2, order_pb2_grpc

def get_order(order_id: str) -> order_pb2.Order:
    with grpc.insecure_channel("order-service:50051") as channel:
        stub = order_pb2_grpc.OrderServiceStub(channel)

        try:
            order = stub.GetOrder(
                order_pb2.GetOrderRequest(id=order_id),
                timeout=5.0,  # seconds
                metadata=[("authorization", f"Bearer {get_token()}")],
            )
            return order
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                raise OrderNotFoundError(order_id)
            raise

# Reuse channel — don't create per-call (expensive)
channel = grpc.insecure_channel(
    "order-service:50051",
    options=[
        ("grpc.max_receive_message_length", 50 * 1024 * 1024),
        ("grpc.keepalive_time_ms", 30000),
    ]
)
stub = order_pb2_grpc.OrderServiceStub(channel)

# Client-side streaming
def upload_items(items: list[dict]):
    def item_generator():
        for item in items:
            yield order_pb2.OrderItem(product_id=item["product_id"], quantity=item["qty"])

    result = stub.UploadItems(item_generator())
    print(f"Uploaded {result.item_count} items")

# Server-side streaming
for order in stub.WatchOrders(order_pb2.WatchRequest(customer_id="cust-1")):
    print(f"Order update: {order.id} -> {order.status}")
```

---

### 4. How do you handle errors and status codes?

**A:**

```python
# Server side
def GetOrder(self, request, context):
    # Method 1: set_code + set_details
    context.set_code(grpc.StatusCode.NOT_FOUND)
    context.set_details("Order not found")
    return order_pb2.Order()

    # Method 2: abort — stops processing immediately
    context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Order ID cannot be empty")

    # Method 3: abort_with_status — rich error details
    from grpc_status import rpc_status
    from google.rpc import status_pb2, error_details_pb2

    detail = error_details_pb2.BadRequest()
    detail.field_violations.add(field="customer_id", description="required")

    rich_status = rpc_status.to_status(
        status_pb2.Status(
            code=grpc.StatusCode.INVALID_ARGUMENT.value[0],
            message="Validation failed",
            details=[detail.SerializeToString()],
        )
    )
    context.abort_with_status(rich_status)

# Client side
try:
    order = stub.GetOrder(request)
except grpc.RpcError as e:
    code = e.code()
    details = e.details()

    if code == grpc.StatusCode.NOT_FOUND:
        return None
    elif code == grpc.StatusCode.DEADLINE_EXCEEDED:
        raise TimeoutError("Request timed out")
    elif code == grpc.StatusCode.UNAVAILABLE:
        raise ServiceUnavailableError("Order service unavailable")
    else:
        raise
```

---

## 🟡 Mid Level

---

### 5. How do you implement interceptors in Python gRPC?

**A:**

```python
import grpc
from grpc import ServerInterceptor

class AuthInterceptor(grpc.ServerInterceptor):

    def intercept_service(self, continuation, handler_call_details):
        # Check metadata for auth token
        metadata = dict(handler_call_details.invocation_metadata)
        token = metadata.get("authorization", "")

        if not token.startswith("Bearer "):
            def abort(ignored_request, context):
                context.abort(grpc.StatusCode.UNAUTHENTICATED, "Missing token")
            return grpc.unary_unary_rpc_method_handler(abort)

        try:
            user_id = validate_token(token[7:])
            # Store in context (tricky in Python — use threading.local or contextvars)
            _current_user.set(user_id)
        except TokenError:
            def abort(ignored_request, context):
                context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid token")
            return grpc.unary_unary_rpc_method_handler(abort)

        return continuation(handler_call_details)

# Simpler: use grpc.experimental.interceptors
class LoggingServerInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        start = time.monotonic()
        handler = continuation(handler_call_details)

        def wrapper(request, context):
            try:
                response = handler.unary_unary(request, context)
                duration = time.monotonic() - start
                logger.info("RPC %s duration=%.3fs", handler_call_details.method, duration)
                return response
            except Exception as e:
                logger.error("RPC %s failed: %s", handler_call_details.method, e)
                raise

        return grpc.unary_unary_rpc_method_handler(wrapper)
```

---

### 6. How do you use async gRPC in Python?

**A:**

```python
import grpc.aio
from gen.order.v1 import order_pb2, order_pb2_grpc

# Async server
class AsyncOrderService(order_pb2_grpc.OrderServiceServicer):

    async def GetOrder(self, request, context):
        async with async_db_session() as session:
            order = await session.get(Order, request.id)
            if not order:
                await context.abort(grpc.StatusCode.NOT_FOUND, f"Order {request.id} not found")

            return order_pb2.Order(id=order.id, total=float(order.total))

    async def WatchOrders(self, request, context):
        async for order in stream_orders_async(request.customer_id):
            if context.cancelled():
                return
            yield order_pb2.Order(id=order.id, status=order.status)

async def serve():
    server = grpc.aio.server()
    order_pb2_grpc.add_OrderServiceServicer_to_server(AsyncOrderService(), server)
    server.add_insecure_port("[::]:50051")
    await server.start()
    await server.wait_for_termination()

asyncio.run(serve())

# Async client
async def main():
    async with grpc.aio.insecure_channel("order-service:50051") as channel:
        stub = order_pb2_grpc.OrderServiceStub(channel)

        # Concurrent calls
        order1, order2 = await asyncio.gather(
            stub.GetOrder(order_pb2.GetOrderRequest(id="order-1")),
            stub.GetOrder(order_pb2.GetOrderRequest(id="order-2")),
        )

        # Streaming
        async for order in stub.WatchOrders(order_pb2.WatchRequest(customer_id="cust-1")):
            print(order.status)
```

---

### 7. How do you test gRPC services in Python?

**A:**

```python
import pytest
import grpc
from grpc import testing as grpc_testing
from unittest.mock import MagicMock

# Unit test — no network
def test_get_order_not_found():
    servicer = OrderServiceServicer(db=MockDB())
    request = order_pb2.GetOrderRequest(id="missing")

    context = MagicMock()
    result = servicer.GetOrder(request, context)

    context.set_code.assert_called_with(grpc.StatusCode.NOT_FOUND)

# Integration test — real in-process server
@pytest.fixture
def grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    order_pb2_grpc.add_OrderServiceServicer_to_server(
        OrderServiceServicer(db=TestDB()), server
    )
    port = server.add_insecure_port("[::]:0")  # random port
    server.start()
    yield f"localhost:{port}"
    server.stop(0)

def test_create_order(grpc_server):
    with grpc.insecure_channel(grpc_server) as channel:
        stub = order_pb2_grpc.OrderServiceStub(channel)
        request = order_pb2.CreateOrderRequest(
            customer_id="cust-1",
            items=[order_pb2.OrderItem(product_id="prod-1", quantity=2)]
        )
        order = stub.CreateOrder(request)
        assert order.id
        assert order.customer_id == "cust-1"

# Test streaming
def test_watch_orders(grpc_server):
    with grpc.insecure_channel(grpc_server) as channel:
        stub = order_pb2_grpc.OrderServiceStub(channel)
        orders = list(stub.WatchOrders(order_pb2.WatchRequest(customer_id="cust-1")))
        assert len(orders) == 3
```

---

## 🔴 Senior Level

---

### 8. How do you implement TLS and mTLS in Python gRPC?

**A:**

```python
# Server TLS
with open("server.key", "rb") as f: server_key = f.read()
with open("server.crt", "rb") as f: server_cert = f.read()

credentials = grpc.ssl_server_credentials([(server_key, server_cert)])
server.add_secure_port("[::]:50051", credentials)

# Server mTLS — require client certificate
with open("ca.crt", "rb") as f: ca_cert = f.read()

credentials = grpc.ssl_server_credentials(
    [(server_key, server_cert)],
    root_certificates=ca_cert,
    require_client_auth=True,
)

# Client TLS
with open("ca.crt", "rb") as f: ca_cert = f.read()
credentials = grpc.ssl_channel_credentials(root_certificates=ca_cert)
channel = grpc.secure_channel("order-service:50051", credentials)

# Client mTLS
with open("client.key", "rb") as f: client_key = f.read()
with open("client.crt", "rb") as f: client_cert = f.read()

credentials = grpc.ssl_channel_credentials(
    root_certificates=ca_cert,
    private_key=client_key,
    certificate_chain=client_cert,
)
```

---

## 🏛️ Architect Level

---

### 9. How do you design gRPC services in a Python microservices architecture?

**A:**

**Proto organization with buf:**
```yaml
# buf.yaml
version: v2
lint:
  use: [DEFAULT]
breaking:
  use: [FILE]

# buf.gen.yaml
version: v2
plugins:
  - remote: buf.build/protocolbuffers/python
    out: gen
  - remote: buf.build/grpc/python
    out: gen
```

**Service design:**
```protobuf
// Follow Google API Design Guide
service OrderService {
  rpc ListOrders(ListOrdersRequest) returns (ListOrdersResponse);
  rpc GetOrder(GetOrderRequest) returns (Order);
  rpc CreateOrder(CreateOrderRequest) returns (Order);
  rpc CancelOrder(CancelOrderRequest) returns (Order);

  // Streaming for real-time updates
  rpc WatchOrders(WatchOrdersRequest) returns (stream Order);
}
```

**Production pattern — reusable channel:**
```python
import grpc
from grpc import Channel
from functools import lru_cache

@lru_cache(maxsize=None)
def get_channel(target: str) -> Channel:
    return grpc.insecure_channel(
        target,
        options=[
            ("grpc.keepalive_time_ms", 30_000),
            ("grpc.keepalive_timeout_ms", 5_000),
            ("grpc.keepalive_permit_without_calls", True),
            ("grpc.http2.max_pings_without_data", 0),
            ("grpc.max_receive_message_length", 50 * 1024 * 1024),
        ]
    )

# Interceptor chain for all clients
class ClientInterceptor(grpc.UnaryUnaryClientInterceptor):
    def intercept_unary_unary(self, continuation, client_call_details, request):
        # Add trace headers, auth, etc.
        metadata = list(client_call_details.metadata or [])
        metadata.append(("x-trace-id", get_current_trace_id()))
        metadata.append(("authorization", f"Bearer {get_service_token()}"))
        new_details = client_call_details._replace(metadata=metadata)
        return continuation(new_details, request)
```
