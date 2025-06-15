from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.cache import cache_page
from django.db.models import Q
from .models import Message, Notification
from .forms import DeleteAccountForm

User = get_user_model()

@login_required
@require_http_methods(["GET", "POST"])
def delete_user(request):
    """
    View to handle user account deletion with confirmation.
    The actual user deletion will be handled by the post_delete signal.
    """
    user = request.user
    
    if request.method == 'POST':
        form = DeleteAccountForm(request.POST, user=user)
        if form.is_valid():
            try:
                # This will trigger the post_delete signal
                username = user.username
                user.delete()
                # Log the user out after deletion
                logout(request)
                messages.success(request, f'Account {username} has been successfully deleted.')
                return redirect('home')  # Replace 'home' with your actual home URL name
            except Exception as e:
                messages.error(request, f'An error occurred while deleting your account: {str(e)}')
                return redirect('profile')
    else:
        form = DeleteAccountForm()
    
    return render(request, 'messaging/delete_account_confirm.html', {'form': form})


@login_required
def inbox(request):
    """
    Affiche la boîte de réception de l'utilisateur avec les conversations.
    Utilise le gestionnaire personnalisé pour les messages non lus.
    """
    # Utilisation du gestionnaire personnalisé pour les messages non lus
    unread_messages = Message.unread.unread_for_user(request.user)
    
    # Récupérer les derniers messages de chaque conversation
    # Utilisation de select_related pour optimiser les requêtes
    latest_messages = Message.objects.filter(
        Q(receiver=request.user) | Q(sender=request.user)
    ).select_related('sender', 'receiver').order_by('sender', 'receiver', '-timestamp').distinct('sender', 'receiver')
    
    # Créer une liste unique de conversations
    conversations = []
    
    # Utilisation d'un ensemble pour éviter les doublons
    seen_conversations = set()
    
    for msg in latest_messages:
        # Déterminer l'autre utilisateur de la conversation
        if msg.sender == request.user:
            other_user = msg.receiver
        else:
            other_user = msg.sender
        
        # Vérifier si on a déjà traité cette conversation
        if other_user.id in seen_conversations:
            continue
            
        seen_conversations.add(other_user.id)
        
        # Utiliser le gestionnaire personnalisé pour le décompte des non lus
        unread_count = Message.unread.unread_count_for_user(request.user)
        
        conversations.append({
            'other_user': other_user,
            'last_message': msg,
            'unread_count': unread_count
        })
    
    # Trier les conversations par date du dernier message
    conversations.sort(key=lambda x: x['last_message'].timestamp, reverse=True)
    
    # Marquer les messages comme lus si nécessaire
    if request.method == 'POST' and 'mark_all_read' in request.POST:
        unread_ids = list(unread_messages.values_list('id', flat=True))
        if unread_ids:
            Message.unread_objects.mark_as_read(unread_ids, request.user)
            messages.success(request, "All messages marked as read.")
            return redirect('messaging:inbox')
    
    return render(request, 'messaging/inbox.html', {
        'conversations': conversations,
        'unread_count': len(unread_messages),
    })


@login_required
@cache_page(60)  # Cache la vue pendant 60 secondes
def conversation(request, user_id):
    """
    Affiche la conversation avec un utilisateur spécifique.
    Utilise le gestionnaire personnalisé et optimise les requêtes.
    La vue est mise en cache pendant 60 secondes.
    """
    other_user = get_object_or_404(get_user_model(), pk=user_id)
    
    # Récupérer les messages non lus avec le gestionnaire personnalisé
    unread_messages = Message.unread.unread_for_user(request.user).filter(
        sender=other_user
    )
    
    # Récupérer les IDs des messages non lus
    unread_ids = list(unread_messages.values_list('id', flat=True))
    
    # Marquer les messages comme lus en une seule requête
    if unread_ids:
        Message.unread.mark_as_read(unread_ids, request.user)
    
    # Récupérer la conversation avec optimisation des requêtes
    # Utilisation de select_related pour les relations et only() pour les champs nécessaires
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).select_related(
        'sender', 'receiver'
    ).only(
        'id', 'content', 'timestamp', 'is_read', 'is_edited',
        'sender__id', 'sender__username', 'sender__email',
        'receiver__id', 'receiver__username'
    ).order_by('timestamp')
    
    # Si c'est une requête AJAX, renvoyer uniquement les messages
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'messaging/_messages.html', {
            'messages': messages,
            'current_user': request.user
        })
    
    # Récupérer le nombre de messages non lus pour l'affichage
    unread_count = Message.unread.unread_count_for_user(request.user)
    
    return render(request, 'messaging/conversation.html', {
        'other_user': other_user,
        'messages': messages,
        'unread_count': unread_count
    })


@login_required
@require_http_methods(["POST"])
def send_message(request, user_id):
    """
    Envoie un message à un utilisateur.
    """
    receiver = get_object_or_404(get_user_model(), pk=user_id)
    content = request.POST.get('content', '').strip()
    
    if not content:
        messages.error(request, "Message cannot be empty.")
    else:
        # Créer le message
        message = Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content
        )
        
        # Créer une notification pour le destinataire
        Notification.objects.create(
            user=receiver,
            message=message,
            is_read=False
        )
        
        messages.success(request, "Message sent successfully.")
    
    return redirect('messaging:conversation', user_id=user_id)
