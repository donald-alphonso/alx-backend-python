import django_filters
from django.db.models import Q
from django_filters import rest_framework as filters
from .models import Message, Conversation, User


class MessageFilter(django_filters.FilterSet):
    """
    Filter class for Message model to enable filtering by various criteria
    """
    # Date range filtering
    sent_after = django_filters.DateTimeFilter(
        field_name='sent_at', 
        lookup_expr='gte',
        help_text='Filter messages sent after this date (YYYY-MM-DD HH:MM:SS)'
    )
    sent_before = django_filters.DateTimeFilter(
        field_name='sent_at', 
        lookup_expr='lte',
        help_text='Filter messages sent before this date (YYYY-MM-DD HH:MM:SS)'
    )
    
    # Date range filtering (date only, no time)
    sent_date = django_filters.DateFilter(
        field_name='sent_at__date',
        help_text='Filter messages sent on specific date (YYYY-MM-DD)'
    )
    sent_date_after = django_filters.DateFilter(
        field_name='sent_at__date',
        lookup_expr='gte',
        help_text='Filter messages sent on or after this date (YYYY-MM-DD)'
    )
    sent_date_before = django_filters.DateFilter(
        field_name='sent_at__date',
        lookup_expr='lte',
        help_text='Filter messages sent on or before this date (YYYY-MM-DD)'
    )
    
    # Sender filtering
    sender = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name='sender',
        to_field_name='user_id',
        help_text='Filter messages by sender user ID'
    )
    sender_username = django_filters.CharFilter(
        field_name='sender__username',
        lookup_expr='icontains',
        help_text='Filter messages by sender username (case insensitive)'
    )
    
    # Conversation filtering
    conversation = django_filters.ModelChoiceFilter(
        queryset=Conversation.objects.all(),
        field_name='conversation',
        to_field_name='conversation_id',
        help_text='Filter messages by conversation ID'
    )
    
    # Message content filtering
    message_body = django_filters.CharFilter(
        field_name='message_body',
        lookup_expr='icontains',
        help_text='Search in message content (case insensitive)'
    )
    
    # Boolean filters
    has_content = django_filters.BooleanFilter(
        method='filter_has_content',
        help_text='Filter messages that have content (true) or are empty (false)'
    )
    
    class Meta:
        model = Message
        fields = {
            'sent_at': ['exact', 'gte', 'lte'],
            'sender': ['exact'],
            'conversation': ['exact'],
            'message_body': ['icontains'],
        }
    
    def filter_has_content(self, queryset, name, value):
        """
        Custom filter method to check if message has content
        """
        if value:
            return queryset.exclude(message_body__exact='')
        return queryset.filter(message_body__exact='')


class ConversationFilter(django_filters.FilterSet):
    """
    Filter class for Conversation model
    """
    # Date filtering
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text='Filter conversations created after this date'
    )
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text='Filter conversations created before this date'
    )
    
    # Participant filtering
    participant = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name='participants',
        to_field_name='user_id',
        help_text='Filter conversations by participant user ID'
    )
    participant_username = django_filters.CharFilter(
        method='filter_by_participant_username',
        help_text='Filter conversations by participant username'
    )
    
    # Multiple participants filtering
    participants_count = django_filters.NumberFilter(
        method='filter_by_participants_count',
        help_text='Filter conversations by number of participants'
    )
    participants_count_gte = django_filters.NumberFilter(
        method='filter_by_participants_count_gte',
        help_text='Filter conversations with at least this many participants'
    )
    participants_count_lte = django_filters.NumberFilter(
        method='filter_by_participants_count_lte',
        help_text='Filter conversations with at most this many participants'
    )
    
    # Recent activity filtering
    has_recent_messages = django_filters.BooleanFilter(
        method='filter_has_recent_messages',
        help_text='Filter conversations with messages in last 24 hours'
    )
    
    class Meta:
        model = Conversation
        fields = {
            'created_at': ['exact', 'gte', 'lte'],
            'participants': ['exact'],
        }
    
    def filter_by_participant_username(self, queryset, name, value):
        """
        Filter conversations by participant username
        """
        return queryset.filter(participants__username__icontains=value)
    
    def filter_by_participants_count(self, queryset, name, value):
        """
        Filter conversations by exact number of participants
        """
        return queryset.annotate(
            participant_count=django_filters.Count('participants')
        ).filter(participant_count=value)
    
    def filter_by_participants_count_gte(self, queryset, name, value):
        """
        Filter conversations with at least specified number of participants
        """
        return queryset.annotate(
            participant_count=django_filters.Count('participants')
        ).filter(participant_count__gte=value)
    
    def filter_by_participants_count_lte(self, queryset, name, value):
        """
        Filter conversations with at most specified number of participants
        """
        return queryset.annotate(
            participant_count=django_filters.Count('participants')
        ).filter(participant_count__lte=value)
    
    def filter_has_recent_messages(self, queryset, name, value):
        """
        Filter conversations that have messages in the last 24 hours
        """
        from django.utils import timezone
        from datetime import timedelta
        
        if value:
            recent_time = timezone.now() - timedelta(hours=24)
            return queryset.filter(messages__sent_at__gte=recent_time).distinct()
        else:
            recent_time = timezone.now() - timedelta(hours=24)
            return queryset.exclude(messages__sent_at__gte=recent_time)


class UserFilter(django_filters.FilterSet):
    """
    Filter class for User model
    """
    # Name filtering
    first_name = django_filters.CharFilter(
        field_name='first_name',
        lookup_expr='icontains',
        help_text='Filter users by first name (case insensitive)'
    )
    last_name = django_filters.CharFilter(
        field_name='last_name',
        lookup_expr='icontains',
        help_text='Filter users by last name (case insensitive)'
    )
    full_name = django_filters.CharFilter(
        method='filter_full_name',
        help_text='Search in full name (first name + last name)'
    )
    
    # Role filtering
    role = django_filters.ChoiceFilter(
        choices=[('guest', 'Guest'), ('host', 'Host'), ('admin', 'Admin')],
        help_text='Filter users by role'
    )
    
    # Registration date filtering
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text='Filter users created after this date'
    )
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text='Filter users created before this date'
    )
    
    class Meta:
        model = User
        fields = {
            'username': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'role': ['exact'],
            'created_at': ['exact', 'gte', 'lte'],
        }
    
    def filter_full_name(self, queryset, name, value):
        """
        Filter users by full name (combination of first_name and last_name)
        """
        return queryset.filter(
            Q(first_name__icontains=value) | 
            Q(last_name__icontains=value) |
            Q(first_name__icontains=value.split()[0] if ' ' in value else '') |
            Q(last_name__icontains=value.split()[-1] if ' ' in value else '')
        )