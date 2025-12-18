# Integration Guide

## Overview

This guide explains how to integrate Behflow with external services, tools, and platforms. Behflow provides flexible integration options through APIs, webhooks, and SDK support.

## API Integration

### REST API Client

#### Python Client

```python
import requests
from typing import Optional, Dict, List

class BehflowClient:
    """Python client for Behflow API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
    
    def login(self, username: str, password: str) -> Dict:
        """Authenticate and store token"""
        response = requests.post(
            f"{self.base_url}/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        self.token = data["token"]
        return data
    
    def create_task(self, name: str, description: str = "", priority: str = "medium") -> Dict:
        """Create a new task"""
        response = requests.post(
            f"{self.base_url}/api/v1/tasks",
            headers={"Authorization": self.token},
            json={"name": name, "description": description, "priority": priority}
        )
        response.raise_for_status()
        return response.json()
    
    def list_tasks(self, status: Optional[str] = None) -> List[Dict]:
        """List all tasks"""
        params = {"status": status} if status else {}
        response = requests.get(
            f"{self.base_url}/api/v1/tasks",
            headers={"Authorization": self.token},
            params=params
        )
        response.raise_for_status()
        return response.json()["tasks"]
    
    def chat(self, message: str, session_id: Optional[str] = None) -> Dict:
        """Send a chat message"""
        response = requests.post(
            f"{self.base_url}/api/v1/chat",
            headers={"Authorization": self.token},
            json={"message": message, "session_id": session_id}
        )
        response.raise_for_status()
        return response.json()

# Usage
client = BehflowClient()
client.login("username", "password")
task = client.create_task("Review integration guide", priority="high")
response = client.chat("Show me all high priority tasks")
```

#### Node.js Client

```javascript
const axios = require('axios');

class BehflowClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
    this.token = null;
  }

  async login(username, password) {
    const response = await axios.post(`${this.baseUrl}/login`, {
      username,
      password
    });
    this.token = response.data.token;
    return response.data;
  }

  async createTask(name, description = '', priority = 'medium') {
    const response = await axios.post(
      `${this.baseUrl}/api/v1/tasks`,
      { name, description, priority },
      { headers: { Authorization: this.token } }
    );
    return response.data;
  }

  async listTasks(status = null) {
    const params = status ? { status } : {};
    const response = await axios.get(
      `${this.baseUrl}/api/v1/tasks`,
      {
        headers: { Authorization: this.token },
        params
      }
    );
    return response.data.tasks;
  }

  async chat(message, sessionId = null) {
    const response = await axios.post(
      `${this.baseUrl}/api/v1/chat`,
      { message, session_id: sessionId },
      { headers: { Authorization: this.token } }
    );
    return response.data;
  }
}

// Usage
const client = new BehflowClient();
await client.login('username', 'password');
const task = await client.createTask('Review integration guide', '', 'high');
const response = await client.chat('Show me all high priority tasks');
```

## Calendar Integration

### Google Calendar

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta

class GoogleCalendarIntegration:
    """Sync Behflow tasks with Google Calendar"""
    
    def __init__(self, credentials: Credentials):
        self.service = build('calendar', 'v3', credentials=credentials)
    
    def create_event_from_task(self, task: Dict) -> str:
        """Create a Google Calendar event from a Behflow task"""
        event = {
            'summary': task['name'],
            'description': task['description'],
            'start': {
                'dateTime': task['due_date'],
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': (datetime.fromisoformat(task['due_date']) + timedelta(hours=1)).isoformat(),
                'timeZone': 'UTC',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 30},
                ],
            },
        }
        
        event = self.service.events().insert(calendarId='primary', body=event).execute()
        return event['id']
    
    def sync_tasks_to_calendar(self, tasks: List[Dict]):
        """Sync all tasks with due dates to Google Calendar"""
        for task in tasks:
            if task.get('due_date'):
                self.create_event_from_task(task)
```

### Outlook Calendar

```python
import requests

class OutlookCalendarIntegration:
    """Sync tasks with Outlook Calendar"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://graph.microsoft.com/v1.0"
    
    def create_event_from_task(self, task: Dict) -> Dict:
        """Create an Outlook event from a task"""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        event = {
            'subject': task['name'],
            'body': {
                'contentType': 'HTML',
                'content': task['description']
            },
            'start': {
                'dateTime': task['due_date'],
                'timeZone': 'UTC'
            },
            'end': {
                'dateTime': (datetime.fromisoformat(task['due_date']) + timedelta(hours=1)).isoformat(),
                'timeZone': 'UTC'
            }
        }
        
        response = requests.post(
            f"{self.base_url}/me/events",
            headers=headers,
            json=event
        )
        return response.json()
```

## Notification Services

### Slack Integration

```python
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SlackIntegration:
    """Send Behflow notifications to Slack"""
    
    def __init__(self, token: str, channel: str):
        self.client = WebClient(token=token)
        self.channel = channel
    
    def send_task_notification(self, task: Dict, action: str):
        """Send task notification to Slack"""
        message = self._format_task_message(task, action)
        
        try:
            response = self.client.chat_postMessage(
                channel=self.channel,
                blocks=[
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"Task {action.capitalize()}"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Task:*\n{task['name']}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Priority:*\n{task['priority']}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Status:*\n{task['status']}"
                            }
                        ]
                    }
                ]
            )
            return response
        except SlackApiError as e:
            print(f"Error sending message: {e.response['error']}")
    
    def _format_task_message(self, task: Dict, action: str) -> str:
        return f"Task '{task['name']}' was {action}"
```

### Discord Integration

```python
import discord
from discord import Webhook
import aiohttp

class DiscordIntegration:
    """Send notifications to Discord"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def send_task_notification(self, task: Dict, action: str):
        """Send task notification to Discord"""
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(self.webhook_url, session=session)
            
            embed = discord.Embed(
                title=f"Task {action.capitalize()}",
                description=task['name'],
                color=discord.Color.blue()
            )
            embed.add_field(name="Priority", value=task['priority'], inline=True)
            embed.add_field(name="Status", value=task['status'], inline=True)
            
            if task.get('due_date'):
                embed.add_field(name="Due Date", value=task['due_date'], inline=False)
            
            await webhook.send(embed=embed)
```

### Email Notifications

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailIntegration:
    """Send email notifications"""
    
    def __init__(self, smtp_host: str, smtp_port: int, username: str, password: str):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
    
    def send_task_notification(self, to_email: str, task: Dict, action: str):
        """Send task notification email"""
        message = MIMEMultipart('alternative')
        message['Subject'] = f"Behflow: Task {action.capitalize()}"
        message['From'] = self.username
        message['To'] = to_email
        
        html_content = f"""
        <html>
          <body>
            <h2>Task {action.capitalize()}</h2>
            <p><strong>Task:</strong> {task['name']}</p>
            <p><strong>Description:</strong> {task['description']}</p>
            <p><strong>Priority:</strong> {task['priority']}</p>
            <p><strong>Status:</strong> {task['status']}</p>
            {f"<p><strong>Due Date:</strong> {task['due_date']}</p>" if task.get('due_date') else ""}
          </body>
        </html>
        """
        
        html_part = MIMEText(html_content, 'html')
        message.attach(html_part)
        
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(message)
```

## Project Management Tools

### Jira Integration

```python
from jira import JIRA

class JiraIntegration:
    """Sync tasks with Jira"""
    
    def __init__(self, server: str, email: str, api_token: str):
        self.jira = JIRA(server=server, basic_auth=(email, api_token))
    
    def create_jira_issue_from_task(self, task: Dict, project_key: str) -> str:
        """Create a Jira issue from a Behflow task"""
        issue_dict = {
            'project': {'key': project_key},
            'summary': task['name'],
            'description': task['description'],
            'issuetype': {'name': 'Task'},
            'priority': {'name': self._map_priority(task['priority'])},
        }
        
        if task.get('due_date'):
            issue_dict['duedate'] = task['due_date'].split('T')[0]
        
        new_issue = self.jira.create_issue(fields=issue_dict)
        return new_issue.key
    
    def _map_priority(self, behflow_priority: str) -> str:
        """Map Behflow priority to Jira priority"""
        mapping = {
            'urgent': 'Highest',
            'high': 'High',
            'medium': 'Medium',
            'low': 'Low'
        }
        return mapping.get(behflow_priority, 'Medium')
    
    def sync_task_status(self, jira_issue_key: str, behflow_status: str):
        """Update Jira issue status based on Behflow task status"""
        transitions = {
            'not_started': 'To Do',
            'in_progress': 'In Progress',
            'completed': 'Done',
            'blocked': 'Blocked'
        }
        
        target_status = transitions.get(behflow_status)
        if target_status:
            self.jira.transition_issue(jira_issue_key, target_status)
```

### Trello Integration

```python
from trello import TrelloClient

class TrelloIntegration:
    """Sync tasks with Trello"""
    
    def __init__(self, api_key: str, token: str):
        self.client = TrelloClient(api_key=api_key, token=token)
    
    def create_card_from_task(self, task: Dict, board_id: str, list_name: str):
        """Create a Trello card from a Behflow task"""
        board = self.client.get_board(board_id)
        
        # Find the list
        target_list = None
        for lst in board.list_lists():
            if lst.name == list_name:
                target_list = lst
                break
        
        if not target_list:
            raise ValueError(f"List '{list_name}' not found")
        
        # Create card
        card = target_list.add_card(
            name=task['name'],
            desc=task['description']
        )
        
        # Add label based on priority
        priority_colors = {
            'urgent': 'red',
            'high': 'orange',
            'medium': 'yellow',
            'low': 'green'
        }
        color = priority_colors.get(task['priority'], 'yellow')
        for label in board.get_labels():
            if label.color == color:
                card.add_label(label)
                break
        
        # Set due date
        if task.get('due_date'):
            card.set_due(task['due_date'])
        
        return card.id
```

## Webhook Integration

### Outgoing Webhooks

Configure Behflow to send events to external services:

```python
# backend/app/webhooks.py

import requests
from typing import Dict, List
import os

class WebhookManager:
    """Manage outgoing webhooks"""
    
    def __init__(self):
        self.webhooks: List[str] = self._load_webhooks()
    
    def _load_webhooks(self) -> List[str]:
        """Load webhook URLs from configuration"""
        webhook_urls = os.getenv('WEBHOOK_URLS', '')
        return [url.strip() for url in webhook_urls.split(',') if url.strip()]
    
    def trigger_event(self, event_type: str, data: Dict):
        """Send webhook event to all registered URLs"""
        payload = {
            'event': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }
        
        for webhook_url in self.webhooks:
            try:
                requests.post(
                    webhook_url,
                    json=payload,
                    timeout=5,
                    headers={'Content-Type': 'application/json'}
                )
            except Exception as e:
                logger.error(f"Failed to send webhook to {webhook_url}: {e}")
    
    def on_task_created(self, task: Dict):
        """Trigger webhook when task is created"""
        self.trigger_event('task.created', task)
    
    def on_task_updated(self, task: Dict):
        """Trigger webhook when task is updated"""
        self.trigger_event('task.updated', task)
    
    def on_task_completed(self, task: Dict):
        """Trigger webhook when task is completed"""
        self.trigger_event('task.completed', task)
```

### Incoming Webhooks

Accept events from external services:

```python
# backend/app/api/routers/webhooks.py

from fastapi import APIRouter, Request, HTTPException
import hmac
import hashlib

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify webhook signature"""
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

@router.post("/github")
async def github_webhook(request: Request):
    """Handle GitHub webhooks"""
    signature = request.headers.get('X-Hub-Signature-256', '').replace('sha256=', '')
    payload = await request.body()
    
    secret = os.getenv('GITHUB_WEBHOOK_SECRET')
    if not verify_signature(payload, signature, secret):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    event = request.headers.get('X-GitHub-Event')
    data = await request.json()
    
    # Handle different GitHub events
    if event == 'issues':
        handle_github_issue(data)
    elif event == 'pull_request':
        handle_github_pr(data)
    
    return {"status": "success"}
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/sync-issues.yml

name: Sync GitHub Issues to Behflow

on:
  issues:
    types: [opened, edited, closed]

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Sync to Behflow
        run: |
          curl -X POST ${{ secrets.BEHFLOW_API_URL }}/api/v1/tasks \
            -H "Authorization: ${{ secrets.BEHFLOW_TOKEN }}" \
            -H "Content-Type: application/json" \
            -d '{
              "name": "${{ github.event.issue.title }}",
              "description": "${{ github.event.issue.body }}",
              "priority": "medium",
              "tags": ["github", "issue-${{ github.event.issue.number }}"]
            }'
```

### Jenkins Integration

```groovy
// Jenkinsfile

pipeline {
    agent any
    
    environment {
        BEHFLOW_API = 'http://behflow.example.com'
        BEHFLOW_TOKEN = credentials('behflow-token')
    }
    
    stages {
        stage('Create Build Task') {
            steps {
                script {
                    sh """
                        curl -X POST ${BEHFLOW_API}/api/v1/tasks \
                            -H "Authorization: ${BEHFLOW_TOKEN}" \
                            -H "Content-Type: application/json" \
                            -d '{
                                "name": "Build ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                                "description": "Build started at ${env.BUILD_TIMESTAMP}",
                                "priority": "high"
                            }'
                    """
                }
            }
        }
        
        stage('Build') {
            steps {
                // Build steps
                echo 'Building...'
            }
        }
        
        stage('Update Task') {
            steps {
                script {
                    sh """
                        curl -X PUT ${BEHFLOW_API}/api/v1/tasks/\${TASK_ID} \
                            -H "Authorization: ${BEHFLOW_TOKEN}" \
                            -H "Content-Type: application/json" \
                            -d '{"status": "completed"}'
                    """
                }
            }
        }
    }
}
```

## Mobile Integration

### iOS Shortcuts

```json
{
  "shortcut": {
    "name": "Add Behflow Task",
    "actions": [
      {
        "type": "ask_for_input",
        "question": "What's the task?",
        "input_type": "text"
      },
      {
        "type": "http_request",
        "method": "POST",
        "url": "http://your-behflow-instance.com/api/v1/tasks",
        "headers": {
          "Authorization": "YOUR_TOKEN",
          "Content-Type": "application/json"
        },
        "body": {
          "name": "{{input}}",
          "priority": "medium"
        }
      }
    ]
  }
}
```

### Android Tasker

```javascript
// Tasker Task
var taskName = global('TASK_NAME');
var priority = global('TASK_PRIORITY');

var url = 'http://your-behflow-instance.com/api/v1/tasks';
var headers = {
    'Authorization': 'YOUR_TOKEN',
    'Content-Type': 'application/json'
};
var body = JSON.stringify({
    name: taskName,
    priority: priority || 'medium'
});

// HTTP POST
httpPost(url, body, headers);
```

## Future Integration Plans

- [ ] Zapier integration
- [ ] IFTTT support
- [ ] Notion database sync
- [ ] Asana bidirectional sync
- [ ] Microsoft Teams bot
- [ ] Telegram bot
- [ ] Apple Reminders sync
- [ ] Google Tasks integration
