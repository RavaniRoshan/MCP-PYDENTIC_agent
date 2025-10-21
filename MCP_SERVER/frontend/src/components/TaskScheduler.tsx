// src/components/TaskScheduler.tsx
import React, { useState } from 'react';
import { 
  CalendarIcon, 
  ClockIcon, 
  PlusIcon, 
  TrashIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';

interface ScheduledTask {
  id: string;
  title: string;
  description: string;
  schedule: {
    type: 'once' | 'daily' | 'weekly' | 'monthly';
    date?: string;
    time?: string;
    days?: string[]; // For weekly schedule
    dayOfMonth?: number; // For monthly schedule
  };
  createdAt: string;
  status: 'scheduled' | 'running' | 'completed' | 'failed' | 'cancelled';
}

const TaskScheduler: React.FC = () => {
  const [tasks, setTasks] = useState<ScheduledTask[]>([
    {
      id: '1',
      title: 'Weekly Social Media Post',
      description: 'Post latest blog article to LinkedIn and Twitter',
      schedule: { type: 'weekly', days: ['Monday'], time: '09:00' },
      createdAt: '2023-05-15',
      status: 'scheduled'
    },
    {
      id: '2',
      title: 'Daily Price Monitoring',
      description: 'Check competitor prices on their website',
      schedule: { type: 'daily', time: '10:30' },
      createdAt: '2023-05-16',
      status: 'running'
    }
  ]);
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    scheduleType: 'once' as 'once' | 'daily' | 'weekly' | 'monthly',
    date: '',
    time: '',
    days: [] as string[],
    dayOfMonth: 1
  });
  
  const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

  const handleAddTask = () => {
    if (!newTask.title || !newTask.description) return;
    
    const scheduledTask: ScheduledTask = {
      id: `task_${Date.now()}`,
      title: newTask.title,
      description: newTask.description,
      schedule: {
        type: newTask.scheduleType,
        ...(newTask.scheduleType === 'once' && { date: newTask.date, time: newTask.time }),
        ...(newTask.scheduleType === 'daily' && { time: newTask.time }),
        ...(newTask.scheduleType === 'weekly' && { days: newTask.days, time: newTask.time }),
        ...(newTask.scheduleType === 'monthly' && { dayOfMonth: newTask.dayOfMonth, time: newTask.time })
      },
      createdAt: new Date().toISOString(),
      status: 'scheduled'
    };

    setTasks([...tasks, scheduledTask]);
    setIsModalOpen(false);
    resetForm();
  };

  const resetForm = () => {
    setNewTask({
      title: '',
      description: '',
      scheduleType: 'once',
      date: '',
      time: '',
      days: [],
      dayOfMonth: 1
    });
  };

  const handleDayToggle = (day: string) => {
    setNewTask(prev => ({
      ...prev,
      days: prev.days.includes(day) 
        ? prev.days.filter(d => d !== day) 
        : [...prev.days, day]
    }));
  };

  const deleteTask = (id: string) => {
    setTasks(tasks.filter(task => task.id !== id));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'failed':
        return 'text-red-600 bg-red-100';
      case 'running':
        return 'text-blue-600 bg-blue-100';
      case 'cancelled':
        return 'text-gray-600 bg-gray-100';
      default: // scheduled
        return 'text-yellow-600 bg-yellow-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="px-4 py-5 border-b border-gray-200 sm:px-6">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold text-gray-900">Task Scheduler</h1>
          <button
            onClick={() => setIsModalOpen(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
            Schedule Task
          </button>
        </div>
        <p className="mt-1 text-sm text-gray-500">
          Automate recurring tasks on your schedule.
        </p>
      </div>

      {/* Task List */}
      <div className="flex-1 overflow-y-auto p-4">
        {tasks.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center py-12">
            <CalendarIcon className="h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-1">No scheduled tasks</h3>
            <p className="text-gray-500 mb-4">
              You haven't scheduled any automated tasks yet.
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
            >
              <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
              Schedule your first task
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {tasks.map((task) => (
              <div key={task.id} className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">{task.title}</h3>
                      <p className="mt-1 text-sm text-gray-500">{task.description}</p>
                    </div>
                    <button 
                      onClick={() => deleteTask(task.id)}
                      className="text-gray-400 hover:text-red-500"
                    >
                      <TrashIcon className="h-5 w-5" />
                    </button>
                  </div>
                  
                  <div className="mt-4">
                    <div className="flex items-center text-sm text-gray-500">
                      <CalendarIcon className="h-4 w-4 mr-1" />
                      <span className="capitalize">{task.schedule.type}</span>
                      {task.schedule.time && (
                        <span className="ml-2">at {task.schedule.time}</span>
                      )}
                      {task.schedule.days && task.schedule.days.length > 0 && (
                        <span className="ml-2">on {task.schedule.days.join(', ')}</span>
                      )}
                      {task.schedule.dayOfMonth && task.schedule.type === 'monthly' && (
                        <span className="ml-2">on day {task.schedule.dayOfMonth}</span>
                      )}
                      {task.schedule.date && (
                        <span className="ml-2">{new Date(task.schedule.date).toLocaleDateString()}</span>
                      )}
                    </div>
                  </div>
                  
                  <div className="mt-4 flex items-center justify-between">
                    <div className="flex items-center">
                      <div className={getStatusColor(task.status)}>
                        <div className="flex items-center px-2 py-1 rounded-full text-xs font-medium">
                          {getStatusIcon(task.status)}
                          <span className="ml-1 capitalize">{task.status}</span>
                        </div>
                      </div>
                    </div>
                    <div className="text-xs text-gray-500">
                      Created: {new Date(task.createdAt).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal for adding new task */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900">Schedule New Task</h3>
                <button
                  onClick={() => {
                    setIsModalOpen(false);
                    resetForm();
                  }}
                  className="text-gray-400 hover:text-gray-500"
                >
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="mt-4">
                <form>
                  <div className="mb-4">
                    <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                      Task Title
                    </label>
                    <input
                      type="text"
                      id="title"
                      value={newTask.title}
                      onChange={(e) => setNewTask({...newTask, title: e.target.value})}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                      placeholder="e.g., Weekly social media post"
                    />
                  </div>
                  
                  <div className="mb-4">
                    <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                      Description
                    </label>
                    <textarea
                      id="description"
                      value={newTask.description}
                      onChange={(e) => setNewTask({...newTask, description: e.target.value})}
                      rows={3}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                      placeholder="Describe what this task should do..."
                    />
                  </div>
                  
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Schedule Type
                    </label>
                    <div className="grid grid-cols-4 gap-2">
                      {(['once', 'daily', 'weekly', 'monthly'] as const).map((type) => (
                        <button
                          key={type}
                          type="button"
                          onClick={() => setNewTask({...newTask, scheduleType: type})}
                          className={`py-2 px-3 rounded-md text-sm font-medium ${
                            newTask.scheduleType === type
                              ? 'bg-blue-100 text-blue-700 border border-blue-300'
                              : 'bg-white text-gray-700 border border-gray-300'
                          }`}
                        >
                          {type.charAt(0).toUpperCase() + type.slice(1)}
                        </button>
                      ))}
                    </div>
                  </div>
                  
                  {/* Schedule-specific fields */}
                  {(newTask.scheduleType === 'once' || newTask.scheduleType === 'weekly' || newTask.scheduleType === 'monthly') && (
                    <div className="mb-4">
                      <label htmlFor="time" className="block text-sm font-medium text-gray-700 mb-1">
                        Time
                      </label>
                      <input
                        type="time"
                        id="time"
                        value={newTask.time}
                        onChange={(e) => setNewTask({...newTask, time: e.target.value})}
                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                      />
                    </div>
                  )}
                  
                  {newTask.scheduleType === 'once' && (
                    <div className="mb-4">
                      <label htmlFor="date" className="block text-sm font-medium text-gray-700 mb-1">
                        Date
                      </label>
                      <input
                        type="date"
                        id="date"
                        value={newTask.date}
                        onChange={(e) => setNewTask({...newTask, date: e.target.value})}
                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                      />
                    </div>
                  )}
                  
                  {newTask.scheduleType === 'weekly' && (
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Days of Week
                      </label>
                      <div className="grid grid-cols-4 gap-2">
                        {daysOfWeek.map((day) => (
                          <button
                            key={day}
                            type="button"
                            onClick={() => handleDayToggle(day)}
                            className={`py-2 px-3 rounded-md text-sm font-medium ${
                              newTask.days.includes(day)
                                ? 'bg-blue-100 text-blue-700 border border-blue-300'
                                : 'bg-white text-gray-700 border border-gray-300'
                            }`}
                          >
                            {day.substring(0, 3)}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {newTask.scheduleType === 'monthly' && (
                    <div className="mb-4">
                      <label htmlFor="dayOfMonth" className="block text-sm font-medium text-gray-700 mb-1">
                        Day of Month
                      </label>
                      <input
                        type="number"
                        id="dayOfMonth"
                        min="1"
                        max="31"
                        value={newTask.dayOfMonth}
                        onChange={(e) => setNewTask({...newTask, dayOfMonth: parseInt(e.target.value) || 1})}
                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                      />
                    </div>
                  )}
                  
                  <div className="mt-6 flex justify-end space-x-3">
                    <button
                      type="button"
                      onClick={() => {
                        setIsModalOpen(false);
                        resetForm();
                      }}
                      className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      Cancel
                    </button>
                    <button
                      type="button"
                      onClick={handleAddTask}
                      className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      Schedule Task
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TaskScheduler;