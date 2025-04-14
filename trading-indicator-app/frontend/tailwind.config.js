/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'dark-bg': '#121212',
        'dark-surface': '#1E1E1E',
        'dark-primary': '#BB86FC',
        'dark-secondary': '#03DAC6',
        'dark-error': '#CF6679',
        'dark-text': '#FFFFFF',
        'dark-text-secondary': '#B0B0B0',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
} 