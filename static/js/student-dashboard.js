// static/js/student-dashboard.js
$(document).ready(function() {
    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();
    
    // Auto-refresh dashboard data every 5 minutes
    setInterval(function() {
        refreshDashboardData();
    }, 300000);
    
    // Handle notification mark as read
    $('.notification-item').click(function() {
        var notificationId = $(this).data('notification-id');
        if (notificationId) {
            markNotificationAsRead(notificationId);
        }
    });
    
    // Handle quick actions
    $('.quick-action-btn').click(function() {
        var action = $(this).data('action');
        performQuickAction(action);
    });
    
    // Profile completion animation
    animateProfileCompletion();
});

function refreshDashboardData() {
    $.ajax({
        url: '/student/api/dashboard-data/',
        method: 'GET',
        success: function(data) {
            // Update dashboard stats
            updateDashboardStats(data);
        },
        error: function(xhr, status, error) {
            console.error('Error refreshing dashboard:', error);
        }
    });
}

function markNotificationAsRead(notificationId) {
    $.ajax({
        url: '/student/api/quick-actions/',
        method: 'POST',
        data: JSON.stringify({
            action: 'mark_notification_read',
            notification_id: notificationId
        }),
        contentType: 'application/json',
        success: function(response) {
            if (response.success) {
                // Update notification appearance
                $(`[data-notification-id="${notificationId}"]`).addClass('read');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error marking notification as read:', error);
        }
    });
}

function performQuickAction(action) {
    var data = {
        action: action
    };
    
    $.ajax({
        url: '/student/api/quick-actions/',
        method: 'POST',
        data: JSON.stringify(data),
        contentType: 'application/json',
        success: function(response) {
            if (response.success) {
                showNotification(response.message, 'success');
            } else {
                showNotification(response.message, 'error');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error performing quick action:', error);
            showNotification('Error performing action', 'error');
        }
    });
}

function updateDashboardStats(data) {
    // Update profile completion
    if (data.profile_completion !== undefined) {
        $('.profile-completion-percentage').text(data.profile_completion + '%');
        $('.profile-completion-bar').css('width', data.profile_completion + '%');
    }
    
    // Update application count
    if (data.application_count !== undefined) {
        $('.application-count').text(data.application_count);
    }
    
    // Update document count
    if (data.document_count !== undefined) {
        $('.document-count').text(data.document_count);
    }
}

function animateProfileCompletion() {
    var percentage = parseInt($('.profile-completion-percentage').text());
    var circle = $('.profile-completion-circle');
    
    if (circle.length > 0) {
        var radius = circle.attr('r');
        var circumference = 2 * Math.PI * radius;
        var strokeDasharray = circumference;
        var strokeDashoffset = circumference - (percentage / 100) * circumference;
        
        circle.css({
            'stroke-dasharray': strokeDasharray,
            'stroke-dashoffset': strokeDashoffset
        });
        
        // Animate the circle
        circle.animate({
            'stroke-dashoffset': strokeDashoffset
        }, 1000);
    }
}

function showNotification(message, type) {
    var alertClass = 'alert-info';
    
    switch (type) {
        case 'success':
            alertClass = 'alert-success';
            break;
        case 'error':
            alertClass = 'alert-danger';
            break;
        case 'warning':
            alertClass = 'alert-warning';
            break;
    }
    
    var notification = $(`
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `);
    
    $('#notification-container').append(notification);
    
    // Auto-dismiss after 5 seconds
    setTimeout(function() {
        notification.alert('close');
    }, 5000);
}

// Chart.js configuration for dashboard charts
if (typeof Chart !== 'undefined') {
    // Profile completion chart
    var profileCtx = document.getElementById('profileCompletionChart');
    if (profileCtx) {
        var profileChart = new Chart(profileCtx, {
            type: 'doughnut',
            data: {
                labels: ['Completed', 'Remaining'],
                datasets: [{
                    data: [profileCompletion, 100 - profileCompletion],
                    backgroundColor: ['#28a745', '#e9ecef'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    // Application status chart
    var statusCtx = document.getElementById('applicationStatusChart');
    if (statusCtx) {
        var statusChart = new Chart(statusCtx, {
            type: 'bar',
            data: {
                labels: ['Draft', 'Submitted', 'Under Review', 'Approved', 'Rejected'],
                datasets: [{
                    label: 'Applications',
                    data: [2, 3, 1, 2, 0],
                    backgroundColor: [
                        '#6c757d',
                        '#007bff',
                        '#ffc107',
                        '#28a745',
                        '#dc3545'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}
