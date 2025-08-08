# Monitoring Stack

Services:
- Prometheus (9090)
- Grafana (3001)
- Node Exporter (9100, host network)
- cAdvisor (8081 -> 8080 in container)

Local bring-up:
```bash
docker compose up -d prometheus grafana node-exporter cadvisor
```

Prometheus config: `monitoring/prometheus/prometheus.yml`

Grafana provisioning: `monitoring/grafana/provisioning/*`

