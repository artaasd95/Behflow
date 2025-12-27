// API Base URL - adjust based on your backend setup
// When running inside Docker, frontend proxies /api to the backend; use a relative path
const API_BASE_URL = ''; // use relative paths like /api/xxx

// Get form elements
const loginForm = document.getElementById('loginForm');
const loginBtn = document.getElementById('loginBtn');
const errorMessage = document.getElementById('errorMessage');

// Show error message
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.add('show');
    setTimeout(() => {
        errorMessage.classList.remove('show');
    }, 5000);
}

// Handle login form submission
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    
    if (!username || !password) {
        showError('Please enter both username and password');
        return;
    }
    
    // Disable button and show loading state
    loginBtn.disabled = true;
    loginBtn.innerHTML = '<span class="loading"></span> Logging in...';
    
    try {
        // Create form data for OAuth2 password flow
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store token and user info
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('token_type', data.token_type);
            localStorage.setItem('username', username);
            
            // Redirect to main app
            window.location.href = 'index.html';
        } else {
            showError(data.detail || 'Login failed. Please check your credentials.');
        }
    } catch (error) {
        console.error('Login error:', error);
        showError('Connection error. Please make sure the server is running.');
    } finally {
        // Re-enable button
        loginBtn.disabled = false;
        loginBtn.innerHTML = 'Login';
    }
});

// Check if already logged in
if (localStorage.getItem('access_token')) {
    window.location.href = 'index.html';
}
