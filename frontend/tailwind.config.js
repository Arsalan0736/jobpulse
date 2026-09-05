/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Geist', 'system-ui', 'sans-serif'],
        mono: ['Geist Mono', 'ui-monospace', 'monospace'],
      },
      colors: {
        // Premium cold-luxury palette: near-black, off-white, single electric amber accent
        ink: {
          950: '#0a0a0a',
          900: '#101012',
          800: '#17171a',
          700: '#222226',
          600: '#2c2c32',
          500: '#3a3a42',
          400: '#6b6b75',
          300: '#9b9ba3',
          200: '#c7c7cd',
          100: '#e5e5e8',
        },
        amber: {
          glow: '#ffb547',
        },
      },
      letterSpacing: {
        tightest: '-0.04em',
      },
    },
  },
  plugins: [],
}