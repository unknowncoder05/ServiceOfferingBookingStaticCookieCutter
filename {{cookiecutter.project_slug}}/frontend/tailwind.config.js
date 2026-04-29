module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50:  'var(--primary-50, #fef2f2)',
          100: 'var(--primary-100, #fee2e2)',
          200: 'var(--primary-200, #fecaca)',
          300: 'var(--primary-300, #fca5a5)',
          400: 'var(--primary-400, #f87171)',
          500: 'var(--primary-500, #ef4444)',
          600: 'var(--primary-600, #DC2626)',
          700: 'var(--primary-700, #b91c1c)',
          800: 'var(--primary-800, #991b1b)',
          900: 'var(--primary-900, #7f1d1d)',
        },
        secondary: {
          50:  'var(--secondary-50, #f9fafb)',
          100: 'var(--secondary-100, #f3f4f6)',
          200: 'var(--secondary-200, #e5e7eb)',
          300: 'var(--secondary-300, #d1d5db)',
          400: 'var(--secondary-400, #9ca3af)',
          500: 'var(--secondary-500, #6b7280)',
          600: 'var(--secondary-600, #4b5563)',
          700: 'var(--secondary-700, #374151)',
          800: 'var(--secondary-800, #1f2937)',
          900: 'var(--secondary-900, #111827)',
        },
        success: {
          50:  'var(--success-50, #f0fdf4)',
          500: 'var(--success-500, #22c55e)',
          600: 'var(--success-600, #16a34a)',
        },
        danger: {
          50:  'var(--danger-50, #fef2f2)',
          500: 'var(--danger-500, #ef4444)',
          600: 'var(--danger-600, #dc2626)',
        },
        warning: {
          50:  'var(--warning-50, #fffbeb)',
          500: 'var(--warning-500, #f59e0b)',
          600: 'var(--warning-600, #d97706)',
        },
        info: {
          50:  'var(--info-50, #f0f9ff)',
          500: 'var(--info-500, #0ea5e9)',
          600: 'var(--info-600, #0284c7)',
        },
      },
    },
  },
  plugins: [require('@tailwindcss/forms')],
}
