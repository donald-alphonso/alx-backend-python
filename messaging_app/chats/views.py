from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import User, Conversation, Message
from .serializers import (
    ConversationSerializer, 
    MessageSerializer, 
    ConversationCreateSerializer,
    MessageCreateSerializer
)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations - Communication channels management
    Provides CRUD operations for conversations between users
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'conversation_id'
    
    def get_queryset(self):
        """
        Filter conversations to show only those where current user is participant
        """
        user = self.request.user
        return Conversation.objects.filter(participants=user).prefetch_related(
            'participants', 'messages'
        )
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'create':
            return ConversationCreateSerializer
        return ConversationSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new conversation with specified participants
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        participant_ids = serializer.validated_data['participant_ids']
        
        # Create conversation with transaction to ensure data integrity
        with transaction.atomic():
            conversation = Conversation.objects.create()
            
            # Add participants to the conversation
            participants = User.objects.filter(user_id__in=participant_ids)
            conversation.participants.set(participants)
            
            # Serialize the created conversation for response
            response_serializer = ConversationSerializer(conversation)
            
            return Response(
                response_serializer.data, 
                status=status.HTTP_201_CREATED
            )
    
    @action(detail=True, methods=['get'])
    def messages(self, request, conversation_id=None):
        """
        Custom action to retrieve all messages for a specific conversation
        """
        conversation = self.get_object()
        
        # Check if current user is participant in this conversation
        if request.user not in conversation.participants.all():
            return Response(
                {'error': 'You are not authorized to view this conversation'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        messages = conversation.messages.all()
        serializer = MessageSerializer(messages, many=True)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, conversation_id=None):
        """
        Add a new participant to an existing conversation
        """
        conversation = self.get_object()
        
        # Check if current user is participant (authorization)
        if request.user not in conversation.participants.all():
            return Response(
                {'error': 'You are not authorized to modify this conversation'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'User ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_to_add = User.objects.get(user_id=user_id)
            conversation.participants.add(user_to_add)
            
            return Response(
                {'message': f'User {user_to_add.username} added to conversation'}, 
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages - Communication content management
    Handles message creation, retrieval, and management within conversations
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'message_id'
    
    def get_queryset(self):
        """
        Filter messages to show only those from conversations where user participates
        """
        user = self.request.user
        return Message.objects.filter(
            conversation__participants=user
        ).select_related('sender', 'conversation')
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new message in a conversation
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        
        try:
            # Get conversation and sender from validated data
            conversation = Conversation.objects.get(
                conversation_id=validated_data['conversation_id']
            )
            sender = User.objects.get(
                user_id=validated_data['sender_id']
            )
            
            # Verify sender is authenticated user (security check)
            if sender != request.user:
                return Response(
                    {'error': 'You can only send messages as yourself'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Create the message
            message = Message.objects.create(
                conversation=conversation,
                sender=sender,
                message_body=validated_data['message_body']
            )
            
            # Serialize response
            response_serializer = MessageSerializer(message)
            
            return Response(
                response_serializer.data, 
                status=status.HTTP_201_CREATED
            )
            
        except (Conversation.DoesNotExist, User.DoesNotExist) as e:
            return Response(
                {'error': 'Conversation or User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Custom action to get recent messages (last 24 hours)
        """
        from django.utils import timezone
        from datetime import timedelta
        
        # Get messages from last 24 hours
        recent_time = timezone.now() - timedelta(hours=24)
        recent_messages = self.get_queryset().filter(sent_at__gte=recent_time)
        
        serializer = self.get_serializer(recent_messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def mark_as_read(self, request, message_id=None):
        """
        Custom action to mark a message as read (placeholder for future implementation)
        """
        message = self.get_object()
        
        # Check if user is participant in the conversation
        if request.user not in message.conversation.participants.all():
            return Response(
                {'error': 'You are not authorized to access this message'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Placeholder response (you could add a 'read_by' field to Message model)
        return Response(
            {'message': 'Message marked as read'}, 
            status=status.HTTP_200_OK
        )
    
    def destroy(self, request, *args, **kwargs):
        """
        Override delete to only allow message sender to delete their own messages
        """
        message = self.get_object()
        
        # Only sender can delete their message
        if message.sender != request.user:
            return Response(
                {'error': 'You can only delete your own messages'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().destroy(request, *args, **kwargs)
