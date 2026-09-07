// file: ProductCatalog.test.jsx
// descr: mock getProducts, because ProductCatalog is responsible for calling the API



import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import ProductCatalog from './ProductCatalog'
import { getProducts } from '../../api/products'

vi.mock('../../api/products', () => ({
    getProducts: vi.fn(),
}))

vi.mock('../../components/ProductCard', () => ({
    default: ({ product }) => (
        <article>
            <h2>{product.product_name}</h2>
            <p>{product.brand}</p>
        </article>
    ),
}))

describe('ProductCatalog', () => {
    it('renders the loading state', () => {
        getProducts.mockReturnValue(new Promise(() => { }))

        render(<ProductCatalog />)

        expect(screen.getByText('Loading products...')).toBeInTheDocument()
    })

    it('renders the error state when the API call fails', async () => {
        getProducts.mockRejectedValue(new Error('API error'))

        render(<ProductCatalog />)

        expect(
            await screen.findByRole('alert'),
        ).toHaveTextContent('Unable to load products.')
    })

    it('renders the empty state when no products are returned', async () => {
        getProducts.mockResolvedValue([])

        render(<ProductCatalog />)

        expect(
            await screen.findByText('No products available.'),
        ).toBeInTheDocument()

        expect(screen.getByRole('heading', { name: 'Products' }))
            .toBeInTheDocument()
    })

    it('renders products returned by the API', async () => {
        getProducts.mockResolvedValue([
            {
                product_id: 1,
                product_name: 'Test Product',
                category: 'Electronics',
                brand: 'Test Brand',
                description: 'Test description',
                variants: [
                    {
                        sku: 'TEST-001',
                        price: 19.99,
                        color: 'Black',
                        size: 'Medium',
                        is_in_stock: true,
                    },
                ],
            },
        ])

        render(<ProductCatalog />)

        expect(
            await screen.findByRole('heading', {
                name: 'Test Product',
            }),
        ).toBeInTheDocument()

        expect(screen.getByText('Test Brand')).toBeInTheDocument()
    })
})
