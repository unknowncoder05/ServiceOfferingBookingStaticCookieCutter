# Celery Setup for Agent Async Tasks

## Overview

This project uses Celery for asynchronous task processing, specifically for handling agent responses to user messages. When a user sends a message to an agent, the response is processed asynchronously via Celery and delivered through WebSockets.

## Architecture

1. **User sends message** → API endpoint receives it
2. **Message saved** → User message stored in database
3. **Celery task triggered** → `process_agent_message` task queued
4. **Task processes** → Waits 5 seconds (simulating processing)
5. **Agent responds** → Response saved to database
6. **WebSocket notification** → Message sent via WebSocket to connected clients

## Components

### Celery Configuration
- **File**: `src/config/celery.py`
- **Broker/Backend**: Redis (configured via `REDIS_URL` env variable)
- **Settings**: `src/config/settings/local.py` (Celery configuration section)

### Tasks
- **File**: `src/api/agents/tasks.py`
- **Main Task**: `process_agent_message(message_id)` - Processes user messages and generates agent responses
- **Secondary Task**: `send_proactive_agent_message(conversation_id, content)` - Sends proactive messages from agents

### WebSocket Integration
- **Consumer**: `src/api/ws/consumers.py` - Handles WebSocket connections
- **Routing**: `src/api/ws/routing.py` - WebSocket URL patterns
- **Serializer**: `src/api/ws/serializers/ws.py` - Validates WebSocket subscriptions

## Running Celery

### Development (Local)

1. **Start Redis** (if not already running):
   ```bash
   docker run -d -p 6379:6379 redis:latest
   # OR if using docker-compose
   docker-compose up -d redis
   ```

2. **Start Celery Worker**:
   ```bash
   cd src
   celery -A config.celery_app worker -l INFO
   ```

3. **Start Celery Beat** (for periodic tasks - optional):
   ```bash
   cd src
   celery -A config.celery_app beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
   ```

### Production

Use the provided startup scripts:
```bash
./compose/production/django/celery/worker/start
./compose/production/django/celery/beat/start
```

## Testing the Setup

### 1. Connect to WebSocket

Connect to the WebSocket endpoint:
```
ws://localhost:8000/ws/
```

Subscribe to a conversation:
```json
{
  "type": "conversation",
  "conversation_id": 1
}
```

You should receive a confirmation:
```json
{
  "type": "subscription_confirmed",
  "groups": ["conversation-1"]
}
```

### 2. Send a Message

Make a POST request to send a message:
```bash
curl -X POST http://localhost:8000/api/v1/agents/conversations/1/send_message/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "content": "Hello, agent!",
    "message_type": "text"
  }'
```

### 3. Receive Agent Response

After 5 seconds, you should receive a WebSocket message:
```json
{
  "type": "agent_message",
  "message": {
    "id": 123,
    "conversation_id": 1,
    "content": "Hello! I'm Agent Name. I received your message...",
    "message_type": "text",
    "is_from_user": false,
    "sender_name": "Agent Name",
    "sender_avatar": "🤖",
    "created_at": "2024-01-12T10:30:00Z",
    "metadata": {
      "task_id": "abc123",
      "processing_time": 5
    }
  }
}
```

## Environment Variables

Make sure these are set in your environment:

```bash
# Redis for Celery and Channels
REDIS_URL=redis://localhost:6379/0

# Database
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
```

## Monitoring

### Check Celery Status
```bash
celery -A config.celery_app inspect active
celery -A config.celery_app inspect stats
```

### Check Redis Connection
```bash
redis-cli ping
# Should return: PONG
```

### View Task Results
```bash
celery -A config.celery_app result TASK_ID
```

## Troubleshooting

### Issue: Tasks not executing
- Check if Celery worker is running
- Verify Redis connection
- Check worker logs for errors

### Issue: WebSocket not receiving messages
- Ensure WebSocket is connected and subscribed to correct conversation
- Check Redis connection for Channel Layers
- Verify `CHANNEL_LAYERS` configuration in settings

### Issue: Import errors
- Make sure all requirements are installed: `pip install -r requirements/local.txt`
- Check that `config/__init__.py` imports the celery app

## Next Steps

To customize agent behavior:
1. Edit `api/agents/tasks.py` - Modify `process_agent_message` function
2. Add LLM integration (OpenAI, Anthropic) for intelligent responses
3. Implement context awareness using conversation history
4. Add file attachments support
5. Implement typing indicators

## WebSocket Message Types

The WebSocket consumer supports these subscription types:
- `conversation` - Subscribe to agent conversation messages
- `event` - Subscribe to event updates (legacy)

## API Endpoints

### Conversations
- `GET /api/v1/agents/conversations/` - List conversations
- `POST /api/v1/agents/conversations/` - Create conversation
- `GET /api/v1/agents/conversations/{id}/` - Get conversation details
- `POST /api/v1/agents/conversations/{id}/send_message/` - Send message (triggers Celery task)

### Messages
- `GET /api/v1/agents/conversations/{id}/messages/` - List messages in conversation
