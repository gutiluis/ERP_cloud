import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, test, vi } from 'vitest'

import CartPage from './CartPage'

import {
    getCart,
    updateCartItem,
    deleteCartItem,
} from '../../api/cart'

import userEvent from '@testing-library/user-event'

vi.mock('../../api/cart', () => ({
    getCart: vi.fn(),
    updateCartItem: vi.fn(),
    deleteCartItem: vi.fn(),
}))

describe('CartPage', () => {
    beforeEach(() => {
        localStorage.clear()
        vi.clearAllMocks()
    })

    test('loads and displays the cart', async () => {
        localStorage.setItem('cart_token', 'abc123')

        getCart.mockResolvedValue({
            cart_token: 'abc123',
            items: [
                {
                    id: 1,
                    product_id: 1,
                    product_variant_id: 1,
                    quantity: 2,
                    unit_price: '29.99',
                },
            ],
            total_amount: '59.98',
        })

        render(<CartPage />)

        expect(
            await screen.findByText('Product variant 1'),
        ).toBeInTheDocument()

        expect(screen.getByText('Quantity')).toBeInTheDocument()
        expect(screen.getByText('Total: $59.98')).toBeInTheDocument()

        expect(getCart).toHaveBeenCalledWith('abc123')
    })

    test('updates a cart item', async () => {
        localStorage.setItem('cart_token', 'abc123')

        getCart.mockResolvedValue({
            cart_token: 'abc123',
            items: [
                {
                    id: 1,
                    product_id: 1,
                    product_variant_id: 1,
                    quantity: 2,
                    unit_price: '29.99',
                },
            ],
            total_amount: '59.98',
        })

        updateCartItem.mockResolvedValue({
            cart_token: 'abc123',
            item: {
                id: 1,
                product_id: 1,
                product_variant_id: 1,
                quantity: 3,
                unit_price: '29.99',
            },
            total_amount: '89.97',
        })

        render(<CartPage />)

        const quantityInput = await screen.findByLabelText('Quantity')

        fireEvent.change(quantityInput, {
            target: { value: '3' },
        })

        // import user
        const user = userEvent.setup()
        // onChange event patch
        await user.clear(quantityInput)
        // onBlur event patch
        await user.type(quantityInput, '3')
        // onKeyDown event patch
        await user.keyboard('{Enter}')

        await waitFor(() => {
            expect(updateCartItem).toHaveBeenCalledWith(
                'abc123',
                1,
                3,
            )
        })
        console.log(updateCartItem.mock.calls)

        expect(await screen.findByDisplayValue('3')).toBeInTheDocument()
        expect(screen.getByText('Total: $89.97')).toBeInTheDocument()
    })

    test('deletes a cart item', async () => {
        localStorage.setItem('cart_token', 'abc123')

        getCart.mockResolvedValue({
            cart_token: 'abc123',
            items: [
                {
                    id: 1,
                    product_id: 1,
                    product_variant_id: 1,
                    quantity: 2,
                    unit_price: '29.99',
                },
            ],
            total_amount: '59.98',
        })

        deleteCartItem.mockResolvedValue({
            cart_token: 'abc123',
            message: 'Item deleted successfully.',
            total_amount: '0.00',
        })

        render(<CartPage />)

        await screen.findByText('Product variant 1')

        fireEvent.click(screen.getByRole('button', { name: 'Remove' }))

        await waitFor(() => {
            expect(deleteCartItem).toHaveBeenCalledWith(
                'abc123',
                1,
            )
        })

        expect(
            screen.getByText('Your cart is empty.'),
        ).toBeInTheDocument()

        expect(screen.getByText('Your cart')).toBeInTheDocument()
    })
})
