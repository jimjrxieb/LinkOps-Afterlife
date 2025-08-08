#!/bin/bash
# AfterLife Production Deployment Script
# Deploys the complete application stack with monitoring to Azure VM

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   log_error "This script should not be run as root for security reasons"
   exit 1
fi

log_info "🚀 Starting AfterLife Production Deployment"
log_info "=============================================="

# Step 1: Verify prerequisites
log_info "📋 Step 1: Verifying prerequisites..."

# Check if Docker is installed and running
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! docker info &> /dev/null; then
    log_error "Docker daemon is not running. Please start Docker."
    exit 1
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    log_error "Docker Compose plugin is not available. Please install docker-compose-plugin."
    exit 1
fi

# Check if git is available
if ! command -v git &> /dev/null; then
    log_error "Git is not installed. Please install git."
    exit 1
fi

log_success "Prerequisites verified"

# Step 2: Setup application directory
log_info "📁 Step 2: Setting up application directory..."

APP_DIR="$HOME/afterlife"
if [ ! -d "$APP_DIR" ]; then
    log_info "Creating application directory: $APP_DIR"
    mkdir -p "$APP_DIR"
fi

cd "$APP_DIR"
log_success "Application directory ready: $APP_DIR"

# Step 3: Clone or update repository
log_info "📦 Step 3: Getting latest application code..."

if [ ! -d ".git" ]; then
    log_info "Cloning AfterLife repository..."
    git clone https://jimmie012506@dev.azure.com/jimmie012506/LinkOps/_git/LinkOps .
else
    log_info "Updating existing repository..."
    git fetch origin
    git reset --hard origin/master
fi

log_success "Application code updated"

# Step 4: Configure environment
log_info "⚙️  Step 4: Configuring environment..."

if [ ! -f ".env" ]; then
    log_info "Creating .env file from template..."
    cp .env.example .env
    log_warning "⚠️  IMPORTANT: Please edit .env file with your actual values:"
    log_warning "   - DOMAIN (your actual domain)"
    log_warning "   - ACME_EMAIL (your email for SSL certificates)"
    log_warning "   - ACR_USERNAME and ACR_PASSWORD (Azure Container Registry credentials)"
    log_warning "   - SECRET_KEY (generate secure JWT secret)"
    log_warning "   - GF_ADMIN_PASSWORD (secure Grafana admin password)"
    log_warning "   - API keys (D_ID_API_KEY, ELEVENLABS_API_KEY if available)"
    echo
    read -p "Press Enter after editing .env file, or Ctrl+C to exit and edit manually..."
fi

# Validate critical environment variables
log_info "Validating environment configuration..."

if [ -f ".env" ]; then
    source .env
    
    # Check required variables
    REQUIRED_VARS=("DOMAIN" "ACME_EMAIL" "ACR_LOGIN_SERVER")
    MISSING_VARS=()
    
    for var in "${REQUIRED_VARS[@]}"; do
        if [ -z "${!var:-}" ]; then
            MISSING_VARS+=("$var")
        fi
    done
    
    if [ ${#MISSING_VARS[@]} -ne 0 ]; then
        log_error "Missing required environment variables: ${MISSING_VARS[*]}"
        log_error "Please edit .env file and set these variables"
        exit 1
    fi
    
    log_success "Environment configuration validated"
else
    log_error ".env file not found. Please create it from .env.example"
    exit 1
fi

# Step 5: Login to Azure Container Registry
log_info "🔐 Step 5: Logging into Azure Container Registry..."

if [ -n "${ACR_USERNAME:-}" ] && [ -n "${ACR_PASSWORD:-}" ]; then
    echo "$ACR_PASSWORD" | docker login "$ACR_LOGIN_SERVER" -u "$ACR_USERNAME" --password-stdin
    log_success "Successfully logged into ACR: $ACR_LOGIN_SERVER"
else
    log_warning "ACR credentials not provided. Using existing Docker login."
fi

# Step 6: Pull latest images
log_info "📥 Step 6: Pulling latest Docker images..."

docker compose -f docker-compose.prod.yml pull
log_success "Latest images pulled"

# Step 7: Deploy application stack
log_info "🚀 Step 7: Deploying application stack..."

# Stop existing containers gracefully
if docker compose -f docker-compose.prod.yml ps --services --filter "status=running" | grep -q .; then
    log_info "Stopping existing containers..."
    docker compose -f docker-compose.prod.yml down
fi

# Deploy with all services
log_info "Starting all services..."
docker compose -f docker-compose.prod.yml up -d

log_success "Application stack deployed"

# Step 8: Wait for services to be healthy
log_info "⏳ Step 8: Waiting for services to be healthy..."

# Function to check if a service is healthy
check_service_health() {
    local service=$1
    local max_attempts=30
    local attempt=1
    
    log_info "Checking health of $service..."
    
    while [ $attempt -le $max_attempts ]; do
        if docker compose -f docker-compose.prod.yml ps --services --filter "status=running" | grep -q "^$service$"; then
            local health=$(docker inspect --format='{{.State.Health.Status}}' "afterlife-$service" 2>/dev/null || echo "no-healthcheck")
            
            if [ "$health" = "healthy" ] || [ "$health" = "no-healthcheck" ]; then
                log_success "$service is healthy"
                return 0
            fi
        fi
        
        echo -n "."
        sleep 5
        ((attempt++))
    done
    
    log_warning "$service health check timeout"
    return 1
}

# Check critical services
SERVICES=("backend" "frontend" "proxy")
for service in "${SERVICES[@]}"; do
    check_service_health "$service" || true
done

# Step 9: Verify deployment
log_info "🧪 Step 9: Verifying deployment..."

log_info "Waiting for services to be fully ready..."
sleep 30

# Test backend health
log_info "Testing backend health..."
for i in {1..10}; do
    if curl -sf http://localhost:8000/healthz > /dev/null 2>&1; then
        log_success "Backend health check passed"
        break
    elif [ $i -eq 10 ]; then
        log_warning "Backend health check failed"
    else
        echo -n "."
        sleep 3
    fi
done

# Test persona system
log_info "Testing persona system..."
if curl -sf http://localhost:8000/personas > /dev/null 2>&1; then
    log_success "Persona system is accessible"
else
    log_warning "Persona system test failed"
fi

# Test frontend
log_info "Testing frontend..."
if curl -sf http://localhost:8080/ > /dev/null 2>&1; then
    log_success "Frontend is accessible"
else
    log_warning "Frontend test failed"
fi

# Step 10: Display deployment status
log_info "📊 Step 10: Deployment Status"
log_info "=============================="

echo
log_info "Container Status:"
docker compose -f docker-compose.prod.yml ps

echo
log_info "Service URLs:"
log_info "• Frontend: http://localhost:8080/"
log_info "• Backend API: http://localhost:8000/"
log_info "• API Health: http://localhost:8000/healthz"
log_info "• API Docs: http://localhost:8000/docs"
log_info "• Personas: http://localhost:8000/personas"
log_info "• Prometheus: http://localhost:9090/"
log_info "• Grafana: http://localhost:3001/ (admin / check .env for password)"

if [ -n "${DOMAIN:-}" ]; then
    echo
    log_info "Production URLs (once DNS is configured):"
    log_info "• Application: https://$DOMAIN/"
    log_info "• API: https://$DOMAIN/healthz"
    log_info "• Monitoring: https://$DOMAIN:3001/"
fi

echo
log_info "🎯 Quick Tests:"
echo "# Test API health"
echo "curl http://localhost:8000/healthz"
echo
echo "# Test persona system"
echo "curl http://localhost:8000/personas"
echo
echo "# Test persona chat"
echo 'curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '"'"'{"message": "What is AfterLife?", "persona_id": "james"}'"'"

echo
log_info "📝 Next Steps:"
log_info "1. Verify all services are running: docker compose -f docker-compose.prod.yml ps"
log_info "2. Check logs if needed: docker compose -f docker-compose.prod.yml logs [service]"
log_info "3. Configure your domain's DNS to point to this server's IP"
log_info "4. Test HTTPS access once DNS propagates"
log_info "5. Access Grafana at port 3001 for monitoring dashboards"

echo
log_success "🎉 AfterLife deployment completed!"
log_success "Your AI avatar platform with persona system is now running!"

# Cleanup
log_info "🧹 Cleaning up old Docker images..."
docker system prune -f > /dev/null 2>&1 || true

log_success "Deployment script finished successfully!"

# Display final status
echo
echo "=============================================="
log_success "🚀 AfterLife is now running with full monitoring!"
echo "=============================================="