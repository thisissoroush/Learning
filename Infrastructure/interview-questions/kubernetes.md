# ⚓ Kubernetes — Interview Questions

---

### 1. What is Kubernetes and what problems does it solve?

**A:** Kubernetes (K8s) is an open-source container orchestration system that automates deployment, scaling, and management of containerized applications.

**Problems it solves:**
- **Self-healing** — restarts failed containers, reschedules on healthy nodes
- **Horizontal scaling** — scale pods up/down manually or automatically (HPA)
- **Service discovery & load balancing** — DNS-based service discovery, kube-proxy load balancing
- **Rolling updates & rollbacks** — deploy with zero downtime, roll back on failure
- **Secret & config management** — ConfigMaps and Secrets separate config from code
- **Storage orchestration** — dynamically provision storage (PV/PVC)
- **Resource management** — CPU/memory requests and limits per container

---

### 2. What are the core Kubernetes components?

**A:**

```
Control Plane (Master):
├── kube-apiserver     — REST API server, all communication goes through it
├── etcd              — distributed key-value store (cluster state)
├── kube-scheduler    — assigns pods to nodes based on resources + constraints
├── kube-controller-manager — runs controllers (ReplicaSet, Node, Endpoint, etc.)
└── cloud-controller-manager — integrates with cloud providers (AWS, GCP, Azure)

Worker Nodes:
├── kubelet           — agent on each node, ensures containers run per PodSpec
├── kube-proxy        — network proxy, maintains iptables/IPVS rules for Services
└── container runtime — containerd, CRI-O (implements CRI interface)
```

---

### 3. What is a Pod and why is it the basic unit?

**A:** A Pod is the smallest deployable unit in Kubernetes — one or more containers that share:
- Network namespace (same IP address, same `localhost`)
- Storage (shared volumes)
- Lifecycle (start/stop together)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
  labels:
    app: myapp
    version: "1.0"
spec:
  containers:
    - name: app
      image: myapp:1.0
      ports:
        - containerPort: 8080
      resources:
        requests:
          cpu: "100m"      # 0.1 CPU core
          memory: "128Mi"
        limits:
          cpu: "500m"
          memory: "512Mi"
      env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
      livenessProbe:
        httpGet:
          path: /healthz
          port: 8080
        initialDelaySeconds: 10
        periodSeconds: 15
      readinessProbe:
        httpGet:
          path: /readyz
          port: 8080
        initialDelaySeconds: 5
        periodSeconds: 5

    # Sidecar container — shares network + volumes
    - name: log-shipper
      image: fluent/fluent-bit:2.2
      volumeMounts:
        - name: logs
          mountPath: /var/log/app

  volumes:
    - name: logs
      emptyDir: {}

  # Pod-level settings
  restartPolicy: Always
  serviceAccountName: myapp-sa
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
```

---

### 4. What is the difference between Deployment, StatefulSet, DaemonSet, and Job?

**A:**

| Workload | Use for | Key feature |
|----------|---------|-------------|
| `Deployment` | Stateless apps (web servers, APIs) | Rolling updates, replica management |
| `StatefulSet` | Stateful apps (databases, Kafka, Zookeeper) | Stable pod identity, ordered deployment |
| `DaemonSet` | Node-level agents (log shippers, monitoring) | One pod per node |
| `Job` | One-time batch tasks | Runs to completion |
| `CronJob` | Scheduled batch tasks | Cron schedule |
| `ReplicaSet` | Rarely used directly (Deployment manages it) | Maintains pod count |

```yaml
# StatefulSet — stable identity (pod-0, pod-1, pod-2)
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres-headless   # required
  replicas: 3
  selector:
    matchLabels:
      app: postgres
  template:
    spec:
      containers:
        - name: postgres
          image: postgres:16
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:            # PVC per pod (pod-0 gets data-postgres-0, etc.)
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: gp2
        resources:
          requests:
            storage: 10Gi
```

---

### 5. What are Services and what types exist?

**A:** A Service provides a stable network endpoint for pods (which have ephemeral IPs):

```yaml
# ClusterIP (default) — internal only
apiVersion: v1
kind: Service
metadata:
  name: myapp-svc
spec:
  selector:
    app: myapp           # routes to pods with this label
  ports:
    - port: 80           # service port
      targetPort: 8080   # container port
  type: ClusterIP        # only accessible within cluster

---
# NodePort — exposes on every node's IP at a static port
spec:
  type: NodePort
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 30080    # 30000-32767 range

---
# LoadBalancer — provisions cloud LB (AWS ELB, GCP LB, etc.)
spec:
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: 8080

---
# ExternalName — DNS alias to external service
spec:
  type: ExternalName
  externalName: mydb.external.company.com

---
# Headless — no ClusterIP, DNS returns pod IPs directly (StatefulSets)
spec:
  clusterIP: None
  selector:
    app: postgres
```

---

### 6. What is an Ingress and how does it work?

**A:** Ingress manages external HTTP/HTTPS access to services, providing routing, SSL termination, and virtual hosting:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/rate-limit: "100"
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx       # which ingress controller
  tls:
    - hosts:
        - myapp.example.com
      secretName: myapp-tls     # TLS cert stored in Secret

  rules:
    - host: myapp.example.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: api-service
                port:
                  number: 80
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend-service
                port:
                  number: 80

    - host: admin.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: admin-service
                port:
                  number: 80
```

---

### 7. What are ConfigMaps and Secrets?

**A:**

```yaml
# ConfigMap — non-sensitive configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  LOG_LEVEL: "info"
  MAX_CONNECTIONS: "100"
  config.yaml: |
    server:
      port: 8080
    database:
      pool_size: 10

---
# Secret — sensitive data (base64 encoded, not encrypted by default)
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  DB_PASSWORD: cGFzc3dvcmQ=   # base64("password")
stringData:
  DB_URL: "postgres://user:password@db:5432/mydb"  # auto-encoded
```

```yaml
# Use in Pod
spec:
  containers:
    - name: app
      # As environment variables
      envFrom:
        - configMapRef:
            name: app-config
        - secretRef:
            name: db-secret

      # Individual env var from ConfigMap
      env:
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: LOG_LEVEL

      # Mount as files
      volumeMounts:
        - name: config
          mountPath: /app/config
          readOnly: true

  volumes:
    - name: config
      configMap:
        name: app-config
        items:
          - key: config.yaml
            path: config.yaml
```

---

### 8. What are resource requests and limits?

**A:**

```yaml
resources:
  requests:       # guaranteed resources — used for scheduling decisions
    cpu: "100m"   # 0.1 CPU core (100 millicores)
    memory: "128Mi"
  limits:         # maximum — enforced by cgroups
    cpu: "500m"   # 0.5 CPU core
    memory: "512Mi"
```

**What happens when limits are exceeded:**
- **CPU** → throttled (slowed down, not killed)
- **Memory** → OOMKilled (process killed by kernel)

**Quality of Service (QoS) classes:**
- `Guaranteed` — requests == limits (highest priority, last to be evicted)
- `Burstable` — requests < limits (medium priority)
- `BestEffort` — no requests/limits set (first evicted under pressure)

```yaml
# LimitRange — set defaults for a namespace
apiVersion: v1
kind: LimitRange
metadata:
  name: defaults
spec:
  limits:
    - type: Container
      default:
        cpu: "200m"
        memory: "256Mi"
      defaultRequest:
        cpu: "100m"
        memory: "128Mi"
      max:
        cpu: "2"
        memory: "2Gi"
```

---

### 9. What is the Horizontal Pod Autoscaler (HPA)?

**A:**

```yaml
# Scale based on CPU (classic)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70   # scale up when avg CPU > 70%

    - type: Resource
      resource:
        name: memory
        target:
          type: AverageValue
          averageValue: 400Mi

    # Custom metric (requires metrics-server + adapter)
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "100"

  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300    # wait 5 min before scaling down
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0     # scale up immediately
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
```

```bash
# KEDA — event-driven autoscaling (Kafka lag, queue depth, etc.)
# Scales to zero when no events
```

---

### 10. How do rolling updates and rollbacks work?

**A:**

```yaml
# Deployment update strategy
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0    # never take a pod down before replacement is ready
      maxSurge: 1          # max extra pods during update

  # OR: Recreate — all pods killed, then new ones created (downtime)
  strategy:
    type: Recreate
```

```bash
# Update image
kubectl set image deployment/myapp app=myapp:2.0
kubectl rollout status deployment/myapp   # watch progress

# Annotate for history
kubectl annotate deployment/myapp kubernetes.io/change-cause="Release v2.0"

# Check history
kubectl rollout history deployment/myapp
kubectl rollout history deployment/myapp --revision=2

# Rollback
kubectl rollout undo deployment/myapp                    # to previous
kubectl rollout undo deployment/myapp --to-revision=2    # to specific

# Pause/resume (canary manual testing)
kubectl rollout pause deployment/myapp
kubectl rollout resume deployment/myapp
```

---

### 11. What are namespaces and how do you use them?

**A:**

```bash
# Namespaces provide logical isolation within a cluster
kubectl get namespaces
# default        — default namespace for resources
# kube-system    — Kubernetes system components
# kube-public    — publicly readable resources
# kube-node-lease — node heartbeat leases

# Create namespace
kubectl create namespace production
kubectl create namespace staging

# Work in a namespace
kubectl get pods -n production
kubectl get all -n production

# Set default namespace for kubectl
kubectl config set-context --current --namespace=production
```

```yaml
# Apply namespace to resource
metadata:
  namespace: production

# ResourceQuota — limit resources per namespace
apiVersion: v1
kind: ResourceQuota
metadata:
  name: production-quota
  namespace: production
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    pods: "50"
    services: "20"
    persistentvolumeclaims: "10"
```

---

### 12. What are Persistent Volumes and Persistent Volume Claims?

**A:**

```yaml
# PersistentVolume — cluster-level storage resource
apiVersion: v1
kind: PersistentVolume
metadata:
  name: postgres-pv
spec:
  capacity:
    storage: 20Gi
  accessModes:
    - ReadWriteOnce      # one node at a time
    # ReadOnlyMany       — multiple nodes, read-only
    # ReadWriteMany      — multiple nodes, read-write (NFS, EFS)
  reclaimPolicy: Retain  # Keep after PVC deleted (Recycle, Delete)
  storageClassName: gp2
  awsElasticBlockStore:
    volumeID: vol-0abc123
    fsType: ext4

---
# PersistentVolumeClaim — namespace-level request for storage
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: gp2   # dynamic provisioning via StorageClass
  resources:
    requests:
      storage: 20Gi

---
# StorageClass — dynamic provisioning
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
reclaimPolicy: Delete
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
```

---

### 13. What is RBAC in Kubernetes?

**A:**

```yaml
# ServiceAccount — identity for pods
apiVersion: v1
kind: ServiceAccount
metadata:
  name: myapp-sa
  namespace: production

---
# Role — namespaced permissions
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: production
rules:
  - apiGroups: [""]
    resources: ["pods", "pods/log"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list"]

---
# RoleBinding — bind role to ServiceAccount
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: myapp-pod-reader
  namespace: production
subjects:
  - kind: ServiceAccount
    name: myapp-sa
    namespace: production
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io

---
# ClusterRole + ClusterRoleBinding — cluster-wide permissions
# (same structure but Kind: ClusterRole / ClusterRoleBinding)
```

---

### 14. How do liveness, readiness, and startup probes work?

**A:**

```yaml
containers:
  - name: app
    # Liveness probe — is the container alive?
    # Fails → container is restarted
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 30    # wait before first check
      periodSeconds: 15          # check every 15s
      timeoutSeconds: 5          # timeout per check
      failureThreshold: 3        # fail after 3 consecutive failures

    # Readiness probe — is the container ready to receive traffic?
    # Fails → removed from Service endpoints (no traffic, not restarted)
    readinessProbe:
      httpGet:
        path: /readyz
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 5
      failureThreshold: 3

    # Startup probe — for slow-starting containers
    # Disables liveness/readiness until it succeeds
    startupProbe:
      httpGet:
        path: /healthz
        port: 8080
      failureThreshold: 30       # 30 * 10s = 5 minutes to start
      periodSeconds: 10

    # Probe types:
    # httpGet    — HTTP GET request (2xx-3xx = success)
    # tcpSocket  — TCP connection attempt
    # exec       — run command inside container (exit 0 = success)
    # grpc       — gRPC health protocol
```

---

### 15. What is Helm and why do you use it?

**A:** Helm is the package manager for Kubernetes — it templates and manages complex K8s manifests:

```bash
# Install a chart from repository
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install my-postgres bitnami/postgresql \
  --set auth.password=mypassword \
  --set primary.persistence.size=20Gi \
  --namespace production

# List releases
helm list -n production

# Upgrade
helm upgrade my-postgres bitnami/postgresql --set auth.password=newpass

# Rollback
helm rollback my-postgres 1   # rollback to revision 1

# Uninstall
helm uninstall my-postgres -n production

# Create your own chart
helm create myapp
# generates: Chart.yaml, values.yaml, templates/
```

```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "myapp.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  template:
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
```

---

### 16. What is a NetworkPolicy?

**A:**

```yaml
# Default deny all ingress
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
  namespace: production
spec:
  podSelector: {}    # applies to all pods
  policyTypes:
    - Ingress
    - Egress
  # No rules = deny all

---
# Allow only specific traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-policy
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
    - Ingress
    - Egress
  ingress:
    # Allow from frontend pods
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - port: 8080

    # Allow from monitoring namespace
    - from:
        - namespaceSelector:
            matchLabels:
              name: monitoring
      ports:
        - port: 9090

  egress:
    # Allow to database
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - port: 5432
    # Allow DNS
    - ports:
        - port: 53
          protocol: UDP
```

---

### 17. What are Pod Disruption Budgets?

**A:**

```yaml
# Ensure minimum availability during voluntary disruptions (node drain, updates)
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: myapp-pdb
spec:
  minAvailable: 2          # always keep at least 2 pods running
  # OR: maxUnavailable: 1  # allow at most 1 pod down at a time
  selector:
    matchLabels:
      app: myapp
```

Voluntary disruptions: node drain, cluster upgrades, node scaling down
Involuntary: node failure, OOM kill

Without PDB, a `kubectl drain node` could evict ALL pods on that node simultaneously.

---

### 18. How do you implement zero-downtime deployments?

**A:**

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0   # never kill old pod before new one is ready
      maxSurge: 1

  template:
    spec:
      # 1. Readiness probe — only send traffic when ready
      readinessProbe:
        httpGet: { path: /readyz, port: 8080 }
        initialDelaySeconds: 5
        periodSeconds: 5

      # 2. Graceful shutdown — handle SIGTERM
      terminationGracePeriodSeconds: 30

      containers:
        - lifecycle:
            # 3. preStop hook — give time for LB to drain
            preStop:
              exec:
                command: ["sleep", "10"]
```

```yaml
# 4. PodDisruptionBudget
spec:
  minAvailable: 1

# 5. Anti-affinity — spread across nodes
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchLabels:
            app: myapp
        topologyKey: kubernetes.io/hostname
```

---

### 19. How do you handle secrets management in Kubernetes?

**A:**

```bash
# K8s Secrets are base64 encoded, NOT encrypted by default
# Stored as plaintext in etcd unless encryption at rest is configured

# Better options:
# 1. etcd encryption at rest
# 2. HashiCorp Vault + Vault Agent Injector
# 3. External Secrets Operator (AWS SSM, Azure Key Vault, GCP Secret Manager)
# 4. Sealed Secrets (encrypted secrets committed to git)
```

```yaml
# External Secrets Operator — sync from AWS Secrets Manager
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-store
    kind: ClusterSecretStore
  target:
    name: db-secret      # creates K8s Secret
    creationPolicy: Owner
  data:
    - secretKey: DB_PASSWORD
      remoteRef:
        key: production/myapp/db
        property: password
```

---

### 20. What is the difference between `kubectl apply` and `kubectl create`?

**A:**

```bash
# create — imperative, fails if resource already exists
kubectl create deployment myapp --image=myapp:1.0

# apply — declarative, creates or updates, idempotent
kubectl apply -f deployment.yaml
kubectl apply -f ./k8s/           # apply all files in directory
kubectl apply -k ./k8s/overlays/prod  # Kustomize

# delete
kubectl delete -f deployment.yaml
kubectl delete deployment myapp

# diff — preview changes before applying
kubectl diff -f deployment.yaml

# dry-run — validate without applying
kubectl apply -f deployment.yaml --dry-run=client
kubectl apply -f deployment.yaml --dry-run=server   # server-side validation
```

---

### 21. How do you debug pods in Kubernetes?

**A:**

```bash
# Pod status and events
kubectl describe pod myapp-abc123
kubectl get events --sort-by='.lastTimestamp' -n production

# Logs
kubectl logs myapp-abc123
kubectl logs myapp-abc123 -c sidecar      # specific container
kubectl logs myapp-abc123 --previous      # previous container (after crash)
kubectl logs -l app=myapp --all-containers  # all pods with label
kubectl logs myapp-abc123 -f --tail=100   # follow

# Shell access
kubectl exec -it myapp-abc123 -- /bin/sh
kubectl exec -it myapp-abc123 -c sidecar -- sh

# Port forward for local debugging
kubectl port-forward pod/myapp-abc123 8080:8080
kubectl port-forward service/myapp-svc 8080:80

# Ephemeral debug containers (no exec available on distroless)
kubectl debug -it myapp-abc123 --image=busybox --target=app

# Copy files
kubectl cp myapp-abc123:/app/logs/error.log ./error.log

# Resource usage
kubectl top pods -n production
kubectl top nodes
```

---

### 22. What is Kustomize and how does it work?

**A:** Kustomize is a Kubernetes-native configuration management tool (built into kubectl):

```
k8s/
├── base/                     # common manifests
│   ├── kustomization.yaml
│   ├── deployment.yaml
│   └── service.yaml
└── overlays/
    ├── staging/
    │   ├── kustomization.yaml
    │   └── replica-patch.yaml
    └── production/
        ├── kustomization.yaml
        └── resource-patch.yaml
```

```yaml
# base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
  - service.yaml
commonLabels:
  app: myapp

# overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
bases:
  - ../../base
namespace: production
images:
  - name: myapp
    newTag: "2.0.1"
patches:
  - path: replica-patch.yaml
replicas:
  - name: myapp
    count: 5
configMapGenerator:
  - name: app-config
    envs:
      - config.env
```

```bash
kubectl apply -k k8s/overlays/production
kubectl diff -k k8s/overlays/production
```

---

### 23. How does Kubernetes scheduling work?

**A:**

```yaml
# Node affinity — prefer/require specific nodes
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:  # hard requirement
      nodeSelectorTerms:
        - matchExpressions:
            - key: topology.kubernetes.io/zone
              operator: In
              values: [us-east-1a, us-east-1b]
    preferredDuringSchedulingIgnoredDuringExecution:  # soft preference
      - weight: 100
        preference:
          matchExpressions:
            - key: node-type
              operator: In
              values: [high-memory]

# Pod anti-affinity — spread pods across nodes/zones
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchLabels:
              app: myapp
          topologyKey: topology.kubernetes.io/zone

# Taints and tolerations — reserve nodes for specific workloads
# Taint a node:
# kubectl taint nodes gpu-node gpu=true:NoSchedule
tolerations:
  - key: "gpu"
    operator: "Equal"
    value: "true"
    effect: "NoSchedule"

# Resource-based scheduling
# Scheduler finds nodes where sum(pod.requests) <= node.allocatable
nodeSelector:
  accelerator: nvidia-tesla-v100
```

---

### 24. What is a Kubernetes Operator?

**A:** An Operator extends Kubernetes to manage complex, stateful applications using custom resources and controllers:

```yaml
# Custom Resource Definition
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: postgresclusters.postgres-operator.crunchydata.com
spec:
  group: postgres-operator.crunchydata.com
  versions:
    - name: v1beta1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                instances:
                  type: array
  scope: Namespaced
  names:
    plural: postgresclusters
    singular: postgrescluster
    kind: PostgresCluster

---
# Use the custom resource
apiVersion: postgres-operator.crunchydata.com/v1beta1
kind: PostgresCluster
metadata:
  name: mydb
spec:
  instances:
    - name: instance1
      replicas: 3
      dataVolumeClaimSpec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 100Gi
  backups:
    pgbackrest:
      repos:
        - name: repo1
          s3:
            bucket: mybackupbucket
            region: us-east-1
```

Popular operators: PostgreSQL (CrunchyData), Kafka (Strimzi), Prometheus (Prometheus Operator), Elasticsearch (ECK).

---

### 25. How do you monitor a Kubernetes cluster?

**A:**

```yaml
# Prometheus + Grafana (kube-prometheus-stack helm chart)
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set grafana.adminPassword=secret

# Key metrics to monitor:
# Node level:
#   node_cpu_utilization, node_memory_utilization, node_disk_pressure
# Pod level:
#   container_cpu_usage_seconds_total, container_memory_working_set_bytes
#   kube_pod_status_phase (Pending/Running/Failed)
# Kubernetes objects:
#   kube_deployment_status_replicas_available
#   kube_deployment_spec_replicas
#   kube_pod_container_status_restarts_total

# ServiceMonitor — auto-discover services to scrape
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: myapp-monitor
spec:
  selector:
    matchLabels:
      app: myapp
  endpoints:
    - port: metrics
      path: /metrics
      interval: 30s
```

```bash
# Metrics server (for kubectl top and HPA)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Check cluster health
kubectl get nodes
kubectl get componentstatuses
kubectl get events --all-namespaces --sort-by='.lastTimestamp' | tail -50
```
