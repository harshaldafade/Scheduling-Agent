export interface User {
  id: number;
  email: string;
  name: string;
  timezone: string;
  preferences: Record<string, any>;
  availability_patterns: Record<string, any>;
  created_at: string;
  updated_at?: string;
  is_active: boolean;
}

export interface Meeting {
  id: number;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  duration_minutes: number;
  organizer_id: number;
  participants: number[];
  status: 'proposed' | 'confirmed' | 'cancelled';
  meeting_type: string;
  constraints: Record<string, any>;
  created_at: string;
  updated_at?: string;
}

export interface Schedule {
  id: number;
  user_id: number;
  date: string;
  available_slots: Array<{
    start: string;
    end: string;
  }>;
  busy_slots: Array<{
    start: string;
    end: string;
  }>;
  created_at: string;
  updated_at?: string;
}

export interface SchedulingRequest {
  user_id: number;
  request_text: string;
  participants?: number[];
  duration_minutes?: number;
  meeting_type?: string;
  constraints?: Record<string, any>;
}

export interface SchedulingResponse {
  success: boolean;
  message: string;
  action?: string;
  meeting_proposal?: Record<string, any>;
  alternative_slots?: Array<Record<string, any>>;
  meetings?: Array<Record<string, any>>;
  agent_reasoning?: string;
  meeting_to_delete?: Record<string, any>;
  meetings_to_delete?: Array<Record<string, any>>;
  available_meetings?: Array<Record<string, any>>;
  raw_ai_output?: string;
}

export interface MeetingProposal {
  title: string;
  description?: string;
  organizer_id: number;
  participants: number[];
  start_time: string;
  end_time: string;
  meeting_type: string;
  constraints?: Record<string, any>;
}

export interface UserPreferences {
  preferred_time_slots?: string[];
  preferred_duration?: string;
  preferred_meeting_types?: string[];
  timezone?: string;
  availability_patterns?: Record<string, any>;
  feedback_sentiment?: 'positive' | 'negative' | 'neutral';
}

export interface PreferenceRecommendations {
  preferred_meeting_times: string[];
  preferred_meeting_duration: string;
  preferred_meeting_types: string[];
  similar_user_patterns: Record<string, any>;
  suggested_improvements: string[];
}

export interface SimilarUser {
  user_id: number;
  name: string;
  email: string;
  similarity_score: number;
  preferences: Record<string, any>;
}

export interface AgentMessage {
  id: string;
  type: 'user' | 'agent';
  content: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface VoiceState {
  isListening: boolean;
  isSpeaking: boolean;
  transcript: string;
  error?: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
} 