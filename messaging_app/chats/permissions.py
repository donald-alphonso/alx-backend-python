from rest_framework import permissions
from .models import Conversation, Message


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission class to ensure only participants of a conversation
    can access, send, view, update and delete messages within that conversation.
    """
    
    def has_permission(self, request, view):
        """
        Check if user is authenticated before allowing any access
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user is participant of the conversation for object-level permissions
        """
        # Handle Conversation objects
        if isinstance(obj, Conversation):
            return obj.participants.filter(user_id=request.user.user_id).exists()
        
        # Handle Message objects - check if user is participant of the message's conversation
        if isinstance(obj, Message):
            return obj.conversation.participants.filter(user_id=request.user.user_id).exists()
        
        return False


class IsMessageSender(permissions.BasePermission):
    """
    Permission to allow only message sender to modify or delete their own messages
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Only allow sender to modify/delete their own messages
        """
        if isinstance(obj, Message):
            # For destructive operations, only sender can perform them
            if request.method in ['PUT', 'PATCH', 'DELETE']:
                return obj.sender.user_id == request.user.user_id
            
            # For read operations, check if user is participant
            return obj.conversation.participants.filter(user_id=request.user.user_id).exists()
        
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for owner
        return obj.owner == request.user


class CanAccessOwnDataOnly(permissions.BasePermission):
    """
    General permission: users can only access their own data
    """
    
    def has_permission(self, request, view):
        # User must be authenticated
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # For messages: check if user is participant in conversation
        if isinstance(obj, Message):
            return obj.conversation.participants.filter(user_id=request.user.user_id).exists()
        
        # For conversations: check if user is participant
        if isinstance(obj, Conversation):
            return obj.participants.filter(user_id=request.user.user_id).exists()
        
        # For other objects, check if user is the owner
        if hasattr(obj, 'user'):
            return obj.user.user_id == request.user.user_id
        
        return False