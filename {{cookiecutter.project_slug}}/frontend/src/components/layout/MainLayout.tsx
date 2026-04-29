import React from 'react';
import { Outlet } from 'react-router-dom';
import { TopBar } from './TopBar';

export const MainLayout: React.FC = () => {
  return (
    <div className="h-screen flex flex-col bg-secondary-50 dark:bg-secondary-900 transition-colors">
      <TopBar onMenuClick={() => {}} />
      <div className="flex-1 overflow-auto">
        <Outlet />
      </div>
    </div>
  );
};
