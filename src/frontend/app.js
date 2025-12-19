// API Base URL - adjust based on your backend setup
// When running inside Docker, frontend proxies /api to the backend; use a relative path
const API_BASE_URL = ''; // use relative paths like /api/xxx

// Get stored auth token
const token = localStorage.getItem('access_token');
const tokenType = localStorage.getItem('token_type') || 'Bearer';
const username = localStorage.getItem('username');

// Check authentication
if (!token) {
    window.location.href = 'login.html';
}

// Display username
const userDisplay = document.getElementById('userDisplay');
if (userDisplay && username) {
    userDisplay.textContent = `👤 ${username}`;
}

// Set initial timestamp
const initialTime = document.getElementById('initialTime');
if (initialTime) {
    initialTime.textContent = new Date().toLocaleTimeString();
}

// Logout functionality
const logoutBtn = document.getElementById('logoutBtn');
logoutBtn.addEventListener('click', () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('token_type');
    localStorage.removeItem('username');
    window.location.href = 'login.html';
});

// API Helper function
async function apiRequest(endpoint, options = {}) {
    const defaultOptions = {
        headers: {
            'Authorization': `${tokenType} ${token}`,
            'Content-Type': 'application/json',
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            ...defaultOptions
        });
        
        if (response.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('access_token');
            window.location.href = 'login.html';
            return null;
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        return null;
    }
}

// ===== TASKS FUNCTIONALITY =====

// Task status mapping
const TASK_STATUS = {
    'not-started': 'Not Started',
    'in-progress': 'In Progress',
    'completed': 'Completed',
    'blocked': 'Blocked'
};

// Load and display tasks
async function loadTasks() {
    const tasksContainer = document.getElementById('tasksContainer');
    
    try {
        // Fetch tasks from API
        const tasks = await apiRequest('/api/chat/tasks');
        
        if (!tasks || tasks.length === 0) {
            tasksContainer.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📋</div>
                    <p>No tasks found. Start a conversation to create tasks!</p>
                </div>
            `;
            return;
        }
        
        // Group tasks by status
        const tasksByStatus = {};
        tasks.forEach(task => {
            const status = task.status || 'not-started';
            if (!tasksByStatus[status]) {
                tasksByStatus[status] = [];
            }
            tasksByStatus[status].push(task);
        });
        
        // Render tasks by status
        let html = '';
        for (const [status, statusTasks] of Object.entries(tasksByStatus)) {
            html += `
                <div class="tasks-section">
                    <h2>${TASK_STATUS[status] || status}</h2>
                    <ul class="task-list">
                        ${statusTasks.map(task => `
                            <li class="task-item ${status}" data-task-id="${task.id}">
                                <div class="markdown-content">${marked.parse(task.description || task.title)}</div>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `;
        }
        
        tasksContainer.innerHTML = html;
        
        // Add click handlers for tasks
        document.querySelectorAll('.task-item').forEach(item => {
            item.addEventListener('click', () => {
                const taskId = item.getAttribute('data-task-id');
                handleTaskClick(taskId);
            });
        });
        
    } catch (error) {
        console.error('Error loading tasks:', error);
        tasksContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <p>Error loading tasks. Please try again later.</p>
            </div>
        `;
    }
}

// Handle task click
function handleTaskClick(taskId) {
    console.log('Task clicked:', taskId);
    // You can implement task detail view or actions here
}

// ===== CHAT FUNCTIONALITY =====

const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');

// Load chat history
async function loadChatHistory() {
    try {
        const messages = await apiRequest('/api/chat/history');
        
        if (messages && messages.length > 0) {
            // Clear initial message
            chatMessages.innerHTML = '';
            
            messages.forEach(msg => {
                addMessageToChat(msg.content, msg.role === 'user' ? 'user' : 'assistant', new Date(msg.timestamp));
            });
            
            // Scroll to bottom
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    } catch (error) {
        console.error('Error loading chat history:', error);
    }
}

// Add message to chat UI
function addMessageToChat(content, role, timestamp = new Date()) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    
    // Parse markdown for assistant messages
    if (role === 'assistant') {
        contentDiv.className = 'markdown-content';
        contentDiv.innerHTML = marked.parse(content);
    } else {
        contentDiv.textContent = content;
    }
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = timestamp.toLocaleTimeString();
    
    messageDiv.appendChild(contentDiv);
    messageDiv.appendChild(timeDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Send message
async function sendMessage() {
    const message = chatInput.value.trim();
    
    if (!message) return;
    
    // Add user message to UI
    addMessageToChat(message, 'user');
    
    // Clear input
    chatInput.value = '';
    
    // Disable send button
    sendBtn.disabled = true;
    sendBtn.innerHTML = '<span class="loading"></span>';
    
    try {
        // Send message to API
        const response = await apiRequest('/api/chat/message', {
            method: 'POST',
            body: JSON.stringify({ message })
        });
        
        if (response && response.response) {
            // Add assistant response to UI
            addMessageToChat(response.response, 'assistant');
            
            // Reload tasks if they might have changed
            await loadTasks();
        } else {
            addMessageToChat('Sorry, I encountered an error. Please try again.', 'assistant');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        addMessageToChat('Connection error. Please try again.', 'assistant');
    } finally {
        // Re-enable send button
        sendBtn.disabled = false;
        sendBtn.innerHTML = 'Send';
        chatInput.focus();
    }
}

// Event listeners for chat
sendBtn.addEventListener('click', sendMessage);

chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Auto-resize textarea
chatInput.addEventListener('input', () => {
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
});

// ===== INITIALIZATION =====

// Load data on page load
async function initialize() {
    await Promise.all([
        loadTasks(),
        loadChatHistory()
    ]);
}

// Initialize the app
initialize();

// Refresh tasks periodically (every 30 seconds)
setInterval(loadTasks, 30000);
