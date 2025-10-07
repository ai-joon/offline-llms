/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('daisyui'),
  ],
  daisyui: {
    themes: [
      'light',
      'dark',
      {
        corporate: {
          ...require('daisyui/src/theming/themes')['[data-theme=corporate]'],
        },
      },
    ],
    darkTheme: 'dark',
  },
}

