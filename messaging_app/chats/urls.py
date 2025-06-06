from django.urls import path, include
from rest_framework import routers
from rest_framework_nested import routers as nested_routers
from .views import ConversationViewSet, MessageViewSet

# Create router and register viewsets
router = routers.DefaultRouter()

# Register viewsets with the router
# This will automatically create:
# - conversations/ (GET, POST)
# - conversations/{id}/ (GET, PUT, PATCH, DELETE)
# - messages/ (GET, POST) 
# - messages/{id}/ (GET, PUT, PATCH, DELETE)
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

conversations_router = nested_routers.NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversations_router.urls)),
]