export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'float':        'float 9s ease-in-out infinite',
        'float-slow':   'float 13s ease-in-out 3s infinite',
        'float-fast':   'float 7s ease-in-out 1.5s infinite',
        'fade-in':      'fadeIn 0.7s ease-out forwards',
        'slide-up':     'slideUp 0.7s ease-out forwards',
        'slide-up-d1':  'slideUp 0.7s ease-out 0.1s forwards',
        'slide-up-d2':  'slideUp 0.7s ease-out 0.2s forwards',
        'slide-up-d3':  'slideUp 0.7s ease-out 0.3s forwards',
        'gradient':     'gradientShift 5s ease infinite',
        'flow-dot':     'flowDot 2s ease-in-out infinite',
        'flow-dot-d1':  'flowDot 2s ease-in-out 0.66s infinite',
        'flow-dot-d2':  'flowDot 2s ease-in-out 1.33s infinite',
        'shimmer':      'shimmer 2.5s ease-in-out infinite',
        'count-up':     'fadeIn 0.6s ease-out forwards',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px) translateX(0px)' },
          '33%':      { transform: 'translateY(-28px) translateX(12px)' },
          '66%':      { transform: 'translateY(18px) translateX(-12px)' },
        },
        fadeIn: {
          from: { opacity: '0' },
          to:   { opacity: '1' },
        },
        slideUp: {
          from: { opacity: '0', transform: 'translateY(28px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        gradientShift: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%':      { backgroundPosition: '100% 50%' },
        },
        flowDot: {
          '0%':   { transform: 'translateX(0%)', opacity: '0' },
          '10%':  { opacity: '1' },
          '90%':  { opacity: '1' },
          '100%': { transform: 'translateX(100%)', opacity: '0' },
        },
        shimmer: {
          '0%':   { backgroundPosition: '-200% center' },
          '100%': { backgroundPosition: '200% center' },
        },
      },
    },
  },
  plugins: [],
}
