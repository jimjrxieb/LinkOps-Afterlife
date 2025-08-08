# 🚀 Deploy AfterLife NOW - Step by Step Guide

**Complete deployment of AfterLife with persona system and monitoring in 5 minutes!**

## 📋 Prerequisites Checklist

Before starting, ensure you have:
- [ ] Azure VM running Ubuntu 20.04+ with Docker installed
- [ ] SSH access to the VM
- [ ] Domain name pointing to your VM's public IP
- [ ] Azure Container Registry access (linkops.azurecr.io)

## ⚡ Quick Deployment (5 Steps)

### Step 1: Connect to Your Azure VM
```bash
ssh your-username@your-vm-ip
```

### Step 2: Run the Automated Deployment Script
```bash
# Download and run the deployment script
curl -fsSL https://raw.githubusercontent.com/yourusername/LinkOps/master/deploy-production.sh | bash

# OR clone the repo and run locally
git clone https://jimmie012506@dev.azure.com/jimmie012506/LinkOps/_git/LinkOps
cd LinkOps
./deploy-production.sh
```

### Step 3: Configure Environment Variables
The script will create a `.env` file. Edit it with your values:
```bash
cd ~/afterlife
nano .env
```

**Required values to update:**
```env
DOMAIN=afterlife.yourdomain.com
ACME_EMAIL=you@yourdomain.com
ACR_USERNAME=<your_acr_username>
ACR_PASSWORD=<your_acr_password>
SECRET_KEY=<generate_32_char_secret>
GF_ADMIN_PASSWORD=<secure_grafana_password>
```

### Step 4: Complete Deployment
After editing `.env`, re-run the deployment:
```bash
./deploy-production.sh
```

### Step 5: Verify Everything Works
```bash
./verify-monitoring.sh
```

## 🎯 Expected Results

After successful deployment, you'll have:

### 🌐 **Application Stack**
- ✅ **Frontend**: React app at `https://yourdomain.com/`
- ✅ **Backend API**: FastAPI at `https://yourdomain.com/healthz`
- ✅ **James Persona**: Ready for recruiter demos
- ✅ **Auto HTTPS**: Caddy with Let's Encrypt certificates

### 📊 **Monitoring Stack** 
- ✅ **Grafana**: Dashboards at `https://yourdomain.com:3001/`
- ✅ **Prometheus**: Metrics at `http://vm-ip:9090/`
- ✅ **System Metrics**: CPU, memory, disk, network
- ✅ **Application Metrics**: API requests, response times
- ✅ **Container Metrics**: Docker container resources

### 🎭 **Persona System**
- ✅ **James Persona**: LinkOps/DevSecOps expert
- ✅ **Pinned Q&A**: Perfect recruiter responses
- ✅ **Professional Boundaries**: Safe topic handling
- ✅ **Dual Chat Modes**: Text + video responses

## 🧪 Quick Tests

After deployment, test these endpoints:

### Health Check
```bash
curl https://yourdomain.com/healthz
# Expected: {"status": "ok", "timestamp": "..."}
```

### Persona System
```bash
curl https://yourdomain.com/personas
# Expected: {"personas": ["james"], "count": 1}
```

### James Persona Chat
```bash
curl -X POST https://yourdomain.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is AfterLife?", "persona_id": "james"}'
# Expected: Professional response with matched_qa: true
```

### Monitoring Access
- **Grafana**: `https://yourdomain.com:3001/` (admin + your password)
- **Application**: `https://yourdomain.com/`

## 🎬 Perfect Demo Flow

Once deployed, use this sequence for recruiter demos:

### Phase 1: Quick Text Responses
1. **"What is AfterLife?"** → Instant pinned Q&A response
2. **"Tell me about LinkOps"** → Project expertise with pillars
3. **"What's your Kubernetes experience?"** → CKA certification details

### Phase 2: Show the Platform
4. **Frontend Demo** → Show persona selector and dual chat modes
5. **Monitoring Dashboard** → Professional infrastructure
6. **API Documentation** → `https://yourdomain.com/docs`

### Phase 3: Technical Deep Dive
7. **"What makes LinkOps unique?"** → Tool execution capabilities
8. **"How do you handle security?"** → Defense-in-depth approach
9. **Switch to video mode** → Full avatar with D-ID + ElevenLabs

## 🚨 Troubleshooting

### Common Issues

**🔴 Domain not resolving:**
```bash
nslookup yourdomain.com
# Verify DNS points to your VM IP
```

**🔴 Containers not starting:**
```bash
docker compose -f docker-compose.prod.yml logs backend
# Check container logs for errors
```

**🔴 SSL certificates failing:**
```bash
docker logs afterlife-proxy
# Check Caddy logs for ACME issues
```

**🔴 ACR authentication:**
```bash
docker login linkops.azurecr.io -u username -p password
# Verify ACR credentials work
```

### Health Check Commands

```bash
# Container status
docker compose -f docker-compose.prod.yml ps

# Service health
curl http://localhost:8000/healthz
curl http://localhost:9090/-/healthy
curl http://localhost:3001/api/health

# Logs
docker compose -f docker-compose.prod.yml logs -f [service]
```

## 🎉 Success Indicators

✅ **All containers running** (8 total: app + monitoring)  
✅ **HTTPS working** (Green padlock in browser)  
✅ **Persona responds** (James answers questions)  
✅ **Monitoring active** (Grafana shows data)  
✅ **API healthy** (`/healthz` returns OK)  

## 📞 Support

If you encounter issues:
1. **Check logs**: `docker compose -f docker-compose.prod.yml logs [service]`
2. **Verify environment**: Ensure `.env` has correct values
3. **Test connectivity**: Ensure ports 80/443 are open
4. **DNS propagation**: May take up to 48 hours

---

## 🎯 You're Ready!

After successful deployment, your **AfterLife platform** showcases:
- 🤖 **Professional AI personas** with domain expertise
- 📊 **Production monitoring** with Prometheus + Grafana  
- 🔒 **Enterprise security** with HTTPS and JWT authentication
- 🚀 **Azure-native deployment** with ACR integration

**Perfect for impressing recruiters with your full-stack + DevOps capabilities!** 🔥