// src/components/TaskStatusDisplay.tsx
import React from 'react';
import { TaskResponse } from '../types';
import { motion } from 'framer-motion';
import { 
  ClockIcon, 
  CheckCircleIcon, 
  XCircleIcon, 
  InformationCircleIcon,
  ArrowPathIcon 
} from '@heroicons/react/24/outline';
import { formatDate, formatTime } from '../utils/dateUtils';

/**
 * @interface TaskStatusDisplayProps
 * @description The props for the TaskStatusDisplay component.
 * @property {TaskResponse} task - The task to be displayed.
 */
interface TaskStatusDisplayProps {
  task: TaskResponse;
}

/**
 * @component TaskStatusDisplay
 * @description A component that displays the status of a single automation task.
 * @param {TaskStatusDisplayProps} props - The props for the component.
 * @returns {React.FC} The task status display component.
 */
const TaskStatusDisplay: React.FC<TaskStatusDisplayProps> = ({ task }) => {
  /**
   * @function getStatusColor
   * @description Returns the color for a given status.
   * @param {string} status - The status to get the color for.
   * @returns {string} The color class.
   */
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

  /**
   * @function getStatusIcon
   * @description Returns the icon for a given status.
   * @param {string} status - The status to get the icon for.
   * @returns {React.ReactNode} The icon.
   */
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

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm"
    >
      {/* Task header */}
      <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
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
          <div className="text-xs text-gray-500">
            {task.started_at ? formatTime(new Date(task.started_at)) : 'Just now'}
          </div>
        </div>
        <div className="mt-1 text-sm font-medium text-gray-900">
          {task.request.user_prompt.prompt}
        </div>
      </div>

      {/* Task details */}
      <div className="p-4">
        {/* Execution plan */}
        {task.plan && task.plan.actions.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-medium text-gray-900 mb-2">Execution Plan</h4>
            <div className="space-y-2">
              {task.plan.actions.map((action, index) => (
                <div key={action.id} className="flex items-start text-sm">
                  <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-blue-100 text-blue-800 text-xs font-medium mr-2">
                    {index + 1}
                  </span>
                  <div>
                    <p className="font-medium text-gray-900">{action.type}</p>
                    <p className="text-gray-600">{action.description}</p>
                    {action.element && (
                      <p className="text-xs text-gray-500">
                        Element: {action.element.type} = {action.element.value}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action results */}
        {task.results.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-2">Results</h4>
            <div className="space-y-2">
              {task.results.map((result, index) => (
                <div 
                  key={result.action_id} 
                  className={`p-3 rounded-md border ${
                    result.success 
                      ? 'bg-green-50 border-green-200' 
                      : 'bg-red-50 border-red-200'
                  }`}
                >
                  <div className="flex items-start">
                    <div className="flex-shrink-0">
                      {result.success ? (
                        <CheckCircleIcon className="h-5 w-5 text-green-500" />
                      ) : (
                        <XCircleIcon className="h-5 w-5 text-red-500" />
                      )}
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-gray-900">
                        {result.success ? 'Success' : 'Failed'}
                      </p>
                      <p className="text-sm text-gray-500">{result.result || result.error}</p>
                      {result.execution_time && (
                        <p className="text-xs text-gray-400 mt-1">
                          Execution time: {result.execution_time.toFixed(2)}s
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Error display */}
        {task.error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <div className="flex">
              <XCircleIcon className="h-5 w-5 text-red-500 flex-shrink-0" />
              <div className="ml-3">
                <p className="text-sm font-medium text-red-800">Error</p>
                <p className="text-sm text-red-700">{task.error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Execution time */}
        {task.execution_time !== undefined && (
          <div className="mt-4 pt-4 border-t border-gray-200 text-xs text-gray-500">
            Total execution time: {task.execution_time.toFixed(2)} seconds
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default TaskStatusDisplay;