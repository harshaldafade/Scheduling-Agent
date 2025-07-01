import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { 
  UserGroupIcon, 
  PlusIcon,
  SearchIcon,
  MailIcon,
  ClockIcon,
  GlobeAltIcon
} from '@heroicons/react/outline';
import { apiService } from '../services/api';
import { useAuth } from '../hooks/useAuth';

const Users: React.FC = () => {
  const { currentUser } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');

  const { data: users, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: () => apiService.getUsers(),
  });

  const filteredUsers = users?.filter(user => 
    user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  if (!currentUser) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="text-center py-12">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Team Members</h1>
          <p className="text-gray-600">Please log in to view team members.</p>
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
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Team Members</h1>
            <p className="text-gray-600">
              View and manage your team members for scheduling coordination
            </p>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="btn-primary flex items-center space-x-2"
            onClick={() => window.location.href = '/scheduling-agent'}
          >
            <PlusIcon className="h-4 w-4" />
            <span>Invite Member</span>
          </motion.button>
        </div>
      </div>

      {/* Search */}
      <div className="card mb-6">
        <div className="relative">
          <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search team members..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Users Grid */}
      {isLoading ? (
        <div className="card">
          <div className="flex items-center justify-center py-12">
            <div className="spinner"></div>
            <span className="ml-2 text-gray-600">Loading team members...</span>
          </div>
        </div>
      ) : filteredUsers.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredUsers.map((user, index) => (
            <motion.div
              key={user.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="card hover:shadow-md transition-shadow"
            >
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-lg">
                      {user.name.charAt(0).toUpperCase()}
                    </span>
                  </div>
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <h3 className="text-lg font-semibold text-gray-900 truncate">
                      {user.name}
                    </h3>
                    {user.id === currentUser.id && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        You
                      </span>
                    )}
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2 text-sm text-gray-500">
                      <MailIcon className="h-4 w-4" />
                      <span className="truncate">{user.email}</span>
                    </div>
                    
                    <div className="flex items-center space-x-2 text-sm text-gray-500">
                      <GlobeAltIcon className="h-4 w-4" />
                      <span>{user.timezone}</span>
                    </div>
                    
                    <div className="flex items-center space-x-2 text-sm text-gray-500">
                      <ClockIcon className="h-4 w-4" />
                      <span>
                        {user.preferences?.preferred_time_slots?.length > 0
                          ? user.preferences.preferred_time_slots.join(', ')
                          : 'No preferences set'}
                      </span>
                    </div>
                  </div>
                  
                  <div className="mt-4 flex space-x-2">
                    <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                      View Profile
                    </button>
                    <button className="text-green-600 hover:text-green-800 text-sm font-medium">
                      Schedule Meeting
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="card">
          <div className="text-center py-12">
            <UserGroupIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No team members found</h3>
            <p className="text-gray-500 mb-6">
              {searchTerm ? 'No team members match your search criteria.' : 'You don\'t have any team members yet.'}
            </p>
            <button
              onClick={() => window.location.href = '/scheduling-agent'}
              className="btn-primary flex items-center space-x-2 mx-auto"
            >
              <PlusIcon className="h-4 w-4" />
              <span>Invite Your First Team Member</span>
            </button>
          </div>
        </div>
      )}

      {/* Team Stats */}
      {users && users.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-8 card"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Team Statistics</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{users.length}</p>
              <p className="text-sm text-gray-600">Total Members</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {users.filter(u => u.preferences && Object.keys(u.preferences).length > 0).length}
              </p>
              <p className="text-sm text-gray-600">With Preferences</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">
                {new Set(users.map(u => u.timezone)).size}
              </p>
              <p className="text-sm text-gray-600">Time Zones</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-orange-600">
                {users.filter(u => u.is_active).length}
              </p>
              <p className="text-sm text-gray-600">Active Members</p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default Users; 