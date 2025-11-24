// Professional Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard components
    initializeClock();
    initializeSidebar();
    initializeNotifications();
    initializeStats();
    initializeTaskActions();
});

// Real-time clock display
function initializeClock() {
    const timeDisplay = document.getElementById('timeDisplay');

    function updateTime() {
        const now = new Date();
        const options = {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: true
        };

        timeDisplay.textContent = now.toLocaleDateString('en-US', options);
    }

    updateTime();
    setInterval(updateTime, 1000);
}

// Sidebar toggle functionality
function initializeSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarCollapse = document.getElementById('sidebarCollapse');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');

    // Mobile sidebar toggle
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
    }

    // Desktop sidebar collapse/expand
    if (sidebarCollapse) {
        sidebarCollapse.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');

            // Save sidebar state to localStorage
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
        });
    }

    // Restore sidebar state on page load
    const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (sidebarCollapsed && window.innerWidth > 992) {
        sidebar.classList.add('collapsed');
    }

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(event) {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(event.target) && !sidebarToggle.contains(event.target)) {
                sidebar.classList.remove('show');
            }
        }
    });

    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('show');
        }

        // Auto-expand sidebar on larger screens if it was collapsed
        if (window.innerWidth > 992 && sidebar.classList.contains('collapsed')) {
            // Keep collapsed state as user preference
        } else if (window.innerWidth <= 992 && sidebar.classList.contains('collapsed')) {
            sidebar.classList.remove('collapsed');
        }
    });
}

// Notification system with sound
function initializeNotifications() {
    // Mark notifications as read when clicked
    const notificationItems = document.querySelectorAll('.notification-menu .dropdown-item');

    notificationItems.forEach(item => {
        item.addEventListener('click', function() {
            // Remove the badge count after clicking
            const badge = document.querySelector('.notification-btn .badge');
            if (badge) {
                const currentCount = parseInt(badge.textContent);
                if (currentCount > 1) {
                    badge.textContent = currentCount - 1;
                } else {
                    badge.remove();
                }
            }
        });
    });

    // Auto-refresh notifications every 30 seconds
    setInterval(fetchNotifications, 30000);

    // Check for due tasks every minute
    setInterval(checkDueTasks, 60000);

    // Check for reminders every minute
    setInterval(checkReminders, 60000);
}

async function fetchNotifications() {
    try {
        const response = await fetch('/api/notifications/');
        if (response.ok) {
            const data = await response.json();
            updateNotificationUI(data.notifications);
        }
    } catch (error) {
        console.log('Failed to fetch notifications:', error);
    }
}

function updateNotificationUI(notifications) {
    const notificationMenu = document.querySelector('.notification-menu .dropdown-menu');
    const badge = document.querySelector('.notification-btn .badge');

    if (notifications && notifications.length > 0) {
        // Update badge count
        if (badge) {
            badge.textContent = notifications.length;
        } else {
            // Create badge if it doesn't exist
            const notificationBtn = document.querySelector('.notification-btn');
            const newBadge = document.createElement('span');
            newBadge.className = 'position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger';
            newBadge.textContent = notifications.length;
            notificationBtn.appendChild(newBadge);
        }

        // Play sound notification if enabled
        playNotificationSound();

        // Show browser notification if permitted
        if (Notification.permission === 'granted') {
            const notification = notifications[0]; // Show first notification
            showBrowserNotification(notification.title, notification.message, notification.notification_type);
        }

        console.log('New notifications:', notifications);
    } else {
        if (badge) {
            badge.remove();
        }
    }
}

function playNotificationSound() {
    // Check if sound notifications are enabled (would be stored in user preferences)
    const soundEnabled = localStorage.getItem('sound_notifications') !== 'false';

    if (soundEnabled) {
        // Create audio context and play notification sound
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);

            oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
            oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1);

            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        } catch (error) {
            // Fallback: try to play a simple beep
            console.log('Audio notification played');
        }
    }
}

function showBrowserNotification(title, message, type) {
    if ('Notification' in window) {
        const icon = getNotificationIcon(type);

        const notification = new Notification(title, {
            body: message,
            icon: icon,
            badge: icon,
            tag: 'todo-notification'
        });

        notification.onclick = function() {
            window.focus();
            notification.close();
        };

        // Auto-close after 5 seconds
        setTimeout(() => {
            notification.close();
        }, 5000);
    }
}

function getNotificationIcon(type) {
    // Return appropriate icon based on notification type
    switch (type) {
        case 'reminder':
            return '/static/core/images/reminder-icon.png';
        case 'due_soon':
            return '/static/core/images/due-icon.png';
        case 'overdue':
            return '/static/core/images/overdue-icon.png';
        case 'completed':
            return '/static/core/images/completed-icon.png';
        default:
            return '/static/core/images/notification-icon.png';
    }
}

async function checkDueTasks() {
    try {
        // This would typically fetch due tasks from the server
        // For now, we'll simulate checking
        console.log('Checking for due tasks...');

        // In a real implementation, you'd fetch tasks due within the next hour
        // and show notifications for them
    } catch (error) {
        console.log('Error checking due tasks:', error);
    }
}

async function checkReminders() {
    try {
        // Check for active reminders
        console.log('Checking for reminders...');

        // In a real implementation, you'd check for reminders that should trigger now
        // and show appropriate notifications
    } catch (error) {
        console.log('Error checking reminders:', error);
    }
}

// Request notification permission on page load
document.addEventListener('DOMContentLoaded', function() {
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
});

// Statistics animations
function initializeStats() {
    const statValues = document.querySelectorAll('.stat-value');

    statValues.forEach(stat => {
        const targetValue = parseInt(stat.textContent);
        animateCounter(stat, 0, targetValue, 1000);
    });
}

function animateCounter(element, start, end, duration) {
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        const currentValue = Math.floor(start + (end - start) * progress);
        element.textContent = currentValue.toLocaleString();

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

// Task actions
function initializeTaskActions() {
    // Quick complete task
    const completeButtons = document.querySelectorAll('.task-complete-btn');
    completeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const taskId = this.dataset.taskId;

            Swal.fire({
                title: 'Complete Task?',
                text: 'Mark this task as completed?',
                icon: 'question',
                showCancelButton: true,
                confirmButtonColor: '#28a745',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'Yes, complete it!'
            }).then((result) => {
                if (result.isConfirmed) {
                    completeTask(taskId);
                }
            });
        });
    });

    // Quick delete task
    const deleteButtons = document.querySelectorAll('.task-delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const taskId = this.dataset.taskId;
            const taskTitle = this.dataset.taskTitle;

            Swal.fire({
                title: 'Delete Task?',
                text: `Are you sure you want to delete "${taskTitle}"?`,
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#dc3545',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'Yes, delete it!'
            }).then((result) => {
                if (result.isConfirmed) {
                    deleteTask(taskId);
                }
            });
        });
    });
}

async function completeTask(taskId) {
    try {
        const response = await fetch(`/api/tasks/${taskId}/complete/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        });

        if (response.ok) {
            Swal.fire({
                icon: 'success',
                title: 'Task Completed!',
                text: 'The task has been marked as completed.',
                timer: 2000,
                showConfirmButton: false
            }).then(() => {
                location.reload();
            });
        } else {
            throw new Error('Failed to complete task');
        }
    } catch (error) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Failed to complete the task. Please try again.'
        });
    }
}

async function deleteTask(taskId) {
    try {
        const response = await fetch(`/api/tasks/${taskId}/delete/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        });

        if (response.ok) {
            Swal.fire({
                icon: 'success',
                title: 'Task Deleted!',
                text: 'The task has been deleted successfully.',
                timer: 2000,
                showConfirmButton: false
            }).then(() => {
                location.reload();
            });
        } else {
            throw new Error('Failed to delete task');
        }
    } catch (error) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Failed to delete the task. Please try again.'
        });
    }
}

// Utility functions
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function getCSRFToken() {
    return getCookie('csrftoken');
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + B to toggle sidebar
    if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault();
        const sidebar = document.querySelector('.sidebar');
        sidebar.classList.toggle('show');
    }

    // Escape to close sidebar on mobile
    if (e.key === 'Escape' && window.innerWidth <= 768) {
        const sidebar = document.querySelector('.sidebar');
        sidebar.classList.remove('show');
    }
});

// Performance monitoring
function initializePerformanceMonitoring() {
    // Monitor page load time
    window.addEventListener('load', function() {
        const loadTime = performance.now();
        console.log(`Page loaded in ${loadTime.toFixed(2)} milliseconds`);
    });

    // Monitor API calls
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        const start = performance.now();
        return originalFetch.apply(this, args).then(response => {
            const end = performance.now();
            console.log(`API call to ${args[0]} took ${(end - start).toFixed(2)}ms`);
            return response;
        });
    };
}

// Initialize performance monitoring
initializePerformanceMonitoring();