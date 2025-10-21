// src/components/ChatInterface.tsx
import React, { useState, useRef, useEffect } from 'react';
import { useTasks } from '../contexts/TaskContext';
import { useAuth } from '../contexts/AuthContext';
import { TaskResponse } from '../types';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  PaperAirplaneIcon, 
  ArrowPathIcon,
  InformationCircleIcon,
  LightBulbIcon
} from '@heroicons/react/24/outline';
import TaskStatusDisplay from './TaskStatusDisplay';

const ChatInterface: React.FC = () => {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { tasks, addTask } = useTasks();
  const { user } = useAuth();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Sample automation suggestions for the interface
  const sampleSuggestions = [
    "Post this article to my LinkedIn",
    "Scrape product prices from competitor sites",
    "Schedule my content across social platforms",
    "Fill out and submit forms automatically",
    "Monitor website changes for me"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [tasks]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    setIsLoading(true);

    try {
      // Create a new task object (in a real app, this would be sent to the backend)
      const newTask: TaskResponse = {
        task_id: `task_${Date.now()}`,
        status: 'processing',
        request: {
          id: `req_${Date.now()}`,
          user_prompt: {
            prompt: input,
            priority: 'normal',
            timeout: 300
          },
          target_urls: [],
          expected_outputs: [],
          created_at: new Date()
        },
        results: [],
        started_at: new Date(),
        execution_time: 0
      };

      // Add the task to context (this simulates sending to the backend)
      addTask(newTask);
      
      // In a real app, you would send this to the backend API
      // const response = await api.createTask(input);
      // addTask(response);
      
      setInput('');
    } catch (error) {
      console.error('Error creating task:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="px-4 py-5 border-b border-gray-200 sm:px-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 w-10 h-10 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">A</span>
            </div>
            <h1 className="ml-3 text-xl font-semibold text-gray-900">AutomateAI</h1>
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <div className="flex items-center">
              <div className="w-2 h-2 rounded-full bg-green-500 mr-1"></div>
              <span>Online</span>
            </div>
          </div>
        </div>
        <p className="mt-1 text-sm text-gray-500">
          Describe any web task and I'll handle it for you. Hands-free automation.
        </p>
      </div>

      {/* Main chat area */}
      <div className="flex-1 overflow-hidden flex flex-col">
        <div className="flex-1 overflow-y-auto p-4">
          {/* Welcome message */}
          {tasks.length === 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-8 text-center"
            >
              <div className="mx-auto max-w-2xl">
                <div className="bg-gradient-to-r from-blue-500 to-purple-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <LightBulbIcon className="h-8 w-8 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">How can I help you today?</h2>
                <p className="text-gray-600 mb-8">
                  Automate any web task with simple instructions. I'll navigate, click, type, and post on your behalf.
                </p>
                
                {/* Task suggestions */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-8">
                  {sampleSuggestions.slice(0, 4).map((suggestion, index) => (
                    <motion.button
                      key={index}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="bg-white border border-gray-200 rounded-lg p-4 text-left hover:bg-gray-50 transition-colors duration-200"
                    >
                      <p className="font-medium text-gray-900">{suggestion}</p>
                    </motion.button>
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          {/* Task history */}
          <div className="space-y-4">
            {tasks.map((task) => (
              <motion.div
                key={task.task_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="chat-message"
              >
                <div className="mb-4">
                  <TaskStatusDisplay task={task} />
                </div>
              </motion.div>
            ))}
          </div>

          {/* Messages container */}
          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div className="border-t border-gray-200 bg-white p-4">
          <form onSubmit={handleSubmit} className="relative">
            <div className="flex items-end rounded-md border border-gray-300 bg-white shadow-sm focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500">
              <textarea
                rows={2}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={isLoading}
                placeholder="Describe the web task you want me to perform..."
                className="flex-1 border-0 resize-none py-2 pl-4 pr-10 focus:ring-0 sm:text-sm"
              />
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="mr-3 mb-2 flex-shrink-0 inline-flex items-center justify-center h-8 w-8 rounded-full bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {isLoading ? (
                  <ArrowPathIcon className="h-4 w-4 animate-spin" />
                ) : (
                  <PaperAirplaneIcon className="h-4 w-4" />
                )}
              </button>
            </div>
            <p className="mt-2 text-xs text-gray-500">
              AutomateAI can access and interact with any website. Describe your task in simple English.
            </p>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;