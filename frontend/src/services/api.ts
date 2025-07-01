import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  User, 
  Meeting, 
  SchedulingRequest, 
  SchedulingResponse, 
  MeetingProposal,
  UserPreferences,
  PreferenceRecommendations,
  SimilarUser,
  ApiResponse 
} from '../types';

// Use relative path for proxy configuration
const API_BASE_URL = '/api/v1';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.api.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor with token refresh
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          // Try to refresh token
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            try {
              const response = await this.refreshToken(refreshToken);
              localStorage.setItem('auth_token', response.access_token);
              if (response.refresh_token) {
                localStorage.setItem('refresh_token', response.refresh_token);
              }
              
              // Retry original request
              originalRequest.headers.Authorization = `Bearer ${response.access_token}`;
              return this.api(originalRequest);
            } catch (refreshError) {
              // Refresh failed, redirect to login
              localStorage.removeItem('auth_token');
              localStorage.removeItem('refresh_token');
              localStorage.removeItem('current_user');
              window.location.href = '/login';
              return Promise.reject(refreshError);
            }
          } else {
            // No refresh token, redirect to login
            localStorage.removeItem('auth_token');
            localStorage.removeItem('current_user');
            window.location.href = '/login';
          }
        }
        
        return Promise.reject(error);
      }
    );
  }

  // OAuth Authentication endpoints
  async getOAuthUrls(): Promise<{ oauth_urls: { google?: { url: string; state: string }; github?: { url: string; state: string } } }> {
    const response: AxiosResponse<{ oauth_urls: { google?: { url: string; state: string }; github?: { url: string; state: string } } }> = await this.api.get('/auth/oauth-urls');
    return response.data;
  }

  async handleOAuthCallback(provider: string, code: string, state?: string): Promise<{ access_token: string; refresh_token?: string; user: User }> {
    const response: AxiosResponse<{ access_token: string; refresh_token?: string; user: User }> = await this.api.post(`/auth/${provider}/callback`, 
      { code, state },
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse<User> = await this.api.get('/auth/me');
    return response.data;
  }

  async refreshToken(refreshToken: string): Promise<{ access_token: string; refresh_token?: string; user: User }> {
    const response: AxiosResponse<{ access_token: string; refresh_token?: string; user: User }> = await this.api.post('/auth/refresh', {
      refresh_token: refreshToken
    });
    return response.data;
  }

  async logout(): Promise<void> {
    try {
      await this.api.post('/auth/logout');
    } finally {
      // Always clear local storage
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('current_user');
      localStorage.removeItem('oauth_state_google');
      localStorage.removeItem('oauth_state_github');
      // Add any other session keys here if needed
      window.location.href = '/login';
      window.location.reload();
    }
  }

  // User endpoints
  async getUsers(): Promise<User[]> {
    const response: AxiosResponse<User[]> = await this.api.get('/users');
    return response.data;
  }

  async getUser(userId: number): Promise<User> {
    const response: AxiosResponse<User> = await this.api.get(`/users/${userId}`);
    return response.data;
  }

  async createUser(userData: Partial<User>): Promise<User> {
    const response: AxiosResponse<User> = await this.api.post('/users', userData);
    return response.data;
  }

  async updateUser(userId: number, userData: Partial<User>): Promise<User> {
    const response: AxiosResponse<User> = await this.api.put(`/users/${userId}`, userData);
    return response.data;
  }

  async deleteUser(userId: number): Promise<void> {
    await this.api.delete(`/users/${userId}`);
  }

  // Scheduling endpoints
  async scheduleMeeting(request: SchedulingRequest): Promise<SchedulingResponse> {
    const response: AxiosResponse<SchedulingResponse> = await this.api.post('/schedule', request);
    return response.data;
  }

  async confirmAction(data: {
    meeting_id: number;
    action: string;
    updates?: any;
  }): Promise<SchedulingResponse> {
    const response: AxiosResponse<SchedulingResponse> = await this.api.post('/confirm-action', data);
    return response.data;
  }

  async proposeMeeting(proposal: MeetingProposal): Promise<ApiResponse> {
    const response: AxiosResponse<ApiResponse> = await this.api.post('/propose-meeting', proposal);
    return response.data;
  }

  async resolveConflicts(meetingId: number, conflictType: string, userFeedback?: string): Promise<ApiResponse> {
    const response: AxiosResponse<ApiResponse> = await this.api.post('/resolve-conflicts', {
      meeting_id: meetingId,
      conflict_type: conflictType,
      user_feedback: userFeedback,
    });
    return response.data;
  }

  async getUserMeetings(status?: string): Promise<Meeting[]> {
    const params = status ? { status } : {};
    const response: AxiosResponse<Meeting[]> = await this.api.get('/meetings', { params });
    return response.data;
  }

  async getMeetingSuggestions(
    userId: number, 
    participantIds: number[], 
    durationMinutes: number = 60,
    startDate?: string,
    endDate?: string
  ): Promise<ApiResponse> {
    const params = {
      participant_ids: participantIds.join(','),
      duration_minutes: durationMinutes,
      start_date: startDate,
      end_date: endDate,
    };
    const response: AxiosResponse<ApiResponse> = await this.api.get('/suggestions', { params });
    return response.data;
  }

  // Preference endpoints
  async getUserPreferences(): Promise<UserPreferences> {
    const response: AxiosResponse<{ preferences: UserPreferences }> = await this.api.get('/preferences');
    return response.data.preferences;
  }

  async updateUserPreferences(preferences: UserPreferences): Promise<ApiResponse> {
    const response: AxiosResponse<ApiResponse> = await this.api.put('/preferences', {
      preferences,
    });
    return response.data;
  }

  async processFeedback(feedback: string, meetingContext?: Record<string, any>): Promise<ApiResponse> {
    const response: AxiosResponse<ApiResponse> = await this.api.post('/preferences/feedback', {
      feedback,
      meeting_context: meetingContext,
    });
    return response.data;
  }

  async findSimilarUsers(limit: number = 5): Promise<SimilarUser[]> {
    const response: AxiosResponse<{ similar_users: SimilarUser[] }> = await this.api.post('/preferences/similar-users', {
      limit,
    });
    return response.data.similar_users;
  }

  async getPreferenceRecommendations(): Promise<PreferenceRecommendations> {
    const response: AxiosResponse<{ recommendations: PreferenceRecommendations }> = await this.api.get('/preferences/recommendations');
    return response.data.recommendations;
  }

  async getPreferenceAnalytics(): Promise<ApiResponse> {
    const response: AxiosResponse<ApiResponse> = await this.api.get('/preferences/analytics');
    return response.data;
  }

  // Learning endpoints
  async learnPreferences(userId: number, feedback: string, meetingContext?: Record<string, any>): Promise<ApiResponse> {
    const response: AxiosResponse<ApiResponse> = await this.api.post('/learn-preferences', {
      user_id: userId,
      feedback,
      meeting_context: meetingContext,
    });
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response: AxiosResponse<{ status: string }> = await this.api.get('/health');
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService; 