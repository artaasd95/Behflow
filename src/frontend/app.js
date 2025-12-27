// API Base URL - adjust based on your backend setup
// When running inside Docker, frontend proxies /api to the backend; use a relative path
// Docker maps backend port 8000 -> host 8010, so point to host:8010 when testing outside the proxy
const API_BASE_URL = 'http://46.249.101.150:8010'; // e.g. http://<backend-host>:8010

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

// ===== DATE DISPLAY FUNCTIONALITY =====

/**
 * Convert Gregorian date to Jalali (Persian) date
 * Simple conversion algorithm
 */
function gregorianToJalali(gYear, gMonth, gDay) {
    const g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
    
    let jYear = (gYear <= 1600) ? 0 : 979;
    gYear -= (gYear <= 1600) ? 621 : 1600;
    
    let gy2 = (gMonth > 2) ? (gYear + 1) : gYear;
    let days = (365 * gYear) + (Math.floor((gy2 + 3) / 4)) - (Math.floor((gy2 + 99) / 100)) + 
               (Math.floor((gy2 + 399) / 400)) - 80 + gDay + g_d_m[gMonth - 1];
    
    jYear += 33 * Math.floor(days / 12053);
    days %= 12053;
    
    jYear += 4 * Math.floor(days / 1461);
    days %= 1461;
    
    if (days > 365) {
        jYear += Math.floor((days - 1) / 365);
        days = (days - 1) % 365;
    }
    
    const jMonth = (days < 186) ? 1 + Math.floor(days / 31) : 7 + Math.floor((days - 186) / 30);
    const jDay = 1 + ((days < 186) ? (days % 31) : ((days - 186) % 30));
    
    return [jYear, jMonth, jDay];
}

/**
 * Get Jalali month name
 */
function getJalaliMonthName(month) {
    const months = [
        'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
        'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
    ];
    return months[month - 1];
}

/**
 * Update date display in header
 */
function updateDateDisplay() {
    const now = new Date();
    
    // Gregorian date
    const gregorianOptions = { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    };
    const gregorianStr = now.toLocaleDateString('en-US', gregorianOptions);
    
    // Jalali date
    const [jYear, jMonth, jDay] = gregorianToJalali(
        now.getFullYear(), 
        now.getMonth() + 1, 
        now.getDate()
    );
    const jalaliStr = `${jDay} ${getJalaliMonthName(jMonth)} ${jYear}`;
    
    // Update DOM
    const dateGregorian = document.getElementById('dateGregorian');
    const dateJalali = document.getElementById('dateJalali');
    
    if (dateGregorian) {
        dateGregorian.textContent = `📅 ${gregorianStr}`;
    }
    
    if (dateJalali) {
        dateJalali.textContent = `📅 ${jalaliStr}`;
    }
}

// Initialize date display
updateDateDisplay();

// Update date display at midnight
setInterval(() => {
    const now = new Date();
    if (now.getHours() === 0 && now.getMinutes() === 0) {
        updateDateDisplay();
    }
}, 60000); // Check every minute

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
    'pending': 'Pending',
    'in_progress': 'In Progress',
    'completed': 'Completed',
    'cancelled': 'Cancelled'
};

// Task status enum values for API
const STATUS_ENUM = {
    'pending': 'pending',
    'in_progress': 'in_progress',
    'completed': 'completed',
    'cancelled': 'cancelled'
};

/**
 * Update task status via API
 */
async function updateTaskStatus(taskId, status) {
    try {
        const response = await apiRequest('/api/v1/tasks/status', {
            method: 'PUT',
            body: JSON.stringify({
                task_id: taskId,
                status: status
            })
        });
        
        if (response && response.success) {
            console.log(`Task ${taskId} status updated to ${status}`);
            // Reload tasks to reflect changes
            await loadTasks();
            return true;
        } else {
            console.error('Failed to update task status:', response);
            return false;
        }
    } catch (error) {
        console.error('Error updating task status:', error);
        return false;
    }
}

/**
 * Mark task as completed
 */
async function markTaskComplete(taskId) {
    return await updateTaskStatus(taskId, STATUS_ENUM.completed);
}

/**
 * Handle status change button click
 */
function handleStatusChange(taskId, selectElement) {
    const newStatus = selectElement.value;
    
    // Create and show update button if it doesn't exist
    let updateBtn = selectElement.nextElementSibling;
    if (!updateBtn || !updateBtn.classList.contains('task-btn-update')) {
        updateBtn = document.createElement('button');
        updateBtn.className = 'task-btn task-btn-update';
        updateBtn.textContent = 'Update';
        updateBtn.onclick = async () => {
            const success = await updateTaskStatus(taskId, newStatus);
            if (success) {
                // Remove the dropdown and update button after successful update
                selectElement.remove();
                updateBtn.remove();
            }
        };
        selectElement.parentNode.insertBefore(updateBtn, selectElement.nextSibling);
    }
}

// Load and display tasks
async function loadTasks() {
    const tasksContainer = document.getElementById('tasksContainer');
    
    try {
        // Fetch tasks from API
        const tasks = await apiRequest('/api/v1/tasks');
        
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
            const status = task.status || 'pending';
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
                            <li class="task-item ${status}" data-task-id="${task.task_id}">
                                <div class="task-item-content">
                                    <div class="markdown-content">${marked.parse(task.name || 'Untitled Task')}</div>
                                    ${task.description ? `<div class="markdown-content" style="font-size: 0.9em; opacity: 0.8; margin-top: 5px;">${marked.parse(task.description)}</div>` : ''}
                                    <div class="task-actions">
                                        <button class="task-btn task-btn-done" onclick="markTaskComplete('${task.task_id}')">
                                            ✓ Done
                                        </button>
                                        <button class="task-btn task-btn-change" onclick="showStatusDropdown('${task.task_id}', this)">
                                            ⚡ Change Status
                                        </button>
                                    </div>
                                </div>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `;
        }
        
        tasksContainer.innerHTML = html;
        
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

/**
 * Show status dropdown for task
 */
function showStatusDropdown(taskId, buttonElement) {
    // Check if dropdown already exists
    const existingDropdown = buttonElement.nextElementSibling;
    if (existingDropdown && existingDropdown.tagName === 'SELECT') {
        existingDropdown.remove();
        const existingUpdateBtn = existingDropdown.nextElementSibling;
        if (existingUpdateBtn && existingUpdateBtn.classList.contains('task-btn-update')) {
            existingUpdateBtn.remove();
        }
        return;
    }
    
    // Create status dropdown
    const select = document.createElement('select');
    select.className = 'task-status-select';
    
    // Add options
    for (const [value, label] of Object.entries(TASK_STATUS)) {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = label;
        select.appendChild(option);
    }
    
    // Preselect current task status when showing the dropdown
    const taskElem = document.querySelector(`[data-task-id="${taskId}"]`);
    if (taskElem) {
        // The list item has a class matching the status name (e.g., 'in_progress')
        const classes = Array.from(taskElem.classList);
        const currentStatus = Object.keys(TASK_STATUS).find(s => classes.includes(s));
        if (currentStatus) {
            select.value = currentStatus;
        }
    }

    // Add change handler
    select.onchange = () => handleStatusChange(taskId, select);
    
    // Insert after button
    buttonElement.parentNode.insertBefore(select, buttonElement.nextSibling);
}

// ===== CHAT FUNCTIONALITY =====

const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');

// Load chat history
async function loadChatHistory() {
    try {
        const messages = await apiRequest('/api/v1/chat/history');
        
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
        const response = await apiRequest('/api/v1/chat', {
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
