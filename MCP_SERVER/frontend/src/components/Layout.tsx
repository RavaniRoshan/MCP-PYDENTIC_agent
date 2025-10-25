// src/components/Layout.tsx
import React, { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ChatBubbleLeftRightIcon, 
  ChartBarIcon, 
  ClockIcon, 
  Cog6ToothIcon,
  LightBulbIcon,
  CalendarIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';

/**
 * @interface LayoutProps
 * @description The props for the Layout component.
 * @property {ReactNode} children - The child elements to be rendered within the layout.
 */
interface LayoutProps {
  children: ReactNode;
}

/**
 * @component Layout
 * @description A component that provides the main layout for the application, including a sidebar and main content area.
 * @param {LayoutProps} props - The props for the component.
 * @returns {React.FC} The layout component.
 */
const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  const { user, logout } = useAuth();
  
  const navigation = [
    { name: 'Chat', href: '/', icon: ChatBubbleLeftRightIcon },
    { name: 'Dashboard', href: '/dashboard', icon: ChartBarIcon },
    { name: 'History', href: '/history', icon: ClockIcon },
    { name: 'Social Media', href: '/social-media', icon: ChatBubbleLeftRightIcon },
    { name: 'Scheduler', href: '/scheduler', icon: CalendarIcon },
    { name: 'Suggestions', href: '/suggestions', icon: LightBulbIcon },
    { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
  ];

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0">
        <div className="flex flex-col flex-grow pt-5 bg-white overflow-y-auto border-r border-gray-200">
          <div className="flex-shrink-0 px-4 flex items-center justify-center">
            <div className="flex items-center space-x-2">
              <div className="bg-gradient-to-r from-blue-500 to-purple-600 w-8 h-8 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">A</span>
              </div>
              <h1 className="text-xl font-bold text-gray-900">AutomateAI</h1>
            </div>
          </div>
          
          <div className="mt-8 flex-1 flex flex-col">
            <nav className="flex-1 px-2 space-y-1">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`${
                      isActive 
                        ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700' 
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    } group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200`}
                  >
                    <item.icon
                      className={`${
                        isActive ? 'text-blue-700' : 'text-gray-400 group-hover:text-gray-500'
                      } mr-3 h-6 w-6 flex-shrink-0`}
                      aria-hidden="true"
                    />
                    {item.name}
                  </Link>
                );
              })}
            </nav>
            
            {/* User section */}
            <div className="p-4 border-t border-gray-200">
              {user ? (
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="bg-gray-200 border-2 border-dashed rounded-xl w-8 h-8" />
                    <div className="ml-3">
                      <p className="text-sm font-medium text-gray-700">{user.name}</p>
                      <p className="text-xs text-gray-500">Online</p>
                    </div>
                  </div>
                  <button
                    onClick={logout}
                    className="text-gray-400 hover:text-gray-500"
                  >
                    <ArrowRightOnRectangleIcon className="h-5 w-5" />
                  </button>
                </div>
              ) : (
                <Link 
                  to="/login" 
                  className="text-sm font-medium text-blue-600 hover:text-blue-500"
                >
                  Sign in
                </Link>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="md:pl-64 flex flex-col flex-1">
        {/* Mobile header */}
        <div className="md:hidden flex items-center px-4 py-3 bg-white border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 w-8 h-8 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">A</span>
            </div>
            <h1 className="text-xl font-bold text-gray-900">AutomateAI</h1>
          </div>
        </div>
        
        {/* Content area */}
        <main className="flex-1 pb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="h-full"
          >
            {children}
          </motion.div>
        </main>
      </div>
    </div>
  );
};

export default Layout;