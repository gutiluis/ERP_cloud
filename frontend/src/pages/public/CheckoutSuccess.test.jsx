import { render, screen } from '@testing-library/react'
import CheckoutSuccess from './CheckoutSuccess'

describe('CheckoutSuccess', () => {
    beforeEach(() => {
        localStorage.clear()
    })

    test('clears the cart token after successful checkout', () => {
        localStorage.setItem('cart_token', 'abc123')

        render(<CheckoutSuccess />)

        expect(localStorage.getItem('cart_token')).toBeNull()
        expect(
            screen.getByRole('heading', { name: 'Checkout Successful' })
        ).toBeInTheDocument()
    })
})
