# WebSocket Implementation Guide

This document explains how to use the WebSocket implementation for real-time communication in ProjectMaker.

> **Security Note**: For details on authentication, permissions, and security features, see [WEBSOCKET_SECURITY.md](./WEBSOCKET_SECURITY.md)

## Overview

The WebSocket implementation provides **secure**, real-time bidirectional communication between the frontend and backend. It supports:

- **User Notifications**: Personal notifications delivered only to the authenticated user
- **Project updates**: Real-time updates for project-wide events
- **Agent messages**: Real-time agent responses and proactive messages
- **Channel updates**: Updates for specific channels
- **Conversation updates**: Real-time message delivery in conversations

### Key Features

- ✅ **Automatic Authentication**: JWT token-based authentication
- ✅ **Auto-Connect on Login**: Establishes connection when user logs in
- ✅ **Auto-Disconnect on Logout**: Cleans up connection when user logs out
- ✅ **Permission Checks**: Validates user access before subscriptions
- ✅ **User Isolation**: Messages only delivered to authorized users

## Architecture

### Backend Components

1. **WebSocket Consumer** (`api/ws/consumers.py`)
   - Handles WebSocket connections
   - Manages subscriptions to different channels/groups
   - Routes messages to clients

2. **WebSocket Serializer** (`api/ws/serializers.py`)
   - Validates subscription requests
   - Generates group names for subscriptions

3. **WebSocket Utility** (`api/utils/web_socket.py`)
   - Helper functions to send messages from Django views/services
   - Supports both sync and async usage

4. **Celery Tasks** (`api/agents/tasks.py`)
   - Background tasks that send WebSocket messages
   - Example: Agent message processing

### Frontend Components

1. **WebSocket Service** (`src/services/websocket.ts`)
   - Singleton service managing WebSocket connection
   - Handles reconnection, message queuing, and subscriptions
   - Provides callbacks for messages and connection status

2. **useWebSocket Hook** (`src/hooks/useWebSocket.ts`)
   - React hook for easy WebSocket integration
   - Auto-connect and auto-subscribe capabilities
   - Automatic cleanup on unmount

## Usage Examples

> **Note**: WebSocket connection is **automatically established on login** and **disconnected on logout**. You don't need to manually manage the connection lifecycle.

### Frontend: Using the Hook in a Component

```tsx
import React from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

function ConversationPage({ conversationId }: { conversationId: number }) {
  // WebSocket is already connected (authenticated on login)
  // This hook just subscribes to the conversation
  const { isConnected } = useWebSocket({
    conversationId,
    autoConnect: false,  // Already connected globally
    onMessage: (message) => {
      console.log('Received message:', message);

      // Handle different message types
      switch (message.type) {
        case 'agent_message':
          // Update UI with new agent message
          dispatch(addMessage(message.data));
          break;
        case 'agent_typing':
          // Show typing indicator
          setIsTyping(true);
          break;
        case 'notification':
          // Show notification
          toast.info(message.data.title);
          break;
        default:
          console.log('Unknown message type:', message.type);
      }
    }
  });

  return (
    <div>
      <p>Connection Status: {isConnected ? '🟢 Connected' : '🔴 Disconnected'}</p>
      {/* Your conversation UI */}
    </div>
  );
}
```

### Automatic Connection Flow

The connection is managed automatically by the auth system:

```typescript
// 1. User logs in
dispatch(login({ email, password }));

// 2. Auth slice automatically connects WebSocket
// (No manual intervention needed)

// 3. User navigates to pages - WebSocket is already connected

// 4. User logs out
dispatch(signOut());

// 5. Auth slice automatically disconnects WebSocket
// (No manual intervention needed)
```

### Frontend: Manual Subscription Management

```tsx
import { useWebSocket } from '../hooks/useWebSocket';

function ProjectDashboard({ projectId }: { projectId: number }) {
  const { subscribe, unsubscribe, onMessage } = useWebSocket({
    autoConnect: true,
    onMessage: (message) => {
      console.log('Project update:', message);
    }
  });

  useEffect(() => {
    // Subscribe to project updates
    subscribe({ projectId });

    // Cleanup
    return () => {
      unsubscribe({ projectId });
    };
  }, [projectId]);

  // Component render...
}
```

### Frontend: Direct Service Usage

```tsx
import websocketService from '../services/websocket';

// Connect
websocketService.connect();

// Subscribe to updates
websocketService.subscribe({
  action: 'subscribe',
  conversation_id: 123
});

// Listen for messages
const unsubscribe = websocketService.onMessage((message) => {
  console.log('Message received:', message);
});

// Send custom message
websocketService.send({
  type: 'custom_event',
  data: { foo: 'bar' }
});

// Cleanup
unsubscribe();
websocketService.disconnect();
```

### Backend: Sending Messages from Views/Services

```python
from api.utils.web_socket import send_message

# Send a message to a project group
send_message(
    channel_name='project_123',
    message={'content': 'Project updated!'},
    message_type='project_update'
)

# Send a message to a conversation group
send_message(
    channel_name='conversation-456',
    message={
        'id': 789,
        'content': 'Hello from agent!',
        'sender_name': 'Agent Name'
    },
    message_type='agent_message'
)
```

### Backend: Sending Messages from Celery Tasks

```python
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@shared_task
def my_background_task(conversation_id, data):
    # Your task logic...

    # Send WebSocket message
    channel_layer = get_channel_layer()
    group_name = f'conversation-{conversation_id}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'agent_message',  # Routes to consumer's agent_message method
            'message': {
                'content': 'Task completed!',
                'data': data
            }
        }
    )
```

## Subscription Channel Names

The following group names are supported:

- `project_{id}` - Project-wide updates
- `agent_{agent_id}_project_{project_id}` - Agent-specific updates within a project
- `channel_{id}` - Channel-specific updates
- `conversation-{id}` - Conversation-specific updates (for agent messages)

## Message Format

### Frontend to Backend

```json
{
  "action": "subscribe",
  "project_id": 123,
  "channel_id": "channel-abc",
  "agent_id": "agent-xyz",
  "conversation_id": 456
}
```

### Backend to Frontend

```json
{
  "type": "agent_message",
  "payload": {
    "id": 789,
    "content": "Hello!",
    "sender_name": "Agent Name"
  }
}
```

## Configuration

### Backend Settings

WebSocket configuration is in `config/settings/local.py` and `config/settings/production.py`:

```python
# Channel Layers (Redis backend for WebSocket)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [os.environ.get('REDIS_URL', 'redis://redis:6379/0')],
        },
    },
}

# JWT Settings (for WebSocket authentication)
SIMPLE_JWT = {
    'ACCESS_TOKEN_COOKIE': 'ACCESS',
    'REFRESH_TOKEN_COOKIE': 'REFRESH',
    # ... other JWT settings
}
```

### ASGI Configuration

The ASGI application uses JWT authentication middleware:

```python
# config/asgi.py
from api.ws.middleware import JWTAuthMiddlewareStack

application = ProtocolTypeRouter({
    "http": asgi_app,
    "websocket": JWTAuthMiddlewareStack(
        URLRouter(api.ws.routing.websocket_urlpatterns)
    ),
})
```

### Frontend Configuration

WebSocket URL is derived from the API URL. Authentication token is automatically managed by the auth system. No additional configuration needed.

## Testing

### Backend WebSocket Connection

You can test the WebSocket connection using a WebSocket client like `wscat`:

```bash
# Install wscat
npm install -g wscat

# Connect to WebSocket
wscat -c ws://localhost:5000/ws/

# Subscribe to a conversation
{"action": "subscribe", "conversation_id": 1}

# You should receive a confirmation
{"type": "subscription_confirmed", "groups": ["conversation-1"]}
```

### Testing Agent Message Flow

1. Create a conversation in the UI
2. Send a message to an agent
3. The Celery task `process_agent_message` will process it (5 second delay)
4. You should receive the agent's response via WebSocket in real-time

## Troubleshooting

### Connection Issues

1. **WebSocket fails to connect**
   - Check Redis is running: `docker ps | grep redis`
   - Check Django server is running with ASGI: `python manage.py runserver`
   - Verify WebSocket URL in browser console

2. **Messages not received**
   - Check subscription was successful (should receive `subscription_confirmed`)
   - Verify group name matches what backend is sending to
   - Check browser console for errors

3. **Reconnection issues**
   - The service auto-reconnects with exponential backoff
   - Max 5 reconnection attempts
   - Check network tab for WebSocket close codes

### Backend Issues

1. **Channel layer not found**
   - Ensure Redis is running
   - Check `CHANNEL_LAYERS` configuration in settings

2. **Messages not sent from backend**
   - Check Celery is running: `celery -A config worker -l info`
   - Verify group name is correct
   - Check Django logs for errors

## Best Practices

1. **Always clean up subscriptions** - Use the useWebSocket hook's auto-cleanup or manually unsubscribe
2. **Handle reconnection** - The service handles this automatically, but your UI should show connection status
3. **Message type handling** - Always handle different message types in your onMessage callback
4. **Error handling** - Wrap message handlers in try-catch blocks
5. **Performance** - Avoid creating too many subscriptions; use project-level or channel-level when possible

## Security Considerations

1. **Authentication** - The WebSocket consumer uses `AuthMiddlewareStack` to verify user authentication
2. **Authorization** - Implement permission checks in the serializer's `get_group_names` method
3. **Input validation** - All subscription requests are validated through the serializer
4. **Rate limiting** - Consider implementing rate limiting for WebSocket messages in production

## Future Enhancements

- [ ] Add typing indicators for multi-user conversations
- [ ] Implement presence/online status
- [ ] Add message acknowledgment system
- [ ] Support for binary messages (file uploads)
- [ ] WebSocket compression for large payloads
