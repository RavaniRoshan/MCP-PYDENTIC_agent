// src/components/SocialMediaScheduler.tsx
import React, { useState } from 'react';
import { socialMediaApi } from '../services/api';
import { 
  UserCircleIcon, 
  HashtagIcon, 
  PhotoIcon, 
  LinkIcon,
  CalendarIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { TaskResponse } from '../types';
import { convertApiTaskResponse } from '../types';
import { useTasks } from '../contexts/TaskContext';

interface SocialMediaPost {
  text: string;
  title?: string;
  images: string[];
  videos: string[];
  links: string[];
  hashtags: string[];
  mentions: string[];
}

const SocialMediaScheduler: React.FC = () => {
  const { addTask } = useTasks();
  const [postContent, setPostContent] = useState<SocialMediaPost>({
    text: '',
    images: [],
    videos: [],
    links: [],
    hashtags: [],
    mentions: []
  });
  
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const [scheduledTime, setScheduledTime] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const platforms = [
    { id: 'linkedin', name: 'LinkedIn', color: 'bg-blue-600' },
    { id: 'twitter', name: 'Twitter/X', color: 'bg-blue-400' },
    { id: 'facebook', name: 'Facebook', color: 'bg-blue-800' },
    { id: 'instagram', name: 'Instagram', color: 'bg-gradient-to-r from-purple-500 to-pink-500' },
    { id: 'tiktok', name: 'TikTok', color: 'bg-black' }
  ];

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setPostContent(prev => ({
      ...prev,
      [name]: name === 'hashtags' || name === 'mentions' || name === 'images' || name === 'links' || name === 'videos' 
        ? value.split(',').map(item => item.trim())
        : value
    }));
  };

  const handlePlatformToggle = (platformId: string) => {
    setSelectedPlatforms(prev => 
      prev.includes(platformId)
        ? prev.filter(id => id !== platformId)
        : [...prev, platformId]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (selectedPlatforms.length === 0) {
      setStatusMessage('Please select at least one platform');
      return;
    }

    if (!postContent.text.trim()) {
      setStatusMessage('Please enter some content for your post');
      return;
    }

    setIsLoading(true);
    setStatusMessage(null);

    try {
      let response;
      if (scheduledTime) {
        // Schedule the post
        response = await socialMediaApi.schedulePost(
          postContent,
          selectedPlatforms,
          scheduledTime
        );
        setStatusMessage('Post scheduled successfully!');
        console.log('Scheduled post response:', response);
      } else {
        // Post immediately
        response = await socialMediaApi.postToSocialMedia(
          postContent,
          selectedPlatforms
        );
        setStatusMessage('Post published successfully!');
        console.log('Posted response:', response);
      }
      
      // If the response is a task (which it should be), add it to the context
      if (response && response.task_id) {
        const task = convertApiTaskResponse(response);
        addTask(task);
      }

      // Reset form
      setPostContent({
        text: '',
        images: [],
        videos: [],
        links: [],
        hashtags: [],
        mentions: []
      });
      setSelectedPlatforms([]);
      setScheduledTime('');
    } catch (error) {
      console.error('Error with social media post:', error);
      setStatusMessage('Error posting to social media. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="px-4 py-5 border-b border-gray-200 sm:px-6">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold text-gray-900">Social Media Scheduler</h1>
          <p className="text-sm text-gray-500">
            Cross-platform posting to LinkedIn, Twitter, and more
          </p>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-md p-6">
            {statusMessage && (
              <div className={`mb-6 p-3 rounded-md ${
                statusMessage.includes('successfully') 
                  ? 'bg-green-50 text-green-800' 
                  : 'bg-red-50 text-red-800'
              }`}>
                {statusMessage}
              </div>
            )}
            
            <form onSubmit={handleSubmit}>
              {/* Content section */}
              <div className="mb-6">
                <label htmlFor="text" className="block text-sm font-medium text-gray-700 mb-2">
                  Post Content
                </label>
                <textarea
                  id="text"
                  name="text"
                  value={postContent.text}
                  onChange={handleInputChange}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="What would you like to share?"
                />
              </div>
              
              {/* Hashtags */}
              <div className="mb-6">
                <label htmlFor="hashtags" className="block text-sm font-medium text-gray-700 mb-2">
                  Hashtags
                </label>
                <div className="relative">
                  <HashtagIcon className="h-5 w-5 text-gray-400 absolute left-3 top-2.5" />
                  <input
                    type="text"
                    id="hashtags"
                    name="hashtags"
                    value={postContent.hashtags.join(', ')}
                    onChange={handleInputChange}
                    className="w-full pl-10 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="e.g., automation, ai, web"
                  />
                </div>
                <p className="mt-1 text-xs text-gray-500">Separate hashtags with commas</p>
              </div>
              
              {/* Images/Links */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <label htmlFor="images" className="block text-sm font-medium text-gray-700 mb-2">
                    Image URLs
                  </label>
                  <div className="relative">
                    <PhotoIcon className="h-5 w-5 text-gray-400 absolute left-3 top-2.5" />
                    <input
                      type="text"
                      id="images"
                      name="images"
                      value={postContent.images.join(', ')}
                      onChange={handleInputChange}
                      className="w-full pl-10 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="e.g., https://example.com/image.jpg"
                    />
                  </div>
                  <p className="mt-1 text-xs text-gray-500">Separate multiple URLs with commas</p>
                </div>
                
                <div>
                  <label htmlFor="links" className="block text-sm font-medium text-gray-700 mb-2">
                    Link URLs
                  </label>
                  <div className="relative">
                    <LinkIcon className="h-5 w-5 text-gray-400 absolute left-3 top-2.5" />
                    <input
                      type="text"
                      id="links"
                      name="links"
                      value={postContent.links.join(', ')}
                      onChange={handleInputChange}
                      className="w-full pl-10 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="e.g., https://example.com/article"
                    />
                  </div>
                  <p className="mt-1 text-xs text-gray-500">Separate multiple URLs with commas</p>
                </div>
              </div>
              
              {/* Platform selection */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Platforms
                </label>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                  {platforms.map((platform) => (
                    <button
                      key={platform.id}
                      type="button"
                      onClick={() => handlePlatformToggle(platform.id)}
                      className={`flex flex-col items-center justify-center p-3 rounded-lg border ${
                        selectedPlatforms.includes(platform.id)
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:bg-gray-50'
                      }`}
                    >
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center mb-1 ${platform.color}`}>
                        <UserCircleIcon className="h-6 w-6 text-white" />
                      </div>
                      <span className="text-xs font-medium">{platform.name}</span>
                    </button>
                  ))}
                </div>
              </div>
              
              {/* Scheduling */}
              <div className="mb-6">
                <label htmlFor="scheduledTime" className="block text-sm font-medium text-gray-700 mb-2">
                  Schedule Post (optional)
                </label>
                <div className="relative">
                  <CalendarIcon className="h-5 w-5 text-gray-400 absolute left-3 top-2.5" />
                  <ClockIcon className="h-5 w-5 text-gray-400 absolute right-3 top-2.5" />
                  <input
                    type="datetime-local"
                    id="scheduledTime"
                    value={scheduledTime}
                    onChange={(e) => setScheduledTime(e.target.value)}
                    className="w-full pl-10 pr-10 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <p className="mt-1 text-xs text-gray-500">
                  Leave empty to post immediately, or select a future date/time
                </p>
              </div>
              
              {/* Submit button */}
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={isLoading}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  {isLoading ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Processing...
                    </>
                  ) : scheduledTime ? 'Schedule Post' : 'Post Now'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SocialMediaScheduler;