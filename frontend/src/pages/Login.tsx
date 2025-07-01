import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { 
  CalendarIcon, 
  ClockIcon, 
  UserGroupIcon,
  ChatAltIcon,
  SparklesIcon
} from '@heroicons/react/outline';
import { apiService } from '../services/api';
import { useAuth } from '../hooks/useAuth';

const Login: React.FC = () => {
  const { login } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [oauthUrls, setOauthUrls] = useState<{ 
    google?: { url: string; state: string }; 
    github?: { url: string; state: string } 
  }>({});

  useEffect(() => {
    const fetchOAuthUrls = async () => {
      try {
        const response = await apiService.getOAuthUrls();
        setOauthUrls(response.oauth_urls);
      } catch (error) {
        console.error('Failed to fetch OAuth URLs:', error);
        toast.error('Failed to load authentication options');
      }
    };

    fetchOAuthUrls();
  }, []);

  const handleOAuthLogin = (provider: string) => {
    const providerData = oauthUrls[provider as keyof typeof oauthUrls];
    if (providerData) {
      // Store state for validation
      localStorage.setItem(`oauth_state_${provider}`, providerData.state);
      window.location.href = providerData.url;
    } else {
      toast.error(`${provider} OAuth is not configured`);
    }
  };

  const features = [
    {
      icon: CalendarIcon,
      title: 'Smart Scheduling',
      description: 'AI-powered meeting scheduling with intelligent conflict resolution'
    },
    {
      icon: UserGroupIcon,
      title: 'Team Coordination',
      description: 'Easily coordinate with multiple participants and find optimal meeting times'
    },
    {
      icon: ChatAltIcon,
      title: 'Natural Language',
      description: 'Schedule meetings using simple, natural language commands'
    },
    {
      icon: ClockIcon,
      title: 'Time Optimization',
      description: 'Automatically find the best meeting times based on everyone\'s availability'
    },
    {
      icon: SparklesIcon,
      title: 'Learning Agent',
      description: 'The AI learns your preferences and gets better over time'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Left Side - Features */}
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
            >
              <div className="mb-8">
                <h1 className="text-4xl font-bold text-gray-900 mb-4">
                  AI Scheduling Agent
                </h1>
                <p className="text-xl text-gray-600 mb-6">
                  Your intelligent assistant for seamless meeting scheduling and team coordination
                </p>
              </div>

              <div className="space-y-6">
                {features.map((feature, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: index * 0.1 }}
                    className="flex items-start space-x-4"
                  >
                    <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                      <feature.icon className="h-6 w-6 text-white" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">
                        {feature.title}
                      </h3>
                      <p className="text-gray-600">
                        {feature.description}
                      </p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            {/* Right Side - Login */}
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="flex justify-center"
            >
              <div className="w-full max-w-md">
                <div className="bg-white rounded-2xl shadow-xl p-8">
                  <div className="text-center mb-8">
                    <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                      <CalendarIcon className="h-8 w-8 text-white" />
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">
                      Welcome Back
                    </h2>
                    <p className="text-gray-600">
                      Sign in to access your AI scheduling assistant
                    </p>
                  </div>

                  <div className="space-y-4">
                    {oauthUrls.google && (
                      <button
                        onClick={() => handleOAuthLogin('google')}
                        disabled={isLoading}
                        className="w-full flex items-center justify-center space-x-3 bg-white border border-gray-300 rounded-lg px-4 py-3 text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <svg className="w-5 h-5" viewBox="0 0 24 24">
                          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                        </svg>
                        <span className="font-medium">
                          {isLoading ? 'Signing in...' : 'Continue with Google'}
                        </span>
                      </button>
                    )}

                    {oauthUrls.github && (
                      <button
                        onClick={() => handleOAuthLogin('github')}
                        disabled={isLoading}
                        className="w-full flex items-center justify-center space-x-3 bg-gray-900 text-white rounded-lg px-4 py-3 hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                        </svg>
                        <span className="font-medium">
                          {isLoading ? 'Signing in...' : 'Continue with GitHub'}
                        </span>
                      </button>
                    )}

                    {!oauthUrls.google && !oauthUrls.github && (
                      <div className="text-center py-8">
                        <div className="text-gray-500 mb-4">
                          <CalendarIcon className="h-12 w-12 mx-auto mb-2" />
                          <p>OAuth providers not configured</p>
                        </div>
                        <p className="text-sm text-gray-400">
                          Please configure OAuth providers in the backend
                        </p>
                      </div>
                    )}
                  </div>

                  <div className="mt-8 pt-6 border-t border-gray-200">
                    <p className="text-xs text-gray-500 text-center">
                      By signing in, you agree to our Terms of Service and Privacy Policy
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login; 