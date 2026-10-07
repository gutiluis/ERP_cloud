/// <reference types="vitest/config" />

// descr: configure development/build tool; not react app

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'


export default defineConfig({
    plugins: [react(), tailwindcss()],
    // test property
    test: {
        environment: 'jsdom',
        setupFiles: './src/setupTests.js',
        globals: true,
        // recursive globbing enabled by vitest's glob-matching library. not by shell
        // file/** in shell globbing. its a glob pattern. it's a wildcard when recursive globbing is enabled
        // file/** is not regex nor a wildcard
        exclude: ['**/node_modules/**', 'e2e/**'],
    },
})
