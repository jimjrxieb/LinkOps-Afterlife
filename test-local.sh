#!/bin/bash
# AfterLife Local Testing Script
# Build and test the complete stack locally before Azure deployment

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

echo "🧪 AfterLife Local Testing"
echo "=========================="

# Check prerequisites
log_info "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! docker info &> /dev/null; then
    log_error "Docker daemon is not running. Please start Docker."
    exit 1
fi

if ! docker compose version &> /dev/null; then
    log_error "Docker Compose plugin is not available."
    exit 1
fi

log_success "Prerequisites verified"

# Ensure we're in the right directory
if [ ! -f "docker-compose.local.yml" ]; then
    log_error "docker-compose.local.yml not found. Are you in the project root?"
    exit 1
fi

# Stop any existing local containers
log_info "🛑 Stopping any existing local containers..."
docker compose -f docker-compose.local.yml down --remove-orphans 2>/dev/null || true

# Clean up old images
log_info "🧹 Cleaning up old images..."
docker system prune -f > /dev/null 2>&1 || true

# Build and start the stack
log_info "🏗️  Building and starting local stack..."
docker compose -f docker-compose.local.yml build --parallel
docker compose -f docker-compose.local.yml up -d

log_success "Local stack started"

# Wait for services to be ready
log_info "⏳ Waiting for services to be ready..."

wait_for_service() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    log_info "Waiting for $service..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -sf "$url" > /dev/null 2>&1; then
            log_success "$service is ready"
            return 0
        fi
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    log_warning "$service timeout after $max_attempts attempts"
    return 1
}

# Wait for backend
wait_for_service "Backend" "http://localhost:8000/healthz"

# Wait for frontend (through proxy)
wait_for_service "Frontend" "http://localhost:80/"

# Wait for monitoring
wait_for_service "Prometheus" "http://localhost:9090/-/healthy"
wait_for_service "Grafana" "http://localhost:3001/api/health"

echo
log_info "🧪 Running API Tests"
log_info "===================="

# Test backend health
log_info "Testing backend health..."
if response=$(curl -s "http://localhost:8000/healthz" 2>/dev/null); then
    if echo "$response" | jq -e '.status' > /dev/null 2>&1; then
        status=$(echo "$response" | jq -r '.status')
        log_success "Backend health: $status"
    else
        log_warning "Backend health response invalid"
    fi
else
    log_error "Backend health check failed"
fi

# Test personas endpoint
log_info "Testing persona system..."
if response=$(curl -s "http://localhost:8000/personas" 2>/dev/null); then
    if echo "$response" | jq -e '.personas' > /dev/null 2>&1; then
        count=$(echo "$response" | jq -r '.count // 0')
        log_success "Persona system: $count personas available"
    else
        log_warning "Persona system response invalid"
    fi
else
    log_error "Persona system test failed"
fi

# Test James persona
log_info "Testing James persona..."
if response=$(curl -s "http://localhost:8000/personas/james" 2>/dev/null); then
    if echo "$response" | jq -e '.persona.display_name' > /dev/null 2>&1; then
        name=$(echo "$response" | jq -r '.persona.display_name')
        log_success "James persona loaded: $name"
    else
        log_warning "James persona response invalid"
    fi
else
    log_error "James persona test failed"
fi

# Test persona chat
log_info "Testing persona chat..."
chat_payload='{"message": "What is AfterLife?", "persona_id": "james"}'
if response=$(curl -s -X POST "http://localhost:8000/chat" \
    -H "Content-Type: application/json" \
    -d "$chat_payload" 2>/dev/null); then
    
    if echo "$response" | jq -e '.response.answer' > /dev/null 2>&1; then
        matched_qa=$(echo "$response" | jq -r '.response.matched_qa // false')
        answer_preview=$(echo "$response" | jq -r '.response.answer' | cut -c1-50)
        log_success "Persona chat working (Pinned Q&A: $matched_qa)"
        log_info "Answer preview: \"$answer_preview...\""
    else
        log_warning "Persona chat response invalid"
    fi
else
    log_error "Persona chat test failed"
fi

echo
log_info "📊 Testing Monitoring Stack"
log_info "============================"

# Test Prometheus metrics
log_info "Testing Prometheus metrics..."
if curl -s "http://localhost:9090/api/v1/label/__name__/values" | jq -e '.data | length > 0' > /dev/null 2>&1; then
    metric_count=$(curl -s "http://localhost:9090/api/v1/label/__name__/values" | jq '.data | length')
    log_success "Prometheus: $metric_count metrics available"
else
    log_warning "Prometheus metrics not ready yet"
fi

# Test Grafana API
log_info "Testing Grafana API..."
if curl -s "http://localhost:3001/api/health" | jq -e '.database' > /dev/null 2>&1; then
    db_status=$(curl -s "http://localhost:3001/api/health" | jq -r '.database')
    log_success "Grafana database: $db_status"
else
    log_warning "Grafana API not ready yet"
fi

echo
log_info "🐳 Container Status"
log_info "==================="
docker compose -f docker-compose.local.yml ps

echo
log_info "🔗 Local Access URLs"
log_info "===================="
echo "Application:"
echo "• Frontend (via proxy): http://localhost/"
echo "• Backend API: http://localhost:8000/"
echo "• API Health: http://localhost:8000/healthz"
echo "• API Docs: http://localhost:8000/docs"
echo "• Personas: http://localhost:8000/personas"
echo
echo "Monitoring:"
echo "• Prometheus: http://localhost:9090/"
echo "• Grafana: http://localhost:3001/ (admin/admin)"
echo "• Node Exporter: http://localhost:9100/"
echo "• cAdvisor: http://localhost:8081/"

echo
log_info "🧪 Manual Test Commands"
log_info "======================="
echo "# Test persona chat"
echo 'curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '"'"'{"message": "Tell me about LinkOps", "persona_id": "james"}'"'"
echo
echo "# Test different questions"
echo 'curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '"'"'{"message": "What are your certifications?", "persona_id": "james"}'"'"
echo
echo "# View backend logs"
echo "docker compose -f docker-compose.local.yml logs backend"
echo
echo "# Stop local stack"
echo "docker compose -f docker-compose.local.yml down"

echo
log_success "🎉 Local testing completed!"
log_info "Your AfterLife platform is running locally with full monitoring."
log_info "Open http://localhost/ to interact with the frontend."
log_info "The persona system is ready for testing!"

# Keep script running to show logs
echo
log_info "📝 Showing recent backend logs (Ctrl+C to exit):"
echo "=================================================="
docker compose -f docker-compose.local.yml logs --tail=20 -f backend