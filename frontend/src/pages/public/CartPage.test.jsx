// file: public/CartPage.test.jsx
// descr: unit/component/integration testing of cart page. frontend integration-style testing the cart page calling api layer. form uses html required so test should verify browser constraint validation, not produce a custom error message.


import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, test, vi } from 'vitest'

import CartPage from './CartPage'

import {
    getCart,
    updateCartItem,
    deleteCartItem,
} from '../../api/cart'

import { createCheckout } from '../../api/checkout'

import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'




vi.mock('../../api/cart', () => ({
    getCart: vi.fn(),
    updateCartItem: vi.fn(),
    deleteCartItem: vi.fn(),
}))

vi.mock('../../api/checkout', () => ({
    createCheckout: vi.fn(),
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

        render(
            <MemoryRouter>
                <CartPage />
            </MemoryRouter>,
        )

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

        const user = userEvent.setup()

        render(
            <MemoryRouter>
                <CartPage />
            </MemoryRouter>,
        )

        const quantityInput = await screen.findByLabelText('Quantity')
        await user.clear(quantityInput)
        await user.type(quantityInput, '3')
        await user.keyboard('{Enter}')

        await waitFor(() => {
            expect(updateCartItem).toHaveBeenCalledWith(
                'abc123',
                1,
                3,
            )
        })

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

        render(
            <MemoryRouter>
                <CartPage />
            </MemoryRouter>,
        )

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

    test('shows a link to continue shopping when the cart is empty', async () => {
        render(
            <MemoryRouter>
                <CartPage />
            </MemoryRouter>,
        )

        expect(
            await screen.findByRole('link', {
                name: 'Continue Shopping',
            }),
        ).toHaveAttribute('href', '/')
    })
    // api/checkout
    test('does not submit checkout when required shipping address is missing', async () => {
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

        const user = userEvent.setup()

        render(
            <MemoryRouter>
                <CartPage />
            </MemoryRouter>,
        )

        await screen.findByText('Product variant 1')

        const addressInput = screen.getByLabelText('Address')
        expect(addressInput).toBeRequired()

        await user.click(
            screen.getByRole('button', { name: 'Checkout' }),
        )

        expect(createCheckout).not.toHaveBeenCalled()
        expect(addressInput).toBeInvalid()
    })
})
