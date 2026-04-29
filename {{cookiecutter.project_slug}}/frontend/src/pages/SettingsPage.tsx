import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '../store/hooks';
import { getCurrentUser } from '../store/authSlice';
import apiService from '../services/api';
import toast from 'react-hot-toast';
import { Breadcrumbs } from '../components/shared';

export const SettingsPage: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [searchParams] = useSearchParams();
  const { user } = useAppSelector((state) => state.auth);
  const [isConnectingGitHub, setIsConnectingGitHub] = useState(false);
  const [isDisconnectingGitHub, setIsDisconnectingGitHub] = useState(false);

  const handleGitHubCallback = useCallback(async (code: string, state: string) => {
    setIsConnectingGitHub(true);
    try {
      await apiService.gitHubCallback({ code, state });
      toast.success('GitHub account connected successfully!');
      // Refresh user data to get updated GitHub info
      dispatch(getCurrentUser());
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to connect GitHub account');
    } finally {
      setIsConnectingGitHub(false);
    }
  }, [dispatch]);

  // Handle GitHub OAuth callback
  useEffect(() => {
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    const storedState = sessionStorage.getItem('github_oauth_state');

    if (code && state) {
      // Clear the URL params
      window.history.replaceState({}, '', '/settings');

      if (state !== storedState) {
        toast.error('Invalid OAuth state. Please try again.');
        return;
      }

      sessionStorage.removeItem('github_oauth_state');

      // Exchange code for token
      handleGitHubCallback(code, state);
    }
  }, [searchParams, handleGitHubCallback]);

  const handleConnectGitHub = async () => {
    setIsConnectingGitHub(true);
    try {
      const response = await apiService.getGitHubAuthUrl();
      const { auth_url, state } = response.data;

      // Store state for validation
      sessionStorage.setItem('github_oauth_state', state);

      // Redirect to GitHub OAuth
      window.location.href = auth_url;
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to get GitHub authorization URL');
      setIsConnectingGitHub(false);
    }
  };

  const handleDisconnectGitHub = async () => {
    if (!window.confirm('Are you sure you want to disconnect your GitHub account?')) {
      return;
    }

    setIsDisconnectingGitHub(true);
    try {
      await apiService.disconnectGitHub();
      toast.success('GitHub account disconnected');
      dispatch(getCurrentUser());
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to disconnect GitHub account');
    } finally {
      setIsDisconnectingGitHub(false);
    }
  };

  return (
    <div className="min-h-screen bg-secondary-50 dark:bg-secondary-900 transition-colors">
      {/* Header */}
      <div className="bg-white dark:bg-secondary-800 border-b border-secondary-200 dark:border-secondary-700 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate(-1)}
              className="p-2 hover:bg-secondary-100 dark:hover:bg-secondary-700 rounded-lg transition-colors text-secondary-600 dark:text-secondary-400"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <h1 className="text-xl font-semibold text-secondary-900 dark:text-white">Settings</h1>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <Breadcrumbs />
        
        {/* Profile Section */}
        <div className="bg-white rounded-lg shadow-sm border border-secondary-200 mb-6">
          <div className="px-6 py-4 border-b border-secondary-200">
            <h2 className="text-lg font-semibold text-secondary-900">Profile</h2>
          </div>
          <div className="px-6 py-4">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-primary-600 rounded-full flex items-center justify-center text-white text-2xl font-semibold">
                {user?.email?.charAt(0).toUpperCase() || 'U'}
              </div>
              <div>
                <p className="text-lg font-medium text-secondary-900">
                  {user?.first_name} {user?.last_name}
                </p>
                <p className="text-sm text-secondary-500">{user?.email}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Integrations Section */}
        <div className="bg-white rounded-lg shadow-sm border border-secondary-200">
          <div className="px-6 py-4 border-b border-secondary-200">
            <h2 className="text-lg font-semibold text-secondary-900">Integrations</h2>
            <p className="text-sm text-secondary-500 mt-1">Connect external services to enhance your projects</p>
          </div>
          <div className="px-6 py-4">
            {/* GitHub Integration */}
            <div className="flex items-center justify-between py-4 border-b border-secondary-100 last:border-0">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-secondary-900 rounded-lg flex items-center justify-center">
                  <svg className="w-7 h-7 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-base font-medium text-secondary-900">GitHub</h3>
                  {user?.github_connected ? (
                    <p className="text-sm text-primary-600">
                      Connected as <span className="font-medium">@{user.github_username}</span>
                    </p>
                  ) : (
                    <p className="text-sm text-secondary-500">Connect to clone repositories and manage code</p>
                  )}
                </div>
              </div>
              <div>
                {user?.github_connected ? (
                  <button
                    onClick={handleDisconnectGitHub}
                    disabled={isDisconnectingGitHub}
                    className="px-4 py-2 text-sm font-medium text-danger-600 bg-danger-50 hover:bg-danger-100 dark:bg-danger-900/20 dark:hover:bg-danger-900/30 rounded-lg transition-colors disabled:opacity-50"
                  >
                    {isDisconnectingGitHub ? 'Disconnecting...' : 'Disconnect'}
                  </button>
                ) : (
                  <button
                    onClick={handleConnectGitHub}
                    disabled={isConnectingGitHub}
                    className="px-4 py-2 text-sm font-medium text-white bg-secondary-900 hover:bg-secondary-800 dark:bg-primary-600 dark:hover:bg-primary-700 rounded-lg transition-colors disabled:opacity-50"
                  >
                    {isConnectingGitHub ? 'Connecting...' : 'Connect GitHub'}
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
