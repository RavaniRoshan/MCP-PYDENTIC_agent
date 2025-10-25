# AutomateAI Frontend Documentation

## Overview
The AutomateAI frontend is a React-based user interface that provides a modern, interactive experience for users to interact with the AutomateAI backend services. It features a sleek chat interface similar to ChatGPT, with additional capabilities for task management, scheduling, and social media automation.

## Architecture

### Tech Stack
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **React Router** for navigation
- **Framer Motion** for animations
- **Headless UI** for accessible components
- **Heroicons** for icons
- **Socket.io-client** for real-time updates
- **Axios** for API requests
- **Date-fns** for date handling

### Project Structure
```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/     # React components
│   ├── contexts/       # React Context providers
│   ├── services/       # API service layer
│   ├── types/          # TypeScript type definitions
│   ├── utils/          # Utility functions
│   ├── App.tsx         # Main application component
│   ├── index.tsx       # Entry point
│   └── index.css       # Global styles
├── package.json
├── .env               # Environment variables
└── ...                # Configuration files
```

## Components

### Core Components
1. **Layout.tsx** - Main layout with sidebar navigation
2. **ChatInterface.tsx** - Primary interface for task creation
3. **Dashboard.tsx** - Task statistics and analytics
4. **TaskHistory.tsx** - Historical task records
5. **TaskScheduler.tsx** - Task scheduling interface
6. **AutomationSuggestions.tsx** - Pre-built automation templates
7. **SocialMediaScheduler.tsx** - Social media posting interface
8. **Settings.tsx** - Application settings
9. **TaskStatusDisplay.tsx** - Individual task status view

### Context Providers
1. **AuthContext.tsx** - User authentication state
2. **TaskContext.tsx** - Task management state with WebSocket integration

## API Integration

### Service Layer
The frontend includes a comprehensive API service layer in `src/services/api.ts`:

```typescript
// Core task management API
const taskApi = {
  createTask: (prompt, priority) => api.post('/prompt', { prompt, priority }),
  getTask: (taskId) => api.get(`/tasks/${taskId}`),
  getAllTasks: () => api.get('/tasks'),
  executeAction: (action) => api.post('/execute', action),
  getBrowserState: () => api.get('/observe')
}

// Social media scheduler API
const socialMediaApi = {
  authenticateAccount: (credentials) => api.post('/social/authenticate', credentials),
  postToSocialMedia: (content, platforms) => api.post('/social/post', { ...content, platforms }),
  schedulePost: (content, platforms, scheduledTime) => api.post('/social/schedule', { ...content, platforms, scheduled_time: scheduledTime }),
  executeSocialMediaTask: (taskRequest) => api.post('/social/task', taskRequest),
  getScheduledPosts: () => api.get('/social/scheduled')
}
```

### Date Handling
The application includes a utility (`src/utils/dateUtils.ts`) for proper date conversion between API responses and UI display:
- `parseAPIDate()` - Convert API date strings to Date objects
- `formatDate()` - Format dates for display
- `formatTime()` - Format time only

## Type Safety

The application uses comprehensive TypeScript definitions in `src/types/index.ts`:
- API response interfaces with conversion functions
- Internal application interfaces
- Type guards and converters for API responses

## Real-time Updates

The application uses WebSocket connections through Socket.io for real-time task updates:
- Automatic connection/disconnection handling
- Task status updates in real-time
- Error handling for connection issues

## Key Features

### 1. Chat Interface
- Natural language task creation
- Real-time task status updates
- Sample automation suggestions
- Responsive design for all devices

### 2. Social Media Scheduler
- Cross-platform posting (LinkedIn, Twitter/X, etc.)
- Content formatting with hashtags, mentions, links
- Scheduling functionality
- Real-time status updates

### 3. Task Management
- Dashboard with task statistics
- Historical task records with filtering
- Task scheduling for recurring automations
- Status tracking and analytics

### 4. Responsive Design
- Mobile-first approach
- Responsive sidebar navigation
- Adaptive grid layouts
- Touch-friendly interface elements

## Environment Configuration

The application uses environment variables defined in `.env`:
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

## Installation & Running

### Prerequisites
- Node.js (16.x or higher)
- npm or yarn package manager

### Setup
1. Navigate to the frontend directory:
   ```bash
   cd MCP_SERVER/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```
   The application will be available at `http://localhost:3000`

### Production Build
To create a production build:
```bash
npm run build
```

## API Communication

### Request Flow
1. User interacts with UI
2. Components call API service functions
3. Services make HTTP requests to backend
4. WebSocket connections receive real-time updates
5. Context providers update application state
6. Components re-render with new data

### Error Handling
- Graceful fallback for API errors
- User-friendly error messages
- Offline capability indicators
- Connection status indicators

## Customization

### Theming
The application uses Tailwind CSS for styling, allowing easy customization:
- Primary colors defined in tailwind.config.js
- Component-specific styling classes
- Responsive design utilities

### Components
- Reusable component architecture
- Props-based customization
- Context-based state management
- TypeScript interface definitions

## Security Considerations

### Client Security
- Input sanitization
- Safe API communication
- Environment variable management
- Secure WebSocket connections

### Data Handling
- Client-side data encryption for sensitive information
- Secure authentication flow
- Proper error message sanitization

## Troubleshooting

### Common Issues
1. **API connection errors**: Verify backend server is running on configured port
2. **WebSocket issues**: Check network connectivity and server status
3. **Build errors**: Run `npm install` to reinstall dependencies
4. **CORS errors**: Backend should have proper CORS configuration

### Debugging Tips
- Use browser developer tools for API inspection
- Check console for error messages
- Verify environment variable configuration
- Confirm backend endpoints are accessible

## Development Guidelines

### Code Style
- Consistent TypeScript interfaces
- Component-based architecture
- Context for state management
- Proper error handling
- Responsive design principles

### Best Practices
- Type-safe API interactions
- Efficient state updates
- Proper cleanup of subscriptions
- Accessible UI components
- Performance optimization

---

This documentation covers the current state of the AutomateAI frontend as implemented for the validation product and integration with the backend services.