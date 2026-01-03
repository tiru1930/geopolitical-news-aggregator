/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Indian Army inspired colors
        army: {
          olive: '#4B5320',
          'olive-light': '#6B7B3A',
          'olive-dark': '#3A4119',
          khaki: '#C3B091',
          'khaki-light': '#D4C4A8',
          'khaki-dark': '#A89B7A',
          maroon: '#800020',
          'maroon-light': '#A0324A',
          gold: '#D4AF37',
          'gold-light': '#E5C158',
          sand: '#F4E9D8',
          cream: '#FFFEF7',
        },
        primary: {
          50: '#f6f7f4',
          100: '#e8ebe3',
          200: '#d1d7c7',
          300: '#b3bda3',
          400: '#939f7d',
          500: '#4B5320',  // Army olive
          600: '#3f4619',
          700: '#343a15',
          800: '#2a2e12',
          900: '#1f220d',
        },
        accent: {
          50: '#fdf8f8',
          100: '#f9e8ea',
          200: '#f2ced3',
          300: '#e7a5ae',
          400: '#d67383',
          500: '#800020',  // Army maroon
          600: '#6d001b',
          700: '#5a0016',
          800: '#470011',
          900: '#34000d',
        }
      },
      backgroundImage: {
        'army-pattern': "url('/army-pattern.svg')",
        'camo-subtle': "linear-gradient(135deg, #4B5320 25%, transparent 25%), linear-gradient(225deg, #6B7B3A 25%, transparent 25%)",
      },
      fontFamily: {
        'military': ['Roboto Condensed', 'Arial Narrow', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
