from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction
from .models import Message, Notification, MessageHistory
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Signal receiver that creates a notification for the receiver
    when a new message is created.
    """
    if created:  # Only create notification for new messages
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            is_read=False
        )

@receiver(pre_save, sender=Message)
def save_previous_message_content(sender, instance, **kwargs):
    """
    Signal receiver that saves the previous content of a message
    to MessageHistory before it's updated.
    """
    if instance.pk:  # Only for existing messages
        try:
            old_message = Message.objects.get(pk=instance.pk)
            if old_message.content != instance.content:  # Only if content changed
                # Save old content to history
                MessageHistory.objects.create(
                    original_message=instance,
                    content=old_message.content,
                    edited_by=instance.sender  # Assuming the sender is the one editing
                )
                # Update message metadata
                instance.is_edited = True
                instance.last_edited = timezone.now()
        except Message.DoesNotExist:
            pass  # New message, nothing to save in history


@receiver(post_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    """
    Signal handler to clean up related data when a user is deleted.
    This is a safety net in case CASCADE doesn't work as expected.
    """
    # Delete all messages where the user is either sender or receiver
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()
    
    # Delete all notifications for this user
    Notification.objects.filter(user=instance).delete()
    
    # Delete message history where the user was the editor
    MessageHistory.objects.filter(edited_by=instance).delete()
    
    # For MessageHistory where the user was mentioned in the content
    # (This is optional and might be resource-intensive for large datasets)
    for history in MessageHistory.objects.filter(content__icontains=instance.username):
        history.delete()
