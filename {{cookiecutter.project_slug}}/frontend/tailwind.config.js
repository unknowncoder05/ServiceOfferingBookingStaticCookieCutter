// Primary palette — each shade is individually configurable via REACT_APP_PRIMARY_* env vars.
// Defaults match Tailwind's sky palette. Values are baked in at `npm run build` time.
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50:  process.env.REACT_APP_PRIMARY_50  || '#f0f9ff',
          100: process.env.REACT_APP_PRIMARY_100 || '#e0f2fe',
          200: process.env.REACT_APP_PRIMARY_200 || '#bae6fd',
          300: process.env.REACT_APP_PRIMARY_300 || '#7dd3fc',
          400: process.env.REACT_APP_PRIMARY_400 || '#38bdf8',
          500: process.env.REACT_APP_PRIMARY_500 || '#0ea5e9',
          600: process.env.REACT_APP_PRIMARY_600 || '#0284c7',
          700: process.env.REACT_APP_PRIMARY_700 || '#0369a1',
          800: process.env.REACT_APP_PRIMARY_800 || '#075985',
          900: process.env.REACT_APP_PRIMARY_900 || '#0c4a6e',
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
