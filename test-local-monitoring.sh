#!/bin/bash
# Test just the monitoring stack locally without building app containers
set -euo pipefail

echo "🧪 AfterLife Monitoring Stack Test"
echo "==================================="

# Stop any existing containers
echo "Stopping any existing containers..."
docker compose -f docker-compose.local.yml down --remove-orphans 2>/dev/null || true

# Start only monitoring services (not frontend/backend)
echo "Starting monitoring stack..."
docker compose -f docker-compose.local.yml up -d prometheus grafana node-exporter cadvisor

echo "Waiting 20 seconds for services to initialize..."
sleep 20

# Check container status
echo ""
echo "📊 Container Status:"
docker compose -f docker-compose.local.yml ps prometheus grafana node-exporter cadvisor

echo ""
echo "🧪 Testing Monitoring Services"
echo "==============================="

# Test Prometheus
echo "Testing Prometheus..."
if curl -sf "http://localhost:9090/-/healthy" > /dev/null 2>&1; then
    echo "✅ Prometheus is healthy"
    # Check if metrics are available
    metric_count=$(curl -s "http://localhost:9090/api/v1/label/__name__/values" | python3 -c "import json,sys; data=json.load(sys.stdin); print(len(data.get('data', [])))" 2>/dev/null || echo "0")
    echo "📊 Prometheus has $metric_count metrics available"
else
    echo "❌ Prometheus health check failed"
fi

# Test Grafana
echo ""
echo "Testing Grafana..."
if curl -sf "http://localhost:3001/api/health" > /dev/null 2>&1; then
    echo "✅ Grafana is healthy"
    health_response=$(curl -s "http://localhost:3001/api/health" 2>/dev/null)
    echo "📊 Grafana health: $health_response"
else
    echo "❌ Grafana health check failed"
fi

# Test Node Exporter
echo ""
echo "Testing Node Exporter..."
if curl -sf "http://localhost:9100/metrics" | head -1 > /dev/null 2>&1; then
    echo "✅ Node Exporter is working"
    metric_lines=$(curl -s "http://localhost:9100/metrics" | wc -l)
    echo "📊 Node Exporter has $metric_lines metric lines"
else
    echo "❌ Node Exporter test failed"
fi

# Test cAdvisor
echo ""
echo "Testing cAdvisor..."
if curl -sf "http://localhost:8081/containers/" > /dev/null 2>&1; then
    echo "✅ cAdvisor is working"
else
    echo "❌ cAdvisor test failed"
fi

echo ""
echo "🔗 Monitoring Access URLs:"
echo "• Prometheus: http://localhost:9090/"
echo "• Grafana: http://localhost:3001/ (admin/admin)"
echo "• Node Exporter: http://localhost:9100/"
echo "• cAdvisor: http://localhost:8081/"

echo ""
echo "🧪 Persona System Test (Direct)"
echo "================================"

# Test persona system directly (without Docker)
cd backend
if python3 -c "from persona_loader import load_persona; persona = load_persona('james', '../data/personas'); print(f'✅ Persona loaded: {persona.display_name}'); print(f'✅ Style: {persona.style.tone}'); print(f'✅ Pinned Q&A items: {len(persona.qa.pinned_qa)}')" 2>/dev/null; then
    echo "✅ Backend persona system is working"
else
    echo "❌ Backend persona system test failed"
fi
cd ..

echo ""
echo "📝 Manual Testing Instructions:"
echo "1. Open Grafana at http://localhost:3001/ (admin/admin)"
echo "2. Check that Prometheus datasource is connected"
echo "3. View system metrics in dashboards"
echo "4. Open Prometheus at http://localhost:9090/ and run queries"

echo ""
echo "To stop monitoring stack: docker compose -f docker-compose.local.yml down"