// file: CheckoutSuccess.jsx
// descr: checkout success page. still needs the route under src/App.jsx


import { useEffect } from 'react'

function CheckoutSuccess() {
    useEffect(() => {
        localStorage.removeItem('cart_token')
    }, [])

    return (
        <main>
            <h1>Checkout Successful</h1>
            <p>Your payment was successful. Thank you for your order.</p>
        </main>
    )
}

export default CheckoutSuccess
