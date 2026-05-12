const variableScale = (name, steps, fallbacks) =>
  Object.fromEntries(
    steps.map((step) => [step, `rgb(var(--${name}-${step}-rgb, ${fallbacks[step]}) / <alpha-value>)`])
  );

module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: variableScale('primary', [50, 100, 200, 300, 400, 500, 600, 700, 800, 900], {
          50: '254 242 242',
          100: '254 226 226',
          200: '254 202 202',
          300: '252 165 165',
          400: '248 113 113',
          500: '239 68 68',
          600: '220 38 38',
          700: '185 28 28',
          800: '153 27 27',
          900: '127 29 29',
        }),
        secondary: variableScale('secondary', [50, 100, 200, 300, 400, 500, 600, 700, 800, 900], {
          50: '249 250 251',
          100: '243 244 246',
          200: '229 231 235',
          300: '209 213 219',
          400: '156 163 175',
          500: '107 114 128',
          600: '75 85 99',
          700: '55 65 81',
          800: '31 41 55',
          900: '17 24 39',
        }),
        success: variableScale('success', [50, 500, 600], {
          50: '240 253 244',
          500: '34 197 94',
          600: '22 163 74',
        }),
        danger: variableScale('danger', [50, 500, 600], {
          50: '254 242 242',
          500: '239 68 68',
          600: '220 38 38',
        }),
        warning: variableScale('warning', [50, 500, 600], {
          50: '255 251 235',
          500: '245 158 11',
          600: '217 119 6',
        }),
        info: variableScale('info', [50, 500, 600], {
          50: '240 249 255',
          500: '14 165 233',
          600: '2 132 199',
        }),
      },
    },
  },
  plugins: [require('@tailwindcss/forms')],
}
