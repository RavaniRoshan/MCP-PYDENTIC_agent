// src/components/TaskHistory.tsx
import React, { useState } from 'react';
import { useTasks } from '../contexts/TaskContext';
import { TaskResponse } from '../types';
import { 
  ClockIcon, 
  CheckCircleIcon, 
  XCircleIcon, 
  InformationCircleIcon,
  ArrowPathIcon,
  FunnelIcon
} from '@heroicons/react/24/outline';

const TaskHistory: React.FC = () => {
  const { tasks } = useTasks();
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [dateFilter, setDateFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Filter tasks based on selected filters
  const filteredTasks = tasks.filter(task => {
    // Status filter
    if (statusFilter !== 'all' && task.status !== statusFilter) {
      return false;
    }
    
    // Search filter
    if (searchQuery && 
        !task.request.user_prompt.prompt.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    
    // Date filter
    if (dateFilter !== 'all' && task.started_at) {
      const taskDate = new Date(task.started_at);
      const now = new Date();
      
      switch (dateFilter) {
        case 'today':
          return taskDate.toDateString() === now.toDateString();
        case 'week':
          const oneWeekAgo = new Date();
          oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
          return taskDate >= oneWeekAgo;
        case 'month':
          const oneMonthAgo = new Date();
          oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1);
          return taskDate >= oneMonthAgo;
        default:
          return true;
      }
    }
    
    return true;
  });

  // Sort tasks by start date (newest first)
  const sortedTasks = [...filteredTasks].sort((a, b) => {
    const dateA = a.started_at ? new Date(a.started_at).getTime() : 0;
    const dateB = b.started_at ? new Date(b.started_at).getTime() : 0;
    return dateB - dateA;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-50';
      case 'failed':
        return 'text-red-600 bg-red-50';
      case 'processing':
      case 'executing':
        return 'text-blue-600 bg-blue-50';
      default:
        return 'text-yellow-600 bg-yellow-50';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case 'processing':
      case 'executing':
        return <ArrowPathIcon className="h-5 w-5 text-blue-500 animate-spin" />;
      default:
        return <ClockIcon className="h-5 w-5 text-yellow-500" />;
    }
  };

  const statusOptions = [
    { value: 'all', label: 'All Statuses' },
    { value: 'pending', label: 'Pending' },
    { value: 'processing', label: 'Processing' },
    { value: 'completed', label: 'Completed' },
    { value: 'failed', label: 'Failed' },
  ];

  const dateOptions = [
    { value: 'all', label: 'All Time' },
    { value: 'today', label: 'Today' },
    { value: 'week', label: 'Last 7 Days' },
    { value: 'month', label: 'Last 30 Days' },
  ];

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="px-4 py-5 border-b border-gray-200 sm:px-6">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold text-gray-900">Task History</h1>
          <div className="flex items-center space-x-2">
            <div className="relative rounded-md shadow-sm">
              <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                <InformationCircleIcon className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search tasks..."
                className="block w-full rounded-md border-gray-300 py-2 pl-10 pr-12 focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              />
            </div>
          </div>
        </div>
        <p className="mt-1 text-sm text-gray-500">
          Browse through your completed automation tasks and their outcomes.
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-4 space-y-4 sm:space-y-0">
          <div className="flex items-center">
            <FunnelIcon className="h-5 w-5 text-gray-400 mr-2" />
            <span className="text-sm font-medium text-gray-700 mr-2">Filter by:</span>
          </div>
          
          <div className="flex flex-wrap gap-4">
            <div>
              <label htmlFor="status-filter" className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                id="status-filter"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              >
                {statusOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label htmlFor="date-filter" className="block text-sm font-medium text-gray-700 mb-1">
                Date
              </label>
              <select
                id="date-filter"
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              >
                {dateOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Task list */}
      <div className="flex-1 overflow-y-auto p-4">
        {sortedTasks.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-center">
            <ClockIcon className="h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-1">No tasks found</h3>
            <p className="text-gray-500">
              {tasks.length === 0 
                ? "You haven't created any tasks yet."
                : "No tasks match your current filters."
              }
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {sortedTasks.map((task) => (
              <div 
                key={task.task_id} 
                className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow duration-200"
              >
                <div className="px-4 py-5 sm:p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className={getStatusColor(task.status)}>
                        <div className="flex items-center px-2 py-1 rounded-full text-xs font-medium">
                          {getStatusIcon(task.status)}
                          <span className="ml-1 capitalize">{task.status.replace('_', ' ')}</span>
                        </div>
                      </div>
                      {task.request.user_prompt.priority !== 'normal' && (
                        <span className="ml-2 px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">
                          {task.request.user_prompt.priority}
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-gray-500">
                      {task.started_at ? new Date(task.started_at).toLocaleString() : 'N/A'}
                    </div>
                  </div>
                  
                  <h3 className="mt-3 text-lg font-medium text-gray-900">
                    {task.request.user_prompt.prompt}
                  </h3>
                  
                  <div className="mt-4 flex items-center justify-between">
                    <div className="text-sm text-gray-500">
                      {task.results.length} actions • {task.execution_time ? `${task.execution_time.toFixed(2)}s` : 'N/A'}
                    </div>
                    
                    <div className="flex space-x-2">
                      <button className="text-sm font-medium text-blue-600 hover:text-blue-500">
                        View Details
                      </button>
                    </div>
                  </div>
                  
                  {task.error && (
                    <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-md">
                      <div className="flex">
                        <XCircleIcon className="h-5 w-5 text-red-500 flex-shrink-0" />
                        <div className="ml-3">
                          <p className="text-sm text-red-700 truncate">{task.error}</p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default TaskHistory;