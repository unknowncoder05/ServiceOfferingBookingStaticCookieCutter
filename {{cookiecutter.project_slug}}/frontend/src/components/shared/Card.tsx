import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  description?: string;
  onClick?: () => void;
  hoverable?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  title,
  description,
  onClick,
  hoverable = false
}) => {
  const hoverStyles = hoverable ? 'hover:shadow-lg transition-shadow cursor-pointer' : '';

  return (
    <div
      className={`bg-white rounded-lg shadow-md border border-secondary-200 ${hoverStyles} ${className}`}
      onClick={onClick}
    >
      {(title || description) && (
        <div className="px-6 py-4 border-b border-secondary-200">
          {title && <h3 className="text-lg font-semibold text-secondary-900">{title}</h3>}
          {description && <p className="mt-1 text-sm text-secondary-600">{description}</p>}
        </div>
      )}
      <div className="px-6 py-4">
        {children}
      </div>
    </div>
  );
};
