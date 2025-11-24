# Todo App Developer Guide

## Overview

This Django-based Todo application provides a comprehensive task management system with user authentication, CRUD operations, reminders, calendar views, and responsive design. The app follows Django best practices and includes features like priority levels, categories, due dates, and reminder notifications.

## Architecture

### Project Structure

```
myapp/
├── myapp/                 # Main Django project
│   ├── settings.py       # Project settings
│   ├── urls.py          # Main URL configuration
│   └── ...
├── core/                 # Main app
│   ├── models.py        # Data models
│   ├── views.py         # View logic
│   ├── forms.py         # Form definitions
│   ├── urls.py          # App URL configuration
│   ├── admin.py         # Admin interface
│   ├── context_processors.py  # Template context processors
│   ├── templates/core/  # HTML templates
│   └── static/core/     # Static files (CSS, JS)
├── docs/                # Documentation
└── db.sqlite3          # SQLite database
```

## Models

### Todo Model

The core model representing a todo item:

```python
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
    due_date = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    category = models.CharField(max_length=100, blank=True)
    reminder_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
```

#### Key Methods

- `is_overdue()`: Checks if the todo is past its due date
- `reminder_due()`: Checks if a reminder notification should be shown
- `__str__()`: Returns the todo title

## Views

### Authentication Views

- `register(request)`: Handles user registration
- `user_login(request)`: Handles user login
- `user_logout(request)`: Handles user logout

### Todo CRUD Views

- `todo_list(request)`: Displays all todos for the authenticated user
- `todo_create(request)`: Creates a new todo
- `todo_update(request, pk)`: Updates an existing todo
- `todo_delete(request, pk)`: Deletes a todo
- `calendar_view(request)`: Displays todos grouped by due date

All views are decorated with `@login_required` to ensure authentication.

## Forms

### UserRegistrationForm

Extends Django's `UserCreationForm` to include email field:

```python
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
```

## Templates

### Base Template

`core/templates/core/base.html` provides the common layout with:

- Bootstrap 5 integration
- Font Awesome icons
- SweetAlert2 for notifications
- Responsive navbar with authentication links
- Reminder dropdown for pending notifications

### Key Templates

- `login.html`: User login form
- `register.html`: User registration form
- `todo_list.html`: Grid layout of todos with status indicators
- `todo_form.html`: Create/edit form with datetime inputs
- `todo_confirm_delete.html`: Delete confirmation dialog
- `calendar.html`: Todos grouped by due date

## Static Files

### CSS (`core/static/core/css/style.css`)

Custom styling with:

- Black, green, white color scheme
- Responsive design enhancements
- Hover effects and animations
- Bootstrap overrides for consistent theming

### JavaScript (`core/static/core/js/script.js`)

Client-side functionality:

- SweetAlert integration for messages and confirmations
- Form validation
- Dynamic status updates
- Reminder checking (placeholder for future enhancements)

## Context Processors

### Reminders Context Processor

`core/context_processors.py` provides pending reminders to all templates:

```python
def reminders(request):
    if request.user.is_authenticated:
        reminders = Todo.objects.filter(
            user=request.user,
            reminder_date__lte=timezone.now(),
            completed=False
        ).order_by('reminder_date')[:5]
        return {'reminders': reminders}
    return {'reminders': []}
```

## URL Configuration

### Main URLs (`myapp/urls.py`)

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]
```

### App URLs (`core/urls.py`)

```python
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('', views.todo_list, name='todo_list'),
    path('todo/create/', views.todo_create, name='todo_create'),
    path('todo/<int:pk>/update/', views.todo_update, name='todo_update'),
    path('todo/<int:pk>/delete/', views.todo_delete, name='todo_delete'),
    path('calendar/', views.calendar_view, name='calendar'),
]
```

## Admin Interface

Registered models in `core/admin.py`:

```python
@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'priority', 'due_date', 'completed', 'created_at')
    list_filter = ('status', 'priority', 'completed', 'due_date', 'user')
    search_fields = ('title', 'description', 'category')
    ordering = ('-created_at',)
```

## Settings Configuration

Key settings in `myapp/settings.py`:

- `INSTALLED_APPS`: Includes 'core' app
- `TEMPLATES`: Configured with custom context processors
- `STATICFILES_DIRS`: Points to app static files
- Database: SQLite (default)

## Features

### Authentication

- User registration with email
- Login/logout functionality
- Session-based authentication
- Protected views with `@login_required`

### Todo Management

- Create, read, update, delete operations
- Priority levels (Low, Medium, High)
- Status tracking (Pending, In Progress, Completed)
- Categories for organization
- Due dates with overdue detection
- Rich descriptions

### Reminders

- Optional reminder dates
- Context processor for pending reminders
- Navbar dropdown notification
- Links to edit reminded todos

### Calendar View

- Todos grouped by due date
- Visual priority indicators
- Responsive card layout

### User Interface

- Bootstrap 5 responsive design
- Black, green, white color scheme
- SweetAlert notifications
- Font Awesome icons
- Mobile-friendly layout

## Security Considerations

- CSRF protection on all forms
- Authentication required for all todo operations
- User isolation (users only see their own todos)
- Secure password handling via Django auth

## Performance

- Efficient database queries with select_related/prefetch_related where applicable
- Pagination ready (can be added for large todo lists)
- Static file optimization
- Minimal JavaScript for fast loading

## Future Enhancements

- Email notifications for reminders
- Recurring todos
- File attachments
- Todo sharing/collaboration
- Advanced filtering and search
- API endpoints for mobile app integration
- Calendar integration (Google Calendar, etc.)
- Time tracking
- Todo templates

## Testing

To run the application:

1. Ensure Python and Django are installed
2. Run migrations: `python manage.py migrate`
3. Create superuser: `python manage.py createsuperuser`
4. Run server: `python manage.py runserver`
5. Access at http://127.0.0.1:8000/

## Deployment

For production deployment:

1. Set `DEBUG = False`
2. Configure proper database (PostgreSQL recommended)
3. Set up static file serving
4. Configure email backend for notifications
5. Set secure SECRET_KEY
6. Use HTTPS
7. Configure ALLOWED_HOSTS

This documentation covers the core Django logic and architecture. The application follows Django best practices and provides a solid foundation for a production-ready todo management system.