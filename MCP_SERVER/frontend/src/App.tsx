// src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { TaskProvider } from './contexts/TaskContext';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/Layout';
import ChatInterface from './components/ChatInterface';
import Dashboard from './components/Dashboard';
import TaskHistory from './components/TaskHistory';
import Settings from './components/Settings';
import AutomationSuggestions from './components/AutomationSuggestions';
import TaskScheduler from './components/TaskScheduler';
import SocialMediaScheduler from './components/SocialMediaScheduler';
import './App.css';

/**
 * @component App
 * @description The main component of the application, responsible for setting up the router and context providers.
 * @returns {React.FC} The main application component.
 */
function App() {
  return (
    <AuthProvider>
      <TaskProvider>
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<ChatInterface />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/history" element={<TaskHistory />} />
              <Route path="/scheduler" element={<TaskScheduler />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/suggestions" element={<AutomationSuggestions />} />
              <Route path="/social-media" element={<SocialMediaScheduler />} />
            </Routes>
          </Layout>
        </Router>
      </TaskProvider>
    </AuthProvider>
  );
}

export default App;