/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Paleta oficial ProntuSMART (Design 2026)
        // Base: #4E32A8, #6E56CF, #8F7EE2, #C1BDF6, #F4F2FF
        brand: {
          50:  '#F4F2FF',
          100: '#E8E4FB',
          200: '#C1BDF6',
          300: '#A79FEE',
          400: '#8F7EE2',
          500: '#6E56CF',
          600: '#5E46BE',
          700: '#4E32A8',
          800: '#3E2889',
          900: '#2E1E66',
          950: '#1C1140',
        },
        // Override do `blue` para que classes existentes (bg-blue-600, text-blue-700, etc.)
        // adotem automaticamente a nova paleta da marca.
        blue: {
          50:  '#F4F2FF',
          100: '#E8E4FB',
          200: '#C1BDF6',
          300: '#A79FEE',
          400: '#8F7EE2',
          500: '#6E56CF',
          600: '#5E46BE',
          700: '#4E32A8',
          800: '#3E2889',
          900: '#2E1E66',
          950: '#1C1140',
        },
        // Aliases semânticos
        'clinica-primary':   '#4E32A8',
        'clinica-secondary': '#6E56CF',
        'clinica-accent':    '#8F7EE2',
        'clinica-soft':      '#C1BDF6',
        'clinica-surface':   '#F4F2FF',
      }
    },
  },
  plugins: [],
}
