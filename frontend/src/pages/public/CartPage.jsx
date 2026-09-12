import { useEffect, useState } from 'react'
import {
    getCart,
    updateCartItem,
    deleteCartItem,
} from '../../api/cart'

function CartPage() {
    const [cart, setCart] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        async function loadCart() {
            const cartToken = localStorage.getItem('cart_token')

            if (!cartToken) {
                setCart({
                    items: [],
                    total_amount: '0.00',
                })
                setLoading(false)
                return
            }

            try {
                const data = await getCart(cartToken)
                setCart(data)
            } catch {
                setError('Unable to load cart.')
            } finally {
                setLoading(false)
            }
        }

        loadCart()
    }, [])

    async function handleUpdateItem(itemId, quantity) {

        if (!Number.isInteger(quantity) || quantity < 1) {
            return
        }
        const cartToken = localStorage.getItem('cart_token')

        if (!cartToken) {
            return
        }

        try {
            const data = await updateCartItem(
                cartToken,
                itemId,
                quantity,
            )

            setCart((currentCart) => ({
                ...currentCart,
                items: currentCart.items.map((item) =>
                    item.id === itemId ? data.item : item,
                ),
                total_amount: data.total_amount,
            }))
        } catch {
            setError('Unable to update cart item.')
        }
    }

    async function handleDeleteItem(itemId) {
        const cartToken = localStorage.getItem('cart_token')

        if (!cartToken) {
            return
        }

        try {
            const data = await deleteCartItem(cartToken, itemId)

            setCart((currentCart) => ({
                ...currentCart,
                items: currentCart.items.filter(
                    (item) => item.id !== itemId,
                ),
                total_amount: data.total_amount,
            }))
        } catch {
            setError('Unable to remove cart item.')
        }
    }

    if (loading) {
        return (
            <main className="mx-auto max-w-7xl px-6 py-12">
                <p className="text-gray-600">Loading cart...</p>
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

    if (cart.items.length === 0) {
        return (
            <main className="mx-auto max-w-7xl px-6 py-12">
                <h1 className="text-3xl font-bold text-gray-900">
                    Your cart
                </h1>

                <p className="mt-4 text-gray-600">
                    Your cart is empty.
                </p>
            </main>
        )
    }

    return (
        <main className="mx-auto max-w-7xl px-6 py-12">
            <h1 className="text-3xl font-bold text-gray-900">
                Your cart
            </h1>

            <section className="mt-8 space-y-4">
                {cart.items.map((item) => (
                    <article
                        key={item.id}
                        className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm"
                    >
                        <div className="flex items-center justify-between">
                            <div>
                                <h2 className="font-semibold text-gray-900">
                                    Product variant {item.product_variant_id}
                                </h2>

                                <p className="mt-1 text-sm text-gray-600">
                                    Unit price: ${item.unit_price}
                                </p>
                            </div>

                            <button
                                type="button"
                                onClick={() =>
                                    handleDeleteItem(item.id)
                                }
                                className="text-sm font-medium text-red-700 hover:text-red-900"
                            >
                                Remove
                            </button>
                        </div>

                        <div className="mt-4 flex items-center gap-3">
                            <label
                                htmlFor={`quantity-${item.id}`}
                                className="text-sm font-medium text-gray-700"
                            >
                                Quantity
                            </label>

                            <input
                                id={`quantity-${item.id}`}
                                type="number"
                                min="1"
                                value={item.quantity}
                                // on a cart UI there is no need for a patch event trigger for each update
                                // onChange controls the spinner arrows
                                onChange={(event) => {

                                    const quantity = Number(event.target.value)
                                    setCart((currentCart) => ({
                                        ...currentCart,
                                        items: currentCart.items.map((currentItem) =>
                                            currentItem.id === item.id
                                                ? { ...currentItem, quantity }
                                                : currentItem,
                                        ),
                                    }))
                                }}
                                // onBlur occurs when an html element loses focus
                                // clicking the number spinner changes the value but does not blur the input. no patch is sent
                                // send a patch every focus of cursor click outside
                                onBlur={(event) => {

                                    handleUpdateItem(
                                        item.id,
                                        Number(event.target.value),
                                    )
                                }}
                                // send a patch with enter after updating quantity
                                // without sending a patch for every focus to update quantity
                                onKeyDown={(event) => {
                                    if (event.key === 'Enter') {
                                        event.currentTarget.blur()
                                    }
                                }}
                                className="w-20 rounded-md border border-gray-300 px-3 py-2"
                            />
                        </div>

                        <p className="mt-4 font-semibold text-gray-900">
                            ${(Number(item.unit_price) * item.quantity).toFixed(2)}
                        </p>
                    </article>
                ))}
            </section>

            <div className="mt-8 border-t border-gray-200 pt-6 text-right">
                <p className="text-xl font-bold text-gray-900">
                    Total: ${cart.total_amount}
                </p>
            </div>
        </main>
    )
}

export default CartPage
