import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  HomeIcon,
  ChatAltIcon,
  CalendarIcon,
  CogIcon,
  UsersIcon,
  ChartBarIcon,
  LightningBoltIcon,
  ClockIcon
} from '@heroicons/react/outline';

const Sidebar: React.FC = () => {
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/', icon: HomeIcon },
    { name: 'AI Agent', href: '/scheduling-agent', icon: ChatAltIcon },
    { name: 'Meetings', href: '/meetings', icon: CalendarIcon },
    { name: 'Calendar', href: '/calendar', icon: CalendarIcon },
    { name: 'Preferences', href: '/preferences', icon: CogIcon },
    { name: 'Users', href: '/users', icon: UsersIcon },
  ];

  const quickActions = [
    { name: 'Schedule Meeting', href: '/scheduling-agent', icon: LightningBoltIcon },
    { name: 'View Calendar', href: '/calendar', icon: ClockIcon },
    { name: 'Analytics', href: '/preferences', icon: ChartBarIcon },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="hidden lg:flex lg:flex-shrink-0">
      <div className="flex flex-col w-64">
        <div className="flex flex-col h-0 flex-1 bg-white border-r border-gray-200">
          {/* Navigation */}
          <div className="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto">
            <nav className="mt-5 flex-1 px-2 space-y-1">
              {navigation.map((item) => {
                const isCurrent = isActive(item.href);
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors ${
                      isCurrent
                        ? 'bg-blue-100 text-blue-900 border-r-2 border-blue-500'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`}
                  >
                    <item.icon
                      className={`mr-3 flex-shrink-0 h-6 w-6 ${
                        isCurrent ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'
                      }`}
                    />
                    {item.name}
                  </Link>
                );
              })}
            </nav>

            {/* Quick Actions */}
            <div className="mt-8 px-2">
              <h3 className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Quick Actions
              </h3>
              <div className="mt-2 space-y-1">
                {quickActions.map((action) => (
                  <Link
                    key={action.name}
                    to={action.href}
                    className="group flex items-center px-3 py-2 text-sm font-medium text-gray-600 rounded-md hover:text-gray-900 hover:bg-gray-50 transition-colors"
                  >
                    <action.icon className="mr-3 flex-shrink-0 h-5 w-5 text-gray-400 group-hover:text-gray-500" />
                    {action.name}
                  </Link>
                ))}
              </div>
            </div>
          </div>

          {/* Bottom Section */}
          <div className="flex-shrink-0 flex border-t border-gray-200 p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-xs">AI</span>
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-700">AI Scheduling Agent</p>
                <p className="text-xs text-gray-500">Powered by LangChain</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar; 