import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useMutation } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { 
  PaperAirplaneIcon, 
  ClockIcon,
  UserGroupIcon,
  CalendarIcon,
  ExclamationCircleIcon
} from '@heroicons/react/outline';
import { AgentMessage, VoiceState, SchedulingRequest } from '../types';
import { apiService } from '../services/api';
import { useAuth } from '../hooks/useAuth';
import VoiceInterface from '../components/VoiceInterface';

const SchedulingAgent: React.FC = () => {
  const { currentUser } = useAuth();
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [voiceState, setVoiceState] = useState<VoiceState>({
    isListening: false,
    isSpeaking: false,
    transcript: '',
  });
  const [confirmationData, setConfirmationData] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Initialize with welcome message
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          id: '1',
          type: 'agent',
          content: `Hello ${currentUser?.name || 'there'}! I'm your AI Scheduling Agent. I can help you schedule meetings, coordinate with participants, and learn your preferences. How can I assist you today?`,
          timestamp: new Date().toISOString(),
        },
      ]);
    }
  }, [currentUser, messages.length]);

  // Confirmation mutation
  const confirmMutation = useMutation({
    mutationFn: (data: any) => apiService.confirmAction(data),
    onSuccess: (response) => {
      const agentMessage: AgentMessage = {
        id: Date.now().toString(),
        type: 'agent',
        content: response.message,
        timestamp: new Date().toISOString(),
        metadata: {
          meeting_proposal: response.meeting_proposal,
        },
      };
      setMessages(prev => [...prev, agentMessage]);
      setConfirmationData(null);
      setIsProcessing(false);
      
      if (response.success) {
        toast.success('Action completed successfully!');
      }
    },
    onError: (error: any) => {
      const errorMessage: AgentMessage = {
        id: Date.now().toString(),
        type: 'agent',
        content: `I apologize, but I encountered an error: ${error.message || 'Something went wrong'}. Please try again.`,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
      setConfirmationData(null);
      setIsProcessing(false);
      toast.error('Failed to complete action');
    },
  });

  // Scheduling mutation
  const scheduleMutation = useMutation({
    mutationFn: (request: SchedulingRequest) => apiService.scheduleMeeting(request),
    onSuccess: (response) => {
      // Check if this is a confirmation request
      if (response.action && response.action.startsWith('CONFIRM_')) {
        setConfirmationData({
          action: response.action,
          message: response.message,
          meeting_to_delete: response.meeting_to_delete,
          meetings_to_delete: response.meetings_to_delete,
          available_meetings: response.available_meetings,
        });
        setIsProcessing(false);
        return;
      }

      // If the response is not successful and has raw_ai_output, show it
      let content = response.message ?? response.agent_reasoning ?? '';
      if (response.raw_ai_output) {
        content += `\n\nAI raw output: ${response.raw_ai_output}`;
      }

      const agentMessage: AgentMessage = {
        id: Date.now().toString(),
        type: 'agent',
        content,
        timestamp: new Date().toISOString(),
        metadata: {
          meeting_proposal: response.meeting_proposal,
          alternative_slots: response.alternative_slots,
          meetings: response.meetings,
        },
      };
      setMessages(prev => [...prev, agentMessage]);
      setIsProcessing(false);
      
      if (response.success) {
        toast.success('Request processed successfully!');
      }
    },
    onError: (error: any) => {
      const errorMessage: AgentMessage = {
        id: Date.now().toString(),
        type: 'agent',
        content: `I apologize, but I encountered an error: ${error.message || 'Something went wrong'}. Please try again.`,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsProcessing(false);
      toast.error('Failed to schedule meeting');
    },
  });

  const handleConfirmAction = (confirmed: boolean) => {
    if (!confirmed) {
      setConfirmationData(null);
      setIsProcessing(false);
      return;
    }

    if (!confirmationData) return;

    let confirmRequest: any = {};

    if (confirmationData.action === 'CONFIRM_DELETION') {
      confirmRequest = {
        meeting_id: confirmationData.meeting_to_delete.id,
        action: 'confirm_delete'
      };
    } else if (confirmationData.action === 'CONFIRM_DELETE_ALL') {
      confirmRequest = {
        meeting_id: 0, // Not used for bulk delete
        action: 'confirm_delete_all'
      };
    } else if (confirmationData.action === 'CONFIRM_UPDATE') {
      confirmRequest = {
        meeting_id: confirmationData.meeting_to_update.id,
        action: 'confirm_update',
        updates: confirmationData.updates
      };
    } else if (confirmationData.action === 'CONFIRM_CREATION') {
      confirmRequest = {
        action: 'confirm_create',
        meeting_proposal: confirmationData.meeting_proposal
      };
    }

    confirmMutation.mutate(confirmRequest);
  };

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    // Use default user ID if no current user
    const userId = currentUser?.id || 1;

    const userMessage: AgentMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputText,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsProcessing(true);

    // Send to scheduling agent
    const request: SchedulingRequest = {
      user_id: userId,
      request_text: inputText,
    };

    scheduleMutation.mutate(request);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleVoiceInput = (transcript: string) => {
    setInputText(transcript);
    setVoiceState(prev => ({ ...prev, transcript }));
  };

  const handleVoiceSubmit = () => {
    if (voiceState.transcript.trim()) {
      setInputText(voiceState.transcript);
      setVoiceState(prev => ({ ...prev, transcript: '' }));
      handleSendMessage();
    }
  };

  const renderConfirmationDialog = () => {
    if (!confirmationData) return null;

    // Handle meeting creation confirmation
    if (confirmationData.action === 'CONFIRM_CREATION') {
      const proposal = confirmationData.meeting_proposal;
      return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-center space-x-3 mb-4">
              <ExclamationCircleIcon className="h-6 w-6 text-yellow-500" />
              <h3 className="text-lg font-semibold text-gray-900">Confirm Meeting Creation</h3>
            </div>
            <p className="text-gray-700 mb-6">{confirmationData.message}</p>
            <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-4">
              <p className="text-sm text-green-800"><strong>Title:</strong> {proposal.title}</p>
              <p className="text-sm text-green-700"><strong>Time:</strong> {new Date(proposal.start_time).toLocaleString()}</p>
              <p className="text-sm text-green-700"><strong>Duration:</strong> {proposal.duration_minutes} minutes</p>
              {proposal.location && <p className="text-sm text-green-700"><strong>Location:</strong> {proposal.location}</p>}
              {proposal.description && <p className="text-sm text-green-700"><strong>Description:</strong> {proposal.description}</p>}
            </div>
            <div className="flex space-x-3">
              <button
                onClick={() => handleConfirmAction(false)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => handleConfirmAction(true)}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      );
    }

    // ... existing code for deletion/update confirmation ...

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
          <div className="flex items-center space-x-3 mb-4">
            <ExclamationCircleIcon className="h-6 w-6 text-yellow-500" />
            <h3 className="text-lg font-semibold text-gray-900">Confirm Action</h3>
          </div>
          
          <p className="text-gray-700 mb-6">{confirmationData.message}</p>
          
          {confirmationData.meeting_to_delete && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
              <p className="text-sm text-red-800">
                <strong>Meeting to cancel:</strong> {confirmationData.meeting_to_delete.title}
              </p>
              <p className="text-sm text-red-700">
                {new Date(confirmationData.meeting_to_delete.start_time).toLocaleString()}
              </p>
            </div>
          )}
          
          {confirmationData.meetings_to_delete && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
              <p className="text-sm text-red-800 mb-2">
                <strong>Meetings to cancel:</strong>
              </p>
              <div className="space-y-1">
                {confirmationData.meetings_to_delete.map((meeting: any, index: number) => (
                  <p key={index} className="text-sm text-red-700">
                    • {meeting.title} - {meeting.date} at {meeting.start_time}
                  </p>
                ))}
              </div>
            </div>
          )}
          
          <div className="flex space-x-3">
            <button
              onClick={() => handleConfirmAction(false)}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={() => handleConfirmAction(true)}
              className="flex-1 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
            >
              Confirm
            </button>
          </div>
        </div>
      </div>
    );
  };

  const renderMessage = (message: AgentMessage) => {
    const isAgent = message.type === 'agent';
    
    return (
      <motion.div
        key={message.id}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`flex ${isAgent ? 'justify-start' : 'justify-end'} mb-4`}
      >
        <div className={`max-w-3xl ${isAgent ? 'agent-message' : 'user-message'}`}>
          <div className="flex items-start space-x-3">
            {isAgent && (
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-white font-bold text-sm">AI</span>
              </div>
            )}
            
            <div className="flex-1">
              <p className="text-sm text-gray-600 mb-1">
                {isAgent ? 'AI Agent' : currentUser?.name || 'You'}
              </p>
              <div className="prose prose-sm max-w-none">
                <p className="text-gray-900 whitespace-pre-wrap">{message.content}</p>
                
                {/* Render meeting proposal if available */}
                {message.metadata?.meeting_proposal && (
                  <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                    <h4 className="font-medium text-green-800 mb-2">Meeting Proposal</h4>
                    <div className="space-y-2 text-sm">
                      <p><strong>Title:</strong> {message.metadata.meeting_proposal.title}</p>
                      <p><strong>Time:</strong> {new Date(message.metadata.meeting_proposal.start_time).toLocaleString()}</p>
                      <p><strong>Duration:</strong> {message.metadata.meeting_proposal.duration_minutes} minutes</p>
                    </div>
                  </div>
                )}

                {/* Render alternative slots if available */}
                {message.metadata?.alternative_slots && message.metadata.alternative_slots.length > 0 && (
                  <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <h4 className="font-medium text-blue-800 mb-2">Alternative Times</h4>
                    <div className="space-y-1 text-sm">
                      {message.metadata.alternative_slots.slice(0, 3).map((slot: any, index: number) => (
                        <p key={index} className="text-blue-700">
                          {new Date(slot.start).toLocaleString()}
                        </p>
                      ))}
                    </div>
                  </div>
                )}

                {/* Render meetings if available */}
                {message.metadata?.meetings && message.metadata.meetings.length > 0 && (
                  <div className="mt-4 p-4 bg-purple-50 border border-purple-200 rounded-lg">
                    <h4 className="font-medium text-purple-800 mb-2">Your Meetings</h4>
                    <div className="space-y-3">
                      {message.metadata.meetings.map((meeting: any, index: number) => (
                        <div key={index} className="border-l-4 border-purple-400 pl-3">
                          <p className="font-medium text-purple-900">{meeting.title}</p>
                          <p className="text-sm text-purple-700">
                            {new Date(meeting.start_time).toLocaleString()} - {meeting.duration_minutes} minutes
                          </p>
                          {meeting.location && (
                            <p className="text-sm text-purple-600">📍 {meeting.location}</p>
                          )}
                          {meeting.description && (
                            <p className="text-sm text-purple-600 mt-1">{meeting.description}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              
              <p className="text-xs text-gray-500 mt-2">
                {new Date(message.timestamp).toLocaleTimeString()}
              </p>
            </div>

            {!isAgent && (
              <div className="w-8 h-8 bg-gray-400 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-white font-bold text-sm">
                  {currentUser?.name?.charAt(0) || 'U'}
                </span>
              </div>
            )}
          </div>
        </div>
      </motion.div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto">
      {renderConfirmationDialog()}
      
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Scheduling Agent</h1>
        <p className="text-gray-600">
          Chat with your intelligent scheduling assistant. I can help you schedule meetings, 
          coordinate with participants, and learn your preferences.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chat Interface */}
        <div className="lg:col-span-2">
          <div className="card h-[600px] flex flex-col">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              <AnimatePresence>
                {messages.map(renderMessage)}
              </AnimatePresence>
              
              {isProcessing && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex justify-start"
                >
                  <div className="agent-message">
                    <div className="flex items-center space-x-2">
                      <div className="spinner"></div>
                      <span className="text-gray-600">AI is thinking...</span>
                    </div>
                  </div>
                </motion.div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t border-gray-200 p-4">
              <div className="flex space-x-2">
                <div className="flex-1">
                  <textarea
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Describe your scheduling needs... (e.g., 'Schedule a 1-hour team meeting with John and Sarah next week')"
                    className="input-field resize-none"
                    rows={3}
                    disabled={isProcessing}
                  />
                </div>
                
                <div className="flex flex-col space-y-2">
                  <button
                    onClick={handleSendMessage}
                    disabled={!inputText.trim() || isProcessing}
                    className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <PaperAirplaneIcon className="h-4 w-4" />
                  </button>
                  
                  <VoiceInterface
                    onTranscript={handleVoiceInput}
                    onSubmit={handleVoiceSubmit}
                    isProcessing={isProcessing}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <button
                onClick={() => setInputText("Schedule a 30-minute meeting with the development team tomorrow")}
                className="w-full text-left p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center space-x-2">
                  <CalendarIcon className="h-5 w-5 text-blue-600" />
                  <span className="text-sm text-gray-700">Schedule Team Meeting</span>
                </div>
              </button>
              
              <button
                onClick={() => setInputText("Find available time slots for a 1-hour interview with 3 candidates")}
                className="w-full text-left p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center space-x-2">
                  <UserGroupIcon className="h-5 w-5 text-green-600" />
                  <span className="text-sm text-gray-700">Schedule Interview</span>
                </div>
              </button>
              
              <button
                onClick={() => setInputText("Check my availability for next week and suggest optimal meeting times")}
                className="w-full text-left p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center space-x-2">
                  <ClockIcon className="h-5 w-5 text-purple-600" />
                  <span className="text-sm text-gray-700">Check Availability</span>
                </div>
              </button>
            </div>
          </div>

          {/* Agent Status */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Agent Status</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Status</span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Active
                </span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Memory</span>
                <span className="text-sm text-gray-900">Learning enabled</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Voice</span>
                <span className="text-sm text-gray-900">Available</span>
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
            <div className="space-y-2">
              {messages.slice(-3).map((message) => (
                <div key={message.id} className="text-sm text-gray-600">
                  <span className="font-medium">
                    {message.type === 'agent' ? 'AI' : currentUser?.name || 'You'}:
                  </span>
                  <span className="ml-1 truncate block">
                    {message.content.substring(0, 50)}...
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SchedulingAgent; 