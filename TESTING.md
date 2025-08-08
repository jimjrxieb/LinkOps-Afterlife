# LinkOps-Afterlife Testing Guide

## 🧪 Testing Overview

LinkOps-Afterlife includes comprehensive automated testing to ensure reliability, security, and functionality across the entire platform. This guide covers backend unit tests, frontend E2E tests, and full pipeline integration tests.

### Testing Strategy:

- **Backend Unit Tests**: 80+ tests covering authentication, file validation, encryption, processing workflows, and API endpoints
- **Frontend E2E Tests**: Complete user journey testing with Cypress
- **Integration Tests**: Full pipeline testing from registration to deletion
- **Security Tests**: Authentication, authorization, and data protection validation
- **Mock External APIs**: D-ID and ElevenLabs APIs mocked to avoid real costs during testing

## 🚀 Quick Start

### Prerequisites
```bash
# Ensure Docker and Docker Compose are installed
docker --version
docker-compose --version

# Ensure Node.js 18+ is installed for Cypress
node --version
npm --version
```

### Run All Tests
```bash
# Backend tests in Docker
docker-compose --profile testing run test

# Frontend E2E tests (requires backend running)
cd frontend
npm run cypress:run

# Or open Cypress UI for interactive testing
npm run cypress:open
```

## 🔧 Backend Testing

### Test Structure
```
backend/tests/
├── conftest.py           # Test configuration and fixtures
├── test_auth.py          # Authentication and authorization
├── test_upload.py        # File upload, validation, encryption
├── test_processing.py    # AI processing workflows
├── test_interaction.py   # User interaction and responses
└── test_full_pipeline.py # End-to-end integration tests
```

### Running Backend Tests

#### Using Docker (Recommended)
```bash
# Run all tests with coverage
docker-compose --profile testing run test

# Run specific test file
docker-compose --profile testing run test pytest tests/test_auth.py -v

# Run tests with specific markers
docker-compose --profile testing run test pytest -m "auth" -v
docker-compose --profile testing run test pytest -m "security" -v
```

#### Local Development
```bash
cd backend

# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html --cov-report=term

# Run specific test categories
pytest -m "auth" -v          # Authentication tests
pytest -m "upload" -v        # File upload tests
pytest -m "processing" -v    # AI processing tests
pytest -m "interaction" -v   # User interaction tests
pytest -m "integration" -v   # Full pipeline tests
```

### Test Coverage
```bash
# Generate HTML coverage report
pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Backend Test Categories

#### 1. Authentication Tests (`test_auth.py`)
- ✅ User registration with validation
- ✅ Login with JWT token generation
- ✅ Protected endpoint access control
- ✅ Token expiry and refresh
- ✅ Password hashing security
- ✅ Session management
- ✅ Consent tracking and validation
- ✅ Usage limits enforcement

#### 2. File Upload Tests (`test_upload.py`)
- ✅ File type validation (JPG/PNG, WAV/MP3, TXT)
- ✅ File size limits (5MB photos/audio, 10MB text)
- ✅ Audio duration validation (30 seconds max)
- ✅ File encryption with Fernet
- ✅ Secure filename generation
- ✅ Session metadata creation
- ✅ Upload failure handling

#### 3. Processing Tests (`test_processing.py`)
- ✅ Photo preprocessing workflows
- ✅ Avatar generation with D-ID API
- ✅ Voice cloning with ElevenLabs API
- ✅ Text analysis and personality extraction
- ✅ Conversation model fine-tuning
- ✅ API key validation
- ✅ Processing error handling

#### 4. Interaction Tests (`test_interaction.py`)
- ✅ Real-time chat interaction
- ✅ Video response generation
- ✅ Session requirement validation
- ✅ Usage limit enforcement
- ✅ Consent requirement checks
- ✅ Session ownership verification
- ✅ Error handling and recovery

#### 5. Integration Tests (`test_full_pipeline.py`)
- ✅ Complete user journey (registration → deletion)
- ✅ Security enforcement throughout pipeline
- ✅ Consent requirement validation
- ✅ Error recovery and cleanup
- ✅ Unauthorized access prevention

## 🎭 Frontend Testing

### Test Structure
```
frontend/cypress/
├── e2e/
│   ├── auth.cy.js         # Authentication flow
│   ├── consent.cy.js      # Consent management
│   ├── upload.cy.js       # File upload and processing
│   ├── interaction.cy.js  # Avatar interaction
│   └── deletion.cy.js     # Session deletion
├── fixtures/
│   └── test-files.json    # Test data
└── support/
    ├── commands.js        # Custom Cypress commands
    └── e2e.js            # Global configuration
```

### Running Frontend Tests

#### Prerequisites
```bash
# Start backend server
docker-compose up backend

# Install frontend dependencies
cd frontend
npm install
```

#### Running Tests
```bash
# Run all E2E tests (headless)
npm run cypress:run

# Open Cypress UI for interactive testing
npm run cypress:open

# Run specific test file
npx cypress run --spec "cypress/e2e/auth.cy.js"

# Run tests in specific browser
npx cypress run --browser chrome

## 🩺 Monitoring Smoke Test

```bash
# Start monitoring stack locally
docker compose up -d prometheus grafana node-exporter cadvisor

# Verify backend metrics
curl -fsS http://localhost:8000/metrics | head -n 20

# Verify Prometheus targets
curl -fsS http://localhost:9090/api/v1/targets | jq '.data.activeTargets | length'

# Access Grafana at http://localhost:3001 (admin/admin or GF_ADMIN_* from .env)
```
```

### Frontend Test Categories

#### 1. Authentication Tests (`auth.cy.js`)
- ✅ User registration form validation
- ✅ Login/logout functionality
- ✅ Session persistence across refreshes
- ✅ Token expiry handling
- ✅ Error message display

#### 2. Consent Tests (`consent.cy.js`)
- ✅ Consent dialog display after upload
- ✅ Three-tier consent validation
- ✅ Grief counseling resource links
- ✅ Consent requirement enforcement
- ✅ Form submission and validation

#### 3. Upload Tests (`upload.cy.js`)
- ✅ File selection and validation
- ✅ Upload progress indicators
- ✅ File type/size error handling
- ✅ Processing status display
- ✅ Session creation and tracking

#### 4. Interaction Tests (`interaction.cy.js`)
- ✅ Chat input and message sending
- ✅ Video response playback
- ✅ Conversation history display
- ✅ Usage limit warnings
- ✅ Error handling and retry
- ✅ Accessibility compliance

#### 5. Deletion Tests (`deletion.cy.js`)
- ✅ Session deletion confirmation
- ✅ Data privacy explanations
- ✅ Complete data removal
- ✅ UI state reset after deletion
- ✅ Export options before deletion

## 🔒 Security Testing

### Security Test Coverage

#### Authentication & Authorization
- ✅ JWT token validation and expiry
- ✅ Protected endpoint access control
- ✅ Session ownership verification
- ✅ Password hashing with bcrypt
- ✅ Unauthorized access prevention

#### Data Protection
- ✅ File encryption with Fernet
- ✅ Secure file storage and deletion
- ✅ Input validation and sanitization
- ✅ SQL injection prevention
- ✅ XSS protection in frontend

#### Privacy & Consent
- ✅ Mandatory consent before processing
- ✅ Complete data deletion capability
- ✅ Usage limit enforcement
- ✅ Audit logging for deletions
- ✅ GDPR compliance features

## 🎯 Test Configuration

### Backend Configuration (`pytest.ini`)
```ini
[tool:pytest]
testpaths = tests
addopts = 
    -v --tb=short --cov=. --cov-report=html --cov-report=term
markers = 
    auth: authentication tests
    upload: file upload tests
    processing: AI processing tests
    interaction: user interaction tests
    security: security-related tests
```

### Frontend Configuration (`cypress.config.js`)
```javascript
export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    viewportWidth: 1280,
    viewportHeight: 720,
    defaultCommandTimeout: 10000,
    env: {
      apiUrl: 'http://localhost:8000'
    }
  }
})
```

### Docker Test Configuration
```yaml
test:
  build:
    context: ./backend
  command: pytest -v --cov=. --cov-report=html
  environment:
    - D_ID_API_KEY=test_d_id_key
    - ELEVENLABS_API_KEY=test_elevenlabs_key
    - SECRET_KEY=test_secret_key
  profiles:
    - testing
```

## 🚨 Continuous Integration

### GitHub Actions Workflow (Recommended)
```yaml
name: Test Suite
on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Backend Tests
        run: docker-compose --profile testing run test
        
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Start Backend
        run: docker-compose up -d backend
      - name: Run E2E Tests
        run: |
          cd frontend
          npm install
          npm run cypress:run
```

## 📊 Test Metrics

### Coverage Targets
- **Backend Code Coverage**: >85%
- **Frontend E2E Coverage**: 100% user journeys
- **Security Test Coverage**: 100% authentication flows
- **Integration Test Coverage**: 100% critical paths

### Performance Benchmarks
- **Backend API Response**: <2s per endpoint
- **File Upload Processing**: <30s for standard files
- **Frontend Page Load**: <3s initial load
- **E2E Test Suite**: <10 minutes complete run

## 🛠️ Development Workflow

### Test-Driven Development
1. **Write Failing Test**: Create test for new feature
2. **Implement Feature**: Write minimal code to pass test
3. **Refactor**: Improve code while maintaining test pass
4. **Integration**: Verify feature works in full pipeline

### Pre-Commit Testing
```bash
# Run quick test suite before commits
pytest tests/test_auth.py tests/test_upload.py -v

# Run security-focused tests
pytest -m "security" -v

# Run full backend test suite
pytest --tb=short
```

## 🐛 Debugging Tests

### Backend Test Debugging
```bash
# Run single test with detailed output
pytest tests/test_auth.py::test_login_success -v -s

# Debug with pdb
pytest tests/test_auth.py::test_login_success --pdb

# Show all print statements
pytest tests/test_auth.py -s
```

### Frontend Test Debugging
```bash
# Open Cypress UI for interactive debugging
npm run cypress:open

# Run with video recording
npx cypress run --record --key your-key

# Debug specific test
npx cypress run --spec "cypress/e2e/auth.cy.js" --headed
```

### Common Issues

#### Backend Tests
- **Database Lock**: Ensure proper test isolation with fixtures
- **API Key Errors**: Use test keys in `conftest.py`
- **File Path Issues**: Use `temp_session_dir` fixture
- **Mock Failures**: Verify patch paths and return values

#### Frontend Tests
- **Element Not Found**: Add proper `data-cy` attributes
- **Timing Issues**: Use `cy.wait()` for API calls
- **Backend Dependency**: Ensure backend is running on port 8000
- **Browser Issues**: Try different browsers (`--browser chrome`)

## 📈 Test Reporting

### Coverage Reports
```bash
# Generate HTML coverage report
pytest --cov=. --cov-report=html

# View in browser
open htmlcov/index.html

# Generate XML for CI
pytest --cov=. --cov-report=xml
```

### Cypress Reports
```bash
# Generate mochawesome report
npm install --save-dev mochawesome

# Run with reporting
npx cypress run --reporter mochawesome
```

## 🎯 Best Practices

### Backend Testing
- ✅ Use fixtures for common setup (database, auth, files)
- ✅ Mock external API calls (D-ID, ElevenLabs)
- ✅ Test both success and failure scenarios
- ✅ Verify security controls in every test
- ✅ Use descriptive test names and docstrings

### Frontend Testing
- ✅ Use semantic `data-cy` attributes for selectors
- ✅ Mock API responses for consistent testing
- ✅ Test user workflows, not implementation details
- ✅ Verify accessibility features
- ✅ Handle loading states and error conditions

### Integration Testing
- ✅ Test complete user journeys end-to-end
- ✅ Verify data consistency across components
- ✅ Test security boundaries and access controls
- ✅ Validate consent and privacy requirements
- ✅ Ensure proper cleanup after tests

## 🚀 Advanced Testing

### Load Testing
```bash
# Install locust for load testing
pip install locust

# Create load test scenarios
# Test concurrent users, file uploads, API limits
```

### Security Testing
```bash
# Install security testing tools
pip install bandit safety

# Run security scans
bandit -r backend/
safety check
```

### Performance Testing
```bash
# Profile backend performance
python -m cProfile backend/main.py

# Monitor frontend performance
npm run build && npm run preview
```

## 📞 Support

### Test Issues
- Check test logs for specific error messages
- Verify environment variables are set correctly
- Ensure Docker containers are healthy
- Review mock configurations and fixtures

### Contributing Tests
- Follow existing test patterns and naming
- Include both positive and negative test cases
- Mock external dependencies appropriately
- Update documentation for new test categories

---

**Testing is critical for LinkOps-Afterlife's reliability and security. These comprehensive tests ensure that families can trust the platform with their most precious memories while maintaining the highest standards of data protection and user experience.** 🧪🔒