// Authentication management
document.addEventListener('DOMContentLoaded', function() {
    const logoutBtn = document.getElementById('logout-btn');
    
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            // Clear stored authentication data
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            
            // Redirect to home page
            window.location.href = '/';
        });
    }
    
    // Check authentication status on page load
    checkAuthStatus();
});

function checkAuthStatus() {
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    
    if (!token || !user) {
        // Clear any invalid data
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        return;
    }
    
    // Verify token is still valid
    fetch('/api/auth/me', {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    })
    .then(response => {
        if (!response.ok) {
            // Token is invalid, clear it
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            if (window.location.pathname.startsWith('/dashboard')) {
                window.location.href = '/login';
            }
        }
    })
    .catch(error => {
        console.error('Auth check failed:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    });
}

// Helper function to get auth headers
function getAuthHeaders() {
    const token = localStorage.getItem('token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
    };
}
