from .models import Todo, Notification
from django.utils import timezone

def notifications(request):
    if request.user.is_authenticated:
        # Get unread notifications
        notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).order_by('-created_at')[:10]  # Show top 10 notifications

        return {'notifications': notifications}
    return {'notifications': []}

def reminders(request):
    if request.user.is_authenticated:
        reminders = Todo.objects.filter(
            user=request.user,
            reminder_date__lte=timezone.now(),
            completed=False
        ).order_by('reminder_date')[:5]  # Show top 5 reminders
        return {'reminders': reminders}
    return {'reminders': []}