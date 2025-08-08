# 🎭 Persona System Acceptance Tests

Quick commands to verify the avatar persona system is working correctly.

## 🔧 Prerequisites

Ensure the backend is running with the persona files mounted:

```bash
# Development
cd backend && python main.py

# Production
docker compose -f docker-compose.prod.yml up -d
```

## 🧪 API Tests

### 1. Health Check
```bash
curl https://yourdomain.com/healthz
# Expected: {"status": "ok", "timestamp": "..."}
```

### 2. List Available Personas
```bash
curl https://yourdomain.com/personas
# Expected: {"personas": ["james"], "count": 1, ...}
```

### 3. Get James Persona Details
```bash
curl https://yourdomain.com/personas/james
# Expected: Full persona config with display_name, style, memory, etc.
```

### 4. Test Persona Chat (Pinned Q&A)
```bash
curl -X POST https://yourdomain.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is AfterLife?",
    "persona_id": "james"
  }'
# Expected: Pinned answer about AfterLife + matched_qa: true
```

### 5. Test General Conversation
```bash
curl -X POST https://yourdomain.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about your Kubernetes experience",
    "persona_id": "james"
  }'
# Expected: Response about CKA certification and K8s deployments
```

### 6. Test Project-Specific Question
```bash
curl -X POST https://yourdomain.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What makes LinkOps unique?",
    "persona_id": "james"
  }'
# Expected: Pinned answer about LinkOps + tool execution + matched_qa: true
```

### 7. Test Boundaries
```bash
curl -X POST https://yourdomain.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are your political views?",
    "persona_id": "james"
  }'
# Expected: Professional refusal response
```

### 8. Test Alternative Persona Route
```bash
curl -X POST https://yourdomain.com/chat/james \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the LinkOps pillars?",
    "context": "recruiter interview"
  }'
# Expected: Answer about Chat, HTC, Monitoring, Toolkit
```

## 🎯 Expected Response Format

All chat responses should include:
```json
{
  "response": {
    "answer": "...",
    "persona_id": "james",
    "persona_name": "James (LinkOps Creator)",
    "tts_voice": "en_US-male-1",
    "matched_qa": true/false,
    "system_prompt_preview": "You are James..."
  },
  "timestamp": "2024-..."
}
```

## 🚨 Error Cases

### Missing Persona
```bash
curl https://yourdomain.com/personas/nonexistent
# Expected: 404 with available personas list
```

### Empty Message
```bash
curl -X POST https://yourdomain.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "", "persona_id": "james"}'
# Expected: 400 "Message is required and cannot be empty"
```

## ✅ Success Criteria

- [ ] All persona endpoints return 200 OK
- [ ] James persona loads with complete configuration
- [ ] Pinned Q&A triggers for expected keywords ("AfterLife", "LinkOps")  
- [ ] Contextual responses generated for non-pinned questions
- [ ] Professional boundaries enforced (refusals for politics, etc.)
- [ ] TTS voice field populated in responses
- [ ] Error handling graceful with helpful messages

## 🎭 James Persona Verification

Key aspects to verify in responses:
- ✅ Professional, confident tone
- ✅ Technical accuracy (CKA, Security+, Kubernetes)
- ✅ Project mentions (LinkOps, AfterLife)
- ✅ Step-by-step explanations when appropriate
- ✅ Brief humor without being unprofessional
- ✅ Boundaries respected

## 🚀 Frontend Tests

1. Open React app and navigate to InteractionPanel
2. Verify persona selector appears with "James" option
3. Verify persona info displays after selection
4. Test quick text chat (Send button)
5. Verify persona responses show with badges for pinned Q&A
6. Test both interaction modes work

## 📈 Monitoring

Check logs for persona system activity:
```bash
# Development
tail -f backend/logs/app.log | grep -i persona

# Production
docker logs afterlife-backend --follow | grep -i persona
```