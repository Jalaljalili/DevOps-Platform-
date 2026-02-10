helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
helm upgrade --install loki grafana/loki-stack -n observability --create-namespace -f observability/loki-promtail/values.yaml
