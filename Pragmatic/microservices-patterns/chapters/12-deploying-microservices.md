# Chapter 12 — Deploying Microservices

> *"Deploying a microservices-based application is much more complex than deploying a monolith."*

---

## 🎯 Core Concept

With dozens of services to deploy, you need automated infrastructure. This chapter covers four deployment patterns — from simple language packages to containers and serverless — and how Kubernetes has become the standard platform for microservice deployment.

---

## 📦 Pattern 1: Language-Specific Packaging

Deploy as JAR, WAR, npm package, etc. on a shared server.

```
Traditional approach:
  Build → WAR file → Copy to Tomcat server
  
Problems:
  - Shared server → services compete for resources
  - No resource isolation between services
  - Dependency conflicts between services
  - Manual scaling and management
```

**Verdict**: Only suitable for very simple applications.

---

## 🖥️ Pattern 2: Deploy as Virtual Machine

Each service gets its own VM.

```
Service A → VM A  (2 CPU, 4GB RAM)
Service B → VM B  (4 CPU, 8GB RAM)
Service C → VM C  (1 CPU, 2GB RAM)

Benefits:
  ✅ Full isolation
  ✅ Right-sized resources per service
  ✅ Familiar operations model

Drawbacks:
  ❌ Slow to provision (minutes)
  ❌ VMs are heavyweight — OS overhead
  ❌ Cost-inefficient for many small services
```

---

## 🐳 Pattern 3: Deploy as Container ✅ Recommended

Containers offer isolation without the VM overhead.

```
Docker Container:
  lightweight process isolation
  packages service + dependencies
  starts in seconds (vs. minutes for VMs)
  runs identically on dev laptop and production

Dockerfile for Order Service:
  FROM openjdk:17
  COPY target/order-service.jar app.jar
  EXPOSE 8080
  ENTRYPOINT ["java", "-jar", "app.jar"]
  
docker build -t order-service:1.0 .
docker run -p 8080:8080 order-service:1.0
```

**Benefits**: Fast startup, resource efficient, immutable images, consistent environments  
**Drawbacks**: Requires container orchestration at scale

---

## ☸️ Deploying with Kubernetes

Kubernetes is the de facto standard for container orchestration.

```
Kubernetes Architecture:
  ┌─────────────────────────────────────────┐
  │  Kubernetes Cluster                     │
  │                                         │
  │  ┌──────────────────────────────────┐   │
  │  │  Worker Node 1                   │   │
  │  │  Pod: order-service (2 replicas) │   │
  │  └──────────────────────────────────┘   │
  │  ┌──────────────────────────────────┐   │
  │  │  Worker Node 2                   │   │
  │  │  Pod: kitchen-service            │   │
  │  │  Pod: accounting-service         │   │
  │  └──────────────────────────────────┘   │
  └─────────────────────────────────────────┘
```

### Key Kubernetes Concepts

| Concept | Description |
|---------|-------------|
| **Pod** | One or more containers running together |
| **Deployment** | Manages desired number of pod replicas |
| **Service** | Stable DNS name + load balances across pods |
| **ConfigMap** | Non-secret configuration |
| **Secret** | Sensitive configuration (passwords, tokens) |
| **Ingress** | Routes external traffic to services |

### Zero-Downtime Deployments

```
Rolling Update Strategy:
  Old version: [v1] [v1] [v1]
  
  Step 1: [v1] [v1] [v2]    ← add one new
  Step 2: [v1] [v2] [v2]    ← remove one old
  Step 3: [v2] [v2] [v2]    ← complete
  
  At each step: readiness probe must pass before routing traffic
```

### Service Mesh (Istio)

Separates deployment from release:
```
Canary Release:
  90% traffic → v1 (stable)
  10% traffic → v2 (canary)
  
  If v2 metrics are good → shift 100% to v2
  If v2 metrics are bad → shift back to 100% v1
```

---

## ⚡ Pattern 4: Serverless Deployment

No servers to manage — just upload code.

```
AWS Lambda:
  - Upload ZIP/JAR with function code
  - Lambda runs the function on demand
  - You pay per invocation (not idle time)
  - Scales automatically from 0 to millions

Trigger types:
  HTTP → API Gateway → Lambda
  Events → S3, DynamoDB, SQS → Lambda
  Schedule → CloudWatch Events → Lambda

Ideal for:
  Event-driven processing, infrequent tasks, batch jobs
  
Not ideal for:
  Long-running services, services with state, latency-sensitive APIs
```

---

## 💡 Key Takeaways

| Insight | Implication |
|---------|-------------|
| Containers are the standard unit of deployment | Package each service as a Docker image |
| Kubernetes handles orchestration | Use Deployment, Service, ConfigMap, Secret |
| Zero-downtime deployments are achievable | Use rolling updates with readiness probes |
| Service mesh separates deployment from release | Canary and blue-green deployments become easy |
| Serverless is not for everything | Great for event-driven, terrible for long-running services |
| Automate everything | Manual deployment of 50+ services is impossible |

---

*← [Back to Microservices Patterns](../README.md)*
