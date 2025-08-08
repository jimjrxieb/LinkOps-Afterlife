# LinkOps-Afterlife Security Setup Guide

## 🔐 Security Features Overview

LinkOps-Afterlife implements comprehensive security and ethical safeguards to protect user data and ensure responsible use of AI technology for digital memorials.

### Security Features Implemented:

1. **JWT Authentication** - Secure user registration and login system
2. **File Encryption** - All uploaded files encrypted using Fernet symmetric encryption  
3. **File Validation** - Strict validation of file types, sizes, and content
4. **User Session Management** - Secure session tracking with usage limits
5. **Consent Management** - Mandatory consent forms before data processing
6. **Data Deletion** - Complete session data deletion on user request
7. **Usage Limits** - Daily interaction limits to prevent abuse

## 🚀 Quick Setup

### 1. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Generate secure JWT secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Edit .env file with your credentials:
# - D_ID_API_KEY=your_d_id_api_key
# - ELEVENLABS_API_KEY=your_elevenlabs_api_key  
# - SECRET_KEY=your_generated_secret_key
```

### 2. Start the Platform

```bash
# Using Docker (Recommended)
docker-compose up --build

# Access points:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
```

### 3. Test Authentication

```bash
# Register a user
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'

# Login to get token
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'

# Use token for authenticated requests
curl -X GET http://localhost:8000/session_status/your_session_id \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🛡️ Security Architecture

### Authentication Flow
1. User registers with username/password (min 8 chars)
2. Password hashed with bcrypt
3. Login returns JWT token (24h expiry)
4. All API endpoints require valid JWT token
5. Frontend stores token and includes in requests

### File Security
1. **Upload Validation**:
   - Photos: JPG/PNG only, max 5MB
   - Audio: WAV/MP3 only, max 5MB, max 30 seconds
   - Text: TXT only, max 10MB, UTF-8 encoding

2. **Encryption Process**:
   - Unique Fernet key generated per session
   - All uploaded files encrypted immediately
   - Original files deleted after encryption
   - Encrypted files stored with .enc extension

3. **Access Control**:
   - Users can only access their own sessions
   - Session ownership verified on every request
   - Secure filename generation prevents path traversal

### Consent Management
1. **Mandatory Consent**: Users must agree to:
   - Terms of use and data processing
   - Emotional impact acknowledgment
   - Data deletion rights

2. **Consent Tracking**:
   - Consent stored in database with timestamp
   - Required before any AI processing
   - Can be withdrawn (triggers data deletion)

### Usage Limits
- **Daily Limits**: 10 interactions per session per day
- **Rate Limiting**: Prevents API abuse
- **Session Limits**: Configurable per user

## 🎯 Ethical Safeguards

### Data Privacy
- **Encryption at Rest**: All user files encrypted
- **Minimal Data Collection**: Only necessary data stored
- **Data Retention**: Users can delete all data anytime
- **No Third-Party Sharing**: Data never shared without consent

### Emotional Considerations
- **Consent Forms**: Explicit acknowledgment of emotional impact
- **Grief Resources**: Links to professional grief counseling
- **Clear Disclaimers**: Technology limitations clearly stated
- **Respectful Design**: UI emphasizes memorial nature

### AI Ethics
- **Consent Required**: Only process data with explicit consent
- **Purpose Limitation**: AI only used for memorial purposes
- **Transparency**: Clear explanation of AI processing steps
- **User Control**: Users retain full control over their data

## 🔧 Advanced Configuration

### Environment Variables

```bash
# Required
D_ID_API_KEY=your_d_id_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
SECRET_KEY=your_jwt_secret_key

# Optional
VITE_API_BASE_URL=http://localhost:8000  # Frontend API endpoint
DATABASE_PATH=/app/db/users.db           # SQLite database path
GF_ADMIN_USER=admin                      # Grafana admin user (prod)
GF_ADMIN_PASSWORD=change_me              # Grafana admin password (prod)
```

### File Validation Limits

```python
# Configurable in backend/utils.py
MAX_PHOTO_SIZE = 5 * 1024 * 1024     # 5MB
MAX_AUDIO_SIZE = 5 * 1024 * 1024     # 5MB  
MAX_TEXT_SIZE = 10 * 1024 * 1024     # 10MB
MAX_AUDIO_DURATION = 30              # seconds
```

### Usage Limits

```python
# Configurable in backend/auth.py
ACCESS_TOKEN_EXPIRE_HOURS = 24       # JWT expiry
DAILY_INTERACTION_LIMIT = 10         # Interactions per session
```

## 🚨 Security Checklist

### Pre-Production
- [ ] Change default SECRET_KEY to secure random value
- [ ] Verify all API keys are properly configured
- [ ] Test authentication flow end-to-end
- [ ] Verify file encryption is working
- [ ] Test consent form workflow
- [ ] Verify session deletion works completely

### Production Deployment
- [ ] Use HTTPS/TLS for all communications
- [ ] Set up proper database backups
- [ ] Configure log rotation and monitoring
- [ ] Set up rate limiting at reverse proxy level
- [ ] Regular security updates for dependencies
- [ ] Monitor for unusual usage patterns
- [ ] Harden monitoring stack (restrict Grafana admin creds, avoid public Prometheus UI)

## 🆘 Troubleshooting

### Common Issues

**Authentication Fails**
```bash
# Check SECRET_KEY is set
echo $SECRET_KEY

# Verify token format
jwt.io # Paste token to decode
```

**File Upload Fails**
```bash
# Check file permissions
ls -la data/
mkdir -p data/ db/

# Check encryption key generation
ls -la data/session_id/encryption_key.key
```

**Database Issues**
```bash
# Check database file
ls -la db/users.db

# Reset database (WARNING: Deletes all users)
rm db/users.db
# Restart application to recreate
```

## 📞 Support

For security concerns or questions:
- Review code in `/backend/auth.py` and `/backend/utils.py`
- Check logs for authentication errors
- Verify environment configuration
- Test with curl commands provided above

## 🔮 Future Enhancements

- [ ] OAuth2 integration (Google, GitHub)
- [ ] Two-factor authentication (2FA)
- [ ] Advanced audit logging
- [ ] GDPR compliance features
- [ ] Automated security scanning
- [ ] Session timeout controls