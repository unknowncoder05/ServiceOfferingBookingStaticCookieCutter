import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { validateAccount, requestValidateToken, clearError } from '../store/authSlice';
import { ValidateAccountRequest } from '../types/auth';
import { AUTH_PROVIDERS, AuthProvider } from '../utils/constants';

const VerifyAccount: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [searchParams] = useSearchParams();
  const { isLoading, error } = useAppSelector((state) => state.auth);

  const [phoneNumber, setPhoneNumber] = useState(searchParams.get('phone') || '');
  const [verificationCode, setVerificationCode] = useState('');
  const [provider] = useState<AuthProvider>((searchParams.get('provider') as AuthProvider) || AUTH_PROVIDERS.SMS);

  useEffect(() => {
    return () => {
      dispatch(clearError());
    };
  }, [dispatch]);

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!phoneNumber.trim() || !verificationCode.trim()) {
      return;
    }

    try {
      const validationData: ValidateAccountRequest = {
        phone_number: phoneNumber,
        token: verificationCode,
      };

      await dispatch(validateAccount(validationData)).unwrap();
      navigate('/dashboard');
    } catch (error) {
      // Error is handled by Redux
    }
  };

  const handleResendCode = async () => {
    if (!phoneNumber.trim()) {
      return;
    }

    try {
      await dispatch(requestValidateToken({
        phone_number: phoneNumber,
        provider: provider
      })).unwrap();

      toast.success('Verification code resent successfully!');
    } catch (error) {
      // Error is handled by Redux
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Verify Your Account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Enter the verification code sent to your phone
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleVerify}>
          <div className="space-y-4">
            <div>
              <label htmlFor="phone-number" className="block text-sm font-medium text-gray-700">
                Phone Number
              </label>
              <input
                id="phone-number"
                name="phone-number"
                type="tel"
                required
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="+1234567890"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
              />
            </div>

            <div>
              <label htmlFor="verification-code" className="block text-sm font-medium text-gray-700">
                Verification Code
              </label>
              <input
                id="verification-code"
                name="verification-code"
                type="text"
                required
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="Enter verification code"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value)}
              />
            </div>
          </div>

          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="text-sm text-red-700">{error}</div>
            </div>
          )}

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Verifying...
                </div>
              ) : (
                'Verify Account'
              )}
            </button>
          </div>
        </form>

        <div className="text-center space-y-2">
          <button
            type="button"
            onClick={handleResendCode}
            disabled={isLoading || !phoneNumber.trim()}
            className="text-sm text-indigo-600 hover:text-indigo-500 disabled:text-gray-400"
          >
            Resend verification code
          </button>

          <div>
            <button
              type="button"
              onClick={() => navigate('/signup')}
              className="text-sm text-gray-600 hover:text-gray-500"
            >
              Back to sign up
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VerifyAccount;
