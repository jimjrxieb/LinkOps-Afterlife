# 📊 AfterLife Monitoring Stack

Complete Prometheus + Grafana monitoring setup with best practices for production deployment.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Monitoring Stack                      │
├─────────────────────────────────────────────────────────┤
│  Caddy Proxy → Grafana (3001) + Main App (80/443)     │
│       ↓                                                │
│  Prometheus (internal) ← scrapes ←┐                   │
│       ↓                            │                   │
│  ┌─────────────────┬─────────────────┬──────────────┐  │
│  │   Backend       │  Node Exporter  │  cAdvisor    │  │
│  │   /metrics      │  System Metrics │  Container   │  │
│  │   API Metrics   │  (CPU, RAM,     │  Metrics     │  │
│  │                 │   Disk, Net)    │              │  │
│  └─────────────────┴─────────────────┴──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

Your monitoring stack is already integrated! When you deploy with `docker-compose.prod.yml`, you get:

- **Prometheus**: Metrics collection at `http://VM_IP:9090` (internal)
- **Grafana**: Dashboards at `https://yourdomain.com:3001`
- **Node Exporter**: System metrics collector
- **cAdvisor**: Container metrics collector

## 🔐 Access

### Grafana Dashboard
- URL: `https://yourdomain.com:3001`
- Username: `admin` (from `GF_ADMIN_USER` in `.env`)
- Password: `change_me_please` (from `GF_ADMIN_PASSWORD` in `.env`)

**⚠️ IMPORTANT**: Change the default password in your `.env` file!

### Prometheus (Internal)
- URL: `http://VM_IP:9090` (not exposed publicly for security)
- Use for debugging queries and checking targets

## 📈 Pre-configured Dashboards

### 1. AfterLife API Overview
- Request rate and response times
- HTTP status codes distribution  
- Active sessions tracking
- Memory usage trends
- API endpoint performance heatmap

### 2. System Metrics
- CPU, Memory, Disk usage
- Network I/O statistics
- Container resource consumption
- Docker container health

## 🔍 Key Metrics Tracked

### FastAPI Application Metrics
```promql
# Request rate
rate(http_requests_total{job="backend"}[5m])

# Response time percentiles
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(http_requests_total{job="backend",status_code=~"5.."}[5m])

# Active sessions (based on upload endpoint hits)
increase(http_requests_total{job="backend",handler="/upload"}[1h])
```

### System Metrics
```promql
# CPU Usage
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory Usage  
100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))

# Disk Usage
100 - (node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100
```

### Container Metrics
```promql
# Container CPU
rate(container_cpu_usage_seconds_total{name=~"afterlife-.*"}[5m]) * 100

# Container Memory
container_memory_usage_bytes{name=~"afterlife-.*"}
```

## ⚙️ Configuration Files

```
monitoring/
├── prometheus/
│   └── prometheus.yml          # Scrape config for all targets
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       │   └── prometheus.yml  # Auto-configure Prometheus datasource
│       └── dashboards/
│           ├── dashboard-config.yml        # Dashboard provider
│           ├── afterlife-overview.json     # API metrics dashboard
│           └── system-metrics.json         # System metrics dashboard
```

## 🛠️ Customization

### Add Custom Metrics to FastAPI
The backend already has `prometheus-fastapi-instrumentator` configured. To add custom metrics:

```python
from prometheus_client import Counter, Histogram

# Custom counter
api_calls = Counter('afterlife_api_calls_total', 'Total API calls', ['endpoint'])

# Custom histogram  
processing_time = Histogram('afterlife_processing_seconds', 'Processing time')

# In your endpoint
@app.post("/process")
async def process_data():
    api_calls.labels(endpoint='process').inc()
    with processing_time.time():
        # Your processing code
        pass
```

### Add New Dashboard
1. Create dashboard in Grafana UI
2. Export as JSON
3. Place in `monitoring/grafana/provisioning/dashboards/`
4. Redeploy or restart Grafana container

### Modify Scrape Targets
Edit `monitoring/prometheus/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'new-service'
    static_configs:
      - targets: ['service:port']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

## 🚨 Alerting Setup

To add Prometheus alerting:

1. Create `monitoring/prometheus/rules/alerts.yml`:
```yaml
groups:
  - name: afterlife.rules
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status_code=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: High error rate detected
```

2. Update `prometheus.yml`:
```yaml
rule_files:
  - "rules/alerts.yml"
```

3. Configure Alertmanager (separate container).

## 🔧 Troubleshooting

### Prometheus Not Scraping Targets
```bash
# Check target status
curl http://VM_IP:9090/api/v1/targets

# Check container logs
docker logs afterlife-prometheus
```

### Grafana Can't Connect to Prometheus
```bash
# Test connectivity from Grafana container
docker exec afterlife-grafana curl http://prometheus:9090/api/v1/query?query=up

# Check datasource config
docker logs afterlife-grafana
```

### Missing Metrics
```bash
# Check if instrumentator is working
curl https://yourdomain.com/metrics

# Verify container is exposing metrics
docker exec afterlife-backend curl http://localhost:8000/metrics
```

### Dashboard Not Loading
```bash
# Check provisioning logs
docker logs afterlife-grafana | grep provision

# Verify dashboard files are mounted
docker exec afterlife-grafana ls -la /etc/grafana/provisioning/dashboards/
```

## 📊 Production Best Practices

### Security
- ✅ Prometheus not exposed publicly (internal port only)
- ✅ Grafana behind HTTPS with authentication
- ⚠️ Change default Grafana admin password
- ⚠️ Consider additional Grafana authentication (LDAP, OAuth)

### Performance
- ✅ 30-day retention for Prometheus data
- ✅ Efficient scrape intervals (10s for API, 15s for system)
- ✅ Resource limits in Docker Compose (add if needed)

### Monitoring
- ✅ Health checks for all containers
- ✅ Grafana dashboards auto-provisioned
- ⚠️ Set up alerting for critical metrics
- ⚠️ Configure backup for Grafana dashboards

### Data Persistence
- ✅ Prometheus data: `prom_data` volume
- ✅ Grafana data: `grafana_data` volume
- ⚠️ Include volumes in backup strategy

## 🔗 Useful Links

- [Prometheus Query Language](https://prometheus.io/docs/prometheus/latest/querying/)
- [Grafana Dashboard Gallery](https://grafana.com/grafana/dashboards/)
- [FastAPI Metrics Best Practices](https://github.com/trallnag/prometheus-fastapi-instrumentator)
- [Node Exporter Metrics](https://github.com/prometheus/node_exporter)
- [cAdvisor Metrics](https://github.com/google/cadvisor/blob/master/docs/storage/prometheus.md)