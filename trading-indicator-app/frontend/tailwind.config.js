/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],
  theme: {
    extend: {
      colors: {
        'buy': '#10b981', // Green
        'sell': '#ef4444', // Red
      },
    },
  },
  plugins: [],
} 