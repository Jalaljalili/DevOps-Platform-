# FastAPI + Redis Platform (DevOps Assignment)

This repository contains a production-oriented DevOps setup for a small platform composed of:
- **FastAPI service** that reads/writes values in **Redis**
- **Containerized build** with an optimized Dockerfile
- **Kubernetes deployment** using **Helm** (app + Redis dependency)
- **CI/CD pipeline** (GitHub Actions): test → build/push → deploy
- **Centralized logging** (Loki + Promtail)
- **Monitoring** (kube-prometheus-stack)
- **Performance testing** (k6) with thresholds

---

## Repository Structure

- `app/`  
  FastAPI source code, optimized Dockerfile, requirements.
- `helm/`  
  Helm chart to deploy the app + Redis (via Bitnami dependency), plus HPA.
- `.github/`  
  GitHub Actions CI/CD workflow (`ci-cd.yaml`).
- `observability/`  
  Loki + Promtail values + install commands for log collection.
- `monitoring/`  
  kube-prometheus-stack values + install commands for metrics.
- `perf/`  
  k6 load test script and run instructions.
- `docs/`  
  Decision documentation and justifications.

---

## Requirements

### Local (optional)
- Docker (for local container build/run)
- Docker Compose (optional, for local app+redis quick run)

### Kubernetes deployment
- Kubernetes cluster (minikube/kind or managed)
- `kubectl`
- `helm`

### CI/CD
- GitHub repository
- GitHub Actions enabled
- Container registry: **GHCR** (GitHub Container Registry)

### Observability / Monitoring
- Helm repos access:
  - Grafana charts (Loki stack)
  - Prometheus community charts (kube-prometheus-stack)

### Performance test
- `k6`

---

## Application Endpoints

- `GET /healthz`  
  Liveness endpoint (always returns OK if app is running)
- `GET /readyz`  
  Readiness endpoint (returns ready only if Redis is reachable)
- `GET /`  
  Reads Redis key `example_key`
- `POST /write/{key}?value=...`  
  Writes `{key} => value` into Redis

---

## Run Locally

### 1) Install dependencies (optional)
```bash
cd app
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2) Run with Docker (app only)

```bash
docker build -t fastapi-redis:local ./app
docker run --rm -p 8000:8000 fastapi-redis:local
```
For full local functionality you must run Redis too (e.g., docker compose or a local redis container).

### 3) Quick local Redis (example)

```bash
docker run --rm -d --name redis -p 6379:6379 redis:7
export REDIS_HOST=127.0.0.1
export REDIS_PORT=6379
cd app
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Kubernetes Deployment (Helm)
### 1) Add Helm repos

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```
### 2)Deploy
From repo root:

```bash
helm dependency update helm/platform
helm upgrade --install platform helm/platform \
  -n platform --create-namespace \
  --set image.repository=ghcr.io/ORG/fastapi-redis \
  --set image.tag=latest
```

### 3) Access service (port-forward)

```bash
kubectl -n platform port-forward svc/platform 8000:8000
curl http://127.0.0.1:8000/healthz
```

## CI/CD (GitHub Actions)

Workflow file: .github/workflows/ci-cd.yaml

Pipeline stages:

- test: basic import check after installing requirements

- build_and_push: builds Docker image and pushes to GHCR

- deploy: deploys via Helm to Kubernetes using kubeconfig secret

### Required GitHub Secrets

Set these in: Repository → Settings → Secrets and variables → Actions

* IMAGE_REPO
Example: ghcr.io/<org-or-user>/<image-name>

* KUBECONFIG_B64
Base64 encoded kubeconfig (cluster access with deploy permissions)

* KUBE_NAMESPACE
Example: platform

* HELM_RELEASE
Example: platform

Create kubeconfig base64:

```bash
base64 -w 0 ~/.kube/config
```

## Logging (All Services)

Tooling: Loki + Promtail

Promtail collects stdout/stderr logs from all pods in the cluster/namespace and ships to Loki with Kubernetes labels (namespace/pod/container).

Install:

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
helm upgrade --install loki grafana/loki-stack \
  -n observability --create-namespace \
  -f observability/loki-promtail/values.yaml
```

## Monitoring

Tooling: kube-prometheus-stack (Prometheus Operator bundle)

Install:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace \
  -f monitoring/kube-prometheus-stack/values.yaml
```
## Performance Testing (k6)

Run load test:

```bash
k6 run -e BASE_URL=http://127.0.0.1:8000 perf/k6/loadtest.js
```
This test includes thresholds:

* http_req_failed < 1%

* p95 latency < 300ms

## Notes on Optimization Choices

### Dockerfile:

* python:3.9-slim for smaller image

* dependency caching by copying requirements.txt first

* non-root user runtime

* gunicorn + uvicorn worker for higher throughput

### Kubernetes:

* readiness probe depends on Redis connectivity

* resources requests/limits for predictable scheduling

* HPA enabled for CPU-based autoscaling

### Logging:

* Loki+Promtail: Kubernetes-native discovery, low overhead, no app changes required

All decision justifications are documented in docs/DECISIONS.md.