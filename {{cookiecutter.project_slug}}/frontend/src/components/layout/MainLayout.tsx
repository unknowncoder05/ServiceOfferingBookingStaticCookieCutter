import React from 'react';
import { Outlet } from 'react-router-dom';
import { TopBar } from './TopBar';

export const MainLayout: React.FC = () => {
  return (
    <div className="h-screen flex flex-col bg-gray-50 dark:bg-gray-900 transition-colors">
      <TopBar onMenuClick={() => {}} />
      <div className="flex-1 overflow-auto">
        <Outlet />
      </div>
    </div>
  );
};
