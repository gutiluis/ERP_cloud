// file: cart.test.js
// descr: Api cart layer before the ui implementation. cart api unit test


import { describe, beforeEach, test, vi, expect } from 'vitest'

// import routes
import {
    createCart,
    getCart,
    addCartItem,
    updateCartItem,
    deleteCartItem,
} from './cart'


describe('cart API', () => {
    beforeEach(() => {
        vi.restoreAllMocks()
    })

    function mockFetchResponse(
        responseData,
        {
            ok = true,
            status = 200,
            contentType = 'application/json',
        } = {},
    ) {
        vi.spyOn(globalThis, 'fetch').mockResolvedValue({
            ok,
            status,
            headers: {
                get: () => contentType,
            },
            json: async () => responseData,
        })
    }

    test('creates a cart', async () => {
        const responseData = {
            message: 'Cart created successfully.',
            cart_token: 'abc123',
        }

        mockFetchResponse(responseData)

        const result = await createCart(25, 2)

        expect(fetch).toHaveBeenCalledWith('/api/cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                product_variant_id: 25,
                quantity: 2,
            }),
        })

        expect(result).toEqual(responseData)
    })

    test('gets a cart', async () => {
        const responseData = {
            cart_token: 'abc123',
            items: [],
            total_amount: '0.00',
        }

        mockFetchResponse(responseData)

        const result = await getCart('abc123')

        expect(fetch).toHaveBeenCalledWith('/api/cart/abc123')
        expect(result).toEqual(responseData)
    })

    test('adds an item to a cart', async () => {
        const responseData = {
            message: 'Item added successfully.',
            cart_token: 'abc123',
            item: {
                id: 1,
                product_id: 10,
                product_variant_id: 25,
                quantity: 2,
                unit_price: '19.99',
            },
            total_amount: '39.98',
        }

        mockFetchResponse(responseData)

        const result = await addCartItem('abc123', 25, 2)

        expect(fetch).toHaveBeenCalledWith('/api/cart/abc123/items', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                product_variant_id: 25,
                quantity: 2,
            }),
        })

        expect(result).toEqual(responseData)
    })

    test('updates a cart item', async () => {
        const responseData = {
            message: 'Item updated successfully.',
            cart_token: 'abc123',
            item: {
                id: 1,
                product_id: 10,
                product_variant_id: 25,
                quantity: 3,
                unit_price: '19.99',
            },
            total_amount: '59.97',
        }

        mockFetchResponse(responseData)

        const result = await updateCartItem('abc123', 1, 3)

        expect(fetch).toHaveBeenCalledWith('/api/cart/abc123/items/1', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                quantity: 3,
            }),
        })

        expect(result).toEqual(responseData)
    })

    test('deletes a cart item', async () => {
        const responseData = {
            message: 'Item deleted successfully.',
            cart_token: 'abc123',
            total_amount: '0.00',
        }

        mockFetchResponse(responseData)

        const result = await deleteCartItem('abc123', 1)

        expect(fetch).toHaveBeenCalledWith('/api/cart/abc123/items/1', {
            method: 'DELETE',
        })

        expect(result).toEqual(responseData)
    })

    test('throws the API error when the request fails', async () => {
        mockFetchResponse(
            { error: 'Cart not found' },
            { ok: false, status: 404 },
        )

        await expect(getCart('abc123')).rejects.toThrow('Cart not found')
    })

    test('throws a status error for a non-JSON response', async () => {
        mockFetchResponse(
            '<html>Not Found</html>',
            {
                ok: false,
                status: 404,
                contentType: 'text/html',
            },
        )

        await expect(getCart('abc123')).rejects.toThrow(
            'Request failed with status 404',
        )
    })
})
