from rest_framework import permissions
from .models import Conversation, Message

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée pour permettre seulement aux propriétaires
    d'un objet de le modifier.
    """
    def has_object_permission(self, request, view, obj):
        # Permissions de lecture pour tous les utilisateurs authentifiés
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permissions d'écriture seulement pour le propriétaire
        return obj.owner == request.user

class IsParticipantOrReadOnly(permissions.BasePermission):
    """
    Permission pour les conversations : seuls les participants peuvent voir/modifier
    """
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Conversation):
            # Vérifier si l'utilisateur est participant à la conversation
            return obj.participants.filter(user_id=request.user.user_id).exists()
        
        if isinstance(obj, Message):
            # Pour les messages, vérifier si l'utilisateur est participant à la conversation
            return obj.conversation.participants.filter(user_id=request.user.user_id).exists()
        
        return False

class IsMessageSender(permissions.BasePermission):
    """
    Permission pour les messages : seul l'expéditeur peut modifier son message
    """
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Message):
            # Seul l'expéditeur peut modifier/supprimer son message
            if request.method in ['PUT', 'PATCH', 'DELETE']:
                return obj.sender.user_id == request.user.user_id
            
            # Pour la lecture, vérifier si c'est un participant
            return obj.conversation.participants.filter(user_id=request.user.user_id).exists()
        
        return False

class CanAccessOwnDataOnly(permissions.BasePermission):
    """
    Permission générale : les utilisateurs ne peuvent accéder qu'à leurs propres données
    """
    def has_permission(self, request, view):
        # L'utilisateur doit être authentifié
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
