// src/components/AutomationSuggestions.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  LightBulbIcon, 
  ArrowRightIcon, 
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  UserGroupIcon,
  ArrowTrendingUpIcon,
  CurrencyDollarIcon,
  ShoppingBagIcon,
  PresentationChartBarIcon,
  MagnifyingGlassIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline';

/**
 * @interface SuggestionCategory
 * @description Represents a category of automation suggestions.
 * @property {string} id - The unique identifier for the category.
 * @property {string} name - The name of the category.
 * @property {React.ReactNode} icon - The icon for the category.
 * @property {string[]} suggestions - A list of suggestions in the category.
 */
interface SuggestionCategory {
  id: string;
  name: string;
  icon: React.ReactNode;
  suggestions: string[];
}

/**
 * @component AutomationSuggestions
 * @description A component that displays a list of automation suggestions, categorized for easy browsing.
 * @returns {React.FC} The automation suggestions component.
 */
const AutomationSuggestions: React.FC = () => {
  const navigate = useNavigate();
  const [activeCategory, setActiveCategory] = useState<string>('all');
  
  const categories: SuggestionCategory[] = [
    {
      id: 'social',
      name: 'Social Media',
      icon: <UserGroupIcon className="h-5 w-5" />,
      suggestions: [
        'Post this article to my LinkedIn',
        'Schedule tweets for next week',
        'Cross-post content to Twitter and Facebook',
        'Engage with followers automatically',
        'Monitor brand mentions across platforms'
      ]
    },
    {
      id: 'marketing',
      name: 'Marketing',
      icon: <PresentationChartBarIcon className="h-5 w-5" />,
      suggestions: [
        'Scrape competitor prices from their website',
        'Collect email addresses from lead generation sites',
        'Schedule content across social platforms',
        'Monitor ad campaign performance',
        'Generate weekly marketing reports'
      ]
    },
    {
      id: 'research',
      name: 'Research',
      icon: <MagnifyingGlassIcon className="h-5 w-5" />,
      suggestions: [
        'Monitor website changes for me',
        'Extract product information from e-commerce sites',
        'Gather contact information from business directories',
        'Collect pricing data from multiple retailers',
        'Track stock availability for specific products'
      ]
    },
    {
      id: 'business',
      name: 'Business Ops',
      icon: <Cog6ToothIcon className="h-5 w-5" />,
      suggestions: [
        'Fill out and submit forms automatically',
        'Schedule appointments based on calendar availability',
        'Process invoices from email attachments',
        'Update CRM with new lead information',
        'Monitor inventory levels and alert when low'
      ]
    },
    {
      id: 'personal',
      name: 'Personal',
      icon: <DocumentTextIcon className="h-5 w-5" />,
      suggestions: [
        'Book travel when deals are found',
        'Monitor price drops for items on my wishlist',
        'Apply for jobs based on my criteria',
        'Organize my subscriptions and cancel unused ones',
        'Aggregate news from multiple sources'
      ]
    }
  ];

  const allSuggestions = categories.flatMap(cat => 
    cat.suggestions.map(s => ({ name: s, category: cat.id }))
  );

  const filteredSuggestions = activeCategory === 'all' 
    ? allSuggestions 
    : allSuggestions.filter(s => s.category === activeCategory);

  /**
   * @function handleSuggestionClick
   * @description Handles the click event for a suggestion, navigating to the chat interface with the suggestion pre-filled.
   * @param {string} suggestion - The suggestion that was clicked.
   */
  const handleSuggestionClick = (suggestion: { name: string, category: string }) => {
    // In a real app, this would navigate to the chat interface with the suggestion pre-filled
    navigate('/', { state: { prefill: suggestion.name } });
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="px-4 py-5 border-b border-gray-200 sm:px-6">
        <div className="flex items-center">
          <LightBulbIcon className="h-8 w-8 text-yellow-500 mr-3" />
          <div>
            <h1 className="text-xl font-semibold text-gray-900">Automation Suggestions</h1>
            <p className="mt-1 text-sm text-gray-500">
              Discover popular automation tasks used by our community.
            </p>
          </div>
        </div>
      </div>

      {/* Category filter */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setActiveCategory('all')}
            className={`px-3 py-1.5 rounded-full text-sm font-medium ${
              activeCategory === 'all'
                ? 'bg-blue-100 text-blue-800'
                : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
            }`}
          >
            All Categories
          </button>
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => setActiveCategory(category.id)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium flex items-center ${
                activeCategory === category.id
                  ? 'bg-blue-100 text-blue-800'
                  : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
              }`}
            >
              {category.icon}
              <span className="ml-1">{category.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Suggestions grid */}
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredSuggestions.map((suggestion, index) => {
              const category = categories.find(cat => cat.id === (suggestion as any).category);
              return (
                <div 
                  key={index} 
                  className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow duration-200 cursor-pointer"
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="flex items-center">
                        {category?.icon}
                        <span className="ml-2 text-xs font-medium text-gray-500 uppercase tracking-wide">
                          {category?.name}
                        </span>
                      </div>
                      <h3 className="mt-2 text-lg font-medium text-gray-900">
                        {suggestion.name}
                      </h3>
                    </div>
                    <ArrowRightIcon className="h-5 w-5 text-gray-400" />
                  </div>
                </div>
              );
            })}
          </div>

          {/* Popular templates section */}
          <div className="mt-12">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Popular Automation Templates</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white rounded-lg border border-gray-200 p-5 hover:shadow-md transition-shadow duration-200">
                <div className="bg-blue-100 w-10 h-10 rounded-lg flex items-center justify-center mb-3">
                  <UserGroupIcon className="h-6 w-6 text-blue-600" />
                </div>
                <h3 className="font-medium text-gray-900">Social Media Scheduler</h3>
                <p className="text-sm text-gray-500 mt-1">Post content across platforms at scheduled times</p>
                <button className="mt-3 text-sm font-medium text-blue-600 hover:text-blue-500">
                  Use Template
                </button>
              </div>
              
              <div className="bg-white rounded-lg border border-gray-200 p-5 hover:shadow-md transition-shadow duration-200">
                <div className="bg-green-100 w-10 h-10 rounded-lg flex items-center justify-center mb-3">
                  <ArrowTrendingUpIcon className="h-6 w-6 text-green-600" />
                </div>
                <h3 className="font-medium text-gray-900">Price Monitor</h3>
                <p className="text-sm text-gray-500 mt-1">Track competitor prices and get alerts</p>
                <button className="mt-3 text-sm font-medium text-blue-600 hover:text-blue-500">
                  Use Template
                </button>
              </div>
              
              <div className="bg-white rounded-lg border border-gray-200 p-5 hover:shadow-md transition-shadow duration-200">
                <div className="bg-purple-100 w-10 h-10 rounded-lg flex items-center justify-center mb-3">
                  <CurrencyDollarIcon className="h-6 w-6 text-purple-600" />
                </div>
                <h3 className="font-medium text-gray-900">Deal Finder</h3>
                <p className="text-sm text-gray-500 mt-1">Find and book the best deals automatically</p>
                <button className="mt-3 text-sm font-medium text-blue-600 hover:text-blue-500">
                  Use Template
                </button>
              </div>
            </div>
          </div>

          {/* How it works section */}
          <div className="mt-12">
            <h2 className="text-lg font-medium text-gray-900 mb-4">How It Works</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="bg-gray-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <ChatBubbleLeftRightIcon className="h-8 w-8 text-gray-600" />
                </div>
                <h3 className="font-medium text-gray-900">Describe Your Task</h3>
                <p className="mt-2 text-sm text-gray-500">
                  Tell us what you want to automate in simple English
                </p>
              </div>
              
              <div className="text-center">
                <div className="bg-gray-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Cog6ToothIcon className="h-8 w-8 text-gray-600" />
                </div>
                <h3 className="font-medium text-gray-900">We Handle It</h3>
                <p className="mt-2 text-sm text-gray-500">
                  Our AI performs the web tasks just like a human would
                </p>
              </div>
              
              <div className="text-center">
                <div className="bg-gray-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <PresentationChartBarIcon className="h-8 w-8 text-gray-600" />
                </div>
                <h3 className="font-medium text-gray-900">Get Results</h3>
                <p className="mt-2 text-sm text-gray-500">
                  Monitor progress and receive notifications when complete
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AutomationSuggestions;