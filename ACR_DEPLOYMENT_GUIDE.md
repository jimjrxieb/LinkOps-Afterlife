# 🚀 Azure Container Registry (ACR) Deployment Guide

Complete setup guide for deploying AfterLife with Azure Container Registry.

## 📋 Prerequisites

1. **Azure Container Registry**: `linkops.azurecr.io` (already created)
2. **Azure VM**: Running Ubuntu with Docker installed
3. **Domain**: Pointing to your VM's public IP
4. **GitHub Repository**: With proper secrets configured

## 🔑 Required GitHub Secrets

Set these in your GitHub repository (`Settings > Secrets and variables > Actions`):

| Secret | Value | Description |
|--------|-------|-------------|
| `ACR_LOGIN_SERVER` | `linkops.azurecr.io` | ACR registry URL |
| `ACR_USERNAME` | `<from Azure portal>` | ACR admin username |
| `ACR_PASSWORD` | `<from Azure portal>` | ACR admin password |
| `VM_HOST` | `<VM public IP/domain>` | Target deployment VM |
| `VM_USER` | `<SSH username>` | SSH user for VM access |
| `VM_SSH_KEY` | `<private key PEM>` | SSH private key content |

## 🏗️ Deployment Architecture

```
GitHub Push → Actions Workflow → ACR Build/Push → SSH to VM → Docker Pull/Deploy
                    ↓
          linkops.azurecr.io/afterlife-*:latest
                    ↓
              Azure VM Docker Compose
```

## ⚙️ VM Setup (.env Configuration)

Create `/home/username/afterlife/.env` with:

```bash
# Domain & TLS
DOMAIN=afterlife.yourdomain.com
ACME_EMAIL=you@example.com

# Azure Container Registry
ACR_LOGIN_SERVER=linkops.azurecr.io
ACR_USERNAME=<acr_admin_username>
ACR_PASSWORD=<acr_admin_password>
IMAGE_TAG=latest

# Backend Configuration
SECRET_KEY=<secure-jwt-secret-32-chars>
JWT_EXPIRE_MINUTES=120
CORS_ORIGINS=https://afterlife.yourdomain.com

# Database
DATABASE_URL=sqlite:////app/db/users.db

# API Keys (Optional)
D_ID_API_KEY=<your_d_id_api_key>
ELEVENLABS_API_KEY=<your_elevenlabs_api_key>

# Voice & Monitoring
TTS_PROVIDER=local
GF_ADMIN_USER=admin
GF_ADMIN_PASSWORD=<secure_grafana_password>
ENVIRONMENT=production
```

## 🚀 Deployment Commands

### Automated (GitHub Actions)
```bash
git push origin master  # Triggers auto-deployment
```

### Manual Deployment
```bash
# 1. Login to ACR
docker login linkops.azurecr.io -u "$ACR_USERNAME" -p "$ACR_PASSWORD"

# 2. Pull and deploy
cd ~/afterlife
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d

# 3. Verify
curl -I https://yourdomain.com/
curl -s https://yourdomain.com/healthz
```

## 🧪 Acceptance Tests

### 1. Infrastructure Health
```bash
# API Health
curl https://yourdomain.com/healthz
# Expected: {"status": "ok"}

# Persona System
curl https://yourdomain.com/personas
# Expected: {"personas": ["james"], "count": 1}

# Frontend
curl -I https://yourdomain.com/
# Expected: 200 OK with React app
```

### 2. Persona Chat Test
```bash
curl -X POST https://yourdomain.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is AfterLife?", "persona_id": "james"}'

# Expected: James persona response with matched_qa: true
```

### 3. Container Status
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
# Expected: All containers running with proper ports
```

## 🎯 Complete Feature Set

Your deployed system includes:

### 🤖 **Core Platform**
- ✅ FastAPI backend with JWT authentication
- ✅ React frontend with modern UI
- ✅ SQLite database with encryption
- ✅ File upload and processing

### 🎭 **Avatar Persona System**
- ✅ James persona (LinkOps/DevSecOps expert)
- ✅ Pinned Q&A for recruiter questions
- ✅ Professional boundaries and refusals
- ✅ Contextual response generation

### 🔧 **Production Infrastructure**
- ✅ Caddy reverse proxy with auto HTTPS
- ✅ Prometheus + Grafana monitoring
- ✅ Docker Compose orchestration
- ✅ Azure Container Registry integration

### 🚀 **CI/CD Pipeline**
- ✅ GitHub Actions automated deployment
- ✅ ACR build/push on git push
- ✅ SSH-based VM deployment
- ✅ Health check validation

## 🎥 Demo Flow

Perfect sequence for recruiter demonstrations:

### Phase 1: Quick Chat Mode
1. "What is AfterLife?" → **Pinned Q&A response**
2. "Tell me about LinkOps" → **Project expertise**
3. "What's your Kubernetes experience?" → **CKA certification details**

### Phase 2: Full Avatar Mode  
4. Switch to video mode → **D-ID avatar generation**
5. "What makes LinkOps unique?" → **Video response with voice**
6. Show monitoring dashboard → **Professional infrastructure**

## 🚨 Troubleshooting

### ACR Login Issues
```bash
# Test ACR access
docker login linkops.azurecr.io -u username -p password
# Verify credentials in Azure portal

# Check GitHub secrets
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/owner/repo/actions/secrets
```

### Deployment Failures
```bash
# Check GitHub Actions logs
# Verify VM SSH access: ssh username@vm-ip
# Check .env file on VM: cat ~/afterlife/.env
# View container logs: docker logs afterlife-backend
```

### DNS/TLS Issues
```bash
# Verify DNS: nslookup yourdomain.com
# Check Caddy logs: docker logs afterlife-proxy
# Test HTTP: curl -I http://yourdomain.com
```

## 🎉 Success Indicators

✅ **GitHub Actions**: Green checkmarks on all workflow runs  
✅ **Containers**: All services running and healthy  
✅ **HTTPS**: Valid SSL certificate from Let's Encrypt  
✅ **Monitoring**: Grafana accessible with dashboards populated  
✅ **Persona System**: James responds with professional expertise  
✅ **API Health**: All endpoints return expected responses  

Your AfterLife platform is now enterprise-ready with Azure-native deployment! 🚀