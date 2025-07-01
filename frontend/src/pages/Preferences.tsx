import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { 
  CogIcon, 
  ChartBarIcon, 
  CheckCircleIcon,
  LightBulbIcon
} from '@heroicons/react/outline';
import { apiService } from '../services/api';
import { useAuth } from '../hooks/useAuth';
import { UserPreferences, PreferenceRecommendations } from '../types';

// Type definitions for API responses
interface PreferenceAnalytics {
  total_preferences: number;
  preference_completeness: number;
  preference_categories: string[];
}

const Preferences: React.FC = () => {
  const { currentUser } = useAuth();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<'preferences' | 'analytics' | 'learning'>('preferences');
  const [feedback, setFeedback] = useState('');

  // Fetch user preferences
  const { data: userPreferences = {} as UserPreferences, isLoading: userPreferencesLoading } = useQuery({
    queryKey: ['userPreferences'],
    queryFn: async () => {
      if (!currentUser) return {} as UserPreferences;
      return await apiService.getUserPreferences();
    },
    enabled: !!currentUser,
  });

  // Fetch preference recommendations
  const { data: recommendations = {} as PreferenceRecommendations, isLoading: recommendationsLoading } = useQuery({
    queryKey: ['preferenceRecommendations'],
    queryFn: async () => {
      if (!currentUser) return {} as PreferenceRecommendations;
      return await apiService.getPreferenceRecommendations();
    },
    enabled: !!currentUser,
  });

  // Fetch similar users
  const { data: similarUsers, isLoading: similarUsersLoading } = useQuery({
    queryKey: ['similarUsers'],
    queryFn: () => currentUser ? apiService.findSimilarUsers(5) : Promise.resolve([]),
    enabled: !!currentUser,
  });

  // Fetch preference analytics
  const { data: analytics = {} as PreferenceAnalytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['preferenceAnalytics'],
    queryFn: async () => {
      if (!currentUser) return {} as PreferenceAnalytics;
      const response = await apiService.getPreferenceAnalytics();
      return response.data || {} as PreferenceAnalytics;
    },
    enabled: !!currentUser,
  });

  // Update preferences mutation
  const updatePreferencesMutation = useMutation({
    mutationFn: (preferences: Partial<UserPreferences>) =>
      currentUser ? apiService.updateUserPreferences(preferences) : Promise.resolve({}),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['userPreferences'] });
      toast.success('Preferences updated successfully!');
    },
    onError: () => {
      toast.error('Failed to update preferences');
    },
  });

  // Process feedback mutation
  const processFeedbackMutation = useMutation({
    mutationFn: (feedback: string) =>
      currentUser ? apiService.processFeedback(feedback, {}) : Promise.resolve({}),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['userPreferences'] });
      queryClient.invalidateQueries({ queryKey: ['preferenceRecommendations'] });
      setFeedback('');
      toast.success('Feedback processed! Your preferences have been updated.');
    },
    onError: () => {
      toast.error('Failed to process feedback');
    },
  });

  const handlePreferenceUpdate = (key: keyof UserPreferences, value: any) => {
    const updatedPreferences = { ...userPreferences, [key]: value };
    updatePreferencesMutation.mutate(updatedPreferences);
  };

  const handleFeedbackSubmit = () => {
    if (feedback.trim()) {
      processFeedbackMutation.mutate(feedback);
    }
  };

  if (!currentUser) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="text-center py-12">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Preferences</h1>
          <p className="text-gray-600">Please log in to manage your preferences.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Preferences & Learning</h1>
        <p className="text-gray-600">
          Manage your scheduling preferences and see how AI learns from your behavior
        </p>
      </div>

      {/* Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { key: 'preferences', label: 'Preferences', icon: CogIcon },
              { key: 'analytics', label: 'Analytics', icon: ChartBarIcon },
              { key: 'learning', label: 'AI Learning', icon: LightBulbIcon },
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.key
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'preferences' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Current Preferences */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card"
          >
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Current Preferences</h2>
            
            {userPreferencesLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="spinner"></div>
                <span className="ml-2 text-gray-600">Loading preferences...</span>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Preferred Time Slots */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Preferred Meeting Times
                  </label>
                  <div className="space-y-2">
                    {['morning', 'afternoon', 'evening'].map((time) => (
                      <label key={time} className="flex items-center">
                        <input
                          type="checkbox"
                          checked={userPreferences?.preferred_time_slots?.includes(time) || false}
                          onChange={(e) => {
                            const current = userPreferences?.preferred_time_slots || [];
                            const updated = e.target.checked
                              ? [...current, time]
                              : current.filter((t: string) => t !== time);
                            handlePreferenceUpdate('preferred_time_slots', updated);
                          }}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="ml-2 text-sm text-gray-700 capitalize">{time}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Preferred Duration */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Preferred Meeting Duration
                  </label>
                  <select
                    value={userPreferences?.preferred_duration || 'standard'}
                    onChange={(e) => handlePreferenceUpdate('preferred_duration', e.target.value)}
                    className="input-field"
                  >
                    <option value="short">Short (15-30 min)</option>
                    <option value="standard">Standard (45-60 min)</option>
                    <option value="long">Long (90+ min)</option>
                  </select>
                </div>

                {/* Preferred Meeting Types */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Preferred Meeting Types
                  </label>
                  <div className="space-y-2">
                    {['team_meeting', 'interview', 'client_meeting', 'one_on_one'].map((type) => (
                      <label key={type} className="flex items-center">
                        <input
                          type="checkbox"
                          checked={userPreferences?.preferred_meeting_types?.includes(type) || false}
                          onChange={(e) => {
                            const current = userPreferences?.preferred_meeting_types || [];
                            const updated = e.target.checked
                              ? [...current, type]
                              : current.filter((t: string) => t !== type);
                            handlePreferenceUpdate('preferred_meeting_types', updated);
                          }}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="ml-2 text-sm text-gray-700 capitalize">
                          {type.replace('_', ' ')}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </motion.div>

          {/* Recommendations */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card"
          >
            <h2 className="text-xl font-semibold text-gray-900 mb-6">AI Recommendations</h2>
            
            {recommendationsLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="spinner"></div>
                <span className="ml-2 text-gray-600">Loading recommendations...</span>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Suggested Improvements */}
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-3">Suggested Improvements</h3>
                  <div className="space-y-2">
                    {recommendations?.suggested_improvements?.map((suggestion: string, index: number) => (
                      <div key={index} className="flex items-start space-x-2 p-3 bg-blue-50 rounded-lg">
                        <LightBulbIcon className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                        <p className="text-sm text-blue-800">{suggestion}</p>
                      </div>
                    )) || (
                      <p className="text-sm text-gray-500">No suggestions at this time.</p>
                    )}
                  </div>
                </div>

                {/* Similar User Patterns */}
                {recommendations?.similar_user_patterns && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-3">Similar User Patterns</h3>
                    <div className="space-y-2">
                      {recommendations.similar_user_patterns.common_time_slots && (
                        <div className="p-3 bg-green-50 rounded-lg">
                          <p className="text-sm text-green-800">
                            <strong>Common times:</strong> {recommendations.similar_user_patterns.common_time_slots.join(', ')}
                          </p>
                        </div>
                      )}
                      {recommendations.similar_user_patterns.common_durations && (
                        <div className="p-3 bg-purple-50 rounded-lg">
                          <p className="text-sm text-purple-800">
                            <strong>Common duration:</strong> {recommendations.similar_user_patterns.common_durations[0]}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </motion.div>
        </div>
      )}

      {activeTab === 'analytics' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Analytics Overview */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card"
          >
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Preference Analytics</h2>
            
            {analyticsLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="spinner"></div>
                <span className="ml-2 text-gray-600">Loading analytics...</span>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <p className="text-2xl font-bold text-blue-600">{analytics?.total_preferences || 0}</p>
                    <p className="text-sm text-blue-800">Total Preferences</p>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <p className="text-2xl font-bold text-green-600">
                      {Math.round((analytics?.preference_completeness || 0) * 100)}%
                    </p>
                    <p className="text-sm text-green-800">Completeness</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="text-sm font-medium text-gray-700">Preference Categories</h3>
                  <div className="space-y-2">
                    {analytics?.preference_categories?.map((category: string) => (
                      <div key={category} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <span className="text-sm text-gray-700 capitalize">{category.replace('_', ' ')}</span>
                        <CheckCircleIcon className="h-4 w-4 text-green-500" />
                      </div>
                    )) || (
                      <p className="text-sm text-gray-500">No preferences set yet.</p>
                    )}
                  </div>
                </div>
              </div>
            )}
          </motion.div>

          {/* Similar Users */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card"
          >
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Similar Users</h2>
            
            {similarUsersLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="spinner"></div>
                <span className="ml-2 text-gray-600">Loading similar users...</span>
              </div>
            ) : (
              <div className="space-y-4">
                {similarUsers?.map((user) => (
                  <div key={user.user_id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{user.name}</p>
                      <p className="text-xs text-gray-500">{user.email}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-blue-600">
                        {Math.round(user.similarity_score * 100)}% match
                      </p>
                    </div>
                  </div>
                )) || (
                  <p className="text-sm text-gray-500">No similar users found.</p>
                )}
              </div>
            )}
          </motion.div>
        </div>
      )}

      {activeTab === 'learning' && (
        <div className="space-y-8">
          {/* Feedback Input */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card"
          >
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Help AI Learn</h2>
            <p className="text-gray-600 mb-4">
              Provide feedback about your scheduling experiences to help the AI improve its suggestions.
            </p>
            
            <div className="space-y-4">
              <textarea
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                placeholder="Share your feedback about scheduling experiences... (e.g., 'I prefer morning meetings because I'm more productive then')"
                className="input-field"
                rows={4}
              />
              
              <div className="flex justify-end">
                <button
                  onClick={handleFeedbackSubmit}
                  disabled={!feedback.trim() || processFeedbackMutation.isPending}
                  className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {processFeedbackMutation.isPending ? 'Processing...' : 'Submit Feedback'}
                </button>
              </div>
            </div>
          </motion.div>

          {/* Learning Examples */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card"
          >
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Learning Examples</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-blue-50 rounded-lg">
                <h3 className="font-medium text-blue-900 mb-2">Time Preferences</h3>
                <p className="text-sm text-blue-800">
                  "I prefer meetings in the morning when I'm most alert and focused."
                </p>
              </div>
              <div className="p-4 bg-green-50 rounded-lg">
                <h3 className="font-medium text-green-900 mb-2">Duration Preferences</h3>
                <p className="text-sm text-green-800">
                  "Short 30-minute meetings are more productive for quick updates."
                </p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg">
                <h3 className="font-medium text-purple-900 mb-2">Meeting Types</h3>
                <p className="text-sm text-purple-800">
                  "I enjoy team meetings but prefer one-on-ones for sensitive discussions."
                </p>
              </div>
              <div className="p-4 bg-orange-50 rounded-lg">
                <h3 className="font-medium text-orange-900 mb-2">Scheduling Patterns</h3>
                <p className="text-sm text-orange-800">
                  "I like to have breaks between meetings to process information."
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default Preferences; 