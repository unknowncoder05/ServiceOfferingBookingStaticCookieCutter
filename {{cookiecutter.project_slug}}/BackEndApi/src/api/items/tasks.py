"""
Item Celery tasks - Background task definitions for Item operations.

This module demonstrates Celery task patterns:
- Simple task definition with @shared_task
- Task with retry logic
- Task chaining and grouping examples

Usage:
    from api.items.tasks import cleanup_archived_items

    # Run synchronously (for testing)
    cleanup_archived_items()

    # Run asynchronously
    cleanup_archived_items.delay()

    # Run with countdown (delay execution)
    cleanup_archived_items.apply_async(countdown=60)
"""
from datetime import timedelta

from celery import shared_task
from django.utils import timezone


@shared_task(bind=True, max_retries=3)
def cleanup_archived_items(self, days_old: int = 30):
    """
    Delete items that have been archived for more than X days.

    This is an example periodic task that could be scheduled
    via Celery Beat to run daily.

    Args:
        days_old: Number of days an item must be archived before deletion

    Returns:
        Number of items deleted
    """
    from api.items.models import Item

    try:
        cutoff_date = timezone.now() - timedelta(days=days_old)
        deleted_count, _ = Item.objects.filter(
            status=Item.Status.ARCHIVED,
            updated_at__lt=cutoff_date
        ).delete()
        return deleted_count
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def send_item_notification(item_id: int, notification_type: str):
    """
    Send a notification about an item.

    This is an example task for sending notifications asynchronously.
    Implement your notification logic (email, push, webhook, etc.) here.

    Args:
        item_id: The ID of the item
        notification_type: Type of notification ('created', 'updated', 'archived')
    """
    from api.items.models import Item

    try:
        item = Item.objects.select_related('owner').get(id=item_id)
    except Item.DoesNotExist:
        return None

    # Example: Log the notification (replace with actual notification logic)
    # You could use Django's email, push notifications, webhooks, etc.
    print(f"Notification: Item '{item.name}' was {notification_type} by {item.owner}")

    return {
        'item_id': item_id,
        'notification_type': notification_type,
        'status': 'sent'
    }


@shared_task
def bulk_update_item_status(item_ids: list, new_status: str):
    """
    Update status of multiple items in bulk.

    Useful for batch operations that might be slow to do synchronously.

    Args:
        item_ids: List of item IDs to update
        new_status: The new status to set

    Returns:
        Number of items updated
    """
    from api.items.models import Item

    return Item.objects.filter(id__in=item_ids).update(status=new_status)
