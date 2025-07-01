import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { 
  CalendarIcon, 
  ClockIcon, 
  UserGroupIcon,
  PlusIcon,
  SearchIcon
} from '@heroicons/react/outline';
import { apiService } from '../services/api';
import { useAuth } from '../hooks/useAuth';
import { Meeting } from '../types';

const Meetings: React.FC = () => {
  const { currentUser } = useAuth();
  const [filter, setFilter] = useState<'all' | 'upcoming' | 'past' | 'pending'>('all');
  const [searchTerm, setSearchTerm] = useState('');

  const { data: meetings, isLoading } = useQuery({
    queryKey: ['userMeetings'],
    queryFn: () => apiService.getUserMeetings(),
    enabled: !!currentUser,
  });

  const filteredMeetings = meetings?.filter(meeting => {
    const matchesSearch = meeting.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         meeting.description?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const now = new Date();
    const meetingDate = new Date(meeting.start_time);
    
    switch (filter) {
      case 'upcoming':
        return meetingDate > now && meeting.status === 'confirmed' && matchesSearch;
      case 'past':
        return meetingDate < now && matchesSearch;
      case 'pending':
        return meeting.status === 'proposed' && matchesSearch;
      default:
        return matchesSearch;
    }
  }) || [];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'bg-green-100 text-green-800';
      case 'proposed':
        return 'bg-yellow-100 text-yellow-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getMeetingTypeIcon = (type: string) => {
    switch (type) {
      case 'team_meeting':
        return <UserGroupIcon className="h-5 w-5 text-blue-600" />;
      case 'interview':
        return <UserGroupIcon className="h-5 w-5 text-green-600" />;
      case 'client_meeting':
        return <UserGroupIcon className="h-5 w-5 text-purple-600" />;
      default:
        return <CalendarIcon className="h-5 w-5 text-gray-600" />;
    }
  };

  if (!currentUser) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="text-center py-12">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Meetings</h1>
          <p className="text-gray-600">Please log in to view your meetings.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Meetings</h1>
            <p className="text-gray-600">
              Manage and view all your scheduled meetings
            </p>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="btn-primary flex items-center space-x-2"
            onClick={() => window.location.href = '/scheduling-agent'}
          >
            <PlusIcon className="h-4 w-4" />
            <span>New Meeting</span>
          </motion.button>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="card mb-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          {/* Filter Tabs */}
          <div className="flex space-x-1">
            {[
              { key: 'all', label: 'All Meetings' },
              { key: 'upcoming', label: 'Upcoming' },
              { key: 'past', label: 'Past' },
              { key: 'pending', label: 'Pending' },
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setFilter(tab.key as any)}
                className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                  filter === tab.key
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Search */}
          <div className="relative">
            <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search meetings..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Meetings List */}
      {isLoading ? (
        <div className="card">
          <div className="flex items-center justify-center py-12">
            <div className="spinner"></div>
            <span className="ml-2 text-gray-600">Loading meetings...</span>
          </div>
        </div>
      ) : filteredMeetings.length > 0 ? (
        <div className="space-y-4">
          {filteredMeetings.map((meeting, index) => (
            <motion.div
              key={meeting.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="card hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    {getMeetingTypeIcon(meeting.meeting_type)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 truncate">
                        {meeting.title}
                      </h3>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(meeting.status)}`}>
                        {meeting.status}
                      </span>
                    </div>
                    
                    {meeting.description && (
                      <p className="text-gray-600 mb-3 line-clamp-2">
                        {meeting.description}
                      </p>
                    )}
                    
                    <div className="flex items-center space-x-6 text-sm text-gray-500">
                      <div className="flex items-center space-x-1">
                        <CalendarIcon className="h-4 w-4" />
                        <span>
                          {new Date(meeting.start_time).toLocaleDateString()}
                        </span>
                      </div>
                      
                      <div className="flex items-center space-x-1">
                        <ClockIcon className="h-4 w-4" />
                        <span>
                          {new Date(meeting.start_time).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                          })} - {new Date(meeting.end_time).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </span>
                      </div>
                      
                      <div className="flex items-center space-x-1">
                        <UserGroupIcon className="h-4 w-4" />
                        <span>{meeting.participants.length} participants</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="flex-shrink-0 ml-4">
                  <div className="flex flex-col items-end space-y-2">
                    <span className="text-sm text-gray-500">
                      {meeting.duration_minutes} min
                    </span>
                    
                    <div className="flex space-x-2">
                      <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                        View Details
                      </button>
                      {meeting.status === 'proposed' && (
                        <>
                          <button className="text-green-600 hover:text-green-800 text-sm font-medium">
                            Accept
                          </button>
                          <button className="text-red-600 hover:text-red-800 text-sm font-medium">
                            Decline
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="card">
          <div className="text-center py-12">
            <CalendarIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No meetings found</h3>
            <p className="text-gray-500 mb-6">
              {searchTerm ? 'No meetings match your search criteria.' : 'You don\'t have any meetings yet.'}
            </p>
            <button
              onClick={() => window.location.href = '/scheduling-agent'}
              className="btn-primary flex items-center space-x-2 mx-auto"
            >
              <PlusIcon className="h-4 w-4" />
              <span>Schedule Your First Meeting</span>
            </button>
          </div>
        </div>
      )}

      {/* Stats */}
      {meetings && meetings.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-8 card"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Meeting Statistics</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{meetings.length}</p>
              <p className="text-sm text-gray-600">Total Meetings</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {meetings.filter(m => m.status === 'confirmed' && new Date(m.start_time) > new Date()).length}
              </p>
              <p className="text-sm text-gray-600">Upcoming</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">
                {meetings.filter(m => m.status === 'proposed').length}
              </p>
              <p className="text-sm text-gray-600">Pending</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-600">
                {meetings.filter(m => new Date(m.start_time) < new Date()).length}
              </p>
              <p className="text-sm text-gray-600">Past</p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default Meetings; 