from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Message, Notification

User = get_user_model()

class MessageModelTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@example.com',
            password='testpass123'
        )
        self.receiver = User.objects.create_user(
            username='receiver',
            email='receiver@example.com',
            password='testpass123'
        )
    
    def test_message_creation(self):
        """Test that a message can be created and has the correct string representation."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content='Hello, this is a test message.'
        )
        self.assertEqual(str(message), f'Message from {self.sender} to {self.receiver} at {message.timestamp}')


class NotificationSignalTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@example.com',
            password='testpass123'
        )
        self.receiver = User.objects.create_user(
            username='receiver',
            email='receiver@example.com',
            password='testpass123'
        )
    
    def test_notification_created_on_message_save(self):
        """Test that a notification is created when a new message is saved."""
        # Create a new message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content='Hello, this is a test message.'
        )
        
        # Check that a notification was created
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.receiver)
        self.assertEqual(notification.message, message)
        self.assertFalse(notification.is_read)
    
    def test_notification_not_created_on_message_update(self):
        """Test that a notification is not created when an existing message is updated."""
        # Create a message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content='Hello, this is a test message.'
        )
        
        # Clear notifications
        Notification.objects.all().delete()
        
        # Update the message
        message.content = 'Updated content'
        message.save()
        
        # Check that no new notification was created
        self.assertEqual(Notification.objects.count(), 0)
