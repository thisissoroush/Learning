# Chapter 11 — Event-Driven Architecture: Integrating Microservices

> *"With events, services stay loosely coupled. Temporal decoupling: they don't need to be running at the same time."*

---

## 🎯 Core Concept

Scale from events within a process to events between services using message brokers (Redis, Kafka). Services communicate asynchronously through events.

---

## 🔄 Internal vs External Events

### Internal Events (Within One Process)

```python
# Message bus within Python process
def handle(event, uow):
    for handler in HANDLERS[type(event)]:
        handler(event, uow)
```

Synchronous, in-process, fast.

### External Events (Between Services)

```python
# Redis pub/sub between services
def publish_event_to_message_broker(event):
    redis_client.publish(
        'order_events',
        json.dumps(event.to_dict()),
    )

# Another service subscribes:
def subscribe_to_events():
    pubsub = redis_client.pubsub()
    pubsub.subscribe('order_events')
    
    for message in pubsub.listen():
        event_dict = json.loads(message['data'])
        event = OutOfStockEvent(**event_dict)
        handle(event)
```

---

## 🗓️ Temporal Decoupling

External events enable **temporal decoupling**: services don't need to be running at the same time.

```
Service A publishes event at 10:00:00
    ↓
Event stored in message broker (Redis, Kafka)
    ↓
Service B comes online at 10:00:30
    ↓
Service B consumes event from broker
    ↓
Event processed by Service B at 10:00:31
```

Service A doesn't care if Service B is running. The broker buffers the event.

---

## 📡 Example: Redis Pub/Sub Integration

```python
import redis

redis_client = redis.Redis()

# Service 1: Publishing
def allocate_order(cmd, uow):
    with uow:
        product = uow.products.get(cmd.sku)
        product.allocate(OrderLine(cmd.orderid, cmd.sku, cmd.qty))
        uow.commit()
        
        # Publish to external message broker
        for event in product.events:
            redis_client.publish(
                'order_events',
                json.dumps(event.to_dict()),
            )

# Service 2: Subscribing
def subscribe():
    pubsub = redis_client.pubsub()
    pubsub.subscribe('order_events')
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            event_data = json.loads(message['data'])
            
            if event_data['type'] == 'OutOfStockEvent':
                send_notification(event_data['sku'])
            
            elif event_data['type'] == 'OrderAllocatedEvent':
                update_shipping_system(event_data)
```

---

## ✅ Benefits

| Benefit | How |
|---------|-----|
| **Loose coupling** | Services don't import each other |
| **Async processing** | Don't wait for other services |
| **Resilience** | One service down doesn't stop others |
| **Scale independently** | Each service can scale separately |
| **Temporal decoupling** | Services can be offline |

---

## 📋 Integration Patterns

| Pattern | When to Use |
|---------|------------|
| **Synchronous calls** | Small systems, fast dependency |
| **Internal events** | Decoupling within one service |
| **External events** | Between microservices |

---

## 💡 Key Takeaways

| Concept | The Lesson |
|---------|-----------|
| **Internal events** | Message bus within process |
| **External events** | Message broker between services |
| **Temporal decoupling** | Services don't need simultaneous running |
| **Resilience** | Failures don't cascade |
| **Loose coupling** | No direct service-to-service calls |

---

*← [Back to Architecture Patterns](../README.md)*
