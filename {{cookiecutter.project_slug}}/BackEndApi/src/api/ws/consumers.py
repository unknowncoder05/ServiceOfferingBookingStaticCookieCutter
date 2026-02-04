# Channels
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

# Serializers
from api.ws.serializers import WSSerializer
from api.ws.middleware import get_user_from_token


class WSConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        """
        Handle WebSocket connection.
        Accepts connection without authentication.
        Client must send an 'authenticate' message with token after connecting.
        """
        # Accept the connection without authentication
        await self.accept()

        # Send connection accepted message prompting for authentication
        await self.send_json({
            'type': 'connection_accepted',
            'message': 'Connection established. Please send authenticate message with token.',
        })

    async def authenticate(self, token):
        """
        Authenticate the WebSocket connection using a JWT token.
        Called when client sends an 'authenticate' message.
        """
        user = await get_user_from_token(token)

        if not user:
            await self.send_json({
                'type': 'authentication_failed',
                'error': 'Invalid or expired token',
            })
            await self.close(code=4001)
            return False

        # Set the authenticated user in scope
        self.scope['user'] = user

        # Subscribe to user's personal notification channel
        user_group = f'user_{user.id}'
        self.groups.append(user_group)
        await self.channel_layer.group_add(
            user_group,
            self.channel_name,
        )

        # Send authentication success with user info
        await self.send_json({
            'type': 'connection_established',
            'user_id': user.id,
            'user_group': user_group,
        })

        return True

    async def disconnect(self, close_code):
        """Handle disconnect - cleanup groups."""
        # Groups are automatically cleaned up by parent class
        pass

    async def notify(self, event):
        """
        This handles calls elsewhere in this codebase that look
        like:

            channel_layer.group_send(group_name, {
                'type': 'notify',  # This routes it to this handler.
                'content': json_message,
            })

        Don't try to directly use send_json or anything; this
        decoupling will help you as things grow.
        """
        await self.send_json(event["content"])

    async def agent_message(self, event):
        """
        Handle agent messages sent via Celery tasks.

        This receives messages from channel_layer.group_send() calls
        with type='agent_message' and forwards them to the WebSocket client.
        """
        print(f"[CONSUMER] Received agent_message event: {event}")
        print(f"[CONSUMER] Current groups: {self.groups}")
        await self.send_json({
            'type': 'agent_message',
            'message': event['message']
        })
        print(f"[CONSUMER] Sent agent_message to client")

    async def backlog_update(self, event):
        """
        Handle backlog update notifications.

        Sent when backlog items are auto-extracted from conversations.
        """
        await self.send_json({
            'type': 'backlog_update',
            'data': event.get('content', event)
        })

    async def code_change_pending(self, event):
        """
        Handle code change pending approval notifications.

        Sent when an agent generates code that needs user review.
        """
        await self.send_json({
            'type': 'code_change_pending',
            'data': event.get('content', event)
        })

    async def task_status_update(self, event):
        """
        Handle task status change notifications.

        Sent when a scrum task status changes.
        """
        await self.send_json({
            'type': 'task_status_update',
            'data': event.get('content', event)
        })

    async def backlog_extraction(self, event):
        """
        Handle backlog extraction notifications.

        Sent after items are extracted from a conversation.
        """
        await self.send_json({
            'type': 'backlog_extraction',
            'data': event.get('content', event)
        })

    async def code_change_status(self, event):
        """
        Handle code change status update notifications.

        Sent when a code change is approved, rejected, applied, or reverted.
        """
        await self.send_json({
            'type': 'code_change_status',
            'data': event.get('content', event)
        })

    async def tool_call_pending(self, event):
        """
        Handle pending tool call approval notifications.

        Sent when an agent wants to execute tools and requires user approval.
        Contains the batch of tool calls waiting for approval.
        """
        await self.send_json({
            'type': 'tool_call_pending',
            'data': event.get('content', event)
        })

    async def tool_call_executed(self, event):
        """
        Handle tool call execution completion notifications.

        Sent after tool calls are executed (post-approval).
        """
        await self.send_json({
            'type': 'tool_call_executed',
            'data': event.get('content', event)
        })

    # ==================================================================
    # RESOURCE EVENTS
    # ==================================================================

    async def resource_created(self, event):
        """
        Handle resource creation notifications.

        Sent when a new resource is created by a user or agent.
        """
        await self.send_json({
            'type': 'resource_created',
            'data': event.get('content', event)
        })

    async def resource_updated(self, event):
        """
        Handle resource update notifications.

        Sent when a resource is modified.
        """
        await self.send_json({
            'type': 'resource_updated',
            'data': event.get('content', event)
        })

    async def resource_deleted(self, event):
        """
        Handle resource deletion notifications.

        Sent when a resource is deleted.
        """
        await self.send_json({
            'type': 'resource_deleted',
            'data': event.get('content', event)
        })

    async def resource_locked(self, event):
        """
        Handle resource lock notifications.

        Sent when a resource is locked for editing.
        """
        await self.send_json({
            'type': 'resource_locked',
            'data': event.get('content', event)
        })

    async def resource_unlocked(self, event):
        """
        Handle resource unlock notifications.

        Sent when a resource lock is released.
        """
        await self.send_json({
            'type': 'resource_unlocked',
            'data': event.get('content', event)
        })

    async def resource_comment_added(self, event):
        """
        Handle resource comment notifications.

        Sent when a comment is added to a resource.
        """
        await self.send_json({
            'type': 'resource_comment_added',
            'data': event.get('content', event)
        })

    async def resource_collaborator_joined(self, event):
        """
        Handle collaborator join notifications.

        Sent when someone starts viewing/editing a resource.
        """
        await self.send_json({
            'type': 'resource_collaborator_joined',
            'data': event.get('content', event)
        })

    async def resource_collaborator_left(self, event):
        """
        Handle collaborator leave notifications.

        Sent when someone stops viewing/editing a resource.
        """
        await self.send_json({
            'type': 'resource_collaborator_left',
            'data': event.get('content', event)
        })

    async def receive_json(self, content, **kwargs):
        """
        Handle incoming WebSocket messages from the client.

        Handles authentication, ping/pong, and subscription requests.
        """
        action = content.get('action')
        msg_type = content.get('type')

        # Handle ping messages (keep-alive)
        if msg_type == 'ping' or action == 'ping':
            await self.send_json({'type': 'pong'})
            return

        # Handle authentication message
        if action == 'authenticate':
            token = content.get('token')
            if not token:
                await self.send_json({
                    'type': 'error',
                    'error': 'Token is required for authentication',
                })
                return
            await self.authenticate(token)
            return

        # For all other actions, require authentication
        user = self.scope.get('user')
        if not user or user.is_anonymous:
            await self.send_json({
                'type': 'error',
                'error': 'Unauthorized. Please authenticate first.',
            })
            return

        serializer = WSSerializer(data=content)

        try:
            await sync_to_async(serializer.is_valid)(raise_exception=True)
        except Exception as e:
            print("WEBSOCKET ERROR:", e)
            await self.send_json({
                'type': 'error',
                'error': str(e)
            })
            return

        # Check permissions before subscribing
        try:
            has_permission = await sync_to_async(serializer.check_permissions)(user)
            if not has_permission:
                await self.send_json({
                    'type': 'error',
                    'error': 'Permission denied for requested subscription'
                })
                return
        except Exception as e:
            print("PERMISSION CHECK ERROR:", e)
            await self.send_json({
                'type': 'error',
                'error': 'Permission check failed'
            })
            return

        # Get group names for subscription
        group_names = await sync_to_async(serializer.get_group_names)()
        action = serializer.validated_data.get('action', 'subscribe')

        if action == 'subscribe':
            # Subscribe to requested groups
            for group_name in group_names:
                if group_name not in self.groups:
                    self.groups.append(group_name)
                    await self.channel_layer.group_add(
                        group_name,
                        self.channel_name,
                    )
                    print(f"[CONSUMER] Subscribed to group: {group_name}")

            print(f"[CONSUMER] All subscribed groups: {self.groups}")

            # Send confirmation
            await self.send_json({
                'type': 'subscription_confirmed',
                'groups': group_names
            })
        elif action == 'unsubscribe':
            # Unsubscribe from requested groups
            for group_name in group_names:
                if group_name in self.groups:
                    self.groups.remove(group_name)
                    await self.channel_layer.group_discard(
                        group_name,
                        self.channel_name,
                    )

            # Send confirmation
            await self.send_json({
                'type': 'unsubscription_confirmed',
                'groups': group_names
            })
