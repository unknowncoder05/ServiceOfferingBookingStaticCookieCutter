import { useEffect } from 'react';

const THEME_VARS = [
  'PRIMARY_50', 'PRIMARY_100', 'PRIMARY_200', 'PRIMARY_300', 'PRIMARY_400',
  'PRIMARY_500', 'PRIMARY_600', 'PRIMARY_700', 'PRIMARY_800', 'PRIMARY_900',
  'SECONDARY_50', 'SECONDARY_100', 'SECONDARY_200', 'SECONDARY_300', 'SECONDARY_400',
  'SECONDARY_500', 'SECONDARY_600', 'SECONDARY_700', 'SECONDARY_800', 'SECONDARY_900',
  'SUCCESS_50', 'SUCCESS_500', 'SUCCESS_600',
  'DANGER_50', 'DANGER_500', 'DANGER_600',
  'WARNING_50', 'WARNING_500', 'WARNING_600',
  'INFO_50', 'INFO_500', 'INFO_600'
];

export const ThemeInitializer: React.FC = () => {
  useEffect(() => {
    const root = document.documentElement;
    THEME_VARS.forEach(varName => {
      const envValue = process.env[`REACT_APP_${varName}`];
      if (envValue) {
        root.style.setProperty(`--${varName.toLowerCase().replace(/_/g, '-')}`, envValue);
      }
    });
  }, []);

  return null;
};
