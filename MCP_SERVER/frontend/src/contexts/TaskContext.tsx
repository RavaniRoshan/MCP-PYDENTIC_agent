// src/contexts/TaskContext.tsx
import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import io, { Socket } from 'socket.io-client';
import { TaskResponse } from '../types';

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
    const newSocket = io(wsUrl);
    
    newSocket.on('task_update', (data) => {
      updateTask(data.data); // The server sends the full task object in the 'data' field
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
    setTasks(prev => 
      prev.map(task => 
        task.task_id === updatedTask.task_id ? updatedTask : task
      )
    );
    
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

export const useTasks = () => {
  const context = useContext(TaskContext);
  if (context === undefined) {
    throw new Error('useTasks must be used within a TaskProvider');
  }
  return context;
};