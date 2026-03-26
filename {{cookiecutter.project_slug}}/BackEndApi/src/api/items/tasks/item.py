"""Item Celery tasks — background task definitions for Item operations."""
from datetime import timedelta

from celery import shared_task
from django.utils import timezone


@shared_task(bind=True, max_retries=3)
def cleanup_archived_items(self, days_old: int = 30):
    """Delete items archived for more than X days."""
    from api.items.models import Item

    try:
        cutoff_date = timezone.now() - timedelta(days=days_old)
        deleted_count, _ = Item.objects.filter(
            status=Item.Status.ARCHIVED,
            updated_at__lt=cutoff_date,
        ).delete()
        return deleted_count
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def send_item_notification(item_id: int, notification_type: str):
    """Send a notification about an item (implement with email/push/webhook)."""
    from api.items.models import Item

    try:
        item = Item.objects.select_related('owner').get(id=item_id)
    except Item.DoesNotExist:
        return None

    print(f"Notification: Item '{item.name}' was {notification_type} by {item.owner}")

    return {
        'item_id': item_id,
        'notification_type': notification_type,
        'status': 'sent',
    }


@shared_task
def bulk_update_item_status(item_ids: list, new_status: str):
    """Update status of multiple items in bulk."""
    from api.items.models import Item

    return Item.objects.filter(id__in=item_ids).update(status=new_status)
