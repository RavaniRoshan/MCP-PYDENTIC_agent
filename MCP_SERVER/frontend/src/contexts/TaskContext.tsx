// src/contexts/TaskContext.tsx
import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import io, { Socket } from 'socket.io-client';
import { TaskResponse } from '../types';

/**
 * @interface TaskContextType
 * @description The context for managing tasks.
 * @property {TaskResponse[]} tasks - A list of all tasks.
 * @property {TaskResponse | null} activeTask - The currently active task.
 * @property {(task: TaskResponse) => void} addTask - A function to add a new task.
 * @property {(task: TaskResponse) => void} updateTask - A function to update an existing task.
 * @property {(task: TaskResponse | null) => void} setActiveTask - A function to set the active task.
 * @property {() => void} connectWebSocket - A function to connect to the WebSocket.
 * @property {() => void} disconnectWebSocket - A function to disconnect from the WebSocket.
 */
interface TaskContextType {
  tasks: TaskResponse[];
  activeTask: TaskResponse | null;
  addTask: (task: TaskResponse) => void;
  updateTask: (task: TaskResponse) => void;
  setActiveTask: (task: TaskResponse | null) => void;
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
}

const TaskContext = createContext<TaskContextType | undefined>(undefined);

/**
 * @provider TaskProvider
 * @description A provider for the task context.
 * @param {{ children: ReactNode }} props - The props for the component.
 * @returns {React.FC} The task provider.
 */
export const TaskProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [tasks, setTasks] = useState<TaskResponse[]>([]);
  const [activeTask, setActiveTask] = useState<TaskResponse | null>(null);
  const [socket, setSocket] = useState<Socket | null>(null);

  // Connect to WebSocket when component mounts
  useEffect(() => {
    connectWebSocket();
    return () => {
      disconnectWebSocket();
    };
  }, []);

  const connectWebSocket = () => {
    // Replace with your actual backend URL
    const wsUrl = process.env.REACT_APP_WS_URL || 'http://localhost:8000';
    const newSocket = io(wsUrl, {
      transports: ['websocket'], // Use only WebSocket transport
      // Additional configuration options
      timeout: 20000,
      autoConnect: true,
    });
    
    newSocket.on('connect', () => {
      console.log('Connected to WebSocket server');
    });
    
    newSocket.on('disconnect', (reason) => {
      console.log('Disconnected from WebSocket server:', reason);
    });
    
    newSocket.on('task_update', (data) => {
      updateTask(data); // Update task with the received data
      console.log('Task updated via WebSocket:', data);
    });

    newSocket.on('error', (error) => {
      console.error('WebSocket error:', error);
    });

    setSocket(newSocket);
  };

  const disconnectWebSocket = () => {
    if (socket) {
      socket.close();
      setSocket(null);
    }
  };

  const addTask = (task: TaskResponse) => {
    setTasks(prev => [...prev, task]);
  };

  const updateTask = (updatedTask: TaskResponse) => {
    setTasks(prev => {
      // Check if task already exists
      const taskExists = prev.some(task => task.task_id === updatedTask.task_id);
      
      if (taskExists) {
        // Update existing task
        return prev.map(task => 
          task.task_id === updatedTask.task_id ? updatedTask : task
        );
      } else {
        // Add new task
        return [updatedTask, ...prev];
      }
    });
    
    // If this is the active task, update it too
    if (activeTask && activeTask.task_id === updatedTask.task_id) {
      setActiveTask(updatedTask);
    }
  };

  return (
    <TaskContext.Provider 
      value={{ 
        tasks, 
        activeTask, 
        addTask, 
        updateTask, 
        setActiveTask,
        connectWebSocket,
        disconnectWebSocket
      }}
    >
      {children}
    </TaskContext.Provider>
  );
};

/**
 * @hook useTasks
 * @description A hook to use the task context.
 * @returns {TaskContextType} The task context.
 */
export const useTasks = () => {
  const context = useContext(TaskContext);
  if (context === undefined) {
    throw new Error('useTasks must be used within a TaskProvider');
  }
  return context;
};