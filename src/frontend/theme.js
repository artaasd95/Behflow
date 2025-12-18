// Theme Management
const themeToggle = document.getElementById('themeToggle');
const themeIcon = document.getElementById('themeIcon');
const html = document.documentElement;

// Get theme from localStorage or default to dark
let currentTheme = localStorage.getItem('theme') || 'dark';

// Apply theme on load
function applyTheme(theme) {
    html.setAttribute('data-theme', theme);
    themeIcon.textContent = theme === 'dark' ? '🌙' : '☀️';
    currentTheme = theme;
    localStorage.setItem('theme', theme);
}

// Initialize theme
applyTheme(currentTheme);

// Toggle theme
themeToggle.addEventListener('click', () => {
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    applyTheme(newTheme);
});
