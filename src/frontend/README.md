# Behflow Frontend

A modern task management and chat interface with Atom One Dark Pro theme support.

## Features

- **Authentication**: Login and registration pages
- **Task Management**: View tasks grouped by status (Not Started, In Progress, Completed, Blocked)
- **Chat Interface**: Interactive chat assistant with markdown support
- **Theme Switching**: Toggle between dark and light themes
- **Responsive Design**: Works on desktop and mobile devices

## Files

- `index.html` - Main application page
- `login.html` - Login page
- `register.html` - Registration page
- `styles.css` - Atom One Dark Pro theme styling
- `app.js` - Main application logic (tasks & chat)
- `login.js` - Login functionality
- `register.js` - Registration functionality
- `theme.js` - Theme management

## Setup

1. **Configure API Endpoint**: Update `API_BASE_URL` in the JavaScript files to point to your backend (Docker maps backend 8000 -> host 8010):
   ```javascript
   const API_BASE_URL = 'http://localhost:8010';
   ```

2. **Serve the Files**: Use a web server to serve the static files. For example:
   ```bash
   # Using Python
   python -m http.server 3000
   
   # Using Node.js (http-server)
   npx http-server -p 3000
   ```

3. **Access the Application**: Open your browser to `http://localhost:3000`

## Theme

The application uses the **Atom One Dark Pro** color scheme with the following palette:

- **Background**: `#282c34` (dark) / `#fafafa` (light)
- **Foreground**: `#abb2bf` (dark) / `#2c313c` (light)
- **Accent Blue**: `#528bff`
- **Accent Red**: `#e06c75`
- **Accent Green**: `#98c379`
- **Accent Yellow**: `#e5c07b`
- **Accent Purple**: `#c678dd`
- **Accent Cyan**: `#56b6c2`

## API Endpoints Expected

The frontend expects the following backend API endpoints:

### Authentication
- `POST /api/v1/auth/login` - Login with username and password
- `POST /api/v1/auth/register` - Register new user

### Chat
- `POST /api/v1/chat` - Send a chat message
- `GET /api/v1/chat/history` - Get chat history
- `GET /api/v1/tasks` - Get user tasks

## Usage

1. **Login/Register**: Start by creating an account or logging in
2. **View Tasks**: Tasks are displayed on the left panel, grouped by status
3. **Chat**: Use the chat panel on the right to interact with the AI assistant
4. **Theme Toggle**: Click the theme button in the header to switch between dark/light mode
5. **Logout**: Click the logout button to end your session

## Dependencies

- [Marked.js](https://marked.js.org/) - Markdown parsing (loaded via CDN)

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Customization

### Changing Colors
Edit the CSS variables in `styles.css`:
```css
:root {
  --bg-primary: #282c34;
  --accent-blue: #528bff;
  /* ... other colors */
}
```

### Adjusting Panel Sizes
Modify the flex properties in `styles.css`:
```css
.tasks-panel {
  flex: 0 0 70%;  /* Change this percentage */
}

.chat-panel {
  flex: 0 0 30%;  /* Change this percentage */
}
```
