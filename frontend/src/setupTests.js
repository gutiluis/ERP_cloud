// file: /src/setupTests.js
// descr: run before src/App.test.jsx and configure testing environments
import '@testing-library/jest-dom/vitest'
import { afterEach } from 'vitest'

const storage = new Map()
// localStorage mock. needs browser APIs
Object.defineProperty(globalThis, 'localStorage', {
    value: {
        getItem(key) {
            return storage.get(key) ?? null
        },

        setItem(key, value) {
            storage.set(key, String(value))
        },

        removeItem(key) {
            storage.delete(key)
        },

        clear() {
            storage.clear()
        },
    },
})

afterEach(() => {
    localStorage.clear()
})
