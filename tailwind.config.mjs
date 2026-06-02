/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#12211a',
        cream: '#f8f6ef',
        pine: '#2b6a4b',
        gold: '#b88a2b',
        rust: '#b44a2f'
      }
    }
  },
  plugins: []
};
