// file: App.text.jsx
// descr: Integration tests. API testing of src/pages/public/ProductCatalog. validate interactions, mock only externals. includes loading error, and empty catalog test



import { afterEach, describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
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
                                sku: 'SKU-001',
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
        expect(screen.getByText('SKU: SKU-001')).toBeInTheDocument()
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
})
