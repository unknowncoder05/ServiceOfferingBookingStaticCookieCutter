import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAppSelector } from '../store/hooks';
import { Navbar } from '../components/shared';

const features = [
  {
    key: 'auth',
    icon: '🔐',
    color: 'bg-blue-50 dark:bg-blue-900/20',
  },
  {
    key: 'items',
    icon: '📦',
    color: 'bg-green-50 dark:bg-green-900/20',
  },
  {
    key: 'realtime',
    icon: '⚡',
    color: 'bg-yellow-50 dark:bg-yellow-900/20',
  },
  {
    key: 'async',
    icon: '⚙️',
    color: 'bg-purple-50 dark:bg-purple-900/20',
  },
  {
    key: 'cloud',
    icon: '☁️',
    color: 'bg-sky-50 dark:bg-sky-900/20',
  },
  {
    key: 'darkMode',
    icon: '🌙',
    color: 'bg-slate-50 dark:bg-slate-700/20',
  },
];

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { user } = useAppSelector((state) => state.auth);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      <Navbar />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Hero */}
        <div className="text-center mb-16">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 mb-4">
            {t('dashboard.badge')}
          </span>

          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 dark:text-white mb-4 leading-tight">
            {t('dashboard.welcome')}
          </h1>

          <p className="text-xl text-gray-500 dark:text-gray-400 mb-2">
            {t('dashboard.subtitle')}
          </p>

          <p className="text-sm text-gray-400 dark:text-gray-500">
            {t('dashboard.loggedInAs')} {user?.email}
          </p>

          <div className="mt-8 flex flex-wrap gap-3 justify-center">
            <button
              onClick={() => navigate('/items')}
              className="px-6 py-3 bg-primary-600 hover:bg-primary-700 dark:bg-primary-500 dark:hover:bg-primary-600 text-white font-medium rounded-lg transition-colors shadow-sm"
            >
              {t('dashboard.cta.items')}
            </button>
            <button
              onClick={() => navigate('/settings')}
              className="px-6 py-3 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200 font-medium rounded-lg border border-gray-200 dark:border-gray-700 transition-colors shadow-sm"
            >
              {t('dashboard.cta.settings')}
            </button>
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
                <div
                  className={`${f.color} rounded-lg w-10 h-10 flex items-center justify-center flex-shrink-0 text-lg`}
                >
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
      </div>
    </div>
  );
};

export default Dashboard;
