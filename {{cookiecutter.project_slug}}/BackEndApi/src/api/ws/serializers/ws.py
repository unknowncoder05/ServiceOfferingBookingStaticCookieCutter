# Rest Framework
from rest_framework import serializers
from api.projects.models import Project
from api.agents.models import Conversation


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
    project_id = serializers.IntegerField(required=False, allow_null=True)
    channel_id = serializers.CharField(required=False, allow_null=True)
    agent_id = serializers.CharField(required=False, allow_null=True)
    conversation_id = serializers.IntegerField(required=False, allow_null=True)

    def get_group_names(self):
        """
        Generate channel group names based on subscription request.

        Returns a list of group names the client should subscribe to.
        Supports subscribing to:
        - Project-wide updates: 'project_{id}'
        - Agent-specific updates: 'agent_{id}_project_{project_id}'
        - Channel updates: 'channel_{id}'
        - Conversation updates: 'conversation-{id}'
        """
        group_names = []

        project_id = self.validated_data.get('project_id')
        channel_id = self.validated_data.get('channel_id')
        agent_id = self.validated_data.get('agent_id')
        conversation_id = self.validated_data.get('conversation_id')

        # Subscribe to project updates
        if project_id:
            group_names.append(f'project_{project_id}')

        # Subscribe to specific agent updates within a project
        if agent_id and project_id:
            group_names.append(f'agent_{agent_id}_project_{project_id}')

        # Subscribe to channel updates
        if channel_id:
            group_names.append(f'channel_{channel_id}')

        # Subscribe to conversation updates
        if conversation_id:
            group_names.append(f'conversation-{conversation_id}')

        return group_names

    def check_permissions(self, user):
        """
        Check if the user has permission to subscribe to the requested resources.

        Args:
            user: The requesting user

        Returns:
            bool: True if user has permission, False otherwise
        """
        project_id = self.validated_data.get('project_id')
        conversation_id = self.validated_data.get('conversation_id')

        # Check project access
        if project_id:
            try:
                project = Project.objects.get(id=project_id)
                # Check if user owns the project or is a team member
                if project.user_id != user.id:
                    return False
            except Project.DoesNotExist:
                return False

        # Check conversation access
        if conversation_id:
            try:
                conversation = Conversation.objects.select_related('user', 'project').get(id=conversation_id)
                # User must own the conversation or the associated project
                if conversation.user_id != user.id and conversation.project.user_id != user.id:
                    return False
            except Conversation.DoesNotExist:
                return False

        # All checks passed
        return True
