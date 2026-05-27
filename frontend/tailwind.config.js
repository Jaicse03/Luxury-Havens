/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        luxury: {
          50: '#f8fafc',
          100: '#f1f5f9',
          800: '#0f172a',
          900: '#020617',
          gold: '#d4af37',
          accent: '#4f46e5'
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
