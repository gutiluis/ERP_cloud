// file: api/cart.js
// descr: cart frontend api module. which matches backend cart api routes and methods. createCart POST, getCart GET, addCartItem POST, updateCartItem PATCH, deleteCartItem DELETE function endpoints
// /api/cart, /api/cart/:cartToken, /api/cart:cartToken/items, /api/cart/:cartToken/items/:itemId. /api/cart:cartToken/items/:itemId
// load cart, handles empty-error state, update quantity, removes items, submits checkouts, handles checkout errors, redirects to stripe
// unit/component testing


async function handleResponse(response) {
    const contentType = response.headers.get('content-type')

    if (!contentType?.includes('application/json')) {
        throw new Error(`Request failed with status ${response.status}`)
    }

    const data = await response.json()

    if (!response.ok) {
        throw new Error(data.error || `Request failed with status ${response.status}`)
    }

    return data
}




// not an api endpoint
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

    return handleResponse(response)

}

export async function getCart(cartToken) {
    const response = await fetch(`/api/cart/${cartToken}`)

    return handleResponse(response)
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

    return handleResponse(response)
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

    return handleResponse(response)

}

export async function deleteCartItem(cartToken, itemId) {
    const response = await fetch(`/api/cart/${cartToken}/items/${itemId}`, {
        method: 'DELETE',
    })

    return handleResponse(response)
}
