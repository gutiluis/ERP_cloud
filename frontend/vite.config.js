/// <reference types="vitest/config" />

// descr: configure development/build tool; not react app

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// used by different compose environment local development, http://e2e_api:8000
// loadEnv is provided by environment compose*.yaml .env.VITE_API_TARGET
// proxy target environment-driven
const apiTarget = process.env.VITE_API_TARGET ?? 'http://localhost:8000'

export default defineConfig({
    plugins: [react(), tailwindcss()],
    // not needed for production but its ok to leave as nginx resolves
    // server is needed for e2e
    // development port :5173
    server: {
        proxy: {
            '/api': {
                target: apiTarget,
                changeOrigin: true,
            },
        },
    },
    // not needed under production. nginx can do it so it can be removed. only for development
    //preview: {
    //    host: '0.0.0.0',
    //    port: 4173,
    //    proxy: {
    //        '/api': {
    //            target: apiTarget,
    //            changeOrigin: true,
    //        },
    //    },
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
