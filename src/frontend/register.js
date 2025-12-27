// API Base URL - adjust based on your backend setup
// When running inside Docker, frontend proxies /api to the backend; use a relative path
const API_BASE_URL = ''; // use relative paths like /api/xxx

// Get form elements
const registerForm = document.getElementById('registerForm');
const registerBtn = document.getElementById('registerBtn');
const errorMessage = document.getElementById('errorMessage');

// Show error message
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.add('show');
    setTimeout(() => {
        errorMessage.classList.remove('show');
    }, 5000);
}

// Validate password
function validatePassword(password, confirmPassword) {
    if (password.length < 6) {
        return 'Password must be at least 6 characters long';
    }
    if (password !== confirmPassword) {
        return 'Passwords do not match';
    }
    return null;
}

// Validate email
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Handle registration form submission
registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    // Validate inputs
    if (!username || !email || !password || !confirmPassword) {
        showError('Please fill in all fields');
        return;
    }
    
    if (username.length < 3) {
        showError('Username must be at least 3 characters long');
        return;
    }
    
    if (!validateEmail(email)) {
        showError('Please enter a valid email address');
        return;
    }
    
    const passwordError = validatePassword(password, confirmPassword);
    if (passwordError) {
        showError(passwordError);
        return;
    }
    
    // Disable button and show loading state
    registerBtn.disabled = true;
    registerBtn.innerHTML = '<span class="loading"></span> Creating account...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Registration successful - redirect to login
            alert('Registration successful! Please log in.');
            window.location.href = 'login.html';
        } else {
            showError(data.detail || 'Registration failed. Please try again.');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showError('Connection error. Please make sure the server is running.');
    } finally {
        // Re-enable button
        registerBtn.disabled = false;
        registerBtn.innerHTML = 'Register';
    }
});

// Check if already logged in
if (localStorage.getItem('access_token')) {
    window.location.href = 'index.html';
}
