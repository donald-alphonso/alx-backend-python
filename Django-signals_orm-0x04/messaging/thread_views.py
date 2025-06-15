from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.http import require_http_methods, require_POST

from .models import Message
from .forms import ReplyForm

@login_required
def thread_detail(request, message_id):
    """
    Affiche un message et toutes ses réponses de manière hiérarchique.
    Utilise get_thread pour optimiser les requêtes.
    """
    message = get_object_or_404(Message.get_thread(message_id))
    form = ReplyForm()
    
    # Vérifier les permissions
    if request.user not in [message.sender, message.receiver]:
        messages.error(request, "You don't have permission to view this thread.")
        return redirect('inbox')
    
    return render(request, 'messaging/thread_detail.html', {
        'message': message,
        'form': form,
    })

@login_required
@require_http_methods(["GET", "POST"])
def reply_to_message(request, message_id):
    """
    Permet de répondre à un message existant.
    """
    parent_message = get_object_or_404(Message, pk=message_id)
    
    # Vérifier les permissions
    if request.user not in [parent_message.sender, parent_message.receiver]:
        messages.error(request, "You don't have permission to reply to this message.")
        return redirect('inbox')
    
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.sender = request.user
            reply.receiver = parent_message.sender if request.user == parent_message.receiver else parent_message.receiver
            reply.parent_message = parent_message
            reply.save()
            
            messages.success(request, 'Your reply has been sent.')
            return redirect('thread_detail', message_id=parent_message.id)
    else:
        form = ReplyForm(initial={
            'content': f"\n\n\n--- Original Message ---\n{parent_message.content}"
        })
    
    return render(request, 'messaging/reply.html', {
        'form': form,
        'parent_message': parent_message,
    })

def get_threaded_conversation(user1, user2):
    """
    Récupère toute la conversation entre deux utilisateurs sous forme d'arbres de messages.
    """
    # Récupérer tous les messages entre les deux utilisateurs
    messages = Message.objects.filter(
        (Q(sender=user1, receiver=user2) | Q(sender=user2, receiver=user1))
    ).select_related('sender', 'receiver').order_by('timestamp')
    
    # Construire l'arbre des conversations
    threads = []
    messages_dict = {}
    
    # Premier passage: créer des entrées pour tous les messages
    for msg in messages:
        msg.thread_replies = []
        messages_dict[msg.id] = msg
    
    # Deuxième passage: construire la hiérarchie
    for msg in messages:
        if msg.parent_message_id and msg.parent_message_id in messages_dict:
            parent = messages_dict[msg.parent_message_id]
            parent.thread_replies.append(msg)
        elif not msg.parent_message_id:
            threads.append(msg)
    
    return threads
