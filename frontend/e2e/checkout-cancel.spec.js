// file: checkout-cancel.spec.js
// descr: stripe cancel checkout


import { expect, test } from '@playwright/test'

test('cancels Stripe checkout and returns to the cart flow', async ({ page }) => {
    test.setTimeout(60000)

    await page.goto('/')

    const product = page.locator('article').filter({
        hasText: 'cart-test-product',
    })

    await expect(product).toBeVisible()
    await product.getByRole('button', { name: 'Add to cart' }).click()
    await page.getByRole('link', { name: 'View cart' }).click()

    await expect(
        page.getByRole('heading', { name: /cart/i }),
    ).toBeVisible()

    await page.locator('#shipping-address-1').fill('123 Test Street')
    await page.locator('#shipping-country').fill('MX')
    await page.locator('#shipping-state').fill('Jalisco')
    await page.locator('#shipping-city').fill('Guadalajara')
    await page.locator('#shipping-zip-code').fill('45000')

    await page.getByRole('button', { name: 'Checkout' }).click()

    await expect(page).toHaveURL(/checkout\.stripe\.com/, {
        timeout: 15000,
    })

    // Use Stripe Checkout's back link to trigger the configured cancel URL.
    await page.getByRole('link', { name: /back/i }).click()

    await expect(page).toHaveURL(
        /\/checkout\/cancel(?:\?.*)?$/,
        { timeout: 15000 },
    )

    await expect(
        page.getByRole('heading', { name: 'Checkout Canceled' }),
    ).toBeVisible()

    await expect(
        page.getByText('Your checkout was canceled. Your cart has not been charged.'),
    ).toBeVisible()
})
