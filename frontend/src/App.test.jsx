// file: src/App.test.jsx
// descr: Integration tests. API testing of src/pages/public/ProductCatalog. validate interactions, mock only externals. includes loading error, and empty catalog test. Production API integration. Loading/error/empty states/. Cart API functions. localStorage cart-token handling. Buyer clicking add to cart. Correct product_variant_id sent to the backend




// it defines a set of related expectations
// describe is used to group related tests and benchmarks into a suite. Suites help organize testing files by creating logical blocks, making test output easier to read and enabling shared setup/teardown through lifecycle hooks
// expect is used to create assertions. runs in node
import { afterEach, describe, expect, it, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
// simulates full-user interactions by dispatching the events that would happen if the interaction took place in a browser. use with DOM. may handle multiple events and do additional checks
import userEvent from '@testing-library/user-event'
import App from './App'

describe('App', () => {
    afterEach(() => {
        vi.restoreAllMocks()
    })

    it('shows a loading state while products are being fetched', () => {
        vi.spyOn(globalThis, 'fetch').mockReturnValue(
            new Promise(() => { }),
        )

        render(<App />)

        expect(screen.getByText('Loading products...')).toBeInTheDocument()
    })

    it('renders products returned by the API', async () => {
        vi.spyOn(globalThis, 'fetch').mockResolvedValue({
            ok: true,
            json: async () => ({
                products: [
                    {
                        product_id: 'PID-001',
                        product_name: 'Test Product',
                        brand: 'TestBrand',
                        category: 'Electronics',
                        description: 'A test product description.',
                        variants: [
                            {
                                id: 25,
                                price: '19.99',
                                stock_quantity: 10,
                                color: 'Blue',
                                size: 'M',
                                is_in_stock: true,
                            },
                        ],
                    },
                ],
            }),
        })

        render(<App />)

        expect(
            await screen.findByRole('heading', { name: 'Products' }),
        ).toBeInTheDocument()

        expect(screen.getByText('Test Product')).toBeInTheDocument()
        expect(screen.getByText('TestBrand')).toBeInTheDocument()
        expect(screen.getByText('Price: $19.99')).toBeInTheDocument()
        expect(screen.getByText('In stock')).toBeInTheDocument()

        expect(fetch).toHaveBeenCalledWith('/api/products')
    })

    it('shows an error when the API request fails', async () => {
        vi.spyOn(globalThis, 'fetch').mockRejectedValue(
            new Error('Network error'),
        )

        render(<App />)

        expect(
            await screen.findByRole('alert'),
        ).toHaveTextContent('Unable to load products.')
    })

    it('shows an empty state when the catalog has no products', async () => {
        vi.spyOn(globalThis, 'fetch').mockResolvedValue({
            ok: true,
            json: async () => ({
                products: [],
            }),
        })

        render(<App />)

        expect(
            await screen.findByText('No products available.'),
        ).toBeInTheDocument()
    })

    // verify add to cart sends the correct product_variant_id
    it('creates a cart when a buyer adds a product to the cart', async () => {
        // userEvent.setup() before the component is rendered
        const user = userEvent.setup()

        vi.spyOn(globalThis, 'fetch')
            .mockResolvedValueOnce({
                ok: true,
                json: async () => ({
                    products: [
                        {
                            product_id: 'PID-001',
                            product_name: 'Test Product',
                            brand: 'TestBrand',
                            category: 'Electronics',
                            description: 'A test product description.',
                            variants: [
                                {
                                    id: 25,
                                    price: '19.99',
                                    stock_quantity: 10,
                                    color: 'Blue',
                                    size: 'M',
                                    is_in_stock: true,
                                },
                            ],
                        },
                    ],
                }),
            })
            .mockResolvedValueOnce({
                ok: true,
                json: async () => ({
                    message: 'Cart created successfully.',
                    cart_token: 'abc123',
                }),
            })

        render(<App />)
        // find by aria role button
        const addToCartButton = await screen.findByRole('button', {
            name: 'Add to cart',
        })

        await user.click(addToCartButton)

        await waitFor(() => {
            expect(fetch).toHaveBeenCalledWith('/api/cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    product_variant_id: 25,
                    quantity: 1,
                }),
            })
        })
    })
    it('adds a product to an existing cart', async () => {
        const user = userEvent.setup()

        localStorage.setItem('cart_token', 'abc123')

        vi.spyOn(globalThis, 'fetch')
            .mockResolvedValueOnce({
                ok: true,
                json: async () => ({
                    products: [
                        {
                            product_id: 'PID-001',
                            product_name: 'Test Product',
                            brand: 'TestBrand',
                            category: 'Electronics',
                            description: 'A test product description.',
                            variants: [
                                {
                                    id: 25,
                                    price: '19.99',
                                    stock_quantity: 10,
                                    color: 'Blue',
                                    size: 'M',
                                    is_in_stock: true,
                                },
                            ],
                        },
                    ],
                }),
            })
            .mockResolvedValueOnce({
                ok: true,
                json: async () => ({
                    message: 'Item added successfully.',
                    cart_token: 'abc123',
                    item: {
                        id: 1,
                        product_id: 'PID-001',
                        product_variant_id: 25,
                        quantity: 1,
                        unit_price: '19.99',
                    },
                    total_amount: '19.99',
                }),
            })

        render(<App />)

        const addToCartButton = await screen.findByRole('button', {
            name: 'Add to cart',
        })

        await user.click(addToCartButton)

        await waitFor(() => {
            expect(fetch).toHaveBeenCalledWith('/api/cart/abc123/items', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    product_variant_id: 25,
                    quantity: 1,
                }),
            })
        })
    })
})
