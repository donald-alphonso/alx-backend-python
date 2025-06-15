from django.db import models
from django.db.models import Q


class UnreadMessagesManager(models.Manager):
    """
    Gestionnaire personnalisé pour les messages non lus.
    """
    def unread_for_user(self, user):
        """
        Retourne les messages non lus pour un utilisateur donné.
        Utilise only() pour optimiser les requêtes en ne récupérant que les champs nécessaires.
        """
        return self.get_queryset().filter(
            receiver=user,
            is_read=False
        ).select_related('sender').only(
            'id', 'content', 'timestamp', 'is_read', 'is_edited',
            'sender__id', 'sender__username', 'sender__email'
        ).order_by('-timestamp')
    
    def unread_count_for_user(self, user):
        """
        Retourne le nombre de messages non lus pour un utilisateur.
        Utilise values() et count() pour une requête plus légère.
        """
        return self.get_queryset().filter(
            receiver=user,
            is_read=False
        ).values('id').count()
    
    def mark_as_read(self, message_ids, user):
        """
        Marque les messages comme lus.
        Utilise update() pour une mise à jour en masse plus efficace.
        """
        return self.get_queryset().filter(
            id__in=message_ids,
            receiver=user,
            is_read=False
        ).update(is_read=True)
