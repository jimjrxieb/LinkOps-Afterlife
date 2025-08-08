# 🚀 AfterLife - AI-Powered Digital Afterlife Platform

[![Azure DevOps](https://dev.azure.com/jimmie012506/LinkOps/_apis/build/status/LinkOps?branchName=master)](https://dev.azure.com/jimmie012506/LinkOps/_build/latest?definitionId=1&branchName=master)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](./docker-compose.prod.yml)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **Create interactive AI avatars that preserve memories and enable meaningful conversations with departed loved ones.**

AfterLife is a production-ready platform that combines cutting-edge AI technologies to create realistic digital representations of people, enabling families to maintain connections and preserve memories through interactive conversations.

## ✨ Features

### 🤖 AI Avatar Generation
- **Photo Processing**: Multi-photo AI enhancement and face synthesis
- **Voice Cloning**: ElevenLabs integration for realistic voice reproduction  
- **Conversation AI**: Fine-tuned models based on personal text data
- **Video Generation**: D-ID integration for lifelike talking avatars

### 🔐 Security & Privacy
- **JWT Authentication**: Secure user registration and login system
- **File Encryption**: Fernet encryption for all uploaded content
- **Consent Management**: Comprehensive consent tracking and user rights
- **Usage Limits**: Daily interaction limits and session management
- **Secure Deletion**: Complete data removal capabilities

### 📊 Production Infrastructure
- **Docker Compose**: Complete containerized deployment
- **Caddy Reverse Proxy**: Automatic HTTPS with Let's Encrypt
- **Monitoring Stack**: Prometheus + Grafana dashboards
- **CI/CD Pipeline**: GitHub Actions deployment to Azure VM
- **Health Checks**: Comprehensive service monitoring

## 🚀 Quick Start

### Production Deployment

1. **Clone the repository:**
   ```bash
   git clone https://jimmie012506@dev.azure.com/jimmie012506/LinkOps/_git/LinkOps
   cd LinkOps
   ```

2. **Set up Azure VM:**
   ```bash
   curl -fsSL https://raw.githubusercontent.com/yourusername/LinkOps/master/azure-vm-setup.sh | bash
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your domain, API keys, and secrets
   nano .env
   ```

4. **Deploy:**
   ```bash
   docker compose -f docker-compose.prod.yml up -d
   ```

Your application will be available at `https://yourdomain.com` with automatic HTTPS!

### Local Development

1. **Backend:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   python main.py
   ```

2. **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Access:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Production Stack                       │
├─────────────────────────────────────────────────────────────┤
│  Internet → Caddy (80/443) → Frontend + Backend           │
│       ↓                                                     │
│  Auto HTTPS + Security Headers                             │
│       ↓                                                     │
│  ┌──────────────┬──────────────┬────────────────────────┐  │
│  │   Frontend   │   Backend    │     Monitoring         │  │
│  │   React      │   FastAPI    │   Prometheus+Grafana  │  │
│  │   (Static)   │   (API)      │   + Node Exporter     │  │
│  └──────────────┴──────────────┴────────────────────────┘  │
│       ↓                ↓                      ↓            │
│  ┌──────────────┬──────────────┬────────────────────────┐  │
│  │  Static      │  SQLite DB   │    Persistent Volumes  │  │
│  │  Files       │  User Data   │    Monitoring Data     │  │
│  └──────────────┴──────────────┴────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Authentication**: JWT with bcrypt password hashing
- **Database**: SQLite with encrypted file storage
- **AI Integration**: 
  - D-ID API (avatar generation)
  - ElevenLabs API (voice cloning)
  - Hugging Face Transformers (text processing)
- **Security**: Cryptography (Fernet), file validation, CORS

### Frontend
- **Framework**: React 18 with Vite
- **UI**: Modern responsive design
- **State Management**: React hooks and context
- **Testing**: Cypress E2E testing

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Reverse Proxy**: Caddy (automatic HTTPS)
- **Monitoring**: Prometheus + Grafana
- **CI/CD**: GitHub Actions
- **Cloud**: Azure VM deployment ready

## 📊 Monitoring

Access your monitoring dashboard at `https://yourdomain.com:3001`:

### Pre-configured Dashboards:
- **API Overview**: Request rates, response times, error rates
- **System Metrics**: CPU, memory, disk, network usage  
- **Container Metrics**: Docker container resource usage
- **Custom Metrics**: Session tracking, upload statistics

### Key Metrics Tracked:
- HTTP request/response metrics
- System resource utilization
- Application-specific KPIs
- Error rates and availability

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=.
```

### Frontend E2E Tests  
```bash
cd frontend
npm run test:e2e
```

### API Testing
The platform includes comprehensive test coverage:
- Authentication flows
- File upload validation
- API endpoint testing
- Integration testing
- Security validation

## 📚 Documentation

- **[🚀 Deployment Guide](DEPLOYMENT.md)**: Complete production setup
- **[📊 Monitoring Guide](MONITORING.md)**: Prometheus + Grafana setup
- **[🔐 Security Setup](SECURITY_SETUP.md)**: Security configuration
- **[🧪 Testing Guide](TESTING.md)**: Testing procedures

## 🔧 Configuration

### Required API Keys
1. **D-ID API**: Get from [d-id.com](https://www.d-id.com/) for avatar generation
2. **ElevenLabs API**: Get from [elevenlabs.io](https://www.elevenlabs.io/) for voice cloning

### Environment Variables
See [`.env.example`](.env.example) for all configuration options.

### Security Configuration
- Generate secure JWT secret: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Configure CORS origins for your domain
- Set up proper file upload limits

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'feat: Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines
- Follow conventional commits for commit messages
- Add tests for new features
- Update documentation as needed
- Ensure security best practices

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the guides in the `/docs` folder
- **Issues**: Report bugs or request features via Azure DevOps issues
- **Monitoring**: Use Grafana dashboards for system health
- **Logs**: `docker compose logs -f [service]` for debugging

## 🎯 Roadmap

- [ ] Advanced avatar personality profiles
- [ ] Multi-language support
- [ ] Mobile application
- [ ] Advanced analytics dashboard
- [ ] Integration with more AI providers
- [ ] Kubernetes deployment manifests

---

**Built with ❤️ for preserving memories and connecting hearts across time.**