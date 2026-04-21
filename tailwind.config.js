/** @type {import('tailwindcss').Config} */
module.exports = {
  // 1. Specify the paths to all of your template files
  // and the Flowbite node_modules directory
  content: [
    "./index.html",
    "./frontend/src/**/*.{js,ts,jsx,tsx}",
    "./node_modules/flowbite/**/*.js" // This is required for Flowbite's JS-based components
  ],
  theme: {
    extend: {
      // You can customize your theme here
    },
  },
  plugins: [
    // 2. Add the Flowbite plugin
    require('flowbite/plugin')
  ],
  // 3. Optional: Enable class-based dark mode (recommended by Flowbite)
  darkMode: 'class',
}
