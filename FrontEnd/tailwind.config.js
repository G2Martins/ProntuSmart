/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts}", // Diz ao Tailwind para buscar classes nesses arquivos
  ],
  theme: {
    extend: {
      colors: {
        // Você pode definir as cores da UCB ou da clínica aqui futuramente
        'clinica-primary': '#0D47A1',
        'clinica-secondary': '#1976D2',
        'clinica-accent': '#00B0FF',
      }
    },
  },
  plugins: [],
}