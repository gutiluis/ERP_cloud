// file: products.test.jsx
// descr: unit tests for the API module which keeps he HTTP/API contract separate from the React component testing. spyon doesnt determint the test type. integration several components vs unit single component



import { describe, expect, it, vi } from 'vitest'
import { getProducts } from './products'

describe('getProducts', () => {
    it('returns products from the API', async () => {
        vi.spyOn(globalThis, 'fetch').mockResolvedValue({
            ok: true,
            json: async () => ({
                products: [
                    {
                        product_id: 'PID-001',
                        product_name: 'Test Product',
                    },
                ],
            }),
        })

        const products = await getProducts()

        expect(products).toEqual([
            {
                product_id: 'PID-001',
                product_name: 'Test Product',
            },
        ])

        expect(fetch).toHaveBeenCalledWith('/api/products')
    })

    it('throws when the API request fails', async () => {
        vi.spyOn(globalThis, 'fetch').mockResolvedValue({
            ok: false,
        })

        await expect(getProducts()).rejects.toThrow(
            'Failed to fetch products',
        )
    })
})
