import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { 
  ChevronLeftIcon, 
  ChevronRightIcon,
  CalendarIcon,
  ClockIcon,
  UserGroupIcon,
  PlusIcon
} from '@heroicons/react/outline';
import { apiService } from '../services/api';
import { useAuth } from '../hooks/useAuth';
import { Meeting } from '../types';

const Calendar: React.FC = () => {
  const { currentUser } = useAuth();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);

  // Fetch user meetings
  const { data: meetings, isLoading } = useQuery({
    queryKey: ['userMeetings'],
    queryFn: () => apiService.getUserMeetings(),
    enabled: !!currentUser,
  });

  // Get calendar data for current month
  const getCalendarDays = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());
    
    const days = [];
    const current = new Date(startDate);
    
    while (current <= lastDay || current.getDay() !== 0) {
      days.push(new Date(current));
      current.setDate(current.getDate() + 1);
    }
    
    return days;
  };

  // Get meetings for a specific date
  const getMeetingsForDate = (date: Date) => {
    if (!meetings) return [];
    
    return meetings.filter(meeting => {
      const meetingDate = new Date(meeting.start_time);
      return (
        meetingDate.getDate() === date.getDate() &&
        meetingDate.getMonth() === date.getMonth() &&
        meetingDate.getFullYear() === date.getFullYear()
      );
    });
  };

  // Navigate to previous month
  const goToPreviousMonth = () => {
    setCurrentDate(prev => new Date(prev.getFullYear(), prev.getMonth() - 1, 1));
  };

  // Navigate to next month
  const goToNextMonth = () => {
    setCurrentDate(prev => new Date(prev.getFullYear(), prev.getMonth() + 1, 1));
  };

  // Navigate to today
  const goToToday = () => {
    setCurrentDate(new Date());
    setSelectedDate(new Date());
  };

  const calendarDays = getCalendarDays();
  const today = new Date();

  if (!currentUser) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="text-center py-12">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Calendar</h1>
          <p className="text-gray-600">Please log in to view your calendar.</p>
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
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Calendar</h1>
            <p className="text-gray-600">
              View and manage your meetings in calendar format
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

      {/* Calendar Navigation */}
      <div className="card mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={goToPreviousMonth}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ChevronLeftIcon className="h-5 w-5" />
            </button>
            
            <h2 className="text-xl font-semibold text-gray-900">
              {currentDate.toLocaleDateString('en-US', { 
                month: 'long', 
                year: 'numeric' 
              })}
            </h2>
            
            <button
              onClick={goToNextMonth}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ChevronRightIcon className="h-5 w-5" />
            </button>
          </div>
          
          <button
            onClick={goToToday}
            className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors"
          >
            Today
          </button>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="card">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="spinner"></div>
            <span className="ml-2 text-gray-600">Loading calendar...</span>
          </div>
        ) : (
          <div className="grid grid-cols-7 gap-px bg-gray-200">
            {/* Day Headers */}
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
              <div key={day} className="bg-gray-50 p-3 text-center">
                <span className="text-sm font-medium text-gray-700">{day}</span>
              </div>
            ))}
            
            {/* Calendar Days */}
            {calendarDays.map((date, index) => {
              const isCurrentMonth = date.getMonth() === currentDate.getMonth();
              const isToday = date.toDateString() === today.toDateString();
              const isSelected = selectedDate && date.toDateString() === selectedDate.toDateString();
              const dayMeetings = getMeetingsForDate(date);
              
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: index * 0.01 }}
                  className={`min-h-[120px] bg-white p-2 cursor-pointer transition-colors ${
                    isSelected ? 'ring-2 ring-blue-500' : ''
                  } ${!isCurrentMonth ? 'bg-gray-50' : ''}`}
                  onClick={() => setSelectedDate(date)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className={`text-sm font-medium ${
                      isToday 
                        ? 'bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center'
                        : isCurrentMonth 
                          ? 'text-gray-900' 
                          : 'text-gray-400'
                    }`}>
                      {date.getDate()}
                    </span>
                  </div>
                  
                  {/* Meetings for this day */}
                  <div className="space-y-1">
                    {dayMeetings.slice(0, 3).map((meeting) => (
                      <div
                        key={meeting.id}
                        className={`text-xs p-1 rounded truncate ${
                          meeting.status === 'confirmed' 
                            ? 'bg-green-100 text-green-800' 
                            : meeting.status === 'proposed'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                        title={`${meeting.title} - ${new Date(meeting.start_time).toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}`}
                      >
                        {meeting.title}
                      </div>
                    ))}
                    {dayMeetings.length > 3 && (
                      <div className="text-xs text-gray-500 text-center">
                        +{dayMeetings.length - 3} more
                      </div>
                    )}
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>

      {/* Selected Date Details */}
      {selectedDate && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 card"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {selectedDate.toLocaleDateString('en-US', { 
              weekday: 'long', 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}
          </h3>
          
          {(() => {
            const selectedDateMeetings = getMeetingsForDate(selectedDate);
            
            if (selectedDateMeetings.length === 0) {
              return (
                <div className="text-center py-8">
                  <CalendarIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">No meetings scheduled for this date</p>
                  <button
                    onClick={() => window.location.href = '/scheduling-agent'}
                    className="mt-4 btn-primary flex items-center space-x-2 mx-auto"
                  >
                    <PlusIcon className="h-4 w-4" />
                    <span>Schedule Meeting</span>
                  </button>
                </div>
              );
            }
            
            return (
              <div className="space-y-4">
                {selectedDateMeetings.map((meeting) => (
                  <div key={meeting.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 mb-1">{meeting.title}</h4>
                        {meeting.description && (
                          <p className="text-sm text-gray-600 mb-2">{meeting.description}</p>
                        )}
                        
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <div className="flex items-center space-x-1">
                            <ClockIcon className="h-4 w-4" />
                            <span>
                              {new Date(meeting.start_time).toLocaleTimeString([], {
                                hour: '2-digit',
                                minute: '2-digit'
                              })} - {new Date(meeting.end_time).toLocaleTimeString([], {
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </span>
                          </div>
                          
                          <div className="flex items-center space-x-1">
                            <UserGroupIcon className="h-4 w-4" />
                            <span>{meeting.participants.length} participants</span>
                          </div>
                          
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                            meeting.status === 'confirmed' 
                              ? 'bg-green-100 text-green-800' 
                              : meeting.status === 'proposed'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            {meeting.status}
                          </span>
                        </div>
                      </div>
                      
                      <div className="flex-shrink-0 ml-4">
                        <span className="text-sm text-gray-500">
                          {meeting.duration_minutes} min
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            );
          })()}
        </motion.div>
      )}
    </div>
  );
};

export default Calendar; 