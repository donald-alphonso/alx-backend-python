from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    """Serializer for soldiers - User data"""
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['user_id', 'username', 'password','first_name', 'last_name', 'email', 'phone_number', 'role', 'created_at']
        read_only_fields = ['user_id', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def get_full_name(self, obj):
        """Method to obtain the full name"""
        return f"{obj.first_name} {obj.last_name}".strip()
    
    def validate_email(self, value):
        """Method to validate email"""
        if User.objects.filter(email=value).exclude(user_id=self.instance.user_id if self.instance else None).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    def validate_password(self, value):
        """Method to validate password"""
        if 'password' in value and 'confirm_password' in value:
            if value['password'] != value['confirm_password']:
                raise serializers.ValidationError("Passwords do not match")
        return value

class MessageSerializer(serializers.ModelSerializer):
    """Serializer for messages - Communications"""
    sender = UserSerializer(read_only=True)
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    conversation_id = serializers.UUIDField(source='conversation.conversation_id', read_only=True)
    message_length = serializers.SerializerMethodField()
    is_recent = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'sender_username', 'conversation_id', 'message_body', 'sent_at', 'message_length', 'is_recent']
        read_only_fields = ['message_id', 'sender', 'sent_at']
    
    def get_message_length(self, obj):
        """Method to get the length of the message"""
        return len(obj.message_body)
    
    def get_is_recent(self, obj):
        """Method to check if the message is recent"""
        from django.utils import timezone
        from datetime import timedelta
        return obj.sent_at >= timezone.now() - timedelta(hours=24)
    
    def validate_message_body(self, value):
        """Method to validate message body"""
        if not value or not value.strip():
            raise serializers.validationError("Message body cannot be empty, soldier")
        
        if len(value) > 1000:
            raise serializers.validationError("Message body cannot be longer than 1000 characters, soldier")
        
        forbidden_words = ['spam', 'hack', 'virus']
        if any(word in value.lower() for word in forbidden_words):
            raise serializers.validationError("Message body contains forbidden words, soldier")
        
        return value.strip()

class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for conversations - Communication channels"""
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    participant_count = serializers.SerializerMethodField()
    latest_message = serializers.SerializerMethodField()
    has_recent_activity = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'participant_count', 'messages', 'latest_message', 'has_recent_activity', 'created_at']
        read_only_fields = ['conversation_id', 'created_at']
    
    def get_participant_count(self, obj):
        """Get the number of participants in the conversation"""
        return obj.participants.count()
    
    def get_latest_message(self, obj):
        """Get the latest message in the conversation"""
        latest = obj.messages.first()
        if latest:
            return {
                'message_body': latest.message_body,
                'sender': latest.sender.username,
                'sent_at': latest.sent_at
            }
        return None
    
    def get_has_recent_activity(self, obj):
        """Check if the conversation has recent activity"""
        from django.utils import timezone
        from datetime import timedelta
        
        latest_message = obj.messages.first()
        if latest_message:
            return latest_message.sent_at >= timezone.now() - timedelta(hours=24)
        return False
    
    def validate(self, data):
        """Validate the conversation data"""
        return data

class ConversationCreateSerializer(serializers.Serializer):
    """Serializer spécial pour créer des conversations"""
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=2,
        help_text="Liste des UUIDs des participants (minimum 2)"
    )
    
    def validate_participant_ids(self, value):
        """Validation des IDs des participants"""
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Impossible d'ajouter le même participant plusieurs fois!")
        
        # Vérifier que tous les utilisateurs existent
        existing_users = User.objects.filter(user_id__in=value)
        if existing_users.count() != len(value):
            existing_ids = set(str(user.user_id) for user in existing_users)
            missing_ids = set(str(uid) for uid in value) - existing_ids
            raise serializers.ValidationError(f"Utilisateurs introuvables: {missing_ids}")
        
        return value

class MessageCreateSerializer(serializers.Serializer):
    """Serializer spécial pour créer des messages"""
    conversation_id = serializers.UUIDField(help_text="UUID de la conversation")
    sender_id = serializers.UUIDField(help_text="UUID de l'expéditeur")
    message_body = serializers.CharField(max_length=1000, help_text="Contenu du message")
    
    def validate_message_body(self, value):
        """Validation du message"""
        if not value or not value.strip():
            raise serializers.ValidationError("Le message ne peut pas être vide!")
        
        if len(value) > 1000:
            raise serializers.ValidationError("Message trop long! Maximum 1000 caractères!")
        
        return value.strip()
    
    def validate_conversation_id(self, value):
        """Vérifier que la conversation existe"""
        if not Conversation.objects.filter(conversation_id=value).exists():
            raise serializers.ValidationError("Conversation introuvable!")
        return value
    
    def validate_sender_id(self, value):
        """Vérifier que l'expéditeur existe"""
        if not User.objects.filter(user_id=value).exists():
            raise serializers.ValidationError("Utilisateur expéditeur introuvable!")
        return value
    
    def validate(self, data):
        """Validation croisée - vérifier que l'expéditeur fait partie de la conversation"""
        try:
            conversation = Conversation.objects.get(conversation_id=data['conversation_id'])
            sender = User.objects.get(user_id=data['sender_id'])
            
            if sender not in conversation.participants.all():
                raise serializers.ValidationError("L'expéditeur ne fait pas partie de cette conversation!")
            
        except (Conversation.DoesNotExist, User.DoesNotExist):
            raise serializers.ValidationError("Conversation ou utilisateur introuvable!")
        
        return data