// file: products.js
// descr: Public API module. API-to be called function


export async function getProducts() {
    const response = await fetch('/api/products')

    if (!response.ok) {
        throw new Error('Failed to fetch products')
    }

    const data = await response.json()

    return data.products
}
