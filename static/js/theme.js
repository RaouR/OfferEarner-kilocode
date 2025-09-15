// Theme Management
class ThemeManager {
    constructor() {
        this.themeToggle = document.getElementById('theme-toggle');
        this.init();
    }

    init() {
        // Check for saved theme or default to light
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.setTheme(savedTheme);
        
        // Add event listener to toggle button
        if (this.themeToggle) {
            this.themeToggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        }
    }

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Update toggle button text
        if (this.themeToggle) {
            this.themeToggle.textContent = theme === 'light' ? '🌙' : '☀️';
        }
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }

    getCurrentTheme() {
        return document.documentElement.getAttribute('data-theme');
    }
}

// Navigation management
function updateNavigation() {
    const navAuthLinks = document.getElementById('nav-auth-links');
    if (!navAuthLinks) return;
    
    if (auth.isAuthenticated()) {
        const userInfo = auth.getUserInfo();
        navAuthLinks.innerHTML = `
            <a href="/dashboard" class="nav-link">Dashboard</a>
            <span class="nav-link" style="color: var(--primary-color);">Hi, ${userInfo?.username || 'User'}</span>
            <button onclick="auth.logout()" class="nav-link" style="background: none; border: none; cursor: pointer;">Logout</button>
        `;
    } else {
        navAuthLinks.innerHTML = `
            <a href="/login" class="nav-link">Login</a>
            <a href="/register" class="nav-link">Register</a>
        `;
    }
}

// Initialize theme manager and navigation when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ThemeManager();
    updateNavigation();
});

// Authentication and utility functions
const auth = {
    // Get stored token
    getToken() {
        return localStorage.getItem('access_token');
    },

    // Set token
    setToken(token) {
        localStorage.setItem('access_token', token);
    },

    // Remove token
    removeToken() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_info');
    },

    // Get user info
    getUserInfo() {
        const userStr = localStorage.getItem('user_info');
        return userStr ? JSON.parse(userStr) : null;
    },

    // Set user info
    setUserInfo(user) {
        localStorage.setItem('user_info', JSON.stringify(user));
    },

    // Check if user is authenticated
    isAuthenticated() {
        return !!this.getToken();
    },

    // Logout user
    logout() {
        this.removeToken();
        window.location.href = '/';
    }
};

// Utility functions
const utils = {
    // Format currency
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    },

    // Show notification
    showNotification(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 0.5rem;
            color: white;
            z-index: 1000;
            animation: slideIn 0.3s ease;
            max-width: 300px;
        `;
        
        const colors = {
            info: '#3b82f6',
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b'
        };
        
        toast.style.backgroundColor = colors[type] || colors.info;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        // Remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    },

    // API call wrapper with authentication
    async apiCall(url, options = {}) {
        try {
            const headers = {
                'Content-Type': 'application/json',
                ...options.headers
            };
            
            // Add authorization header if token exists
            const token = auth.getToken();
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
            
            const response = await fetch(url, {
                headers,
                ...options
            });
            
            if (response.status === 401) {
                // Token expired or invalid
                auth.logout();
                return;
            }
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            this.showNotification(error.message || 'Request failed. Please try again.', 'error');
            throw error;
        }
    }
};

// Export for use in other scripts
window.utils = utils;