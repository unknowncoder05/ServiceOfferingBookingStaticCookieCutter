# Channels
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


async def send_message_async(channel_name, message, message_type):
    """
    Send message to WebSocket channel (async version).

    Args:
        channel_name: The group name to send to (e.g., 'project_123')
        message: The message payload to send
        message_type: The message type for frontend handling
    """
    group_name = channel_name
    channel_layer = get_channel_layer()

    content = {
        # This "type" passes through to the front-end to facilitate
        # our Redux events.
        "type": message_type,
        "payload": message,
    }

    await channel_layer.group_send(group_name, {
        # This "type" defines which handler on the Consumer gets
        # called.
        "type": "notify",
        "content": content,
    })


def send_message(channel_name, message, message_type):
    """
    Send message to WebSocket channel (sync wrapper).

    Args:
        channel_name: The group name to send to (e.g., 'project_123')
        message: The message payload to send
        message_type: The message type for frontend handling
    """
    async_to_sync(send_message_async)(channel_name, message, message_type)
