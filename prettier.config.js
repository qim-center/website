const GoTemplatePlugin = require('prettier-plugin-go-template')

/** @type {import("prettier").Config} */
const config = {
  trailingComma: 'es5',
  tabWidth: 2,
  semi: false,
  singleQuote: true,
  printWidth: 120,
  plugins: [GoTemplatePlugin, 'prettier-plugin-tailwindcss'],
  overrides: [
    {
      files: ['*.html'],
      options: {
        parser: 'go-template',
      },
    },
  ],
}

module.exports = config
