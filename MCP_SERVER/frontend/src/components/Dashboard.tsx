// src/components/Dashboard.tsx
import React, { useState } from 'react';
import { useTasks } from '../contexts/TaskContext';
import { TaskResponse } from '../types';
import { motion } from 'framer-motion';
import { 
  ChartBarIcon, 
  ClockIcon, 
  CheckCircleIcon, 
  XCircleIcon,
  ArrowTrendingUpIcon,
  CpuChipIcon
} from '@heroicons/react/24/outline';

/**
 * @component Dashboard
 * @description A component that displays a dashboard with statistics and recent activity for automation tasks.
 * @returns {React.FC} The dashboard component.
 */
const Dashboard: React.FC = () => {
  const { tasks } = useTasks();
  const [timeRange, setTimeRange] = useState<'day' | 'week' | 'month'>('week');

  // Calculate statistics
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter(t => t.status === 'completed').length;
  const failedTasks = tasks.filter(t => t.status === 'failed').length;
  const successRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  // Get tasks for the selected time range
  const now = new Date();
  const filteredTasks = tasks.filter(task => {
    if (!task.started_at) return true;
    const taskDate = new Date(task.started_at);
    
    switch (timeRange) {
      case 'day':
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
  });

  // Status distribution
  const statusDistribution = {
    pending: tasks.filter(t => t.status === 'pending').length,
    processing: tasks.filter(t => t.status === 'processing' || t.status === 'executing').length,
    completed: completedTasks,
    failed: failedTasks,
  };

  // Recent tasks
  const recentTasks = [...tasks]
    .sort((a, b) => new Date(b.started_at || 0).getTime() - new Date(a.started_at || 0).getTime())
    .slice(0, 5);

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="px-4 py-5 border-b border-gray-200 sm:px-6">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold text-gray-900">Dashboard</h1>
          <div className="flex items-center space-x-2">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value as any)}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            >
              <option value="day">Last 24 hours</option>
              <option value="week">Last 7 days</option>
              <option value="month">Last 30 days</option>
            </select>
          </div>
        </div>
        <p className="mt-1 text-sm text-gray-500">
          Overview of your automation tasks and performance.
        </p>
      </div>

      {/* Stats overview */}
      <div className="p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white overflow-hidden shadow rounded-lg"
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className="bg-blue-100 p-3 rounded-md">
                  <ChartBarIcon className="h-6 w-6 text-blue-600" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Total Tasks</dt>
                    <dd className="flex items-baseline">
                      <div className="text-2xl font-semibold text-gray-900">{totalTasks}</div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white overflow-hidden shadow rounded-lg"
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className="bg-green-100 p-3 rounded-md">
                  <CheckCircleIcon className="h-6 w-6 text-green-600" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Completed</dt>
                    <dd className="flex items-baseline">
                      <div className="text-2xl font-semibold text-gray-900">{completedTasks}</div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white overflow-hidden shadow rounded-lg"
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className="bg-red-100 p-3 rounded-md">
                  <XCircleIcon className="h-6 w-6 text-red-600" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Failed</dt>
                    <dd className="flex items-baseline">
                      <div className="text-2xl font-semibold text-gray-900">{failedTasks}</div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white overflow-hidden shadow rounded-lg"
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className={`p-3 rounded-md ${
                  successRate >= 80 ? 'bg-green-100' : 
                  successRate >= 60 ? 'bg-yellow-100' : 'bg-red-100'
                }`}>
                  <ArrowTrendingUpIcon className={`h-6 w-6 ${
                    successRate >= 80 ? 'text-green-600' : 
                    successRate >= 60 ? 'text-yellow-600' : 'text-red-600'
                  }`} />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Success Rate</dt>
                    <dd className="flex items-baseline">
                      <div className="text-2xl font-semibold text-gray-900">{successRate}%</div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Charts and recent activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Status Distribution */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Task Status Distribution</h2>
            <div className="space-y-4">
              {Object.entries(statusDistribution).map(([status, count]) => (
                <div key={status} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-2 ${
                      status === 'completed' ? 'bg-green-500' :
                      status === 'failed' ? 'bg-red-500' :
                      status === 'processing' ? 'bg-blue-500' : 'bg-yellow-500'
                    }`}></div>
                    <span className="text-sm font-medium text-gray-700 capitalize">{status}</span>
                  </div>
                  <span className="text-sm text-gray-900">{count}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Tasks */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Tasks</h2>
            <div className="flow-root">
              <ul className="divide-y divide-gray-200">
                {recentTasks.length > 0 ? (
                  recentTasks.map((task) => (
                    <li key={task.task_id} className="py-4">
                      <div className="flex items-center space-x-4">
                        <div className={`flex-shrink-0 h-5 w-5 rounded-full ${
                          task.status === 'completed' ? 'bg-green-400' :
                          task.status === 'failed' ? 'bg-red-400' :
                          'bg-blue-400'
                        }`}></div>
                        <div className="min-w-0 flex-1">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {task.request.user_prompt.prompt.substring(0, 50)}...
                          </p>
                          <p className="text-sm text-gray-500">
                            {task.status} • {task.started_at ? new Date(task.started_at).toLocaleDateString() : 'Just now'}
                          </p>
                        </div>
                        <div>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            task.status === 'completed' ? 'bg-green-100 text-green-800' :
                            task.status === 'failed' ? 'bg-red-100 text-red-800' :
                            'bg-blue-100 text-blue-800'
                          }`}>
                            {task.status}
                          </span>
                        </div>
                      </div>
                    </li>
                  ))
                ) : (
                  <li className="py-4 text-center text-gray-500">
                    No tasks found. Start by creating your first automation.
                  </li>
                )}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;