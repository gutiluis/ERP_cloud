// file: api/cart.js
// descr: cart frontend api which matches backend cart api routes and methods

export async function createCart(productVariantId, quantity) {
    // fetc() takes one mandatory argument path to resources. returning a promise
    const response = await fetch('/api/cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        // structured data json // not a constructor
        // JSON is a built-in javascript global object
        // the json namespace contains static methods for parsing values from and converting values to json
        // JSON.stringify return a json string corresponding to the specified value, optionally including only certain propertier or replacing property values in a user-defined manner
        // body is a property option of the RequestInit object that you pass as the second argument to fetch()
        body: JSON.stringify({
            product_variant_id: productVariantId,
            quantity,
        }),
    })

    if (!response.ok) {
        throw new Error('Failed to create cart')
    }

    return response.json()
}

export async function getCart(cartToken) {
    const response = await fetch(`/api/cart/${cartToken}`)

    if (!response.ok) {
        throw new Error('Failed to fetch cart')
    }

    return response.json()
}

export async function addCartItem(cartToken, productVariantId, quantity) {
    const response = await fetch(`/api/cart/${cartToken}/items`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_variant_id: productVariantId,
            quantity,
        }),
    })

    if (!response.ok) {
        throw new Error('Failed to add cart item')
    }

    return response.json()
}

export async function updateCartItem(cartToken, itemId, quantity) {
    const response = await fetch(`/api/cart/${cartToken}/items/${itemId}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            quantity,
        }),
    })

    if (!response.ok) {
        throw new Error('Failed to update cart item')
    }

    return response.json()
}

export async function deleteCartItem(cartToken, itemId) {
    const response = await fetch(`/api/cart/${cartToken}/items/${itemId}`, {
        method: 'DELETE',
    })

    if (!response.ok) {
        throw new Error('Failed to delete cart item')
    }

    return response.json()
}
