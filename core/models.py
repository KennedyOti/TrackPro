from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Todo(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    category = models.CharField(max_length=100, blank=True)
    reminder_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.title

    def is_overdue(self):
        if self.due_date and self.due_date < timezone.now():
            return True
        return False

    def reminder_due(self):
        if self.reminder_date and self.reminder_date <= timezone.now() and not self.completed:
            return True
        return False

    class Meta:
        ordering = ['-created_at']

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('reminder', 'Reminder'),
        ('due_soon', 'Due Soon'),
        ('overdue', 'Overdue'),
        ('completed', 'Completed'),
        ('system', 'System'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    sound_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    class Meta:
        ordering = ['-created_at']

class TimeEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE, null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)  # in seconds
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.todo.title if self.todo else 'General'} - {self.start_time}"

    def save(self, *args, **kwargs):
        if self.end_time and self.start_time:
            self.duration = self.end_time - self.start_time
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-start_time']

class UserProfile(models.Model):
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('auto', 'Auto'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, max_length=500)
    timezone = models.CharField(max_length=50, default='UTC')
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')

    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    sound_notifications = models.BooleanField(default=True)
    reminder_notifications = models.BooleanField(default=True)
    due_date_notifications = models.BooleanField(default=True)
    completed_task_notifications = models.BooleanField(default=False)

    # Dashboard preferences
    dashboard_layout = models.CharField(max_length=20, default='default')
    items_per_page = models.IntegerField(default=10)
    default_priority = models.CharField(max_length=10, default='medium')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
