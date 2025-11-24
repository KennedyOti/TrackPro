from django.contrib import admin
from .models import Todo, Notification

@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'priority', 'due_date', 'completed', 'created_at')
    list_filter = ('status', 'priority', 'completed', 'due_date', 'user')
    search_fields = ('title', 'description', 'category')
    ordering = ('-created_at',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at', 'user')
    search_fields = ('title', 'message', 'user__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
