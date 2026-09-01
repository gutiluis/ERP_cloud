import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import App from './App'

describe('App', () => {
    it('increments the counter when clicked', () => {
        render(<App />)

        const button = screen.getByRole('button', { name: 'Count is 0' })

        expect(button).toBeInTheDocument()

        fireEvent.click(button)

        expect(
            screen.getByRole('button', { name: 'Count is 1' }),
        ).toBeInTheDocument()
    })
})
