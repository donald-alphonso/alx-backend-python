from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend

from .models import User, Conversation, Message
from .serializers import (
    ConversationSerializer, 
    MessageSerializer, 
    ConversationCreateSerializer,
    MessageCreateSerializer
)
from .permissions import IsParticipantOfConversation, IsMessageSender


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations - Communication channels management
    Provides CRUD operations for conversations between users
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    lookup_field = 'conversation_id'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['created_at']
    search_fields = ['participants__username']
    
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
        
        # Permission check is handled by IsParticipantOfConversation
        messages = conversation.messages.all()
        serializer = MessageSerializer(messages, many=True)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, conversation_id=None):
        """
        Add a new participant to an existing conversation
        """
        conversation = self.get_object()
        
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
    
    @action(detail=True, methods=['delete'])
    def remove_participant(self, request, conversation_id=None):
        """
        Remove a participant from the conversation
        """
        conversation = self.get_object()
        
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'User ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_to_remove = User.objects.get(user_id=user_id)
            
            # Prevent removing yourself if it would leave conversation empty
            if user_to_remove == request.user and conversation.participants.count() == 1:
                return Response(
                    {'error': 'Cannot remove yourself from conversation as the only participant'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            conversation.participants.remove(user_to_remove)
            
            return Response(
                {'message': f'User {user_to_remove.username} removed from conversation'}, 
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
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    lookup_field = 'message_id'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['sent_at', 'conversation']
    search_fields = ['message_body', 'sender__username']
    
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
    
    def get_permissions(self):
        """
        Instantiate and return the list of permissions required for this view.
        For update/delete operations, also check if user is the message sender
        """
        permission_classes = [IsAuthenticated, IsParticipantOfConversation]
        
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes.append(IsMessageSender)
        
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """
        Create a new message in a conversation
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        
        try:
            # Get conversation and verify user is participant
            conversation = Conversation.objects.get(
                conversation_id=validated_data['conversation_id']
            )
            
            # Check if user is participant (redundant but explicit)
            if not conversation.participants.filter(user_id=request.user.user_id).exists():
                return Response(
                    {'error': 'You are not a participant in this conversation'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Create the message with current user as sender
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                message_body=validated_data['message_body']
            )
            
            # Serialize response
            response_serializer = MessageSerializer(message)
            
            return Response(
                response_serializer.data, 
                status=status.HTTP_201_CREATED
            )
            
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'}, 
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
        
        # Permission check is handled by IsParticipantOfConversation
        # Placeholder response (you could add a 'read_by' field to Message model)
        return Response(
            {'message': 'Message marked as read'}, 
            status=status.HTTP_200_OK
        )
    
    def destroy(self, request, *args, **kwargs):
        """
        Override delete to only allow message sender to delete their own messages
        Permissions is enforced by IsMessageSender is get_permissions()
        """
        return super().destroy(request, *args, **kwargs)