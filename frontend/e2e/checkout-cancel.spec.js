// file: checkout-cancel.spec.js
// descr: stripe cancel checkout

import { test, expect } from '@playwright/test'

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

    const stripeNavigation = page.waitForURL(
        /checkout\.stripe\.com/,
        { timeout: 30000 },
    )

    await page.getByRole('button', { name: 'Checkout' }).click()
    await stripeNavigation

    const backLink = page.getByRole('link', { name: /back/i })

    await expect(backLink).toBeVisible({ timeout: 10000 })
    await backLink.click({ timeout: 10000 })

    // cancellation url checks
    await expect(page).toHaveURL(
        /\/checkout\/cancel(?:\?.*)?$/,
        { timeout: 15000 },
    )

    await expect(
        page.getByRole('heading', { name: 'Checkout Canceled' }),
    ).toBeVisible({ timeout: 15000 })

    await expect(
        page.getByText(
            'Your checkout was canceled. Your cart has not been charged.',
        ),
    ).toBeVisible({ timeout: 15000 })

})
