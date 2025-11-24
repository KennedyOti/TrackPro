from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from core.models import Todo, Notification, UserProfile
import datetime


class Command(BaseCommand):
    help = 'Send notifications for due tasks, reminders, and overdue items'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what notifications would be sent without actually sending them',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        now = timezone.now()

        self.stdout.write(f'Starting notification check at {now}')

        # Check for reminders
        self.check_reminders(now, dry_run)

        # Check for due soon tasks (due within next hour)
        self.check_due_soon_tasks(now, dry_run)

        # Check for overdue tasks
        self.check_overdue_tasks(now, dry_run)

        # Check for completed tasks (if user wants notifications)
        self.check_completed_tasks(now, dry_run)

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No notifications were actually sent'))
        else:
            self.stdout.write(self.style.SUCCESS('Notification check completed'))

    def check_reminders(self, now, dry_run):
        """Check for tasks with reminders that should trigger now"""
        # Find todos with reminder_date that has passed and task is not completed
        reminders = Todo.objects.filter(
            reminder_date__lte=now,
            completed=False
        ).exclude(
            # Don't send if we already sent a reminder recently (within last hour)
            id__in=Notification.objects.filter(
                notification_type='reminder',
                created_at__gte=now - datetime.timedelta(hours=1)
            ).values_list('todo_id', flat=True)
        )

        for todo in reminders:
            user_profile = UserProfile.objects.filter(user=todo.user).first()
            if user_profile and user_profile.reminder_notifications:
                title = f"Reminder: {todo.title}"
                message = f"Don't forget to work on: {todo.title}"

                if not dry_run:
                    Notification.objects.create(
                        user=todo.user,
                        todo=todo,
                        notification_type='reminder',
                        title=title,
                        message=message,
                        sound_enabled=user_profile.sound_notifications
                    )

                self.stdout.write(f"Reminder notification for: {todo.title} (User: {todo.user.username})")

    def check_due_soon_tasks(self, now, dry_run):
        """Check for tasks due within the next hour"""
        due_soon_threshold = now + datetime.timedelta(hours=1)

        due_soon_tasks = Todo.objects.filter(
            due_date__lte=due_soon_threshold,
            due_date__gt=now,
            completed=False
        ).exclude(
            # Don't send if we already sent a due soon notification recently
            id__in=Notification.objects.filter(
                notification_type='due_soon',
                created_at__gte=now - datetime.timedelta(hours=2)
            ).values_list('todo_id', flat=True)
        )

        for todo in due_soon_tasks:
            user_profile = UserProfile.objects.filter(user=todo.user).first()
            if user_profile and user_profile.due_date_notifications:
                time_until_due = todo.due_date - now
                hours_until_due = int(time_until_due.total_seconds() / 3600)

                title = f"Due Soon: {todo.title}"
                message = f"Task due in {hours_until_due} hour{'s' if hours_until_due != 1 else ''}"

                if not dry_run:
                    Notification.objects.create(
                        user=todo.user,
                        todo=todo,
                        notification_type='due_soon',
                        title=title,
                        message=message,
                        sound_enabled=user_profile.sound_notifications
                    )

                self.stdout.write(f"Due soon notification for: {todo.title} (User: {todo.user.username})")

    def check_overdue_tasks(self, now, dry_run):
        """Check for overdue tasks"""
        overdue_tasks = Todo.objects.filter(
            due_date__lt=now,
            completed=False
        ).exclude(
            # Don't send overdue notifications more than once per day
            id__in=Notification.objects.filter(
                notification_type='overdue',
                created_at__gte=now - datetime.timedelta(days=1)
            ).values_list('todo_id', flat=True)
        )

        for todo in overdue_tasks:
            user_profile = UserProfile.objects.filter(user=todo.user).first()
            if user_profile and user_profile.due_date_notifications:
                overdue_time = now - todo.due_date
                days_overdue = overdue_time.days
                hours_overdue = int(overdue_time.total_seconds() / 3600) % 24

                title = f"Overdue: {todo.title}"
                if days_overdue > 0:
                    message = f"Task is {days_overdue} day{'s' if days_overdue != 1 else ''} overdue"
                else:
                    message = f"Task is {hours_overdue} hour{'s' if hours_overdue != 1 else ''} overdue"

                if not dry_run:
                    Notification.objects.create(
                        user=todo.user,
                        todo=todo,
                        notification_type='overdue',
                        title=title,
                        message=message,
                        sound_enabled=user_profile.sound_notifications
                    )

                self.stdout.write(f"Overdue notification for: {todo.title} (User: {todo.user.username})")

    def check_completed_tasks(self, now, dry_run):
        """Check for recently completed tasks"""
        # Only check tasks completed in the last hour
        recent_completions = Todo.objects.filter(
            completed=True,
            updated_at__gte=now - datetime.timedelta(hours=1)
        ).exclude(
            # Don't send if we already sent a completion notification
            id__in=Notification.objects.filter(
                notification_type='completed',
                created_at__gte=now - datetime.timedelta(hours=1)
            ).values_list('todo_id', flat=True)
        )

        for todo in recent_completions:
            user_profile = UserProfile.objects.filter(user=todo.user).first()
            if user_profile and user_profile.completed_task_notifications:
                title = f"Task Completed: {todo.title}"
                message = f"Great job! You completed: {todo.title}"

                if not dry_run:
                    Notification.objects.create(
                        user=todo.user,
                        todo=todo,
                        notification_type='completed',
                        title=title,
                        message=message,
                        sound_enabled=user_profile.sound_notifications
                    )

                self.stdout.write(f"Completion notification for: {todo.title} (User: {todo.user.username})")