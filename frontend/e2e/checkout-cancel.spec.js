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

    const stripeNavigation = page.waitForURL(
        /checkout\.stripe\.com/,
        { timeout: 30000, waitUntil: 'commit' },
    )

    await page.getByRole('button', { name: 'Checkout' }).click()
    await stripeNavigation

    await page.getByRole('link', { name: /back/i }).click()

    await expect(page).toHaveURL(/\/checkout\/cancel/)
    await expect(
        page.getByRole('heading', { name: 'Checkout Canceled' }),
    ).toBeVisible()
})
