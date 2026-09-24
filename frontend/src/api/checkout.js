async function handleResponse(response) {
    const contentType = response.headers.get('content-type')

    if (!contentType?.includes('application/json')) {
        throw new Error(`Request failed with status ${response.status}`)
    }

    const data = await response.json()

    if (!response.ok) {
        // or Request failed
        throw new Error(data.error || `Request failed with status ${response.status}`)
    }

    return data
}

export async function createCheckout(
    cartToken,
    shippingAddress,
) {
    const response = await fetch('/api/checkout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            cart_token: cartToken,
            shipping_address_1: shippingAddress.address1,
            shipping_address_2: shippingAddress.address2,
            shipping_country: shippingAddress.country,
            shipping_city: shippingAddress.city,
            shipping_zip_code: shippingAddress.zipCode,
            shipping_state: shippingAddress.state,
        }),
    })

    return handleResponse(response)
}
