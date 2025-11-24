from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Count, Sum, Q
from .forms import UserRegistrationForm, UserProfileForm, TimeEntryForm
from .models import Todo, Notification, TimeEntry, UserProfile
def landing(request):
    return render(request, 'core/landing.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'core/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

@login_required
def todo_list(request):
    todos = Todo.objects.filter(user=request.user).order_by('-created_at')

    # Calculate stats
    completed_count = todos.filter(completed=True).count()
    pending_count = todos.filter(status='pending').count()
    overdue_count = todos.filter(
        due_date__lt=timezone.now(),
        completed=False
    ).count()

    context = {
        'todos': todos,
        'completed_count': completed_count,
        'pending_count': pending_count,
        'overdue_count': overdue_count,
    }

    return render(request, 'core/todo_list.html', context)

@login_required
def todo_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        due_date = request.POST.get('due_date')
        priority = request.POST.get('priority')
        category = request.POST.get('category')
        reminder_date = request.POST.get('reminder_date')
        Todo.objects.create(
            user=request.user,
            title=title,
            description=description,
            due_date=due_date if due_date else None,
            priority=priority,
            category=category,
            reminder_date=reminder_date if reminder_date else None,
        )
        messages.success(request, 'Todo created successfully!')
        return redirect('todo_list')
    return render(request, 'core/todo_form.html')

@login_required
def todo_update(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    if request.method == 'POST':
        # Handle AJAX status update
        if request.POST.get('status') and not request.POST.get('title'):
            todo.status = request.POST.get('status')
            todo.completed = request.POST.get('status') == 'completed'
            todo.updated_at = timezone.now()
            todo.save()

            # Return JSON response for AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'status': todo.status,
                    'completed': todo.completed
                })

            messages.success(request, f'Task status updated to {todo.get_status_display()}!')
            return redirect('todo_list')

        # Handle full form update
        todo.title = request.POST.get('title')
        todo.description = request.POST.get('description')
        due_date = request.POST.get('due_date')
        todo.due_date = due_date if due_date else None
        todo.priority = request.POST.get('priority')
        todo.category = request.POST.get('category')
        reminder_date = request.POST.get('reminder_date')
        todo.reminder_date = reminder_date if reminder_date else None
        todo.status = request.POST.get('status')
        todo.completed = 'completed' in request.POST.get('status', '')
        todo.save()
        messages.success(request, 'Todo updated successfully!')
        return redirect('todo_list')
    return render(request, 'core/todo_form.html', {'todo': todo})

@login_required
def todo_delete(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        messages.success(request, 'Todo deleted successfully!')
        return redirect('todo_list')
    return render(request, 'core/todo_confirm_delete.html', {'todo': todo})

@login_required
def calendar_view(request):
    todos = Todo.objects.filter(user=request.user, due_date__isnull=False)
    return render(request, 'core/calendar.html', {'todos': todos})

@login_required
def dashboard(request):
    # Get statistics
    user = request.user
    now = timezone.now()

    # Basic statistics
    total_tasks = Todo.objects.filter(user=user).count()
    pending_tasks = Todo.objects.filter(user=user, status='pending').count()
    in_progress_tasks = Todo.objects.filter(user=user, status='in_progress').count()
    completed_tasks = Todo.objects.filter(user=user, status='completed').count()

    # Priority statistics
    high_priority = Todo.objects.filter(user=user, priority='high', completed=False).count()
    medium_priority = Todo.objects.filter(user=user, priority='medium', completed=False).count()
    low_priority = Todo.objects.filter(user=user, priority='low', completed=False).count()

    # Due date statistics
    overdue_tasks = Todo.objects.filter(
        user=user,
        due_date__lt=now,
        completed=False
    ).count()

    due_today = Todo.objects.filter(
        user=user,
        due_date__date=now.date(),
        completed=False
    ).count()

    due_this_week = Todo.objects.filter(
        user=user,
        due_date__date__range=[now.date(), now.date() + timezone.timedelta(days=7)],
        completed=False
    ).exclude(due_date__date=now.date()).count()

    # Recent tasks
    recent_tasks = Todo.objects.filter(user=user).order_by('-created_at')[:5]

    # Productivity stats (completed this week)
    week_start = now - timezone.timedelta(days=now.weekday())
    completed_this_week = Todo.objects.filter(
        user=user,
        completed=True,
        created_at__gte=week_start
    ).count()

    context = {
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
        'high_priority': high_priority,
        'medium_priority': medium_priority,
        'low_priority': low_priority,
        'overdue_tasks': overdue_tasks,
        'due_today': due_today,
        'due_this_week': due_this_week,
        'recent_tasks': recent_tasks,
        'completed_this_week': completed_this_week,
    }

    return render(request, 'core/dashboard.html', context)

@login_required
def reports_view(request):
    user = request.user
    now = timezone.now()

    # Task Analysis
    total_tasks = Todo.objects.filter(user=user).count()
    completed_tasks = Todo.objects.filter(user=user, completed=True).count()
    pending_tasks = Todo.objects.filter(user=user, status='pending').count()
    in_progress_tasks = Todo.objects.filter(user=user, status='in_progress').count()

    # Priority Analysis
    high_priority = Todo.objects.filter(user=user, priority='high').count()
    medium_priority = Todo.objects.filter(user=user, priority='medium').count()
    low_priority = Todo.objects.filter(user=user, priority='low').count()

    # Completion Rate
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    # Time Tracking Analysis
    total_time_entries = TimeEntry.objects.filter(user=user).count()
    total_time_spent = TimeEntry.objects.filter(user=user).aggregate(
        total=Sum('duration')
    )['total'] or timezone.timedelta(0)

    # Productivity Analysis (last 30 days)
    thirty_days_ago = now - timezone.timedelta(days=30)
    tasks_last_30_days = Todo.objects.filter(
        user=user,
        created_at__gte=thirty_days_ago
    ).count()

    completed_last_30_days = Todo.objects.filter(
        user=user,
        completed=True,
        updated_at__gte=thirty_days_ago
    ).count()

    # Category Analysis
    category_stats = Todo.objects.filter(user=user).values('category').annotate(
        total=Count('id'),
        completed=Count('id', filter=Q(completed=True))
    ).order_by('-total')

    # Monthly Progress (last 6 months)
    monthly_data = []
    for i in range(5, -1, -1):
        month_start = (now - timezone.timedelta(days=30*i)).replace(day=1, hour=0, minute=0, second=0)
        month_end = (month_start + timezone.timedelta(days=32)).replace(day=1) - timezone.timedelta(seconds=1)

        month_completed = Todo.objects.filter(
            user=user,
            completed=True,
            updated_at__range=(month_start, month_end)
        ).count()

        monthly_data.append({
            'month': month_start.strftime('%B %Y'),
            'completed': month_completed
        })

    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'high_priority': high_priority,
        'medium_priority': medium_priority,
        'low_priority': low_priority,
        'completion_rate': round(completion_rate, 1),
        'total_time_entries': total_time_entries,
        'total_time_spent': total_time_spent,
        'tasks_last_30_days': tasks_last_30_days,
        'completed_last_30_days': completed_last_30_days,
        'category_stats': category_stats,
        'monthly_data': monthly_data,
    }

    return render(request, 'core/reports_simple.html', context)

@login_required
def settings_view(request):
    user = request.user

    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully!')
            return redirect('settings')
    else:
        form = UserProfileForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,
    }

    return render(request, 'core/settings.html', context)

@login_required
def time_tracking_view(request):
    user = request.user

    if request.method == 'POST':
        form = TimeEntryForm(request.POST, user=user)
        if form.is_valid():
            time_entry = form.save(commit=False)
            time_entry.user = user
            time_entry.save()
            messages.success(request, 'Time entry added successfully!')
            return redirect('time_tracking')
    else:
        form = TimeEntryForm(user=user)

    # Get time entries
    time_entries = TimeEntry.objects.filter(user=user).order_by('-start_time')

    # Active time entry
    active_entry = TimeEntry.objects.filter(user=user, is_active=True).first()

    # Today's time summary
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_entries = TimeEntry.objects.filter(
        user=user,
        start_time__gte=today_start
    )

    today_total = sum((entry.duration.total_seconds() for entry in today_entries if entry.duration), 0)

    # Get incomplete todos for quick actions
    incomplete_todos = Todo.objects.filter(user=user, completed=False)[:5]

    context = {
        'form': form,
        'time_entries': time_entries,
        'active_entry': active_entry,
        'today_total': today_total,
        'incomplete_todos': incomplete_todos,
    }

    return render(request, 'core/time_tracking.html', context)

# API Views
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View

class NotificationsAPIView(View):
    def get(self, request):
        user = request.user
        notifications = Notification.objects.filter(user=user, is_read=False)[:10]

        data = []
        for notification in notifications:
            data.append({
                'id': notification.id,
                'type': notification.notification_type,
                'title': notification.title,
                'message': notification.message,
                'created_at': notification.created_at.isoformat(),
                'sound_enabled': notification.sound_enabled,
            })

        return JsonResponse({'notifications': data})

    @method_decorator(csrf_exempt)
    def post(self, request):
        user = request.user
        notification_id = request.POST.get('notification_id')

        if notification_id:
            try:
                notification = Notification.objects.get(id=notification_id, user=user)
                notification.is_read = True
                notification.save()
                return JsonResponse({'success': True})
            except Notification.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Notification not found'})

        return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def start_time_tracking(request, todo_id=None):
    user = request.user

    # Stop any active time entry
    active_entry = TimeEntry.objects.filter(user=user, is_active=True).first()
    if active_entry:
        active_entry.end_time = timezone.now()
        active_entry.is_active = False
        active_entry.save()

    # Start new time entry
    todo = None
    if todo_id:
        todo = get_object_or_404(Todo, id=todo_id, user=user)

    time_entry = TimeEntry.objects.create(
        user=user,
        todo=todo,
        start_time=timezone.now(),
        is_active=True
    )

    messages.success(request, f'Time tracking started for {todo.title if todo else "general work"}')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

@login_required
def stop_time_tracking(request):
    user = request.user

    active_entry = TimeEntry.objects.filter(user=user, is_active=True).first()
    if active_entry:
        active_entry.end_time = timezone.now()
        active_entry.is_active = False
        active_entry.save()
        messages.success(request, 'Time tracking stopped')
    else:
        messages.warning(request, 'No active time tracking to stop')

    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
