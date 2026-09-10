// file: ProductCard.test.jsx
// descr:


import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import ProductCard from './ProductCard'

describe('ProductCard', () => {
    it('renders product information and variants', () => {
        const product = {
            product_id: 'PID-001',
            product_name: 'Test Product',
            brand: 'TestBrand',
            category: 'Electronics',
            description: 'A test product description.',
            variants: [
                {
                    id: 1,
                    price: '19.99',
                    stock_quantity: 10,
                    color: 'Blue',
                    size: 'M',
                    is_in_stock: true,
                },
            ],
        }

        render(<ProductCard product={product} />)

        expect(
            screen.getByRole('heading', { name: 'Test Product' }),
        ).toBeInTheDocument()

        expect(screen.getByText('TestBrand')).toBeInTheDocument()
        expect(screen.getByText('Electronics')).toBeInTheDocument()
        expect(
            screen.getByText('A test product description.'),
        ).toBeInTheDocument()

        expect(screen.getByText('Price: $19.99')).toBeInTheDocument()
        expect(screen.getByText('In stock')).toBeInTheDocument()
    })

    it('shows out of stock for unavailable variants', () => {
        const product = {
            product_id: 'PID-002',
            product_name: 'Out Of Stock Product',
            brand: 'TestBrand',
            category: 'Electronics',
            description: 'Unavailable product.',
            variants: [
                {
                    id: 1,
                    price: '29.99',
                    stock_quantity: 0,
                    color: 'Black',
                    size: 'L',
                    is_in_stock: false,
                },
            ],
        }

        render(<ProductCard product={product} />)

        expect(screen.getByText('Out of stock')).toBeInTheDocument()
    })
})
