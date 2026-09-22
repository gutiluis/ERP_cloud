import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
// vite.config.js is not common.js use ES modules
import { defineConfig, globalIgnores } from 'eslint/config'

// arrray destructuring extracts values from an array
// array literal creates an array
// [..] is array literal not array destructuring
export default defineConfig([
    globalIgnores(['dist']),
    {
        // eslint.config.js docs
        // **/*.extension in docs. match .js and .jsx files in the directory "." and its subdirectories no need for src/*
        files: ['**/*.{js,jsx}'],
        // ignores uses minimatch syntax
        ignores: [
            "playwright.config.js",
            // recursively
            "e2e/**",
        ],
        extends: [
            js.configs.recommended,
            reactHooks.configs.flat.recommended,
            reactRefresh.configs.vite,
        ],
        languageOptions: {
            globals: globals.browser,
            parserOptions: {
                ecmaFeatures: { jsx: true },
            },
        },
    },
    {
        files: ["vite.config.js"],
        extends: [
            js.configs.recommended,
        ],
        languageOptions: {
            globals: globals.node,
        },
    },
])
