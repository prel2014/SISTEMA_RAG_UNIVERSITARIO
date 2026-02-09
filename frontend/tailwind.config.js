/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1E3A5F',
          50: '#E8EDF3',
          100: '#D1DBE7',
          200: '#A3B7CF',
          300: '#7593B7',
          400: '#476F9F',
          500: '#1E3A5F',
          600: '#182E4C',
          700: '#122339',
          800: '#0C1726',
          900: '#060C13',
        },
        secondary: {
          DEFAULT: '#C8102E',
          50: '#FBE8EB',
          100: '#F7D1D7',
          200: '#EFA3AF',
          300: '#E77587',
          400: '#DF475F',
          500: '#C8102E',
          600: '#A00D25',
          700: '#780A1C',
          800: '#500713',
          900: '#28030A',
        },
      },
    },
  },
  plugins: [],
};
