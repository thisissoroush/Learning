# 🐳 Docker — Interview Questions

---

### 1. What is Docker and how does it differ from a virtual machine?

**A:** Docker is a containerization platform that packages applications and their dependencies into lightweight, portable containers.

| | Docker Container | Virtual Machine |
|--|-----------------|----------------|
| OS | Shares host kernel | Full guest OS |
| Size | MBs | GBs |
| Startup | Milliseconds | Minutes |
| Isolation | Process-level (namespaces + cgroups) | Hardware-level (hypervisor) |
| Overhead | Very low | High |

Containers use **Linux namespaces** (PID, network, mount, UTS, IPC) for isolation and **cgroups** (control groups) to limit CPU, memory, and I/O.

---

### 2. What is the difference between an image and a container?

**A:**
- **Image** — a read-only, layered blueprint (filesystem + metadata). Built from a Dockerfile. Can be stored in a registry.
- **Container** — a running instance of an image. Adds a writable layer on top.

```bash
# Image operations
docker build -t myapp:1.0 .
docker pull postgres:16-alpine
docker push myregistry.io/myapp:1.0
docker images
docker rmi myapp:1.0

# Container operations
docker run -d --name myapp -p 8080:8080 myapp:1.0
docker ps           # running containers
docker ps -a        # all containers
docker stop myapp
docker rm myapp
docker logs myapp --follow
docker exec -it myapp /bin/sh
```

---

### 3. What is a Dockerfile and what are the most important instructions?

**A:**

```dockerfile
# Base image
FROM golang:1.22-alpine AS builder

# Set metadata
LABEL maintainer="team@mycompany.com"
LABEL version="1.0"

# Set working directory
WORKDIR /app

# Copy dependency files first (better cache utilization)
COPY go.mod go.sum ./
RUN go mod download

# Copy source
COPY . .

# Build
RUN CGO_ENABLED=0 GOOS=linux go build -o server ./cmd/server

# ── Final image ──
FROM alpine:3.19

WORKDIR /app

# Copy only the binary
COPY --from=builder /app/server .
COPY --from=builder /app/configs ./configs

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# Document port (informational only)
EXPOSE 8080

# Environment variable with default
ENV LOG_LEVEL=info

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -qO- http://localhost:8080/health || exit 1

# Entrypoint vs CMD:
# ENTRYPOINT ["./server"]       — always runs, CMD are default args
# CMD ["--config", "prod.yaml"] — overridable at docker run
ENTRYPOINT ["./server"]
CMD ["--config", "configs/prod.yaml"]
```

---

### 4. What is a multi-stage build and why is it important?

**A:** Multi-stage builds use multiple `FROM` statements — each stage can copy artifacts from previous stages. Produces a minimal final image:

```dockerfile
# Stage 1: Build (large — includes compiler, SDK, dev tools)
FROM node:20 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Dependencies only (production)
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Stage 3: Final (minimal — no build tools)
FROM node:20-alpine
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
USER node
EXPOSE 3000
CMD ["node", "dist/index.js"]

# Result: 800MB builder → 120MB final image
```

---

### 5. How does Docker layer caching work and how do you optimize it?

**A:** Each instruction in a Dockerfile creates a layer. Docker caches layers — if a layer's inputs haven't changed, it reuses the cached layer.

```dockerfile
# BAD — COPY . . early invalidates cache on any file change
FROM python:3.12
COPY . .                    # any change here busts all subsequent layers
RUN pip install -r requirements.txt  # reinstalls every time

# GOOD — copy dependency files first, code last
FROM python:3.12
COPY requirements.txt .     # cached as long as requirements.txt unchanged
RUN pip install -r requirements.txt  # cached unless requirements change
COPY . .                    # only this layer busts on code changes
RUN python -m pytest
```

**Cache-busting strategies:**
```bash
# Force no cache
docker build --no-cache .

# Build args to bust specific layers
ARG CACHE_BUST=1
RUN --mount=type=cache,target=/root/.cache/pip pip install ...
```

---

### 6. What are Docker volumes and bind mounts?

**A:**

| | Volume | Bind Mount | tmpfs |
|--|--------|-----------|-------|
| Storage | Docker managed (`/var/lib/docker/volumes`) | Host filesystem path | RAM only |
| Portability | High | Low (host-dependent) | N/A |
| Use for | Persistent data, DB files | Dev hot-reload, config | Secrets, temp data |

```bash
# Named volume — managed by Docker
docker run -v mydata:/var/lib/postgresql/data postgres:16

# Bind mount — mounts host directory
docker run -v $(pwd)/src:/app/src myapp   # dev hot-reload

# Read-only bind mount
docker run -v $(pwd)/config:/app/config:ro myapp

# tmpfs — in-memory, not persisted
docker run --tmpfs /tmp myapp

# Volume management
docker volume create mydata
docker volume ls
docker volume inspect mydata
docker volume rm mydata
docker volume prune     # remove unused volumes
```

---

### 7. How does Docker networking work?

**A:** Docker provides several network drivers:

| Driver | Use case |
|--------|----------|
| `bridge` (default) | Isolated containers on single host; DNS by container name |
| `host` | Container shares host network stack (Linux only) |
| `none` | No networking |
| `overlay` | Multi-host networking (Docker Swarm, Kubernetes) |
| `macvlan` | Container gets its own MAC/IP on host network |

```bash
# Create a network
docker network create mynet

# Connect containers — they can reach each other by name
docker run -d --name postgres --network mynet postgres:16
docker run -d --name app --network mynet myapp
# app can reach postgres at "postgres:5432"

# Inspect
docker network ls
docker network inspect mynet

# Port mapping (host:container)
docker run -p 8080:80 nginx         # host 8080 → container 80
docker run -p 127.0.0.1:8080:80 nginx  # localhost only
docker run -p 80 nginx              # random host port
```

---

### 8. What is Docker Compose and when do you use it?

**A:** Docker Compose defines and runs multi-container applications via a YAML file:

```yaml
# docker-compose.yml
version: "3.9"

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: development        # specific stage for dev
    image: myapp:dev
    ports:
      - "8080:8080"
    environment:
      DATABASE_URL: postgres://user:pass@db:5432/mydb
      REDIS_URL: redis://cache:6379
    env_file:
      - .env.local
    volumes:
      - .:/app                   # hot-reload in dev
      - /app/node_modules        # anonymous volume to preserve node_modules
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
    networks:
      - backend
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - backend

  cache:
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redisdata:/data
    networks:
      - backend

volumes:
  pgdata:
  redisdata:

networks:
  backend:
    driver: bridge
```

```bash
docker compose up -d              # start in background
docker compose up --build         # rebuild images
docker compose down               # stop + remove containers
docker compose down -v            # + remove volumes
docker compose logs app -f        # follow logs
docker compose exec app sh        # shell into service
docker compose ps                 # status
docker compose scale app=3        # scale (without orchestrator)
```

---

### 9. How do you handle environment variables and secrets in Docker?

**A:**

```bash
# Pass at runtime
docker run -e DB_PASSWORD=secret myapp

# From file
docker run --env-file .env myapp

# Docker secrets (Swarm mode)
echo "mysecretpassword" | docker secret create db_password -
docker service create --secret db_password myapp
# Secret available at /run/secrets/db_password in container

# Build-time args (visible in image history — don't use for secrets)
docker build --build-arg API_KEY=key .
```

```dockerfile
# Use ARG for build-time, ENV for runtime
ARG NODE_ENV=production
ENV NODE_ENV=${NODE_ENV}

# NEVER do this — secret visible in image layers
RUN curl -H "Authorization: Bearer ${SECRET_TOKEN}" ...

# Instead: use BuildKit secret mounts
RUN --mount=type=secret,id=mysecret \
    cat /run/secrets/mysecret | do_something
```

```bash
# Build with secret (never stored in image)
DOCKER_BUILDKIT=1 docker build --secret id=mysecret,src=./mysecret.txt .
```

---

### 10. What is `.dockerignore` and why is it important?

**A:** Like `.gitignore` — excludes files from the build context sent to the Docker daemon:

```dockerignore
# .dockerignore
.git
.gitignore
node_modules
npm-debug.log
.env
.env.*
*.test.js
coverage/
dist/
.DS_Store
Dockerfile*
docker-compose*
README.md
docs/
.github/
```

**Why it matters:**
- Smaller build context → faster `docker build`
- Prevents leaking secrets (`.env` files) into image
- Prevents invalidating cache due to `.git` changes
- Without it, entire project directory is sent to daemon on every build

---

### 11. How do you reduce Docker image size?

**A:**

```dockerfile
# 1. Use minimal base images
FROM alpine:3.19         # ~5MB instead of ubuntu ~75MB
FROM python:3.12-slim    # slim variant
FROM gcr.io/distroless/python3  # distroless — no shell, no package manager

# 2. Multi-stage builds (compile in fat image, ship in slim)

# 3. Combine RUN commands — fewer layers
# BAD
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*

# GOOD
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# 4. Don't copy unnecessary files (use .dockerignore)

# 5. Use specific versions (reproducible + smaller)
FROM node:20.10-alpine3.19

# 6. Remove build artifacts
RUN go build -o server && \
    rm -rf /go/src /root/.cache
```

```bash
# Analyze image layers
docker image history myapp:1.0
dive myapp:1.0   # third-party tool for layer analysis
```

---

### 12. How do you run containers as non-root?

**A:**

```dockerfile
# Create dedicated user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Or in Alpine
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Set file ownership
COPY --chown=appuser:appgroup . .

# Switch to non-root
USER appuser

# Verify: container process runs as non-root
# docker run myapp id → uid=1000(appuser) gid=1000(appgroup)
```

```yaml
# docker-compose.yml — override user
services:
  app:
    user: "1000:1000"

  # Or use security_opt
  db:
    security_opt:
      - no-new-privileges:true
```

Running as root in containers is a serious security risk — a container escape vulnerability would give root access to the host.

---

### 13. What is Docker BuildKit and what does it add?

**A:** BuildKit is the modern build engine (default since Docker 23). Key features:

```bash
# Enable explicitly (older Docker)
DOCKER_BUILDKIT=1 docker build .

# Features:
# 1. Parallel stage execution
# 2. Better cache (skips unused stages)
# 3. Secret mounts (never stored in image)
RUN --mount=type=secret,id=npmrc cat /run/secrets/npmrc >> ~/.npmrc && npm install

# 4. SSH forwarding
RUN --mount=type=ssh git clone git@github.com:private/repo.git

# 5. Cache mounts — persist cache between builds
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
RUN --mount=type=cache,target=/go/pkg/mod go mod download

# 6. Inline Dockerfile syntax version
# syntax=docker/dockerfile:1.5
```

---

### 14. How do you implement Docker health checks?

**A:**

```dockerfile
# Dockerfile health check
HEALTHCHECK --interval=30s \
            --timeout=10s \
            --start-period=40s \
            --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1
# exit 0 = healthy, exit 1 = unhealthy
```

```yaml
# docker-compose.yml — override or add health check
services:
  app:
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
```

```bash
docker inspect --format='{{json .State.Health}}' mycontainer
```

---

### 15. How do you debug a running container?

**A:**

```bash
# Shell access
docker exec -it mycontainer sh
docker exec -it mycontainer bash

# Run as root to debug (even if USER is set)
docker exec -it --user root mycontainer sh

# Copy files from container
docker cp mycontainer:/app/logs/error.log ./error.log

# Inspect container details
docker inspect mycontainer
docker inspect --format='{{.State.ExitCode}}' mycontainer
docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mycontainer

# Resource usage
docker stats
docker stats mycontainer --no-stream

# Attach to running process stdout/stderr
docker attach mycontainer   # careful — Ctrl+C kills the container

# Check container logs
docker logs mycontainer
docker logs mycontainer --tail=100
docker logs mycontainer --since=1h
docker logs mycontainer -f 2>&1 | grep ERROR

# Inspect filesystem layers
docker diff mycontainer     # shows modified files

# Create new image from running container (debugging)
docker commit mycontainer debug-snapshot:1
```

---

### 16. What is Docker registry and how do you use it?

**A:**

```bash
# Docker Hub (default)
docker login
docker push myuser/myapp:1.0
docker pull myuser/myapp:1.0

# Private registry
docker login registry.mycompany.com
docker tag myapp:1.0 registry.mycompany.com/myteam/myapp:1.0
docker push registry.mycompany.com/myteam/myapp:1.0

# Run local registry
docker run -d -p 5000:5000 --name registry registry:2
docker tag myapp:1.0 localhost:5000/myapp:1.0
docker push localhost:5000/myapp:1.0

# Image tagging conventions
myapp:latest          # latest (avoid in production — not deterministic)
myapp:1.2.3           # semantic version (preferred)
myapp:1.2             # minor version alias
myapp:git-abc1234     # git commit SHA (CI/CD)
myapp:2024-01-15      # date-based

# Scan image for vulnerabilities
docker scout cves myapp:1.0
trivy image myapp:1.0
```

---

### 17. How do you limit container resources?

**A:**

```bash
# CPU
docker run --cpus="1.5" myapp           # 1.5 CPU cores
docker run --cpu-shares=512 myapp       # relative weight (default 1024)
docker run --cpuset-cpus="0,1" myapp    # pin to specific CPUs

# Memory
docker run --memory="512m" myapp        # hard limit — OOM kill
docker run --memory="512m" --memory-swap="1g" myapp  # includes swap
docker run --memory-reservation="256m" myapp  # soft limit

# Both
docker run --cpus="0.5" --memory="256m" myapp
```

```yaml
# docker-compose.yml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 512M
        reservations:
          cpus: "0.25"
          memory: 256M
```

---

### 18. What is Docker content trust and image signing?

**A:**

```bash
# Enable content trust — only pull signed images
export DOCKER_CONTENT_TRUST=1

docker pull myapp:1.0    # fails if not signed
docker push myapp:1.0    # signs automatically

# Sign with specific key
docker trust sign myapp:1.0

# View signers
docker trust inspect myapp:1.0

# Cosign (modern approach — OCI-based)
cosign sign --key cosign.key myregistry.io/myapp:1.0
cosign verify --key cosign.pub myregistry.io/myapp:1.0
```

---

### 19. What are the key Docker security best practices?

**A:**

```dockerfile
# 1. Non-root user
USER appuser

# 2. Read-only filesystem
# docker run --read-only myapp
# Mount writable volumes only where needed
VOLUME ["/tmp", "/var/log"]

# 3. Minimal base image (smaller attack surface)
FROM gcr.io/distroless/java17-debian12

# 4. Pin exact versions
FROM python:3.12.1-slim-bookworm  # not python:latest

# 5. No secrets in ENV or ARG
# Use Docker secrets, Vault, or secret manager

# 6. Scan at build time
# docker scout cves, trivy, snyk

# 7. Drop capabilities
# docker run --cap-drop ALL --cap-add NET_BIND_SERVICE myapp

# 8. Seccomp / AppArmor profiles
# docker run --security-opt seccomp=seccomp.json myapp
# docker run --security-opt apparmor=docker-default myapp

# 9. No privileged
# NEVER: docker run --privileged myapp

# 10. Sign images (cosign/DCT)
```

---

### 20. How does Docker work under the hood?

**A:**

```
docker run ubuntu echo "hello"

1. Docker CLI sends request to Docker daemon (dockerd) via Unix socket /var/run/docker.sock
2. dockerd checks if image exists locally → pulls from registry if not
3. dockerd creates a container via containerd (higher-level runtime)
4. containerd delegates to runc (OCI runtime) to create the container:
   a. Creates Linux namespaces: PID, NET, MNT, UTS, IPC, USER
   b. Sets up cgroups for resource limits
   c. Sets up OverlayFS filesystem (image layers + writable layer)
5. runc starts the process inside the namespaces
6. Process runs, output goes to Docker log driver
7. Container exits, writable layer is preserved (until docker rm)
```

**Key components:**
- `dockerd` — Docker daemon (API server)
- `containerd` — container lifecycle management (OCI-compliant)
- `runc` — low-level OCI runtime (creates namespaces, cgroups)
- `OverlayFS` — union filesystem for image layers

---

### 21. How do you build images for multiple architectures?

**A:**

```bash
# Create a multi-platform builder
docker buildx create --name multibuilder --use
docker buildx inspect --bootstrap

# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64,linux/arm/v7 \
  --tag myregistry.io/myapp:1.0 \
  --push \
  .

# Inspect manifest
docker manifest inspect myregistry.io/myapp:1.0

# In Dockerfile — handle architecture-specific logic
FROM --platform=$BUILDPLATFORM golang:1.22 AS builder
ARG TARGETOS TARGETARCH
RUN GOOS=$TARGETOS GOARCH=$TARGETARCH go build -o server .
```

---

### 22. What is Docker Swarm and how does it compare to Kubernetes?

**A:**

| | Docker Swarm | Kubernetes |
|--|-------------|-----------|
| Complexity | Simple | Complex |
| Setup | `docker swarm init` | Significant |
| Scaling | Basic | Advanced (HPA, VPA) |
| Networking | Overlay | CNI plugins |
| Storage | Volumes | PV/PVC/StorageClass |
| Auto-healing | Basic | Advanced |
| Ecosystem | Small | Vast |
| Use when | Simple apps, small teams | Production scale |

```bash
# Initialize Swarm
docker swarm init --advertise-addr 192.168.1.1

# Join worker node
docker swarm join --token <token> 192.168.1.1:2377

# Deploy stack (docker-compose.yml compatible)
docker stack deploy -c docker-compose.yml myapp

# Scale service
docker service scale myapp_web=5

# Rolling update
docker service update --image myapp:2.0 --update-delay 30s myapp_web
```

---

### 23. How do you implement a CI/CD pipeline with Docker?

**A:**

```yaml
# GitHub Actions example
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha    # GitHub Actions cache
          cache-to: type=gha,mode=max

      - name: Scan for vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/${{ github.repository }}:${{ github.sha }}
          exit-code: 1
          severity: HIGH,CRITICAL
```

---

### 24. How do you manage Docker logs in production?

**A:**

```bash
# Log drivers
docker run --log-driver json-file \
           --log-opt max-size=10m \
           --log-opt max-file=3 \
           myapp

# Other log drivers
# --log-driver syslog        → syslog
# --log-driver journald      → systemd journal
# --log-driver gelf          → Graylog
# --log-driver fluentd       → Fluentd
# --log-driver awslogs       → CloudWatch
# --log-driver splunk        → Splunk
# --log-driver none          → discard all logs
```

```yaml
# docker-compose.yml — configure globally or per service
services:
  app:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "5"
        labels: "service,version"
        env: "NODE_ENV"

# Production pattern: sidecar log shipper
  fluent-bit:
    image: fluent/fluent-bit:2.2
    volumes:
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - ./fluent-bit.conf:/fluent-bit/etc/fluent-bit.conf
```

---

### 25. What is the difference between `COPY` and `ADD` in Dockerfile?

**A:**

```dockerfile
# COPY — simple, explicit, preferred for most cases
COPY src/ /app/src/
COPY package.json package-lock.json ./

# ADD — extra features (use only when needed)
# 1. Auto-extracts tar archives
ADD app.tar.gz /app/    # extracts automatically

# 2. Downloads from URLs (AVOID — better to use curl + RUN)
ADD https://example.com/file.tar.gz /app/    # downloads + extracts

# Rule: always prefer COPY unless you specifically need ADD's features
# ADD's auto-extraction can cause surprising behavior and cache invalidation
```

---

### 26. How do you optimize Docker for production?

**A:**

```dockerfile
# 1. Distroless final images — no shell, no package manager
FROM gcr.io/distroless/java17-debian12
COPY --from=builder /app/server.jar /app/
CMD ["/app/server.jar"]

# 2. Layer ordering — most stable layers first
FROM python:3.12-slim
COPY requirements.txt .       # stable — cached
RUN pip install -r requirements.txt  # cached unless requirements change
COPY . .                       # changes frequently

# 3. Use .dockerignore aggressively

# 4. Pin base image digest (immutable reference)
FROM python:3.12.1-slim-bookworm@sha256:abc123...

# 5. BuildKit cache mounts for package managers
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# 6. Inline health checks
HEALTHCHECK --interval=30s CMD curl -f http://localhost/health || exit 1
```

```bash
# 7. Regular image cleanup
docker system prune -f                    # remove stopped containers + dangling images
docker system prune -a --volumes -f       # full cleanup
docker image prune -a --filter "until=720h"  # remove images older than 30 days
```
