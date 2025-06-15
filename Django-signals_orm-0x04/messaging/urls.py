from django.urls import path
from . import views
from .thread_views import thread_detail, reply_to_message
from django.contrib.auth.decorators import login_required

app_name = 'messaging'

urlpatterns = [
    # User account
    path('user/delete/', views.delete_user, name='delete_user'),
    
    # Inbox and conversations
    path('inbox/', login_required(views.inbox), name='inbox'),
    path('conversation/<int:user_id>/', login_required(views.conversation), name='conversation'),
    path('send/<int:user_id>/', login_required(views.send_message), name='send_message'),
    
    # Threaded conversations
    path('thread/<int:message_id>/', login_required(thread_detail), name='thread_detail'),
    path('thread/<int:message_id>/reply/', login_required(reply_to_message), name='reply_to_message'),
]
