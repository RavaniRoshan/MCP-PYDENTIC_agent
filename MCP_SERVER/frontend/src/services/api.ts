// src/services/api.ts
import axios from 'axios';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
});

// Request interceptor to add auth headers if needed
api.interceptors.request.use(
  (config) => {
    // If we had authentication tokens, we would add them here
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export default api;

// API functions for task management
export const taskApi = {
  // Create a new task
  createTask: async (prompt: string, priority: 'low' | 'normal' | 'high' | 'critical' = 'normal') => {
    const response = await api.post('/prompt', {
      prompt,
      priority,
      timeout: 300
    });
    return response.data;
  },

  // Get a specific task by ID
  getTask: async (taskId: string) => {
    const response = await api.get(`/tasks/${taskId}`);
    return response.data;
  },

  // Get all tasks
  getAllTasks: async () => {
    const response = await api.get('/tasks');
    return response.data;
  },

  // Execute a browser action
  executeAction: async (action: any) => {
    const response = await api.post('/execute', action);
    return response.data;
  },

  // Get current browser state
  getBrowserState: async () => {
    const response = await api.get('/observe');
    return response.data;
  }
};

// API functions for social media scheduler
export const socialMediaApi = {
  // Authenticate a social media account
  authenticateAccount: async (credentials: {
    platform: string;
    username: string;
    password?: string;
    access_token?: string;
  }) => {
    const response = await api.post('/social/authenticate', credentials);
    return response.data;
  },

  // Post content to social media platforms
  postToSocialMedia: async (content: any, platforms: string[]) => {
    const response = await api.post('/social/post', {
      ...content,
      platforms
    });
    return response.data;
  },

  // Schedule a social media post
  schedulePost: async (content: any, platforms: string[], scheduledTime: string) => {
    const response = await api.post('/social/schedule', {
      ...content,
      platforms,
      scheduled_time: scheduledTime
    });
    return response.data;
  },

  // Execute a social media task
  executeSocialMediaTask: async (taskRequest: any) => {
    const response = await api.post('/social/task', taskRequest);
    return response.data;
  },

  // Get scheduled posts
  getScheduledPosts: async () => {
    const response = await api.get('/social/scheduled');
    return response.data;
  },

  // Get a specific scheduled post
  getScheduledPost: async (postId: string) => {
    const response = await api.get(`/social/scheduled/${postId}`);
    return response.data;
  }
};