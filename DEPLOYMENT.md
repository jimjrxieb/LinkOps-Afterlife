# 🚀 AfterLife Production Deployment Guide

Complete CI/CD setup for deploying AfterLife to Azure VM with Docker Compose + Caddy reverse proxy + automatic HTTPS.

## 📋 Quick Setup Checklist

### 1. Azure VM Setup (One-time)
```bash
# On your Azure VM:
curl -fsSL https://raw.githubusercontent.com/jimjrxieb/LinkOps-Afterlife/main/azure-vm-setup.sh | bash
cd ~/afterlife
nano .env  # Edit with your actual domain and API keys
```

### 2. GitHub Repository Secrets
Add these secrets to your GitHub repository (`Settings > Secrets and variables > Actions`):

- `VM_HOST`: Your Azure VM public IP or domain name
- `VM_USER`: SSH username (usually the user you created the VM with)  
- `VM_SSH_KEY`: Private SSH key content (PEM format) with access to the VM

### 3. Configure Domain & .env
Edit `~/afterlife/.env` on your VM with:

```env
DOMAIN=afterlife.yourdomain.com
ACME_EMAIL=you@example.com
SECRET_KEY=your-secure-jwt-secret-here
D_ID_API_KEY=your_d_id_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

### 4. Deploy
Push to `main` branch → GitHub Actions automatically builds & deploys!

---

## 🏗️ Architecture

```
Internet → Caddy (80/443) → Frontend (8080) + Backend (8000)
                  ↓
              Auto HTTPS + Security Headers
```

**Services:**
- **Caddy**: Reverse proxy with automatic HTTPS certificates
- **Frontend**: React app built with Vite, served by Caddy  
- **Backend**: FastAPI server with health checks
- **Volumes**: Persistent storage for database and user data

---

## 🔄 CI/CD Pipeline

**Triggers:** Push to `main` branch with changes to:
- `frontend/**`
- `backend/**` 
- `docker-compose.prod.yml`
- `Caddyfile`
- `.github/workflows/deploy.yml`

**Process:**
1. Build & push Docker images to GitHub Container Registry
2. SSH to Azure VM
3. Pull latest images
4. Deploy with `docker compose up -d`
5. Clean up old images

---

## 🛠️ Manual Operations

### View Status
```bash
cd ~/afterlife
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f
```

### Update Deployment  
```bash
cd ~/afterlife
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

### Restart Services
```bash
cd ~/afterlife
docker compose -f docker-compose.prod.yml restart
```

### View Caddy Logs (TLS issues)
```bash
docker compose -f docker-compose.prod.yml logs caddy
```

---

## 🔍 Health Checks

- **Frontend**: `https://yourdomain.com/` (should show React app)
- **Backend**: `https://yourdomain.com/healthz` (should return `{"status": "ok"}`)  
- **API Docs**: `https://yourdomain.com/docs` (FastAPI interactive docs)

---

## 🔐 Security Features

- **Automatic HTTPS** with Let's Encrypt certificates
- **Security headers** (HSTS, CSP, etc.) 
- **JWT authentication** for API access
- **File encryption** for uploaded content
- **CORS protection** configured for your domain
- **Daily usage limits** per user session

---

## 📊 Monitoring

### Check Container Health
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### View Resource Usage
```bash
docker stats --no-stream
```

### Check TLS Certificate Status
```bash
docker exec afterlife-proxy caddy list-certificates
```

### Prometheus + Grafana

- Prometheus UI: `http://<VM_IP>:9090` (avoid exposing publicly)
- Grafana UI: `https://yourdomain.com:3001` (admin defaults via `GF_ADMIN_USER` and `GF_ADMIN_PASSWORD` in `.env`)

Prometheus scrapes:
- `backend` FastAPI at `/metrics`
- `node-exporter` (host metrics)
- `cadvisor` (container metrics)

Grafana will auto-provision a Prometheus datasource and dashboards placed in `monitoring/grafana/provisioning`.

---

## 🚨 Troubleshooting

### Frontend Not Loading
1. Check if domain DNS points to your VM IP
2. Verify `.env` file has correct `DOMAIN` value
3. Check frontend container: `docker logs afterlife-frontend`

### HTTPS Certificate Issues
1. Verify `ACME_EMAIL` in `.env` file
2. Check Caddy logs: `docker logs afterlife-proxy`
3. Ensure ports 80/443 are open in Azure Network Security Group

### Backend API Errors
1. Check backend logs: `docker logs afterlife-backend`
2. Verify `SECRET_KEY` is set in `.env`
3. Check database volume: `docker volume inspect afterlife_app_db`

### GitHub Actions Deployment Failing  
1. Verify VM_HOST, VM_USER, VM_SSH_KEY secrets are correct
2. Test SSH access manually: `ssh VM_USER@VM_HOST`
3. Check GitHub Actions logs in repository

---

## 🎯 Next Steps

1. **Set up monitoring** with health check endpoints
2. **Configure backups** for the SQLite database volume
3. **Add rate limiting** in Caddy for API endpoints
4. **Implement log aggregation** for better debugging
5. **Add avatar persona profiles** for different interviewer types

---

## 📞 Support

- **Logs**: `docker compose -f docker-compose.prod.yml logs -f [service]`
- **Health**: Visit `/healthz` endpoint  
- **Docs**: Visit `/docs` for API documentation
- **GitHub**: Check Actions tab for deployment status