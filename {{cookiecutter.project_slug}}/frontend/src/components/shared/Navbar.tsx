import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { signOut } from '../../store/authSlice';
import { useTheme } from '../../context/ThemeContext';
import { useTranslation } from 'react-i18next';

const LANGUAGES = [
  { code: 'en', label: 'EN' },
  { code: 'es', label: 'ES' },
];

export const Navbar: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { user } = useAppSelector((state) => state.auth);
  const { isDark, toggleTheme } = useTheme();
  const { t, i18n } = useTranslation();
  const [langOpen, setLangOpen] = useState(false);

  const handleLogout = async () => {
    await dispatch(signOut());
    navigate('/login');
  };

  return (
    <nav className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Left: brand + nav links */}
          <div className="flex items-center">
            <Link to="/dashboard" className="flex items-center mr-8">
              <span className="text-xl font-bold text-primary-600 dark:text-primary-400">
                My Project
              </span>
            </Link>
            <div className="hidden sm:flex sm:space-x-6">
              <Link
                to="/dashboard"
                className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-700 dark:text-gray-200 border-b-2 border-transparent hover:border-primary-500 transition-colors"
              >
                {t('nav.dashboard')}
              </Link>
              <Link
                to="/items"
                className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-700 dark:text-gray-200 border-b-2 border-transparent hover:border-primary-500 transition-colors"
              >
                {t('nav.items')}
              </Link>
            </div>
          </div>

          {/* Right: theme toggle, language, user */}
          <div className="flex items-center gap-1">
            {/* Dark mode toggle */}
            <button
              onClick={toggleTheme}
              title={isDark ? t('theme.light') : t('theme.dark')}
              className="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              {isDark ? (
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
                  />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
                  />
                </svg>
              )}
            </button>

            {/* Language selector */}
            <div className="relative">
              <button
                onClick={() => setLangOpen(!langOpen)}
                className="px-2.5 py-1.5 text-xs font-semibold text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                {i18n.language.toUpperCase()}
              </button>
              {langOpen && (
                <>
                  <div className="fixed inset-0 z-10" onClick={() => setLangOpen(false)} />
                  <div className="absolute right-0 mt-1 w-20 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-20">
                    {LANGUAGES.map((lang) => (
                      <button
                        key={lang.code}
                        onClick={() => {
                          i18n.changeLanguage(lang.code);
                          localStorage.setItem('language', lang.code);
                          setLangOpen(false);
                        }}
                        className={`w-full text-left px-3 py-1.5 text-xs hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                          i18n.language === lang.code
                            ? 'text-primary-600 dark:text-primary-400 font-bold'
                            : 'text-gray-700 dark:text-gray-300'
                        }`}
                      >
                        {lang.label}
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>

            <span className="text-sm text-gray-500 dark:text-gray-400 ml-2 mr-1 hidden sm:block">
              {user?.email}
            </span>

            <button
              onClick={handleLogout}
              className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 px-3 py-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              {t('nav.logout')}
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};
