# Rest Framework
from rest_framework import serializers


class WSSerializer(serializers.Serializer):
    """
    Serializer for WebSocket subscription requests.

    Validates incoming WebSocket messages and determines which
    channel groups the client should subscribe to.
    """
    action = serializers.ChoiceField(
        choices=['subscribe', 'unsubscribe'],
        default='subscribe'
    )
    channel_id = serializers.CharField(required=False, allow_null=True)
    agent_id = serializers.CharField(required=False, allow_null=True)
    conversation_id = serializers.IntegerField(required=False, allow_null=True)

    def get_group_names(self):
        """
        Generate channel group names based on subscription request.

        Returns a list of group names the client should subscribe to.
        Supports subscribing to:
        - Agent-specific updates: 'agent_{id}'
        - Channel updates: 'channel_{id}'
        - Conversation updates: 'conversation-{id}'
        """
        group_names = []

        channel_id = self.validated_data.get('channel_id')
        agent_id = self.validated_data.get('agent_id')
        conversation_id = self.validated_data.get('conversation_id')

        if agent_id:
            group_names.append(f'agent_{agent_id}')

        if channel_id:
            group_names.append(f'channel_{channel_id}')

        if conversation_id:
            group_names.append(f'conversation-{conversation_id}')

        return group_names

    def check_permissions(self, user):
        """
        Check if the user has permission to subscribe to the requested resources.

        Override this method in your application to add resource-specific
        permission checks.

        Args:
            user: The requesting user

        Returns:
            bool: True if user has permission, False otherwise
        """
        return user.is_authenticated
