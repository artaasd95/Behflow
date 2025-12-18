# Frontend Tests

## Overview

Frontend tests for Behflow using Jest and Testing Library.

## Setup

```bash
npm install --save-dev jest @testing-library/dom @testing-library/jest-dom jsdom
```

## Running Tests

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Watch mode
npm test -- --watch
```

## Test Files

- `app.test.js` - Task management and chat functionality
- `auth.test.js` - Authentication flows
- `theme.test.js` - Theme switching

## Example Test

```javascript
// app.test.js
const { JSDOM } = require('jsdom');

describe('Task Management', () => {
  let dom;
  let document;

  beforeEach(() => {
    dom = new JSDOM('<!DOCTYPE html><div id="app"></div>');
    document = dom.window.document;
    global.document = document;
  });

  test('creates task element', () => {
    const task = {
      task_id: '123',
      name: 'Test Task',
      priority: 'high',
      status: 'not_started'
    };

    // Test implementation
    expect(task.name).toBe('Test Task');
  });
});
```

## Package.json Configuration

Add to `package.json`:

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  },
  "jest": {
    "testEnvironment": "jsdom",
    "coverageDirectory": "./coverage",
    "collectCoverageFrom": [
      "*.js",
      "!*.test.js"
    ]
  }
}
```

## Notes

- Frontend tests are currently configured but require Jest setup in the frontend directory
- Tests can be run after installing Jest dependencies
- Mock API calls using jest.fn() for unit tests
