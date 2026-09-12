/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        forest: {
          950: '#052e16',
          900: '#14532d',
          800: '#166534',
          700: '#15803d',
          600: '#16a34a',
          500: '#22c55e',
          400: '#4ade80',
          300: '#86efac',
          200: '#bbf7d0',
          100: '#dcfce7',
          50:  '#f0fdf4',
        },
        harvest: {
          600: '#d97706',
          500: '#f59e0b',
          400: '#fbbf24',
          100: '#fef3c7',
        },
        sage: {
          50:  '#f0fdf4',
          100: '#f9faf2',
        },
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      boxShadow: {
        'agri': '0 1px 3px 0 rgba(20, 83, 45, 0.08), 0 4px 12px 0 rgba(20, 83, 45, 0.06)',
        'agri-md': '0 4px 16px 0 rgba(20, 83, 45, 0.12), 0 1px 4px 0 rgba(20, 83, 45, 0.08)',
        'agri-lg': '0 8px 32px 0 rgba(20, 83, 45, 0.16)',
      },
    },
  },
  plugins: [],
}
