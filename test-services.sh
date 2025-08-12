#!/bin/bash
# Test all local services and provide access information

echo "🧪 AfterLife Local Services Test"
echo "==============================="

# Test Persona Server
echo "🤖 Testing Persona Server..."
if curl -sf http://localhost:8001/healthz > /dev/null 2>&1; then
    echo "✅ Persona Server: http://localhost:8001/healthz"
    personas=$(curl -s http://localhost:8001/personas | jq -r '.count' 2>/dev/null)
    echo "   📊 Available personas: $personas"
else
    echo "❌ Persona Server: Not responding"
fi

# Test Prometheus
echo ""
echo "📊 Testing Prometheus..."
if curl -sf http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo "✅ Prometheus: http://localhost:9090"
    targets=$(curl -s "http://localhost:9090/api/v1/targets" | jq '.data.activeTargets | length' 2>/dev/null)
    echo "   📊 Active targets: $targets"
else
    echo "❌ Prometheus: Not responding"
fi

# Test Grafana
echo ""
echo "📈 Testing Grafana..."
if curl -sf http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "✅ Grafana: http://localhost:3000 (admin/admin)"
    version=$(curl -s http://localhost:3000/api/health | jq -r '.version' 2>/dev/null)
    echo "   📊 Version: $version"
else
    echo "❌ Grafana: Not responding"
fi

# Check metrics collection
echo ""
echo "📊 Testing Metrics Collection..."
if metrics=$(curl -s http://localhost:8001/metrics | grep -c "http_requests_total" 2>/dev/null); then
    echo "✅ Metrics endpoint working"
    echo "   📊 HTTP request metrics: $metrics entries"
else
    echo "❌ Metrics endpoint: Not working"
fi

echo ""
echo "🔗 Access URLs:"
echo "================================"
echo "🤖 Persona API:     http://localhost:8001"
echo "   • Health:        http://localhost:8001/healthz" 
echo "   • Personas:      http://localhost:8001/personas"
echo "   • Documentation: http://localhost:8001/docs"
echo "   • Metrics:       http://localhost:8001/metrics"
echo ""
echo "📊 Monitoring:"
echo "   • Prometheus:    http://localhost:9090"
echo "   • Grafana:       http://localhost:3000 (admin/admin)"
echo ""

echo "🧪 Test Commands:"
echo "================================"
echo '# Test persona endpoint'
echo 'curl http://localhost:8001/personas'
echo ''
echo '# View collected metrics'
echo 'curl http://localhost:8001/metrics | grep http_requests'
echo ''
echo '# Test Prometheus queries'
echo 'curl "http://localhost:9090/api/v1/query?query=up"'