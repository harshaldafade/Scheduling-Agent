import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { 
  CalendarIcon, 
  UserGroupIcon, 
  ChartBarIcon,
  PlusIcon,
  CheckCircleIcon,
  ExclamationIcon,
  CogIcon
} from '@heroicons/react/outline';
import { apiService } from '../services/api';
import { useAuth } from '../hooks/useAuth';

const Dashboard: React.FC = () => {
  const { currentUser } = useAuth();

  // Fetch user data
  const { data: userMeetings, isLoading: meetingsLoading } = useQuery({
    queryKey: ['userMeetings'],
    queryFn: () => apiService.getUserMeetings(),
    enabled: !!currentUser,
  });

  const { data: userPreferences, isLoading: preferencesLoading } = useQuery({
    queryKey: ['userPreferences'],
    queryFn: () => apiService.getUserPreferences(),
    enabled: !!currentUser,
  });

  const upcomingMeetings = userMeetings?.filter(meeting => 
    new Date(meeting.start_time) > new Date() && meeting.status === 'confirmed'
  ).slice(0, 5) || [];

  const pendingMeetings = userMeetings?.filter(meeting => 
    meeting.status === 'proposed'
  ).slice(0, 3) || [];

  const stats = {
    totalMeetings: userMeetings?.length || 0,
    upcomingMeetings: upcomingMeetings.length,
    pendingMeetings: pendingMeetings.length,
    preferenceCompleteness: Object.keys(userPreferences || {}).length > 0 ? 'Good' : 'Needs Setup',
  };

  const quickActions = [
    {
      title: 'Schedule New Meeting',
      description: 'Create a new meeting with AI assistance',
      icon: PlusIcon,
      href: '/scheduling-agent',
      color: 'bg-blue-500',
    },
    {
      title: 'View Calendar',
      description: 'See all your scheduled meetings',
      icon: CalendarIcon,
      href: '/calendar',
      color: 'bg-green-500',
    },
    {
      title: 'Manage Preferences',
      description: 'Update your scheduling preferences',
      icon: CogIcon,
      href: '/preferences',
      color: 'bg-purple-500',
    },
    {
      title: 'Team Overview',
      description: 'View team members and availability',
      icon: UserGroupIcon,
      href: '/users',
      color: 'bg-orange-500',
    },
  ];

  if (!currentUser) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="text-center py-12">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Welcome to AI Scheduling Agent</h1>
          <p className="text-gray-600 mb-8">Please log in to access your dashboard.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Welcome back, {currentUser.name}!
        </h1>
        <p className="text-gray-600">
          Here's what's happening with your schedule today.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card"
        >
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <CalendarIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Meetings</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalMeetings}</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircleIcon className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Upcoming</p>
              <p className="text-2xl font-bold text-gray-900">{stats.upcomingMeetings}</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <ExclamationIcon className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Pending</p>
              <p className="text-2xl font-bold text-gray-900">{stats.pendingMeetings}</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card"
        >
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <ChartBarIcon className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Preferences</p>
              <p className="text-2xl font-bold text-gray-900">{stats.preferenceCompleteness}</p>
            </div>
          </div>
        </motion.div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Quick Actions */}
        <div className="lg:col-span-2">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="card"
          >
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Quick Actions</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {quickActions.map((action, index) => (
                <Link
                  key={action.title}
                  to={action.href}
                  className="group block p-4 border border-gray-200 rounded-lg hover:border-gray-300 hover:shadow-md transition-all"
                >
                  <div className="flex items-center">
                    <div className={`p-2 rounded-lg ${action.color} text-white`}>
                      <action.icon className="h-5 w-5" />
                    </div>
                    <div className="ml-4">
                      <h3 className="text-sm font-medium text-gray-900 group-hover:text-blue-600">
                        {action.title}
                      </h3>
                      <p className="text-sm text-gray-500">{action.description}</p>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Upcoming Meetings */}
        <div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="card"
          >
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Upcoming Meetings</h2>
            {upcomingMeetings.length > 0 ? (
              <div className="space-y-4">
                {upcomingMeetings.map((meeting) => (
                  <div key={meeting.id} className="flex items-start space-x-3">
                    <div className="flex-shrink-0">
                      <div className="w-2 h-2 bg-green-400 rounded-full mt-2"></div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {meeting.title}
                      </p>
                      <p className="text-sm text-gray-500">
                        {new Date(meeting.start_time).toLocaleDateString()} at{' '}
                        {new Date(meeting.start_time).toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <CalendarIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No upcoming meetings</p>
                <div className="mt-2 space-y-2">
                  <Link
                    to="/scheduling-agent"
                    className="inline-flex items-center text-sm text-blue-600 hover:text-blue-500"
                  >
                    Schedule a meeting
                    <PlusIcon className="ml-1 h-4 w-4" />
                  </Link>
                  <br />
                  <Link
                    to="/calendar"
                    className="inline-flex items-center text-sm text-gray-600 hover:text-gray-500"
                  >
                    View calendar
                    <CalendarIcon className="ml-1 h-4 w-4" />
                  </Link>
                </div>
              </div>
            )}
          </motion.div>
        </div>
      </div>

      {/* Recent Activity */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
        className="mt-8 card"
      >
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Recent Activity</h2>
        <div className="space-y-4">
          {userMeetings?.slice(0, 5).map((meeting) => (
            <div key={meeting.id} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0">
              <div className="flex items-center space-x-3">
                <div className={`w-2 h-2 rounded-full ${
                  meeting.status === 'confirmed' ? 'bg-green-400' :
                  meeting.status === 'proposed' ? 'bg-yellow-400' : 'bg-gray-400'
                }`}></div>
                <div>
                  <p className="text-sm font-medium text-gray-900">{meeting.title}</p>
                  <p className="text-sm text-gray-500">
                    {new Date(meeting.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                meeting.status === 'confirmed' ? 'bg-green-100 text-green-800' :
                meeting.status === 'proposed' ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-800'
              }`}>
                {meeting.status}
              </span>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};

export default Dashboard; 