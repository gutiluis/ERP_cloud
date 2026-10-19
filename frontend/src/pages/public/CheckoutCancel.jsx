// file: /public/CheckoutCancel.jsx
// descr: react using javascript and jsx checkout cancel page

import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { cancelCheckout } from '../../api/checkout'

function CheckoutCancel() {
    const [message, setMessage] = useState(() => {
        const sessionId = new URLSearchParams(window.location.search).get('session_id')
        const cartToken = localStorage.getItem('cart_token')

        return sessionId && cartToken
            ? 'Canceling checkout...'
            : 'Checkout was canceled. You can return to your cart to try again.'
    })
    const [error, setError] = useState(false)

    useEffect(() => {
        const sessionId = new URLSearchParams(window.location.search).get('session_id')
        const cartToken = localStorage.getItem('cart_token')

        if (!sessionId || !cartToken) {
            return
        }

        let active = true

        cancelCheckout(cartToken, sessionId)
            .then(() => {
                if (active) {
                    setMessage('Your checkout session was canceled. Your cart is still available to restart checkout.')
                }
            })
            .catch(() => {
                if (active) {
                    setError(true)
                    setMessage('We could not confirm cancellation with Stripe. Return to your cart to check checkout status.')
                }
            })

        return () => {
            active = false
        }
    }, [])

    return (
        <main>
            <h1>Checkout Canceled</h1>
            <p role="status">{message}</p>
            {error && <p role="alert">The checkout session may still be active.</p>}
            <Link to="/cart">Return to cart</Link>
        </main>
    )
}

export default CheckoutCancel
