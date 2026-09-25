// file: CartPage.jsx
// descr: Cart Page. has an api helper /api/checkout.js



import { useEffect, useState } from 'react'
import {
    getCart,
    updateCartItem,
    deleteCartItem,
} from '../../api/cart'
import { Link } from 'react-router-dom'
import { createCheckout } from '../../api/checkout'




function CartPage() {
    // useState can obly be called at the top level of the component or own hook
    // use array destructuring
    // cart state variable declarations
    // set initial state
    // setCart set function update state to a different value and trigger a re-render
    const [cart, setCart] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    // api/checkout
    const [shippingAddress, setShippingAddress] = useState({
        address1: '',
        address2: '',
        country: '',
        city: '',
        zipCode: '',
        state: '',
    })
    const [checkoutLoading, setCheckoutLoading] = useState(false)
    const [checkoutError, setCheckoutError] = useState(null)

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

    // empty cart section
    if (cart.items.length === 0) {
        return (
            <main className="mx-auto max-w-7xl px-6 py-12">
                <h1 className="text-3xl font-bold text-gray-900">
                    Your cart
                </h1>

                <p className="mt-4 text-gray-600">
                    Your cart is empty.
                </p>

                <Link
                    to="/"
                    className="mt-6 inline-block font-medium text-blue-700 hover:text-blue-900"
                >
                    Continue Shopping
                </Link>
            </main>
        )
    }
    // /api/checkout
    async function handleCheckout(event) {
        event.preventDefault()

        const cartToken = localStorage.getItem('cart_token')

        if (!cartToken) {
            setCheckoutError('Unable to identify your cart.')
            return
        }

        setCheckoutLoading(true)
        setCheckoutError(null)

        try {
            const data = await createCheckout(cartToken, shippingAddress)

            console.log('CHECKOUT DATA', data)

            window.location.assign(data.checkout_url)
        } catch (error) {
            setCheckoutError(error.message)
        } finally {
            setCheckoutLoading(false)
        }
    }
    // controlled input helper
    function handleShippingChange(event) {
        const { name, value } = event.target

        setShippingAddress((currentAddress) => ({
            ...currentAddress,
            [name]: value,
        }))
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

            <div className="mt-8 border-t border-gray-200 pt-6">
                <div className="text-right">
                    <p className="text-xl font-bold text-gray-900">
                        Total: ${cart.total_amount}
                    </p>
                </div>

                <form
                    onSubmit={handleCheckout}
                    className="mt-8 max-w-2xl space-y-6"
                >
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900">
                            Shipping information
                        </h2>

                        <p className="mt-2 text-gray-600">
                            Enter your shipping address to continue to payment.
                        </p>
                    </div>

                    {checkoutError && (
                        <p
                            role="alert"
                            className="rounded-md border border-red-200 bg-red-50 p-4 text-red-700"
                        >
                            {checkoutError}
                        </p>
                    )}

                    <div>
                        <label
                            htmlFor="shipping-address-1"
                            className="block text-sm font-medium text-gray-700"
                        >
                            Address
                        </label>

                        <input
                            id="shipping-address-1"
                            name="address1"
                            type="text"
                            required
                            value={shippingAddress.address1}
                            onChange={handleShippingChange}
                            className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2"
                        />
                    </div>

                    <div>
                        <label
                            htmlFor="shipping-address-2"
                            className="block text-sm font-medium text-gray-700"
                        >
                            Address 2
                        </label>

                        <input
                            id="shipping-address-2"
                            name="address2"
                            type="text"
                            value={shippingAddress.address2}
                            onChange={handleShippingChange}
                            className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2"
                        />
                    </div>

                    <div className="grid gap-6 sm:grid-cols-2">
                        <div>
                            <label
                                htmlFor="shipping-country"
                                className="block text-sm font-medium text-gray-700"
                            >
                                Country
                            </label>

                            <input
                                id="shipping-country"
                                name="country"
                                type="text"
                                required
                                value={shippingAddress.country}
                                onChange={handleShippingChange}
                                className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2"
                            />
                        </div>

                        <div>
                            <label
                                htmlFor="shipping-state"
                                className="block text-sm font-medium text-gray-700"
                            >
                                State
                            </label>

                            <input
                                id="shipping-state"
                                name="state"
                                type="text"
                                required
                                value={shippingAddress.state}
                                onChange={handleShippingChange}
                                className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2"
                            />
                        </div>

                        <div>
                            <label
                                htmlFor="shipping-city"
                                className="block text-sm font-medium text-gray-700"
                            >
                                City
                            </label>

                            <input
                                id="shipping-city"
                                name="city"
                                type="text"
                                required
                                value={shippingAddress.city}
                                onChange={handleShippingChange}
                                className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2"
                            />
                        </div>

                        <div>
                            <label
                                htmlFor="shipping-zip-code"
                                className="block text-sm font-medium text-gray-700"
                            >
                                ZIP code
                            </label>

                            <input
                                id="shipping-zip-code"
                                name="zipCode"
                                type="text"
                                required
                                value={shippingAddress.zipCode}
                                onChange={handleShippingChange}
                                className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2"
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={checkoutLoading}
                        className="rounded-md bg-blue-700 px-6 py-3 font-medium text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                        {checkoutLoading ? 'Starting checkout...' : 'Checkout'}
                    </button>
                </form>
            </div>

        </main>
    )
}

export default CartPage
