import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAppSelector } from '../store/hooks';
import { useTheme } from '../context/ThemeContext';

const features = [
  { key: 'auth',     icon: '🔐', color: 'bg-blue-50 dark:bg-blue-900/20' },
  { key: 'items',    icon: '📦', color: 'bg-green-50 dark:bg-green-900/20' },
  { key: 'realtime', icon: '⚡', color: 'bg-yellow-50 dark:bg-yellow-900/20' },
  { key: 'async',    icon: '⚙️', color: 'bg-purple-50 dark:bg-purple-900/20' },
  { key: 'cloud',    icon: '☁️', color: 'bg-sky-50 dark:bg-sky-900/20' },
  { key: 'darkMode', icon: '🌙', color: 'bg-slate-50 dark:bg-slate-700/20' },
];

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { isDark, toggleTheme } = useTheme();
  const { isAuthenticated } = useAppSelector((state) => state.auth);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">

      {/* Top nav */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
          <span className="text-base font-semibold text-gray-900 dark:text-white">
            {{cookiecutter.project_name}}
          </span>

          <div className="flex items-center gap-2">
            <button
              onClick={toggleTheme}
              aria-label={isDark ? t('theme.light') : t('theme.dark')}
              className="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              {isDark ? (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707M17.657 17.657l-.707-.707M6.343 6.343l-.707-.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              )}
            </button>

            {isAuthenticated ? (
              <button
                onClick={() => navigate('/dashboard')}
                className="px-4 py-1.5 bg-primary-600 hover:bg-primary-700 dark:bg-primary-500 dark:hover:bg-primary-600 text-white text-sm font-medium rounded-lg transition-colors"
              >
                {t('home.nav.dashboard')}
              </button>
            ) : (
              <>
                <button
                  onClick={() => navigate('/login')}
                  className="px-4 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  {t('home.nav.login')}
                </button>
                <button
                  onClick={() => navigate('/signup')}
                  className="px-4 py-1.5 bg-primary-600 hover:bg-primary-700 dark:bg-primary-500 dark:hover:bg-primary-600 text-white text-sm font-medium rounded-lg transition-colors"
                >
                  {t('home.nav.signup')}
                </button>
              </>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16">

        {/* Hero */}
        <div className="text-center mb-20">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 mb-4">
            {t('dashboard.badge')}
          </span>

          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 dark:text-white mb-4 leading-tight">
            {t('home.hero.title')}
          </h1>

          <p className="text-xl text-gray-500 dark:text-gray-400 max-w-2xl mx-auto mb-8">
            {t('home.hero.subtitle')}
          </p>

          <div className="flex flex-wrap gap-3 justify-center">
            {isAuthenticated ? (
              <button
                onClick={() => navigate('/dashboard')}
                className="px-6 py-3 bg-primary-600 hover:bg-primary-700 dark:bg-primary-500 dark:hover:bg-primary-600 text-white font-medium rounded-lg transition-colors shadow-sm"
              >
                {t('home.hero.ctaDashboard')}
              </button>
            ) : (
              <>
                <button
                  onClick={() => navigate('/signup')}
                  className="px-6 py-3 bg-primary-600 hover:bg-primary-700 dark:bg-primary-500 dark:hover:bg-primary-600 text-white font-medium rounded-lg transition-colors shadow-sm"
                >
                  {t('home.hero.ctaSignup')}
                </button>
                <button
                  onClick={() => navigate('/login')}
                  className="px-6 py-3 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200 font-medium rounded-lg border border-gray-200 dark:border-gray-700 transition-colors shadow-sm"
                >
                  {t('home.hero.ctaLogin')}
                </button>
              </>
            )}
          </div>
        </div>

        {/* Features */}
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-500 text-center mb-8">
            {t('dashboard.features')}
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {features.map((f) => (
              <div
                key={f.key}
                className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-5 flex gap-4 transition-colors"
              >
                <div className={`${f.color} rounded-lg w-10 h-10 flex items-center justify-center flex-shrink-0 text-lg`}>
                  {f.icon}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white text-sm mb-1">
                    {t(`features.${f.key}`)}
                  </h3>
                  <p className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
                    {t(`features.${f.key}Desc`)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
};

export default HomePage;
