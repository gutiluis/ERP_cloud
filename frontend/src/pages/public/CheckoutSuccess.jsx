// file: CheckoutSuccess.jsx
// descr: checkout success page. still needs the route under src/App.jsx


import { useEffect, useState } from 'react'

function CheckoutSuccess() {
    const sessionId = new URLSearchParams(
        window.location.search,
    ).get('session_id')

    const [status, setStatus] = useState(
        sessionId ? 'checking' : 'unverified',
    )

    useEffect(() => {
        if (!sessionId) return

        let cancelled = false

        async function verifyPayment() {
            try {
                const response = await fetch(
                    `/api/orders/payment-status?session_id=${encodeURIComponent(sessionId)}`,
                )

                if (!response.ok) {
                    throw new Error('Unable to verify payment')
                }

                const data = await response.json()

                if (cancelled) return

                if (data.status === 'paid') {
                    localStorage.removeItem('cart_token')
                    setStatus('paid')
                } else {
                    setStatus('pending')
                }
            } catch {
                if (!cancelled) {
                    setStatus('unverified')
                }
            }
        }

        verifyPayment()

        return () => {
            cancelled = true
        }
    }, [sessionId])

    return (
        <main>
            {status === 'checking' && (
                <p>Verifying payment…</p>
            )}

            {status === 'paid' && (
                <>
                    <h1>Checkout Successful</h1>
                    <p>
                        Your payment was confirmed. Thank you for your order.
                    </p>
                </>
            )}

            {status === 'pending' && (
                <p>Your payment is still being processed.</p>
            )}

            {status === 'unverified' && (
                <p>
                    We couldn't verify your payment. Please check your order status.
                </p>
            )}
        </main>
    )
}

export default CheckoutSuccess
