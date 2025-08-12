#!/bin/bash
# Simple local test - build containers separately to avoid resource issues
set -euo pipefail

echo "🧪 Simple AfterLife Local Testing"
echo "================================="

# Stop any existing containers
echo "Stopping any existing containers..."
docker compose -f docker-compose.local.yml down --remove-orphans 2>/dev/null || true

# Build backend first
echo "Building backend..."
docker compose -f docker-compose.local.yml build backend

# Build frontend
echo "Building frontend..."  
docker compose -f docker-compose.local.yml build frontend

# Start services
echo "Starting all services..."
docker compose -f docker-compose.local.yml up -d

echo "Waiting 30 seconds for services to start..."
sleep 30

# Check container status
echo "Container status:"
docker compose -f docker-compose.local.yml ps

# Test backend health
echo "Testing backend health..."
if curl -sf "http://localhost:8000/healthz" > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
fi

# Test persona system
echo "Testing persona system..."
if curl -sf "http://localhost:8000/personas" > /dev/null 2>&1; then
    response=$(curl -s "http://localhost:8000/personas" 2>/dev/null)
    echo "✅ Persona system working: $response"
else
    echo "❌ Persona system test failed"
fi

echo ""
echo "🔗 Access URLs:"
echo "• Frontend: http://localhost/"
echo "• Backend API: http://localhost:8000/"
echo "• Backend Health: http://localhost:8000/healthz"
echo "• Prometheus: http://localhost:9090/"
echo "• Grafana: http://localhost:3001/ (admin/admin)"
echo ""
echo "To stop: docker compose -f docker-compose.local.yml down"