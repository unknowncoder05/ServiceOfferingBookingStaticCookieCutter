import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import LoginForm from '../components/LoginForm';
import SignUpForm from '../components/SignUpForm';

const AuthPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isLogin, setIsLogin] = useState(location.pathname === '/login');

  // Update isLogin state when the path changes
  useEffect(() => {
    setIsLogin(location.pathname === '/login');
  }, [location.pathname]);

  const handleAuthSuccess = () => {
    const from = (location.state as { from?: Location })?.from?.pathname;
    navigate(from && from !== '/login' && from !== '/signup' ? from : '/dashboard', { replace: true });
  };

  const switchToSignUp = () => {
    navigate('/signup');
  };

  const switchToLogin = () => {
    navigate('/login');
  };

  return (
    <>
      {isLogin ? (
        <LoginForm
          onSuccess={handleAuthSuccess}
          onSwitchToSignUp={switchToSignUp}
        />
      ) : (
        <SignUpForm
          onSuccess={handleAuthSuccess}
          onSwitchToLogin={switchToLogin}
        />
      )}
    </>
  );
};

export default AuthPage;
