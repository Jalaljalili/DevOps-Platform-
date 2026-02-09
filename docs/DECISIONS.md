# Decisions and Justifications

## CI/CD first
- test -> build/push -> deploy to gate deployments.
- concurrency: single deployment lane on main.
- build cache: gha cache for faster and more reliable builds.

Secrets:
- IMAGE_REPO
- KUBECONFIG_B64
- KUBE_NAMESPACE
- HELM_RELEASE

## Dockerfile
- python:3.9-slim to reduce image size.
- cache-friendly layers (requirements first).
- non-root runtime user.
- gunicorn + uvicorn worker for better throughput.

## Logging
Tool: Loki + Promtail
- collects stdout/stderr from all pods with Kubernetes metadata labels.
- efficient label-based indexing and low ops overhead.

## Performance
- liveness/readiness endpoints.
- readiness depends on Redis ping.
- resources + HPA for scaling.
- k6 thresholds for p95 latency and error rate.
