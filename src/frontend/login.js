// API Base URL - adjust based on your backend setup
// When running inside Docker, frontend proxies /api to the backend; use a relative path
// Docker maps backend port 8000 -> host 8010, so point to host:8010 when testing outside the proxy
const API_BASE_URL = 'http://46.249.101.150:8010'; // e.g. http://<backend-host>:8010

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
        // Send JSON credentials
        const payload = {
            username: username,
            password: password
        };

        const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok) {
            // Backend returns a LoginResponse with `user` and `message`.
            // Store the user id and username for subsequent requests (backend expects x-user-id header)
            localStorage.setItem('user_id', data.user.user_id);
            localStorage.setItem('username', data.user.username);

            // Redirect to main app
            window.location.href = 'index.html';
        } else {
            showError(data.detail || data.message || 'Login failed. Please check your credentials.');
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
if (localStorage.getItem('user_id')) {
    window.location.href = 'index.html';
}
