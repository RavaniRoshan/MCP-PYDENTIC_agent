// src/components/Settings.tsx
import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Cog6ToothIcon, UserCircleIcon, ShieldCheckIcon, BellIcon, KeyIcon } from '@heroicons/react/24/outline';

/**
 * @component Settings
 * @description A component that provides a user interface for managing account settings and preferences.
 * @returns {React.FC} The settings component.
 */
const Settings: React.FC = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');

  // Mock settings data
  const [settings, setSettings] = useState({
    profile: {
      name: user?.name || 'John Doe',
      email: user?.email || 'john@example.com',
      bio: 'AutomateAI user',
    },
    preferences: {
      theme: 'light',
      notifications: {
        email: true,
        browser: true,
        tasks: true
      },
      privacy: {
        profile_visible: true,
        activity_visible: true
      }
    },
    security: {
      two_factor: false,
      login_alerts: true,
      app_access: true
    }
  });

  /**
   * @function handleSave
   * @description Handles the saving of settings.
   */
  const handleSave = () => {
    alert('Settings saved successfully!');
  };

  const tabs = [
    { id: 'profile', name: 'Profile', icon: UserCircleIcon },
    { id: 'preferences', name: 'Preferences', icon: Cog6ToothIcon },
    { id: 'security', name: 'Security', icon: ShieldCheckIcon },
    { id: 'notifications', name: 'Notifications', icon: BellIcon },
  ];

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="px-4 py-5 border-b border-gray-200 sm:px-6">
        <h1 className="text-xl font-semibold text-gray-900">Settings</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage your AutomateAI account settings and preferences.
        </p>
      </div>

      <div className="flex-1 overflow-hidden flex flex-col md:flex-row">
        {/* Settings sidebar */}
        <div className="w-full md:w-64 border-r border-gray-200 bg-white">
          <nav className="flex flex-1 flex-col">
            <ul className="space-y-1 px-2">
              {tabs.map((tab) => {
                return (
                  <li key={tab.id}>
                    <button
                      onClick={() => setActiveTab(tab.id)}
                      className={`${
                        activeTab === tab.id
                          ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                      } group flex items-center px-3 py-2 text-sm font-medium rounded-md w-full text-left transition-colors duration-200`}
                    >
                      <tab.icon
                        className={`${
                          activeTab === tab.id ? 'text-blue-700' : 'text-gray-400 group-hover:text-gray-500'
                        } mr-3 h-5 w-5 flex-shrink-0`}
                        aria-hidden="true"
                      />
                      {tab.name}
                    </button>
                  </li>
                );
              })}
            </ul>
          </nav>
        </div>

        {/* Settings content */}
        <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
          <div className="max-w-3xl mx-auto">
            {/* Profile Settings */}
            {activeTab === 'profile' && (
              <div className="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
                <div className="md:grid md:grid-cols-3 md:gap-6">
                  <div className="md:col-span-1">
                    <h3 className="text-lg font-medium leading-6 text-gray-900">Profile</h3>
                    <p className="mt-1 text-sm text-gray-500">
                      This information will be displayed publicly so be careful what you share.
                    </p>
                  </div>
                  <div className="mt-5 md:col-span-2 md:mt-0">
                    <form>
                      <div className="grid grid-cols-6 gap-6">
                        <div className="col-span-6">
                          <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                            Full name
                          </label>
                          <input
                            type="text"
                            name="name"
                            id="name"
                            value={settings.profile.name}
                            onChange={(e) => setSettings({
                              ...settings,
                              profile: { ...settings.profile, name: e.target.value }
                            })}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                          />
                        </div>

                        <div className="col-span-6">
                          <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                            Email address
                          </label>
                          <input
                            type="email"
                            name="email"
                            id="email"
                            value={settings.profile.email}
                            onChange={(e) => setSettings({
                              ...settings,
                              profile: { ...settings.profile, email: e.target.value }
                            })}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                          />
                        </div>

                        <div className="col-span-6">
                          <label htmlFor="bio" className="block text-sm font-medium text-gray-700">
                            Bio
                          </label>
                          <textarea
                            id="bio"
                            name="bio"
                            rows={3}
                            value={settings.profile.bio}
                            onChange={(e) => setSettings({
                              ...settings,
                              profile: { ...settings.profile, bio: e.target.value }
                            })}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                          />
                        </div>
                      </div>
                    </form>
                  </div>
                </div>
                <div className="mt-6 flex justify-end">
                  <button
                    type="button"
                    className="rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={handleSave}
                    className="ml-3 inline-flex justify-center rounded-md border border-transparent bg-blue-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  >
                    Save
                  </button>
                </div>
              </div>
            )}

            {/* Preferences Settings */}
            {activeTab === 'preferences' && (
              <div className="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
                <div className="md:grid md:grid-cols-3 md:gap-6">
                  <div className="md:col-span-1">
                    <h3 className="text-lg font-medium leading-6 text-gray-900">Preferences</h3>
                    <p className="mt-1 text-sm text-gray-500">
                      Configure your AutomateAI experience.
                    </p>
                  </div>
                  <div className="mt-5 md:col-span-2 md:mt-0">
                    <form className="divide-y divide-gray-200">
                      <div className="py-6">
                        <div className="space-y-6">
                          <div className="grid grid-cols-6 gap-6">
                            <div className="col-span-6">
                              <h4 className="text-sm font-medium text-gray-900">Theme</h4>
                              <div className="mt-2 space-y-2">
                                {['light', 'dark'].map((theme) => (
                                  <div key={theme} className="flex items-center">
                                    <input
                                      id={`theme-${theme}`}
                                      name="theme"
                                      type="radio"
                                      checked={settings.preferences.theme === theme}
                                      onChange={() => setSettings({
                                        ...settings,
                                        preferences: { ...settings.preferences, theme }
                                      })}
                                      className="h-4 w-4 border-gray-300 text-blue-600 focus:ring-blue-500"
                                    />
                                    <label htmlFor={`theme-${theme}`} className="ml-3 block text-sm font-medium text-gray-700">
                                      {theme.charAt(0).toUpperCase() + theme.slice(1)}
                                    </label>
                                  </div>
                                ))}
                              </div>
                            </div>
                            
                            <div className="col-span-6">
                              <h4 className="text-sm font-medium text-gray-900">Notifications</h4>
                              <div className="mt-2 space-y-2">
                                <div className="flex items-center justify-between">
                                  <label className="block text-sm font-medium text-gray-700">Email notifications</label>
                                  <input
                                    type="checkbox"
                                    checked={settings.preferences.notifications.email}
                                    onChange={(e) => setSettings({
                                      ...settings,
                                      preferences: {
                                        ...settings.preferences,
                                        notifications: {
                                          ...settings.preferences.notifications,
                                          email: e.target.checked
                                        }
                                      }
                                    })}
                                    className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                  />
                                </div>
                                <div className="flex items-center justify-between">
                                  <label className="block text-sm font-medium text-gray-700">Browser notifications</label>
                                  <input
                                    type="checkbox"
                                    checked={settings.preferences.notifications.browser}
                                    onChange={(e) => setSettings({
                                      ...settings,
                                      preferences: {
                                        ...settings.preferences,
                                        notifications: {
                                          ...settings.preferences.notifications,
                                          browser: e.target.checked
                                        }
                                      }
                                    })}
                                    className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                  />
                                </div>
                                <div className="flex items-center justify-between">
                                  <label className="block text-sm font-medium text-gray-700">Task updates</label>
                                  <input
                                    type="checkbox"
                                    checked={settings.preferences.notifications.tasks}
                                    onChange={(e) => setSettings({
                                      ...settings,
                                      preferences: {
                                        ...settings.preferences,
                                        notifications: {
                                          ...settings.preferences.notifications,
                                          tasks: e.target.checked
                                        }
                                      }
                                    })}
                                    className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                  />
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </form>
                  </div>
                </div>
                <div className="mt-6 flex justify-end">
                  <button
                    type="button"
                    className="rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={handleSave}
                    className="ml-3 inline-flex justify-center rounded-md border border-transparent bg-blue-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  >
                    Save
                  </button>
                </div>
              </div>
            )}

            {/* Security Settings */}
            {activeTab === 'security' && (
              <div className="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
                <div className="md:grid md:grid-cols-3 md:gap-6">
                  <div className="md:col-span-1">
                    <h3 className="text-lg font-medium leading-6 text-gray-900">Security</h3>
                    <p className="mt-1 text-sm text-gray-500">
                      Manage your account security settings.
                    </p>
                  </div>
                  <div className="mt-5 md:col-span-2 md:mt-0">
                    <form className="divide-y divide-gray-200">
                      <div className="py-6">
                        <div className="space-y-6">
                          <div className="grid grid-cols-6 gap-6">
                            <div className="col-span-6">
                              <div className="flex items-center justify-between">
                                <span className="flex flex-col">
                                  <span className="text-sm font-medium text-gray-900">Two-factor authentication</span>
                                  <span className="text-sm text-gray-500">Add an extra layer of security to your account</span>
                                </span>
                                <button
                                  type="button"
                                  className="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                                  role="switch"
                                  aria-checked={settings.security.two_factor}
                                >
                                  <span
                                    aria-hidden="true"
                                    className={`${
                                      settings.security.two_factor ? 'translate-x-5' : 'translate-x-0'
                                    } pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out`}
                                  />
                                </button>
                              </div>
                            </div>
                            
                            <div className="col-span-6">
                              <div className="flex items-center justify-between">
                                <span className="flex flex-col">
                                  <span className="text-sm font-medium text-gray-900">Login alerts</span>
                                  <span className="text-sm text-gray-500">Receive notifications when your account is accessed from a new device</span>
                                </span>
                                <button
                                  type="button"
                                  className="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                                  role="switch"
                                  aria-checked={settings.security.login_alerts}
                                >
                                  <span
                                    aria-hidden="true"
                                    className={`${
                                      settings.security.login_alerts ? 'translate-x-5' : 'translate-x-0'
                                    } pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out`}
                                  />
                                </button>
                              </div>
                            </div>
                            
                            <div className="col-span-6">
                              <div className="flex items-center justify-between">
                                <span className="flex flex-col">
                                  <span className="text-sm font-medium text-gray-900">App access</span>
                                  <span className="text-sm text-gray-500">Allow or restrict access to your account by third-party applications</span>
                                </span>
                                <button
                                  type="button"
                                  className="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                                  role="switch"
                                  aria-checked={settings.security.app_access}
                                >
                                  <span
                                    aria-hidden="true"
                                    className={`${
                                      settings.security.app_access ? 'translate-x-5' : 'translate-x-0'
                                    } pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out`}
                                  />
                                </button>
                              </div>
                            </div>
                          </div>
                          
                          <div className="pt-6">
                            <div className="flex items-center">
                              <KeyIcon className="h-5 w-5 text-gray-400" />
                              <h4 className="ml-2 text-sm font-medium text-gray-900">Change Password</h4>
                            </div>
                            <div className="mt-4 grid grid-cols-6 gap-6">
                              <div className="col-span-6 sm:col-span-4">
                                <label htmlFor="current-password" className="block text-sm font-medium text-gray-700">
                                  Current password
                                </label>
                                <input
                                  type="password"
                                  name="current-password"
                                  id="current-password"
                                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                />
                              </div>
                              
                              <div className="col-span-6 sm:col-span-4">
                                <label htmlFor="new-password" className="block text-sm font-medium text-gray-700">
                                  New password
                                </label>
                                <input
                                  type="password"
                                  name="new-password"
                                  id="new-password"
                                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                />
                              </div>
                              
                              <div className="col-span-6 sm:col-span-4">
                                <label htmlFor="confirm-password" className="block text-sm font-medium text-gray-700">
                                  Confirm new password
                                </label>
                                <input
                                  type="password"
                                  name="confirm-password"
                                  id="confirm-password"
                                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                />
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </form>
                  </div>
                </div>
                <div className="mt-6 flex justify-end">
                  <button
                    type="button"
                    className="rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={handleSave}
                    className="ml-3 inline-flex justify-center rounded-md border border-transparent bg-blue-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  >
                    Save
                  </button>
                </div>
              </div>
            )}

            {/* Notifications Settings */}
            {activeTab === 'notifications' && (
              <div className="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
                <div className="md:grid md:grid-cols-3 md:gap-6">
                  <div className="md:col-span-1">
                    <h3 className="text-lg font-medium leading-6 text-gray-900">Notifications</h3>
                    <p className="mt-1 text-sm text-gray-500">
                      Configure how you receive notifications.
                    </p>
                  </div>
                  <div className="mt-5 md:col-span-2 md:mt-0">
                    <form className="divide-y divide-gray-200">
                      <div className="py-6">
                        <div className="space-y-6">
                          <div className="grid grid-cols-6 gap-6">
                            <div className="col-span-6">
                              <h4 className="text-sm font-medium text-gray-900">Task Notifications</h4>
                              <div className="mt-2 space-y-2">
                                <div className="flex items-center justify-between">
                                  <label className="block text-sm font-medium text-gray-700">Task completion</label>
                                  <input
                                    type="checkbox"
                                    checked={settings.preferences.notifications.tasks}
                                    onChange={(e) => setSettings({
                                      ...settings,
                                      preferences: {
                                        ...settings.preferences,
                                        notifications: {
                                          ...settings.preferences.notifications,
                                          tasks: e.target.checked
                                        }
                                      }
                                    })}
                                    className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                  />
                                </div>
                                <div className="flex items-center justify-between">
                                  <label className="block text-sm font-medium text-gray-700">Failed tasks</label>
                                  <input
                                    type="checkbox"
                                    defaultChecked
                                    className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                  />
                                </div>
                                <div className="flex items-center justify-between">
                                  <label className="block text-sm font-medium text-gray-700">Scheduled task warnings</label>
                                  <input
                                    type="checkbox"
                                    defaultChecked
                                    className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                  />
                                </div>
                              </div>
                            </div>
                            
                            <div className="col-span-6">
                              <h4 className="text-sm font-medium text-gray-900">Account Notifications</h4>
                              <div className="mt-2 space-y-2">
                                <div className="flex items-center justify-between">
                                  <label className="block text-sm font-medium text-gray-700">Login alerts</label>
                                  <input
                                    type="checkbox"
                                    defaultChecked
                                    className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                  />
                                </div>
                                <div className="flex items-center justify-between">
                                  <label className="block text-sm font-medium text-gray-700">Security alerts</label>
                                  <input
                                    type="checkbox"
                                    defaultChecked
                                    className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                  />
                                </div>
                                <div className="flex items-center justify-between">
                                  <label className="block text-sm font-medium text-gray-700">Plan updates</label>
                                  <input
                                    type="checkbox"
                                    className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                  />
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </form>
                  </div>
                </div>
                <div className="mt-6 flex justify-end">
                  <button
                    type="button"
                    className="rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={handleSave}
                    className="ml-3 inline-flex justify-center rounded-md border border-transparent bg-blue-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  >
                    Save
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;