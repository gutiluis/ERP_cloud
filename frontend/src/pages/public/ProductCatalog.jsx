// file: ProductCatalog.jsx
// descr: indirect API call. react page/component which triggers the API call. 4 different Product UI states



import { useEffect, useState } from 'react'
import { getProducts } from '../../api/products'
import { createCart, addCartItem } from '../../api/cart'
import ProductCard from '../../components/ProductCard'

function ProductCatalog() {
    const [products, setProducts] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    // survive page refresh
    const [cartToken, setCartToken] = useState(
        () => localStorage.getItem('cart_token')
    )


    useEffect(() => {
        async function loadProducts() {
            try {
                const data = await getProducts()
                setProducts(data)
            } catch {
                setError('Unable to load products.')
            } finally {
                setLoading(false)
            }
        }

        loadProducts()
    }, [])

    if (loading) {
        return (
            <main className="mx-auto max-w-7xl px-6 py-12">
                <p className="text-gray-600">Loading products...</p>
            </main>
        )
    }

    if (error) {
        return (
            <main className="mx-auto max-w-7xl px-6 py-12">
                <p
                    role="alert"
                    className="rounded-md border border-red-200 bg-red-50 p-4 text-red-700"
                >
                    {error}
                </p>
            </main>
        )
    }

    async function handleAddToCart(productVariantId) {
        try {
            const data = cartToken
                ? await addCartItem(cartToken, productVariantId, 1)
                : await createCart(productVariantId, 1)

            setCartToken(data.cart_token)
        } catch {
            setError('Unable to add product to cart.')
        }
    }

    if (products.length === 0) {
        return (
            <main className="mx-auto max-w-7xl px-6 py-12">
                <h1 className="text-3xl font-bold text-gray-900">
                    Products
                </h1>

                <p className="mt-4 text-gray-600">
                    No products available.
                </p>
            </main>
        )
    }

    return (
        <main className="mx-auto max-w-7xl px-6 py-12">
            <header className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900">
                    Products
                </h1>

                <p className="mt-2 text-gray-600">
                    Browse our available products.
                </p>
            </header>

            <section className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {products.map((product) => (
                    <ProductCard
                        key={product.product_id}
                        product={product}
                        onAddToCart={handleAddToCart}
                    />
                ))}
            </section>
        </main>
    )
}

export default ProductCatalog
