from django.contrib import admin
from django.utils.html import format_html
from .models import Message, Notification, MessageHistory

class MessageHistoryInline(admin.TabularInline):
    model = MessageHistory
    extra = 0
    readonly_fields = ('edited_at', 'edited_by', 'content')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ('original_message', 'edited_by', 'edited_at')
    list_filter = ('edited_at',)
    search_fields = ('original_message__content', 'edited_by__username')
    readonly_fields = ('original_message', 'content', 'edited_at', 'edited_by')
    date_hierarchy = 'edited_at'
    
    def has_add_permission(self, request):
        return False


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    inlines = [MessageHistoryInline]
    list_display = ('sender', 'receiver', 'timestamp', 'is_read', 'is_edited', 'last_edited')
    list_filter = ('is_read', 'is_edited', 'timestamp')
    search_fields = ('content', 'sender__username', 'receiver__username')
    date_hierarchy = 'timestamp'
    readonly_fields = ('is_edited', 'last_edited')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message__content')
    date_hierarchy = 'created_at'
