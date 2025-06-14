from rest_framework import permissions
from .models import Conversation, Message

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for owner
        return obj.owner == request.user

class IsParticipantOrReadOnly(permissions.BasePermission):
    """
    Custom permission class to ensure only participants of a conversation
    can access, send, view, update and delete messages within that conversation.
    """
    def has_permission(self, request, view):
        """
        Check is user is authenticated before allowing any access
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user is participant of the conversation for object-level permissions
        """
        
        # Vérifier si l'utilisateur est participant à la conversation
        if isinstance(obj, Conversation):
            return obj.participants.filter(user_id=request.user.user_id).exists()
        
        # Pour les messages, vérifier si l'utilisateur est participant à la conversation
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
            
            # For need operations, check if user is participant
            return obj.conversation.participants.filter(user_id=request.user.user_id).exists()
        
        return False

class CanAccessOwnDataOnly(permissions.BasePermission):
    """
    General permission: users can only access their own data
    """
    def has_permission(self, request, view):
        # User must be authenticated
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Pour les messages : vérifier si l'utilisateur est participant à la conversation
        if isinstance(obj, Message):
            return obj.conversation.participants.filter(user_id=request.user.user_id).exists()
        
        # Pour les conversations : vérifier si l'utilisateur est participant
        if isinstance(obj, Conversation):
            return obj.participants.filter(user_id=request.user.user_id).exists()
        
        # Pour les autres objets, vérifier si l'utilisateur en est le propriétaire
        if hasattr(obj, 'user'):
            return obj.user.user_id == request.user.user_id
        
        return False
