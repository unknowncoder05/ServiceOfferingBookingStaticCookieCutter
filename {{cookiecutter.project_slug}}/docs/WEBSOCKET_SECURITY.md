# WebSocket Security & Authentication Guide

This document explains how the WebSocket implementation ensures secure, authenticated connections with proper user isolation.

## Security Overview

The WebSocket implementation includes:

1. **JWT Token Authentication** - All connections require valid JWT tokens
2. **User-Specific Channels** - Automatic subscription to user-only notification channels
3. **Permission Checks** - Validation before subscribing to any resource
4. **Automatic Connection Management** - Connect on login, disconnect on logout
5. **User Isolation** - Messages only delivered to authorized users

## Authentication Flow

### 1. Login Process

When a user logs in successfully:

```typescript
// User logs in
dispatch(login({ email, password }))

// On successful login (authSlice.ts):
.addCase(login.fulfilled, (state, action) => {
  // Store tokens
  state.tokens = action.payload;

  // AUTOMATICALLY establish WebSocket connection
  websocketService.setAuthToken(action.payload.access);
  websocketService.connect();
})
```

### 2. WebSocket Connection

The WebSocket service automatically:

```typescript
// Includes token in connection URL
const url = `wss://api.example.com/ws/?token=${encodeURIComponent(token)}`;
const ws = new WebSocket(url);
```

### 3. Backend Authentication

The JWT middleware validates the token:

```python
# api/ws/middleware.py
class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Extract token from query param or cookie
        token = query_params.get('token') or cookies.get('ACCESS')

        # Validate token and get user
        if token:
            scope['user'] = await get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()
```

### 4. Connection Acceptance

The consumer checks authentication:

```python
# api/ws/consumers.py
async def connect(self):
    user = self.scope.get('user')

    # Reject unauthenticated connections
    if not user or user.is_anonymous:
        await self.close(code=4001)  # Unauthorized
        return

    await self.accept()

    # Auto-subscribe to user's personal channel
    user_group = f'user_{user.id}'
    await self.channel_layer.group_add(user_group, self.channel_name)
```

## User-Specific Notifications

Every authenticated user is automatically subscribed to their personal notification channel:

```
user_{user_id}
```

### Sending Notifications to Specific Users

```python
from api.utils.web_socket import send_message

# Send notification to specific user
send_message(
    channel_name=f'user_{user.id}',
    message={
        'title': 'New Message',
        'body': 'You have a new message from Agent X'
    },
    message_type='notification'
)
```

### Frontend: Receiving User Notifications

Notifications are automatically received once logged in:

```typescript
useWebSocket({
  autoConnect: true,  // Auto-connects on mount if authenticated
  onMessage: (message) => {
    if (message.type === 'notification') {
      // Display notification to user
      toast.info(message.payload.title);
    }
  }
});
```

## Permission-Based Subscriptions

Users can only subscribe to resources they have permission to access.

### Subscription Permission Flow

1. **Client requests subscription**:
```typescript
websocketService.subscribe({
  action: 'subscribe',
  project_id: 123,
  conversation_id: 456
});
```

2. **Backend validates permissions**:
```python
# api/ws/serializers.py
def check_permissions(self, user):
    project_id = self.validated_data.get('project_id')

    if project_id:
        project = Project.objects.get(id=project_id)
        # Check ownership
        if project.user_id != user.id:
            return False  # Permission denied

    return True
```

3. **Subscription granted or denied**:
```python
# api/ws/consumers.py
if not has_permission:
    await self.send_json({
        'type': 'error',
        'error': 'Permission denied for requested subscription'
    })
    return
```

## Channel Groups & Isolation

Different types of channels ensure proper data isolation:

| Channel Pattern | Description | Who Can Subscribe |
|----------------|-------------|-------------------|
| `user_{user_id}` | User's personal notifications | Only that user (automatic) |
| `project_{project_id}` | Project updates | Project owner and team members |
| `conversation-{conv_id}` | Agent conversation messages | Conversation owner |
| `agent_{agent_id}_project_{project_id}` | Agent-specific updates in project | Project owner |

## Security Features

### 1. Token Expiration Handling

When a token expires:

```typescript
// Frontend automatically handles 401/4001 WebSocket close codes
ws.onclose = (event) => {
  if (event.code === 4001) {
    console.log('Authentication failed, redirecting to login...');
    // User will be logged out via API interceptor
  }
};
```

### 2. Automatic Cleanup on Logout

```typescript
// authSlice.ts
.addCase(signOut.fulfilled, (state) => {
  // Clear auth state
  state.isAuthenticated = false;

  // AUTOMATICALLY disconnect WebSocket
  websocketService.disconnect();
  websocketService.setAuthToken(null);
})
```

### 3. Connection on App Load

If user is already authenticated (token in localStorage):

```typescript
// App.tsx initializes auth
useEffect(() => {
  const token = localStorage.getItem('access_token');
  if (token) {
    dispatch(getCurrentUser());  // Validates token & connects WebSocket
  }
}, []);

// authSlice.ts
.addCase(getCurrentUser.fulfilled, (state, action) => {
  state.user = action.payload;

  // Connect WebSocket with existing token
  const token = localStorage.getItem('access_token');
  websocketService.setAuthToken(token);
  websocketService.connect();
})
```

## Message Flow Examples

### Example 1: Agent Response to User

```python
# Backend: Celery task sends agent message
@shared_task
def process_agent_message(message_id):
    # ... process message ...

    # Send via WebSocket to conversation channel
    channel_layer = get_channel_layer()
    conversation_id = message.conversation_id

    async_to_sync(channel_layer.group_send)(
        f'conversation-{conversation_id}',
        {
            'type': 'agent_message',
            'message': {
                'content': 'Agent response here',
                'sender': 'Agent Name'
            }
        }
    )
```

```typescript
// Frontend: User receives message in real-time
useWebSocket({
  conversationId: 123,
  onMessage: (msg) => {
    if (msg.type === 'agent_message') {
      // Update UI with new message
      dispatch(addMessage(msg.data));
    }
  }
});
```

### Example 2: Project-Wide Notification

```python
# Backend: Send notification to all project members
def notify_project_members(project_id, notification):
    send_message(
        channel_name=f'project_{project_id}',
        message=notification,
        message_type='project_notification'
    )
```

```typescript
// Frontend: All project members receive it
useWebSocket({
  projectId: 123,
  onMessage: (msg) => {
    if (msg.type === 'project_notification') {
      toast.info(msg.payload.message);
    }
  }
});
```

## Security Best Practices

### 1. Always Validate Permissions

Before sending messages to a group, verify the recipient has access:

```python
# Bad: Don't do this
send_message(f'project_{project_id}', data, 'update')

# Good: Verify first
project = Project.objects.get(id=project_id)
if project.user_id == requesting_user.id:
    send_message(f'project_{project_id}', data, 'update')
```

### 2. Use User-Specific Channels for Sensitive Data

```python
# For personal notifications, use user channels
send_message(f'user_{user.id}', sensitive_data, 'private_notification')

# Not project channels (visible to all members)
```

### 3. Don't Trust Client-Side Data

Always validate on the backend:

```python
def check_permissions(self, user):
    # ALWAYS check database, not just request data
    project = Project.objects.get(id=self.validated_data['project_id'])
    return project.user_id == user.id
```

### 4. Limit Subscription Scope

Don't allow wildcard or overly broad subscriptions:

```python
# Bad: Allow subscribing to all projects
group_names.append('all_projects')

# Good: Specific project only
group_names.append(f'project_{project_id}')
```

## Testing Authentication

### Test 1: Unauthenticated Connection

```bash
# Try connecting without token
wscat -c ws://localhost:5000/ws/

# Should close with code 4001
```

### Test 2: Valid Token

```bash
# Connect with valid token
wscat -c 'ws://localhost:5000/ws/?token=YOUR_JWT_TOKEN'

# Should receive:
# {"type": "connection_established", "user_id": 123, "user_group": "user_123"}
```

### Test 3: Invalid Token

```bash
# Connect with invalid/expired token
wscat -c 'ws://localhost:5000/ws/?token=invalid_token'

# Should close with code 4001
```

### Test 4: Permission Check

```javascript
// Subscribe to project you don't own
ws.send(JSON.stringify({
  action: 'subscribe',
  project_id: 999  // Not your project
}));

// Should receive:
// {"type": "error", "error": "Permission denied for requested subscription"}
```

## Monitoring & Logging

### Backend Logs

```python
# Consumer logs authentication
print(f"WebSocket connected: user_id={user.id}")
print(f"Permission check failed for user {user.id} on project {project_id}")
```

### Frontend Console

```javascript
// Service logs all events
console.log('WebSocket connected');
console.log('WebSocket authenticated for user:', userId);
console.log('WebSocket message received:', message);
```

## Troubleshooting

### Issue: Messages not received

1. Check user is subscribed:
   ```javascript
   // Should see "subscription_confirmed"
   ```

2. Verify permission:
   ```python
   # Check user owns the resource
   Project.objects.filter(id=project_id, user=user).exists()
   ```

3. Check group name matches:
   ```python
   # Frontend subscribes to: "project_123"
   # Backend sends to: "project_123" (must match exactly)
   ```

### Issue: Connection rejected

1. Check token is valid:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5000/api/v1/users/me/
   ```

2. Verify token is passed correctly:
   ```javascript
   // Check WebSocket URL includes token
   console.log(websocketService.getWebSocketUrl());
   ```

3. Check middleware is installed:
   ```python
   # config/asgi.py should use JWTAuthMiddlewareStack
   ```

## Summary

The WebSocket implementation provides:

- ✅ **Secure Authentication**: JWT tokens required for all connections
- ✅ **User Isolation**: Automatic user-specific channels
- ✅ **Permission Validation**: Resources checked before subscription
- ✅ **Automatic Management**: Connect on login, disconnect on logout
- ✅ **Session Sync**: Connection tied to authentication state
- ✅ **Real-time Notifications**: Messages delivered only to authorized users

All notifications are automatically scoped to the authenticated user, ensuring data privacy and security.
