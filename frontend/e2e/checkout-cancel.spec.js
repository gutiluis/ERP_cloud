// file: checkout-cancel.spec.js
// descr: stripe cancel checkout

import { test, expect } from '@playwright/test'

test('cancels Stripe checkout and returns to the cart flow', async ({ page }) => {
    test.setTimeout(60000)

    await page.goto('/')

    const product = page.locator('article').filter({
        hasText: 'cart-test-product',
    })

    await product.getByRole('button', { name: 'Add to cart' }).click()
    await page.getByRole('link', { name: 'View cart' }).click()

    await page.locator('#shipping-address-1').fill('123 Test Street')
    await page.locator('#shipping-country').fill('MX')
    await page.locator('#shipping-state').fill('Jalisco')
    await page.locator('#shipping-city').fill('Guadalajara')
    await page.locator('#shipping-zip-code').fill('45000')

    let checkoutData

    await page.route('**/api/checkout', async (route) => {
        const response = await route.fetch()
        checkoutData = await response.json()

        await route.fulfill({
            response,
            json: checkoutData,
        })
    })

    const stripeNavigation = page.waitForURL(
        /checkout\.stripe\.com/,
        { timeout: 30000, waitUntil: 'commit' },
    )

    await page.getByRole('button', { name: 'Checkout' }).click()
    await stripeNavigation

    expect(checkoutData.checkout_url).toBeTruthy()
    expect(checkoutData.order_id).toBeTruthy()

    console.log('Stripe Checkout URL:', page.url())
    console.log(
        'Stripe links:',
        await page.getByRole('link').allTextContents(),
    )
    console.log(
        'Stripe buttons:',
        await page.getByRole('button').allTextContents(),
    )

    await page.pause()
})
