import React from 'react';
import { useNavigate } from 'react-router-dom';

const ServerDown: React.FC = () => {
  const navigate = useNavigate();

  const handleRetry = () => {
    // Clear any stored error state and try to go back to home
    window.location.href = '/';
  };

  const handleGoHome = () => {
    navigate('/');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 text-center">
        <div>
          <div className="mx-auto flex items-center justify-center h-24 w-24 rounded-full bg-red-100 mb-4">
            <svg
              className="h-12 w-12 text-red-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>

          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Server Error
          </h2>

          <p className="mt-2 text-center text-sm text-gray-600">
            We're experiencing technical difficulties. Our servers are currently unavailable.
          </p>

          <p className="mt-4 text-center text-sm text-gray-500">
            Please try again in a few moments. If the problem persists, contact support.
          </p>
        </div>

        <div className="mt-8 space-y-4">
          <button
            onClick={handleRetry}
            className="w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Retry
          </button>

          <button
            onClick={handleGoHome}
            className="w-full flex justify-center py-2 px-4 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Go to Home
          </button>
        </div>

        <div className="mt-6">
          <p className="text-xs text-gray-400">
            Error Code: 500 - Internal Server Error
          </p>
        </div>
      </div>
    </div>
  );
};

export default ServerDown;
