// Custom JavaScript for Todo App

document.addEventListener('DOMContentLoaded', function() {
    // Initialize SweetAlert for messages
    const messages = document.querySelectorAll('.alert');
    messages.forEach(function(message) {
        const messageText = message.textContent.trim();
        const messageType = message.classList.contains('alert-success') ? 'success' :
                           message.classList.contains('alert-error') || message.classList.contains('alert-danger') ? 'error' :
                           message.classList.contains('alert-warning') ? 'warning' : 'info';

        if (messageText) {
            Swal.fire({
                icon: messageType,
                title: messageType.charAt(0).toUpperCase() + messageType.slice(1),
                text: messageText,
                timer: 3000,
                showConfirmButton: false
            });
        }
    });

    // Confirm delete with SweetAlert
    const deleteButtons = document.querySelectorAll('a[href*="delete"]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const href = this.getAttribute('href');

            Swal.fire({
                title: 'Are you sure?',
                text: 'This action cannot be undone!',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Yes, delete it!'
            }).then((result) => {
                if (result.isConfirmed) {
                    window.location.href = href;
                }
            });
        });
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        messages.forEach(function(message) {
            const alert = new bootstrap.Alert(message);
            alert.close();
        });
    }, 5000);

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    isValid = false;
                } else {
                    field.classList.remove('is-invalid');
                }
            });

            if (!isValid) {
                e.preventDefault();
                Swal.fire({
                    icon: 'error',
                    title: 'Validation Error',
                    text: 'Please fill in all required fields.'
                });
            }
        });
    });

    // Dynamic status update for completed todos
    const statusSelects = document.querySelectorAll('select[name="status"]');
    statusSelects.forEach(function(select) {
        select.addEventListener('change', function() {
            if (this.value === 'completed') {
                Swal.fire({
                    icon: 'success',
                    title: 'Congratulations!',
                    text: 'Todo marked as completed!',
                    timer: 2000,
                    showConfirmButton: false
                });
            }
        });
    });

    // Reminder notifications (simple browser notification)
    if ('Notification' in window) {
        if (Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }

    // Check for reminders (this would be called periodically in a real app)
    function checkReminders() {
        // This is a placeholder - in a real app, you'd fetch reminders from the server
        console.log('Checking for reminders...');
    }

    // Check reminders every minute
    setInterval(checkReminders, 60000);
});