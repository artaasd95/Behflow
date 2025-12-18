# Frontend Documentation

## Overview

The Behflow frontend is a modern, lightweight single-page application (SPA) built with vanilla JavaScript, HTML5, and CSS3. It provides an intuitive interface for task management and AI-powered chat interactions.

## Architecture

### Technology Stack

- **HTML5**: Semantic markup and structure
- **CSS3**: Custom styling with Atom One Dark Pro theme
- **Vanilla JavaScript**: No framework dependencies
- **Markdown Rendering**: For chat message formatting
- **LocalStorage**: Session persistence

### File Structure

```
frontend/
├── index.html       # Main application page (tasks & chat)
├── login.html       # User login page
├── register.html    # User registration page
├── app.js          # Main application logic
├── login.js        # Login functionality
├── register.js     # Registration functionality
├── theme.js        # Theme switching logic
├── styles.css      # Application styles
├── nginx.conf      # Production server configuration
└── Dockerfile      # Container configuration
```

## Pages

### Login Page (`login.html`)

**Purpose**: User authentication

**Features**:
- Username and password input
- Form validation
- Error message display
- Link to registration page
- Theme toggle

**JavaScript Logic** (`login.js`):
```javascript
// Form submission
document.getElementById('loginForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  
  // API call to /login
  const response = await fetch(`${API_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  
  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('token', data.token);
    localStorage.setItem('user', JSON.stringify(data.user));
    window.location.href = '/index.html';
  }
});
```

---

### Registration Page (`register.html`)

**Purpose**: New user account creation

**Features**:
- Username, password, name, lastname inputs
- Password confirmation
- Form validation
- Error message display
- Link to login page

**JavaScript Logic** (`register.js`):
```javascript
// Registration form submission
document.getElementById('registerForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  // Validate password match
  if (password !== confirmPassword) {
    showError('Passwords do not match');
    return;
  }
  
  // API call to /register
  const response = await fetch(`${API_URL}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password, name, lastname })
  });
  
  if (response.ok) {
    window.location.href = '/login.html';
  }
});
```

---

### Main Application (`index.html`)

**Purpose**: Task management and AI chat interface

**Sections**:
1. **Header**: User info, logout, theme toggle
2. **Task Board**: Tasks grouped by status
3. **Chat Panel**: AI assistant interaction
4. **Add Task Form**: Quick task creation

**Layout**:
```
+------------------------------------------+
|  Header (User Info | Theme | Logout)    |
+------------------------------------------+
|  Task Board                | Chat Panel |
|  ┌────────────────┐        | ┌────────┐ |
|  │ Not Started    │        | │Messages│ |
|  │ ┌──────────┐   │        | │        │ |
|  │ │ Task 1   │   │        | │        │ |
|  │ └──────────┘   │        | └────────┘ |
|  │                │        | ┌────────┐ |
|  │ In Progress    │        | │ Input  │ |
|  │ ┌──────────┐   │        | └────────┘ |
|  │ │ Task 2   │   │        |            |
|  │ └──────────┘   │        |            |
|  └────────────────┘        |            |
+------------------------------------------+
```

## Core Modules

### App Module (`app.js`)

#### Task Management

**Load Tasks**:
```javascript
async function loadTasks() {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_URL}/api/v1/tasks`, {
    headers: { 'Authorization': token }
  });
  const tasks = await response.json();
  renderTasks(tasks);
}
```

**Create Task**:
```javascript
async function createTask(taskData) {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_URL}/api/v1/tasks`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token
    },
    body: JSON.stringify(taskData)
  });
  return await response.json();
}
```

**Update Task Status**:
```javascript
async function updateTaskStatus(taskId, newStatus) {
  const token = localStorage.getItem('token');
  await fetch(`${API_URL}/api/v1/tasks/${taskId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token
    },
    body: JSON.stringify({ status: newStatus })
  });
  loadTasks(); // Refresh
}
```

**Delete Task**:
```javascript
async function deleteTask(taskId) {
  const token = localStorage.getItem('token');
  await fetch(`${API_URL}/api/v1/tasks/${taskId}`, {
    method: 'DELETE',
    headers: { 'Authorization': token }
  });
  loadTasks(); // Refresh
}
```

#### Task Rendering

```javascript
function renderTasks(tasks) {
  const columns = {
    'not_started': document.getElementById('notStartedTasks'),
    'in_progress': document.getElementById('inProgressTasks'),
    'completed': document.getElementById('completedTasks'),
    'blocked': document.getElementById('blockedTasks')
  };
  
  // Clear columns
  Object.values(columns).forEach(col => col.innerHTML = '');
  
  // Group and render tasks
  tasks.forEach(task => {
    const taskElement = createTaskElement(task);
    columns[task.status].appendChild(taskElement);
  });
}

function createTaskElement(task) {
  const div = document.createElement('div');
  div.className = 'task-card';
  div.innerHTML = `
    <h4>${task.name}</h4>
    <p>${task.description}</p>
    <span class="priority-badge ${task.priority}">${task.priority}</span>
    <div class="task-actions">
      <button onclick="editTask('${task.task_id}')">Edit</button>
      <button onclick="deleteTask('${task.task_id}')">Delete</button>
    </div>
  `;
  
  // Drag and drop for status change
  div.draggable = true;
  div.addEventListener('dragstart', (e) => {
    e.dataTransfer.setData('taskId', task.task_id);
  });
  
  return div;
}
```

#### Chat Interface

**Send Message**:
```javascript
async function sendMessage(message) {
  const token = localStorage.getItem('token');
  const sessionId = localStorage.getItem('chatSessionId') || generateSessionId();
  
  // Display user message
  appendMessage('user', message);
  
  // Send to API
  const response = await fetch(`${API_URL}/api/v1/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token
    },
    body: JSON.stringify({ message, session_id: sessionId })
  });
  
  const data = await response.json();
  
  // Display AI response
  appendMessage('assistant', data.response);
  
  // Update tasks if any were created/modified
  if (data.tasks && data.tasks.length > 0) {
    loadTasks();
  }
  
  // Save session ID
  localStorage.setItem('chatSessionId', data.session_id);
}
```

**Render Messages**:
```javascript
function appendMessage(role, content) {
  const chatMessages = document.getElementById('chatMessages');
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${role}`;
  
  // Parse markdown if assistant message
  if (role === 'assistant') {
    messageDiv.innerHTML = parseMarkdown(content);
  } else {
    messageDiv.textContent = content;
  }
  
  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function parseMarkdown(text) {
  // Simple markdown parsing
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>');
}
```

### Theme Module (`theme.js`)

**Theme Switching Logic**:
```javascript
const THEMES = {
  dark: {
    '--bg-primary': '#1e1e1e',
    '--bg-secondary': '#252525',
    '--text-primary': '#d4d4d4',
    '--text-secondary': '#969696',
    '--accent': '#007acc'
  },
  light: {
    '--bg-primary': '#ffffff',
    '--bg-secondary': '#f3f3f3',
    '--text-primary': '#333333',
    '--text-secondary': '#666666',
    '--accent': '#007acc'
  }
};

function toggleTheme() {
  const currentTheme = localStorage.getItem('theme') || 'dark';
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  
  applyTheme(newTheme);
  localStorage.setItem('theme', newTheme);
}

function applyTheme(theme) {
  const root = document.documentElement;
  Object.entries(THEMES[theme]).forEach(([key, value]) => {
    root.style.setProperty(key, value);
  });
}

// Load saved theme on page load
document.addEventListener('DOMContentLoaded', () => {
  const savedTheme = localStorage.getItem('theme') || 'dark';
  applyTheme(savedTheme);
});
```

## Styling

### Atom One Dark Pro Theme

**Color Palette**:
- Background Primary: `#1e1e1e`
- Background Secondary: `#252525`
- Text Primary: `#d4d4d4`
- Text Secondary: `#969696`
- Accent Blue: `#007acc`
- Success Green: `#4ec9b0`
- Warning Orange: `#ce9178`
- Error Red: `#f48771`

**Key CSS Classes**:
```css
.task-card {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  transition: transform 0.2s;
}

.task-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.3);
}

.priority-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.priority-badge.high {
  background: #f48771;
  color: white;
}

.priority-badge.medium {
  background: #ce9178;
  color: white;
}

.priority-badge.low {
  background: #4ec9b0;
  color: white;
}
```

## State Management

### LocalStorage Schema

```javascript
{
  "token": "uuid-string",           // Auth token
  "user": {                          // User info
    "user_id": "uuid",
    "username": "string",
    "name": "string",
    "lastname": "string"
  },
  "chatSessionId": "string",         // Chat session ID
  "theme": "dark|light"              // Theme preference
}
```

### Session Handling

```javascript
function checkAuth() {
  const token = localStorage.getItem('token');
  if (!token) {
    window.location.href = '/login.html';
    return false;
  }
  return true;
}

function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  localStorage.removeItem('chatSessionId');
  window.location.href = '/login.html';
}
```

## Event Handling

### Drag and Drop

```javascript
// Enable drag on task cards
taskElement.draggable = true;
taskElement.addEventListener('dragstart', (e) => {
  e.dataTransfer.setData('taskId', task.task_id);
});

// Enable drop on status columns
columnElement.addEventListener('dragover', (e) => {
  e.preventDefault(); // Allow drop
});

columnElement.addEventListener('drop', async (e) => {
  e.preventDefault();
  const taskId = e.dataTransfer.getData('taskId');
  const newStatus = columnElement.dataset.status;
  await updateTaskStatus(taskId, newStatus);
});
```

## Error Handling

```javascript
async function apiCall(url, options) {
  try {
    const response = await fetch(url, options);
    
    if (response.status === 401) {
      // Unauthorized - redirect to login
      logout();
      return null;
    }
    
    if (!response.ok) {
      const error = await response.json();
      showError(error.detail || 'An error occurred');
      return null;
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    showError('Network error. Please try again.');
    return null;
  }
}

function showError(message) {
  const errorDiv = document.createElement('div');
  errorDiv.className = 'error-toast';
  errorDiv.textContent = message;
  document.body.appendChild(errorDiv);
  
  setTimeout(() => {
    errorDiv.remove();
  }, 5000);
}
```

## Deployment

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Enable gzip compression
    gzip on;
    gzip_types text/css application/javascript text/javascript;

    # Serve static files
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Docker Build

```dockerfile
FROM nginx:alpine
COPY . /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Performance Optimization

1. **Debounce Chat Input**: Prevent excessive API calls
2. **Lazy Load Tasks**: Load on scroll for large lists
3. **Cache Static Assets**: Service worker for offline support
4. **Minify Resources**: CSS/JS compression in production
5. **CDN Integration**: Serve static assets from CDN

## Accessibility

- **Keyboard Navigation**: Tab through all interactive elements
- **ARIA Labels**: Screen reader support
- **Color Contrast**: WCAG AA compliant
- **Focus Indicators**: Clear visual focus states

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Future Enhancements

- [ ] Progressive Web App (PWA) support
- [ ] Offline mode with service workers
- [ ] Real-time updates via WebSocket
- [ ] Mobile app wrapper (Capacitor/Cordova)
- [ ] Advanced task filtering and search
- [ ] Calendar view for tasks
- [ ] File attachments
- [ ] Task templates
