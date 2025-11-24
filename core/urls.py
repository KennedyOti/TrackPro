from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Landing Page
    path('', views.landing, name='landing'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Tasks
    path('tasks/', views.todo_list, name='todo_list'),
    path('todo/create/', views.todo_create, name='todo_create'),
    path('todo/<int:pk>/update/', views.todo_update, name='todo_update'),
    path('todo/<int:pk>/delete/', views.todo_delete, name='todo_delete'),

    # Features
    path('calendar/', views.calendar_view, name='calendar'),
    path('reports/', views.reports_view, name='reports'),
    path('settings/', views.settings_view, name='settings'),
    path('time-tracking/', views.time_tracking_view, name='time_tracking'),

    # Time Tracking Actions
    path('time/start/', views.start_time_tracking, name='start_time_tracking'),
    path('time/start/<int:todo_id>/', views.start_time_tracking, name='start_time_tracking_todo'),
    path('time/stop/', views.stop_time_tracking, name='stop_time_tracking'),

    # API Endpoints
    path('api/notifications/', views.NotificationsAPIView.as_view(), name='api_notifications'),
]