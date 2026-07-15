/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        surface: {
          DEFAULT: '#0a0a0a',
          raised: '#1a1a1a',
          card: '#151515',
        },
        neon: {
          cyan: '#00d9ff',
          lime: '#39ff14',
          pink: '#ff006e',
          yellow: '#ffff00',
        },
        ink: {
          DEFAULT: '#f0f0f0',
          muted: '#888888',
          dim: '#666666',
        },
        line: '#333333',
      },
      fontFamily: {
        sans: ['"Instrument Sans"', 'sans-serif'],
        mono: ['Courier New', 'monospace'],
      },
      letterSpacing: {
        label: '0.1em',
        wide: '0.08em',
      },
      keyframes: {
        'fade-in': {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
      },
      animation: {
        'fade-in': 'fade-in 0.3s ease-out',
      },
    },
  },
  plugins: [],
}
