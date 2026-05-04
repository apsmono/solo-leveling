/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cream: {
          50: '#fffbf4',
          100: '#f8f0e3',
          200: '#efe2cc',
          300: '#dcc6a4',
        },
        brown: {
          400: '#7f6a58',
          500: '#6d5b49',
          600: '#4c3c2d',
        },
        green: {
          800: '#1f3529',
        },
        bronze: {
          400: '#c99b55',
          500: '#8a5a2f',
          600: '#9b6b3d',
        },
        surface: 'rgba(255, 251, 244, 0.92)',
        'surface-strong': 'rgba(251, 245, 235, 0.86)',
      },
      fontFamily: {
        serif: ['"Cormorant Garamond"', 'Baskerville', 'Georgia', 'serif'],
        sans: ['"Plus Jakarta Sans"', 'Segoe UI', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        panel: '32px',
        card: '28px',
        pill: '999px',
      },
      boxShadow: {
        soft: '0 24px 60px rgba(55, 41, 24, 0.12)',
        accent: '0 16px 32px rgba(107, 77, 39, 0.2)',
      },
      maxWidth: {
        container: '1180px',
      },
    },
  },
  plugins: [],
}
