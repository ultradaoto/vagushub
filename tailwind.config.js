/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./views/**/*.ejs",
    "./public/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        'vagus-primary': '#0ea5e9',
        'vagus-orange': '#f4a261',
        'vagus-blue': '#2b95d3',
        'vagus-dark': '#162233',
        'vagus-muted': '#5b6b80',
        'vagus-border': '#e6edf3',
        'vagus-soft': '#f4f9fc',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

