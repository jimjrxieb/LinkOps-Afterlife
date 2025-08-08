#!/bin/bash
# Azure VM Bootstrap Script for AfterLife Deployment
# Run this once on your Azure VM to prepare it for deployment

set -euo pipefail

echo "🚀 Setting up Azure VM for AfterLife deployment..."

# Update system
echo "📦 Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Docker Compose plugin
echo "📋 Installing Docker Compose plugin..."
sudo apt-get install -y docker-compose-plugin

# Create app directory
echo "📁 Setting up application directory..."
mkdir -p ~/afterlife
cd ~/afterlife

# Create initial .env from template (you'll need to edit this manually)
echo "⚙️  Creating initial .env file..."
if [ ! -f .env ]; then
    cat > .env << 'EOF'
# AfterLife Production Configuration
# IMPORTANT: Edit these values before first deployment!

# Domain & TLS Configuration
DOMAIN=YOUR_DOMAIN_HERE.com
ACME_EMAIL=YOUR_EMAIL_HERE@example.com

# GitHub Container Registry
GHCR_NAMESPACE=jimjrxieb
IMAGE_TAG=latest

# Backend Configuration (CHANGE THE SECRET KEY!)
SECRET_KEY=CHANGE-THIS-TO-A-SECURE-SECRET-KEY-IN-PRODUCTION
JWT_EXPIRE_MINUTES=120
CORS_ORIGINS=https://YOUR_DOMAIN_HERE.com

# Database Configuration
DATABASE_URL=sqlite:////app/db/users.db

# API Keys (Optional - for full functionality)
D_ID_API_KEY=your_d_id_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Voice Configuration
TTS_PROVIDER=local

# Environment
ENVIRONMENT=production
EOF
    echo "✅ Created .env file - PLEASE EDIT IT with your actual values!"
else
    echo "ℹ️  .env file already exists, skipping..."
fi

# Set up firewall (allow HTTP/HTTPS)
echo "🔥 Configuring firewall..."
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow ssh
sudo ufw --force enable

# Test Docker installation
echo "🧪 Testing Docker installation..."
docker --version
docker compose version

# Create systemd service to ensure containers start on boot
echo "🔄 Creating systemd service for auto-start..."
sudo tee /etc/systemd/system/afterlife.service > /dev/null << 'EOF'
[Unit]
Description=AfterLife Docker Compose Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory=/home/$USER/afterlife
ExecStart=/usr/bin/docker compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker compose -f docker-compose.prod.yml down
TimeoutStartSec=0
User=$USER

[Install]
WantedBy=multi-user.target
EOF

# Enable the service
sudo systemctl enable afterlife.service

echo ""
echo "🎉 Azure VM setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit ~/afterlife/.env with your actual domain and API keys"
echo "2. Set up GitHub repository secrets:"
echo "   - VM_HOST: This VM's public IP or domain"
echo "   - VM_USER: $USER"
echo "   - VM_SSH_KEY: Your private SSH key (PEM format)"
echo "3. Push to main branch to trigger automatic deployment"
echo ""
echo "🔧 Manual deployment (if needed):"
echo "   cd ~/afterlife"
echo "   docker compose -f docker-compose.prod.yml up -d"
echo ""
echo "📊 View logs:"
echo "   docker compose -f docker-compose.prod.yml logs -f"
echo ""
echo "⚠️  IMPORTANT: Edit the .env file before deploying!"
echo "   nano ~/afterlife/.env"