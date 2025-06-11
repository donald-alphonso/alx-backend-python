from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework_simplyjwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personnalisé pour l'authentification JWT
    Permet de se connecter avec email ou username
    """
    username_field = 'email'  # Utiliser l'email comme identifiant principal
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Modifier les champs requis
        self.fields['email'] = serializers.EmailField()
        self.fields['password'] = serializers.CharField()
        # Retirer le champ username par défaut
        del self.fields['username']
    
    def validate(self, attrs):
        """Validation personnalisée pour l'authentification"""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            # Chercher l'utilisateur par email
            try:
                user = User.objects.get(email=email)
                username = user.username
            except User.DoesNotExist:
                raise serializers.ValidationError('Aucun utilisateur trouvé avec cet email.')
            
            # Authentifier avec le username trouvé
            user = authenticate(username=username, password=password)
            
            if user:
                if not user.is_active:
                    raise serializers.ValidationError('Compte utilisateur désactivé.')
                
                # Utiliser le processus JWT standard
                attrs['username'] = username
                data = super().validate(attrs)
                
                # Ajouter des infos utilisateur au token
                data['user'] = {
                    'user_id': str(user.user_id),
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                }
                
                return data
            else:
                raise serializers.ValidationError('Email ou mot de passe incorrect.')
        else:
            raise serializers.ValidationError('Email et mot de passe requis.')

class CustomTokenObtainPairView(TokenObtainPairView):
    """Vue personnalisée pour l'obtention du token JWT"""
    serializer_class = CustomTokenObtainPairSerializer