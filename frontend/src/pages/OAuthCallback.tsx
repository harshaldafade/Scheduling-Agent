import React, { useEffect, useRef } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { apiService } from '../services/api';
import { toast } from 'react-hot-toast';
import { useQueryClient } from '@tanstack/react-query';

const OAuthCallback: React.FC = () => {
  const { provider } = useParams<{ provider: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const queryClient = useQueryClient();
  const hasHandled = useRef(false);

  useEffect(() => {
    if (hasHandled.current) return;
    hasHandled.current = true;
    const handleCallback = async () => {
      try {
        // Get the authorization code and state from URL parameters
        const urlParams = new URLSearchParams(location.search);
        const code = urlParams.get('code');
        const state = urlParams.get('state');
        const error = urlParams.get('error');

        if (error) {
          toast.error(`OAuth error: ${error}`);
          navigate('/login');
          return;
        }

        if (!code || !provider) {
          toast.error('Missing authorization code or provider');
          navigate('/login');
          return;
        }

        // Validate state parameter
        const storedState = localStorage.getItem(`oauth_state_${provider}`);
        if (state && storedState && state !== storedState) {
          toast.error('Invalid state parameter - possible CSRF attack');
          navigate('/login');
          return;
        }

        // Clear stored state
        localStorage.removeItem(`oauth_state_${provider}`);

        // Exchange code for access token
        const response = await apiService.handleOAuthCallback(
          provider,
          code ?? undefined,
          state ?? undefined
        );
        
        if (response.access_token) {
          // Store tokens
          localStorage.setItem('auth_token', response.access_token);
          if (response.refresh_token) {
            localStorage.setItem('refresh_token', response.refresh_token);
          }
          
          // Clear any cached queries to ensure fresh data
          queryClient.clear();
          
          // Login user
          login(response.user);
          
          toast.success(`Successfully signed in with ${provider}!`);
          
          // Redirect to dashboard
          navigate('/', { replace: true });
        } else {
          throw new Error('No access token received');
        }
      } catch (error: any) {
        console.error('OAuth callback error:', error);
        // Always clear session on error
        localStorage.removeItem('auth_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('current_user');
        localStorage.removeItem('oauth_state_google');
        localStorage.removeItem('oauth_state_github');
        toast.error(`Failed to sign in with ${provider}: ${error.message || 'Authentication failed'}`);
        window.location.replace('/login');
      }
    };

    handleCallback();
  }, [provider, location, navigate, login, queryClient]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          Completing sign in...
        </h2>
        <p className="text-gray-600">
          Please wait while we complete your authentication with {provider}.
        </p>
      </div>
    </div>
  );
};

export default OAuthCallback; 