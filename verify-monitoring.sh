#!/bin/bash
# AfterLife Monitoring Verification Script
# Comprehensive testing of the monitoring stack

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🔍 AfterLife Monitoring Stack Verification"
echo "=========================================="

# Test function
test_endpoint() {
    local name="$1"
    local url="$2"
    local expected_status="${3:-200}"
    
    log_info "Testing $name..."
    
    if response=$(curl -s -w "%{http_code}" -o /dev/null "$url" 2>/dev/null); then
        if [ "$response" -eq "$expected_status" ]; then
            log_success "$name is accessible (HTTP $response)"
            return 0
        else
            log_warning "$name returned HTTP $response (expected $expected_status)"
            return 1
        fi
    else
        log_error "$name is not accessible"
        return 1
    fi
}

# Test JSON endpoint
test_json_endpoint() {
    local name="$1"
    local url="$2"
    local key="$3"
    
    log_info "Testing $name..."
    
    if response=$(curl -s "$url" 2>/dev/null); then
        if echo "$response" | jq -e ".$key" > /dev/null 2>&1; then
            log_success "$name is responding with valid JSON"
            return 0
        else
            log_warning "$name response missing expected key: $key"
            return 1
        fi
    else
        log_error "$name is not accessible"
        return 1
    fi
}

echo
log_info "🏥 Application Health Checks"
log_info "=============================="

# Backend health
test_json_endpoint "Backend Health" "http://localhost:8000/healthz" "status"

# Backend metrics
test_endpoint "Backend Metrics" "http://localhost:8000/metrics"

# Persona system
test_json_endpoint "Persona System" "http://localhost:8000/personas" "personas"

# Frontend
test_endpoint "Frontend" "http://localhost:8080/"

echo
log_info "📊 Monitoring Stack"
log_info "==================="

# Prometheus
test_endpoint "Prometheus Web UI" "http://localhost:9090/-/healthy"

# Check Prometheus targets
log_info "Checking Prometheus targets..."
if targets=$(curl -s "http://localhost:9090/api/v1/targets" 2>/dev/null); then
    up_targets=$(echo "$targets" | jq '.data.activeTargets[] | select(.health == "up") | .scrapePool' 2>/dev/null | wc -l)
    total_targets=$(echo "$targets" | jq '.data.activeTargets | length' 2>/dev/null)
    log_success "Prometheus targets: $up_targets/$total_targets are up"
else
    log_warning "Could not check Prometheus targets"
fi

# Grafana
test_endpoint "Grafana" "http://localhost:3001/api/health"

# Node Exporter
test_endpoint "Node Exporter" "http://localhost:9100/metrics"

# cAdvisor
test_endpoint "cAdvisor" "http://localhost:8081/healthz"

echo
log_info "🎯 Persona System Tests"
log_info "======================="

# Test James persona
log_info "Testing James persona details..."
if persona_response=$(curl -s "http://localhost:8000/personas/james" 2>/dev/null); then
    if echo "$persona_response" | jq -e '.persona.display_name' > /dev/null 2>&1; then
        display_name=$(echo "$persona_response" | jq -r '.persona.display_name')
        log_success "James persona loaded: $display_name"
    else
        log_warning "James persona response invalid"
    fi
else
    log_error "Could not load James persona"
fi

# Test persona chat
log_info "Testing persona chat..."
chat_payload='{"message": "What is AfterLife?", "persona_id": "james"}'
if chat_response=$(curl -s -X POST "http://localhost:8000/chat" \
    -H "Content-Type: application/json" \
    -d "$chat_payload" 2>/dev/null); then
    
    if echo "$chat_response" | jq -e '.response.answer' > /dev/null 2>&1; then
        matched_qa=$(echo "$chat_response" | jq -r '.response.matched_qa // false')
        log_success "Persona chat working (Pinned Q&A: $matched_qa)"
    else
        log_warning "Persona chat response invalid"
    fi
else
    log_error "Persona chat test failed"
fi

echo
log_info "📈 Metrics Collection"
log_info "=====================" 

# Check if metrics are being collected
log_info "Checking metrics collection..."

# HTTP request metrics
if curl -s "http://localhost:9090/api/v1/query?query=http_requests_total" | jq -e '.data.result | length > 0' > /dev/null 2>&1; then
    log_success "HTTP request metrics are being collected"
else
    log_warning "HTTP request metrics not found"
fi

# System metrics
if curl -s "http://localhost:9090/api/v1/query?query=node_cpu_seconds_total" | jq -e '.data.result | length > 0' > /dev/null 2>&1; then
    log_success "System metrics are being collected"
else
    log_warning "System metrics not found"
fi

# Container metrics
if curl -s "http://localhost:9090/api/v1/query?query=container_memory_usage_bytes" | jq -e '.data.result | length > 0' > /dev/null 2>&1; then
    log_success "Container metrics are being collected"
else
    log_warning "Container metrics not found"
fi

echo
log_info "🐳 Container Status"
log_info "=================="

# Check container health
containers=("afterlife-backend" "afterlife-frontend" "afterlife-proxy" "afterlife-prometheus" "afterlife-grafana")

for container in "${containers[@]}"; do
    if docker inspect "$container" &>/dev/null; then
        status=$(docker inspect --format='{{.State.Status}}' "$container")
        health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "no-healthcheck")
        
        if [ "$status" = "running" ]; then
            if [ "$health" = "healthy" ] || [ "$health" = "no-healthcheck" ]; then
                log_success "$container: $status ($health)"
            else
                log_warning "$container: $status ($health)"
            fi
        else
            log_error "$container: $status"
        fi
    else
        log_error "$container: not found"
    fi
done

echo
log_info "📊 Dashboard Status"
log_info "==================="

# Check Grafana dashboards
log_info "Checking Grafana dashboard provisioning..."
if docker exec afterlife-grafana ls /etc/grafana/provisioning/dashboards/ 2>/dev/null | grep -q "json"; then
    dashboard_count=$(docker exec afterlife-grafana ls /etc/grafana/provisioning/dashboards/ 2>/dev/null | grep -c "json" || echo "0")
    log_success "Grafana dashboards provisioned: $dashboard_count found"
else
    log_warning "Grafana dashboards not found"
fi

echo
log_info "🔗 Access URLs"
log_info "=============="

echo "Application:"
echo "• Frontend: http://localhost:8080/"
echo "• Backend API: http://localhost:8000/"
echo "• API Documentation: http://localhost:8000/docs"
echo "• Health Check: http://localhost:8000/healthz"
echo "• Personas: http://localhost:8000/personas"
echo
echo "Monitoring:"
echo "• Prometheus: http://localhost:9090/"
echo "• Grafana: http://localhost:3001/ (admin / check .env)"
echo "• Node Exporter: http://localhost:9100/"
echo "• cAdvisor: http://localhost:8081/"

# If domain is configured
if [ -f ".env" ] && source .env && [ -n "${DOMAIN:-}" ]; then
    echo
    echo "Production URLs:"
    echo "• Application: https://$DOMAIN/"
    echo "• API: https://$DOMAIN/healthz"
    echo "• Monitoring: https://$DOMAIN:3001/"
fi

echo
log_info "🧪 Quick Test Commands"
log_info "======================"

echo "# Test API health"
echo "curl http://localhost:8000/healthz"
echo
echo "# Test persona chat"
echo 'curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '"'"'{"message": "What is LinkOps?", "persona_id": "james"}'"'"
echo
echo "# View container logs"
echo "docker compose -f docker-compose.prod.yml logs -f backend"
echo
echo "# Check Prometheus targets"
echo "curl http://localhost:9090/api/v1/targets"

echo
log_success "🎉 Monitoring verification completed!"
echo "Your AfterLife platform is running with comprehensive monitoring!"